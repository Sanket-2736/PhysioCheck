from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import ExerciseSession


class ReportService:

    @staticmethod
    async def patient_report(patient_id: int, db: AsyncSession):
        q = await db.execute(
            select(ExerciseSession)
            .where(ExerciseSession.patient_id == patient_id)
            .order_by(ExerciseSession.created_at)
        )

        sessions = q.scalars().all()
        if not sessions:
            return {}

        total_reps = sum(s.completed_reps for s in sessions)
        avg_accuracy = round(
            sum(s.accuracy_score for s in sessions) / len(sessions), 2
        )

        error_freq = {}
        for s in sessions:
            for e, c in (s.error_summary or {}).items():
                error_freq[e] = error_freq.get(e, 0) + c

        common_mistakes = sorted(
            [
                {"mistake": k, "count": v}
                for k, v in error_freq.items()
            ],
            key=lambda x: x["count"],
            reverse=True
        )[:5]

        timeline = [
            {
                "date": s.created_at.isoformat(),
                "reps": s.completed_reps,
                "accuracy": s.accuracy_score,
                "duration_sec": s.duration_sec,
                "errors": s.error_summary or {}
            }
            for s in sessions
        ]

        return {
            "summary": {
                "total_sessions": len(sessions),
                "total_reps": total_reps,
                "avg_accuracy": avg_accuracy
            },
            "common_mistakes": common_mistakes,
            "timeline": timeline
        }
