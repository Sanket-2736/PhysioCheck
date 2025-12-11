# routers/exercises_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from services.exercises_service import ExerciseService
from routers.auth_router import get_current_user, require_role

router = APIRouter(prefix="/exercises", tags=["Exercises"])


# --------------------------
# CREATE NEW EXERCISE
# --------------------------
@router.post("/")
async def create_exercise(body: dict, 
                          db: AsyncSession = Depends(get_db),
                          user=Depends(require_role("physician"))):
    return await ExerciseService.create_exercise(
        physician_id=user["user_id"],
        payload=body,
        db=db
    )


# --------------------------
# SAVE PRESET JSON
# --------------------------
@router.post("/{exercise_id}/preset")
async def save_preset(exercise_id: int, 
                      body: dict,
                      db: AsyncSession = Depends(get_db),
                      user=Depends(require_role("physician"))):
    return await ExerciseService.save_preset(exercise_id, body, db)


# --------------------------
# SAVE CAPTURE (POSE TEMPLATE)
# --------------------------
@router.post("/{exercise_id}/capture")
async def save_capture(exercise_id: int,
                       body: dict,
                       db: AsyncSession = Depends(get_db),
                       user=Depends(require_role("physician"))):
    return await ExerciseService.save_capture(
        exercise_id,
        pose_type=body["pose_type"],
        joints=body["joints"],
        reference_angles=body["reference_angles"],
        db=db
    )


# --------------------------
# SAVE RULES
# --------------------------
@router.post("/{exercise_id}/rules")
async def save_rules(exercise_id: int,
                     body: dict,
                     db: AsyncSession = Depends(get_db),
                     user=Depends(require_role("physician"))):
    return await ExerciseService.save_rules(exercise_id, body, db)


# --------------------------
# SAVE LOGIC
# --------------------------
@router.post("/{exercise_id}/logic")
async def save_logic(exercise_id: int,
                     body: dict,
                     db: AsyncSession = Depends(get_db),
                     user=Depends(require_role("physician"))):
    return await ExerciseService.save_logic(exercise_id, body, db)


# --------------------------
# GET FULL EXERCISE DEFINITION
# --------------------------
@router.get("/{exercise_id}")
async def get_exercise_definition(exercise_id: int, db: AsyncSession = Depends(get_db)):
    return await ExerciseService.get_exercise_definition(exercise_id, db)
