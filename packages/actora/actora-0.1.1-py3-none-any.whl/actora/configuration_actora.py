from transformers.models.bert.configuration_bert import BertConfig as OriginalBertConfig

class ActoraConfig(OriginalBertConfig):
    model_type = "actora"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "hidden_act"):
            self.hidden_act = "gelu"