from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from utils.cloudinary import upload_profile_photo
from database.models import Exercise


class ExerciseService:
    @staticmethod
    async def list_exercises(db: AsyncSession):
        q = await db.execute(select(Exercise)).where(Exercise.is_active == True)
        return q.scalars().all()
    
    @staticmethod
    async def delete_exercise(
        exercise_id: int,
        physician_id: int,
        db: AsyncSession
    ):
        q = await db.execute(
            select(Exercise).where(
                Exercise.id == exercise_id,
                Exercise.created_by == physician_id,
                Exercise.is_active == True
            )
        )
        exercise = q.scalar_one_or_none()

        if not exercise:
            raise HTTPException(404, "Exercise not found")

        # 🔥 SOFT DELETE
        exercise.is_active = False
        await db.commit()

        return True


    @staticmethod
    async def create_exercise(
        payload,
        physician_id: int,
        target_image,
        db: AsyncSession
    ):
        # Prevent duplicate exercise names
        q = await db.execute(
            select(Exercise).where(Exercise.name == payload.name)
        )
        if q.scalar_one_or_none():
            raise HTTPException(400, "Exercise already exists")

        if not target_image:
            raise HTTPException(400, "Target image is required")

        # 🔥 Upload to Cloudinary
        image_url = upload_profile_photo(target_image.file)

        exercise = Exercise(
            name=payload.name,
            category=payload.category,
            difficulty=payload.difficulty,
            target_body_parts=payload.target_body_parts,
            target_image_url=image_url,
            created_by=physician_id
        )

        db.add(exercise)
        await db.commit()
        await db.refresh(exercise)

        return exercise

    @staticmethod
    async def get_exercise_by_id(exercise_id: int, db: AsyncSession):
        q = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
        return q.scalar_one_or_none()
