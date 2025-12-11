# routers/rehab_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.rehab_service import RehabService
from database.connection import get_db
from routers.auth_router import require_role, get_current_user

router = APIRouter(prefix="/rehab", tags=["Rehab Plans"])


@router.post("/patients/{patient_id}/plans")
async def create_plan(patient_id: int,
                      body: dict,
                      db: AsyncSession = Depends(get_db),
                      user=Depends(require_role("physician"))):
    return await RehabService.create_plan(
        patient_id=patient_id,
        physician_id=user["user_id"],
        notes=body.get("notes", ""),
        db=db
    )


@router.post("/plans/{plan_id}/exercises")
async def assign_exercise(plan_id: int,
                          body: dict,
                          db: AsyncSession = Depends(get_db),
                          user=Depends(require_role("physician"))):
    return await RehabService.assign_exercise(
        plan_id=plan_id,
        exercise_id=body["exercise_id"],
        target_reps=body.get("target_reps", 5),
        target_sets=body.get("target_sets", 1),
        max_duration=body.get("max_duration", 30),
        custom_rules=body.get("custom_rules", {}),
        db=db
    )
