from fastapi import APIRouter, Response

from app.database import async_session
from app.schemas import AddItemRequest, AddItemResponse
from app.services.order_service import add_item_to_order

router = APIRouter()


@router.post("/orders/items", response_model=AddItemResponse)
async def post_add_item(
    body: AddItemRequest,
    response: Response,
) -> AddItemResponse:
    session = async_session()
    try:
        result = await add_item_to_order(
            session, body.order_id, body.product_id, body.quantity
        )
        if result.message == "Item added":
            response.status_code = 201
        else:
            response.status_code = 200
        return result
    finally:
        await session.close()
