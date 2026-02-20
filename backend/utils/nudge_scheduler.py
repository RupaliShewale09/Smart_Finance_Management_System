from apscheduler.schedulers.background import BackgroundScheduler
from backend.database import SessionLocal, User
from backend.utils.ai_nudge_engine import (
    analyze_user_behavior,
    generate_nudge,
    can_send_nudge,
    save_nudge
)
from loguru import logger

def run_nudges():
    logger.info("--- Nudge Engine Job Started ---")
    db = SessionLocal()
    try:
        users = db.query(User).all()
        logger.info(f"Checking {len(users)} users for potential nudges...")

        for user in users:
            # 1. Analyze behavior
            behavior = analyze_user_behavior(user.id, db)
            if not behavior:
                logger.info(f"User {user.id}: No significant behavior detected.")
                continue

            # 2. Check rate limit
            if not can_send_nudge(user.id, behavior["type"], db):
                logger.info(f"User {user.id}: Nudge type '{behavior['type']}' is currently rate-limited.")
                continue

            # 3. Generate Nudge
            message = generate_nudge(behavior)
            
            # 4. Save to Database
            save_nudge(
                user.id,
                behavior["type"],
                behavior["severity"],
                message,
                db
            )
            logger.success(f"SUCCESS: Nudge saved for User {user.id}: '{message}'")

    except Exception as e:
        logger.error(f"ERROR in Nudge Scheduler: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_nudges, "interval", minutes=180)  ## change this
    scheduler.start()
    logger.info("Scheduler started successfully.")