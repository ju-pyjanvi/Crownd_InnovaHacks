from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, auth
import os
import requests

router = APIRouter()

IG_APP_ID     = os.getenv("IG_APP_ID")
IG_APP_SECRET = os.getenv("IG_APP_SECRET")
REDIRECT_URI  = os.getenv("IG_REDIRECT_URI", "http://127.0.0.1:5500/auth_callback.html")

@router.post("/instagram/callback")
def instagram_callback(
    code: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Step 1: Exchange code for short-lived token
    token_res = requests.post(
        "https://api.instagram.com/oauth/access_token",
        data={
            "client_id":     IG_APP_ID,
            "client_secret": IG_APP_SECRET,
            "grant_type":    "authorization_code",
            "redirect_uri":  REDIRECT_URI,
            "code":          code,
        }
    )
    token_data = token_res.json()

    if "error_type" in token_data or "access_token" not in token_data:
        raise HTTPException(
            status_code=400,
            detail=f"Instagram token exchange failed: {token_data.get('error_message', 'Unknown error')}"
        )

    short_token = token_data["access_token"]
    ig_user_id  = token_data["user_id"]

    # Step 2: Exchange for long-lived token (60 days)
    long_res = requests.get(
        "https://graph.instagram.com/access_token",
        params={
            "grant_type":        "ig_exchange_token",
            "client_secret":     IG_APP_SECRET,
            "access_token":      short_token,
        }
    )
    long_data = long_res.json()
    long_token = long_data.get("access_token", short_token)

    # Step 3: Fetch their Instagram username
    profile_res = requests.get(
        f"https://graph.instagram.com/v18.0/me",
        params={
            "fields":       "id,username",
            "access_token": long_token,
        }
    )
    profile = profile_res.json()
    ig_username = profile.get("username", "")

    # Step 4: Store token + username on the user record
    current_user.instagram_access_token = long_token
    current_user.instagram_user_id      = str(ig_user_id)
    if ig_username:
        current_user.instagram_handle = ig_username

    db.commit()

    return {
        "message":           "Instagram connected successfully",
        "instagram_username": ig_username,
        "instagram_user_id":  str(ig_user_id),
    }
