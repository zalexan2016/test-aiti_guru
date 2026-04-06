-- VIEW «Топ-5 товаров за последний месяц» (Требование 7)
--
-- Представление возвращает пять товаров с наибольшим суммарным количеством
-- проданных штук за последний календарный месяц.
-- Рекурсивный CTE (category_root) поднимается по дереву категорий от категории
-- товара до корневой категории (parent_id IS NULL), чтобы определить категорию
-- первого уровня для каждого товара.
-- Фильтрация заказов: >= начало прошлого месяца AND < начало текущего месяца.
-- Поля: наименование товара, наименование корневой категории, общее количество проданных штук.
-- Результат отсортирован по убыванию total_sold, ограничен 5 записями.

CREATE OR REPLACE VIEW top5_products_last_month AS
WITH RECURSIVE category_root AS (
    -- Базовый случай: категории, привязанные к товарам
    SELECT pc.product_id, cat.id AS category_id, cat.parent_id
    FROM product_categories pc
    JOIN categories cat ON cat.id = pc.category_id

    UNION ALL

    -- Рекурсивный шаг: поднимаемся к корню
    SELECT cr.product_id, parent.id AS category_id, parent.parent_id
    FROM category_root cr
    JOIN categories parent ON parent.id = cr.parent_id
    WHERE cr.parent_id IS NOT NULL
)
SELECT
    p.name AS product_name,
    root_cat.name AS root_category_name,
    SUM(oi.quantity) AS total_sold
FROM order_items oi
JOIN orders o ON o.id = oi.order_id
JOIN products p ON p.id = oi.product_id
LEFT JOIN (
    SELECT DISTINCT product_id, category_id
    FROM category_root
    WHERE parent_id IS NULL
) pr ON pr.product_id = p.id
LEFT JOIN categories root_cat ON root_cat.id = pr.category_id
WHERE o.created_at >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month'
  AND o.created_at < date_trunc('month', CURRENT_DATE)
GROUP BY p.id, p.name, root_cat.name
ORDER BY total_sold DESC
LIMIT 5;
