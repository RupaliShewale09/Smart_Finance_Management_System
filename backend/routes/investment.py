from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.schemas.investment import InvestmentRequest, InvestmentResponse
from backend.utils.investment import suggest_investment
from backend.utils.saving_estimator import estimate_savings_potential
from backend.database import SessionLocal, User
from datetime import date

router = APIRouter(prefix="/investments", tags=["Investment Suggestions"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=InvestmentResponse)
def get_investment_suggestions(
    request: InvestmentRequest = Depends(InvestmentRequest.as_form), 
    db: Session = Depends(get_db)
):

    start_date = request.start_date or date.today().replace(day=1)  # 1st day of current month
    end_date = request.end_date or date.today()                     # today

    # Step 1️⃣: Fetch Step 7 savings potential
    step7_output = estimate_savings_potential(
        db=db,
        user_id=request.user_id,
        start_date=start_date,
        end_date=end_date
    )


    if not step7_output:
        raise HTTPException(status_code=404, detail="User or savings data not found")

    # Step 2️⃣: Only fetch required fields
    savings_potential = step7_output.get("estimated_savings_potential", 0)
    income = step7_output.get("income", 0)
    reducible_expenses = step7_output.get("reducible_breakdown", {})

    # Step 3️⃣: Call Step 8 utility to generate suggestions
    investment_suggestions = suggest_investment(
        user_id=request.user_id,
        step7_output={
            "estimated_savings_potential": savings_potential,
            "income": income,
            "reducible_breakdown": reducible_expenses
        }
    )

    if not investment_suggestions:
        raise HTTPException(status_code=404, detail="Investment suggestions could not be generated")

    return investment_suggestions
