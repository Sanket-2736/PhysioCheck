from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import ExerciseRule


class ExerciseRuleService:

    @staticmethod
    async def save_rules(
        exercise_id: int,
        angle_ranges: dict,
        timing: dict,
        stability: float,
        db: AsyncSession
    ):
        res = await db.execute(
            select(ExerciseRule).where(ExerciseRule.exercise_id == exercise_id)
        )
        rule = res.scalar_one_or_none()

        payload = {
            "angleRanges": angle_ranges,
            "timing": timing,
            "stability": stability
        }

        if rule:
            rule.rules.update(payload)
        else:
            db.add(ExerciseRule(exercise_id=exercise_id, rules=payload))

        await db.commit()
