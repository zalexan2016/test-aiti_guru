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
    """Добавить товар в заказ (upsert) с проверкой наличия и списанием со склада."""

    # 1. Проверить существование заказа
    order = await db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=404,
            detail=f"Заказ с id={order_id} не найден",
        )

    # 2. Получить товар с блокировкой строки (SELECT ... FOR UPDATE)
    stmt = select(Product).where(Product.id == product_id).with_for_update()
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Товар с id={product_id} не найден",
        )

    # 3. Проверить наличие на складе
    if product.stock < quantity:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Недостаточно товара на складе. "
                f"Доступно: {product.stock}, запрошено: {quantity}"
            ),
        )

    # 4. Upsert позиции заказа
    stmt = (
        select(OrderItem)
        .where(OrderItem.order_id == order_id, OrderItem.product_id == product_id)
    )
    result = await db.execute(stmt)
    existing_item = result.scalar_one_or_none()

    if existing_item is not None:
        existing_item.quantity += quantity
        message = "Позиция обновлена"
        result_quantity = existing_item.quantity
    else:
        new_item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=product.price,
        )
        db.add(new_item)
        message = "Позиция добавлена"
        result_quantity = quantity

    # 5. Списать со склада
    product.stock -= quantity

    # 6. Commit транзакции
    await db.commit()

    return AddItemResponse(
        order_id=order_id,
        product_id=product_id,
        quantity=result_quantity,
        message=message,
    )
