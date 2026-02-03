import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from google import genai

from backend.database import (
    Expense,
    UserSpendLimit,
    FinancialNudge
)

# ---------------- GEMINI CLIENT ----------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------- BEHAVIOR ANALYSIS (NO AI) ----------------
def analyze_user_behavior(user_id: int, db: Session):
    now = datetime.utcnow()
    last_hour = now - timedelta(days=7)

    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.timestamp >= last_hour
    ).all()

    if not expenses:
        return None

    discretionary = [e for e in expenses if e.urgency == "discretionary"]

    if len(discretionary) >= 2:
        return {
            "type": "behavior",
            "event": "impulsive_spending",
            "severity": "medium",
            "category": discretionary[0].category
        }

    for exp in expenses:
        limit = db.query(UserSpendLimit).filter(
            UserSpendLimit.user_id == user_id,
            UserSpendLimit.category == exp.category
        ).first()

        if limit and exp.amount >= limit.alert_threshold:
            return {
                "type": "alert",
                "event": "spend_limit_warning",
                "severity": "high",
                "category": exp.category
            }

    return {
        "type": "literacy",
        "event": "savings_encouragement",
        "severity": "low",
        "category": "General"
    }


# ---------------- GEMINI NUDGE GENERATION ----------------
def enforce_length(text: str) -> str:
    words = text.strip().split()
    if len(words) > 25:
        return " ".join(words[:25]) + "."
    return text


def generate_nudge(context: dict) -> str:
    prompt = f"""
You are a financial assistant.

Generate a short, supportive financial nudge.

STRICT RULES:
- Output must be 1 or 2 lines only
- Maximum 25 words
- No emojis
- No statistics unless essential
- Tone must be calm and non-judgmental

Context:
{context}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return enforce_length(response.text)
    except Exception as e:
        # Fallback message if AI is unavailable
        return "Remember to keep an eye on your discretionary spending this week!"


# ---------------- RATE LIMIT + STORE ----------------
def can_send_nudge(user_id: int, nudge_type: str, db: Session):
    last = db.query(FinancialNudge).filter(
        FinancialNudge.user_id == user_id,
        FinancialNudge.nudge_type == nudge_type
    ).order_by(FinancialNudge.delivered_at.desc()).first()

    if not last:
        return True

    return (datetime.utcnow() - last.delivered_at) > timedelta(minutes=30)   ## change this


def save_nudge(user_id, nudge_type, severity, message, db):
    nudge = FinancialNudge(
        user_id=user_id,
        nudge_type=nudge_type,
        severity=severity,
        message=message
    )
    db.add(nudge)
    db.commit()
