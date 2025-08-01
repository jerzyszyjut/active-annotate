from sqlmodel import SQLModel, Field


class LocalStorage(SQLModel, table=True):
    id: int = Field(primary_key=True, foreign_key="storage.id")
    path: str = Field(min_length=1, max_length=1000)



