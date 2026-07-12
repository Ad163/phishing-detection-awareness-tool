"""
Loads the pretest/posttest email pools (study/stimuli/email_pool.json,
produced by src/data/extract_stimuli.py) and selects a balanced random subset
for each participant.

Ground truth ("type") is deliberately NOT sent to the client -- the server
remembers which email IDs were shown to which code, and scoring against
ground truth happens later during analysis (Objective O5), not in real time.
This also means pretest/posttest give no immediate correct/incorrect
feedback, which is the right design for a pre/post measurement (see
study/consent_ethics/ for the participant-facing description).
"""
import json
import random
from pathlib import Path

POOL_FILE = Path(__file__).resolve().parents[1] / "study" / "stimuli" / "email_pool.json"

PRETEST_N_PHISHING = 3
PRETEST_N_LEGIT = 2
POSTTEST_N_PHISHING = 3
POSTTEST_N_LEGIT = 2

_pool = None


def _load_pool():
    global _pool
    if _pool is None:
        with open(POOL_FILE, encoding="utf-8") as f:
            _pool = json.load(f)
    return _pool


def _select(batch: list, n_phishing: int, n_legit: int) -> list:
    phishing = [e for e in batch if e["type"] == "Phishing"]
    legit = [e for e in batch if e["type"] == "Legitimate"]
    selected = random.sample(phishing, min(n_phishing, len(phishing))) + \
        random.sample(legit, min(n_legit, len(legit)))
    random.shuffle(selected)
    return selected


def get_pretest_emails() -> list:
    pool = _load_pool()
    return _select(pool["pretest_batch"], PRETEST_N_PHISHING, PRETEST_N_LEGIT)


def get_posttest_emails() -> list:
    pool = _load_pool()
    return _select(pool["posttest_batch"], POSTTEST_N_PHISHING, POSTTEST_N_LEGIT)


def public_view(emails: list) -> list:
    """Strips ground truth before sending to the client."""
    return [{"id": e["id"], "text": e["text"]} for e in emails]
