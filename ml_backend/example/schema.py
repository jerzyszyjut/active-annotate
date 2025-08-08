from pydantic import BaseModel
from typing import Optional


class TrainResponse(BaseModel):
    message: str
    status: str
    task_id: Optional[str] = None
