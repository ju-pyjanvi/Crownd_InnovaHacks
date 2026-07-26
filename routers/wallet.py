from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth
import razorpay
import os
import hmac
import hashlib
from typing import List

router = APIRouter()

rz_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)

@router.get("/", response_model=schemas.WalletOut)
def get_wallet(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

@router.post("/load", response_model=schemas.RazorpayOrderOut)
def load_wallet(payload: schemas.WalletLoad, current_user: models.User = Depends(auth.get_current_user)):
    if payload.amount < 100:
        raise HTTPException(status_code=400, detail="Minimum load amount is ₹100")

    order = rz_client.order.create({
        "amount": int(payload.amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key_id": os.getenv("RAZORPAY_KEY_ID")
    }

@router.post("/verify-payment")
def verify_payment(payload: schemas.PaymentVerify, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    generated_signature = hmac.new(
        os.getenv("RAZORPAY_KEY_SECRET").encode(),
        f"{payload.razorpay_order_id}|{payload.razorpay_payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    if generated_signature != payload.razorpay_signature:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    order_details = rz_client.order.fetch(payload.razorpay_order_id)
    amount_paid = order_details["amount"] / 100

    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).first()
    wallet.balance += amount_paid

    transaction = models.Transaction(
        wallet_id=wallet.id,
        amount=amount_paid,
        type="credit",
        description="Wallet top-up via Razorpay",
        razorpay_order_id=payload.razorpay_order_id,
        razorpay_payment_id=payload.razorpay_payment_id
    )
    db.add(transaction)
    db.commit()
    db.refresh(wallet)

    return {"message": "Wallet loaded successfully", "new_balance": wallet.balance}

@router.get("/transactions", response_model=List[schemas.TransactionOut])
def get_transactions(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    transactions = db.query(models.Transaction).filter(
        models.Transaction.wallet_id == wallet.id
    ).order_by(models.Transaction.created_at.desc()).all()

    return transactions