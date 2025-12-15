from pydantic import BaseModel

class AssignExerciseRequest(BaseModel):
    patient_id: int
    exercise_id: int
    sets: int = 3
    reps: int = 10
    frequency_per_day: int = 1
