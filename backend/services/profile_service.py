from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from database.models import User, Patient, Physician


class ProfileService:

    # -----------------------------------
    # UPDATE PATIENT PROFILE
    # -----------------------------------
    @staticmethod
    async def update_patient(user_id: int, payload: dict, db: AsyncSession, profile_photo_url=None):
        # Fetch user
        q = await db.execute(select(User).where(User.id == user_id))
        user = q.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "User not found")

        # Fetch patient profile
        p_q = await db.execute(select(Patient).where(Patient.user_id == user_id))
        patient = p_q.scalar_one_or_none()
        if not patient:
            raise HTTPException(404, "Patient profile not found")

        # Update User
        user.full_name = payload.get("full_name", user.full_name)

        # Update Patient model fields
        for field in ["age", "gender", "height_cm", "weight_kg", "address", "injury_description", "goals"]:
            if field in payload:
                setattr(patient, field, payload[field])

        if profile_photo_url:
            patient.profile_photo = profile_photo_url

        await db.commit()
        return {"success": True, "message": "Patient profile updated"}


    # -----------------------------------
    # UPDATE PHYSICIAN PROFILE
    # -----------------------------------
    @staticmethod
    async def update_physician(user_id: int, payload: dict, db: AsyncSession, profile_photo_url=None):

        # Fetch User
        q = await db.execute(select(User).where(User.id == user_id))
        user = q.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "User not found")

        # Fetch Physician
        ph_q = await db.execute(select(Physician).where(Physician.user_id == user_id))
        physician = ph_q.scalar_one_or_none()
        if not physician:
            raise HTTPException(404, "Physician profile not found")

        # Update User fields
        user.full_name = payload.get("full_name", user.full_name)

        # Update Physician fields
        for field in ["specialization", "license_id", "years_experience"]:
            if field in payload:
                setattr(physician, field, payload[field])

        if profile_photo_url:
            physician.profile_photo = profile_photo_url

        await db.commit()
        return {"success": True, "message": "Physician profile updated"}
