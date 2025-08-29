from typing import Any
from datetime import date

from sqlmodel import SQLModel, Field, Column, JSON

class Quote(SQLModel, table=True):
    # auto-incrementing primary key
    id: int | None = Field(default=None, primary_key=True)
    # foreign key to client table (1:M relationship)
    client_id: int = Field(foreign_key="client.id")
    # attributes
    quote_no: str
    issue_date: date | None = Field(default_factory=date.today)
    pdf_html: Any = Field(sa_column=Column(JSON))