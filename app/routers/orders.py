from fastapi import APIRouter, Response

from app.database import async_session
from app.schemas import AddItemRequest, AddItemResponse
from app.services.order_service import add_item_to_order

router = APIRouter()


@router.post("/orders/{order_id}/items", response_model=AddItemResponse)
async def post_add_item(
    order_id: int,
    body: AddItemRequest,
    response: Response,
):
    session = async_session()
    try:
        result = await add_item_to_order(
            session, order_id, body.product_id, body.quantity
        )
        if result.message == "Позиция добавлена":
            response.status_code = 201
        else:
            response.status_code = 200
        return result
    finally:
        await session.close()
