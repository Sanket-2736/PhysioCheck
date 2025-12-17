from sqlalchemy.future import select
from database.models import ExerciseSession

class AnalyticsService:
    @staticmethod
    async def get_risk_summary(patient_id: int, db):
        q = await db.execute(
            select(ExerciseSession.risk_alerts)
            .where(ExerciseSession.patient_id == patient_id)
        )

        summary = {}

        for alerts in q.scalars():
            if not alerts:
                continue
            for a in alerts:
                key = a["joint"]
                summary[key] = summary.get(key, 0) + 1

        return summary

    @staticmethod
    async def get_common_mistakes(patient_id: int, db, top_k: int = 5):
        freq = await AnalyticsService.get_error_frequency(patient_id, db)

        return sorted(
            [
                {"mistake": k, "count": v}
                for k, v in freq.items()
            ],
            key=lambda x: x["count"],
            reverse=True
        )[:top_k]


    @staticmethod
    async def get_error_frequency(patient_id: int, db):
        q = await db.execute(
            select(ExerciseSession.error_summary)
            .where(ExerciseSession.patient_id == patient_id)
        )

        freq = {}

        for row in q.scalars():
            if not row:
                continue
            for joint, count in row.items():
                freq[joint] = freq.get(joint, 0) + count

        return freq
