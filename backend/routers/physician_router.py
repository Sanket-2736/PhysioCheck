from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import get_db
from database.models import Patient, PatientExercise, RehabPlan, Exercise
from routers.auth_router import require_role
from schemas.profile_schemas import PhysicianProfileUpdate

router = APIRouter(prefix="/physician", tags=["Physician"])

@router.get("/patients")
async def get_my_patients(
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Patient)
        .options(selectinload(Patient.user))
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
                "age": p.age,
                "gender": p.gender,
                "profile_photo": p.profile_photo,  # ✅ needed by UI
            }
            for p in patients
        ]
    }

@router.get("/patients/{patient_id}")
async def get_patient_detail(
    patient_id: int,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Patient)
        .options(selectinload(Patient.user))
        .where(
            Patient.user_id == patient_id,
            Patient.physician_id == user["user_id"]
        )
    )
    patient = q.scalar_one_or_none()

    if not patient:
        raise HTTPException(404, "Patient not found")

    return {
        "success": True,
        "patient": {
            # 🔹 USER INFO
            "user_id": patient.user.id,
            "full_name": patient.user.full_name,
            "email": patient.user.email,
            "phone": patient.user.phone,
            "created_at": patient.user.created_at,

            # 🔹 PATIENT INFO
            "profile_photo": patient.profile_photo,
            "age": patient.age,
            "gender": patient.gender,
            "height_cm": patient.height_cm,
            "weight_kg": patient.weight_kg,
            "injury_description": patient.injury_description,
            "goals": patient.goals,
        }
    }

@router.post("/patients/{patient_id}/rehab-plans")
async def create_rehab_plan(
    patient_id: int,
    notes: str | None = None,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    patient = await db.get(Patient, patient_id)

    if not patient or patient.physician_id != user["user_id"]:
        raise HTTPException(403, "Unauthorized patient")

    plan = RehabPlan(
        patient_id=patient_id,
        physician_id=user["user_id"],
        notes=notes
    )

    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    return {
        "success": True,
        "rehab_plan_id": plan.id
    }

from schemas.rep_capture_schema import AssignExerciseRequest

@router.post("/rehab-plans/{plan_id}/assign-exercise")
async def assign_exercise(
    plan_id: int,
    payload: AssignExerciseRequest,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    plan = await db.get(RehabPlan, plan_id)

    if not plan or plan.physician_id != user["user_id"]:
        raise HTTPException(403, "Unauthorized plan")

    assignment = PatientExercise(
        patient_id=plan.patient_id,
        physician_id=user["user_id"],
        exercise_id=payload.exercise_id,
        sets=payload.sets,
        reps=payload.reps,
        frequency_per_day=payload.frequency_per_day
    )

    db.add(assignment)
    await db.commit()

    return {"success": True}

@router.get("/")
async def list_physicians(
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Physician)
        .options(selectinload(Physician.user))
    )

    physicians = q.scalars().all()

    print("Fetched physicians:", physicians)

    return {
        "success": True,
        "physicians": [
            {
                "physician_id": p.user_id,
                "full_name": p.user.full_name,
                "email": p.user.email,
                "profile_photo": p.profile_photo,
                "specialization": p.specialization,
                "years_experience": p.years_experience,
            }
            for p in physicians
        ]
    }

@router.put("/rehab-plans/{plan_id}")
async def update_rehab_plan(
    plan_id: int,
    target_reps: int | None = None,
    frequency_per_week: int | None = None,
    is_active: bool | None = None,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    plan = await db.get(RehabPlan, plan_id)

    if not plan or plan.physician_id != user["user_id"]:
        raise HTTPException(404, "Rehab plan not found")

    if target_reps is not None:
        plan.target_reps = target_reps
    if frequency_per_week is not None:
        plan.frequency_per_week = frequency_per_week
    if is_active is not None:
        plan.is_active = is_active

    await db.commit()
    return {"success": True, "message": "Rehab plan updated"}

from database.models import Physician, User
from sqlalchemy.orm import selectinload

@router.get("/me")
async def get_my_profile(
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Physician)
        .options(selectinload(Physician.user))
        .where(Physician.user_id == user["user_id"])
    )

    physician = q.scalar_one_or_none()

    if not physician:
        raise HTTPException(404, "Physician not found")

    return {
        "success": True,
        "physician": {
            "user_id": physician.user_id,
            "full_name": physician.user.full_name,
            "email": physician.user.email,
            "phone": physician.user.phone,
            "specialization": physician.specialization,
            "license_id": physician.license_id,
            "years_experience": physician.years_experience,
            "is_verified": physician.is_verified,
            "profile_photo": physician.profile_photo,
            "credential_photo": physician.credential_photo,
        }
    }
from utils.cloudinary import upload_profile_photo
from fastapi import UploadFile, File

@router.put("/me/profile-photo")
async def upload_physician_profile_photo(
    file: UploadFile = File(...),
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Physician)
        .where(Physician.user_id == user["user_id"])
    )
    physician = q.scalar_one_or_none()

    if not physician:
        raise HTTPException(404, "Physician not found")

    # Upload to Cloudinary
    photo_url = upload_profile_photo(file.file)

    physician.profile_photo = photo_url
    await db.commit()

    return {
        "success": True,
        "profile_photo": photo_url
    }

@router.put("/me/credential-photo")
async def upload_physician_credential_photo(
    file: UploadFile = File(...),
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Physician)
        .where(Physician.user_id == user["user_id"])
    )
    physician = q.scalar_one_or_none()

    if not physician:
        raise HTTPException(404, "Physician not found")

    credential_url = upload_profile_photo(file.file)

    physician.credential_photo = credential_url
    await db.commit()

    return {
        "success": True,
        "credential_photo": credential_url
    }

@router.put("/me")
async def update_my_profile(
    payload: PhysicianProfileUpdate,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    print("Payload received for update:", payload)
    q = await db.execute(
        select(Physician)
        .options(selectinload(Physician.user))
        .where(Physician.user_id == user["user_id"])
    )
    physician = q.scalar_one_or_none()
    print("Physician fetched from DB:", physician)

    if not physician:
        raise HTTPException(404, "Physician not found")

    # 🔥 THIS LINE FIXES EVERYTHING
    data = payload.dict(exclude_unset=True, exclude_none=True)
    print("Data to be updated:", data)

    if "full_name" in data:
        physician.user.full_name = data["full_name"]
    if "phone" in data:
        physician.user.phone = data["phone"]

    for field in [
        "specialization",
        "license_id",
        "years_experience",
        "profile_photo",
        "credential_photo",
    ]:
        if field in data:
            print(f"Updating {field} to {data[field]}")
            setattr(physician, field, data[field])

    await db.commit()

    return {"success": True}
