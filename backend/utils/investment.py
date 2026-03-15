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
    financial_health = step7_output.get("financial_health", "Weak")
    reducible_expenses = step7_output.get("reducible_breakdown", {})


    if financial_health == "Poor":
        investment_readiness = "not_ready"

    elif financial_health == "Weak":
        investment_readiness = "needs_improvement"

    elif financial_health == "Good":
        investment_readiness = "cautious"

    elif financial_health == "Excellent":
        investment_readiness = "stable"

    else:
        investment_readiness = "cautious"

    # Step 2: Risk Profile
    if risk_tolerance == "low":

        if financial_health == "Poor":
            risk_profile = "very conservative"

        elif financial_health == "Weak":
            risk_profile = "conservative"

        elif financial_health == "Good":
            risk_profile = "conservative"

        else:
            risk_profile = "moderate"

    elif risk_tolerance == "medium":

        if financial_health == "Poor":
            risk_profile = "very conservative"

        elif financial_health == "Weak":
            risk_profile = "cautious"

        elif financial_health == "Good":
            risk_profile = "moderate"

        else:
            risk_profile = "aggressive"

    elif risk_tolerance == "high":

        if financial_health == "Poor":
            risk_profile = "conservative"

        elif financial_health == "Weak":
            risk_profile = "moderate"

        elif financial_health == "Good":
            risk_profile = "aggressive"

        else:
            risk_profile = "aggressive"

    else:
        risk_profile = "moderate"

    if financial_health == "Poor":
        invest_ratio = 0.20

    elif financial_health == "Weak":
        invest_ratio = 0.35

    elif financial_health == "Good":
        invest_ratio = 0.60

    else:
        invest_ratio = 0.75

    suggested_investment = savings_potential * invest_ratio

    # Step 3: Recommended Options
    options_map = {
        "very conservative": ["Savings Account", "Government Bonds", "Fixed Deposits"],
        "conservative": ["Government Bonds", "Fixed Deposits", "Low-risk Mutual Funds"],
        "cautious": ["Balanced Mutual Funds", "Index Funds"],
        "moderate": ["Index Funds", "Balanced Mutual Funds"],
        "aggressive": ["Stocks", "ETFs", "High-risk Mutual Funds"]
    }

    recommended_options = options_map.get(risk_profile, ["Balanced Mutual Funds"])


    return {
        "risk_profile": risk_profile,
        "investment_readiness": investment_readiness,
        "recommended_options": recommended_options,
        "suggested_investment_amount": round(suggested_investment, 2)
    }