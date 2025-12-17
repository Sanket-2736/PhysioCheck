from sqlalchemy import func
from sqlalchemy.future import select
from datetime import date, timedelta

from database.models import ExerciseSession


class PatientProgressService:

    @staticmethod
    async def get_daily_progress(patient_id: int, db):
        since = date.today() - timedelta(days=7)

        q = await db.execute(
            select(
                func.date(ExerciseSession.created_at).label("day"),
                func.count().label("sessions"),
                func.avg(ExerciseSession.accuracy_score).label("avg_accuracy"),
                func.sum(ExerciseSession.completed_reps).label("reps")
            )
            .where(
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.created_at >= since
            )
            .group_by(func.date(ExerciseSession.created_at))
            .order_by("day")
        )

        return [
            {
                "day": r.day.isoformat(),
                "sessions": r.sessions,
                "avgAccuracy": round(r.avg_accuracy or 0, 2),
                "reps": r.reps or 0
            }
            for r in q.all()
        ]

    @staticmethod
    async def get_weekly_progress(patient_id: int, db):
        q = await db.execute(
            select(
                func.yearweek(ExerciseSession.created_at).label("week"),
                func.count().label("sessions"),
                func.avg(ExerciseSession.accuracy_score).label("avg_accuracy"),
                func.sum(ExerciseSession.completed_reps).label("reps")
            )
            .where(ExerciseSession.patient_id == patient_id)
            .group_by("week")
            .order_by("week")
        )

        return [
            {
                "week": r.week,
                "sessions": r.sessions,
                "avgAccuracy": round(r.avg_accuracy or 0, 2),
                "reps": r.reps or 0
            }
            for r in q.all()
        ]

    @staticmethod
    async def get_recovery_trend(patient_id: int, db):
        q = await db.execute(
            select(
                ExerciseSession.created_at,
                ExerciseSession.accuracy_score,
                ExerciseSession.completed_reps
            )
            .where(ExerciseSession.patient_id == patient_id)
            .order_by(ExerciseSession.created_at)
        )

        return [
            {
                "date": s.created_at.date().isoformat(),
                "accuracy": s.accuracy_score,
                "reps": s.completed_reps
            }
            for s in q.scalars()
        ]
