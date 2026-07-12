"""
Storage layer for the Objective O4 evaluation study.

Mirrors the resilient pattern already used in Assignment 6's phishing_app:
    1. Always write to a local CSV first (fast, always works, no external
       dependency).
    2. Optionally ALSO mirror the write to a Google Sheet, via a service
       account (not a personal OAuth login) -- only activates if
       GOOGLE_CREDENTIALS_JSON and GOOGLE_SHEET_ID environment variables are
       set. Silently skipped otherwise, so the whole study runs fully
       locally during development, and the student can switch on live Google
       Sheets sync later just by setting those two env vars once ethics
       approval is granted and real data collection begins.

Participant linking: pretest and posttest responses are matched using a
short, random, anonymous code (no personal information), generated at the
end of pretest and re-entered by the participant to unlock posttest. See
study/consent_ethics/ for the participant-facing explanation of this.
"""
import csv
import json
import os
import random
import string
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]  # Dissertation/
RESPONSES_DIR = ROOT / "study" / "responses"
RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

PRETEST_CSV = RESPONSES_DIR / "pretest_responses.csv"
POSTTEST_CSV = RESPONSES_DIR / "posttest_responses.csv"

PRETEST_FIELDNAMES = [
    "code", "timestamp_utc",
    "age_group", "programme", "year_of_study",
    "prior_training", "prior_phishing_experience", "self_knowledge_rating",
    "pretest_emails_json",
]

POSTTEST_FIELDNAMES = [
    "code", "timestamp_utc",
    "posttest_emails_json",
    "sus_1", "sus_2", "sus_3", "sus_4", "sus_5",
    "sus_6", "sus_7", "sus_8", "sus_9", "sus_10",
    "tlx_mental_demand", "tlx_physical_demand", "tlx_temporal_demand",
    "tlx_performance", "tlx_effort", "tlx_frustration",
]

CODE_CHARSET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # excludes 0/O, 1/I/L for readability


def _ensure_csv(path: Path, fieldnames: list):
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fieldnames).writeheader()


def _existing_codes(path: Path, fieldnames: list) -> set:
    _ensure_csv(path, fieldnames)
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["code"] for row in reader}


def generate_unique_code() -> str:
    existing = _existing_codes(PRETEST_CSV, PRETEST_FIELDNAMES)
    while True:
        code = "".join(random.choices(CODE_CHARSET, k=8))
        if code not in existing:
            return code


def code_status(code: str) -> dict:
    """Returns whether a code exists in pretest and whether posttest is already complete."""
    pretest_codes = _existing_codes(PRETEST_CSV, PRETEST_FIELDNAMES)
    posttest_codes = _existing_codes(POSTTEST_CSV, POSTTEST_FIELDNAMES)
    exists = code in pretest_codes
    already_completed = code in posttest_codes
    return {"exists": exists, "already_completed": already_completed}


# ---------------------------------------------------------------------------
# Optional Google Sheets mirror
# ---------------------------------------------------------------------------
_gs_client = None
_gs_spreadsheet = None


def _get_gs_spreadsheet():
    global _gs_client, _gs_spreadsheet
    if _gs_spreadsheet is not None:
        return _gs_spreadsheet

    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not creds_json or not sheet_id:
        return None  # not configured -- local CSV only, this is expected during development

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scopes)
        client = gspread.authorize(creds)
        _gs_client = client
        _gs_spreadsheet = client.open_by_key(sheet_id)
        return _gs_spreadsheet
    except Exception as e:
        print(f"[Google Sheets] Connection failed, continuing with local CSV only: {e}")
        return None


def _mirror_to_sheet(tab_name: str, fieldnames: list, row: dict):
    spreadsheet = _get_gs_spreadsheet()
    if spreadsheet is None:
        return
    try:
        try:
            ws = spreadsheet.worksheet(tab_name)
        except Exception:
            ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=len(fieldnames))
            ws.append_row(fieldnames)
        ws.append_row([str(row.get(col, "")) for col in fieldnames], value_input_option="USER_ENTERED")
    except Exception as e:
        print(f"[Google Sheets] Mirror write to '{tab_name}' failed: {e}")


# ---------------------------------------------------------------------------
# Public write functions
# ---------------------------------------------------------------------------
def save_pretest(demographics: dict, pretest_emails: list) -> str:
    """Stores a pretest submission and returns the newly generated participant code."""
    code = generate_unique_code()
    row = {
        "code": code,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "age_group": demographics.get("age_group", ""),
        "programme": demographics.get("programme", ""),
        "year_of_study": demographics.get("year_of_study", ""),
        "prior_training": demographics.get("prior_training", ""),
        "prior_phishing_experience": demographics.get("prior_phishing_experience", ""),
        "self_knowledge_rating": demographics.get("self_knowledge_rating", ""),
        "pretest_emails_json": json.dumps(pretest_emails),
    }
    _ensure_csv(PRETEST_CSV, PRETEST_FIELDNAMES)
    with open(PRETEST_CSV, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=PRETEST_FIELDNAMES, extrasaction="ignore").writerow(row)
    _mirror_to_sheet("PretestResponses", PRETEST_FIELDNAMES, row)
    return code


def save_posttest(code: str, posttest_emails: list, sus_responses: list, tlx_responses: dict) -> bool:
    """Stores a posttest submission. Returns False if the code is invalid or already used."""
    status = code_status(code)
    if not status["exists"] or status["already_completed"]:
        return False

    row = {
        "code": code,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "posttest_emails_json": json.dumps(posttest_emails),
    }
    for i in range(10):
        row[f"sus_{i + 1}"] = sus_responses[i] if i < len(sus_responses) else ""
    for key in ["mental_demand", "physical_demand", "temporal_demand", "performance", "effort", "frustration"]:
        row[f"tlx_{key}"] = tlx_responses.get(key, "")

    _ensure_csv(POSTTEST_CSV, POSTTEST_FIELDNAMES)
    with open(POSTTEST_CSV, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=POSTTEST_FIELDNAMES, extrasaction="ignore").writerow(row)
    _mirror_to_sheet("PosttestResponses", POSTTEST_FIELDNAMES, row)
    return True
