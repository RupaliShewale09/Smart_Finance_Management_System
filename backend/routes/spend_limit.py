from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from sqlalchemy import text
from datetime import datetime

from backend.utils.spend_limit import generate_spend_limits, save_user_limits, check_spend_alerts
import backend.database as database

router = APIRouter(prefix="/spend", tags=["Spend Limits"])

# DB Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/generate/{user_id}")
def generate_limits(user_id: int, db: Session = Depends(get_db)):
    # Fetch user transactions
    expenses = db.execute(
        text("""
            SELECT merchant_category, amount 
            FROM expenses 
            WHERE user_id=:user_id
        """),
        {"user_id": user_id}
    ).fetchall()
    
    if not expenses:
        raise HTTPException(status_code=404, detail="No expense data found")

    # Convert to DataFrame
    df = pd.DataFrame(expenses, columns=["merchant_category", "amount"])

    # Fetch user income and savings goal
    user = db.execute(
        text("SELECT income, savings_goal FROM users WHERE id=:user_id"),
        {"user_id": user_id}
    ).fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    income, savings_goal = user

    # Check if income or savings goal is 0.0
    if income == 0.0 or savings_goal == 0.0:
        raise HTTPException(
            status_code=400,
            detail="Please update your monthly income and savings goal first to generate spend limits."
        )

    limits = generate_spend_limits(df, income, savings_goal)
    
    # Save limits in DB
    save_user_limits(db, user_id, limits)
    
    return {"message": "Spend limits generated successfully", "limits": limits}



# Endpoint to check alerts
@router.get("/alerts/{user_id}")
def get_alerts(user_id: int, db: Session = Depends(get_db)):
    current_month_str = datetime.utcnow().strftime('%Y-%m')

    # Get current spend
    expenses = db.execute(
        text("""
            SELECT merchant_category, SUM(amount) as total 
            FROM expenses 
            WHERE user_id = :user_id 
            AND strftime('%Y-%m', timestamp) = :current_month
            GROUP BY merchant_category
        """),
        {"user_id": user_id, "current_month": current_month_str}
    ).fetchall()

    current_spend = {row[0]: row[1] for row in expenses}
    
    alerts = check_spend_alerts(db, user_id, current_spend)
    return {"alerts": alerts}
