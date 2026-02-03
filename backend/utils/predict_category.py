import joblib
import os
from datetime import datetime, timedelta
import backend.database as database
from sqlalchemy.orm import Session
import pandas as pd

# ===== Load ML models once =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "resources", "Expense_categorization.pkl")
MERCHANT_NAME_ENCODER = os.path.join(BASE_DIR, "resources", "merchant_name_encoder.pkl")
MERCHANT_CATEGORY_ENCODER = os.path.join(BASE_DIR, "resources", "merchant_category_encoder.pkl")

expense_model = joblib.load(MODEL_PATH)
merchant_name_encoder = joblib.load(MERCHANT_NAME_ENCODER)
merchant_category_encoder = joblib.load(MERCHANT_CATEGORY_ENCODER)



def is_recurring_transaction(
    db: Session,
    user_id: int,
    merchant_name: str,
    lookback_days: int = 30
) -> int:
    """
    Returns:
    1 -> recurring
    0 -> not recurring
    """

    start_date = datetime.utcnow() - timedelta(days=lookback_days)

    count = db.query(database.Expense).filter(
        database.Expense.user_id == user_id,
        database.Expense.merchant_name == merchant_name,
        database.Expense.timestamp >= start_date
    ).count()

    return 1 if count >= 2 else 0


# ===== Prediction Function =====
def predict_expense_category(
    merchant_name: str,
    merchant_category: str,
    amount: float,
    is_recurring: int,
    user_balance_pre: float,
    timestamp: datetime
):
    """
    Returns:
    - predicted_category
    - predicted_urgency
    """

    hour = timestamp.hour
    day_of_week = timestamp.weekday()

    try:
        merchant_category_encoded = merchant_category_encoder.transform([merchant_category])[0]
    except Exception:
        merchant_category_encoded = 0  # Unknown category

    try:
        merchant_name_encoded = merchant_name_encoder.transform([merchant_name])[0]
    except Exception:
        merchant_name_encoded = 0  # Unknown merchant


    cols = [
        'merchant_name',
        'merchant_category',
        'amount',
        'is_recurring',
        'user_balance_pre',
        'hour',
        'day_of_week'
    ]

    feature_df = pd.DataFrame([[
        merchant_name_encoded,
        merchant_category_encoded,
        amount,
        is_recurring,
        user_balance_pre,
        hour,
        day_of_week
    ]], columns=cols)

    prediction = expense_model.predict(feature_df)[0]

    category_map = {
        2: "red",
        1: "orange",
        0: "yellow"
    }

    predicted_category = category_map.get(int(prediction), "unknown")

    # 🔹 Map category → urgency (example logic)
    urgency_map = {
        "red": "critical",
        "orange": "necessary",
        "yellow": "discretionary"
    }

    predicted_urgency = urgency_map.get(predicted_category, "unknown")

    return predicted_category, predicted_urgency