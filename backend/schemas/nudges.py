from pydantic import BaseModel
from datetime import datetime


class NudgeResponse(BaseModel):
    id: int
    nudge_type: str
    severity: str
    message: str
    delivered_at: datetime

    class Config:
        from_attributes = True