from pydantic import BaseModel

class SubscribeRequest(BaseModel):
    physician_id: int
