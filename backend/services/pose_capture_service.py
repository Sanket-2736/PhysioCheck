from sqlalchemy.ext.asyncio import AsyncSession
from database.models import PoseTemplate, PoseType
from pose_tracking_physician import capture_reference_pose


class PoseCaptureService:

    @staticmethod
    async def capture_reference_pose(
        exercise_id: int,
        db: AsyncSession
    ):
        result = capture_reference_pose(
            exercise_id=exercise_id,
            critical_joints=[
                "left_shoulder", "right_shoulder",
                "left_elbow", "right_elbow"
            ],
            angle_map={
                "left_shoulder": ("left_elbow", "left_shoulder", "left_hip"),
                "right_shoulder": ("right_elbow", "right_shoulder", "right_hip")
            }
        )

        if "error" in result:
            return result

        template = PoseTemplate(
            exercise_id=exercise_id,
            pose_type=PoseType.reference,
            joints=result["joints"],
            reference_angles=result["reference_angles"]
        )

        db.add(template)
        await db.commit()

        return {"success": True}
