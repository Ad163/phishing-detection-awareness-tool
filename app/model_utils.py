"""
Loads the fine-tuned DistilBERT model (winner of Objective O2's three-way
comparison, tables/T13_full_model_comparison.csv) and provides:
    - predict_proba(texts)  -> class probabilities, in the shape LIME expects
    - classify(text)        -> verdict + confidence for a single email
    - explain(text)         -> LIME word-level attribution for the verdict

Label convention (fixed at training time in the Colab notebook, must match
here): 0 = Legitimate, 1 = Phishing.
"""
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from lime.lime_text import LimeTextExplainer

MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "distilbert_final_model"
MAX_LENGTH = 512
LABEL_NAMES = {0: "Legitimate", 1: "Phishing"}

_tokenizer = None
_model = None
_explainer = LimeTextExplainer(class_names=[LABEL_NAMES[0], LABEL_NAMES[1]])


def load():
    global _tokenizer, _model
    if _model is None:
        if not MODEL_DIR.exists():
            raise FileNotFoundError(
                f"Model directory not found at {MODEL_DIR}. "
                "Download 'distilbert_final_model' from the Colab notebook's Drive output first."
            )
        _tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
        _model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
        _model.eval()
    return _tokenizer, _model


def predict_proba(texts, batch_size=32):
    """Returns an (n_samples, 2) array of [P(Legitimate), P(Phishing)]. Required shape for LIME."""
    tokenizer, model = load()
    all_probs = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = list(texts[i:i + batch_size])
            enc = tokenizer(
                batch, truncation=True, max_length=MAX_LENGTH, padding=True, return_tensors="pt"
            )
            logits = model(**enc).logits
            probs = torch.softmax(logits, dim=1).numpy()
            all_probs.append(probs)
    return np.concatenate(all_probs, axis=0)


def classify(text: str) -> dict:
    probs = predict_proba([text])[0]
    pred_idx = int(np.argmax(probs))
    return {
        "verdict": LABEL_NAMES[pred_idx],
        "confidence": float(probs[pred_idx]),
        "phishing_probability": float(probs[1]),
        "legitimate_probability": float(probs[0]),
    }


def explain(text: str, num_features: int = 10, num_samples: int = 100):
    """
    Returns a list of (word, weight) tuples for the Phishing class.
    Positive weight = pushed the model toward "Phishing".
    Negative weight = pushed the model toward "Legitimate".

    Only the first ~500 words are passed to LIME: the model itself truncates
    at 512 tokens, so perturbing words beyond that window would not affect
    the prediction and would only slow down the explanation.
    """
    words = text.split()
    truncated_text = " ".join(words[:500])

    exp = _explainer.explain_instance(
        truncated_text, predict_proba, num_features=num_features, num_samples=num_samples, labels=[1]
    )
    return exp.as_list(label=1)
