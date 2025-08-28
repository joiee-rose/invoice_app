from decimal import Decimal

from sqlmodel import SQLModel, Field

class Service(SQLModel, table=True):
    # auto-incrementing primary key
    id: int | None = Field(default=None, primary_key=True)
    # attributes
    name: str
    description: str | None
    unit_price: Decimal

    def get_formatted_unit_price(self) -> str:
        return f"${self.unit_price:.2f}"