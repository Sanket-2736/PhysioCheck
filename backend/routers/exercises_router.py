from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from routers.auth_router import require_role

from schemas.exercise_schemas import CreateExerciseRequest
from services.exercises_service import ExerciseService
from services.rep_capture_service import RepCaptureService
from services.rep_capture_service import RepCaptureService
from schemas.rep_capture_schema import RepCaptureRequest

router = APIRouter(prefix="/exercises", tags=["Exercises"])


# --------------------------------------------------
# 1️⃣ CREATE EXERCISE (METADATA ONLY)
# --------------------------------------------------
@router.post("")
async def create_exercise(
    body: CreateExerciseRequest,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    exercise = await ExerciseService.create_exercise(
        payload=body,
        physician_id=user["user_id"],
        db=db
    )

    return {
        "success": True,
        "exercise": {
            "id": exercise.id,
            "name": exercise.name,
            "category": exercise.category,
            "difficulty": exercise.difficulty.value,
            "target_body_parts": exercise.target_body_parts
        }
    }


# --------------------------------------------------
# 2️⃣ CAPTURE DEMO REP (THE ONLY CAPTURE API)
# --------------------------------------------------
@router.post("/{exercise_id}/capture-rep")
async def capture_rep(
    exercise_id: int,
    body: RepCaptureRequest,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await RepCaptureService.capture_and_generate(
        exercise_id=exercise_id,
        frames=[f.dict() for f in body.frames],
        db=db
    )

# --------------------------------------------------
# 3️⃣ LIST EXERCISES (READ-ONLY)
# --------------------------------------------------
@router.get("")
async def list_exercises(db: AsyncSession = Depends(get_db)):
    exercises = await ExerciseService.list_exercises(db)
    return {
        "success": True,
        "exercises": exercises
    }
