from pydantic import BaseModel

class CustomerBase(BaseModel):
    name: str
    email: str
    phone_number: str
    address: str

class CustomerCreate(CustomerBase):
    pass

class CustomerRead(CustomerBase):
    id: int

    class Config:
        orm_mode = True