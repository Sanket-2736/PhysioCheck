from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from database.models import ExerciseSession, ExerciseRule

class LiveFeedbackService:

    @staticmethod
    async def evaluate_frame(
        session_id: int,
        frame: dict,
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

        q = await db.execute(
            select(ExerciseRule).where(
                ExerciseRule.exercise_id == session.exercise_id
            )
        )
        rule = q.scalar_one_or_none()
        if not rule:
            raise HTTPException(400, "Rules not found")

        angle_ranges = rule.rules.get("angleRanges", {})
        errors = {}
        accuracy_hits = 0
        total_checks = 0

        for joint, angle in frame["angles"].items():
            if joint not in angle_ranges:
                continue

            total_checks += 1
            min_a = angle_ranges[joint]["min"]
            max_a = angle_ranges[joint]["max"]

            if min_a <= angle <= max_a:
                accuracy_hits += 1
            else:
                errors.setdefault(joint, 0)
                errors[joint] += 1

        accuracy = (
            round((accuracy_hits / total_checks) * 100, 2)
            if total_checks > 0 else 0.0
        )

        return {
            "accuracy": accuracy,
            "errors": errors
        }
