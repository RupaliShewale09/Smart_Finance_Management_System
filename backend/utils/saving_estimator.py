from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import Expense, User


def estimate_savings_potential(
    db: Session,
    user_id: int,
    start_date,
    end_date
):
    # 1️⃣ Fetch user income
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    income = user.income or 0.0

    # 2️⃣ Sum expenses by urgency
    expenses = db.query(
        Expense.urgency,
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user_id,
        Expense.timestamp >= start_date,
        Expense.timestamp <= end_date
    ).group_by(Expense.urgency).all()

    urgency_totals = {
        "critical": 0.0,
        "necessary": 0.0,
        "discretionary": 0.0
    }

    for urgency, total in expenses:
        if urgency:
            urgency_totals[urgency.lower()] = float(total)


    # 5️⃣ Savings estimation logic
    estimated_savings = round(
        (urgency_totals["necessary"] * 0.30) +
        (urgency_totals["discretionary"] * 0.60),
        2
    )

    savings_percentage = (
        round((estimated_savings / income) * 100, 2)
        if income > 0 else 0
    )

    message = (
        "Savings potential is good if discretionary expenses are optimized."
        if estimated_savings > 0
        else "Limited savings potential for the selected period."
    )

    return {
        "income": round(income, 2),
        "estimated_savings_potential": estimated_savings,
        "savings_percentage": savings_percentage,
        "reducible_breakdown": {
            "necessary": round(urgency_totals["necessary"] * 0.30, 2),
            "discretionary": round(urgency_totals["discretionary"] * 0.60, 2)
        },
        "message": message
    }
