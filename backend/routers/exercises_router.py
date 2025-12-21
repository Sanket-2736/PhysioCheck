from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import DifficultyLevel, Exercise
from routers.auth_router import require_role

from schemas.exercise_schemas import CreateExerciseRequest
from schemas.rep_capture_schema import RepCaptureRequest

from services.exercises_service import ExerciseService
from services.rep_capture_service import RepCaptureService

# 👉 NEW IMPORTS
from pose.pose_tracking_patient import (
    init_session_state,
    process_frame,
    save_exercise_session
)

router = APIRouter(prefix="/exercises", tags=["Exercises"])

# --------------------------------------------------
# 1️⃣ CREATE EXERCISE (PHYSICIAN)
# --------------------------------------------------
from fastapi import Form, UploadFile, File
import json
from utils.cloudinary import upload_profile_photo


@router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: int,
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    await ExerciseService.delete_exercise(
        exercise_id=exercise_id,
        physician_id=user["user_id"],
        db=db
    )

    return {
        "success": True,
        "message": "Exercise deleted successfully"
    }


@router.post("/create")
async def create_exercise(
    name: str = Form(...),
    category: str = Form(...),
    difficulty: DifficultyLevel = Form(...),
    target_body_parts: str = Form(...),  # JSON string
    target_image: UploadFile = File(...),

    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    # Parse JSON list
    try:
        target_body_parts_list = json.loads(target_body_parts)
    except Exception:
        raise HTTPException(400, "Invalid target_body_parts format")

    payload = CreateExerciseRequest(
        name=name,
        category=category,
        difficulty=difficulty,
        target_body_parts=target_body_parts_list
    )

    exercise = await ExerciseService.create_exercise(
        payload=payload,
        physician_id=user["user_id"],
        target_image=target_image,
        db=db
    )

    return {
        "success": True,
        "exercise_id": exercise.id,
        "target_image_url": exercise.target_image_url
    }


# --------------------------------------------------
# 2️⃣ CAPTURE DEMO REP (PHYSICIAN)
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
        frames=body.frames,
        db=db
    )


# --------------------------------------------------
# 3️⃣ LIST EXERCISES
# --------------------------------------------------
@staticmethod
async def list_exercises(db: AsyncSession):
    q = await db.execute(
        select(Exercise).where(Exercise.is_active == True)
    )
    return q.scalars().all()


from sqlalchemy import select, desc

@router.get("/my-exercises")
async def list_exercises(
    user=Depends(require_role("physician")),
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Exercise)
        .where(Exercise.created_by == user["user_id"], Exercise.is_active == True)
        .order_by(desc(Exercise.created_at))
    )

    exercises = q.scalars().all()

    return {
        "success": True,
        "exercises": exercises
    }

# ==================================================
# 4️⃣ PATIENT FRAME INGESTION (🔥 THIS IS THE UPDATE)
# ==================================================

# simple in-memory store (replace with Redis later)
SESSION_STORE = {}


@router.post("/{exercise_id}/sessions/{session_id}/frame")
async def ingest_patient_frame(
    exercise_id: int,
    session_id: int,
    file: UploadFile = File(...),
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    frame_bytes = await file.read()

    # ---- INIT SESSION STATE (once) ----
    if session_id not in SESSION_STORE:
        exercise = await ExerciseService.get_exercise_by_id(
            exercise_id=exercise_id,
            db=db
        )

        SESSION_STORE[session_id] = {
            "state": init_session_state(target_reps=exercise.target_reps),
            "exercise": exercise.pose_definition,
            "meta": {
                "patient_id": user["user_id"],
                "physician_id": exercise.created_by,
                "exercise_id": exercise.id,
                "patient_exercise_id": exercise.patient_exercise_id
            }
        }

    entry = SESSION_STORE[session_id]

    result = process_frame(
        frame_bytes=frame_bytes,
        exercise_definition=entry["exercise"],
        state=entry["state"]
    )

    # ---- SAVE ON COMPLETION ----
    if result["status"] == "COMPLETED":
        await save_exercise_session(
            db=db,
            patient_id=entry["meta"]["patient_id"],
            physician_id=entry["meta"]["physician_id"],
            exercise_id=entry["meta"]["exercise_id"],
            patient_exercise_id=entry["meta"]["patient_exercise_id"],
            state=entry["state"]
        )

        SESSION_STORE.pop(session_id, None)

    return result

@router.post("/{exercise_id}/sessions/{session_id}/end")
async def end_exercise_session(
    exercise_id: int,
    session_id: int,
    user=Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db)
):
    if session_id not in SESSION_STORE:
        return {
            "success": False,
            "message": "Session not found or already ended"
        }

    entry = SESSION_STORE[session_id]

    session = await save_exercise_session(
        db=db,
        patient_id=entry["meta"]["patient_id"],
        physician_id=entry["meta"]["physician_id"],
        exercise_id=entry["meta"]["exercise_id"],
        patient_exercise_id=entry["meta"]["patient_exercise_id"],
        state=entry["state"]
    )

    SESSION_STORE.pop(session_id, None)

    return {
        "success": True,
        "session_id": session.id,
        "completed_reps": session.completed_reps,
        "accuracy": session.accuracy_score,
        "duration_sec": session.duration_sec
    }
