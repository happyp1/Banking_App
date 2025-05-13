from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class TransactionCreate(BaseModel):
    amount: float
    type: Literal['deposit', 'withdraw']

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    amount: float
    type: str
    timestamp: datetime

    class Config:
        orm_mode = True
