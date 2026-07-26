from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth
from typing import List

router = APIRouter()

@router.get("/", response_model=List[schemas.BrandOut])
def get_all_brands(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    brands = db.query(models.Brand).filter(models.Brand.is_active == True).all()
    return brands

@router.get("/{brand_id}", response_model=schemas.BrandOut)
def get_brand(brand_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.get("/tier/{tier}", response_model=List[schemas.BrandOut])
def get_brands_by_tier(tier: schemas.CampaignTier, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    brands = db.query(models.Brand).filter(
        models.Brand.campaign_tier == tier,
        models.Brand.is_active == True
    ).all()
    return brands

@router.post("/admin/create", response_model=schemas.BrandOut)
def create_brand(brand: schemas.BrandCreate, db: Session = Depends(get_db)):
    new_brand = models.Brand(
        name=brand.name,
        description=brand.description,
        logo_url=brand.logo_url,
        category=brand.category,
        campaign_tier=brand.campaign_tier,
        cashback_percentage=brand.cashback_percentage,
        max_cashback_cap=brand.max_cashback_cap,
        max_redemptions_per_user=brand.max_redemptions_per_user,
        monthly_budget=brand.monthly_budget,
        min_crownd_score=brand.min_crownd_score
    )
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return new_brand

@router.get("/eligible/me", response_model=List[schemas.BrandOut])
def get_eligible_brands(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    score = db.query(models.CrowndScore).filter(models.CrowndScore.user_id == current_user.id).first()
    user_score = score.total_score if score else 0

    brands = db.query(models.Brand).filter(
        models.Brand.is_active == True,
        models.Brand.min_crownd_score <= user_score
    ).all()
    return brands
