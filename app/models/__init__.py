from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class DatapointStatus(str, Enum):
    PENDING = "pending"
    ANNOTATED = "annotated"
    SKIPPED = "skipped"
    REVIEWED = "reviewed"


class AnnotationSource(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    IMPORTED = "imported"


# Base models for shared properties
class ProjectBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=200)
    active_learning_batch_size: int = Field(default=10, ge=1, le=1000)
    description: Optional[str] = Field(default=None, max_length=1000)


class DatapointBase(SQLModel):
    value: str = Field(max_length=10000)
    status: DatapointStatus = Field(default=DatapointStatus.PENDING)


class AnnotationBase(SQLModel):
    value: str = Field(max_length=10000)
    source: AnnotationSource = Field(default=AnnotationSource.MANUAL)


class ModelBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=200)
    weights: Optional[str] = Field(default=None, max_length=10000)
    model_type: Optional[str] = Field(default=None, max_length=100)


class ALMethodBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    parameters: Optional[str] = Field(default=None, max_length=5000)  # JSON string


class AnnotationServiceBase(SQLModel):
    api_endpoint: str = Field(max_length=500)
    webhook_url: Optional[str] = Field(default=None, max_length=500)
    service_type: str = Field(max_length=100)
    configuration: Optional[str] = Field(default=None, max_length=5000)  # JSON string


# Database models (tables)
class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    datapoints: List["Datapoint"] = Relationship(back_populates="project")
    models: List["Model"] = Relationship(back_populates="project")
    al_methods: List["ALMethod"] = Relationship(back_populates="project")
    annotation_service_id: Optional[int] = Field(default=None, foreign_key="annotationservice.id")
    annotation_service: Optional["AnnotationService"] = Relationship()


class Datapoint(DatapointBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Foreign keys
    project_id: int = Field(foreign_key="project.id")
    
    # Relationships
    project: Project = Relationship(back_populates="datapoints")
    annotations: List["Annotation"] = Relationship(back_populates="datapoint")


class Annotation(AnnotationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="created")
    updated_at: Optional[datetime] = Field(default=None)
    
    # Foreign keys
    datapoint_id: int = Field(foreign_key="datapoint.id")
    
    # Relationships
    datapoint: Datapoint = Relationship(back_populates="annotations")


class Model(ModelBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Foreign keys
    project_id: int = Field(foreign_key="project.id")
    
    # Relationships
    project: Project = Relationship(back_populates="models")


class ALMethod(ALMethodBase, table=True):
    __tablename__ = "almethod"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Foreign keys
    project_id: int = Field(foreign_key="project.id")
    
    # Relationships
    project: Project = Relationship(back_populates="al_methods")


class AnnotationService(AnnotationServiceBase, table=True):
    __tablename__ = "annotationservice"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


# API models for requests and responses
class ProjectCreate(ProjectBase):
    annotation_service_id: Optional[int] = None


class ProjectUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    active_learning_batch_size: Optional[int] = Field(default=None, ge=1, le=1000)
    description: Optional[str] = Field(default=None, max_length=1000)
    annotation_service_id: Optional[int] = None


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    annotation_service_id: Optional[int] = None


class DatapointCreate(DatapointBase):
    project_id: int


class DatapointUpdate(SQLModel):
    value: Optional[str] = Field(default=None, max_length=10000)
    status: Optional[DatapointStatus] = None


class DatapointRead(DatapointBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class AnnotationCreate(AnnotationBase):
    datapoint_id: int


class AnnotationUpdate(SQLModel):
    value: Optional[str] = Field(default=None, max_length=10000)
    source: Optional[AnnotationSource] = None


class AnnotationRead(AnnotationBase):
    id: int
    datapoint_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ModelCreate(ModelBase):
    project_id: int


class ModelUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    weights: Optional[str] = Field(default=None, max_length=10000)
    model_type: Optional[str] = Field(default=None, max_length=100)


class ModelRead(ModelBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ALMethodCreate(ALMethodBase):
    project_id: int


class ALMethodUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    parameters: Optional[str] = Field(default=None, max_length=5000)


class ALMethodRead(ALMethodBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class AnnotationServiceCreate(AnnotationServiceBase):
    pass


class AnnotationServiceUpdate(SQLModel):
    api_endpoint: Optional[str] = Field(default=None, max_length=500)
    webhook_url: Optional[str] = Field(default=None, max_length=500)
    service_type: Optional[str] = Field(default=None, max_length=100)
    configuration: Optional[str] = Field(default=None, max_length=5000)


class AnnotationServiceRead(AnnotationServiceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
