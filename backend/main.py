from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
import models
import schemas
import auth
import webhook
from database import engine, get_db

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="InstaAI SaaS API")
app.include_router(webhook.router, prefix="/api")
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Endpoints
@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    print("PASSWORD =", user.password)
    print("LENGTH =", len(user.password))
    hashed_pass = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not db_user or not auth.verify_password(
        form_data.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = auth.create_access_token(
        data={"sub": db_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@app.get("/api/user/me")
def get_me(
    current_user: models.User = Depends(auth.get_current_user)
):
    return {
    "name": current_user.email,
    "botStatus": current_user.bot_status,
    "instagramPageId": current_user.instagram_page_id,
    "instagramAccessToken": current_user.instagram_access_token,
    "businessDescription": current_user.business_description,
    "aiInstructions": current_user.ai_instructions
}
# User & Bot Settings
@app.get("/api/user/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.patch("/api/user/settings", response_model=schemas.UserResponse)
def update_settings(
    settings: schemas.BotSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    update_data = settings.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

# Product Management
@app.get("/api/products", response_model=List[schemas.ProductResponse])
def read_products(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Product).filter(models.Product.user_id == current_user.id).all()

@app.post("/api/products", response_model=schemas.ProductResponse)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_product = models.Product(**product.dict(), user_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/api/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id, 
        models.Product.user_id == current_user.id
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}

# FAQ Management
@app.get("/api/faqs", response_model=List[schemas.FAQResponse])
def read_faqs(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.FAQ).filter(models.FAQ.user_id == current_user.id).all()

@app.post("/api/faqs", response_model=schemas.FAQResponse)
def create_faq(
    faq: schemas.FAQCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_faq = models.FAQ(**faq.dict(), user_id=current_user.id)
    db.add(db_faq)
    db.commit()
    db.refresh(db_faq)
    return db_faq

# Orders View
@app.get("/api/orders", response_model=List[schemas.OrderResponse])
def read_orders(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()

# Webhook Router (to be defined in webhook.py)
from webhook import router as webhook_router
app.include_router(webhook_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
