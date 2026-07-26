from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
import models
from routers import influencer, brand, wallet, purchase, post
from dotenv import load_dotenv
from routers import instagram_oauth

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Crownd API",
    description="Where every purchase is your crowning moment",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(influencer.router, prefix="/auth", tags=["Auth & Influencer"])
app.include_router(brand.router, prefix="/brands", tags=["Brands"])
app.include_router(wallet.router, prefix="/wallet", tags=["Wallet"])
app.include_router(purchase.router, prefix="/purchase", tags=["Purchase"])
app.include_router(post.router, prefix="/post", tags=["Post Verification"])
app.include_router(instagram_oauth.router, prefix="/auth", tags=["Instagram OAuth"])

@app.get("/api")
def root():
    return {
        "message": "Crownd API is live \U0001F451",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")