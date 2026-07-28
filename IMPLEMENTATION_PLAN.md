# PROM02 Dissertation — Implementation Plan

**Project:** Designing and Evaluating an Intelligent Phishing Detection and Awareness System for University Students: A Machine Learning and User-Centred Design Approach
**Student:** David Adeyemi (250310441), MSc Cybersecurity, University of Sunderland
**Deadline:** 28 August 2026, 23:59 (single PDF, Canvas), 15,000 words excl. references/appendices
**Plan created:** 10 July 2026

---

## 1. The two lanes of work

| Lane | What it produces | Depends on |
|---|---|---|
| **A — Build the classifier** | A trained ML model (best of Logistic Regression / Random Forest / DistilBERT) with LIME/SHAP explainability, wrapped in a Flask web tool (PDAT) | Labelled email dataset |
| **B — Test it on humans** | Pre/post detection-accuracy scores, SUS usability score, NASA-TLX workload score from 30+ student participants | A working tool from Lane A |

Lane A must finish (or at least produce a working prototype) before Lane B's study can run. Dissertation writing (Chapters 1–2) runs in parallel with both from day one.

---

## 2. Dataset decision (Objective O1)

**Chosen dataset:** Kaggle "Phishing Email Dataset" (Naser Abdullah Alam, combining Enron, Ling, CEAS-08, Nazario, Nigerian Fraud, SpamAssassin). ~82,500 emails (42,891 phishing / 39,595 legitimate). Already downloaded and unzipped to `Dissertation/data/`.

- Cite: Al-Subaiey, A., Al-Thani, M., Alam, N.A., Antora, K.F., Khandakar, A. and Zaman, S.A.U. (2024) 'Novel interpretable and robust web-based AI platform for phishing email detection', *arXiv preprint* arXiv:2405.11619.
- This is a superset of the three sources named in the Terms of Reference (Enron, CEAS-08, SpamAssassin) — no proposal deviation.
- **Known limitation to state explicitly in the dissertation**: source emails date mostly from 2001–2008 (concept drift vs. modern phishing tactics — cloud-share links, MFA-fatigue, QR phishing, AI-generated text). Plan to acknowledge this in Practical Work/Evaluation chapters, and optionally supplement with a small hand-built "modern-style" validation set later if time allows.
- `data/phishing_email.csv` is the pre-combined file — likely the primary training source, saving the manual-merge step in O1.2.

---

## 3. Folder structure (created 10 July 2026)

```
Dissertation/
├── IMPLEMENTATION_PLAN.md   ← this file
├── data/
│   ├── raw/                 ← 6 source CSVs + archive.zip (untouched)
│   ├── phishing_email.csv   ← pre-combined dataset, primary working file
│   ├── interim/             ← partially cleaned/merged data
│   └── processed/           ← final train/val/test splits
├── notebooks/                ← EDA and experiment notebooks
├── src/
│   ├── data/                 ← loading/cleaning code
│   ├── features/             ← TF-IDF / tokenisation code
│   ├── models/                ← training scripts (LR, RF, DistilBERT)
│   └── evaluation/            ← metrics, comparison code
├── models/                    ← saved trained model artefacts (large — keep out of any future git repo)
├── app/                       ← the PDAT Flask tool (mirrors Assignment 6's phishing_app structure)
│   ├── templates/
│   └── static/
├── study/
│   ├── instruments/           ← SUS + NASA-TLX questionnaire templates
│   ├── stimuli/                ← pretest/posttest email sets (build from Assignment 6's 10 emails + new equivalent batch)
│   ├── consent_ethics/         ← ethics application + consent forms
│   └── responses/              ← collected study data (raw + cleaned)
├── analysis/                   ← statistical analysis of study results (paired t-tests, Cohen's d, SUS/NASA-TLX scoring)
├── figures/                    ← exported charts for dissertation + appendices
├── writing/
│   └── chapters/                ← dissertation drafts, one file per chapter
└── references/                  ← bibliography management
```

---

## 4. Compute strategy

| Task | Where | Why |
|---|---|---|
| Data cleaning, EDA, TF-IDF, Logistic Regression, Random Forest | **Local machine** (i7-1165G7, 16GB RAM) | No GPU required; runs in seconds–minutes |
| DistilBERT fine-tuning | **Kaggle Notebooks** (fallback: Google Colab) | No dedicated GPU locally (Iris Xe integrated only); dataset already hosted on Kaggle so no re-upload needed; free weekly GPU quota (P100/T4) |
| Flask app + inference (single-email classification) | **Local machine** | Inference on an already-trained DistilBERT is cheap even on CPU; only *training* needs GPU |
| Statistical analysis of study data | **Local machine** | pandas/scipy, small dataset (~30 rows) |

Workflow: train DistilBERT on Kaggle → download fine-tuned weights into `models/` → embed in local Flask app.

---

## 5. Writing plan

Per the module handbook (`Dissertation/Info.docx`): the Introduction is written in stages throughout the project; the Abstract is written last.

- **Chapter 1 (Introduction)** — **drafted 11 July 2026** (~3,000 words). Saved as both `writing/chapters/01_introduction.md` (editable source) and `writing/chapters/01_introduction.docx` (submission-formatted). Update iteratively as the project progresses.
- **Chapter 2 (Literature Review)** — **drafted 11 July 2026** (~4,050 words), fully rewritten (not copied) from the CETM44 base, restructured into 9 sections: cognitive vulnerability, students as an at-risk population, limits of existing interventions, ML approaches to phishing detection, XAI and trust, UCD of security interfaces, usability/workload evaluation methods, and a synthesis identifying the research gap. Includes one embedded comparison table, Table 2.1 (literature gap-analysis matrix showing no prior study covers all five key dimensions this project combines) — an earlier draft also had a second table comparing ML models, but it was dropped as redundant with prose already covering the same ground (see Section 11, formatting conventions). Saved as `writing/chapters/02_literature_review.md` and `.docx`. Confirm the self-plagiarism handling approach with supervisor if asked.
- **`src/writing/md_to_docx.py` now supports Markdown tables** (pipe syntax), rendering them as real Word tables (Table Grid style, bold header row) — use this for any future chapter-embedded comparison table. See `tables/README.md` for the distinction between these chapter-embedded tables (chapter-numbered, e.g. Table 2.1) and the computed result tables in `tables/` (T-numbered).
- **Chapters 3+ (Practical Work, Results, Evaluation, Conclusions)** — cannot be written until there's practical work/results to report. Draft incrementally as each milestone (D1–D6) completes.
- **Workflow**: every chapter is written first in Markdown (`writing/chapters/0N_name.md`, easy to edit/version), then converted to a submission-formatted `.docx` via `src/writing/md_to_docx.py`. That script applies the module's exact formatting requirements from `Info.docx`: A4 paper, Times New Roman 12pt, 25mm margins (above the 20mm minimum), 1.5 line spacing, numbered pages in the footer. Re-run the converter any time the `.md` source changes: `python src/writing/md_to_docx.py writing/chapters/0N_name.md writing/chapters/0N_name.docx`. All chapters must exist in `.docx` form, not just Markdown, per explicit student instruction (11 July 2026).
- **Reused assets**: CETM44 findings (75.3% baseline accuracy, no significant training effect, over-suspicion bias) are citable as the student's own preliminary research motivating this project. The 10 Assignment 6 email stimuli are earmarked for reuse as pretest material (per the original proposal) — a second, equivalent-difficulty batch is still needed for posttest to avoid memory/practice effects.

---

## 6. Schedule (from `PROM02_Filled_v2.docx`, milestones M1–M6)

| # | Milestone | Original target | Status as of 10 Jul 2026 |
|---|---|---|---|
| M1 | Dataset ready (D1) | 10/07/2026 | **In progress today** — dataset acquired, EDA/cleaning starting now |
| M2 | Best model selected (D2) | 24/07/2026 | Not started |
| M3 | Prototype functional (D3) | 31/07/2026 | Not started |
| M4 | Evaluation data collected (D4) | 07/08/2026 | Not started (needs ethics approval first) |
| M5 | Analysis complete (D5) | 14/08/2026 | Not started |
| M6 | Dissertation submitted (D6) | 29/08/2026 | Not started |

Note: M1's original window was 20 Jun–10 Jul; real work is starting on the deadline day itself. Recommend either compressing M2–M3 slightly or treating this as the revised baseline going forward — flag to supervisor if the overall 29 Aug submission looks at risk once M2/M3 durations are confirmed in practice.

---

## 7. Immediate next actions (in order)

1. ~~EDA on `data/phishing_email.csv`~~ — **done 10 Jul 2026**. See Section 9 below for findings; tables saved to `tables/`.
2. ~~Data cleaning pipeline~~ — **done 11 Jul 2026**. See Section 12 below for findings; `src/data/prepare_dataset.py`, splits in `data/processed/`.
3. ~~Chapter 1 draft~~ — **done 11 Jul 2026**.
4. ~~Chapter 2 restructuring~~ — **done 11 Jul 2026**.
5. ~~Baseline models: TF-IDF + Logistic Regression, TF-IDF + Random Forest~~ — **done 11 Jul 2026**. See Section 12; `src/models/train_baselines.py`. *(Next: DistilBERT.)*
6. Kick off ethics application for the human evaluation study (Lane B) early — this has external turnaround time and should not wait for Lane A to finish.
7. DistilBERT fine-tuning on Kaggle Notebooks once baselines are working. *(Next task.)*
8. Model comparison report (D2) — precision/recall/F1/AUC-ROC across all three models (baselines already tabulated in `tables/T11_baseline_model_comparison.csv`; add DistilBERT row once trained).
9. Build PDAT prototype (`app/`) around the winning model + LIME/SHAP.
10. Design pretest/posttest stimuli batches (`study/stimuli/`) + SUS/NASA-TLX instruments (`study/instruments/`).
11. Run the 30+ participant study (Lane B) once ethics approval is granted and the prototype is tested.
12. Statistical analysis (`analysis/`) — paired t-tests, effect sizes, SUS/NASA-TLX scoring.
13. Write Chapters 3–6, then Abstract last.

---

## 9. EDA findings (10 July 2026)

Environment: Python 3.11 venv created at `Dissertation/.venv` (packages in `requirements.txt`). EDA script: `src/data/eda.py`. All tables in `tables/` (naming convention documented in `tables/README.md`).

- **Shape**: `data/phishing_email.csv` = 82,486 rows × 2 columns (`text_combined`, `label`) — subject/body were pre-merged into one text field; sender/date/URL metadata was dropped during the Kaggle author's combination step (still present in the individual raw files).
- **Class balance**: 52% phishing (label=1, n=42,891) / 48% legitimate (label=0, n=39,595) — healthy balance, no resampling needed.
- **Duplicates**: 408 full-row duplicates (0.49%) — remove in cleaning.
- **Text length outliers — needs a decision before training**: mean length is ~1,000–1,500 chars, but the max is **4,279,526 characters** (phishing class) and **107,710 words** — clearly corrupted/degenerate rows, not real emails. 56 rows exceed 50,000 chars, 11 exceed 100,000. 5 rows are under 10 chars (likely empty/near-empty). Recommend filtering both tails in the cleaning pipeline (e.g. drop <10 chars and >~20,000–50,000 chars, or cap/truncate) rather than feeding raw into TF-IDF or DistilBERT.
- **Row provenance verified**: CEAS_08=39,154, Enron=29,767, Ling=2,859, Nazario=1,565, Nigerian_Fraud=3,332, SpamAssasin=5,809 — sums exactly to 82,486, confirming the combined file is a straight concatenation of all 6 raw sources with no filtering applied yet.
- **Date coverage / concept-drift evidence** (from raw files with a `date` column — CEAS, Nazario, Nigerian_Fraud, SpamAssasin; Enron and Ling don't have one): dates are **unreliable and noisy**, not just old. Nazario is genuinely recent (2015–2022) — good. But CEAS shows a max date of **2100-05-27** and SpamAssasin shows a min date of **year 0102** — these are spoofed/malformed email date headers (common in spam/phishing), not real dates. This means the "dataset is from 2001–2008" framing from our earlier discussion needs refining: it's true in aggregate, but the raw date metadata itself is too corrupted to cite precise figures without first sanity-filtering to a plausible range (e.g. 1995–2026) — worth doing this filtering explicitly and citing the *cleaned* date range in the dissertation, plus noting spoofed date headers as an interesting data-quality observation in its own right (arguably reinforces the "attackers manipulate metadata" theme relevant to the Practical Work chapter).

## 10. Reference list audit (10 July 2026)

`80_References_Harvard.docx` (added to the project root) claimed all 80 references were "verified... links checked July 2026." That claim did not hold up under actual verification (CrossRef API cross-check on every DOI, web search on the rest). Findings:

- 9 dead/non-resolving DOIs, 8 confirmed wrong years (some off by over a decade), 2 DOIs pointing to entirely different papers, 1 altered title ([18], real paper is about anti-malware not anti-phishing behaviour).
- Notably, **[6] Liang & Xue and [20] Kumaraguru et al. were mis-dated as "2021" not just in this reference list but across multiple earlier CETM44 assignment documents in this project** — correct years are 2009 and 2007 respectively. Any dissertation prose reused from those earlier documents needs this fixed too.
- 5 references could not be verified as real papers at all ([16], [19], [42], [48], plus [18]'s topic mismatch) — need manual resourcing/replacement before submission.
- Full corrected, annotated list (with ✅/🔧/⚠️ status per entry) now lives at `references/references.md` — **use this as the master reference file going forward**, not the original docx.

## 11. Formatting conventions (set 11 July 2026)

- **No em-dashes ("—") anywhere in chapter text.** Grep every chapter `.md` file for "—" before considering it done.
- **Harvard citations only**, pulled exclusively from the corrected `references/references.md` — never from the original `80_References_Harvard.docx`.
- **Tables are captioned above, figures/images are captioned below** (standard convention). Table captions are a distinct bold line directly above the table (e.g. `**Table 2.1: Description**`), separate from the in-text sentence that references the table by name (e.g. "Table 2.1 shows..."). Both the caption and the in-text mention are required for a table to be considered valid — a table with no textual reference, or a caption with no table, should not exist.
- **Don't add a table just because a comparison could be tabulated.** Before adding one, check whether it would just restate prose that already exists (test: does removing every sentence the table duplicates leave the argument intact? If yes, the table is redundant and should be cut or the prose trimmed instead). Tables earn their place when they present something prose handles awkwardly (many items × many attributes), not as decoration. A dropped example: an early draft of Chapter 2 had a 3-model comparison table that just repeated two paragraphs already covering the same ground — removed rather than kept for its own sake.
- Table numbering is sequential per chapter with no gaps (Table 2.1, Table 2.2, ...) — if a table is removed, renumber the remaining ones rather than leaving a gap.
- **Register**: dissertation prose must read as scholarly writing, not as a decision log explaining choices to a supervisor. Avoid "the main alternative considered was X, rejected on efficiency/practical grounds", "this choice was made because it was easier/faster", "judged an acceptable tradeoff" — this reads as self-justification rather than academic argument. Instead, ground choices in methodological/theoretical merit and cite literature, the way any dissertation would. This surfaced as a real problem in an early Chapter 3 draft (13 July 2026) and was rewritten throughout — check new chapters against this before considering them done, particularly the Practical Research Work chapter where implementation-decision language creeps in naturally.
- **No project-management narration in dissertation text** — don't write things like "the supervisor confirmed X and directed Y". State facts objectively (e.g. "ethics approval remains under review; no data collection has commenced") rather than narrating supervisory conversations.
- **Workflow (changed 13 July 2026)**: chapters are delivered as `.docx` ONLY — no `.md` source files are kept in the project's `writing/chapters/` folder anymore, per explicit student instruction. To draft or revise a chapter, write the Markdown to a scratch/temp location (not the project folder), convert directly to the project's `writing/chapters/0N_name.docx` via `src/writing/md_to_docx.py`, and discard the scratch source. To make a small edit to an existing chapter, regenerate the full chapter text in scratch and overwrite the docx, rather than hand-editing the docx XML.

## 12. Data cleaning and baseline model results (11 July 2026)

**Cleaning** (`src/data/prepare_dataset.py`): started from 82,486 rows. Removed 408 exact duplicates, 6 rows under 10 characters, 56 rows over 50,000 characters (thresholds set against the T10 outlier findings, well above p99.9 of ~40,257 chars so only genuine corruption was cut). Final cleaned dataset: **82,016 rows**. Text normalisation was deliberately minimal (whitespace/control characters only, no lowercasing or punctuation stripping) so TF-IDF and the DistilBERT tokenizer can each apply their own model-specific preprocessing downstream. Summary in `tables/T06_cleaning_summary.csv`.

**Split**: stratified 70/15/15 train/val/test, `random_state=42` (document this seed in Chapter 3). Class balance preserved almost exactly across all three splits (~52.2% phishing each). Train=57,411, val=12,302, test=12,303. Summary in `tables/T08_train_val_test_split_summary.csv`. Splits saved to `data/processed/{train,val,test}.csv`.

**Baseline models** (`src/models/train_baselines.py`): TF-IDF (max_features=50,000, ngram_range=(1,2), min_df=2, English stopwords) + Logistic Regression and Random Forest (200 trees), evaluated on the held-out test set. Both saved to `models/` (`.joblib`) along with the fitted vectoriser. Results in `tables/T11_baseline_model_comparison.csv`:

| Model | Precision | Recall | F1 | AUC-ROC |
|---|---|---|---|---|
| Logistic Regression | 0.9859 | 0.9902 | 0.9880 | 0.9987 |
| Random Forest | 0.9869 | 0.9872 | 0.9871 | 0.9983 |

Both models score extremely high (~98-99% across the board). Worth flagging honestly in the Results/Discussion chapter rather than just celebrating it: this level of separability from TF-IDF alone (a purely lexical, bag-of-words-style representation) suggests the phishing emails in this dataset carry strong, dataset-specific surface-level lexical signatures, consistent with the older/less sophisticated phishing captured by these sources (see Section 9's concept-drift finding). It does not necessarily mean a deployed tool would perform this well against modern phishing that more closely mimics legitimate email style. This is a genuine limitation to discuss, not just a result to report.

**DistilBERT result (11-12 July 2026)**: fine-tuned on Colab (3 epochs, batch size 16, 512-token truncation), evaluated on the identical held-out test set as the baselines. Final model + tokenizer downloaded to `models/distilbert_final_model/` (~257MB: config.json, model.safetensors, tokenizer.json, tokenizer_config.json, training_args.bin).

**Objective O2 complete — full three-way comparison** (`tables/T13_full_model_comparison.csv`):

| Rank | Model | Precision | Recall | F1 | AUC-ROC |
|---|---|---|---|---|---|
| 1 | DistilBERT (fine-tuned) | 0.9956 | 0.9953 | 0.9955 | 0.9998 |
| 2 | Logistic Regression | 0.9859 | 0.9902 | 0.9880 | 0.9987 |
| 3 | Random Forest | 0.9869 | 0.9872 | 0.9871 | 0.9983 |

DistilBERT wins on every metric, satisfying Objective O3's "best-performing model" requirement cleanly. But the margin over the classical baselines is small (~0.7-0.8 F1 points), worth an explicit, honest discussion in Chapter 4/5 rather than treated as an unqualified win: given the baselines already sit near-ceiling from lexical signal alone (see Section 12's earlier note on the dataset's likely dated, lexically-obvious phishing patterns), DistilBERT's deeper contextual understanding has comparatively little headroom to demonstrate its advantage on *this* dataset. This is a genuinely interesting, citable limitation, not just a footnote: it suggests the real test of whether contextual understanding matters would need a harder, more modern/adversarial dataset, which is out of scope here but worth flagging as future work (ties into Objective O6 recommendations and Chapter 6).

Decision: **DistilBERT is the model carried forward into the PDAT prototype** (Objective O3), justified both by it winning on every metric (including recall, which matters most for a security detection task, minimising missed phishing) and because the explainability requirement (LIME/SHAP) directly addresses the interpretability cost of choosing the less transparent model.

## 13. PDAT prototype built and functionally tested (Objective O3, 12 July 2026)

Built: `app/model_utils.py` (loads DistilBERT, exposes `classify()` and LIME-based `explain()`), `app/app.py` (Flask backend, `GET /`, `POST /classify`), `app/templates/index.html` (paste-email interface with colour-coded word-level explanation chips, non-alarming design per the warning-fatigue literature), `app/README.md`. Explainability method: **LIME**, not SHAP, justified in Chapter 2 Section 2.6 (SHAP's extra computational cost is a real tradeoff for a tool meant to respond close to real time).

**Response-time decision**: LIME's `num_samples` reduced from 200 to 100 (single-sample test: ~24s -> ~14s). Documented as a deliberate speed/stability tradeoff; LIME's own literature-noted instability (explanations can vary between runs) grows as samples shrink, so this wasn't pushed lower without evidence it still produces coherent explanations, which it does.

**Structural and functional test** (the explicit requirement in Objective O3): ran all **40 hand-crafted email stimuli from the Assignment 6 `phishing_app`** (20 phishing + 20 legitimate, extracted directly from its `PHISHING_POOL`/`LEGIT_POOL` JS arrays, HTML-stripped to plain text) through the live `/classify` endpoint. Results in `tables/T30_pdat_functional_test.csv`.

**Result: 29/40 correct overall (72.5%)** — but this splits dramatically by class:
- **Phishing: 20/20 (100%)** — every phishing email correctly caught.
- **Legitimate: 9/20 (45%)** — more than half of modern, realistic legitimate emails misclassified as phishing (Zoom meeting invite, university library reminder, Spotify receipt, NHS appointment reminder, Microsoft Teams invite, student union newsletter, Apple receipt, Google security summary, eBay notification, gym booking confirmation, Turnitin receipt — all misclassified, several with >99% confidence).

**This is not a bug** (label mapping was re-verified correct) and **not a failure of Objective O3** (the tool is mechanically functional and structurally sound, exactly what O3 requires) — it is a genuine, well-evidenced result belonging in Chapter 4 (Results) and Chapter 5 (Discussion/Evaluation). It's the concrete, quantified confirmation of the concept-drift limitation flagged since the EDA: the training dataset's notion of "legitimate" (2001-2008-era personal/business correspondence) does not represent modern templated service/institutional emails, so the model systematically over-flags them as suspicious.

**Important cross-cutting finding**: this mirrors, almost exactly, the over-suspicion bias found in the student's own CETM44 human study (legitimate emails classified correctly less often than phishing by human participants too, 73.3% vs 77.3%). Both the human participants AND the ML tool share the same blind spot on legitimate emails, for what look like related reasons (defaulting to suspicion under uncertainty). This parallel is a strong, citable thread to build the Discussion/Conclusion chapters around — arguably one of the most interesting findings of the whole project, not a footnote.

**Response time in this test**: mean 22.8s per email (longer than the single quick sample's ~14s, because these emails are longer, more words within LIME's perturbation window). Worth factoring into Objective O4's study design — if participants interact with the tool multiple times, cumulative wait time adds up; consider whether the O4 protocol needs only one or two tool interactions per participant rather than per-email use throughout.

**Follow-up completed (12 July 2026)**: reran the same 40 emails through the two classical baselines. Result answers the question cleanly: **the over-suspicion gap is NOT dataset-wide, it's model-specific, and it runs in opposite directions for different model families.** Full comparison at `tables/T31_three_way_functional_test_comparison.csv`:

| Model | Overall | Phishing accuracy | Legitimate accuracy |
|---|---|---|---|
| Logistic Regression | 77.5% | 60.0% | 95.0% |
| Random Forest | 72.5% | 45.0% | 100.0% |
| DistilBERT | 72.5% | 100.0% | 45.0% |

This is a near-perfect **inverse pattern** between DistilBERT and Random Forest (100/45 vs 45/100) and represents one of the most valuable findings in the whole project — all three models score ~99% on the in-distribution held-out test set (Section 12), yet generalise completely differently to modern, realistic, out-of-distribution email. Interpretation for Chapter 4/5:

- The classical TF-IDF models learned **lexical signatures specific to this dataset's older phishing style** (likely the crude, spam-era vocabulary in sources like Nigerian_Fraud/Enron), so they under-detect modern, well-crafted phishing that doesn't reuse that vocabulary, while correctly recognising legitimate text (since ordinary written English hasn't changed as much as phishing tactics have).
- DistilBERT's deeper contextual understanding picked up **general structural manipulation cues** (urgency, account/security language, deadlines, links) that generalise well to catch modern phishing perfectly, but the same generalisation causes false positives on modern legitimate service emails that share surface structure with those cues (meeting invites, subscription receipts, account notifications).
- Qualitatively (see the phishing-side breakdown in T31): classical models specifically miss **official/institutional-register phishing** that mimics bureaucratic correspondence (HMRC tax refund, NHS appointment, UCAS offer, academic integrity investigation, council tax rebate), while brand-impersonation phishing with more typical scam markers (Microsoft, PayPal, DHL, Barclays, Apple ID, WhatsApp) is caught by all three models consistently.
- Practical implication worth stating explicitly: **no single model is "best" for real-world deployment on modern email** — each has a complementary failure mode. This nuances the earlier "DistilBERT wins on every metric" conclusion from the held-out test set (Section 12): that conclusion is only true *in-distribution*. Out-of-distribution, on realistic current email, the picture is genuinely a tradeoff, not a clean win.
- This also strengthens, rather than just parallels, the earlier connection to the CETM44 human study: humans and DistilBERT share an over-suspicion bias on legitimate email, while the classical models share the opposite bias (under-suspicion, i.e. missing modern phishing). All three "detectors" (two ML families plus humans) fail in different, explicable ways, none of them for the same reason.

This finding belongs prominently in Chapter 4 (Results) as a dedicated sub-section, not folded into the O2 model-comparison discussion — it's really an O3 finding (generalisation under real deployment conditions) that happens to also retrospectively contextualise O2's results.

## 14. Ethics application materials drafted (Objective O4, 12 July 2026)

Three documents drafted at `study/consent_ethics/`, both `.md` (editable source) and `.docx` (submission-formatted): `participant_information_sheet`, `consent_form`, `ethics_application`. All grounded directly in Chapter 1 Section 1.6's ethical/social/professional/legal considerations, citing the same sources (BPS 2021, UK GDPR/DPA 2018 via Great Britain 2018).

**Note**: `ethics_application.md` is a comprehensive draft covering standard institutional review sections (project summary, methodology, participants, consent, data management, risk assessment, deception/debriefing, declarations) — it has NOT been checked against the University of Sunderland's actual official ethics submission form/portal, which the student should locate and use as the definitive submission route; treat this as source material to transpose in, not a final submission itself. Bracketed placeholders ([Supervisor name], contact emails) still need filling in before use.

**Participant-code mechanism designed** (student's own idea, methodologically important): rather than collecting any identifying information, the study generates a short random anonymous code at the end of Part 1 (pretest), which the participant must re-enter to access Part 2 (posttest). This is how pretest/posttest responses get matched for the paired-samples t-test (Objective O5) without compromising anonymity. Documented in all three ethics documents. **Not yet built in Flask** — this is the next code task: extend the app with a `/study` flow (pretest -> tool interaction -> posttest -> SUS -> NASA-TLX) implementing code generation, storage, and validation (reject a posttest submission if the code doesn't exist or has already been used).

**Data storage plan**: reuse the exact pattern from Assignment 6's `phishing_app` — a Google **service account** (scoped, non-personal credential; `google-auth` + `gspread` libraries), not a personal OAuth login. Corrected the student's recollection of this as "OAuth 1" — it's actually a service account (OAuth 2.0 server-to-server), described accurately in the ethics documents since that's what will actually be implemented.

**Still needed before O4 data collection can start**: fill in placeholders (supervisor name/contact, ethics contact), locate and complete the actual University of Sunderland ethics submission process, then build the Flask study flow described above.

## 15. Flask study flow built and tested (Objective O4, 12 July 2026)

Built ahead of ethics approval, since building/testing the tool doesn't require it, only real data collection does. Once ethics is approved, only the Google Sheets credentials need to be added, no code changes required.

**New files**:
- `src/data/extract_stimuli.py` -- extracts the 40 Assignment 6 email stimuli into a permanent project asset `study/stimuli/email_pool.json`, split into two disjoint batches: pretest pool (P1-P10, L1-L10) and posttest pool (P11-P20, L11-L20). Disjoint batches mean no participant ever sees the same email twice, avoiding a memory/practice-effect confound.
- `app/study_emails.py` -- selects a balanced random subset per participant (3 phishing + 2 legitimate for both pretest and posttest) and strips ground truth before sending to the client (`public_view()`) -- scoring against ground truth happens later during analysis (O5), not in real time, so neither pretest nor posttest gives immediate correct/incorrect feedback (the right design for a genuine pre/post measurement).
- `app/study_storage.py` -- participant code generation (8-char alphanumeric, ambiguous characters like 0/O/1/I/L excluded for readability) and local-CSV-first, optional-Google-Sheets-mirror storage, mirroring Assignment 6's exact resilient pattern. Sheets mirror only activates if `GOOGLE_CREDENTIALS_JSON` + `GOOGLE_SHEET_ID` env vars are set (service account, not personal OAuth) -- silently skipped otherwise, so the whole study runs fully locally during development. Two response files: `study/responses/pretest_responses.csv` and `posttest_responses.csv`, linked by the participant code column (join at analysis time, not via in-place Sheet updates, to avoid race conditions between concurrent participants).
- `app/templates/study.html` -- 10-screen flow: consent (9 checkboxes matching the consent form) -> demographics -> pretest (5 emails, no feedback) -> code display -> tool introduction -> tool interaction (replays the SAME 5 pretest emails through the real `/classify` endpoint, showing verdict + explanation -- this is the intervention) -> code re-entry gate -> posttest (5 disjoint emails, no feedback) -> SUS (10 items) -> NASA-TLX (6 sliders, Raw/unweighted per Chapter 2's justification) -> debrief/thank-you.
- New routes added to `app/app.py`: `GET /study`, `GET /study/pretest-emails`, `POST /study/submit-pretest`, `POST /study/verify-code`, `GET /study/posttest-emails`, `POST /study/submit-posttest`.

**End-to-end tested** with a scripted simulated participant hitting every endpoint in sequence (not just unit-level): confirmed ground truth is never leaked to the client, incomplete demographic submissions are rejected (400), a valid code is correctly generated and accepted, an unknown code is correctly rejected, pretest and posttest email sets are confirmed disjoint per session, a full posttest+SUS+NASA-TLX submission succeeds, and **reusing a code for a second posttest submission is correctly rejected** (prevents duplicate submissions). CSV output verified: both response files correctly linked by participant code, exactly matching the intended schema. Test data cleared from the response CSVs afterward so they're empty and ready for real participants.

**Still to do before real data collection**: ethics approval (Section 14), fill in Google service account credentials when ready (`GOOGLE_CREDENTIALS_JSON`, `GOOGLE_SHEET_ID` env vars, no code changes needed), and decide on public hosting if the study needs to run somewhere other than the researcher's own machine (same hosting-size caveat as noted in `app/README.md` -- DistilBERT + torch's footprint may not fit free-tier hosts like Render).

## 16. Supervisor guidance received (13 July 2026) and Chapter 3 drafted

Supervisor: Randa Almadhoun (Randa.Almadhoun@sunderland.ac.uk) -- now filled into the ethics documents (`participant_information_sheet.md`/`.docx`, `ethics_application.md`/`.docx`), replacing the earlier bracketed placeholders. Student's real email also filled in (david.adeyemi@student.sunderland.ac.uk). One placeholder remains: the University of Sunderland general ethics/faculty contact in the PIS.

Ethics application was submitted externally (outside this project's tracking) and was sent back for corrections; supervisor's explicit instruction: **do not recruit participants until final ethics approval**, but continue technical work, tool evaluation, and dissertation chapters in the meantime. This is fully consistent with the project's existing structure -- Chapter 3 (Practical Research Work) and a meaningful portion of Chapter 4 (the ML model comparison and functional-test results) do not depend on Objective O4 human data at all, only the human-evaluation-specific portion of Chapter 4 (pretest/posttest scores, SUS, NASA-TLX, paired t-tests) is genuinely blocked.

**Chapter 3 (Practical Research Work) drafted (13 July 2026)**, ~2,900 words, `writing/chapters/03_practical_research_work.md` + `.docx`. Six sections: dataset construction/pre-processing (with the T06 cleaning summary as an in-chapter table), comparative model development (selection rationale, implementation, evaluation methodology -- headline results deliberately deferred to Chapter 4, only referenced where needed to justify a decision), PDAT tool development (explainability method selection reasoning, system architecture, UCD design process, structural/functional testing -- again deferring the 40-email finding's *analysis* to Chapter 4 while describing the testing *process* here), evaluation study design (within-subjects rationale, instruments, the participant-code linking mechanism, data storage, and an honest "current status" subsection reflecting the ethics delay), and a closing section on ethical/legal/social/professional considerations as applied in practice. Zero em-dashes, all citations from the corrected `references/references.md`.

**Next**: continue into Chapter 4 with the portions that don't depend on O4 (three-way model comparison analysis, the 40-email functional test finding and its cross-model comparison), leaving the human-evaluation subsection as a placeholder until real study data exists.

**Chapter 3 revised (13 July 2026)**: student flagged that the draft read like a decision log justifying choices to a supervisor ("the main alternative considered was X, rejected on efficiency grounds", "this choice was made because...", "judged an acceptable tradeoff") rather than genuine dissertation prose. Rewrote the whole chapter with an elevated, declarative scholarly register throughout — choices grounded in methodological/theoretical merit rather than practical convenience, and the "Current Status" section rewritten to remove supervisory-conversation narration ("the supervisor has confirmed...") in favour of an objective status statement. Confirmed via grep that Chapters 1-2 never had this problem, it's specific to writing about practical implementation decisions. Applied as a standing convention (see formatting conventions above) for all future chapters, especially Chapter 4/5 where the same risk exists. Also switched to docx-only delivery per student instruction — no `.md` chapter files kept in the project anymore.

**Code repository created (13 July 2026)**: student pointed out that Chapter 3 named specific in-repo file paths (`src/data/prepare_dataset.py`, `notebooks/distilbert_finetuning_colab.ipynb`, etc.) despite not including the full codebase as an appendix, meaning those references pointed at nothing for a reader. Fixed by creating a private GitHub repository (`https://github.com/Ad163/phishing-detection-awareness-tool`) containing the code only, not the dissertation write-up, ethics materials, or the reference list, and cited once in Chapter 3's introduction rather than scattering file paths through the prose. `.gitignore` excludes `/models/` (257MB DistilBERT + 154MB Random Forest, would break a normal push anyway), `/data/` (third-party dataset, not authored content), `/study/responses/` (participant data, must never be committed even accidentally), and `/writing/`, `/study/consent_ethics/`, `/references/` (personal contact details and the academic submission itself, kept out of the code repo). Note the leading slashes in `.gitignore` were necessary, unanchored patterns like `models/` were also matching nested `src/models/` and `src/writing/`, silently excluding real source files — caught by reviewing `git status` before committing, not assumed correct.

Git identity note: the machine's global git config had a pre-existing identity ("Saviour Henry" / johnsavilesh2019@gmail.com) that is NOT a stranger's leftover, it's the student's actual GitHub account under a different display name than the dissertation's "David Adeyemi" identity. Student's explicit decision: ship commits under this existing identity for now, migrate to a school email/GitHub account later when ready. Local repo config set accordingly (not global). Repo is **private** — will need supervisor/examiner invited as a collaborator, or made public, or exported as a zip at actual submission time.

## 17. Chapter 4 drafted as a partial chapter (13 July 2026)

Student asked directly whether Chapter 4 could be written before the O4 human study runs. Answer: yes for the ML-only sections, no for the human-evaluation section — split cleanly rather than waiting for everything. Drafted `writing/chapters/04_results_analysis_evaluation.docx` (~1,600 words, shorter than other chapters because Section 4.5 is a structurally complete but honestly-labelled placeholder, not padded to look finished).

Six sections: introduction (states plainly what's available now vs pending), the Objective 2 three-way model comparison analysis (Table 4.1, discusses the narrow DistilBERT margin and what "near-ceiling, in-distribution" performance actually means), the Objective 3 functional testing findings (Table 4.2, the full critical analysis of the DistilBERT/classical-model inverse pattern and the mechanistic explanation for it — lexical-signature learning vs transfer-learning-derived structural generalisation — plus the qualitative institutional-vs-brand-phishing pattern), a dedicated section connecting this to the CETM44 human study's own over-suspicion bias (the strongest cross-cutting synthesis point in the dissertation so far), the Section 4.5 placeholder (states ethics status factually, lists exactly what analysis will go there: paired t-test + Cohen's d, SUS against Bangor et al. 2008 benchmarks, NASA-TLX subscale breakdown, and a planned cross-reference back to the 4.3 asymmetry once real pre/post data exists), and a closing summary.

Applied all standing conventions: zero em-dashes, zero in-chapter file paths (nothing needed updating here since it was written after the GitHub-repo fix), scholarly register throughout (no decision-log tone), Harvard citations only from `references/references.md`, tables captioned above with a distinct line plus an in-text mention, docx-only delivery.

**Next**: Chapter 5 (Project Evaluation and Reflection) can also be partially drafted now — it evaluates against all six objectives, and O1-O3 are complete enough to evaluate honestly; the O4/O5-dependent parts would need the same placeholder treatment as Chapter 4 Section 4.5.

## 18. Real-world browser testing surfaces a genuine misclassification, and reveals a UX gap (13 July 2026)

Student paused chapter-writing to actually test the study tool in a real browser (correctly prioritized over more writing). This surfaced two important things.

**Real email misclassification investigated properly, not just noted.** Student pasted a genuine personal email (a bootcamp certificate notification, addressed to them, from a legitimate organisation) into the classify demo. It was classified Phishing at ~100% confidence, an outright wrong call on clearly legitimate content. Rather than accepting the first plausible explanation, ran a controlled ablation: (1) with Gmail UI chrome as pasted, (2) clean email body only, (3) with Nigeria-specific content/`.ng` domain removed, (4) with hyperbolic/motivational language also removed. **Verdict stayed Phishing at ~99.98-100% across all four versions.** This ruled out three specific hypotheses (UI-chrome noise, geographic/Nigeria bias via the training data's Nigerian_Fraud corpus, and hyperbolic-language sensitivity) and pointed instead to something more fundamental: the model over-triggers on the certificate/bootcamp-completion notification *genre* itself (forward-referenced "next steps", attachment reference, "Dear [Name] ... Team" structure), robust to every specific content variable tested. This is a concrete, rigorously-tested real-world instance of the exact mechanism already documented in Chapter 4 (DistilBERT generalising structural cues too aggressively to legitimate service correspondence) — a candidate qualitative case study for Chapter 4/5, if used, must be anonymised first since it's the student's real personal email.

Also confirmed: LIME's top explanation words are NOT stable across repeated calls on the identical text (different top words shown in the browser vs. the scripted re-test) — the verdict was stable, only the explanation wording varied. This is LIME's own documented instability (already discussed in Chapter 2, Section 2.6), now with a concrete first-hand example — worth citing as lived evidence, not just a literature claim.

**UX gap found and fixed**: student asked directly "if I paused after pretest, could I resume with my code later?" — answer was NO, a real bug: the backend supports it (code lookup is stateless) but the frontend (`study.html`) had no way to jump straight to the code-entry screen; reloading the page always restarted at consent. Fixed by adding a "Already completed Part 1? Continue to Part 2" link on the consent screen that jumps directly to the code-gate screen, bypassing consent/demographics/pretest entirely.

**Other UX fixes applied to `app/templates/study.html`** in the same pass, per student request:
- **Proper email-client rendering**: emails were displayed as flat, unstyled text blocks, not resembling a real inbox. Added a parser (`parseEmailStructure()`) that extracts Subject/From/To/Date from the stimuli's stored text format (`"[Subject] From: X To: Y Date: Today, H:MM AM/PM [Body]"`, confirmed consistent across all 40 stimuli via a regex test) and renders a proper email-chrome UI (traffic-light dots bar, styled header block, body below), matching the visual language already established in the Assignment 6 `phishing_app`. Falls back to plain text display if parsing fails (deliberately NOT applied to the standalone classify-demo tool in `index.html`, since that accepts arbitrary user-pasted text that won't have this structure and shouldn't be force-parsed).
- **Copy-to-clipboard button** on the participant-code screen (`navigator.clipboard.writeText`, with a "Copied!" confirmation state).
- **Mobile responsiveness**: added a `@media (max-width: 600px)` block — verdict buttons stack vertically, font sizes and padding scale down, code display wraps.
- **Tasteful emoji touches** per student's "make it fun, exclude if it doesn't work" guidance: 🎣/✅ restored on verdict buttons (matching Assignment 6's original style), 🔒 site header (also gives the page a proper header bar, which it lacked before), 🎉 on the Part 1 complete and study-complete screens.

All changes are template-only (`app/templates/study.html`); no backend/route changes needed since Flask serves templates directly via `send_from_directory`, meaning no server restart was required to pick up the changes.

## 19. Realistic Gmail-style email rendering (13 July 2026)

Student pushed back on the design again after seeing it in-browser: "improved but still not ok for exam", and included a screenshot of a genuine Gmail message to show the target (sender avatar, name/email split, "to me", relative date, action icons like star/reply/more). Also independently noticed the email bodies read as one dense block rather than proper paragraphs, correctly connecting this to how the stimuli were originally extracted.

**Root cause**: `src/data/extract_stimuli.py` flattened each email's entire HTML (subject + meta + body) into one space-joined string via a single `get_text(separator=" ")` call, discarding paragraph breaks. That flattened string (`"text"`) is also the exact field the functional testing (T30/T31) was scored against, so it could not simply be changed without risking those already-documented results.

**Fix, done safely**: added a second, separate field (`"display"`) to `study/stimuli/email_pool.json`, extracted directly from the original HTML elements via targeted BeautifulSoup selectors (`.email-subject`, `.email-meta > div`, `.email-body p`) rather than regex-parsing the flattened string. This gives clean structured `{subject, from, to, date, body_paragraphs}` data with paragraph breaks intact. **Verified byte-for-byte that the `"text"` field is completely unchanged** after regenerating the pool (0 mismatches across all 40 stimuli) — the classify endpoint still receives the exact same input it always did, so T30/T31 remain valid.

`app/study_emails.py`'s `public_view()` now returns both fields to the client: `text` (unchanged, used only for the `/classify` call during the tool-interaction step) and `display` (used only for rendering).

`app/templates/study.html` rendering rebuilt around the new `display` data: coloured avatar circle (initial letter, hash-based hue so senders get consistent but varied colours), sender name/email split out of the raw "Name <email>" string, "to me ▾" in place of the literal recipient address, date and a row of decorative action icons (☆ 🙂 ↩ ⋮) aligned right like a real inbox, subject as a proper heading, and body rendered as separate `<p>` paragraphs instead of one block. Required a Flask restart (unlike the earlier template-only CSS/JS tweaks) since this change touched Python code (`study_emails.py`, `extract_stimuli.py`), not just the template.

## 20. Chapter 5 drafted as a partial chapter, same approach as Chapter 4 (13 July 2026)

Student acknowledged the O4/ethics wait explicitly and asked to continue with productive work in the meantime. Drafted `writing/chapters/05_project_evaluation_reflection.docx` (~1,870 words, zero em-dashes, zero file paths, scholarly register throughout, docx-only).

Six sections: introduction, project overview, an Objectives Review (Table 5.1 status summary, then O1-O3 evaluated in full as met with evidence, O4 stated honestly as infrastructure-complete-but-data-collection-pending with the ethics-review framing kept factual rather than narrated, O5 stated as dependent on O4, O6 stated as partially met with candidate design implications already drawable from O2/O3 findings even before the human study), a critical Evaluation of Methodology and Results (the two-phase design's value under the ethics delay, and the key methodological point that in-distribution test performance didn't predict real-world behaviour — discovered only because functional testing went beyond what O3 strictly required), a Personal Reflection section (first-person, appropriately reflective register — the benchmark-vs-real-world lesson, the discipline of testing a hypothesis rather than reporting the first plausible one per the Nigeria-bias ablation work, adapting project sequencing around an external dependency outside the author's control), and a closing Evaluation of Ethical/Legal/Social/Professional Considerations that surfaces one thing not fully anticipated in Chapter 1's original considerations: the social cost of the asymmetric failure mode itself (over-flagging legitimate institutional email has its own trust/alert-fatigue cost, distinct from missed-phishing cost) — flagged as a recommendation to develop further in Chapter 6.

**Next**: Chapter 6 (Conclusions and Recommendations) is the last chapter that can be meaningfully drafted before O4/O5 data exists — it should state the project's answer to the research aim, the required 5+ UXD recommendations (candidates already identified in Ch4/Ch5: complementary-model deployment, mandatory explainability, out-of-distribution evaluation as standard practice, transparent handling of the legitimate-email false-positive cost), and future work. After that, remaining work is genuinely blocked on ethics approval: the Abstract (written last, per module guidance) and the O4/O5-dependent sections of Chapters 4-6 cannot be finished until real study data exists.

**DistilBERT notebook built (11 July 2026)**: `notebooks/distilbert_finetuning_colab.ipynb`, built for Google Colab (student switched from the original Kaggle Notebooks plan to Colab). Key design points:
- Mounts Google Drive at the start; all heavy artefacts (cached cleaned/split data, training checkpoints, final model, results) persist under `MyDrive/prom02_phishing_pdat/` so a Colab disconnect doesn't lose progress.
- Reproduces the *exact* cleaning and split logic from `src/data/prepare_dataset.py` (same MIN_CHARS/MAX_CHARS thresholds, same `random_state=42`), so the DistilBERT test set matches the baselines' test set for a fair three-way comparison. Downloads the raw dataset via `kagglehub.dataset_download("naserabdullahalam/phishing-email-dataset")` only on first run; subsequent runs load the cached split CSVs from Drive instead.
- Training uses `Trainer` with `save_strategy="steps"` (every 500 steps, `save_total_limit=2`) and auto-detects the latest checkpoint via `get_last_checkpoint()` — re-running the training cell after any disconnect resumes rather than restarting.
- `report_to=[]` set explicitly to avoid Trainer prompting for a wandb login in a headless resumed session.
- Tokenizer truncates at 512 tokens (DistilBERT's max) — flagged in a markdown cell as a limitation worth discussing in the dissertation (some long emails will have their tail cut off).
- Final cell instructs how to bring results back: download `T12_distilbert_result.csv` into local `tables/`, download the `distilbert_final_model` folder into local `models/` for later use in the Flask app's explainability layer.

## 21. Supervisor-driven strategic pivot: human evaluation reframed as conditional, not central (16 July 2026)

Supervisor (Randa Almadhoun) meeting revealed ethics approval may not clear before end of summer. Explicit instructions relayed by the student: continue without human participants for now and build a real backup plan; reframe the human study as one part of evaluation, not the central part; ground every methodology choice in an explicit literature gap ("they achieved X, I achieved Y"); update the objectives to reflect this (deviation from the original planning doc is pre-approved by the module leader); reconsider Chapter 2 Section 2.8 (SUS/NASA-TLX), which the supervisor found unmotivated without confirmed human evaluation; check how the XAI literature evaluates explainability and consider doing something similar as a technical evaluation approach; supervisor also flagged confusion over a "Decisions" subsection (not present in the current Chapter 2 — concluded this was from an older draft) and over the words "Evaluation"/"Instrument" (she is not a specialist in this technical area).

**Objectives restructured (Chapter 1, Section 1.3).** Still six objectives, different substance: O1 dataset (unchanged), O2 three-model comparison (unchanged), O3 now also requires a quantitative fidelity/stability evaluation of the explainability layer itself, O4 is new — benchmark O2/O3 results against published literature, O5 is the human study, now explicitly conditional ("where ethics approval is granted... where it is not, Objectives 2-4 constitute the project's primary evaluation evidence, reported transparently"), O6 draws recommendations primarily from O2-O4, supplemented by O5 if it lands. Aims (1.2) and Research Approach (1.4) rewritten to match (development strand / literature-benchmarking strand / conditional human-evaluation strand). Caught and fixed my own repetition bug on the first pass: the ethics-conditional clause was restated near-verbatim in three places (Aims, Objective 5, Research Approach) — flagged by the student; fixed by stating it precisely once in Objective 5 and cross-referencing it elsewhere.

**Chapter 2 restructured.** New Section 2.7 "Evaluating Explainable AI: Fidelity and Stability" added (Doshi-Velez and Kim's 2017 three-tier grounding framework — application-grounded, human-grounded, functionally-grounded — used as the direct methodological justification for a no-human-subjects technical evaluation being a legitimate tier of evidence, not an improvised substitute; plus fidelity/stability as the two properties tested, citing Visani et al. 2022 for LIME stability indices). Old 2.7 (User-Centred Design) → 2.8, old 2.8 (Usability/Workload) → 2.9 with an explicit new lead-in sentence stating it applies only to the conditional O5 strand and glossing "instrument" in plain language ("a standardised questionnaire that's already been tested and validated by other researchers") — directly answers the supervisor's confusion. Table 2.1 gained a "Functionally-grounded XAI evaluation" column and a footnote marking the usability/workload column as conditional on O5.

**New references added** (verified via CrossRef/DOI, not carried over from the old flawed 80-list): Visani, G., Bagli, E., Chesani, F., Poluzzi, A. and Capuzzo, D. (2022) 'Statistical stability indices for LIME', *Journal of the Operational Research Society*, 73(1), pp.91-101; Meléndez, R., Ptaszynski, M. and Masui, F. (2024) 'Comparative Investigation of Traditional Machine-Learning Models and Transformer Models for Phishing Email Detection', *Electronics*, 13(24), 4877 (roBERTa max accuracy 99.43%, independently confirmed); Alhuzali, A., Alloqmani, A., Aljabri, M. and Alharbi, F. (2025) 'In-Depth Analysis of Phishing Email Detection...', *Applied Sciences*, 15(6), 3396 (BERT 98.99%, RoBERTa 99.08%, independently confirmed as belonging to this paper specifically, not the Meléndez paper — two different secondary sources had conflated them). Now 83 entries in `references/references.md`.

**Built and ran the O3 explainability evaluation** (`src/models/evaluate_explainability.py`, new): functionally-grounded stability + fidelity testing of the live LIME layer against the fine-tuned DistilBERT model, on a balanced 10-email sample (P1-P5, L1-L5) from the existing 40-email functional-test pool. No human subjects, no ethics dependency.
- **Stability**: 10 independent LIME runs per email, mean pairwise Jaccard similarity of top-5 words. Results low across the board (`tables/T32_lime_stability_test.csv`): phishing emails 0.023-0.038, legitimate emails 0.05-0.19 (legit consistently more stable than phishing in this sample). Quantifies, for the first time in this project, the LIME instability that had previously only been observed anecdotally.
- **Fidelity**: deletion test — remove LIME's top-5 |weight| words vs. 5 random words (5 repeats), compare resulting shift in predicted phishing probability (`tables/T33_lime_fidelity_test.csv`). Genuine signal on emails where the baseline prediction wasn't already saturated near 0 or 1 (informative/random shift ratios from ~3x up to ~700x on 4 of 5 non-saturated cases); near-zero signal on confidently-saturated predictions (baseline prob exactly 1.0), a known ceiling-effect limitation of deletion-based fidelity tests, not evidence of unfaithfulness — this nuance must be reported honestly in Chapter 4, not glossed over.

**Literature benchmark sources identified for O4** (actual comparison table + analysis still to be written into Chapter 4): Sahingoz et al. (2019, already cited) — RF on URL features, 97.98% accuracy, best of 7 algorithms; Meléndez, Ptaszynski and Masui (2024) and Alhuzali et al. (2025) above — both directly comparable classical-vs-transformer phishing email detection studies, both showing the same near-ceiling in-distribution clustering (98.5-99.5%) across model types that this project's own T13 also shows. The framing for O4/Chapter 4: published literature and this project agree closely on in-distribution performance, but no comparator study tests out-of-distribution/contemporary generalisation the way this project's T30/T31 functional testing does — that is the specific, evidenced gap this project fills.

**Chapter 3 fully updated** (`writing/chapters/03_practical_research_work.docx`): renumbered throughout to match the new O1-O6 scheme (old "Objective 4" human-study references → "Objective 5"); new Section 3.4.6 "Evaluating the Explainability Layer: Fidelity and Stability" describing the completed methodology above in full (past tense, results deferred to Chapter 4 per the chapter's existing convention); new Section 3.5 "Benchmarking Against Published Literature" describing the O4 comparator-selection methodology; Section 3.6 (renumbered from 3.5, human study design) gained an explicit conditional-framing lead-in paragraph mirroring Chapter 2's fix.

**Email drafted for the student to send to Randa** summarising all of the above in plain, non-jargon language (not saved to a file — was delivered inline in conversation for the student to copy/paste and adapt).

**Next**: Chapter 4 needs the same treatment — new sections for the O3 fidelity/stability results (write up T32/T33 honestly, including the saturation caveat) and the O4 literature benchmark table/analysis, plus renumbering the existing "Objectives 4 and 5" evaluation-study section to "Objective 5" only. Chapter 5's Table 5.1 objectives-review summary also needs updating to the new six-objective scheme. Not yet started — should confirm scope with the student before proceeding, same as the Chapter 3 checkpoint.
