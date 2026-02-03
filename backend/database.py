from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from datetime import datetime
import os


# Database Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '../finance_app.db')}"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Password Hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

#----------------------USERS-----------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    income = Column(Float, default=0.0)
    savings_goal = Column(Float, default=0.0)
    risk_tolerance = Column(String, default="medium")

# ---------------- VENDORS ----------------
class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False) 
    hashed_password = Column(String, nullable=False)

# ---------------- WALLETS ----------------
class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True)
    wallet_id = Column(String, unique=True, index=True, nullable=False)
    owner_type = Column(String, nullable=False)  # "user" or "vendor"
    owner_id = Column(Integer, nullable=False)   # user.id or vendor.id
    balance = Column(Float, default=0.0)


# ---------------- TRANSACTIONS ----------------
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, index=True)         # user sending money
    sender_wallet_id = Column(String, index=True)

    receiver_id = Column(Integer, index=True)       # user or vendor receiving
    receiver_wallet_id = Column(String, index=True)
    receiver_type = Column(String, nullable=False)  # "user" or "vendor"

    amount = Column(Float,nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # success / failed


# Expense categorization
class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    merchant_name = Column(String, nullable=False)
    merchant_category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category = Column(String)
    urgency = Column(String)


class UserSpendLimit(Base):
    __tablename__ = "user_spend_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    category = Column(String, nullable=False)
    limit = Column(Float, nullable=False)
    alert_threshold = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CoachConversation(Base):
    __tablename__ = "coach_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    user_message = Column(String, nullable=False)
    ai_response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class FinancialNudge(Base):
    __tablename__ = "financial_nudges"


    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    nudge_type = Column(String) # alert / behavior / literacy
    severity = Column(String) # low / medium / high
    message = Column(String)
    delivered_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)