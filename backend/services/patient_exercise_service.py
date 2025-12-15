from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from database.models import (
    Patient,
    PatientExercise,
    Exercise
)


class PatientExerciseService:

    @staticmethod
    async def assign_exercise(
        physician_id: int,
        payload,
        db: AsyncSession
    ):
        # 1️⃣ Validate patient is subscribed to this physician
        q = await db.execute(
            select(Patient).where(
                Patient.user_id == payload.patient_id,
                Patient.physician_id == physician_id
            )
        )
        if not q.scalar_one_or_none():
            raise HTTPException(403, "Patient not subscribed to you")

        # 2️⃣ Validate exercise ownership
        q = await db.execute(
            select(Exercise).where(
                Exercise.id == payload.exercise_id,
                Exercise.created_by == physician_id
            )
        )
        if not q.scalar_one_or_none():
            raise HTTPException(404, "Exercise not found")

        # 3️⃣ Prevent duplicate assignment
        q = await db.execute(
            select(PatientExercise).where(
                PatientExercise.patient_id == payload.patient_id,
                PatientExercise.exercise_id == payload.exercise_id,
                PatientExercise.is_active == True
            )
        )
        if q.scalar_one_or_none():
            raise HTTPException(400, "Exercise already assigned")

        # 4️⃣ Create assignment
        assignment = PatientExercise(
            patient_id=payload.patient_id,
            physician_id=physician_id,
            exercise_id=payload.exercise_id,
            sets=payload.sets,
            reps=payload.reps,
            frequency_per_day=payload.frequency_per_day
        )

        db.add(assignment)
        await db.commit()

        return {
            "success": True,
            "message": "Exercise assigned successfully"
        }
