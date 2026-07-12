"""
PDAT (Phishing Detection and Awareness Tool) -- Objective O3 prototype.

Flask backend serving:
    GET  /            -> the classification interface
    POST /classify     -> {"email_text": "..."} -> verdict, confidence,
                           word-level explanation, and a plain-language summary

    GET  /study                    -> the Objective O4 evaluation study interface
    GET  /study/pretest-emails      -> 5 random pretest emails (ground truth withheld)
    POST /study/submit-pretest      -> stores pretest + demographics, returns a participant code
    POST /study/verify-code         -> checks a code is valid and posttest not already done
    GET  /study/posttest-emails     -> 5 random posttest emails (disjoint from pretest pool)
    POST /study/submit-posttest     -> stores posttest + SUS + NASA-TLX, keyed by code

Model: fine-tuned DistilBERT (see model_utils.py), winner of the Objective O2
three-way comparison. Explainability: LIME (chosen over SHAP for real-time
responsiveness -- see Chapter 2, Section 2.6 for the justification).
"""
from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path

import model_utils
import study_emails
import study_storage

app = Flask(__name__, static_folder="static")
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def build_summary(verdict: str, confidence: float, word_weights: list) -> str:
    """Plain-language, non-alarming summary in line with the warning-fatigue
    literature discussed in Chapter 2 -- explains *why*, not just *what*."""
    positive_words = [w for w, wt in word_weights if wt > 0][:3]
    negative_words = [w for w, wt in word_weights if wt < 0][:3]
    confidence_pct = round(confidence * 100)

    if verdict == "Phishing":
        if positive_words:
            cue_list = ", ".join(f'"{w}"' for w in positive_words)
            return (
                f"This email was classified as Phishing with {confidence_pct}% confidence. "
                f"Words and phrases like {cue_list} contributed most to this decision. "
                f"Before acting on this email, check the sender's actual address and avoid "
                f"clicking any links directly."
            )
        return f"This email was classified as Phishing with {confidence_pct}% confidence."
    else:
        if negative_words:
            cue_list = ", ".join(f'"{w}"' for w in negative_words)
            return (
                f"This email was classified as Legitimate with {confidence_pct}% confidence. "
                f"Words and phrases like {cue_list} were consistent with genuine correspondence. "
                f"Even so, always verify unexpected requests through a separate, trusted channel."
            )
        return f"This email was classified as Legitimate with {confidence_pct}% confidence."


@app.route("/")
def index():
    return send_from_directory(TEMPLATE_DIR, "index.html")


@app.route("/classify", methods=["POST"])
def classify_route():
    data = request.get_json(silent=True) or {}
    email_text = (data.get("email_text") or "").strip()

    if not email_text:
        return jsonify({"error": "email_text is required"}), 400
    if len(email_text) < 10:
        return jsonify({"error": "email_text is too short to classify meaningfully"}), 400

    result = model_utils.classify(email_text)
    word_weights = model_utils.explain(email_text)

    return jsonify({
        "verdict": result["verdict"],
        "confidence": result["confidence"],
        "phishing_probability": result["phishing_probability"],
        "legitimate_probability": result["legitimate_probability"],
        "explanation": [{"word": w, "weight": round(wt, 4)} for w, wt in word_weights],
        "summary": build_summary(result["verdict"], result["confidence"], word_weights),
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ---------------------------------------------------------------------------
# Objective O4 -- evaluation study routes
# ---------------------------------------------------------------------------
@app.route("/study")
def study_index():
    return send_from_directory(TEMPLATE_DIR, "study.html")


@app.route("/study/pretest-emails")
def study_pretest_emails():
    emails = study_emails.get_pretest_emails()
    return jsonify({"emails": study_emails.public_view(emails)})


@app.route("/study/submit-pretest", methods=["POST"])
def study_submit_pretest():
    data = request.get_json(silent=True) or {}
    demographics = data.get("demographics") or {}
    pretest_emails = data.get("pretest_emails") or []

    required_demo_fields = ["age_group", "programme", "year_of_study", "prior_training", "prior_phishing_experience", "self_knowledge_rating"]
    missing = [f for f in required_demo_fields if not demographics.get(f)]
    if missing:
        return jsonify({"error": f"Missing demographic fields: {', '.join(missing)}"}), 400
    if not pretest_emails:
        return jsonify({"error": "pretest_emails is required"}), 400

    code = study_storage.save_pretest(demographics, pretest_emails)
    return jsonify({"code": code})


@app.route("/study/verify-code", methods=["POST"])
def study_verify_code():
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip().upper()
    if not code:
        return jsonify({"valid": False, "reason": "No code provided."})

    status = study_storage.code_status(code)
    if not status["exists"]:
        return jsonify({"valid": False, "reason": "Code not recognised. Please check and try again."})
    if status["already_completed"]:
        return jsonify({"valid": False, "reason": "This code has already been used to complete Part 2."})
    return jsonify({"valid": True})


@app.route("/study/posttest-emails")
def study_posttest_emails():
    emails = study_emails.get_posttest_emails()
    return jsonify({"emails": study_emails.public_view(emails)})


@app.route("/study/submit-posttest", methods=["POST"])
def study_submit_posttest():
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip().upper()
    posttest_emails = data.get("posttest_emails") or []
    sus_responses = data.get("sus_responses") or []
    tlx_responses = data.get("tlx_responses") or {}

    if not code:
        return jsonify({"error": "code is required"}), 400
    if not posttest_emails:
        return jsonify({"error": "posttest_emails is required"}), 400
    if len(sus_responses) != 10:
        return jsonify({"error": "sus_responses must contain exactly 10 items"}), 400

    ok = study_storage.save_posttest(code, posttest_emails, sus_responses, tlx_responses)
    if not ok:
        return jsonify({"error": "Invalid or already-used code."}), 400
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("Loading DistilBERT model (this may take a few seconds)...")
    model_utils.load()
    print("Model loaded. Starting server on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
