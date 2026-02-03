from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

import backend.database as database
from backend.routes import auth, scan_pay, insights, spend_limit, coach, savings, investment, nudges

from backend.utils.nudge_scheduler import start_scheduler

database.init_db()

app = FastAPI(title="Smart Finance Management System")

app.include_router(auth.router)
app.include_router(scan_pay.router)   # step 2 & 3
app.include_router(insights.router)    # step 4
app.include_router(spend_limit.router)  # step 5
app.include_router(coach.router)  # step 6
app.include_router(savings.router)  # step 7
app.include_router(investment.router)
app.include_router(nudges.router)

@app.on_event("startup")
def start_background_jobs():
    start_scheduler()

@app.get("/")
def root():
    return {"status": "API running successfully"}


if __name__ == "__main__":
    # uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
    port = int(os.environ.get("PORT", 8000)) 
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)
