from fastapi import APIRouter, Depends, UploadFile, File, Body
from sqlalchemy.ext.asyncio import AsyncSession

from routers.auth_router import require_role
from services.profile_service import ProfileService
from utils.cloudinary import upload_profile_photo
from database.connection import get_db

from schemas.profile_schemas import (
    PatientProfileUpdate,
    PhysicianProfileUpdate
)

router = APIRouter(prefix="/profile", tags=["Profile"])


# ---------------------------
# UPDATE PATIENT PROFILE
# ---------------------------
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


# ---------------------------
# UPDATE PHYSICIAN PROFILE
# ---------------------------
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
