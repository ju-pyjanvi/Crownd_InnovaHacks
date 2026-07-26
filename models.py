from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid
import enum

def generate_uuid():
    return str(uuid.uuid4())

class CampaignTier(str, enum.Enum):
    coronet = "coronet"
    regalia = "regalia"
    sovereign = "sovereign"

class PurchaseStatus(str, enum.Enum):
    pending = "pending"
    post_required = "post_required"
    post_submitted = "post_submitted"
    verified = "verified"
    cashback_credited = "cashback_credited"
    rejected = "rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    instagram_handle = Column(String, unique=True, nullable=True)
    follower_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    instagram_access_token = Column(String, nullable=True)
    instagram_user_id = Column(String, nullable=True)
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    purchases = relationship("Purchase", back_populates="user")

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    total_cashback_earned = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="wallet")
    transactions = relationship("Transaction", back_populates="wallet")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    wallet_id = Column(String, ForeignKey("wallets.id"), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # "credit" or "debit"
    description = Column(String, nullable=True)
    razorpay_order_id = Column(String, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    wallet = relationship("Wallet", back_populates="transactions")

class Brand(Base):
    __tablename__ = "brands"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    campaign_tier = Column(Enum(CampaignTier), nullable=False)
    cashback_percentage = Column(Float, default=10.0)
    max_cashback_cap = Column(Float, default=2000.0)
    max_redemptions_per_user = Column(Integer, default=2)
    monthly_budget = Column(Float, default=100000.0)
    budget_used = Column(Float, default=0.0)
    min_crownd_score = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    purchases = relationship("Purchase", back_populates="brand")

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    brand_id = Column(String, ForeignKey("brands.id"), nullable=False)
    amount = Column(Float, nullable=False)
    cashback_amount = Column(Float, default=0.0)
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.pending)
    post_url = Column(String, nullable=True)
    post_verified = Column(Boolean, default=False)
    post_submitted_at = Column(DateTime, nullable=True)
    post_verified_at = Column(DateTime, nullable=True)
    cashback_credited_at = Column(DateTime, nullable=True)
    is_first_purchase = Column(Boolean, default=False)
    voucher_issued = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="purchases")
    brand = relationship("Brand", back_populates="purchases")

class CrowndScore(Base):
    __tablename__ = "crownd_scores"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    total_score = Column(Integer, default=0)
    total_posts = Column(Integer, default=0)
    verified_posts = Column(Integer, default=0)
    avg_engagement_rate = Column(Float, default=0.0)
    brand_diversity_score = Column(Integer, default=0)
    unique_brands_posted = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)