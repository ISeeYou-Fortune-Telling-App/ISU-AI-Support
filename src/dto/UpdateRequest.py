from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile

class UpdateRequest(BaseModel):
    """
    Request model cho việc cập nhật data files
    """
    file: UploadFile  # File được upload để thay thế data
    force_reindex: Optional[bool] = True  # Có tự động reindex sau khi update không