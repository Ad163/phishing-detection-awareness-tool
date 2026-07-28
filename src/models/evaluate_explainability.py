"""
Functionally-grounded evaluation of the PDAT tool's explainability layer
(Objective 3 / Chapter 2, Section 2.7), requiring no human participants.

Two properties are tested on a balanced sample of the 40-email functional
test pool (study/stimuli/email_pool.json), reusing the same stimuli already
used for the T30/T31 functional tests so results are directly comparable:

  1. Stability — does LIME return the same top contributing words when run
     repeatedly on an unchanged input? Measured as the mean pairwise Jaccard
     similarity of the top-5 word set across REPEATS independent runs per
     email, following the general approach of Visani et al. (2022).

  2. Fidelity — do the words LIME identifies as most influential actually
     matter to the model? Measured with a deletion test: the top-5 words by
     |weight| are removed from the email and the resulting shift in the
     model's predicted phishing probability is compared against the mean
     shift from removing 5 randomly selected words (repeated CONTROL_REPEATS
     times), consistent with the feature-removal validation logic used in
     the original LIME paper (Ribeiro, Singh and Guestrin, 2016).

Outputs:
  tables/T32_lime_stability_test.csv
  tables/T33_lime_fidelity_test.csv
"""
import csv
import json
import random
import re
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.model_utils import classify, explain  # noqa: E402

random.seed(42)

REPEATS = 10
CONTROL_REPEATS = 5
TOP_K = 5
NUM_FEATURES = 10
NUM_SAMPLES = 100

SAMPLE_IDS = ["P1", "P2", "P3", "P4", "P5", "L1", "L2", "L3", "L4", "L5"]


def load_sample():
    with open(ROOT / "study" / "stimuli" / "email_pool.json", encoding="utf-8") as f:
        pool = json.load(f)
    by_id = {e["id"]: e for e in pool["pretest_batch"] + pool["posttest_batch"]}
    return [by_id[i] for i in SAMPLE_IDS if i in by_id]


def top_words(exp_list, k):
    ranked = sorted(exp_list, key=lambda t: abs(t[1]), reverse=True)
    return [w for w, _ in ranked[:k]]


def jaccard(a, b):
    a, b = set(a), set(b)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def remove_words(text, words_to_remove):
    lowered = {w.lower() for w in words_to_remove}
    tokens = text.split()

    def strip_punct(tok):
        return re.sub(r"^\W+|\W+$", "", tok).lower()

    kept = [t for t in tokens if strip_punct(t) not in lowered]
    return " ".join(kept)


def run_stability(sample):
    rows = []
    for e in sample:
        text = e["text"]
        runs = [explain(text, num_features=NUM_FEATURES, num_samples=NUM_SAMPLES) for _ in range(REPEATS)]
        top5_runs = [top_words(r, TOP_K) for r in runs]
        pairs = list(combinations(range(REPEATS), 2))
        sims = [jaccard(top5_runs[i], top5_runs[j]) for i, j in pairs]
        mean_jaccard = sum(sims) / len(sims)
        distinct_top1 = len({t[0] for t in top5_runs if t})
        rows.append({
            "id": e["id"],
            "type": e["type"],
            "repeats": REPEATS,
            "mean_top5_jaccard": round(mean_jaccard, 4),
            "distinct_top1_words_across_runs": distinct_top1,
        })
        print(f"[stability] {e['id']} ({e['type']}): mean top-5 Jaccard = {mean_jaccard:.4f}, "
              f"distinct top-1 words = {distinct_top1}/{REPEATS}", flush=True)
    return rows


def run_fidelity(sample):
    rows = []
    for e in sample:
        text = e["text"]
        baseline = classify(text)
        baseline_prob = baseline["phishing_probability"]

        exp = explain(text, num_features=NUM_FEATURES, num_samples=NUM_SAMPLES)
        top5 = top_words(exp, TOP_K)
        informative_text = remove_words(text, top5)
        informative_prob = classify(informative_text)["phishing_probability"]
        informative_shift = abs(baseline_prob - informative_prob)

        all_tokens = list({re.sub(r"^\W+|\W+$", "", t) for t in text.split() if re.sub(r"^\W+|\W+$", "", t)})
        eligible = [t for t in all_tokens if t.lower() not in {w.lower() for w in top5}]

        control_shifts = []
        for _ in range(CONTROL_REPEATS):
            random_words = random.sample(eligible, min(TOP_K, len(eligible)))
            control_text = remove_words(text, random_words)
            control_prob = classify(control_text)["phishing_probability"]
            control_shifts.append(abs(baseline_prob - control_prob))
        control_shift_mean = sum(control_shifts) / len(control_shifts)

        rows.append({
            "id": e["id"],
            "type": e["type"],
            "baseline_phishing_prob": round(baseline_prob, 4),
            "top5_lime_words": "; ".join(top5),
            "informative_removal_shift": round(informative_shift, 4),
            "random_removal_mean_shift": round(control_shift_mean, 4),
            "fidelity_ratio (informative/random)": round(
                informative_shift / control_shift_mean, 2
            ) if control_shift_mean > 0 else float("inf"),
        })
        print(f"[fidelity] {e['id']} ({e['type']}): informative shift = {informative_shift:.4f}, "
              f"random shift (mean of {CONTROL_REPEATS}) = {control_shift_mean:.4f}", flush=True)
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    sample = load_sample()
    print(f"Loaded {len(sample)} sample emails: {[e['id'] for e in sample]}", flush=True)

    print("\n=== Running stability test ===", flush=True)
    stability_rows = run_stability(sample)
    write_csv(stability_rows, ROOT / "tables" / "T32_lime_stability_test.csv")
    print("Saved tables/T32_lime_stability_test.csv", flush=True)

    print("\n=== Running fidelity test ===", flush=True)
    fidelity_rows = run_fidelity(sample)
    write_csv(fidelity_rows, ROOT / "tables" / "T33_lime_fidelity_test.csv")
    print("Saved tables/T33_lime_fidelity_test.csv", flush=True)

    print("\nDone.", flush=True)
