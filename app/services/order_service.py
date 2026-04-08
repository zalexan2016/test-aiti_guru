from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order, OrderItem, Product
from app.schemas import AddItemResponse


async def add_item_to_order(
    db: AsyncSession,
    order_id: int,
    product_id: int,
    quantity: int,
) -> AddItemResponse:
    """Add product to order (upsert) with stock check and deduction."""

    # 1. Check order exists
    order = await db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=404,
            detail=f"Order with id={order_id} not found",
        )

    # 2. Get product with row lock (SELECT ... FOR UPDATE)
    stmt = select(Product).where(Product.id == product_id).with_for_update()
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id={product_id} not found",
        )

    # 3. Check stock availability
    if product.stock < quantity:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Not enough stock. "
                f"Available: {product.stock}, requested: {quantity}"
            ),
        )

    # 4. Upsert order item
    stmt = (
        select(OrderItem)
        .where(OrderItem.order_id == order_id, OrderItem.product_id == product_id)
    )
    result = await db.execute(stmt)
    existing_item = result.scalar_one_or_none()

    if existing_item is not None:
        existing_item.quantity += quantity
        message = "Item updated"
        result_quantity = existing_item.quantity
    else:
        new_item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=product.price,
        )
        db.add(new_item)
        message = "Item added"
        result_quantity = quantity

    # 5. Deduct from stock
    product.stock -= quantity

    # 6. Commit transaction
    await db.commit()

    return AddItemResponse(
        order_id=order_id,
        product_id=product_id,
        quantity=result_quantity,
        message=message,
    )
