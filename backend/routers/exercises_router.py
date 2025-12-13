from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.exercise_schemas import CreateExerciseRequest
from services.exercises_service import ExerciseService
from routers.auth_router import require_role
from database.connection import get_db
from services.pose_capture_service import PoseCaptureService

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.post("/")
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

@router.post("/{exercise_id}/capture-keypoints")
async def capture_keypoints(
    exercise_id: int,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await PoseCaptureService.capture_reference_pose(
        exercise_id=exercise_id,
        db=db
    )

from schemas.pose_template_schema import CapturePoseRequest
from services.pose_template_service import PoseTemplateService


@router.post("/{exercise_id}/capture-pose")
async def capture_pose_template(
    exercise_id: int,
    body: CapturePoseRequest,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await PoseTemplateService.capture_pose_template(
        exercise_id=exercise_id,
        pose_type=body.pose_type,
        db=db
    )

from services.exercise_rule_service import ExerciseRuleService


@router.post("/{exercise_id}/generate-angle-ranges")
async def generate_angle_ranges(
    exercise_id: int,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await ExerciseRuleService.generate_angle_ranges(
        exercise_id=exercise_id,
        db=db
    )

@router.post("/{exercise_id}/generate-timing-stability")
async def generate_timing_and_stability(
    exercise_id: int,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await ExerciseRuleService.generate_timing_and_stability_rules(
        exercise_id=exercise_id,
        db=db
    )

@router.post("/{exercise_id}/generate-alignment-rules")
async def generate_alignment_rules(
    exercise_id: int,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    return await ExerciseRuleService.generate_alignment_rules(
        exercise_id=exercise_id,
        db=db
    )
