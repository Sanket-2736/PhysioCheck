# services/patient_exercise_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from database.models import PatientExercise


class PatientExerciseService:

    @staticmethod
    async def assign_exercise(
        physician_id: int,
        payload,
        db: AsyncSession
    ):
        # Check if already assigned & active
        q = await db.execute(
            select(PatientExercise).where(
                PatientExercise.patient_id == payload.patient_id,
                PatientExercise.exercise_id == payload.exercise_id,
                PatientExercise.physician_id == physician_id,
                PatientExercise.is_active == True
            )
        )
        existing = q.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Exercise already assigned to this patient"
            )

        # Check if previously assigned but inactive → reactivate
        q = await db.execute(
            select(PatientExercise).where(
                PatientExercise.patient_id == payload.patient_id,
                PatientExercise.exercise_id == payload.exercise_id,
                PatientExercise.physician_id == physician_id,
                PatientExercise.is_active == False
            )
        )
        inactive = q.scalar_one_or_none()

        if inactive:
            inactive.is_active = True
            inactive.sets = payload.sets
            inactive.reps = payload.reps
            inactive.frequency_per_day = payload.frequency_per_day

            await db.commit()
            await db.refresh(inactive)

            return {
                "success": True,
                "message": "Exercise re-assigned to patient",
                "patient_exercise_id": inactive.id
            }

        # Fresh assignment
        assignment = PatientExercise(
            patient_id=payload.patient_id,
            physician_id=physician_id,
            exercise_id=payload.exercise_id,
            sets=payload.sets,
            reps=payload.reps,
            frequency_per_day=payload.frequency_per_day,
            is_active=True
        )

        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)

        return {
            "success": True,
            "message": "Exercise assigned to patient",
            "patient_exercise_id": assignment.id
        }

    @staticmethod
    async def deassign_exercise(
        physician_id: int,
        patient_exercise_id: int,
        db: AsyncSession
    ):
        q = await db.execute(
            select(PatientExercise).where(
                PatientExercise.id == patient_exercise_id,
                PatientExercise.physician_id == physician_id,
                PatientExercise.is_active == True
            )
        )
        assignment = q.scalar_one_or_none()

        if not assignment:
            raise HTTPException(404, "Active assignment not found")

        assignment.is_active = False
        await db.commit()

        return {
            "success": True,
            "message": "Exercise de-assigned from patient"
        }
