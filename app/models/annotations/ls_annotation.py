from sqlmodel import SQLModel, Field, UniqueConstraint


class LSAnnotation(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("url", "ls_project_id"),
    )

    id: int = Field(primary_key=True, foreign_key="annotation.id")
    url: str = Field(max_length=200)
    ls_project_id: int = Field()
    api_key: str = Field(max_length=1000) # unencrypted for now
