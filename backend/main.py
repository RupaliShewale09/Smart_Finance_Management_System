from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

import backend.database as database
from backend.routes import auth, scan_pay, insights, spend_limit, coach, savings, investment, nudges, wallet

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
app.include_router(wallet.router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")
DASHBOARD_DIR = os.path.join(FRONTEND_DIR, "dashboard")

app.mount("/dashboard", StaticFiles(directory=DASHBOARD_DIR), name="dashboard")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def select():
    return FileResponse(os.path.join(FRONTEND_DIR, "profile-select.html"))

@app.get("/login")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/register")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "register.html"))

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse(os.path.join(DASHBOARD_DIR, "base.html"))


@app.on_event("startup")
def start_background_jobs():
    start_scheduler()



if __name__ == "__main__":
    # uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
    port = int(os.environ.get("PORT", 8000)) 
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)