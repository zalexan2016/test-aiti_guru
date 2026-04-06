-- Сумма товаров по клиентам (Требование 5)
--
-- Запрос возвращает наименование клиента и общую сумму заказанных товаров.
-- Сумма вычисляется как SUM(quantity × price) по всем позициям всех заказов клиента.
-- Используется oi.price (цена, зафиксированная на момент добавления в заказ),
-- а не p.price (текущая цена товара), чтобы отражать реальную стоимость покупок.
-- Результат отсортирован по убыванию общей суммы.

SELECT
    c.name AS customer_name,
    SUM(oi.quantity * oi.price) AS total_amount
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY c.id, c.name
ORDER BY total_amount DESC;
