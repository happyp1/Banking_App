from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from typing import List
from app.models.accounts import Account
from app.models.user import User
from app.schemas.account import AccountResponse
from app.utils.security import get_current_user, is_admin, is_banker_or_admin

router = APIRouter(prefix="/accounts", tags=["Accounts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Create account (Customer or Banker)
@router.post("/", response_model=AccountResponse)
def create_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if already has an account
    existing = db.query(Account).filter(Account.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account already exists")

    account = Account(user_id=current_user.id)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

# ✅ Get my account
@router.get("/me", response_model=AccountResponse)
def get_my_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# ✅ Get all accounts (Banker/Admin only)
@router.get("/", response_model=List[AccountResponse])
def get_all_accounts(db: Session = Depends(get_db), _: User = Depends(is_banker_or_admin)):
    return db.query(Account).all()

# ❌ Delete account (Admin only)
@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db), _: User = Depends(is_admin)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(acc)
    db.commit()
    return {"message": "Account deleted"}
