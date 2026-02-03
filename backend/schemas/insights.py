from pydantic import BaseModel
from typing import Dict

from pydantic import BaseModel, ValidationError
from fastapi import Form
from fastapi.exceptions import RequestValidationError
from datetime import date


class InsightsForm(BaseModel):
    user_id: int
    start_date: date
    end_date: date

    @classmethod
    def as_form(
        cls,
        user_id: int = Form(...),
        start_date: str = Form(...),  # yyyy-mm-dd
        end_date: str = Form(...)
    ):
        try:
            return cls(
                user_id=user_id,
                start_date=date.fromisoformat(start_date),
                end_date=date.fromisoformat(end_date)
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())


class SpendingInsightsResponse(BaseModel):
    total_spent: float
    category_wise_spending: Dict[str, float]
    category_percentages: Dict[str, float]
    high_urgency_expenses: int
    distinct_recurring_merchants: int
    savings_warning: str
