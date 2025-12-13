import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from database.models import Exercise, ExerciseRule, PoseTemplate, PoseType


class ExerciseRuleService:

    @staticmethod
    async def generate_angle_ranges(exercise_id: int, db: AsyncSession):
        # 1️⃣ Fetch start pose
        start_q = await db.execute(
            select(PoseTemplate)
            .where(
                PoseTemplate.exercise_id == exercise_id,
                PoseTemplate.pose_type == PoseType.start
            )
        )
        start_pose = start_q.scalar_one_or_none()

        # 2️⃣ Fetch peak pose
        peak_q = await db.execute(
            select(PoseTemplate)
            .where(
                PoseTemplate.exercise_id == exercise_id,
                PoseTemplate.pose_type == PoseType.peak
            )
        )
        peak_pose = peak_q.scalar_one_or_none()

        if not start_pose or not peak_pose:
            raise HTTPException(
                status_code=400,
                detail="Start and peak poses must be captured first"
            )

        # 3️⃣ Generate angle ranges
        angle_ranges = {}

        for joint, start_angle in start_pose.reference_angles.items():
            peak_angle = peak_pose.reference_angles.get(joint)

            if peak_angle is None:
                continue

            min_angle = round(min(start_angle, peak_angle), 2)
            max_angle = round(max(start_angle, peak_angle), 2)

            angle_ranges[joint] = {
                "min": min_angle,
                "max": max_angle
            }

        if not angle_ranges:
            raise HTTPException(400, "No valid joint angles found")

        # 4️⃣ Upsert ExerciseRule
        rule_q = await db.execute(
            select(ExerciseRule)
            .where(ExerciseRule.exercise_id == exercise_id)
        )
        rule = rule_q.scalar_one_or_none()

        rules_payload = {
            "angleRanges": angle_ranges
        }

        if rule:
            rule.rules.update(rules_payload)
        else:
            rule = ExerciseRule(
                exercise_id=exercise_id,
                rules=rules_payload
            )
            db.add(rule)

        await db.commit()

        return {
            "success": True,
            "angle_ranges": angle_ranges
        }
    
    @staticmethod
    async def generate_alignment_rules(exercise_id: int, db: AsyncSession):
        # 1️⃣ Fetch reference pose
        q = await db.execute(
            select(PoseTemplate)
            .where(
                PoseTemplate.exercise_id == exercise_id,
                PoseTemplate.pose_type == PoseType.reference
            )
        )
        pose = q.scalar_one_or_none()

        if not pose:
            raise HTTPException(400, "Reference pose not captured")

        joints = pose.joints

        # 2️⃣ Shoulder & hip vertical differences (Y-axis)
        shoulder_diff = abs(
            joints["left_shoulder"]["y"] -
            joints["right_shoulder"]["y"]
        )

        hip_diff = abs(
            joints["left_hip"]["y"] -
            joints["right_hip"]["y"]
        )

        # 3️⃣ Spine deviation (angle from vertical)
        top = joints["nose"]
        bottom = joints["mid_hip"]

        dx = top["x"] - bottom["x"]
        dy = bottom["y"] - top["y"]

        spine_angle = abs(math.degrees(math.atan2(dx, dy)))

        # 4️⃣ Generate alignment rules
        alignment_rules = {
            "shoulderLevel": {
                "left": "left_shoulder",
                "right": "right_shoulder",
                "maxHeightDiff": round(shoulder_diff + 0.02, 3)
            },
            "hipLevel": {
                "left": "left_hip",
                "right": "right_hip",
                "maxHeightDiff": round(hip_diff + 0.02, 3)
            },
            "spineVertical": {
                "top": "nose",
                "bottom": "mid_hip",
                "maxAngleDeviation": round(spine_angle + 8, 2)
            }
        }

        # 5️⃣ Upsert ExerciseRule
        rule_q = await db.execute(
            select(ExerciseRule)
            .where(ExerciseRule.exercise_id == exercise_id)
        )
        rule = rule_q.scalar_one_or_none()

        if rule:
            rule.rules["alignment"] = alignment_rules
        else:
            rule = ExerciseRule(
                exercise_id=exercise_id,
                rules={"alignment": alignment_rules}
            )
            db.add(rule)

        await db.commit()

        return {
            "success": True,
            "alignment_rules": alignment_rules
        }
    
    @staticmethod
    async def generate_timing_and_stability_rules(
        exercise_id: int,
        db: AsyncSession
    ):
        # 1️⃣ Fetch exercise (for difficulty)
        q = await db.execute(
            select(Exercise).where(Exercise.id == exercise_id)
        )
        exercise = q.scalar_one_or_none()

        if not exercise:
            raise HTTPException(404, "Exercise not found")

        # 2️⃣ Difficulty-based timing defaults
        if exercise.difficulty.value == "beginner":
            timing = {
                "minRepDuration": 1.5,
                "peakHoldDuration": 0.8
            }
        elif exercise.difficulty.value == "intermediate":
            timing = {
                "minRepDuration": 1.2,
                "peakHoldDuration": 0.6
            }
        else:  # advanced
            timing = {
                "minRepDuration": 0.9,
                "peakHoldDuration": 0.4
            }

        # 3️⃣ Stability defaults (safe, rehab-oriented)
        stability = {
            "maxJointJitter": 0.05,
            "windowSize": 5
        }

        # 4️⃣ Upsert ExerciseRule
        rule_q = await db.execute(
            select(ExerciseRule)
            .where(ExerciseRule.exercise_id == exercise_id)
        )
        rule = rule_q.scalar_one_or_none()

        if rule:
            rule.rules["timing"] = timing
            rule.rules["stability"] = stability
        else:
            rule = ExerciseRule(
                exercise_id=exercise_id,
                rules={
                    "timing": timing,
                    "stability": stability
                }
            )
            db.add(rule)

        await db.commit()

        return {
            "success": True,
            "timing": timing,
            "stability": stability
        }
