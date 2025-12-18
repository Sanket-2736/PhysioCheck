from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from routers.auth_router import require_role
from database.connection import get_db
from database.models import Patient

router = APIRouter(prefix="/subscription", tags=["Subscription"])


# -------------------------------------------------
# PATIENT → SUBSCRIBE TO PHYSICIAN
# -------------------------------------------------
@router.post("/subscribe/{physician_id}")
async def subscribe(
    physician_id: int,
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Patient).where(Patient.user_id == user["user_id"])
    )
    patient = q.scalar_one_or_none()

    if not patient:
        raise HTTPException(404, "Patient not found")

    patient.physician_id = physician_id
    await db.commit()

    return {
        "success": True,
        "message": "Subscribed to physician successfully"
    }


# -------------------------------------------------
# PATIENT → UNSUBSCRIBE FROM PHYSICIAN
# -------------------------------------------------
@router.post("/unsubscribe")
async def unsubscribe(
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Patient).where(Patient.user_id == user["user_id"])
    )
    patient = q.scalar_one_or_none()

    if not patient:
        raise HTTPException(404, "Patient not found")

    patient.physician_id = None
    await db.commit()

    return {
        "success": True,
        "message": "Unsubscribed successfully"
    }


# -------------------------------------------------
# PHYSICIAN → GET ALL PATIENTS
# -------------------------------------------------
@router.get("/patients")
async def get_my_patients(
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db),
):
    q = await db.execute(
        select(Patient)
        .options(selectinload(Patient.user))  # ✅ IMPORTANT
        .where(Patient.physician_id == user["user_id"])
    )

    patients = q.scalars().all()

    return {
        "success": True,
        "patients": [
            {
                "patient_id": p.user_id,
                "full_name": p.user.full_name,
                "email": p.user.email,
                "profile_photo": p.profile_photo,
                "age": p.age,
                "gender": p.gender,
            }
            for p in patients
        ],
    }
