from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from routers.auth_router import get_current_user, require_role
from services.profile_service import ProfileService
from utils.cloudinary import upload_profile_photo
from database.connection import get_db
from database.models import User, Patient, Physician

from schemas.profile_schemas import (
    PatientProfileUpdate,
    PhysicianProfileUpdate
)

router = APIRouter(prefix="/profile", tags=["Profile"])


# -------------------------------------------
# INTERNAL FUNCTION TO FETCH FULL PROFILE
# -------------------------------------------
async def fetch_full_profile(user_id: int, role: str, db: AsyncSession):
    q = await db.execute(select(User).where(User.id == user_id))
    base_user = q.scalar_one_or_none()

    if not base_user:
        raise HTTPException(404, "User not found")

    if role == "patient":
        pq = await db.execute(select(Patient).where(Patient.user_id == user_id))
        prof = pq.scalar_one_or_none()

        return {
            "role": "patient",
            "full_name": base_user.full_name,
            "email": base_user.email,
            "profile_photo": prof.profile_photo,
            "age": prof.age,
            "gender": prof.gender,
            "height_cm": prof.height_cm,
            "weight_kg": prof.weight_kg,
            "address": prof.address,
            "injury_description": prof.injury_description,
            "goals": prof.goals,
        }

    elif role == "physician":
        pq = await db.execute(select(Physician).where(Physician.user_id == user_id))
        prof = pq.scalar_one_or_none()

        return {
            "role": "physician",
            "full_name": base_user.full_name,
            "email": base_user.email,
            "profile_photo": prof.profile_photo,
            "specialization": prof.specialization,
            "license_id": prof.license_id,
            "years_experience": prof.years_experience,
            "is_verified": prof.is_verified,
            "credential_photo": prof.credential_photo,
        }

    else:
        raise HTTPException(400, "Unknown role")


# -------------------------------------------
# UPDATE PATIENT PROFILE
# -------------------------------------------
@router.put("/patient")
async def update_patient_profile(
    body: PatientProfileUpdate = Depends(),
    profile_photo: UploadFile = File(None),
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    photo_url = None
    if profile_photo:
        photo_url = upload_profile_photo(profile_photo.file)

    return await ProfileService.update_patient(
        user_id=user["user_id"],
        payload=body.dict(exclude_unset=True),
        db=db,
        profile_photo_url=photo_url
    )


# -------------------------------------------
# UPDATE PHYSICIAN PROFILE
# -------------------------------------------
@router.put("/physician")
async def update_physician_profile(
    body: PhysicianProfileUpdate = Depends(),
    profile_photo: UploadFile = File(None),
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    photo_url = None
    if profile_photo:
        photo_url = upload_profile_photo(profile_photo.file)

    return await ProfileService.update_physician(
        user_id=user["user_id"],
        payload=body.dict(exclude_unset=True),
        db=db,
        profile_photo_url=photo_url
    )


# -------------------------------------------
# GET OWN PROFILE (AUTO ROLE DETECTION)
# -------------------------------------------
@router.get("/")
async def get_my_profile(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await fetch_full_profile(
        user_id=user["user_id"],
        role=user["role"],
        db=db
    )


# Alias: GET /profile/me
@router.get("/me")
async def get_my_profile_alias(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await fetch_full_profile(
        user_id=user["user_id"],
        role=user["role"],
        db=db
    )


# -------------------------------------------
# PUBLIC PROFILE (anyone can see)
# Limited information exposed
# -------------------------------------------
@router.get("/public/{user_id}")
async def get_public_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(User).where(User.id == user_id))
    base_user = q.scalar_one_or_none()

    if not base_user:
        raise HTTPException(404, "User not found")

    if base_user.role.name == "physician":
        pq = await db.execute(select(Physician).where(Physician.user_id == user_id))
        prof = pq.scalar_one_or_none()

        return {
            "user_id": user_id,
            "full_name": base_user.full_name,
            "specialization": prof.specialization,
            "years_experience": prof.years_experience,
            "profile_photo": prof.profile_photo,
            "is_verified": prof.is_verified,
        }

    # Patients should not be publicly listed
    return {"message": "Public profile not available for this user"}


# -------------------------------------------
# ADMIN VIEW SPECIFIC PHYSICIAN PROFILE
# -------------------------------------------
@router.get("/physician/{user_id}")
async def admin_view_physician_profile(
    user_id: int,
    user=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(select(User).where(User.id == user_id))
    base_user = q.scalar_one_or_none()

    if not base_user or base_user.role.name != "physician":
        raise HTTPException(404, "Physician not found")

    pq = await db.execute(select(Physician).where(Physician.user_id == user_id))
    prof = pq.scalar_one_or_none()

    return {
        "user_id": user_id,
        "full_name": base_user.full_name,
        "email": base_user.email,
        "specialization": prof.specialization,
        "license_id": prof.license_id,
        "years_experience": prof.years_experience,
        "credential_photo": prof.credential_photo,
        "profile_photo": prof.profile_photo,
        "is_verified": prof.is_verified
    }

# -------------------------------------------
# GET ALL PHYSICIANS (PUBLIC LIST)
# -------------------------------------------
from typing import Optional
from sqlalchemy.orm import selectinload
from fastapi import Query

# -------------------------------------------
# GET ALL PHYSICIANS WITH FILTERS
# -------------------------------------------
@router.get("/physicians")
async def get_all_physicians(
    verified: Optional[bool] = Query(None),
    specialization: Optional[str] = Query(None),
    experience_gte: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):

    query = (
        select(Physician)
        .options(selectinload(Physician.user))
    )

    # Apply filters dynamically
    if verified is not None:
        query = query.where(Physician.is_verified == verified)

    if specialization:
        query = query.where(Physician.specialization.ilike(f"%{specialization}%"))

    if experience_gte is not None:
        query = query.where(Physician.years_experience >= experience_gte)

    result = await db.execute(query)
    physicians = result.scalars().all()

    return {
        "success": True,
        "count": len(physicians),
        "physicians": [
            {
                "user_id": p.user_id,
                "full_name": p.user.full_name,
                "email": p.user.email,
                "specialization": p.specialization,
                "years_experience": p.years_experience,
                "profile_photo": p.profile_photo,
                "credential_photo": p.credential_photo,
                "is_verified": p.is_verified
            }
            for p in physicians
        ]
    }
