import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Optional

from .modeling_actora import ActoraConfig, ActoraModel, ActoraForSequenceClassification

num_cols = ['interactions','comments','shares','liked','loved',
            'haha','wow','sad','angry','support']

emoji_map = {
    'liked': "👍",
    'loved': "❤️",
    'haha': "😂",
    'wow': "😮",
    'sad': "😢",
    'angry': "😡",
    'support': "🤝",
    'shares': "🔄",
    'comments': "💬",
    'interactions': "✨"
}

class ActoraPredictor:

    def __init__(self, model_name_or_path: str = "amrtweg/Actora_full", device: Optional[str] = None):
        self.model_name_or_path = model_name_or_path
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")

        print(f"🔄 تهيئة ActoraPredictor. تحميل التوكنايزر والنموذج من {model_name_or_path} إلى {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path)
        self.model.to(self.device)
        self.model.eval()
        print("✅ تم تهيئة ActoraPredictor بنجاح.")

    def predict(self, text: str) -> dict:

        enc = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        enc = {k: v.to(self.device) for k, v in enc.items()}
        with torch.no_grad():
            outputs = self.model(**enc)
            logits = outputs.logits
            preds = torch.expm1(logits) 
        
        preds[preds < 0] = 0 
        
        emoji_preds = {emoji_map[k]: int(round(v)) for k, v in zip(num_cols, preds[0].cpu().numpy())}
        return emoji_preds

def load_actora_predictor(model_name_or_path: str = "amrtweg/Actora_full", device: Optional[str] = None) -> ActoraPredictor:
    """
    دالة مساعدة لتحميل وإرجاع مثيل ActoraPredictor.
    """
    return ActoraPredictor(model_name_or_path=model_name_or_path, device=device)