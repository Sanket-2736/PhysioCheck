# services/sessions_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import uuid, threading, asyncio
from typing import Optional, Dict, Any

from database.models import Session, SessionProgress, SessionResult, Exercise, ExercisePreset
from pose.pose_tracking_patient import run_exercise_session  # adjust path to your module


class SessionService:
    @staticmethod
    async def start_session(exercise_id: int, patient_id: int, target_reps: int, max_duration: int, db: AsyncSession, run_in_background: bool = True) -> str:
        # validate
        res = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
        exercise = res.scalar_one_or_none()
        if not exercise:
            raise HTTPException(404, "Exercise not found")

        preset_q = await db.execute(select(ExercisePreset).where(ExercisePreset.exercise_id == exercise_id).order_by(ExercisePreset.id.desc()))
        preset = preset_q.scalar_one_or_none()
        if not preset:
            raise HTTPException(400, "No preset configured for this exercise")

        exercise_definition = {"exerciseName": exercise.name, **preset.preset}

        session_id = str(uuid.uuid4())
        s = Session(id=session_id, patient_id=patient_id, exercise_id=exercise_id, target_reps=target_reps, max_duration=max_duration)
        db.add(s)
        await db.commit()

        # define DB save helpers
        async def save_progress(event: Dict[str, Any]):
            async with db.bind.connect() as conn:
                # create new async session to avoid using same session from another thread
                async_session = AsyncSession(bind=conn)
                try:
                    pr = SessionProgress(session_id=session_id, event=event)
                    async_session.add(pr)
                    await async_session.commit()
                finally:
                    await async_session.close()

        async def save_final(result: Dict[str, Any]):
            async with db.bind.connect() as conn:
                async_session = AsyncSession(bind=conn)
                try:
                    res_row = SessionResult(session_id=session_id, summary=result)
                    await async_session.merge(res_row)
                    sess = await async_session.get(Session, session_id)
                    sess.status = "COMPLETED"
                    await async_session.commit()
                finally:
                    await async_session.close()

        # thread callback wrapper
        def callback(event: Dict[str, Any]):
            asyncio.run(save_progress(event))

        def runner():
            result = run_exercise_session(exercise_definition=exercise_definition,
                                         target_reps=target_reps,
                                         max_duration=max_duration,
                                         callback=callback,
                                         show_video=False)
            asyncio.run(save_final(result))

        if run_in_background:
            t = threading.Thread(target=runner, daemon=True)
            t.start()
        else:
            runner()

        return session_id

    @staticmethod
    async def get_session_status(session_id: str, db: AsyncSession):
        s = await db.get(Session, session_id)
        if not s:
            raise HTTPException(404, "Session not found")

        prog_q = await db.execute(select(SessionProgress).where(SessionProgress.session_id == session_id).order_by(SessionProgress.id.desc()))
        latest = prog_q.scalar_one_or_none()

        final_q = await db.execute(select(SessionResult).where(SessionResult.session_id == session_id))
        final = final_q.scalar_one_or_none()

        return {"session": {"id": s.id, "status": s.status.value, "target_reps": s.target_reps, "max_duration": s.max_duration, "started_at": s.started_at, "ended_at": s.ended_at}, "progress": latest.event if latest else None, "final": final.summary if final else None}

    @staticmethod
    async def get_session_summary(session_id: str, db: AsyncSession):
        final_q = await db.execute(select(SessionResult).where(SessionResult.session_id == session_id))
        final = final_q.scalar_one_or_none()
        if not final:
            raise HTTPException(404, "Summary not found")
        return final.summary
