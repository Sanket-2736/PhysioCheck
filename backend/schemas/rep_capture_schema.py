from pydantic import BaseModel
from typing import Dict, List

class AssignExerciseRequest(BaseModel):
    exercise_id: int
    sets: int
    reps: int
    frequency_per_day: int

class FrameData(BaseModel):
    timestamp: float
    joints: Dict[str, Dict[str, float]]
    angles: Dict[str, float]


class RepCaptureRequest(BaseModel):
    frames: List[FrameData]
