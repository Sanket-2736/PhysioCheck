from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.rehab_service import RehabService
from database.connection import get_db
from routers.auth_router import require_role

router = APIRouter(prefix="/rehab", tags=["Rehab Plans"])


# --------------------------------------------------
# CREATE REHAB PLAN
# --------------------------------------------------
@router.post("/patients/{patient_id}/plans")
async def create_plan(
    patient_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("physician"))
):
    return await RehabService.create_plan(
        patient_id=patient_id,
        physician_id=user["user_id"],
        notes=body.get("notes", ""),
        db=db
    )


# --------------------------------------------------
# GET CURRENT ACTIVE PLAN
# --------------------------------------------------
@router.get("/patients/{patient_id}/plans/current")
async def get_current_plan(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("physician"))
):
    return await RehabService.get_current_plan(
        patient_id=patient_id,
        physician_id=user["user_id"],
        db=db
    )


# --------------------------------------------------
# LIST EXERCISES IN PLAN
# --------------------------------------------------
@router.get("/plans/{plan_id}/exercises")
async def list_plan_exercises(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("physician"))
):
    return await RehabService.list_plan_exercises(
        plan_id=plan_id,
        physician_id=user["user_id"],
        db=db
    )


# --------------------------------------------------
# DEASSIGN (REMOVE) EXERCISE FROM PLAN
# --------------------------------------------------
@router.post("/plans/{plan_id}/exercises/{plan_exercise_id}/remove")
async def deassign_exercise(
    plan_id: int,
    plan_exercise_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("physician"))
):
    return await RehabService.deassign_exercise(
        plan_id=plan_id,
        plan_exercise_id=plan_exercise_id,
        physician_id=user["user_id"],
        db=db
    )


# --------------------------------------------------
# ASSIGN EXERCISE TO PLAN
# --------------------------------------------------
@router.post("/plans/{plan_id}/exercises")
async def assign_exercise(
    plan_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("physician"))
):
    return await RehabService.assign_exercise(
        plan_id=plan_id,
        exercise_id=body["exercise_id"],
        target_reps=body.get("target_reps", 5),
        target_sets=body.get("target_sets", 1),
        max_duration=body.get("max_duration", 30),
        custom_rules=body.get("custom_rules", {}),
        physician_id=user["user_id"],
        db=db
    )
