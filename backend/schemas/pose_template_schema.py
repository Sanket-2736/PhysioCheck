from pydantic import BaseModel
from database.models import PoseType
from enum import Enum


class CapturePoseRequest(BaseModel):
    pose_type: PoseType
