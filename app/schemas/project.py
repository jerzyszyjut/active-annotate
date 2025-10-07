from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional


CLS_LABEL_CONFIG = """
    <View>
        <Image name="image" value="$image"/>
        <Choices name="choice" toName="image">
            <Choice value="Adult content"/>
            <Choice value="Weapons" />
            <Choice value="Violence" />
        </Choices>
    </View>
"""


class ProjectCreate(BaseModel):
    name: str
    active_learning_batch_size: int
    label_config: str = CLS_LABEL_CONFIG
    description: Optional[str] = None
    annotation_tool_client_id: Optional[int] = None
    storage_id: Optional[int] = None
    epoch: int = Field(default=0)
    max_epochs: int = Field(ge=1)
    ml_backend_url: Optional[str] = None
    annotated_image_paths: Optional[list[str]] = None
    method: Literal["least_confidence", "entropy", "margin"] = "least_confidence"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    active_learning_batch_size: Optional[int] = None
    label_config: Optional[str] = None
    description: Optional[str] = None
    annotation_tool_client_id: Optional[int] = None
    storage_id: Optional[int] = None
    epoch: Optional[int] = None
    max_epochs: Optional[int] = None
    ml_backend_url: Optional[str] = None
    annotated_image_paths: Optional[list[str]] = None
    method: Optional[Literal["least_confidence", "entropy", "margin"]] = None


class ProjectRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    name: str
    active_learning_batch_size: int
    label_config: str
    description: Optional[str] = None
    annotation_tool_client_id: Optional[int] = None
    storage_id: Optional[int] = None
    epoch: int
    max_epochs: int
    ml_backend_url: Optional[str] = None
    annotated_image_paths: Optional[list[str]] = None
    method: Literal["least_confidence", "entropy", "margin"]

    model_config = {"from_attributes": True}
