from pydantic import BaseModel, ValidationError
from fastapi import Form
from fastapi.exceptions import RequestValidationError
from datetime import date
from typing import List, Optional

class InvestmentRequest(BaseModel):
    user_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @classmethod
    def as_form(
        cls,
        user_id: int = Form(...),
        start_date: Optional[str] = Form(None),  # yyyy-mm-dd
        end_date: Optional[str] = Form(None)
    ):
        try:
            parsed_start = None
            parsed_end = None

            # Start date
            if start_date:
                try:
                    parsed_start = date.fromisoformat(start_date)
                except ValueError:
                    parsed_start = None  # ignore invalid string

            # End date
            if end_date:
                try:
                    parsed_end = date.fromisoformat(end_date)
                except ValueError:
                    parsed_end = None  # ignore invalid string
            return cls(
                user_id=user_id,
                start_date=parsed_start,
                end_date=parsed_end
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())


class InvestmentResponse(BaseModel):
    risk_profile: str
    investment_readiness: str
    recommended_options: List[str]
    reason: str
