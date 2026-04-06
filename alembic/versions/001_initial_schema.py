"""Initial schema — all tables, indexes, constraints

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- categories ---
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "parent_id",
            sa.Integer(),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index("idx_categories_parent_id", "categories", ["parent_id"])

    # --- products ---
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
    )
    op.create_check_constraint(
        "ck_products_stock_non_negative", "products", "stock >= 0"
    )
    op.create_check_constraint(
        "ck_products_price_positive", "products", "price > 0"
    )

    # --- product_categories ---
    op.create_table(
        "product_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("categories.id"),
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        "uq_product_category", "product_categories", ["product_id", "category_id"]
    )

    # --- customers ---
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
    )

    # --- orders ---
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "customer_id",
            sa.Integer(),
            sa.ForeignKey("customers.id"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("idx_orders_customer_id", "orders", ["customer_id"])
    op.create_index("idx_orders_created_at", "orders", ["created_at"])

    # --- order_items ---
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
    )
    op.create_check_constraint(
        "ck_order_items_quantity_positive", "order_items", "quantity > 0"
    )
    op.create_check_constraint(
        "ck_order_items_price_positive", "order_items", "price > 0"
    )
    op.create_unique_constraint(
        "uq_order_item", "order_items", ["order_id", "product_id"]
    )
    op.create_index("idx_order_items_order_id", "order_items", ["order_id"])
    op.create_index("idx_order_items_product_id", "order_items", ["product_id"])


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("customers")
    op.drop_table("product_categories")
    op.drop_table("products")
    op.drop_table("categories")
