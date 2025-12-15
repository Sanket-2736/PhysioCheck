from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import statistics

from database.models import Exercise, PoseTemplate, PoseType, ExerciseRule
from pose.rep_analysis import detect_rep_phases
from pose.stability_analysis import assess_stability


class RepCaptureService:

    @staticmethod
    async def capture_and_generate(
        exercise_id: int,
        frames: list,
        db: AsyncSession
    ):
        if len(frames) < 15:
            raise HTTPException(400, "Insufficient frame data")

        q = await db.execute(
            select(Exercise).where(Exercise.id == exercise_id)
        )
        exercise = q.scalar_one_or_none()
        if not exercise:
            raise HTTPException(404, "Exercise not found")

        primary_joint = "left_shoulder"

        # ---- ANGLE SERIES ----
        angle_series = [
            f.angles.get(primary_joint)
            for f in frames
            if f.angles and primary_joint in f.angles
        ]

        if len(angle_series) < 5:
            raise HTTPException(400, "Not enough valid joint angles")

        start_i, peak_i, end_i = detect_rep_phases(angle_series)

        start = frames[start_i]
        peak = frames[peak_i]
        end = frames[end_i]

        # ---- REFERENCE POSE (MOST STABLE) ----
        reference = min(
            frames,
            key=lambda f: statistics.pstdev(
                f.angles.values()
            ) if f.angles else float("inf")
        )

        # ---- SAVE POSES ----
        for pose_type, frame in [
            (PoseType.reference, reference),
            (PoseType.start, start),
            (PoseType.peak, peak),
            (PoseType.end, end),
        ]:
            await RepCaptureService._save_pose(
                exercise_id, pose_type, frame, db
            )

        # ---- ANGLE RANGES ----
        angle_ranges = {
            j: {
                "min": min(start.angles[j], peak.angles[j]),
                "max": max(start.angles[j], peak.angles[j]),
            }
            for j in start.angles
            if j in peak.angles
        }

        # ---- TIMING ----
        timing = {
            "repDuration": round(
                end.timestamp - start.timestamp, 2
            )
        }

        # ---- STABILITY ----
        stability = assess_stability(frames)

        # ---- SAVE RULES ----
        q = await db.execute(
            select(ExerciseRule)
            .where(ExerciseRule.exercise_id == exercise_id)
        )
        rule = q.scalar_one_or_none()

        payload = {
            "angleRanges": angle_ranges,
            "timing": timing,
            "stability": stability
        }

        if rule:
            rule.rules.update(payload)
        else:
            db.add(
                ExerciseRule(
                    exercise_id=exercise_id,
                    rules=payload
                )
            )

        await db.commit()
        return {"success": True}

    # -------------------------------------
    # SAVE SINGLE POSE TEMPLATE
    # -------------------------------------
    @staticmethod
    async def _save_pose(exercise_id, pose_type, frame, db):
        q = await db.execute(
            select(PoseTemplate)
            .where(
                PoseTemplate.exercise_id == exercise_id,
                PoseTemplate.pose_type == pose_type
            )
        )
        old = q.scalar_one_or_none()
        if old:
            await db.delete(old)
            await db.commit()

        db.add(
            PoseTemplate(
                exercise_id=exercise_id,
                pose_type=pose_type,
                joints=frame.joints,
                reference_angles=frame.angles
            )
        )
        await db.commit()
