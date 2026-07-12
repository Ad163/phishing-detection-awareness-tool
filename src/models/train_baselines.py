"""
Objective O2 (part 1 of 3): train and evaluate the two classical ML baselines
- TF-IDF + Logistic Regression, and TF-IDF + Random Forest - on the cleaned,
split dataset produced by src/data/prepare_dataset.py.

The third model (fine-tuned DistilBERT) is trained separately on Kaggle
Notebooks (GPU) - see src/models/train_distilbert.py and
IMPLEMENTATION_PLAN.md Section 4 (compute strategy).

Metrics reported, per Objective O2: precision, recall, F1-score, AUC-ROC.
Evaluated on the held-out test set (never seen during fitting or vectorising).
"""
import json
import joblib
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[2]  # Dissertation/
PROCESSED = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
TABLES = ROOT / "tables"
MODELS_DIR.mkdir(exist_ok=True)
TABLES.mkdir(exist_ok=True)

TEXT_COL = "text_combined"
LABEL_COL = "label"
RANDOM_STATE = 42


def load_splits():
    train = pd.read_csv(PROCESSED / "train.csv")
    val = pd.read_csv(PROCESSED / "val.csv")
    test = pd.read_csv(PROCESSED / "test.csv")
    return train, val, test


def evaluate(name, model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc_roc = roc_auc_score(y_test, y_proba)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    print(f"\n=== {name} ===")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-score:  {f1:.4f}")
    print(f"AUC-ROC:   {auc_roc:.4f}")
    print(f"Confusion matrix: TN={tn} FP={fp} FN={fn} TP={tp}")

    return {
        "model": name,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "auc_roc": round(auc_roc, 4),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
    }


def main():
    print("Loading train/val/test splits ...")
    train, val, test = load_splits()
    print(f"train={len(train)} val={len(val)} test={len(test)}")

    # drop any rows with missing text just in case (defensive; EDA found none)
    train = train.dropna(subset=[TEXT_COL])
    test = test.dropna(subset=[TEXT_COL])

    print("\nFitting TF-IDF vectoriser on training text ...")
    vectorizer = TfidfVectorizer(
        max_features=50000,
        ngram_range=(1, 2),
        min_df=2,
        stop_words="english",
    )
    X_train = vectorizer.fit_transform(train[TEXT_COL])
    X_test = vectorizer.transform(test[TEXT_COL])
    y_train = train[LABEL_COL]
    y_test = test[LABEL_COL]
    print(f"TF-IDF vocabulary size: {len(vectorizer.vocabulary_)}")

    results = []

    print("\nTraining Logistic Regression ...")
    logreg = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    logreg.fit(X_train, y_train)
    results.append(evaluate("Logistic Regression", logreg, X_test, y_test))
    joblib.dump(logreg, MODELS_DIR / "logistic_regression.joblib")

    print("\nTraining Random Forest ...")
    rf = RandomForestClassifier(
        n_estimators=200, max_depth=None, random_state=RANDOM_STATE, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    results.append(evaluate("Random Forest", rf, X_test, y_test))
    joblib.dump(rf, MODELS_DIR / "random_forest.joblib")

    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    print(f"\nSaved models and vectoriser to {MODELS_DIR}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(TABLES / "T11_baseline_model_comparison.csv", index=False)
    print("\nSaved T11_baseline_model_comparison.csv")
    print(results_df)

    with open(MODELS_DIR / "baseline_config.json", "w") as f:
        json.dump({
            "random_state": RANDOM_STATE,
            "tfidf_max_features": 50000,
            "tfidf_ngram_range": [1, 2],
            "tfidf_min_df": 2,
            "logreg_max_iter": 1000,
            "rf_n_estimators": 200,
        }, f, indent=2)

    print("\n=== Baseline model training complete ===")


if __name__ == "__main__":
    main()
