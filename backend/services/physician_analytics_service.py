from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from database.models import ExerciseSession


class PhysicianAnalyticsService:

    @staticmethod
    async def get_patient_analytics(
        physician_id: int,
        db: AsyncSession
    ):
        q = await db.execute(
            select(
                ExerciseSession.patient_id,
                func.count().label("sessions"),
                func.avg(ExerciseSession.accuracy_score).label("avg_accuracy"),
                func.max(ExerciseSession.created_at).label("last_session")
            )
            .where(ExerciseSession.physician_id == physician_id)
            .group_by(ExerciseSession.patient_id)
        )

        rows = q.all()

        return {
            "success": True,
            "patients": [
                {
                    "patient_id": r.patient_id,
                    "sessions": int(r.sessions),
                    "avg_accuracy": round(r.avg_accuracy, 2),
                    "last_session": r.last_session
                }
                for r in rows
            ]
        }
