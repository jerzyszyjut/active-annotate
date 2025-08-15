from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


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
    active_learning_client_id: Optional[int] = None
    epoch: int = Field(default=0)


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    active_learning_batch_size: Optional[int] = None
    label_config: Optional[str] = None
    description: Optional[str] = None
    annotation_tool_client_id: Optional[int] = None
    storage_id: Optional[int] = None
    active_learning_client_id: Optional[int] = None
    epoch: Optional[int] = None


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
    active_learning_client_id: Optional[int] = None
    epoch: int

    model_config = {"from_attributes": True}
