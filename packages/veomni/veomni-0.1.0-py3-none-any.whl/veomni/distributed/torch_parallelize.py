# Copyright 2025 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import types
from functools import partial
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
from torch.distributed._tensor import Shard
from torch.distributed.fsdp import CPUOffload, FullyShardedDataParallel, MixedPrecision, ShardingStrategy
from torch.distributed.fsdp._common_utils import _get_module_fsdp_state_if_fully_sharded_module
from torch.distributed.fsdp._runtime_utils import _lazy_init
from torch.distributed.fsdp.wrap import lambda_auto_wrap_policy
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.checkpoint import noop_context_fn

from ..models import load_model_weights
from ..utils import logging
from ..utils.import_utils import is_torch_version_greater_than
from .checkpoint import CheckpointFunction
from .fsdp import (
    clip_grad_norm_,
    init_fsdp_fn,
    parallel_init_fsdp_fn,
    parallel_load_safetensors,
    register_checkpoint_extension,
)
from .parallel_state import get_parallel_state
from .utils import get_module_from_path, set_module_from_path


if is_torch_version_greater_than("2.4"):
    from torch.distributed._composable.fsdp import MixedPrecisionPolicy, fully_shard
    from torch.distributed.tensor.parallel import parallelize_module


logger = logging.get_logger(__name__)


def verbose_fsdp_grouping(model, prefix="", depth=0):
    indent = "    " * depth

    for name, child in model.named_children():
        if isinstance(child, FullyShardedDataParallel):
            module_names = [m_name for m_name, _ in child.named_modules()][1:]  # [1:] 排除自身
            strategy = child.sharding_strategy
            logger.debug_rank0(f"{indent}├── [FSDP Group] {prefix}{name}")
            logger.debug_rank0(
                f"{indent}│   ├── Sharding Strategy: {strategy}, Mixed Precision: {child.mixed_precision}"
            )
            logger.debug_rank0(f"{indent}│   └── Contains Modules: {module_names}")

            verbose_fsdp_grouping(child, prefix=f"{prefix}{name}.", depth=depth + 1)
        else:
            verbose_fsdp_grouping(child, prefix=f"{prefix}{name}.", depth=depth)


def parallelize_model_fsdp1(
    model: "nn.Module",
    weights_path: Optional[str] = None,
    enable_full_shard: bool = True,
    enable_mixed_precision: bool = True,
    basic_modules: Optional[List[str]] = None,
    fsdp_no_shard_states=None,
    fsdp_no_shard_states_fqn=None,
    ep_param_suffix=None,
    fqn2spec_info=None,
    **kwargs,
) -> "nn.Module":
    """
    Applies EP (when enabled) + FSDP1 parallel strategy to the model.
    """
    parallel_state = get_parallel_state()

    if parallel_state.ep_enabled:
        parallel_plan = model.get_parallel_plan()
        fqn2spec_info = parallel_plan.apply(model, parallel_state.ep_fsdp_device_mesh)

        fsdp_no_shard_states_fqn_to_module = parallel_plan.get_fsdp_no_shard_info(model)
        fsdp_no_shard_states = list(fsdp_no_shard_states_fqn_to_module.values())
        fsdp_no_shard_states_fqn = list(fsdp_no_shard_states_fqn_to_module.keys())
        logger.info_rank0(f"Apply expert parallel to the model successfully.\nEP modules: {fsdp_no_shard_states_fqn}.")
    else:
        fqn2spec_info = None
        fsdp_no_shard_states = None
        fsdp_no_shard_states_fqn = None

    wrap_policy = partial(lambda_auto_wrap_policy, lambda_fn=lambda module: module.__class__.__name__ in basic_modules)

    # set fsdp/hsdp sharding strategy
    if parallel_state.fsdp_mesh.ndim > 1 and parallel_state.fsdp_mesh.size() > 1:
        strategy = ShardingStrategy.HYBRID_SHARD
    else:
        strategy = ShardingStrategy.FULL_SHARD

    fsdp_kwargs = {
        "auto_wrap_policy": wrap_policy,
        "ignored_states": fsdp_no_shard_states,
        "device_id": torch.cuda.current_device(),
        "sharding_strategy": strategy if enable_full_shard else ShardingStrategy.NO_SHARD,
        "use_orig_params": True,
    }

    fsdp_kwargs["device_mesh"] = parallel_state.fsdp_mesh

    fsdp_kwargs.update(kwargs.pop("fsdp_kwargs", {}))

    if enable_mixed_precision:
        logger.info_rank0("Enable mixed precision training.")
        mixed_precision = MixedPrecision(
            param_dtype=torch.bfloat16,
            reduce_dtype=torch.float32,
            buffer_dtype=torch.float32,
        )
        if hasattr(model, "get_ignore_modules_in_mixed_precision"):
            mixed_precision._module_classes_to_ignore += model.get_ignore_modules_in_mixed_precision()

        fsdp_kwargs["mixed_precision"] = mixed_precision

    if kwargs.get("init_device") == "cpu":
        logger.info_rank0("Enable rank0-only initialization.")
        fsdp_kwargs["sync_module_states"] = True
        if parallel_state.global_rank != 0:
            fsdp_kwargs["param_init_fn"] = init_fsdp_fn(model, device="cuda")
    elif kwargs.get("init_device") == "meta":
        logger.info_rank0("Enable meta initialization.")
        if weights_path is None:
            logger.info_rank0("weights_path is None during meta initialization.")

        shard_states = kwargs.get("shard_states", {})
        if not shard_states and weights_path:
            shard_states = parallel_load_safetensors(weights_path)

        fsdp_kwargs["param_init_fn"] = parallel_init_fsdp_fn(
            model,
            shard_states.copy(),
            ignore_states=fsdp_no_shard_states,
            strict=kwargs.pop("strict", False),
        )

    if kwargs.pop("enable_fsdp_offload", False):
        logger.info_rank0("Enable offloading for parameters & gradients & optimizer states.")
        fsdp_kwargs["cpu_offload"] = CPUOffload(offload_params=True)

    if kwargs.pop("enable_forward_prefetch", False):
        fsdp_kwargs["forward_prefetch"] = True
    else:
        fsdp_kwargs["forward_prefetch"] = False
        fsdp_kwargs["backward_prefetch"] = None

    # FULLY_SHARD first
    model = FullyShardedDataParallel(model, **fsdp_kwargs)

    if fsdp_no_shard_states is not None:
        # apply NO_SHARD the ignored_states, but wrap into DDP
        if parallel_state.ep_fsdp_mesh["ep_fsdp"].size() == 1:
            moe_sharding_strategy = ShardingStrategy.NO_SHARD
            ep_fsdp_device_mesh = parallel_state.fsdp_mesh
        else:
            moe_sharding_strategy = ShardingStrategy.FULL_SHARD
            ep_fsdp_device_mesh = parallel_state.ep_fsdp_mesh["ep_fsdp"]

        logger.info_rank0(f"Apply {moe_sharding_strategy} states on '{fsdp_no_shard_states_fqn}'.")
        fsdp_kwargs.pop("ignored_states", None)
        fsdp_kwargs.pop("auto_wrap_policy", None)
        fsdp_kwargs["sharding_strategy"] = moe_sharding_strategy
        fsdp_kwargs["device_mesh"] = ep_fsdp_device_mesh
        logger.info_rank0(f"{ep_fsdp_device_mesh=}")
        for fqn in fsdp_no_shard_states_fqn:
            no_shard_module = get_module_from_path(model, fqn)
            if kwargs.get("init_device") == "meta":
                key_prefix = fqn + "."
                ep_shard_states = {
                    k[len(key_prefix) :]: v for k, v in shard_states.items() if k.startswith(key_prefix)
                }
                fsdp_kwargs["param_init_fn"] = parallel_init_fsdp_fn(
                    no_shard_module,
                    ep_shard_states,
                    strict=kwargs.pop("strict", False),
                )
            fsdp_module = FullyShardedDataParallel(no_shard_module, **fsdp_kwargs)
            fsdp_state = _get_module_fsdp_state_if_fully_sharded_module(fsdp_module)
            fsdp_state._gradient_postdivide_factor *= parallel_state.ep_size
            set_module_from_path(model, fqn, fsdp_module)

    _lazy_init(model, model)

    # Apply fsdp extension to FSDP model
    save_hook_mesh = parallel_state.ep_fsdp_device_mesh if parallel_state.ep_enabled else None
    logger.info_rank0("Register Checkpoints Extension hook to the model")
    register_checkpoint_extension(
        fsdp_model=model,
        save_hook_mesh=save_hook_mesh,
        fqn2spec_info=fqn2spec_info,
    )

    if parallel_state.ep_enabled:
        model.clip_grad_norm_ = types.MethodType(clip_grad_norm_, model)

    verbose_fsdp_grouping(model)

    # FSDP1 path keeps its own clipper already above

    return model


def parallelize_model_fsdp2(
    model: "nn.Module",
    weights_path: Optional[str] = None,
    enable_mixed_precision: bool = True,
    basic_modules: Optional[List[str]] = None,
    **kwargs,
) -> "nn.Module":
    """
    Applies EP (when enabled) + FSDP2 parallel strategy to the model.

    Flow:
    1. Apply EP: Expert tensors [128,H,I] -> [32,H,I] local tensors per EP rank
    2. Apply FSDP2 to expert modules: Shard expert tensors along dim-1 (hidden dim)
    3. Apply FSDP2 to regular modules: Standard dim-0 sharding
    4. Result: Expert params [32,H/fsdp_size,I], regular params use standard FSDP2
    """
    parallel_state = get_parallel_state()

    # Step 0: Get target classes to shard later
    target_classes = set((getattr(model, "_no_split_modules", []) or []) + (basic_modules or []))
    # Make a list of tuples that contains layer's name and module
    decoder_blocks: List[Tuple[str, nn.Module]] = [
        (fqn, mod) for fqn, mod in model.named_modules() if mod.__class__.__name__ in target_classes
    ]
    logger.info_rank0(f"target classes to shard: {target_classes}")

    # Step 1: Apply expert parallelism (slice expert tensors [128,H,I] -> [16,H,I])
    if parallel_state.ep_enabled:
        parallel_plan = model.get_parallel_plan()
        assert parallel_plan is not None, (
            "Expert parallelism needs parallel plan defined in the model! Please see veomni/models/transformers/qwen3_moe/parallel_plan.py for example."
        )
        ep_fqn2spec_info = parallel_plan.apply(model, parallel_state.ep_fsdp_device_mesh)
        # Attach spec mapping for checkpoint load-time reconstruction
        setattr(model, "_fqn2spec_info", ep_fqn2spec_info)
        # ep_mesh does not really exist in EP parameters' device mesh.
        # EP parameters are loaded as local tensors to be later sharded by fully_shard
        ep_mesh = parallel_state.ep_fsdp_device_mesh["ep"]
        # experts_map is a dict {experts_fqn: experts_mod}
        # - Qwen3MoE keys: model.layers.N.mlp.experts
        # - M8 keys: transformer.h.N.mlp.moe.experts
        experts_map = parallel_plan.get_fsdp_no_shard_info(model)

        logger.info_rank0(f"Applied EP: expert tensors sliced along expert dimension (EP mesh: {ep_mesh})")
        logger.info_rank0(f"Experts Map: {experts_map}")
    else:
        ep_fqn2spec_info = None
        ep_mesh = None
        experts_map = None

    # Extract experts module from the layer if any, then pair them
    layer_pairs = []
    for layer_fqn, layer_mod in decoder_blocks:
        if experts_map is not None:
            # extract experts module from the layer
            experts_mod = next(
                (exp_mod for exp_fqn, exp_mod in experts_map.items() if exp_fqn.startswith(layer_fqn + ".")),
                None,
            )
            layer_pairs.append((layer_fqn, layer_mod, experts_mod))
        else:
            # No experts module found
            layer_pairs.append((layer_fqn, layer_mod, None))

    logger.info_rank0(f"layer pairs: {layer_pairs}")

    # Step 2: Update fsdp2 kwargs
    fsdp_kwargs = {"mesh": parallel_state.fsdp_mesh}
    # 2.1: mp_policy kwargs
    if enable_mixed_precision:
        mp_policy = MixedPrecisionPolicy(
            param_dtype=torch.bfloat16,
            reduce_dtype=torch.float32,
        )
        fsdp_kwargs["mp_policy"] = mp_policy

    if hasattr(model, "get_ignore_modules_in_mixed_precision"):
        modules_to_ignore_in_mixed_precision = model.get_ignore_modules_in_mixed_precision()
    else:
        modules_to_ignore_in_mixed_precision = None

    # 2.2: ep_fsdp2 kwargs
    if parallel_state.ep_enabled:
        # Use the ep_fsdp dimension as DP mesh for experts (shards orthogonal to EP)
        ep_fsdp_mesh = parallel_state.ep_fsdp_device_mesh["ep_fsdp"]
        expert_fsdp_kwargs = dict(fsdp_kwargs)
        expert_fsdp_kwargs["mesh"] = ep_fsdp_mesh

        # Prefer dim-1 sharding for expert weights when composing with EP shard on dim-0
        def _experts_shard_placement_fn(param):
            return Shard(1)

        expert_fsdp_kwargs["shard_placement_fn"] = _experts_shard_placement_fn

    # a helper method that shards layer with mp_policy control
    def _apply_fsdp_to_block(block: "nn.Module") -> None:
        logger.info_rank0(f"Apply FSDP2 to {block.__class__.__name__}.")
        if (
            modules_to_ignore_in_mixed_precision is not None
            and block.__class__ in modules_to_ignore_in_mixed_precision
        ):
            # pass all kwargs except mp_policy
            fully_shard(block, **{k: v for k, v in fsdp_kwargs.items() if k != "mp_policy"})
        else:
            fully_shard(block, **fsdp_kwargs)

    for layer_fqn, layer_mod, experts_mod in layer_pairs:
        if parallel_state.ep_enabled and experts_mod is not None:
            # shard expert
            fully_shard(experts_mod, **expert_fsdp_kwargs)
            if hasattr(experts_mod, "set_gradient_divide_factor"):
                # Align gradient scaling with FSDP1: average EP grads across EP ranks
                experts_mod.set_gradient_divide_factor(parallel_state.ep_size)
        # shard decoder layer
        _apply_fsdp_to_block(layer_mod)
    # shard root model
    fully_shard(model, **fsdp_kwargs)

    if parallel_state.ep_enabled:
        # configure forward prefetch
        blocks = [pair[1] for pair in layer_pairs]
        experts = [pair[2] for pair in layer_pairs]
        next_blocks = blocks[1:] + [None]
        next_experts = experts[1:] + [None]
        for current_block, next_block, next_expert in zip(blocks, next_blocks, next_experts):
            if next_block is not None:
                current_block.set_modules_to_forward_prefetch([next_block, next_expert])

        # configure backward prefetch
        rev_blocks = list(reversed(blocks))
        rev_experts = list(reversed(experts))
        prev_blocks = rev_blocks[1:] + [None]
        prev_experts = rev_experts[1:] + [None]
        for current_block, prev_block, prev_expert in zip(rev_blocks, prev_blocks, prev_experts):
            if prev_block is not None:
                current_block.set_modules_to_backward_prefetch([prev_block, prev_expert])

    # Handle meta initialization for FSDP2 (fallback if pre-load not done)
    if kwargs.get("init_device") == "meta":
        if weights_path is None:
            model.to_empty(device="cuda")
            model.init_weights()
        else:
            from torch.distributed.tensor import distribute_tensor

            logger.info_rank0("starting to load model weights...")
            load_model_weights(model, weights_path, "cuda", dtensor_factory=distribute_tensor)

    # Register grad norm clipping method for FSDP2
    from .fsdp2 import clip_grad_norm as clip_grad_norm_fn

    model.clip_grad_norm_ = types.MethodType(clip_grad_norm_fn, model)

    return model


def build_parallelize_model(
    model: "nn.Module",
    weights_path: Optional[str] = None,
    sharding_plan: Optional[Dict[str, Any]] = None,
    enable_full_shard: bool = True,
    enable_mixed_precision: bool = True,
    enable_gradient_checkpointing: bool = True,
    basic_modules: Optional[List[str]] = None,
    **kwargs,
) -> "nn.Module":
    """
    Applies parallel strategies to the model.
    """
    parallel_state = get_parallel_state()
    fsdp_no_shard_states = None

    if not parallel_state.fsdp_enabled:
        if kwargs.get("init_device") != "cuda":
            raise ValueError("Only FSDP training supports `init_device=cpu` or `init_device=meta`.")
        if kwargs.pop("enable_fsdp_offload", False):
            raise ValueError("Only FSDP training supports `enable_fsdp_offload`.")

    if enable_mixed_precision:  # upcast to float32 before feed it to optimizer
        model = model.float()

    if enable_gradient_checkpointing and hasattr(model, "gradient_checkpointing_enable"):
        logger.info_rank0("Enable gradient checkpointing.")
        use_reentrant = kwargs.pop("enable_reentrant", False)
        if use_reentrant:
            torch.utils.checkpoint.CheckpointFunction = CheckpointFunction

        model.gradient_checkpointing_enable(
            gradient_checkpointing_kwargs={
                "use_reentrant": use_reentrant,
                "context_fn": kwargs.pop("recompute_context_fn", noop_context_fn),
            },
        )

    if parallel_state.tp_enabled:
        logger.info_rank0("Apply tensor parallel to the model.")
        model = parallelize_module(
            model,
            device_mesh=parallel_state.tp_mesh,
        )

    if parallel_state.fsdp_enabled:
        logger.info_rank0(f"Apply data parallel to the model: {parallel_state.dp_mode}.")
        if parallel_state.dp_mode == "fsdp2":
            model = parallelize_model_fsdp2(
                model=model,
                weights_path=weights_path,
                enable_full_shard=enable_full_shard,
                enable_mixed_precision=enable_mixed_precision,
                basic_modules=basic_modules,
                **kwargs,
            )
        elif parallel_state.dp_mode == "fsdp1":
            model = parallelize_model_fsdp1(
                model=model,
                weights_path=weights_path,
                enable_full_shard=enable_full_shard,
                enable_mixed_precision=enable_mixed_precision,
                basic_modules=basic_modules,
                fsdp_no_shard_states=fsdp_no_shard_states,
                **kwargs,
            )
        else:
            ddp_kwargs = {"device_ids": [parallel_state.local_rank]}
            if enable_mixed_precision:
                logger.info_rank0("Enable mixed precision training.")
                mixed_precision = MixedPrecision(
                    param_dtype=torch.bfloat16,
                    reduce_dtype=torch.float32,
                    buffer_dtype=torch.bfloat16,
                )
                ddp_kwargs["mixed_precision"] = mixed_precision

            model = DDP(model, **ddp_kwargs)

    return model
