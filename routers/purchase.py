from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth
from typing import List

router = APIRouter()

TIER_RULES = {
    "coronet": {"cashback_pct": 0.10, "cap": 2000, "max_redemptions": 1},
    "regalia": {"cashback_pct": 0.20, "cap": 3500, "max_redemptions": 2},
    "sovereign": {"cashback_pct": 0.30, "cap": 5000, "max_redemptions": 2},
}

@router.post("/initiate", response_model=schemas.PurchaseOut)
def initiate_purchase(payload: schemas.PurchaseCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(models.Brand.id == payload.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    if not brand.is_active:
        raise HTTPException(status_code=400, detail="Brand is not active")

    score = db.query(models.CrowndScore).filter(models.CrowndScore.user_id == current_user.id).first()
    user_score = score.total_score if score else 0
    if user_score < brand.min_crownd_score:
        raise HTTPException(status_code=403, detail=f"Your Crownd Score is too low for this brand. Required: {brand.min_crownd_score}")

    past_purchases = db.query(models.Purchase).filter(
        models.Purchase.user_id == current_user.id,
        models.Purchase.brand_id == payload.brand_id,
        models.Purchase.status == models.PurchaseStatus.cashback_credited
    ).count()

    tier_key = brand.campaign_tier.value
    rules = TIER_RULES.get(tier_key, TIER_RULES["coronet"])

    if past_purchases >= rules["max_redemptions"]:
        raise HTTPException(status_code=400, detail=f"You have reached the maximum cashback redemptions for {brand.name}")

    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).first()
    if not wallet or wallet.balance < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    cashback_amount = min(
        payload.amount * rules["cashback_pct"],
        rules["cap"],
        brand.cashback_percentage / 100 * payload.amount
    )

    is_first = past_purchases == 0
    voucher_issued = is_first

    wallet.balance -= payload.amount

    debit_tx = models.Transaction(
        wallet_id=wallet.id,
        amount=payload.amount,
        type="debit",
        description=f"Purchase at {brand.name}"
    )
    db.add(debit_tx)

    purchase = models.Purchase(
        user_id=current_user.id,
        brand_id=payload.brand_id,
        amount=payload.amount,
        cashback_amount=cashback_amount,
        status=models.PurchaseStatus.post_required,
        is_first_purchase=is_first,
        voucher_issued=voucher_issued
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    return purchase

@router.get("/my", response_model=List[schemas.PurchaseOut])
def get_my_purchases(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    purchases = db.query(models.Purchase).filter(
        models.Purchase.user_id == current_user.id
    ).order_by(models.Purchase.created_at.desc()).all()
    return purchases

@router.get("/{purchase_id}", response_model=schemas.PurchaseOut)
def get_purchase(purchase_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    purchase = db.query(models.Purchase).filter(
        models.Purchase.id == purchase_id,
        models.Purchase.user_id == current_user.id
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase