from pydantic import BaseModel, Field, ValidationError
from fastapi import Form
from fastapi.exceptions import RequestValidationError


# ---------- Scan & Pay ----------

class ScanPay(BaseModel):
    user_id: int
    receiver_wallet_id: str
    amount: float = Field(..., gt=0)

    @classmethod
    def as_form(
        cls,
        user_id: int = Form(...),
        receiver_wallet_id: str = Form(...),
        amount: float = Form(...)
    ):
        try:
            return cls(
                user_id=user_id,
                receiver_wallet_id=receiver_wallet_id,
                amount=amount
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())


class ScanPayResponse(BaseModel):
    message: str
    transaction_id: int
    expense_id: int
    remaining_balance: float
    expense_category: str
    urgency: str
