from google import genai
import os
from sqlalchemy.orm import Session
from backend.database import CoachConversation
from backend.utils.spend_limit import check_spend_alerts

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def financial_coach_chat(
    db: Session,
    user_id: int,
    user_message: str,
    current_spend: dict,
    recent_transactions: list
):
    history_str = "\n".join([
        f"- {tx.timestamp.strftime('%d %b')}: ₹{tx.amount} at {tx.merchant_name} ({tx.category})" 
        for tx in recent_transactions
    ])

    # Get alerts using existing Step 5 logic
    alerts = check_spend_alerts(db, user_id, current_spend)

    prompt = f"""
    You are a friendly and supportive financial AI coach in India (₹ / INR).
    
    STRICT RULES:
    - Answer ONLY finance-related questions
    - Topics allowed: spending, budgeting, saving, expenses, alerts, financial habits
    - If the user asks anything outside finance, respond with:
        "I'm here to guide you on financial matters like spending, saving, and budgeting."

    RESPONSE STYLE:
    - Keep responses SHORT (4 - 5 sentences max).
    - Be supportive and non-judgmental.
    - Focus on practical, actionable advice.
    - Do NOT give long explanations or stories.

    Recent Transactions: {history_str}

    User's current spending summary: {current_spend}

    Active alerts: {alerts if alerts else "No alerts"}

    User message: "{user_message}"

    RESPONSE GUIDELINES:
    - Use the 'Recent Transactions' to spot trends (e.g., recurring small spends).
    - If alerts exist, gently highlight them.
    - Suggest at most 2 small improvements.
    - Ask at most ONE reflective follow-up question
    """

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
    except Exception as e:
        return "I'm currently unable to respond. Please try again later."

    ai_reply = response.text.strip()

    # Save conversation
    chat = CoachConversation(
        user_id=user_id,
        user_message=user_message,
        ai_response=ai_reply
    )
    db.add(chat)
    db.commit()

    return ai_reply
