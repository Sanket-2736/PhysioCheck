from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.patient_exercise_schema import AssignExerciseRequest
from services.patient_exercise_service import PatientExerciseService
from routers.auth_router import require_role
from database.connection import get_db

router = APIRouter(
    prefix="/patient-exercises",
    tags=["Patient Exercises"]
)

@router.post("/{patient_exercise_id}/deassign")
async def deassign_exercise(
    patient_exercise_id: int,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await PatientExerciseService.deassign_exercise(
        physician_id=user["user_id"],
        patient_exercise_id=patient_exercise_id,
        db=db
    )

@router.post("/assign")
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
