from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, time

import backend.database as database
from backend.utils.saving_estimator import estimate_savings_potential
from backend.schemas.savings import SavingsRequest, SavingsResponse

router = APIRouter(prefix="/savings", tags=["Savings Potential"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/estimate", response_model=SavingsResponse)
def estimate_savings(
    data: SavingsRequest = Depends(SavingsRequest.as_form),
    db: Session = Depends(get_db)
):
    if data.start_date > data.end_date:
        raise HTTPException(400, "Invalid date range")

    start_dt = datetime.combine(data.start_date, time.min)
    end_dt   = datetime.combine(data.end_date, time.max)

    result = estimate_savings_potential(
        db=db,
        user_id=data.user_id,
        start_date=start_dt,
        end_date=end_dt
    )

    if not result:
        raise HTTPException(404, "User not found")

    return result
