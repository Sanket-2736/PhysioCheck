# services/exercises_service.py
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from typing import Dict, Any
from database.models import Exercise, ExercisePreset, PoseTemplate, ExerciseRule, ExerciseLogic


class ExerciseService:
    @staticmethod
    async def create_exercise(physician_id: int, payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        ex = Exercise(
            name=payload["name"],
            category=payload.get("category"),
            difficulty=payload.get("difficulty"),
            target_body_parts=payload.get("target_body_parts", []),
            created_by=physician_id
        )
        db.add(ex)
        await db.flush()
        await db.commit()
        return {"id": ex.id, "name": ex.name}

    @staticmethod
    async def save_preset(exercise_id: int, preset_json: Dict[str, Any], db: AsyncSession):
        # upsert latest preset
        p = ExercisePreset(exercise_id=exercise_id, preset=preset_json)
        db.add(p)
        await db.commit()
        return {"exercise_id": exercise_id, "preset_id": p.id}

    @staticmethod
    async def save_capture(exercise_id: int, pose_type: str, joints: Dict[str, Any], reference_angles: Dict[str, Any], db: AsyncSession):
        pt = PoseTemplate(
            exercise_id=exercise_id,
            pose_type=pose_type,
            joints=joints,
            reference_angles=reference_angles
        )
        db.add(pt)
        await db.commit()
        return {"pose_template_id": pt.id}

    @staticmethod
    async def save_rules(exercise_id: int, rules_json: Dict[str, Any], db: AsyncSession):
        r = ExerciseRule(exercise_id=exercise_id, rules=rules_json)
        db.add(r)
        await db.commit()
        return {"rule_id": r.id}

    @staticmethod
    async def save_logic(exercise_id: int, logic_json: Dict[str, Any], db: AsyncSession):
        l = ExerciseLogic(exercise_id=exercise_id, logic=logic_json)
        db.add(l)
        await db.commit()
        return {"logic_id": l.id}

    @staticmethod
    async def get_exercise_definition(exercise_id: int, db: AsyncSession) -> Dict[str, Any]:
        result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
        exercise = result.scalar_one_or_none()
        if not exercise:
            raise HTTPException(404, "Exercise not found")

        preset_q = await db.execute(select(ExercisePreset).where(ExercisePreset.exercise_id == exercise_id).order_by(ExercisePreset.id.desc()))
        preset = preset_q.scalar_one_or_none()

        pose_q = await db.execute(select(PoseTemplate).where(PoseTemplate.exercise_id == exercise_id))
        poses = [p for p in pose_q.scalars().all()]

        rule_q = await db.execute(select(ExerciseRule).where(ExerciseRule.exercise_id == exercise_id).order_by(ExerciseRule.id.desc()))
        rule = rule_q.scalar_one_or_none()

        return {
            "exercise": {
                "id": exercise.id,
                "name": exercise.name,
                "category": exercise.category,
                "difficulty": exercise.difficulty.value if exercise.difficulty else None,
                "target_body_parts": exercise.target_body_parts
            },
            "preset": preset.preset if preset else None,
            "poses": [{"id": p.id, "pose_type": p.pose_type.value, "reference_angles": p.reference_angles} for p in poses],
            "rules": rule.rules if rule else None
        }
