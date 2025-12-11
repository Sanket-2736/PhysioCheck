# schemas/auth_schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional

from pydantic import BaseModel, EmailStr
from fastapi import Form
from typing import Optional

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    age: int
    gender: str
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    address: Optional[str] = None
    injury_description: Optional[str] = None
    goals: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        full_name: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        age: int = Form(...),
        gender: str = Form(...),
        height_cm: Optional[int] = Form(None),
        weight_kg: Optional[float] = Form(None),
        address: Optional[str] = Form(None),
        injury_description: Optional[str] = Form(None),
        goals: Optional[str] = Form(None),
    ):
        return cls(
            full_name=full_name,
            email=email,
            password=password,
            age=age,
            gender=gender,
            height_cm=height_cm,
            weight_kg=weight_kg,
            address=address,
            injury_description=injury_description,
            goals=goals,
        )


class PhysicianSignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    specialization: str
    license_id: Optional[str] = None
    years_experience: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
