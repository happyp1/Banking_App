from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.models.transaction import Transaction
from app.models.accounts import Account
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.utils.security import get_current_user, is_banker_or_admin

router = APIRouter(prefix="/transactions", tags=["Transactions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Deposit / Withdraw
@router.post("/", response_model=TransactionResponse)
def create_transaction(request: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if request.type == "withdraw":
        if account.balance < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        account.balance -= request.amount
    elif request.type == "deposit":
        account.balance += request.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    txn = Transaction(account_id=account.id, amount=request.amount, type=request.type)
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn

# ✅ View my transactions
@router.get("/me", response_model=List[TransactionResponse])
def get_my_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return db.query(Transaction).filter(Transaction.account_id == account.id).all()

# ✅ View all transactions (Banker/Admin only)
@router.get("/", response_model=List[TransactionResponse])
def get_all_transactions(db: Session = Depends(get_db), _: User = Depends(is_banker_or_admin)):
    return db.query(Transaction).all()


from fastapi import Body

@router.post("/transfer")
def transfer_funds(
    recipient_username: str = Body(...),
    amount: float = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    sender_account = db.query(Account).filter(Account.user_id == current_user.id).first()
    if not sender_account or sender_account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance or account")

    recipient_user = db.query(User).filter(User.username == recipient_username).first()
    if not recipient_user:
        raise HTTPException(status_code=404, detail="Recipient not found")

    recipient_account = db.query(Account).filter(Account.user_id == recipient_user.id).first()
    if not recipient_account:
        raise HTTPException(status_code=404, detail="Recipient has no account")

    # Perform transfer
    sender_account.balance -= amount
    recipient_account.balance += amount

    # Log both transactions
    txn_out = Transaction(account_id=sender_account.id, amount=amount, type="withdraw")
    txn_in = Transaction(account_id=recipient_account.id, amount=amount, type="deposit")
    db.add_all([txn_out, txn_in])
    db.commit()

    # Log audit
    log = AuditLog(
        user_id=current_user.id,
        action=f"Transferred {amount} to {recipient_username}"
    )
    db.add(log)
    db.commit()

    return {"message": f"Transferred ₹{amount} to {recipient_username}"}
