from sqlalchemy import func
from database.models import ExerciseSession

class ProgressService:

    @staticmethod
    async def weekly(patient_id: int, db):
        q = await db.execute(
            func.select(
                func.week(ExerciseSession.created_at).label("week"),
                func.sum(ExerciseSession.completed_reps),
                func.avg(ExerciseSession.accuracy_score)
            )
            .where(ExerciseSession.patient_id == patient_id)
            .group_by("week")
            .order_by("week")
        )

        return [
            {
                "week": w,
                "total_reps": reps,
                "avg_accuracy": round(acc, 2)
            }
            for w, reps, acc in q.all()
        ]
