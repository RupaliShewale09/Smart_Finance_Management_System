from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

import backend.database as database
from backend.utils.coach import financial_coach_chat

router = APIRouter(prefix="/coach", tags=["AI Financial Coach"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/chat/{user_id}")
def chat_with_coach(user_id: int, message: str, db: Session = Depends(get_db)):
    # Get current spend (same logic as alerts endpoint)
    expenses = db.execute(
        text("""
            SELECT merchant_category, SUM(amount)
            FROM expenses
            WHERE user_id=:user_id
            GROUP BY merchant_category
        """),
        {"user_id": user_id}
    ).fetchall()

    current_spend = {row[0]: row[1] for row in expenses}

    recent_tx = db.query(database.Expense)\
                .filter(database.Expense.user_id == user_id)\
                .order_by(database.Expense.timestamp.desc())\
                .limit(10).all()

    reply = financial_coach_chat(
        db=db,
        user_id=user_id,
        user_message=message,
        current_spend=current_spend,
        recent_transactions=recent_tx
    )

    return {"reply": reply}

