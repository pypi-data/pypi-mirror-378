# Copyright (c) 2025, NVIDIA CORPORATION. All rights reserved.

from ..core import LLMBridge, register_model


@register_model("mixtral")
class MixtralBridge(LLMBridge):
    """
    Bridge implementation for Mixtral models.

    This class extends LLMBridge to provide specific configurations and
    optimizations for Qwen2 models, handling the conversion between
    Hugging Face Qwen2 format and Megatron-Core.
    """

    _DIRECT_MAPPING = {
        "embedding.word_embeddings.weight": "model.embed_tokens.weight",
        "decoder.final_layernorm.weight": "model.norm.weight",
        "output_layer.weight": "lm_head.weight",
    }
    _ATTENTION_MAPPING = {
        "self_attention.linear_proj.weight": [
            "model.layers.{layer_number}.self_attn.o_proj.weight"
        ],
        "self_attention.linear_qkv.layer_norm_weight": [
            "model.layers.{layer_number}.input_layernorm.weight"
        ],
        "self_attention.q_layernorm.weight": [
            "model.layers.{layer_number}.self_attn.q_norm.weight"
        ],
        "self_attention.k_layernorm.weight": [
            "model.layers.{layer_number}.self_attn.k_norm.weight"
        ],
        "self_attention.linear_qkv.weight": [
            "model.layers.{layer_number}.self_attn.q_proj.weight",
            "model.layers.{layer_number}.self_attn.k_proj.weight",
            "model.layers.{layer_number}.self_attn.v_proj.weight",
        ],
        "self_attention.linear_qkv.bias": [
            "model.layers.{layer_number}.self_attn.q_proj.bias",
            "model.layers.{layer_number}.self_attn.k_proj.bias",
            "model.layers.{layer_number}.self_attn.v_proj.bias",
        ],
    }

    _MLP_MAPPING = {
        "pre_mlp_layernorm": [
            "model.layers.{layer_number}.post_attention_layernorm.weight"
        ],
        "mlp.router.weight": [
            "model.layers.{layer_number}.block_sparse_moe.gate.weight"
        ],
        "mlp.experts.linear_fc1": [
            "model.layers.{layer_number}.block_sparse_moe.experts.{expert_id}.w1.weight",
            "model.layers.{layer_number}.block_sparse_moe.experts.{expert_id}.w3.weight",
        ],
        "mlp.experts.linear_fc2": [
            "model.layers.{layer_number}.block_sparse_moe.experts.{expert_id}.w2.weight"
        ],
    }

    def _weight_name_mapping_mlp(self, name: str) -> list[str]:
        layer_number = name.split(".")[2]
        convert_names = []
        for keyword, mapping_names in self._MLP_MAPPING.items():
            if keyword in name:
                if "{expert_id}" in mapping_names[0]:
                    expert_id = name.split("weight")[-1]
                    convert_names.extend(
                        [
                            x.format(layer_number=layer_number, expert_id=expert_id)
                            for x in mapping_names
                        ]
                    )
                else:
                    convert_names.extend(
                        [x.format(layer_number=layer_number) for x in mapping_names]
                    )
                break
        if len(convert_names) == 0:
            raise NotImplementedError(f"Unsupported parameter name: {name}")
        return convert_names

    def _build_config(self):
        """
        Build the configuration for Qwen2 models.

        Configures Qwen2-specific parameters such as QKV bias settings and
        layer normalization options.

        Returns:
            TransformerConfig: Configuration object for Qwen2 models
        """
        hf_config = self.hf_config
        return self._build_base_config(
            # MoE specific
            num_moe_experts=hf_config.num_local_experts,
            moe_aux_loss_coeff=hf_config.router_aux_loss_coef,
            moe_router_topk=hf_config.num_experts_per_tok,
            moe_router_pre_softmax=True,
            moe_router_load_balancing_type="none",  # turn off aux_loss as it hurts perf in RL
            moe_router_score_function="softmax",
            moe_shared_expert_intermediate_size=None,  # mixtral has no shared expert
            moe_shared_expert_overlap=False,  # mixtral has no shared expert
            moe_ffn_hidden_size=hf_config.intermediate_size,
            moe_router_bias_update_rate=0.001,
            moe_grouped_gemm=True,
        )
