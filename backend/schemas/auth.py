from pydantic import BaseModel, EmailStr, Field, ValidationError
from typing import Optional
from fastapi import Form
from fastapi.exceptions import RequestValidationError
from enum import Enum

# ---------- User Registration ----------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=10)
    password: str = Field(..., min_length=8)
    confirm_password: str
    initial_balance: float = Field(..., ge=0)

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        email: EmailStr = Form(...),
        phone: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        initial_balance: float = Form(...)
    ):
        try:
            return cls(
                username=username,
                email=email,
                phone=phone,
                password=password,
                confirm_password=confirm_password,
                initial_balance=initial_balance
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())


# ---------- Login ----------
class UserLogin(BaseModel):
    identifier: str
    password: str

    @classmethod
    def as_form(
        cls,
        identifier: str = Form(...),
        password: str = Form(...)
    ):
        try:
            return cls(identifier=identifier, password=password)
        except ValidationError as e:
            raise RequestValidationError(e.errors())


# ---------- Profile Update ----------

class RiskTolerance(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ProfileUpdate(BaseModel):
    monthly_income: Optional[float] = 0.0
    savings_goal: Optional[float] = 0.0
    risk_tolerance: Optional[RiskTolerance] = RiskTolerance.medium

    @classmethod
    def as_form(
        cls,
        monthly_income: float = Form(0.0),
        savings_goal: float = Form(0.0),
         risk_tolerance: RiskTolerance = Form(RiskTolerance.medium)
    ):
        try:
            return cls(
                monthly_income=monthly_income,
                savings_goal=savings_goal,
                risk_tolerance=risk_tolerance
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())



class MerchantCategory(str, Enum):
    Utilities = "Utilities"
    Groceries = "Groceries"
    Dining = "Dining"
    Entertainment = "Entertainment"
    Subscriptions = "Subscriptions"
    Mortgage = "Mortgage"
    Insurance = "Insurance"
    Commuting = "Commuting"
    Healthcare = "Healthcare"
    Shopping = "Shopping"
    Education = "Education"
    Travel = "Travel"
    Fuel = "Fuel"
    Personal_Care = "Personal_Care"
    Financial = "Financial"
    Miscellaneous = "Miscellaneous"


# ---------- VENDOR ----------
class VendorRegister(BaseModel):
    business_name: str
    email : EmailStr
    phone: str = Field(..., min_length=10, max_length=10)
    category: MerchantCategory
    password: str = Field(..., min_length=8)
    confirm_password: str
    initial_balance: Optional[float] = Field(0.0, ge=0)

    @classmethod
    def as_form(
        cls,
        business_name: str = Form(...),
        email: EmailStr = Form(...),
        phone: str = Form(...),
        category: MerchantCategory = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        initial_balance: float = Form(0.0)
    ):
        try:
            return cls(
                business_name=business_name,
                email=email,
                phone=phone,
                category=category,
                password=password,
                confirm_password=confirm_password,
                initial_balance=initial_balance
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())
        

