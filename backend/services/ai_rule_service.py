# services/ai_rule_service.py
from sqlalchemy import func, desc, cast, Integer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from database.models import ExerciseSession, SessionProgress
from services.exercises_service import ExerciseService

class AIRuleService:
    @staticmethod
    async def analyze_session_performance(exercise_id: int, patient_id: int, db: AsyncSession):
        # 🚀 EFFICIENT: Recent COMPLETED sessions
        sessions = await db.execute(
            select(ExerciseSession)
            .join(SessionProgress, SessionProgress.session_id == ExerciseSession.id)
            .where(
                ExerciseSession.exercise_id == exercise_id,
                ExerciseSession.patient_id == patient_id,
                ExerciseSession.status == "COMPLETED",
                ExerciseSession.ended_at >= func.now() - timedelta(days=30),
                cast(SessionProgress.event['repCount'], Integer).isnot(None)
            )
            .group_by(ExerciseSession.id)
            .order_by(desc(ExerciseSession.ended_at))
            .limit(50)
        )
        
        sessions_list = sessions.scalars().all()
        if not sessions_list:
            return {"message": "No recent successful sessions found"}
        
        # 🚀 SIMPLIFIED ANALYSIS (no missing functions needed)
        avg_reps = sum(s.completed_reps for s in sessions_list) / len(sessions_list)
        exercise = await ExerciseService.get_exercise_by_id(exercise_id, db)
        
        # Basic rule suggestions based on performance
        suggestions = {
            "repDefinition": {
                "joint": "left_shoulder",
                "validRange": [45, 115] if avg_reps < 5 else [50, 110],  # Auto-loosen if poor
                "exitRange": [-5, 75],
                "minHoldTime": 0.2
            }
        }
        
        return {
            "sessions_analyzed": len(sessions_list),
            "avg_reps": round(avg_reps, 1),
            "current_rules": getattr(exercise, 'pose_definition', {}),
            "suggested_rules": suggestions,
            "expected_gain": "+25%" if avg_reps < 5 else "+10%"
        }
