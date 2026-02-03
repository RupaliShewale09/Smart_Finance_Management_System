from pydantic import BaseModel, ValidationError
from fastapi import Form
from fastapi.exceptions import RequestValidationError
from datetime import date
from typing import Dict


class SavingsRequest(BaseModel):
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


class SavingsResponse(BaseModel):
    income: float
    estimated_savings_potential: float
    savings_percentage: float
    reducible_breakdown: Dict[str, float]
    message: str
