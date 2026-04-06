from pydantic import BaseModel, Field


class AddItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class AddItemResponse(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    message: str
