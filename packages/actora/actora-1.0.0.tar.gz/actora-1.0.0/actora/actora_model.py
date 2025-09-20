from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig, AutoModel
from transformers.models.bert.configuration_bert import BertConfig as OriginalBertConfig
from transformers.modeling_outputs import SequenceClassifierOutput, BaseModelOutputWithPoolingAndCrossAttentions
from transformers.modeling_utils import PreTrainedModel
import torch
from torch import nn
import torch.nn.functional as F
from typing import Optional, Union, Tuple, List
import math

class ActoraConfig(OriginalBertConfig):
    model_type = "actora"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "hidden_act"):
            self.hidden_act = "gelu"

def get_activation(activation_string):
    if activation_string == "gelu":
        return nn.GELU()
    elif activation_string == "relu":
        return nn.ReLU()
    elif activation_string == "tanh":
        return nn.Tanh()
    else:
        raise ValueError(f"Unsupported activation: {activation_string}")

class ActoraEmbeddings(nn.Module):
    def __init__(self, config: ActoraConfig):
        super().__init__()
        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size, padding_idx=config.pad_token_id)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        self.token_type_embeddings = nn.Embedding(config.type_vocab_size, config.hidden_size)

        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

        self.register_buffer("position_ids", torch.arange(config.max_position_embeddings).expand((1, -1)))
        self.position_embedding_type = getattr(config, "position_embedding_type", "absolute")

    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        past_key_values_length: int = 0,
    ) -> torch.Tensor:
        if input_ids is not None:
            input_shape = input_ids.size()
        else:
            input_shape = inputs_embeds.size()[:-1]

        seq_length = input_shape[1]

        if position_ids is None:
            position_ids = self.position_ids[:, past_key_values_length : seq_length + past_key_values_length]

        if token_type_ids is None:
            token_type_ids = torch.zeros(input_shape, dtype=torch.long, device=self.position_ids.device)

        if inputs_embeds is None:
            inputs_embeds = self.word_embeddings(input_ids)

        token_type_embeddings = self.token_type_embeddings(token_type_ids)

        embeddings = inputs_embeds + token_type_embeddings
        if self.position_embedding_type == "absolute":
            position_embeddings = self.position_embeddings(position_ids)
            embeddings += position_embeddings
        
        embeddings = self.LayerNorm(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings

class ActoraSdpaSelfAttention(nn.Module):
    def __init__(self, config: ActoraConfig, position_embedding_type=None):
        super().__init__()
        if config.hidden_size % config.num_attention_heads != 0 and not hasattr(config, "embedding_size"):
            raise ValueError(
                f"حجم الإخفاء ({config.hidden_size}) يجب أن يكون مضاعفًا لعدد رؤوس الانتباه "
                f"({config.num_attention_heads})"
            )

        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = config.hidden_size // config.num_attention_heads
        self.all_head_size = self.num_attention_heads * self.attention_head_size

        self.query = nn.Linear(config.hidden_size, self.all_head_size)
        self.key = nn.Linear(config.hidden_size, self.all_head_size)
        self.value = nn.Linear(config.hidden_size, self.all_head_size)

        self.dropout = nn.Dropout(config.attention_probs_dropout_prob)
        self.position_embedding_type = position_embedding_type or getattr(
            config, "position_embedding_type", "absolute"
        )
        self.is_decoder = config.is_decoder
        
        self.use_sdpa = getattr(config, "use_sdpa", True)
        self.sdpa_kernel = getattr(config, "sdpa_kernel", "math")

    def transpose_for_scores(self, x: torch.Tensor) -> torch.Tensor:
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(new_x_shape)
        return x.permute(0, 2, 1, 3)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.FloatTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        encoder_hidden_states: Optional[torch.FloatTensor] = None,
        encoder_attention_mask: Optional[torch.FloatTensor] = None,
        past_key_value: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
        output_attentions: Optional[bool] = False,
    ) -> Tuple[torch.Tensor]:
        mixed_query_layer = self.query(hidden_states)

        is_cross_attention = encoder_hidden_states is not None

        if is_cross_attention and past_key_value is not None:
            key_layer = past_key_value[0]
            value_layer = past_key_value[1]
            attention_mask = encoder_attention_mask
        elif is_cross_attention:
            key_layer = self.transpose_for_scores(self.key(encoder_hidden_states))
            value_layer = self.transpose_for_scores(self.value(encoder_hidden_states))
            attention_mask = encoder_attention_mask
        elif past_key_value is not None:
            key_layer_new = self.transpose_for_scores(self.key(hidden_states))
            value_layer_new = self.transpose_for_scores(self.value(hidden_states))
            key_layer = torch.cat([past_key_value[0], key_layer_new], dim=2)
            value_layer = torch.cat([past_key_value[1], value_layer_new], dim=2)
        else:
            key_layer = self.transpose_for_scores(self.key(hidden_states))
            value_layer = self.transpose_for_scores(self.value(hidden_states))

        query_layer = self.transpose_for_scores(mixed_query_layer)
        
        if self.use_sdpa and hasattr(F, "scaled_dot_product_attention"):
            
            attn_output = F.scaled_dot_product_attention(
                query_layer,
                key_layer,
                value_layer,
                attn_mask=attention_mask,
                dropout_p=self.dropout.p if self.training else 0.0,
                is_causal=self.is_decoder,
                scale=self.attention_head_size**-0.5
            )
            context_layer = attn_output.permute(0, 2, 1, 3).contiguous()
            new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
            context_layer = context_layer.view(new_context_layer_shape)
            attention_scores = None
        else:
            attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
            attention_scores = attention_scores / math.sqrt(self.attention_head_size)
            if attention_mask is not None:
                attention_scores = attention_scores + attention_mask
            
            attention_probs = nn.functional.softmax(attention_scores, dim=-1)
            attention_probs = self.dropout(attention_probs)

            if head_mask is not None:
                attention_probs = attention_probs * head_mask

            context_layer = torch.matmul(attention_probs, value_layer)
            context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
            new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
            context_layer = context_layer.view(new_context_layer_shape)

        outputs = (context_layer, attention_scores) if output_attentions else (context_layer,)

        if past_key_value is not None:
            new_past_key_value = (key_layer, value_layer)
            outputs = (new_past_key_value,) + outputs
        
        return outputs

class ActoraSelfOutput(nn.Module):
    def __init__(self, config: ActoraConfig):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states

class ActoraAttention(nn.Module):
    def __init__(self, config: ActoraConfig, position_embedding_type=None):
        super().__init__()
        self.self = ActoraSdpaSelfAttention(config, position_embedding_type=position_embedding_type)
        self.output = ActoraSelfOutput(config)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.FloatTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        encoder_hidden_states: Optional[torch.FloatTensor] = None,
        encoder_attention_mask: Optional[torch.FloatTensor] = None,
        past_key_value: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
        output_attentions: Optional[bool] = False,
    ) -> Tuple[torch.Tensor]:
        self_outputs = self.self(
            hidden_states,
            attention_mask,
            head_mask,
            encoder_hidden_states,
            encoder_attention_mask,
            past_key_value=past_key_value,
            output_attentions=output_attentions,
            encoder_hidden_states=None,
            encoder_attention_mask=None,
        )
        attention_output = self.output(self_outputs[0], hidden_states)
        outputs = (attention_output,) + self_outputs[1:]
        return outputs

class ActoraIntermediate(nn.Module):
    def __init__(self, config: ActoraConfig):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.intermediate_size)
        self.intermediate_act_fn = get_activation(config.hidden_act)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        return hidden_states

class ActoraOutput(nn.Module):
    def __init__(self, config: ActoraConfig):
        super().__init__()
        self.dense = nn.Linear(config.intermediate_size, config.hidden_size)
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states

class ActoraLayer(nn.Module):
    def __init__(self, config: ActoraConfig):
        super().__init__()
        self.chunk_size_feed_forward = config.chunk_size_feed_forward
        self.seq_len_dim = 1
        
        self.attention = ActoraAttention(config)
        
        self.is_decoder = config.is_decoder
        self.add_cross_attention = config.add_cross_attention

        if self.add_cross_attention:
            if not self.is_decoder:
                raise ValueError(f"{self.__class__.__name__} has `add_cross_attention=True` but is not a decoder. "
                                 f"Cross attention cannot be added to an encoder. Use `config.is_decoder=True`.")
            self.crossattention = ActoraAttention(config, position_embedding_type="absolute")
        else:
            self.crossattention = None

        self.intermediate = ActoraIntermediate(config)
        self.output = ActoraOutput(config)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.FloatTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        encoder_hidden_states: Optional[torch.FloatTensor] = None,
        encoder_attention_mask: Optional[torch.FloatTensor] = None,
        past_key_value: Optional[Tuple[Tuple[torch.FloatTensor], Optional[Tuple[torch.FloatTensor]]]] = None,
        output_attentions: Optional[bool] = False,
    ) -> Tuple[torch.Tensor]:
        self_attn_past_key_value = past_key_value[0] if past_key_value is not None else None
        cross_attn_past_key_value = past_key_value[1] if past_key_value is not None and len(past_key_value) > 1 else None

        self_attention_outputs = self.attention(
            hidden_states,
            attention_mask,
            head_mask,
            past_key_value=self_attn_past_key_value,
            output_attentions=output_attentions,
            encoder_hidden_states=None,
            encoder_attention_mask=None,
        )
        attention_output = self_attention_outputs[0]
        outputs = self_attention_outputs[1:]
        
        present_key_value = None
        if self_attn_past_key_value is not None:
            present_key_value = self_attention_outputs[-1]

        if self.add_cross_attention and encoder_hidden_states is not None:
            if self.crossattention is None:
                raise ValueError("Cross attention layer not initialized but `add_cross_attention` is True.")
            
            cross_attention_outputs = self.crossattention(
                attention_output,
                encoder_attention_mask,
                head_mask,
                encoder_hidden_states,
                encoder_attention_mask,
                past_key_value=cross_attn_past_key_value,
                output_attentions=output_attentions,
            )
            attention_output = cross_attention_outputs[0]
            outputs = outputs + cross_attention_outputs[1:]
            
            if cross_attn_past_key_value is not None:
                present_key_value = (present_key_value, cross_attention_outputs[-1])
            elif present_key_value is not None:
                present_key_value = (present_key_value, None)
            else:
                present_key_value = (None, cross_attention_outputs[-1])
        elif self.is_decoder:
            if present_key_value is not None:
                present_key_value = (present_key_value, None)
            elif cross_attn_past_key_value is not None:
                present_key_value = (None, cross_attn_past_key_value)
            else:
                present_key_value = (None, None)

        intermediate_output = self.intermediate(attention_output)
        layer_output = self.output(intermediate_output, attention_output)

        layer_output_and_attentions = (layer_output,) + outputs
        if present_key_value is not None:
            layer_output_and_attentions = layer_output_and_attentions + (present_key_value,)
        
        return layer_output_and_attentions


class ActoraEncoder(nn.Module):
    def __init__(self, config: ActoraConfig):
        super().__init__()
        self.config = config
        self.layer = nn.ModuleList([ActoraLayer(config) for _ in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.FloatTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        encoder_hidden_states: Optional[torch.FloatTensor] = None,
        encoder_attention_mask: Optional[torch.FloatTensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = False,
        output_hidden_states: Optional[bool] = False,
        return_dict: Optional[bool] = True,
    ) -> Union[Tuple[torch.Tensor], BaseModelOutputWithPoolingAndCrossAttentions]:
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None
        all_cross_attentions = () if output_attentions and self.config.add_cross_attention else None

        next_decoder_cache = () if use_cache else None
        
        for i, layer_module in enumerate(self.layer):
            if output_hidden_states:
                all_hidden_states = all_hidden_states + (hidden_states,)

            layer_past_key_value = past_key_values[i] if past_key_values is not None else None

            layer_outputs = layer_module(
                hidden_states,
                attention_mask,
                head_mask[i] if head_mask is not None else None,
                encoder_hidden_states,
                encoder_attention_mask,
                layer_past_key_value,
                output_attentions,
            )

            hidden_states = layer_outputs[0]
            if use_cache:
                next_decoder_cache += (layer_outputs[-1],)
            if output_attentions:
                all_self_attentions = all_self_attentions + (layer_outputs[1],)
                if self.config.add_cross_attention:
                    all_cross_attentions = all_cross_attentions + (layer_outputs[2],)


        if output_hidden_states:
            all_hidden_states = all_hidden_states + (hidden_states,)

        if not return_dict:
            return tuple(
                v
                for v in [
                    hidden_states,
                    next_decoder_cache,
                    all_hidden_states,
                    all_self_attentions,
                    all_cross_attentions,
                ]
                if v is not None
            )
        return BaseModelOutputWithPoolingAndCrossAttentions(
            last_hidden_state=hidden_states,
            past_key_values=next_decoder_cache,
            hidden_states=all_hidden_states,
            attentions=all_self_attentions,
            cross_attentions=all_cross_attentions,
        )

class ActoraPooler(nn.Module):
    def __init__(self, config: ActoraConfig):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.activation = nn.Tanh()

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        first_token_tensor = hidden_states[:, 0]
        pooled_output = self.dense(first_token_tensor)
        pooled_output = self.activation(pooled_output)
        return pooled_output

class ActoraModel(PreTrainedModel):
    config_class = ActoraConfig
    base_model_prefix = "actora"
    _requires_load_in_prior_context = True

    def __init__(self, config: ActoraConfig, add_pooling_layer: bool = True):
        super().__init__(config)
        self.config = config
        self.embeddings = ActoraEmbeddings(config)
        self.encoder = ActoraEncoder(config)
        self.pooler = ActoraPooler(config) if add_pooling_layer else None
        
        self.post_init()
    
    def get_input_embeddings(self) -> nn.Embedding:
        return self.embeddings.word_embeddings

    def set_input_embeddings(self, value: nn.Embedding):
        self.embeddings.word_embeddings = value

    def _prepare_attention_mask(self, attention_mask, input_shape, past_key_values_length):
        if attention_mask is None:
            return attention_mask
        
        attention_mask = attention_mask.to(self.device)

        if attention_mask.dim() == 3:
            extended_attention_mask = attention_mask[:, None, :, :]
        elif attention_mask.dim() == 2:
            extended_attention_mask = attention_mask[:, None, None, :]
        else:
            raise ValueError(
                f"Wrong shape for input_ids (shape {input_shape}) or attention_mask (shape {attention_mask.shape})"
            )
        
        extended_attention_mask = extended_attention_mask.to(dtype=self.dtype)
        extended_attention_mask = (1.0 - extended_attention_mask) * -10000.0
        return extended_attention_mask


    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        encoder_hidden_states: Optional[torch.Tensor] = None,
        encoder_attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple[torch.Tensor], BaseModelOutputWithPoolingAndCrossAttentions]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("لا يمكنك تحديد كل من input_ids و inputs_embeds في نفس الوقت في ActoraModel")
        elif input_ids is not None:
            input_shape = input_ids.size()
        elif inputs_embeds is not None:
            input_shape = inputs_embeds.size()[:-1]
        else:
            raise ValueError("يجب توفير إما input_ids أو inputs_embeds لـ ActoraModel")

        batch_size, seq_length = input_shape
        device = input_ids.device if input_ids is not None else inputs_embeds.device

        extended_attention_mask: torch.Tensor = self._prepare_attention_mask(attention_mask, input_shape, 0)
        
        head_mask = self.get_head_mask(head_mask, self.config.num_hidden_layers)

        embedding_output = self.embeddings(
            input_ids=input_ids,
            position_ids=position_ids,
            token_type_ids=token_type_ids,
            inputs_embeds=inputs_embeds,
            past_key_values_length=0
        )

        encoder_outputs = self.encoder(
            embedding_output,
            attention_mask=extended_attention_mask,
            head_mask=head_mask,
            encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_attention_mask,
            past_key_values=past_key_values,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        sequence_output = encoder_outputs[0]
        pooled_output = self.pooler(sequence_output) if self.pooler is not None else None

        if not return_dict:
            return (sequence_output, pooled_output) + encoder_outputs[1:]

        return BaseModelOutputWithPoolingAndCrossAttentions(
            last_hidden_state=sequence_output,
            pooler_output=pooled_output,
            past_key_values=encoder_outputs.past_key_values,
            hidden_states=encoder_outputs.hidden_states,
            attentions=encoder_outputs.attentions,
            cross_attentions=encoder_outputs.cross_attentions,
        )
    
    def _load_state_dict_into_model(self, state_dict, prefix, model_to_load, _fast_init=True, _ignore_mismatched_sizes=False, _expected_keys=None):
        new_state_dict = {}
        for k, v in state_dict.items():
            if k.startswith("bert."):
                new_key = k.replace("bert.", f"{prefix}.")
            elif k.startswith("base_model_prefix."):
                new_key = k.replace("base_model_prefix.", f"{prefix}.")
            elif k.startswith("actora."):
                new_key = k
            else:
                new_key = f"{prefix}.{k}" if prefix and not k.startswith(prefix) else k
            new_state_dict[new_key] = v
        
        final_state_dict = {}
        for k, v in new_state_dict.items():
            if k.startswith(f"{prefix}."):
                final_state_dict[k[len(f"{prefix}."):]] = v
            else:
                final_state_dict[k] = v

        return super()._load_state_dict_into_model(
            final_state_dict, "", model_to_load, _fast_init=_fast_init, _ignore_mismatched_sizes=_ignore_mismatched_sizes, _expected_keys=_expected_keys
        )

class ActoraForSequenceClassification(PreTrainedModel):
    config_class = ActoraConfig
    base_model_prefix = "actora"
    _auto_class = AutoModelForSequenceClassification

    def __init__(self, config: ActoraConfig):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.config = config

        self.actora = ActoraModel(config, add_pooling_layer=True)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)

        self.post_init()
    
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple[torch.Tensor], SequenceClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.actora(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        pooled_output = outputs.pooler_output

        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)

        loss = None
        if labels is not None:
            if self.config.problem_type is None:
                if self.num_labels == 1:
                    self.config.problem_type = "regression"
                elif self.num_labels > 1 and (labels.dtype == torch.long or labels.dtype == torch.int):
                    self.config.problem_type = "single_label_classification"
                else:
                    self.config.problem_type = "multi_label_classification"

            if self.config.problem_type == "regression":
                loss_fct = nn.MSELoss()
                if self.num_labels == 1:
                    loss = loss_fct(logits.squeeze(), labels.squeeze())
                else:
                    loss = loss_fct(logits, labels)
            elif self.config.problem_type == "single_label_classification":
                loss_fct = nn.CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            elif self.config.problem_type == "multi_label_classification":
                loss_fct = nn.BCEWithLogitsLoss()
                loss = loss_fct(logits, labels.float())

        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output

        return SequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )

    def _load_state_dict_into_model(self, state_dict, prefix, model_to_load, _fast_init=True, _ignore_mismatched_sizes=False, _expected_keys=None):
        actora_state_dict = {}
        classifier_state_dict = {}
        
        for k, v in state_dict.items():
            if k.startswith("actora."):
                actora_state_dict[k[len("actora."):]] = v
            else:
                classifier_state_dict[k] = v
        
        missing_keys_actora, unexpected_keys_actora = model_to_load.actora._load_state_dict_into_model(
            actora_state_dict, "", model_to_load.actora, _fast_init=_fast_init, _ignore_mismatched_sizes=_ignore_mismatched_sizes
        )
        
        missing_keys_classifier, unexpected_keys_classifier = model_to_load.classifier.load_state_dict(
            classifier_state_dict, strict=False
        )
        
        missing_keys = [f"actora.{k}" for k in missing_keys_actora] + missing_keys_classifier
        unexpected_keys = [f"actora.{k}" for k in unexpected_keys_actora] + unexpected_keys_classifier

        return missing_keys, unexpected_keys