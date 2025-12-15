from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from database.models import ExerciseSession


class PatientProgressService:

    @staticmethod
    async def get_progress(patient_id: int, db: AsyncSession):
        q = await db.execute(
            select(
                ExerciseSession.exercise_id,
                func.count().label("sessions"),
                func.avg(ExerciseSession.accuracy_score).label("avg_accuracy"),
                func.sum(ExerciseSession.duration_sec).label("total_time")
            )
            .where(ExerciseSession.patient_id == patient_id)
            .group_by(ExerciseSession.exercise_id)
        )

        rows = q.all()

        return {
            "success": True,
            "progress": [
                {
                    "exercise_id": r.exercise_id,
                    "sessions": int(r.sessions),
                    "avg_accuracy": round(r.avg_accuracy, 2),
                    "total_time_sec": round(r.total_time, 1)
                }
                for r in rows
            ]
        }
