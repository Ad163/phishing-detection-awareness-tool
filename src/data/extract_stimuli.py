"""
Extracts the 40 hand-crafted email stimuli (20 phishing, 20 legitimate) from
the Assignment 6 phishing_app's PHISHING_POOL/LEGIT_POOL JS arrays, and splits
them into two disjoint batches for the Objective O4 evaluation study:
    - Batch A -> pretest pool  (P1-P10, L1-L10)
    - Batch B -> posttest pool (P11-P20, L11-L20)
Disjoint batches mean no participant sees the same email in both pretest and
posttest, avoiding a memory/practice-effect confound.

Output: study/stimuli/email_pool.json
"""
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

SRC = Path(r"C:\Users\testing\Documents\dave\Assignment 6\phishing_app\index.html")
OUT = Path(__file__).resolve().parents[2] / "study" / "stimuli" / "email_pool.json"

pattern = re.compile(
    r"id:\s*'([PL]\d+)',\s*label:\s*(['\"])(.*?)\2,\s*type:\s*'(Phishing|Legitimate)',\s*html:\s*`(.*?)`,\s*feedback:",
    re.DOTALL,
)


def main():
    text = SRC.read_text(encoding="utf-8")
    matches = pattern.findall(text)
    print(f"Found {len(matches)} email entries in {SRC.name}")

    emails = {}
    for email_id, _, label, etype, html in matches:
        soup = BeautifulSoup(html, "html.parser")

        # "text" is UNCHANGED from the original extraction -- this is the exact
        # field used for classification in the functional testing (T30/T31),
        # so it must not be altered by the display-formatting work below.
        clean_text = soup.get_text(separator=" ", strip=True)
        clean_text = re.sub(r"\s{2,}", " ", clean_text)

        # "display" is a NEW, separate field: structured fields extracted
        # directly from their HTML elements (not regex-parsed from flattened
        # text), used only for rendering a realistic email-client UI. Body
        # paragraphs are preserved as separate paragraphs rather than being
        # flattened into one dense block.
        subject_el = soup.select_one(".email-subject")
        meta_divs = soup.select(".email-meta > div")
        body_paragraphs = [p.get_text(" ", strip=True) for p in soup.select(".email-body p")]
        body_paragraphs = [p for p in body_paragraphs if p]

        def meta_value(div):
            # each div is "<span>Label:</span> value" -- strip the label
            text = div.get_text(" ", strip=True)
            return re.sub(r"^(From|To|Date):\s*", "", text).strip()

        display = {
            "subject": subject_el.get_text(" ", strip=True) if subject_el else "",
            "from": meta_value(meta_divs[0]) if len(meta_divs) > 0 else "",
            "to": meta_value(meta_divs[1]) if len(meta_divs) > 1 else "",
            "date": meta_value(meta_divs[2]) if len(meta_divs) > 2 else "",
            "body_paragraphs": body_paragraphs,
        }

        emails[email_id] = {"id": email_id, "label": label, "type": etype, "text": clean_text, "display": display}

    def batch(ids):
        return [emails[i] for i in ids if i in emails]

    batch_a_ids = [f"P{i}" for i in range(1, 11)] + [f"L{i}" for i in range(1, 11)]
    batch_b_ids = [f"P{i}" for i in range(11, 21)] + [f"L{i}" for i in range(11, 21)]

    pool = {
        "source": "Assignment 6 phishing_app PHISHING_POOL/LEGIT_POOL",
        "pretest_batch": batch(batch_a_ids),
        "posttest_batch": batch(batch_b_ids),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(pool['pretest_batch'])} pretest + {len(pool['posttest_batch'])} posttest emails to {OUT}")


if __name__ == "__main__":
    main()
