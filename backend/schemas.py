from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=2, max_length=80)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=8)

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # (Pydantic v2)

class ExpenseBase(BaseModel):
    category: str = Field(min_length=2, max_length=50)
    amount: float = Field(gt=0, description="Must be a positive number")
    date: Optional[datetime] = None
    
class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    category: Optional[str] = Field(default=None, min_length=2, max_length=50)
    amount: Optional[float] = Field(default=None, gt=0)
    date: Optional[datetime] = None

class ExpenseOut(BaseModel):
    id: int
    user_id: int
    category: str
    amount: float
    date: datetime
    class Config:
        from_attributes = True

class FinancialGoalBase(BaseModel):
    target_savings: float = Field(gt=0, description="Target amount to save (positive)")
    start_date: datetime
    end_date: datetime

class FinancialGoalCreate(FinancialGoalBase):
    pass

class FinancialGoalUpdate(BaseModel):
    target_savings: Optional[float] = Field(default=None, gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class FinancialGoalOut(BaseModel):
    id: int
    user_id: int
    target_savings: float
    start_date: datetime
    end_date: datetime

    class Config:
        from_attributes = True

class FinancialGoalCreateViaPeriod(BaseModel):
    target_amount: float = Field(gt=0, description="Target amount to save (positive)")
    period: int = Field(gt=0, description="Goal period in days")
    start_date: Optional[datetime] = None

from datetime import date

class BadgeBase(BaseModel):
    badge_name: str = Field(min_length=2, max_length=100, description="Name of the badge")
    date_awarded: Optional[date] = Field(default_factory=date.today, description="Date when badge was earned")

class BadgeCreate(BadgeBase):
    user_id: int = Field(gt=0, description="User ID who earned the badge")

class BadgeOut(BaseModel):
    id: int
    user_id: int
    badge_name: str
    date_awarded: date

    class Config:
        from_attributes = True