from typing import Any
from datetime import date

from sqlmodel import SQLModel, Field, Column, JSON

class Invoice(SQLModel, table=True):
    # auto-incrementing primary key
    id: int | None = Field(default=None, primary_key=True)
    # foreign key to client table
    client_id: int = Field(foreign_key="client.id")
    # attributes
    invoice_no: str | None
    issue_date: date | None = Field(default_factory=date.today)
    pdf_html: Any = Field(sa_column=Column(JSON))

    def get_formatted_invoice_no(self) -> str:
        return f"{str(self.id).zfill(4)}"