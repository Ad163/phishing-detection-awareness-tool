"""
EDA pass on the combined phishing email dataset (Objective O1).
Saves all summary tables to Dissertation/tables/ using naming convention:
    T<NN>_<short_description>.csv
Figures (if any) go to Dissertation/figures/ using the same numbering.
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # Dissertation/
DATA = ROOT / "data" / "phishing_email.csv"
RAW_DIR = ROOT / "data" / "raw"
TABLES = ROOT / "tables"
TABLES.mkdir(exist_ok=True)

pd.set_option("display.max_columns", None)

print(f"Loading {DATA} ...")
df = pd.read_csv(DATA)
print(f"Combined file shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# ---------------------------------------------------------------------------
# T01 — basic shape / schema summary
# ---------------------------------------------------------------------------
schema = pd.DataFrame({
    "column": df.columns,
    "dtype": [str(t) for t in df.dtypes],
    "n_missing": df.isna().sum().values,
    "pct_missing": (df.isna().mean() * 100).round(2).values,
    "n_unique": [df[c].nunique() for c in df.columns],
})
schema.to_csv(TABLES / "T01_schema_summary.csv", index=False)
print("\nSaved T01_schema_summary.csv")
print(schema)

# ---------------------------------------------------------------------------
# T02 — class balance (label column)
# ---------------------------------------------------------------------------
label_col = "label" if "label" in df.columns else df.columns[-1]
class_counts = df[label_col].value_counts(dropna=False).rename_axis("label").reset_index(name="count")
class_counts["pct"] = (class_counts["count"] / len(df) * 100).round(2)
class_counts.to_csv(TABLES / "T02_class_balance.csv", index=False)
print("\nSaved T02_class_balance.csv")
print(class_counts)

# ---------------------------------------------------------------------------
# T03 — duplicate check (full-row duplicates, and duplicate email bodies)
# ---------------------------------------------------------------------------
n_full_dupes = df.duplicated().sum()
body_col = "body" if "body" in df.columns else None
n_body_dupes = df.duplicated(subset=[body_col]).sum() if body_col else None
dupe_summary = pd.DataFrame({
    "check": ["full_row_duplicates", "duplicate_email_bodies"],
    "count": [n_full_dupes, n_body_dupes],
    "pct_of_total": [
        round(n_full_dupes / len(df) * 100, 2),
        round(n_body_dupes / len(df) * 100, 2) if n_body_dupes is not None else None,
    ],
})
dupe_summary.to_csv(TABLES / "T03_duplicate_check.csv", index=False)
print("\nSaved T03_duplicate_check.csv")
print(dupe_summary)

# ---------------------------------------------------------------------------
# T04 — missing values by column x label (does missingness correlate with class?)
# ---------------------------------------------------------------------------
missing_by_label = df.groupby(label_col).apply(lambda g: g.isna().mean() * 100).round(2)
missing_by_label.to_csv(TABLES / "T04_missingness_by_label.csv")
print("\nSaved T04_missingness_by_label.csv")

# ---------------------------------------------------------------------------
# T05 — text length distribution, by class
# The pre-combined file only has ['text_combined', 'label'] — subject+body
# were already merged into one field, so we work with that directly.
# ---------------------------------------------------------------------------
text_col = "text_combined" if "text_combined" in df.columns else body_col
if text_col:
    df["_text_len_chars"] = df[text_col].astype(str).str.len()
    df["_text_len_words"] = df[text_col].astype(str).str.split().str.len()

len_cols = [c for c in ["_text_len_chars", "_text_len_words"] if c in df.columns]
if len_cols:
    text_len_stats = df.groupby(label_col)[len_cols].describe().round(1)
    text_len_stats.to_csv(TABLES / "T05_text_length_stats_by_label.csv")
    print("\nSaved T05_text_length_stats_by_label.csv")
    print(text_len_stats)

# ---------------------------------------------------------------------------
# T06 — URL presence by class (if 'urls' column exists)
# ---------------------------------------------------------------------------
if "urls" in df.columns:
    url_by_label = df.groupby(label_col)["urls"].value_counts(normalize=True).mul(100).round(2).rename("pct").reset_index()
    url_by_label.to_csv(TABLES / "T06_url_presence_by_label.csv", index=False)
    print("\nSaved T06_url_presence_by_label.csv")
    print(url_by_label)

# ---------------------------------------------------------------------------
# T07/T08 — date range coverage — evidence for the "dataset age / concept drift"
# limitation. The combined file has no date column (dropped during merge), so
# pull dates from the raw source files that retain them (CEAS, Nazario,
# Nigerian_Fraud, SpamAssasin all have a 'date' column per the Kaggle schema;
# Enron and Ling do not).
# ---------------------------------------------------------------------------
date_rows = []
for fname in ["CEAS_08.csv", "Nazario.csv", "Nigerian_Fraud.csv", "SpamAssasin.csv"]:
    fpath = RAW_DIR / fname
    if not fpath.exists():
        continue
    try:
        raw = pd.read_csv(fpath, usecols=lambda c: c.lower() in ("date", "label"), low_memory=False)
    except Exception as e:
        print(f"Could not read date column from {fname}: {e}")
        continue
    date_col = next((c for c in raw.columns if c.lower() == "date"), None)
    if date_col is None:
        continue
    parsed = pd.to_datetime(raw[date_col], errors="coerce", utc=True)
    date_rows.append({
        "source_file": fname,
        "n_rows": len(raw),
        "n_parseable_dates": int(parsed.notna().sum()),
        "n_unparseable_dates": int(parsed.isna().sum()),
        "min_date": parsed.min(),
        "max_date": parsed.max(),
    })

if date_rows:
    date_summary = pd.DataFrame(date_rows)
    date_summary.to_csv(TABLES / "T07_date_range_coverage_by_source.csv", index=False)
    print("\nSaved T07_date_range_coverage_by_source.csv")
    print(date_summary)

# ---------------------------------------------------------------------------
# T09 — row count contributed by each raw source file (provenance breakdown).
# Uses pandas (proper CSV parsing), not naive newline counting — email bodies
# contain embedded newlines inside quoted fields, which inflates a raw
# line-count hugely (confirmed: naive counting gave CEAS_08.csv "1.3M rows",
# which is impossible given the combined file is only 82,486 rows total).
# ---------------------------------------------------------------------------
source_rows = []
if RAW_DIR.exists():
    for f in sorted(RAW_DIR.glob("*.csv")):
        try:
            n = sum(len(chunk) for chunk in pd.read_csv(f, usecols=[0], chunksize=20000, low_memory=False))
        except Exception as e:
            n = f"error: {e}"
        source_rows.append({"source_file": f.name, "row_count": n})
source_df = pd.DataFrame(source_rows)
source_df.to_csv(TABLES / "T09_raw_source_file_row_counts.csv", index=False)
print("\nSaved T09_raw_source_file_row_counts.csv")
print(source_df)

# ---------------------------------------------------------------------------
# T10 — text length outlier check — flags rows that need inspection/cleaning
# before training (extreme outliers found on first pass: max text length in
# the millions of characters for some rows).
# ---------------------------------------------------------------------------
if text_col:
    outlier_thresholds = {
        "p99_chars": df["_text_len_chars"].quantile(0.99),
        "p999_chars": df["_text_len_chars"].quantile(0.999),
        "max_chars": df["_text_len_chars"].max(),
        "n_over_50000_chars": int((df["_text_len_chars"] > 50000).sum()),
        "n_over_100000_chars": int((df["_text_len_chars"] > 100000).sum()),
        "n_under_10_chars": int((df["_text_len_chars"] < 10).sum()),
    }
    outlier_df = pd.DataFrame([outlier_thresholds])
    outlier_df.to_csv(TABLES / "T10_text_length_outlier_check.csv", index=False)
    print("\nSaved T10_text_length_outlier_check.csv")
    print(outlier_df)

print("\n=== EDA pass complete. All tables saved to:", TABLES, "===")
