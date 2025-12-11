# services/rehab_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from database.models import RehabPlan, RehabPlanExercise


class RehabService:
    @staticmethod
    async def create_plan(patient_id: int, physician_id: int, notes: str, db: AsyncSession):
        plan = RehabPlan(patient_id=patient_id, physician_id=physician_id, notes=notes)
        db.add(plan)
        await db.flush()
        await db.commit()
        return {"plan_id": plan.id}

    @staticmethod
    async def assign_exercise(plan_id: int, exercise_id: int, target_reps: int, target_sets: int, max_duration: int, custom_rules: dict, db: AsyncSession):
        # verify plan exists
        q = await db.execute(select(RehabPlan).where(RehabPlan.id == plan_id))
        plan = q.scalar_one_or_none()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        rpe = RehabPlanExercise(
            plan_id=plan_id,
            exercise_id=exercise_id,
            target_reps=target_reps,
            target_sets=target_sets,
            max_duration=max_duration,
            custom_rules=custom_rules
        )
        db.add(rpe)
        await db.commit()
        return {"assigned_id": rpe.id}
