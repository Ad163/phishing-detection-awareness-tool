"""
Data preparation pipeline for Objective O1: clean the combined phishing email
dataset and produce stratified train/validation/test splits ready for model
training (Objective O2).

Cleaning decisions (justified against the EDA findings in tables/T03, T10):
    - Drop exact full-row duplicates (408 found in EDA, T03).
    - Drop rows with text shorter than MIN_CHARS (near-empty/corrupted; 5 rows
      found under 10 chars in EDA, T10).
    - Drop rows with text longer than MAX_CHARS (degenerate/corrupted rows;
      EDA found a max of 4,279,526 chars against a p99.9 of ~40,257, T10).
      50,000 chars is set well above p99.9 so only genuine outliers are cut.
    - Whitespace/control-character normalisation only. No lowercasing or
      punctuation stripping here: TF-IDF and the DistilBERT tokenizer each
      apply their own model-specific preprocessing downstream, so the cleaned
      text is kept as close to natural language as possible.

Split: stratified 70/15/15 train/val/test, fixed random_state=42 for
reproducibility (document this seed in the Practical Research Work chapter).
"""
import re
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]  # Dissertation/
IN_FILE = ROOT / "data" / "phishing_email.csv"
OUT_DIR = ROOT / "data" / "processed"
TABLES = ROOT / "tables"
OUT_DIR.mkdir(exist_ok=True)
TABLES.mkdir(exist_ok=True)

MIN_CHARS = 10
MAX_CHARS = 50000
RANDOM_STATE = 42
TEXT_COL = "text_combined"
LABEL_COL = "label"


def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.replace("\x00", "")  # null bytes
    s = re.sub(r"[\r\n\t]+", " ", s)  # collapse newlines/tabs to space
    s = re.sub(r" {2,}", " ", s)  # collapse repeated spaces
    return s.strip()


def main():
    print(f"Loading {IN_FILE} ...")
    df = pd.read_csv(IN_FILE)
    n_start = len(df)
    print(f"Start: {n_start} rows")

    # 1 -- drop exact full-row duplicates
    df = df.drop_duplicates()
    n_after_dedupe = len(df)
    n_dupes_removed = n_start - n_after_dedupe
    print(f"Removed {n_dupes_removed} full-row duplicates -> {n_after_dedupe} rows")

    # 2 -- clean text
    df[TEXT_COL] = df[TEXT_COL].apply(clean_text)

    # 3 -- filter length outliers
    lengths = df[TEXT_COL].str.len()
    too_short_mask = lengths < MIN_CHARS
    too_long_mask = lengths > MAX_CHARS
    n_too_short = int(too_short_mask.sum())
    n_too_long = int(too_long_mask.sum())

    df = df[~(too_short_mask | too_long_mask)].copy()
    n_final = len(df)
    print(f"Removed {n_too_short} rows under {MIN_CHARS} chars")
    print(f"Removed {n_too_long} rows over {MAX_CHARS} chars")
    print(f"Final cleaned dataset: {n_final} rows")

    # cleaning summary table (T06)
    cleaning_summary = pd.DataFrame([
        {"step": "raw combined dataset", "rows": n_start, "rows_removed": 0},
        {"step": "after removing full-row duplicates", "rows": n_after_dedupe, "rows_removed": n_dupes_removed},
        {"step": f"after removing text < {MIN_CHARS} chars", "rows": n_after_dedupe - n_too_short, "rows_removed": n_too_short},
        {"step": f"after removing text > {MAX_CHARS} chars", "rows": n_final, "rows_removed": n_too_long},
    ])
    cleaning_summary.to_csv(TABLES / "T06_cleaning_summary.csv", index=False)
    print("\nSaved T06_cleaning_summary.csv")
    print(cleaning_summary)

    # 4 -- stratified train/val/test split (70/15/15)
    train_df, temp_df = train_test_split(
        df, test_size=0.30, stratify=df[LABEL_COL], random_state=RANDOM_STATE
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, stratify=temp_df[LABEL_COL], random_state=RANDOM_STATE
    )

    train_df.to_csv(OUT_DIR / "train.csv", index=False)
    val_df.to_csv(OUT_DIR / "val.csv", index=False)
    test_df.to_csv(OUT_DIR / "test.csv", index=False)
    print(f"\nSaved train.csv ({len(train_df)}), val.csv ({len(val_df)}), test.csv ({len(test_df)}) to {OUT_DIR}")

    # split composition summary table (T08)
    split_rows = []
    for name, split_df in [("train", train_df), ("val", val_df), ("test", test_df)]:
        counts = split_df[LABEL_COL].value_counts()
        split_rows.append({
            "split": name,
            "n_rows": len(split_df),
            "n_phishing_label1": int(counts.get(1, 0)),
            "n_legitimate_label0": int(counts.get(0, 0)),
            "pct_phishing": round(counts.get(1, 0) / len(split_df) * 100, 2),
        })
    split_summary = pd.DataFrame(split_rows)
    split_summary.to_csv(TABLES / "T08_train_val_test_split_summary.csv", index=False)
    print("\nSaved T08_train_val_test_split_summary.csv")
    print(split_summary)

    print("\n=== Dataset preparation complete ===")


if __name__ == "__main__":
    main()
