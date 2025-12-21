# services/rehab_service.py
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from database.models import Exercise, RehabPlan, RehabPlanExercise


class RehabService:

    # --------------------------------------------------
    # GET CURRENT ACTIVE PLAN
    # --------------------------------------------------
    @staticmethod
    async def get_current_plan(patient_id: int, physician_id: int, db: AsyncSession):
        q = await db.execute(
            select(RehabPlan)
            .where(
                RehabPlan.patient_id == patient_id,
                RehabPlan.physician_id == physician_id,
                RehabPlan.is_active == True
            )
            .order_by(RehabPlan.created_at.desc())
        )

        plan = q.scalar_one_or_none()

        return {
            "rehab_plan": plan if plan else None
        }

    # --------------------------------------------------
    # LIST EXERCISES IN PLAN (PHYSICIAN SAFE)
    # --------------------------------------------------
    @staticmethod
    async def list_plan_exercises(plan_id: int, physician_id: int, db: AsyncSession):
        q = await db.execute(
            select(
                RehabPlanExercise.id.label("plan_exercise_id"),
                Exercise.name.label("exercise_name"),
                RehabPlanExercise.target_sets,
                RehabPlanExercise.target_reps,
                RehabPlanExercise.max_duration
            )
            .join(Exercise, Exercise.id == RehabPlanExercise.exercise_id)
            .join(RehabPlan, RehabPlan.id == RehabPlanExercise.plan_id)
            .where(
                RehabPlanExercise.plan_id == plan_id,
                RehabPlanExercise.is_active == True,
                RehabPlan.physician_id == physician_id
            )
        )

        rows = q.all()

        exercises = [
            {
                "plan_exercise_id": r.plan_exercise_id,
                "exercise_name": r.exercise_name,
                "target_sets": r.target_sets,
                "target_reps": r.target_reps,
                "max_duration": r.max_duration
            }
            for r in rows
        ]

        return {"exercises": exercises}

    # --------------------------------------------------
    # DEASSIGN EXERCISE (SOFT REMOVE, SAFE)
    # --------------------------------------------------
    @staticmethod
    async def deassign_exercise(
        plan_id: int,
        plan_exercise_id: int,
        physician_id: int,
        db: AsyncSession
    ):
        q = await db.execute(
            select(RehabPlanExercise)
            .join(RehabPlan, RehabPlan.id == RehabPlanExercise.plan_id)
            .where(
                RehabPlanExercise.id == plan_exercise_id,
                RehabPlanExercise.plan_id == plan_id,
                RehabPlanExercise.is_active == True,
                RehabPlan.physician_id == physician_id
            )
        )

        plan_exercise = q.scalar_one_or_none()

        if not plan_exercise:
            raise HTTPException(404, "Exercise not assigned to plan")

        plan_exercise.is_active = False
        await db.commit()

        return {
            "success": True,
            "message": "Exercise removed from rehab plan"
        }

    # --------------------------------------------------
    # CREATE PLAN
    # --------------------------------------------------
    

    @staticmethod
    async def create_plan(patient_id: int, physician_id: int, notes: str, db: AsyncSession):

        # 🔥 Deactivate existing active plans
        await db.execute(
            update(RehabPlan)
            .where(
                RehabPlan.patient_id == patient_id,
                RehabPlan.physician_id == physician_id,
                RehabPlan.is_active == True
            )
            .values(is_active=False)
        )

        # ✅ Create new plan
        plan = RehabPlan(
            patient_id=patient_id,
            physician_id=physician_id,
            notes=notes,
            is_active=True
        )

        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        return {"plan_id": plan.id}


    # --------------------------------------------------
    # ASSIGN EXERCISE (FULLY SAFE)
    # --------------------------------------------------
    @staticmethod
    async def assign_exercise(
        plan_id: int,
        exercise_id: int,
        target_reps: int,
        target_sets: int,
        max_duration: int,
        custom_rules: dict,
        physician_id: int,
        db: AsyncSession
    ):
        # ✅ Verify plan ownership
        q = await db.execute(
            select(RehabPlan).where(
                RehabPlan.id == plan_id,
                RehabPlan.physician_id == physician_id,
                RehabPlan.is_active == True
            )
        )
        plan = q.scalar_one_or_none()

        if not plan:
            raise HTTPException(404, "Rehab plan not found")

        # ✅ Prevent duplicate assignment
        q = await db.execute(
            select(RehabPlanExercise).where(
                RehabPlanExercise.plan_id == plan_id,
                RehabPlanExercise.exercise_id == exercise_id,
                RehabPlanExercise.is_active == True
            )
        )
        if q.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Exercise already assigned to this rehab plan"
            )

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
        await db.refresh(rpe)

        return {"assigned_id": rpe.id}
