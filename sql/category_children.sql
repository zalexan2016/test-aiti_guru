-- Количество дочерних категорий первого уровня (Требование 6)
--
-- Запрос возвращает для каждой категории количество её непосредственных
-- дочерних категорий (первый уровень вложенности).
-- LEFT JOIN гарантирует, что листовые категории (без дочерних элементов)
-- также включены в результат со значением children_count = 0.
-- Результат отсортирован по идентификатору категории.

SELECT
    c.id,
    c.name,
    COUNT(child.id) AS children_count
FROM categories c
LEFT JOIN categories child ON child.parent_id = c.id
GROUP BY c.id, c.name
ORDER BY c.id;
