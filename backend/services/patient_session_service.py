from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import datetime

from database.models import PatientExercise, ExerciseSession


class PatientSessionService:

    @staticmethod
    async def start_session(
        patient_exercise_id: int,
        patient_id: int,
        db: AsyncSession
    ):
        q = await db.execute(
            select(PatientExercise).where(
                PatientExercise.id == patient_exercise_id,
                PatientExercise.patient_id == patient_id,
                PatientExercise.is_active == True
            )
        )
        pe = q.scalar_one_or_none()
        if not pe:
            raise HTTPException(403, "Exercise not assigned")

        session = ExerciseSession(
            patient_id=patient_id,
            physician_id=pe.physician_id,
            exercise_id=pe.exercise_id,
            patient_exercise_id=pe.id,
            completed_reps=0,
            completed_sets=0,
            accuracy_score=0.0,
            error_summary={},
            joint_stats={},
            duration_sec=0.0
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        return {
            "success": True,
            "session_id": session.id
        }

    # ==================================================
    # ✅ ADD THIS METHOD (THIS FIXES YOUR ERROR)
    # ==================================================
    @staticmethod
    async def end_session(
        session_id: int,
        payload: dict,
        db: AsyncSession
    ):
        q = await db.execute(
            select(ExerciseSession).where(
                ExerciseSession.id == session_id
            )
        )
        session = q.scalar_one_or_none()
        if not session:
            raise HTTPException(404, "Session not found")

        # ---- UPDATE FINAL VALUES (SAFE DEFAULTS) ----
        session.duration_sec = payload.get("duration_sec", session.duration_sec)
        session.accuracy_score = payload.get("accuracy", session.accuracy_score)
        session.completed_reps = payload.get("completed_reps", session.completed_reps)
        session.completed_sets = payload.get("completed_sets", session.completed_sets)
        session.error_summary = payload.get("error_summary", session.error_summary)
        session.joint_stats = payload.get("joint_stats", session.joint_stats)

        session.ended_at = datetime.utcnow()

        await db.commit()
        await db.refresh(session)

        return {
            "success": True,
            "session_id": session.id,
            "completed_reps": session.completed_reps,
            "accuracy": session.accuracy_score,
            "duration_sec": session.duration_sec
        }
