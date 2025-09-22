from typing import List, Dict, Any
from decimal import Decimal

from sqlmodel import SQLModel, Field, Column, JSON

class ClientQuoteProfile(SQLModel, table=True):
    # primary key is a foreign key to client table (1:1 relationship)
    client_id: int | None = Field(default=None, primary_key=True, foreign_key="client.id")
    # attributes
    min_monthly_charge: Decimal
    premium_salt_upcharge: Decimal
    services: List[Dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    grand_total: Decimal

class TempClientQuoteProfile(SQLModel, table=True):
    # primary key is a foreign key to client table (1:1 relationship)
    client_id: int | None = Field(default=None, primary_key=True, foreign_key="client.id")
    # attributes
    min_monthly_charge: Decimal
    premium_salt_upcharge: Decimal
    services: List[Dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    grand_total: Decimal