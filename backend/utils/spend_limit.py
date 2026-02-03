import pandas as pd
from sqlalchemy.orm import Session
from backend.database import UserSpendLimit


def generate_spend_limits(df: pd.DataFrame, income: float, savings_goal: float):
    """
    Generate personalized spend limits based on historical transaction data.
    """
    limits = []

    if df.empty or income <= 0:
        return limits
    
     # Total spendable for the month
    spendable_total = max(income - savings_goal, 0)
    

    # Group by category and calculate average spend
    category_avg = df.groupby("merchant_category")["amount"].mean()

    for category, avg_amount in category_avg.items():
        limit = round(avg_amount * 1.2, 2)  # 20% buffer
        alert_threshold = round(limit * 0.9, 2)  # 90% of limit

        proportion = avg_amount / df["amount"].sum()
        limit = min(limit, round(spendable_total * proportion, 2))
        alert_threshold = min(alert_threshold, round(limit * 0.9, 2))

        limits.append({
            "category": category,
            "limit": limit,
            "alert_threshold": alert_threshold
        })

    total_limit = round(df["amount"].sum() * 1.2, 2)
    total_limit = min(total_limit, spendable_total)
    total_alert = round(total_limit * 0.9, 2)

    limits.append({
        "category": "Total Monthly Spend",
        "limit": total_limit,
        "alert_threshold": total_alert
    })

    return limits



def save_user_limits(db: Session, user_id: int, limits: list):
    """Save or update spend limits in DB"""
    # Delete previous limits
    db.query(UserSpendLimit).filter(UserSpendLimit.user_id == user_id).delete()
    db.commit()
    
    # Add new limits
    for limit in limits:
        db_limit = UserSpendLimit(
            user_id=user_id,
            category=limit['category'],
            limit=limit['limit'],
            alert_threshold=limit['alert_threshold']
        )
        db.add(db_limit)
    db.commit()



def check_spend_alerts(db: Session, user_id: int, current_spend: dict):
    """Compare user spend against limits and return alerts"""
    alerts = []
    limits = db.query(UserSpendLimit).filter(UserSpendLimit.user_id == user_id).all()

    if not limits:
        return [{
            "type": "info",
            "message": "Spend limits not configured. Please generate spend limits first."
        }]

    for limit in limits:
        spend = current_spend.get(limit.category, 0)
        if spend >= limit.alert_threshold and spend < limit.limit:
            alerts.append({
                "type": "warning",
                "category": limit.category,
                "message": f"Approaching limit in {limit.category}: {spend}/{limit.limit}"
            })
        elif spend >= limit.limit:
            alerts.append({
                "type": "danger",
                "category": limit.category,
                "message": f"Exceeded limit in {limit.category}: {spend}/{limit.limit}"
            })
    return alerts
