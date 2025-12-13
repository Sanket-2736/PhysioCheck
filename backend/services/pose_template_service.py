from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from database.models import PoseTemplate, Exercise, PoseType
from pose_tracking_physician import capture_reference_pose


class PoseTemplateService:

    @staticmethod
    async def capture_pose_template(
        exercise_id: int,
        pose_type: PoseType,
        db: AsyncSession
    ):
        # 1. Validate exercise exists
        q = await db.execute(
            select(Exercise).where(Exercise.id == exercise_id)
        )
        exercise = q.scalar_one_or_none()

        if not exercise:
            raise HTTPException(404, "Exercise not found")

        # 2. Capture pose via camera
        result = capture_reference_pose(
            exercise_id=exercise_id,
            critical_joints=[
                "left_shoulder", "right_shoulder",
                "left_elbow", "right_elbow",
                "left_hip", "right_hip"
            ],
            angle_map={
                "left_shoulder": ("left_elbow", "left_shoulder", "left_hip"),
                "right_shoulder": ("right_elbow", "right_shoulder", "right_hip"),
                "left_elbow": ("left_shoulder", "left_elbow", "left_wrist"),
                "right_elbow": ("right_shoulder", "right_elbow", "right_wrist")
            }
        )

        if "error" in result:
            raise HTTPException(400, result["error"])

        # 3. Replace existing pose of same type (idempotent)
        existing = await db.execute(
            select(PoseTemplate)
            .where(
                PoseTemplate.exercise_id == exercise_id,
                PoseTemplate.pose_type == pose_type
            )
        )
        existing_pose = existing.scalar_one_or_none()

        if existing_pose:
            await db.delete(existing_pose)
            await db.commit()

        # 4. Save pose template
        pose = PoseTemplate(
            exercise_id=exercise_id,
            pose_type=pose_type,
            joints=result["joints"],
            reference_angles=result["reference_angles"]
        )

        db.add(pose)
        await db.commit()
        await db.refresh(pose)

        return {
            "success": True,
            "pose_type": pose.pose_type,
            "pose_id": pose.id
        }
