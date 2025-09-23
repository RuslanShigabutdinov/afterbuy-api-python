from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from enum import Enum

class Status(Enum):
    started: str = "Started"
    processing: str = "Processing"
    finished: str = "Finished"


class Task(BaseModel):
    name: Optional[str]
    status: Status = Status.started
    timestamp: datetime = datetime.now()