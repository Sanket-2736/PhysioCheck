# services/live_feedback_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from database.models import ExerciseSession, ExercisePreset  # ✅ use preset
from services.exercises_service import ExerciseService

from pose.pose_tracking_patient import (
    init_session_state,
    process_frame,
    save_exercise_session,
)


class LiveFeedbackService:
    SESSION_STORE = {}

    @staticmethod
    async def evaluate_frame(
        session_id: int,
        frame: dict,
        db: AsyncSession,
    ):
        # 1) Find ExerciseSession
        q = await db.execute(
            select(ExerciseSession).where(ExerciseSession.id == session_id)
        )
        session = q.scalar_one_or_none()
        if not session:
            raise HTTPException(404, "Session not found")

        exercise_id = session.exercise_id

        # 2) Init per-session state once
        if session_id not in LiveFeedbackService.SESSION_STORE:
            # Load Exercise
            exercise = await ExerciseService.get_exercise_by_id(
                exercise_id=exercise_id,
                db=db,
            )
            if not exercise:
                raise HTTPException(404, "Exercise not found for session")

            # Load preset (this is where you already store pose config)
            preset_q = await db.execute(
                select(ExercisePreset).where(ExercisePreset.exercise_id == exercise_id)
            )
            preset = preset_q.scalar_one_or_none()

            # Build exercise definition expected by pose_tracking_patient
            if preset:
                pose_def = {
                    "exerciseName": exercise.name,
                    **preset.preset,  # should include criticalJoints, alignmentRules, repDefinition
                }
            else:
                # Fallback generic config if no preset exists
                pose_def = {
                    "exerciseName": exercise.name or "Exercise",
                    "criticalJoints": [],
                    "repDefinition": {
                        "joint": "any_joint",
                        "validRange": [40, 140],
                        "exitRange": [0, 90],
                        "minHoldTime": 0.15,
                    },
                }

            LiveFeedbackService.SESSION_STORE[session_id] = {
                "state": init_session_state(
                    target_reps=getattr(exercise, "reps", 5)
                ),
                "exercise": pose_def,
                "meta": {
                    "patient_id": session.patient_id,
                    "physician_id": session.physician_id,
                    "exercise_id": session.exercise_id,
                    "patient_exercise_id": session.patient_exercise_id,
                },
            }

        entry = LiveFeedbackService.SESSION_STORE[session_id]

        # 3) Use generic rep logic (time‑based in your current process_frame)
        result = process_frame(
            frame_bytes=b"",
            exercise_definition=entry["exercise"],
            state=entry["state"],
            frame=frame,
        )


        # 4) Auto-save if COMPLETED
        if result["status"] == "COMPLETED":
            await save_exercise_session(
                db=db,
                patient_id=entry["meta"]["patient_id"],
                physician_id=entry["meta"]["physician_id"],
                exercise_id=entry["meta"]["exercise_id"],
                patient_exercise_id=entry["meta"]["patient_exercise_id"],
                state=entry["state"],
            )
            LiveFeedbackService.SESSION_STORE.pop(session_id, None)

        # 5) Rep-based live feedback
        return {
            "repCount": result["repCount"],
            "repState": result["repState"],
            "status": result["status"],
            "angle": result["angle"],
            "accuracy": 100.0 if result["repState"] == "COUNTED" else 60.0,
            "errors": {},
        }
