from sqlalchemy.orm import Session
from backend.database import Expense
from backend.utils.predict_category import is_recurring_transaction
from sqlalchemy import func


def generate_insights(db: Session, user_id: int, start_date, end_date):
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        func.date(Expense.timestamp) >= start_date,
        func.date(Expense.timestamp) <= end_date
    ).all()

    print("Expenses found:", len(expenses))  # DEBUG LINE

    total_spent = 0.0
    category_wise = {}
    high_urgency_count = 0
    recurring_merchants = set() 

    for exp in expenses:
        total_spent += exp.amount

        category = exp.category or "Uncategorized"
        category_wise[category] = category_wise.get(category, 0) + exp.amount

        if exp.urgency and exp.urgency.lower() == "critical":
            high_urgency_count += 1

        if is_recurring_transaction(db, user_id, exp.merchant_name):
            recurring_merchants.add(exp.merchant_name)

    recurring_count = len(recurring_merchants)

    warning = (
        "High number of urgent expenses. Consider better planning."
        if high_urgency_count > 3
        else "Spending is under control."
    )

    # Category-wise spending can also include percentages
    category_percentages = {
        cat: round((amt / total_spent) * 100, 2) if total_spent > 0 else 0
        for cat, amt in category_wise.items()
    }

    return {
        "total_spent": round(total_spent, 2),    # Sum of all expenses in the period
        "category_wise_spending": category_wise,   # Expense breakdown by category
        "category_percentages": category_percentages, # Percentage contribution of each category
        "high_urgency_expenses": high_urgency_count,    # Number of expenses marked as 'critical'
        "distinct_recurring_merchants": recurring_count,     #  distinct recurring merchants - unique merchand counts that are recurring
        "savings_warning": warning
    }
