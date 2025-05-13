from pydantic import BaseModel

class AccountCreate(BaseModel):
    pass  # account will be created for a user; balance is default 0.0

class AccountResponse(BaseModel):
    id: int
    user_id: int
    balance: float

    class Config:
        orm_mode = True
