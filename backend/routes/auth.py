from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import re

import backend.schemas.auth as schemas
import backend.database as database
from backend.utils.gen_wallet import generate_wallet_id

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------- DB Dependency ----------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_pass(p, c):
    if p != c: raise HTTPException(400, "Passwords do not match")
    if not (re.search(r"[A-Za-z]", p) and re.search(r"[0-9]", p)):
        raise HTTPException(400, "Password must contain letters and numbers")

# ================= USER AUTH =================

@router.post("/user/register")
def register(
    user: schemas.UserCreate = Depends(schemas.UserCreate.as_form),
    db: Session = Depends(get_db)
):    
    validate_pass(user.password, user.confirm_password)
    
    # Check if user already exists
    existing_user = db.query(database.User).filter(
        (database.User.email == user.email) | 
        (database.User.phone == user.phone) 
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or Phone already registered")
    
    hashed_pwd = database.pwd_context.hash(user.password)
    new_user = database.User(
        username=user.username, 
        email=user.email, 
        phone=user.phone, 
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    wallet = database.Wallet(
        wallet_id=generate_wallet_id("user"),
        owner_type="user",
        owner_id=new_user.id,
        balance=user.initial_balance
    )
    db.add(wallet)
    db.commit()

    return {
        "message": "User Registered Successfully",
        "wallet_id": wallet.wallet_id,
        "balance": wallet.balance
    }

@router.post("/user/login")
def login(
    user: schemas.UserLogin = Depends(schemas.UserLogin.as_form),
    db: Session = Depends(get_db)
):
    # Check if identifier is email or phone or username
    db_user = db.query(database.User).filter(
        (database.User.email == user.identifier) | 
        (database.User.phone == user.identifier) |
        (database.User.username == user.identifier)
    ).first()
    
    if not db_user or not database.pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful", "user_id": db_user.id}


@router.get("/users/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    wallet = db.query(database.Wallet).filter(
        database.Wallet.owner_type == "user",
        database.Wallet.owner_id == user.id
    ).first()

    return {
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "income": user.income,
        "savings_goal": user.savings_goal,
        "risk_tolerance": user.risk_tolerance,
        "wallet": {
            "wallet_id": wallet.wallet_id if wallet else None,
            "balance": wallet.balance if wallet else 0.0
        }
    }


@router.put("/users/profile/{user_id}")
def update_profile(
    user_id: int,
    profile: schemas.ProfileUpdate = Depends(schemas.ProfileUpdate.as_form),
    db: Session = Depends(get_db)
):
    db_user = db.query(database.User).filter(database.User.id == user_id).first()
    if not db_user:
         raise HTTPException(status_code=404, detail="User not found")
    
    db_user.income = profile.monthly_income
    db_user.savings_goal = profile.savings_goal
    db_user.risk_tolerance = profile.risk_tolerance
    db.commit()
    return {"message": "Profile updated"}


# ================= VENDOR AUTH =================

@router.post("/vendor/register")
def vendor_register(
    vendor: schemas.VendorRegister = Depends(schemas.VendorRegister.as_form),
    db: Session = Depends(get_db)
):
    validate_pass(vendor.password, vendor.confirm_password)
    
    if db.query(database.Vendor).filter(
        (database.Vendor.email == vendor.email) |
        (database.Vendor.phone == vendor.phone)
    ).first():
        raise HTTPException(status_code=400, detail="Email or Phone already registered")

    hashed_password = database.pwd_context.hash(vendor.password)

    new_vendor = database.Vendor(
        business_name=vendor.business_name,
        email=vendor.email,
        phone=vendor.phone,
        category=vendor.category,
        hashed_password=hashed_password
    )
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)

    wallet = database.Wallet(
        wallet_id=generate_wallet_id("vendor"),
        owner_type="vendor",
        owner_id=new_vendor.id,
        balance=vendor.initial_balance
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)

    return {
        "message": "Vendor registered successfully",
        "wallet_id": wallet.wallet_id
    }

@router.post("/vendor/login")
def vendor_login(
    login: schemas.UserLogin = Depends(schemas.UserLogin.as_form),
    db: Session = Depends(get_db)
):
    vendor = db.query(database.Vendor).filter(
        (database.Vendor.business_name == login.identifier) |
        (database.Vendor.email == login.identifier) |
        (database.Vendor.phone == login.identifier)
    ).first()

    if not vendor or not database.pwd_context.verify(
        login.password, vendor.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "vendor_id": vendor.id}


@router.get("/vendors/profile/{vendor_id}")
def get_vendor_profile(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(database.Vendor).filter(
        database.Vendor.id == vendor_id
    ).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    wallet = db.query(database.Wallet).filter(
        database.Wallet.owner_type == "vendor",
        database.Wallet.owner_id == vendor.id
    ).first()

    return {
        "vendor_id": vendor.id,
        "business_name": vendor.business_name,
        "email": vendor.email,
        "phone": vendor.phone,
        "category": vendor.category,
        "wallet": {
            "wallet_id": wallet.wallet_id if wallet else None,
            "balance": wallet.balance if wallet else 0.0
        }
    }
