import pandas as pd
from sqlalchemy.orm import Session
from backend.database import UserSpendLimit
from datetime import datetime


def _norm_category(cat: str) -> str:
    return str(cat).strip().title()

def get_month_range():
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if month_start.month == 12:
        next_month = month_start.replace(year=month_start.year + 1, month=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1)

    return month_start, next_month


def generate_spend_limits(df: pd.DataFrame, income: float, savings_goal: float):
    limits = []

    if df.empty or income <= 0:
        return limits

    # Normalize categories before grouping — ensures consistent keys
    df = df.copy()
    df["merchant_category"] = df["merchant_category"].apply(_norm_category)

    # Total spendable for the month
    spendable_total = max(income - savings_goal, 0)

    # Group by normalized category
    category_stats = df.groupby("merchant_category")["amount"].agg(['max', 'mean'])

    for category, stats in category_stats.iterrows():
        suggested_limit = max(stats['mean'] * 1.5, stats['max'])
        safety_cap = spendable_total * 0.6
        final_limit = round(min(suggested_limit, safety_cap), 2)
        alert_threshold = round(final_limit * 0.85, 2)

        limits.append({
            "category": category,           # Already normalized by _norm_category
            "limit": final_limit,
            "alert_threshold": alert_threshold
        })

    total_spent_hist = df["amount"].sum()
    total_limit = min(spendable_total, total_spent_hist * 1.2)

    limits.append({
        "category": "Total Monthly Spend",
        "limit": round(total_limit, 2),
        "alert_threshold": round(total_limit * 0.9, 2)
    })

    return limits


def save_user_limits(db: Session, user_id: int, limits: list):
    """Save or update spend limits in DB — deletes old limits first."""
    db.query(UserSpendLimit).filter(UserSpendLimit.user_id == user_id).delete()
    db.commit()

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
    """Compare user spend against saved limits and return alerts.
    current_spend keys are normalized before comparison."""
    alerts = []
    limits = db.query(UserSpendLimit).filter(UserSpendLimit.user_id == user_id).all()

    if not limits:
        return [{
            "type": "info",
            "message": "Spend limits not configured. Please generate spend limits first."
        }]

    # Normalize incoming spend keys to match stored limit categories
    normalized_spend = {_norm_category(k): v for k, v in current_spend.items()}

    for limit in limits:
        spend = normalized_spend.get(limit.category, 0)
        if spend >= limit.alert_threshold and spend < limit.limit:
            alerts.append({
                "type": "warning",
                "category": limit.category,
                "message": f"Approaching limit in {limit.category}: ₹{spend:.0f} / ₹{limit.limit:.0f}"
            })
        elif spend >= limit.limit:
            alerts.append({
                "type": "danger",
                "category": limit.category,
                "message": f"Exceeded limit in {limit.category}: ₹{spend:.0f} / ₹{limit.limit:.0f}"
            })
    return alerts