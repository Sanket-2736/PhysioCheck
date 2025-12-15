from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from services.physician_analytics_service import PhysicianAnalyticsService
from database.connection import get_db
from routers.auth_router import require_role
from database.models import Patient

router = APIRouter(prefix="/physician", tags=["Physician"])

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from routers.auth_router import require_role
from database.connection import get_db
from schemas.patient_exercise_schema import AssignExerciseRequest
from services.patient_exercise_service import PatientExerciseService

router = APIRouter(prefix="/physician", tags=["Physician"])

@router.post("/assign-exercise")
async def assign_exercise(
    body: AssignExerciseRequest,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await PatientExerciseService.assign_exercise(
        physician_id=user["user_id"],
        payload=body,
        db=db
    )

@router.get("/patients")
async def get_my_patients(
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Patient).where(Patient.physician_id == user["user_id"])
    )
    patients = q.scalars().all()

    return {
        "success": True,
        "patients": [
            {
                "patient_id": p.user_id
            }
            for p in patients
        ]
    }

@router.get("/patient-analytics")
async def get_patient_analytics(
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await PhysicianAnalyticsService.get_patient_analytics(
        physician_id=user["user_id"],
        db=db
    )
