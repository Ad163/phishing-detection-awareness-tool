# PDAT — Phishing Detection and Awareness Tool

Objective O3 prototype: web-based tool integrating the best-performing model from Objective O2 (fine-tuned DistilBERT, see `tables/T13_full_model_comparison.csv`) with LIME-based explainability, behind a simple, non-alarming, user-centred interface.

## Running locally

```bash
cd Dissertation
.venv/Scripts/python.exe app/app.py
```

Then open http://localhost:5000

First request after startup will be slow (model loading); subsequent classifications typically take a few seconds, most of that time is LIME generating the explanation (it re-runs the classifier ~200 times on perturbed versions of the input text).

## Architecture

- `app.py` — Flask backend, two routes: `GET /` (serves the interface) and `POST /classify` (runs classification + explanation).
- `model_utils.py` — loads `models/distilbert_final_model/` once at startup, exposes `classify()` and `explain()`.
- `templates/index.html` — single-page interface: paste email text, get a verdict, confidence, plain-language summary, and colour-coded word-level explanation chips.

## Why LIME, not SHAP

Chapter 2 (Section 2.6) discusses both: SHAP is more theoretically consistent but computationally more expensive, a real tradeoff for a tool meant to return an explanation close to real time. LIME was chosen as the primary explainability method for that reason. `num_samples=200` (reduced from LIME's default 5000) keeps response times reasonable at some cost to explanation stability, worth noting as a limitation if explanations are found to vary between repeated runs on the same email (a known LIME weakness also discussed in Chapter 2).

## Known limitations (carry into Chapter 3/5)

- Input is truncated to the first 500 words before LIME explanation (matches the model's own 512-token truncation, see `model_utils.explain()`), so very long emails only get explained on their opening portion.
- No persistence layer yet — this prototype only classifies; the pretest/posttest study flow (Objective O4) will need its own data collection built on top of this, likely reusing the Assignment 6 `phishing_app` CSV/Flask pattern.
- Not yet deployed anywhere public — running locally only for O3's "structural and functional testing" requirement. Public deployment (if needed for the O4 study) will need to account for the model's size (~257MB) and torch's footprint, which free-tier hosts like Render may struggle with.
