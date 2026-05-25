from pydantic import BaseModel, Field


class WriteFileRequest(BaseModel):

    path: str = Field(
        min_length=1,
        max_length=255
    )

    content: str

    overwrite: bool = False