from sqlmodel import SQLModel, Field

class Client(SQLModel, table=True):
    # auto-incrementing primary key
    id: int | None = Field(default=None, primary_key=True)
    # attributes
    name: str
    business_name: str
    street_address: str
    city: str
    state: str
    zip_code: str
    email: str
    phone: str

    def get_billing_address(self) -> str:
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"