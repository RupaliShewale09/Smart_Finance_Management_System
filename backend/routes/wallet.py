from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

import backend.schemas.auth as schemas
import backend.database as database


router = APIRouter(tags=["Transactions and wallet"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/wallet/add-money")
def add_money(
    data: schemas.WalletAddMoney = Depends(schemas.WalletAddMoney.as_form),
    db: Session = Depends(get_db)
):
    # Find the wallet belonging to the user
    wallet = db.query(database.Wallet).filter(
        database.Wallet.owner_type == "user",
        database.Wallet.owner_id == data.user_id
    ).first()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Update balance
    wallet.balance += data.amount
    db.commit()
    db.refresh(wallet)

    return {
        "message": f"Successfully added ₹{data.amount}",
        "new_balance": wallet.balance
    }

@router.get("/transactions/history/vendor/{vendor_id}")
def get_vendor_transaction_history(vendor_id: int, db: Session = Depends(get_db)):

    vendor_exists = db.query(database.Vendor).filter(database.Vendor.id == vendor_id).first()
    if not vendor_exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Only fetch incoming (received) transactions for this vendor
    transactions = (
        db.query(database.Transaction)
        .filter(
            database.Transaction.status == "success",
            database.Transaction.receiver_id == vendor_id,
            database.Transaction.receiver_type == "vendor"
        )
        .order_by(database.Transaction.timestamp.desc())
        .all()
    )

    history = []

    for tx in transactions:
        # Sender is always a User (only users can send payments)
        sender = db.query(database.User).filter(database.User.id == tx.sender_id).first()
        counterparty = sender.username if sender else "Unknown User"

        history.append({
            "id": tx.id,
            "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
            "amount": float(tx.amount),
            "type": "Received",
            "party_name": counterparty,
            "party_wallet_id": tx.sender_wallet_id,
            "category": vendor_exists.category,   # vendor's own category
            "urgency": None,
            "status": tx.status,
            "is_expense": False
        })

    return history


@router.get("/transactions/history/{user_id}")
def get_transaction_history(user_id: int, db: Session = Depends(get_db)):

    user_exists = db.query(database.User).filter(database.User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = (
        db.query(database.Transaction)
        .filter(
            database.Transaction.status == "success",
            (
                (database.Transaction.sender_id == user_id) |
                ((database.Transaction.receiver_id == user_id) & (database.Transaction.receiver_type == "user"))
            )
        )
        .order_by(database.Transaction.timestamp.desc())
        .all()
    )

    history = []

    for tx in transactions:
        # Default values (original logic)
        tx_type = "Unknown"
        is_expense = False
        counterparty = "Unknown"
        category = "Other"
        
        expense_record = db.query(database.Expense).filter(
            database.Expense.user_id == user_id,
            database.Expense.amount == tx.amount
        ).order_by(database.Expense.timestamp.desc()).first()
        
        expense_category = expense_record.category if expense_record else None
        db_urgency = expense_record.urgency if expense_record else None

        # ---------------- OUTGOING ----------------
        if tx.sender_id == user_id:
            tx_type = "Sent"
            if tx.receiver_type == "vendor":
                vendor = db.query(database.Vendor).filter(database.Vendor.id == tx.receiver_id).first()
                counterparty = vendor.business_name if vendor else "Vendor"
                category = vendor.category if vendor else "General"
                is_expense = True
            elif tx.receiver_type == "user":
                receiver = db.query(database.User).filter(database.User.id == tx.receiver_id).first()
                counterparty = receiver.username if receiver else "Other User"
                category = "Transfer"

        # ---------------- INCOMING ----------------
        elif tx.receiver_id == user_id and tx.receiver_type == "user":
            tx_type = "Received"
            is_expense = False
            category = "Other"
            sender = db.query(database.User).filter(database.User.id == tx.sender_id).first()
            counterparty = sender.username if sender else "External Source"

        history.append({
            "id": tx.id,
            "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
            "amount": float(tx.amount),
            "type": tx_type,
            "party_name": counterparty,
            "party_wallet_id": tx.receiver_wallet_id if tx.sender_id == user_id else tx.sender_wallet_id,
            "category": category, # Original Logic category
            "expense_category": expense_category, # From Expenses Table
            "urgency": db_urgency, # From Expenses Table
            "status": tx.status,
            "is_expense": is_expense
        })

    return history