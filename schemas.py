from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CampaignTier(str, Enum):
    coronet = "coronet"
    regalia = "regalia"
    sovereign = "sovereign"

class PurchaseStatus(str, Enum):
    pending = "pending"
    post_required = "post_required"
    post_submitted = "post_submitted"
    verified = "verified"
    cashback_credited = "cashback_credited"
    rejected = "rejected"

# ===== AUTH =====
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    instagram_handle: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ===== USER =====
class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    instagram_handle: Optional[str]
    follower_count: int
    engagement_rate: float
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SignupOut(BaseModel):
    user: UserOut
    access_token: str
    token_type: str

# ===== WALLET =====
class WalletOut(BaseModel):
    id: str
    user_id: str
    balance: float
    total_cashback_earned: float
    created_at: datetime

    class Config:
        from_attributes = True

class WalletLoad(BaseModel):
    amount: float

class RazorpayOrderOut(BaseModel):
    order_id: str
    amount: int
    currency: str
    key_id: str

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class TransactionOut(BaseModel):
    id: str
    amount: float
    type: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# ===== BRAND =====
class BrandOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    logo_url: Optional[str]
    category: Optional[str]
    campaign_tier: CampaignTier
    cashback_percentage: float
    max_cashback_cap: float
    max_redemptions_per_user: int
    min_crownd_score: int
    is_active: bool

    class Config:
        from_attributes = True

class BrandCreate(BaseModel):
    name: str
    description: Optional[str]
    logo_url: Optional[str]
    category: Optional[str]
    campaign_tier: CampaignTier
    cashback_percentage: float
    max_cashback_cap: float
    max_redemptions_per_user: int
    monthly_budget: float
    min_crownd_score: int = 0

# ===== PURCHASE =====
class PurchaseCreate(BaseModel):
    brand_id: str
    amount: float

class PurchaseOut(BaseModel):
    id: str
    brand_id: str
    amount: float
    cashback_amount: float
    status: PurchaseStatus
    post_url: Optional[str]
    post_verified: bool
    is_first_purchase: bool
    voucher_issued: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ===== POST VERIFICATION =====
class PostSubmit(BaseModel):
    purchase_id: str
    post_url: str

class PostVerifyOut(BaseModel):
    verified: bool
    message: str
    cashback_amount: Optional[float]

# ===== CROWND SCORE =====
class CrowndScoreOut(BaseModel):
    total_score: int
    total_posts: int
    verified_posts: int
    avg_engagement_rate: float
    brand_diversity_score: int
    unique_brands_posted: int

    class Config:
        from_attributes = True