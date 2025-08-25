from pydantic import BaseModel
from typing import Optional

class UpdateResponse(BaseModel):
    status: str
    message: str
    file_size: Optional[int] = None
    reindexed: Optional[bool] = None