from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.utils.ai_nudge_engine import (
    analyze_user_behavior,
    generate_nudge,
    can_send_nudge,
    save_nudge
)


router = APIRouter(prefix="/nudges", tags=["AI Nudges"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/run/{user_id}")
def run_nudge_engine(user_id: int, db: Session = Depends(get_db)):
    behavior = analyze_user_behavior(user_id, db)
    if not behavior:
        return {
            "status": "no_nudge",
            "reason": "No transaction data found for this user in the lookback period."
        }

    if not can_send_nudge(user_id, behavior["type"], db):
        return {
            "status": "rate_limited"
        }

    message = generate_nudge(behavior)
    save_nudge(user_id, behavior["type"], behavior["severity"], message, db)

    return {"nudge": message}
