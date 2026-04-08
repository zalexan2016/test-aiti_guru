-- VIEW «Топ-5 товаров за последний месяц» (Требование 7)
--
-- Представление возвращает пять товаров с наибольшим суммарным количеством
-- проданных штук за последние 30 дней.
-- Рекурсивный CTE (category_path) поднимается по дереву категорий от категории
-- товара до корневой категории (parent_id IS NULL), чтобы определить категорию
-- первого уровня для каждого товара.
-- Поля: наименование товара, наименование корневой категории, общее количество проданных штук.
-- Результат отсортирован по убыванию total_sold, ограничен 5 записями.

CREATE OR REPLACE VIEW top5_products_last_month AS
WITH RECURSIVE category_path AS (
    -- Базовый случай: начинаем с категорий, привязанных к товарам
    SELECT
        pc.product_id,
        cat.id AS current_id,
        cat.parent_id
    FROM product_categories pc
    JOIN categories cat ON cat.id = pc.category_id

    UNION

    -- Рекурсивный шаг: поднимаемся к родителю (только если parent_id не NULL)
    SELECT
        cp.product_id,
        parent.id AS current_id,
        parent.parent_id
    FROM category_path cp
    JOIN categories parent ON parent.id = cp.parent_id
),
product_root AS (
    -- Выбираем корневую категорию (parent_id IS NULL) для каждого товара
    SELECT DISTINCT product_id, current_id AS root_category_id
    FROM category_path
    WHERE parent_id IS NULL
)
SELECT
    p.name AS product_name,
    root_cat.name AS root_category_name,
    SUM(oi.quantity) AS total_sold
FROM order_items oi
JOIN orders o ON o.id = oi.order_id
JOIN products p ON p.id = oi.product_id
LEFT JOIN product_root pr ON pr.product_id = p.id
LEFT JOIN categories root_cat ON root_cat.id = pr.root_category_id
WHERE o.created_at >= NOW() - INTERVAL '1 month'
GROUP BY p.id, p.name, root_cat.name
ORDER BY total_sold DESC
LIMIT 5;

-- Выборка данных из представления
SELECT * FROM top5_products_last_month;
