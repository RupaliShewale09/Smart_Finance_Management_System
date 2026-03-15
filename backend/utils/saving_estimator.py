from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import Expense, User, Wallet


def estimate_savings_potential(
    db: Session,
    user_id: int,
    start_date,
    end_date
):
    # 1️⃣ Fetch user income and wallet balance
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    income = user.income or 0.0

    # Wallet balance
    wallets = db.query(func.sum(Wallet.balance)).filter(
        Wallet.owner_type == "user",
        Wallet.owner_id == user_id
    ).scalar()

    total_balance = float(wallets or 0.0)

    # 2️⃣ Sum expenses by urgency
    expenses = db.query(
        Expense.urgency,
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user_id,
        Expense.timestamp >= start_date,
        Expense.timestamp <= end_date
    ).group_by(Expense.urgency).all()

    print("Expenses", expenses)

    urgency_totals = {
        "critical": 0.0,
        "necessary": 0.0,
        "discretionary": 0.0
    }

    for urgency, total in expenses:
        if urgency:
            urgency_totals[urgency.lower()] = float(total)

    print("Urgency",urgency_totals)

    total_spent = sum(urgency_totals.values())

    # Current savings
    current_savings = max(income - total_spent, 0)

    # Reducible spending
    reducible_necessary = urgency_totals["necessary"] * 0.25
    reducible_discretionary = urgency_totals["discretionary"] * 0.60

    reducible_total = reducible_necessary + reducible_discretionary

    estimated_savings = round(current_savings + reducible_total, 2)

    savings_percentage = (
        round((estimated_savings / income) * 100, 2)
        if income > 0 else 0
    ) 

    savings_score = (
        round((current_savings / income) * 100, 2)
        if income > 0 else 0
    )

    if savings_score < 20:
        financial_health = "Poor"
    elif savings_score < 40:
        financial_health = "Weak"
    elif savings_score < 75:
        financial_health = "Good"
    else:
        financial_health = "Excellent" 

    return {
        "income": round(income, 2),
        "estimated_savings_potential": estimated_savings,
        "savings_potential_percentage": savings_percentage,
        "reducible_breakdown": {
            "necessary": round(reducible_necessary, 2),
            "discretionary": round(reducible_discretionary, 2)
        },
        "savings_score": savings_score,
        "financial_health": financial_health,
    }
