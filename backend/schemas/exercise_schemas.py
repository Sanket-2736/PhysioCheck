from pydantic import BaseModel
from typing import List
from database.models import DifficultyLevel


class CreateExerciseRequest(BaseModel):
    name: str
    category: str
    difficulty: DifficultyLevel
    target_body_parts: List[str]
