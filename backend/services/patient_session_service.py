# services/patient_session_service.py

import time
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

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
            completed_sets=1,
            accuracy_score=0.0,
            error_summary={},
            joint_stats={},
            duration_sec=0.0
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        return {"success": True, "session_id": session.id}

    @staticmethod
    async def end_session(
        session_id: int,
        payload: dict,
        db: AsyncSession
    ):
        session = await db.get(ExerciseSession, session_id)
        if not session:
            raise HTTPException(404, "Session not found")

        state = payload.get("state", {})

        # ---- normalize joint stats ----
        joint_stats = {}
        for j, v in state.get("jointStats", {}).items():
            joint_stats[j] = {
                "min": round(v["min"], 2),
                "max": round(v["max"], 2),
                "avg": round(v["sum"] / max(v["count"], 1), 2)
            }

        session.completed_reps = state.get("repCount", 0)
        session.error_summary = state.get("errorSummary", {})
        session.joint_stats = joint_stats
        session.duration_sec = time.time() - state.get("startTime", time.time())
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
