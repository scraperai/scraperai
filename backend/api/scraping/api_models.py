from typing import Optional

from pydantic import BaseModel, Field


class TaskInitForm(BaseModel):
    urls: Optional[list[str]]
