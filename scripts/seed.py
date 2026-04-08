"""Seed database with sample data matching the technical specification."""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from random import randint

from sqlalchemy import select

from app.config import DATABASE_URL  # noqa: F401
from app.database import async_session
from app.models import Category, Customer, Order, OrderItem, Product, ProductCategory


async def seed():
    async with async_session() as db:
        # Check if data already exists
        result = await db.execute(select(Category).limit(1))
        if result.scalar_one_or_none() is not None:
            print("Database already seeded, skipping.")
            return

        # --- Categories (tree from TZ) ---
        appliances = Category(name="Бытовая техника")
        db.add(appliances)
        await db.flush()

        washing = Category(name="Стиральные машины", parent_id=appliances.id)
        fridges = Category(name="Холодильники", parent_id=appliances.id)
        tvs = Category(name="Телевизоры", parent_id=appliances.id)
        db.add_all([washing, fridges, tvs])
        await db.flush()

        single_chamber = Category(name="Однокамерные", parent_id=fridges.id)
        double_chamber = Category(name="Двухкамерные", parent_id=fridges.id)
        db.add_all([single_chamber, double_chamber])
        await db.flush()

        computers = Category(name="Компьютеры")
        db.add(computers)
        await db.flush()

        laptops = Category(name="Ноутбуки", parent_id=computers.id)
        monoblocks = Category(name="Моноблоки", parent_id=computers.id)
        db.add_all([laptops, monoblocks])
        await db.flush()

        laptops_17 = Category(name='17"', parent_id=laptops.id)
        laptops_19 = Category(name='19"', parent_id=laptops.id)
        db.add_all([laptops_17, laptops_19])
        await db.flush()

        # --- Products ---
        products = [
            Product(name="Стиральная машина Samsung WW60", stock=15, price=Decimal("32999.99")),
            Product(name="Холодильник Beko RCSK270", stock=10, price=Decimal("24500.00")),
            Product(name="Холодильник LG GA-B509", stock=8, price=Decimal("45990.00")),
            Product(name="Телевизор Samsung UE43", stock=20, price=Decimal("29990.00")),
            Product(name="Ноутбук ASUS VivoBook 17", stock=12, price=Decimal("54990.00")),
            Product(name="Ноутбук Lenovo IdeaPad 19", stock=7, price=Decimal("67990.00")),
            Product(name="Моноблок HP All-in-One", stock=5, price=Decimal("79990.00")),
        ]
        db.add_all(products)
        await db.flush()

        # --- Product-Category links (many-to-many) ---
        links = [
            ProductCategory(product_id=products[0].id, category_id=washing.id),
            ProductCategory(product_id=products[1].id, category_id=single_chamber.id),
            ProductCategory(product_id=products[2].id, category_id=double_chamber.id),
            ProductCategory(product_id=products[3].id, category_id=tvs.id),
            ProductCategory(product_id=products[4].id, category_id=laptops_17.id),
            ProductCategory(product_id=products[5].id, category_id=laptops_19.id),
            ProductCategory(product_id=products[6].id, category_id=monoblocks.id),
        ]
        db.add_all(links)

        # --- Customers ---
        customers = [
            Customer(name="ООО Альфа", address="г. Москва, ул. Ленина, д. 1"),
            Customer(name="ИП Иванов", address="г. Санкт-Петербург, пр. Невский, д. 50"),
            Customer(name="ООО Бета", address="г. Новосибирск, ул. Красный проспект, д. 10"),
        ]
        db.add_all(customers)
        await db.flush()

        # --- Orders (some in current month, some in previous) ---
        now = datetime.utcnow()
        last_month = now - timedelta(days=35)

        orders = [
            Order(customer_id=customers[0].id, created_at=now - timedelta(days=2)),
            Order(customer_id=customers[0].id, created_at=last_month),
            Order(customer_id=customers[1].id, created_at=now - timedelta(days=5)),
            Order(customer_id=customers[2].id, created_at=now - timedelta(days=1)),
            Order(customer_id=customers[2].id, created_at=last_month - timedelta(days=3)),
        ]
        db.add_all(orders)
        await db.flush()

        # --- Order Items ---
        items = [
            # Order 1 (Альфа, current month)
            OrderItem(order_id=orders[0].id, product_id=products[0].id, quantity=2, price=products[0].price),
            OrderItem(order_id=orders[0].id, product_id=products[3].id, quantity=3, price=products[3].price),
            # Order 2 (Альфа, last month)
            OrderItem(order_id=orders[1].id, product_id=products[4].id, quantity=1, price=products[4].price),
            # Order 3 (Иванов, current month)
            OrderItem(order_id=orders[2].id, product_id=products[1].id, quantity=2, price=products[1].price),
            OrderItem(order_id=orders[2].id, product_id=products[5].id, quantity=1, price=products[5].price),
            # Order 4 (Бета, current month)
            OrderItem(order_id=orders[3].id, product_id=products[3].id, quantity=5, price=products[3].price),
            OrderItem(order_id=orders[3].id, product_id=products[6].id, quantity=1, price=products[6].price),
            # Order 5 (Бета, last month)
            OrderItem(order_id=orders[4].id, product_id=products[2].id, quantity=3, price=products[2].price),
        ]
        db.add_all(items)

        await db.commit()
        print("Database seeded successfully!")
        print(f"  Categories: 11")
        print(f"  Products: {len(products)}")
        print(f"  Customers: {len(customers)}")
        print(f"  Orders: {len(orders)}")
        print(f"  Order items: {len(items)}")


if __name__ == "__main__":
    asyncio.run(seed())
