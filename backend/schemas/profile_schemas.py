from pydantic import BaseModel
from typing import Optional


class PatientProfileUpdate(BaseModel):
    full_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    height_cm: Optional[int]
    weight_kg: Optional[float]
    address: Optional[str]
    injury_description: Optional[str]
    goals: Optional[str]


class PhysicianProfileUpdate(BaseModel):
    full_name: Optional[str]
    specialization: Optional[str]
    license_id: Optional[str]
    years_experience: Optional[int]
    bio: Optional[str]
