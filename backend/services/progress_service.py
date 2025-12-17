from sqlalchemy import select, func
from database.models import ExerciseSession

class ProgressService:

    @staticmethod
    async def weekly(patient_id: int, db):
        q = await db.execute(
            select(
                func.year(ExerciseSession.created_at).label("year"),
                func.week(ExerciseSession.created_at).label("week"),
                func.sum(ExerciseSession.completed_reps).label("reps"),
                func.avg(ExerciseSession.accuracy_score).label("accuracy")
            )
            .where(ExerciseSession.patient_id == patient_id)
            .group_by("year", "week")
            .order_by("year", "week")
        )

        return [
            {
                "year": year,
                "week": week,
                "total_reps": reps or 0,
                "avg_accuracy": round(acc or 0, 2)
            }
            for year, week, reps, acc in q.all()
        ]
