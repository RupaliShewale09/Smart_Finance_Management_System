from backend.database import SessionLocal, User
from datetime import datetime

def suggest_investment(user_id: int, step7_output: dict):
    """
    Suggest investment options for a user based on their:
    - income
    - savings_goal
    - risk_tolerance
    - actual savings potential
    - optionally reducible expenses
    """

    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()

    if not user:
        return None

    income = user.income or 0.0
    risk_tolerance = (user.risk_tolerance or "medium").lower()

    savings_potential = step7_output.get("estimated_savings_potential", 0)
    reducible_expenses = step7_output.get("reducible_breakdown", {})

    # Step 1: Investment Readiness
    savings_ratio = savings_potential / income if income > 0 else 0

    if savings_ratio >= 0.2:
        investment_readiness = "stable"
        saving_behavior = "good"
    elif savings_ratio >= 0.1:
        investment_readiness = "cautious"
        saving_behavior = "average"
    else:
        investment_readiness = "needs_improvement"
        saving_behavior = "poor"

    # Step 2: Risk Profile
    if risk_tolerance == "low":
        risk_profile = "conservative" if saving_behavior in ["good", "average"] else "very conservative"
    elif risk_tolerance == "medium":
        risk_profile = "moderate" if saving_behavior in ["good", "average"] else "cautious"
    elif risk_tolerance == "high":
        risk_profile = "aggressive" if saving_behavior in ["good", "average"] else "moderate"
    else:
        risk_profile = "moderate"

    # Step 3: Recommended Options
    options_map = {
        "very conservative": ["Savings Account", "Government Bonds", "Fixed Deposits"],
        "conservative": ["Government Bonds", "Fixed Deposits", "Low-risk Mutual Funds"],
        "cautious": ["Balanced Mutual Funds", "Index Funds"],
        "moderate": ["Index Funds", "Balanced Mutual Funds"],
        "aggressive": ["Stocks", "ETFs", "High-risk Mutual Funds"]
    }

    recommended_options = options_map.get(risk_profile, ["Balanced Mutual Funds"])

    # Step 4: Reason
    reason_parts = []
    if saving_behavior in ["good", "average"]:
        reason_parts.append("Based on consistent savings")
    else:
        reason_parts.append("Based on limited savings capacity")

    discretionary_ratio = reducible_expenses.get("discretionary", 0) / income if income else 0
    if discretionary_ratio < 0.1:
        reason_parts.append("and controlled discretionary spending")
    else:
        reason_parts.append("but discretionary spending is high")

    reason = ", ".join(reason_parts)

    return {
        "risk_profile": risk_profile,
        "investment_readiness": investment_readiness,
        "recommended_options": recommended_options,
        "reason": reason
    }