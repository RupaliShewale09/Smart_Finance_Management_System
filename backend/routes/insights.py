from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, time

import backend.database as database
from backend.utils.gen_insights import generate_insights
from backend.schemas.insights import SpendingInsightsResponse, InsightsForm

router = APIRouter(prefix="/insights", tags=["Spending Insights"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/spending-form", response_model=SpendingInsightsResponse)
def get_spending_insights_form(
    data: InsightsForm = Depends(InsightsForm.as_form),
    db: Session = Depends(get_db)
):
    if data.start_date > data.end_date:
        raise HTTPException(400, "Invalid date range")
    
    start_dt = datetime.combine(data.start_date, time.min)  # 00:00:00
    end_dt   = datetime.combine(data.end_date, time.max)    # 23:59:59

    return generate_insights(
        db=db,
        user_id=data.user_id,
        start_date=start_dt,
        end_date=end_dt
    )

