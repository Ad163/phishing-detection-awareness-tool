# Phishing Detection and Awareness Tool (PDAT)

Implementation accompanying the MSc Cybersecurity dissertation *"Designing and Evaluating an Intelligent Phishing Detection and Awareness System for University Students: A Machine Learning and User-Centred Design Approach"* (PROM02, University of Sunderland).

This repository contains the technical implementation only: dataset preparation, model training and comparison, the explainable classification tool, and the evaluation study infrastructure. The dissertation write-up, ethics and consent materials, and the reference list are maintained separately and are not included here.

## Structure

```
src/data/           Dataset cleaning, splitting, and stimulus extraction scripts
src/models/         Baseline model training (TF-IDF + Logistic Regression / Random Forest)
src/writing/        Markdown-to-docx chapter converter (tooling, not dissertation content)
notebooks/          DistilBERT fine-tuning notebook (Google Colab, GPU required)
app/                Flask web application: the PDAT classification tool + the evaluation study flow
tables/             Generated result tables (dataset EDA, model comparison, functional testing)
figures/            Generated charts
IMPLEMENTATION_PLAN.md   Running technical log of the project's build, decisions, and findings
```

## Pipeline overview

1. **Dataset** (`src/data/eda.py`, `src/data/prepare_dataset.py`): a combined phishing/legitimate email dataset (Al-Subaiey et al., 2024, drawing on Enron, Ling, CEAS-08, Nazario, Nigerian Fraud and SpamAssassin) is cleaned (deduplication, length-outlier filtering) and split into stratified train/validation/test sets.
2. **Baseline models** (`src/models/train_baselines.py`): TF-IDF + Logistic Regression and TF-IDF + Random Forest, trained and evaluated locally.
3. **DistilBERT** (`notebooks/distilbert_finetuning_colab.ipynb`): fine-tuned on a GPU runtime, with Google Drive-backed checkpointing for resumability.
4. **PDAT tool** (`app/`): a Flask application serving the best-performing model with LIME-based explainability, plus the pretest/tool-interaction/posttest evaluation study flow (`app/templates/study.html`).
5. **Evaluation study data** (not in this repository): responses are stored locally and optionally mirrored to a Google Sheet via a service account, activated only once research ethics approval is granted.

## Running locally

```bash
python -m venv .venv
.venv/Scripts/activate      # Windows
pip install -r requirements.txt
python app/app.py            # serves http://localhost:5000
```

Note: `models/` (trained model artefacts) and `data/` (the dataset itself) are not tracked in this repository due to size; running the pipeline end to end requires re-running `src/data/prepare_dataset.py` and `src/models/train_baselines.py` against a locally downloaded copy of the dataset, and either fine-tuning DistilBERT via the provided notebook or supplying a pre-trained model directory at `models/distilbert_final_model/`.
