from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from database.models import Exercise


class ExerciseService:

    @staticmethod
    async def create_exercise(payload, physician_id: int, db: AsyncSession):

        # Prevent duplicate exercise names
        q = await db.execute(
            select(Exercise).where(Exercise.name == payload.name)
        )
        if q.scalar_one_or_none():
            raise HTTPException(400, "Exercise already exists")

        exercise = Exercise(
            name=payload.name,
            category=payload.category,
            difficulty=payload.difficulty,
            target_body_parts=payload.target_body_parts,
            created_by=physician_id
        )

        db.add(exercise)
        await db.commit()
        await db.refresh(exercise)

        return exercise
