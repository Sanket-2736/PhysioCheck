from pydantic import BaseModel
from typing import Dict, List


class FrameData(BaseModel):
    timestamp: float
    joints: Dict[str, Dict[str, float]]
    angles: Dict[str, float]


class RepCaptureRequest(BaseModel):
    frames: List[FrameData]
