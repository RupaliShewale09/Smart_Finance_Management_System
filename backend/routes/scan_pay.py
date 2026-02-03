from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

import backend.database as database
from backend.schemas.scanpay import ScanPay, ScanPayResponse
from backend.utils.predict_category import is_recurring_transaction, predict_expense_category

router = APIRouter(prefix="/payments", tags=["Scan & Pay"])

# DB Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/scan-pay", response_model=ScanPayResponse)
def scan_and_pay(
    payload: ScanPay = Depends(ScanPay.as_form),
    db: Session = Depends(get_db)
):
    # 1️⃣ Fetch sender wallet
    sender_wallet = db.query(database.Wallet).filter(
        database.Wallet.owner_type == "user",
        database.Wallet.owner_id == payload.user_id
    ).first()

    if not sender_wallet:
        raise HTTPException(status_code=404, detail="User wallet not found")

    # 2️⃣ Fetch vendor wallet
    receiver_wallet = db.query(database.Wallet).filter(
        database.Wallet.wallet_id == payload.receiver_wallet_id,
    ).first()

    if not receiver_wallet:
        raise HTTPException(status_code=404, detail="Receiver wallet not found")
    
    receiver_type = receiver_wallet.owner_type   # "user" or "vendor"

    # 3️⃣ Balance check
    if payload.amount <= 0:
        raise HTTPException(400, "Invalid amount")
    
    if payload.amount > sender_wallet.balance:
        raise HTTPException(400, "Insufficient wallet balance")

    # Save pre-balance for ML
    sender_balance_pre = sender_wallet.balance

    # 4️⃣ Update balances
    sender_wallet.balance -= payload.amount
    receiver_wallet.balance += payload.amount

    # 5️⃣ Create transaction record
    transaction = database.Transaction(
        sender_id=payload.user_id,
        sender_wallet_id=sender_wallet.wallet_id,
        receiver_id=receiver_wallet.owner_id,
        receiver_wallet_id=receiver_wallet.wallet_id,
        receiver_type=receiver_type,
        amount=payload.amount,
        status="success",
        timestamp=datetime.utcnow()
    )


    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    if receiver_type == "vendor":
        receiver = db.query(database.Vendor).filter(
            database.Vendor.id == receiver_wallet.owner_id
        ).first()

        merchant_name = receiver.business_name
        merchant_category = receiver.category

    else:  # receiver_type == "user"
        receiver = db.query(database.User).filter(
            database.User.id == receiver_wallet.owner_id
        ).first()

        merchant_name = receiver.username
        merchant_category = "Other" 

     # 7️⃣ Calculate is_recurring for both cases
    is_recurring = is_recurring_transaction(
        db=db,
        user_id=payload.user_id,
        merchant_name=merchant_name
    )   


    # ML prediction
    predicted_category, predicted_urgency = predict_expense_category(
        merchant_name=merchant_name,
        merchant_category=merchant_category,
        amount=payload.amount,
        is_recurring=is_recurring,
        user_balance_pre=sender_balance_pre,
        timestamp=transaction.timestamp
    )

    expense = database.Expense(
        user_id=payload.user_id,
        merchant_name=merchant_name,
        merchant_category=merchant_category,
        amount=payload.amount,
        category=predicted_category,
        urgency=predicted_urgency,
        timestamp=datetime.utcnow()
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return {
        "message": "Scan & Pay successful",
        "transaction_id": transaction.id,
        "expense_id": expense.id,
        "remaining_balance": sender_wallet.balance,
        "expense_category": predicted_category,
        "urgency": predicted_urgency
    }
