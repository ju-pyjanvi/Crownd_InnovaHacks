from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth
from datetime import datetime
import os
import requests
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

# ============================================================
# INSTAGRAM GRAPH API HELPERS
# ============================================================

INSTAGRAM_API_BASE = "https://graph.instagram.com/v18.0"

def get_token() -> str:
    return os.getenv("INSTAGRAM_ACCESS_TOKEN", "mock")

def extract_shortcode(post_url: str) -> Optional[str]:
    """Extract shortcode from Instagram URL.
    Handles: instagram.com/p/ABC123/, instagram.com/reel/ABC123/
    """
    url = post_url.rstrip("/")
    parts = url.split("/")
    for i, part in enumerate(parts):
        if part in ("p", "reel", "tv") and i + 1 < len(parts):
            return parts[i + 1]
    return None

def fetch_post_by_url(post_url: str, instagram_handle: str) -> dict:
    """
    Fetch Instagram post data using Graph API.
    Uses the user's own media since Graph API only allows
    reading posts from the authenticated user's own account.
    """
    token = get_token()

    if token == "mock":
        return _mock_verify(post_url)

    shortcode = extract_shortcode(post_url)
    if not shortcode:
        return {
            "verified": False,
            "message": "Could not parse Instagram URL. Use a direct post or reel link.",
            "post_data": None
        }

    # Step 1: Get authenticated user's media list and find matching post
    try:
        # Fetch user's recent media
        media_resp = requests.get(
            f"{INSTAGRAM_API_BASE}/me/media",
            params={
                "fields": "id,shortcode,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
                "access_token": token,
                "limit": 50
            },
            timeout=10
        )
        media_data = media_resp.json()

        if "error" in media_data:
            return {
                "verified": False,
                "message": f"Instagram API error: {media_data['error'].get('message', 'Unknown error')}",
                "post_data": None
            }

        # Find the post matching the shortcode
        matched_post = None
        for post in media_data.get("data", []):
            if post.get("shortcode") == shortcode or shortcode in post.get("permalink", ""):
                matched_post = post
                break

        if not matched_post:
            return {
                "verified": False,
                "message": "Post not found in your Instagram account. Make sure the post is public and belongs to your registered handle.",
                "post_data": None
            }

        return {
            "verified": True,
            "message": "Post found on Instagram.",
            "post_data": {
                "id": matched_post.get("id"),
                "shortcode": matched_post.get("shortcode"),
                "caption": matched_post.get("caption", ""),
                "media_type": matched_post.get("media_type"),
                "media_url": matched_post.get("media_url") or matched_post.get("thumbnail_url"),
                "permalink": matched_post.get("permalink"),
                "timestamp": matched_post.get("timestamp"),
                "like_count": matched_post.get("like_count", 0),
                "comments_count": matched_post.get("comments_count", 0),
            }
        }

    except requests.Timeout:
        return {"verified": False, "message": "Instagram API timed out. Try again.", "post_data": None}
    except Exception as e:
        return {"verified": False, "message": f"Error fetching post: {str(e)}", "post_data": None}


def check_brand_tag(caption: str, brand_name: str) -> bool:
    """Check if caption mentions the brand."""
    if not caption:
        return False
    caption_lower = caption.lower()
    brand_lower = brand_name.lower()
    # Check full brand name, brand without spaces, and common hashtag form
    checks = [
        brand_lower,
        brand_lower.replace(" ", ""),
        brand_lower.replace(" ", "_"),
        f"#{brand_lower.replace(' ', '')}",
        f"@{brand_lower.replace(' ', '')}",
    ]
    return any(c in caption_lower for c in checks)


def _mock_verify(post_url: str) -> dict:
    """Mock verification for demo/testing when no real token."""
    if "instagram.com" in post_url and ("p/" in post_url or "reel/" in post_url):
        return {
            "verified": True,
            "message": "Mock verification successful.",
            "post_data": {
                "id": "mock_12345",
                "shortcode": "mockABC123",
                "caption": "Just got the best pair of glasses from Lenskart! 😍 #Lenskart #CrowndCreator",
                "media_type": "IMAGE",
                "media_url": None,
                "permalink": post_url,
                "timestamp": datetime.utcnow().isoformat(),
                "like_count": 142,
                "comments_count": 18,
            }
        }
    return {
        "verified": False,
        "message": "Invalid Instagram URL. Must be a direct post or reel link.",
        "post_data": None
    }


# ============================================================
# CROWND SCORE UPDATER
# ============================================================

def update_crownd_score(user_id: str, brand_id: str, db: Session):
    score = db.query(models.CrowndScore).filter(
        models.CrowndScore.user_id == user_id
    ).first()
    if not score:
        return

    score.total_posts += 1
    score.verified_posts += 1

    unique_brands = db.query(models.Purchase.brand_id).filter(
        models.Purchase.user_id == user_id,
        models.Purchase.status == models.PurchaseStatus.cashback_credited
    ).distinct().count()

    score.unique_brands_posted = unique_brands
    score.brand_diversity_score = min(unique_brands * 10, 100)

    base_score = score.verified_posts * 15
    diversity_bonus = score.brand_diversity_score
    score.total_score = min(base_score + diversity_bonus, 1000)
    score.updated_at = datetime.utcnow()
    db.commit()


# ============================================================
# SCHEMAS (inline for post-specific responses)
# ============================================================

class PostData(BaseModel):
    id: Optional[str] = None
    shortcode: Optional[str] = None
    caption: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    permalink: Optional[str] = None
    timestamp: Optional[str] = None
    like_count: Optional[int] = 0
    comments_count: Optional[int] = 0

class PostVerifyDetailOut(BaseModel):
    verified: bool
    brand_tagged: bool
    message: str
    cashback_amount: Optional[float] = None
    post_data: Optional[PostData] = None


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/submit", response_model=PostVerifyDetailOut)
def submit_post(
    payload: schemas.PostSubmit,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Find purchase
    purchase = db.query(models.Purchase).filter(
        models.Purchase.id == payload.purchase_id,
        models.Purchase.user_id == current_user.id
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    if purchase.status not in [
        models.PurchaseStatus.post_required,
        models.PurchaseStatus.post_submitted
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Purchase is in '{purchase.status}' status — cannot submit post."
        )

    brand = db.query(models.Brand).filter(models.Brand.id == purchase.brand_id).first()

    # 2. Fetch post from Instagram
    result = fetch_post_by_url(
        post_url=payload.post_url,
        instagram_handle=current_user.instagram_handle or ""
    )

    purchase.post_url = payload.post_url
    purchase.post_submitted_at = datetime.utcnow()

    if not result["verified"]:
        purchase.status = models.PurchaseStatus.post_submitted
        db.commit()
        return PostVerifyDetailOut(
            verified=False,
            brand_tagged=False,
            message=result["message"],
            post_data=None
        )

    # 3. Check brand tag in caption
    post_data = result["post_data"]
    caption = post_data.get("caption", "") or ""
    brand_tagged = check_brand_tag(caption, brand.name)

    if not brand_tagged:
        purchase.status = models.PurchaseStatus.post_submitted
        db.commit()
        return PostVerifyDetailOut(
            verified=False,
            brand_tagged=False,
            message=f"Post found but brand '{brand.name}' is not mentioned in the caption. Add the brand name or tag and resubmit.",
            post_data=PostData(**post_data)
        )

    # 4. All checks passed — credit cashback
    purchase.post_verified = True
    purchase.post_verified_at = datetime.utcnow()
    purchase.status = models.PurchaseStatus.cashback_credited
    purchase.cashback_credited_at = datetime.utcnow()

    wallet = db.query(models.Wallet).filter(
        models.Wallet.user_id == current_user.id
    ).first()
    wallet.balance += purchase.cashback_amount
    wallet.total_cashback_earned += purchase.cashback_amount

    credit_tx = models.Transaction(
        wallet_id=wallet.id,
        amount=purchase.cashback_amount,
        type="credit",
        description=f"Cashback from {brand.name} 👑"
    )
    db.add(credit_tx)

    update_crownd_score(current_user.id, purchase.brand_id, db)
    db.commit()

    return PostVerifyDetailOut(
        verified=True,
        brand_tagged=True,
        message=f"Post verified! ₹{purchase.cashback_amount:.0f} cashback credited to your wallet 👑",
        cashback_amount=purchase.cashback_amount,
        post_data=PostData(**post_data)
    )


@router.get("/preview")
def preview_post(
    post_url: str,
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Fetch and preview an Instagram post before submitting.
    Frontend can call this to show the post thumbnail + caption
    before the user confirms submission.
    """
    result = fetch_post_by_url(post_url, current_user.instagram_handle or "")
    if not result["verified"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {
        "post_data": result["post_data"],
        "message": "Post fetched successfully. Review and confirm to submit."
    }


@router.get("/my-posts")
def get_my_verified_posts(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return all verified purchases with their post URLs and metadata
    for display on the influencer dashboard.
    """
    verified = db.query(models.Purchase).filter(
        models.Purchase.user_id == current_user.id,
        models.Purchase.post_verified == True
    ).order_by(models.Purchase.post_verified_at.desc()).all()

    result = []
    for p in verified:
        brand = db.query(models.Brand).filter(models.Brand.id == p.brand_id).first()
        result.append({
            "purchase_id": p.id,
            "brand_name": brand.name if brand else "Unknown",
            "brand_category": brand.category if brand else None,
            "amount": p.amount,
            "cashback_earned": p.cashback_amount,
            "post_url": p.post_url,
            "verified_at": p.post_verified_at.isoformat() if p.post_verified_at else None,
            "is_first_purchase": p.is_first_purchase,
            "voucher_issued": p.voucher_issued,
        })

    return {"posts": result, "total": len(result)}