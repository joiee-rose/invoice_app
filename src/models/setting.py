from typing import Any

from sqlmodel import SQLModel, Field, Column, JSON

class AppSetting(SQLModel, table=True):
    # primary key
    id: str = Field(primary_key=True)
    # attributes
    category: str
    setting_name: str
    setting_value: Any = Field(sa_column=Column(JSON))