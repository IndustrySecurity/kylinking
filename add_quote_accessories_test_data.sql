-- 直接在wanle schema中添加报价辅材测试数据
SET search_path TO wanle, public;

-- 插入报价辅材测试数据
INSERT INTO quote_accessories (
    id, tenant_id, material_name, unit_price, unit_price_formula,
    sort_order, description, is_enabled, created_by, created_at, updated_at
) VALUES 
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '制版费', 150.00, '固定单价',
    1, '制版费用，按版计算', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '开机费', 80.00, '固定单价',
    2, '开机费用，按次计算', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '分切费', 0.02, '按长度计算',
    3, '分切费用，按米计算', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '复合费', 0.15, '按面积计算',
    4, '复合费用，按平方米计算', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '印刷费', 0.08, '按面积计算',
    5, '印刷费用，按平方米计算', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '制袋费', 0.05, '按数量计算',
    6, '制袋费用，按个计算', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '包装费', 0.03, '按重量计算',
    7, '包装费用，按公斤计算', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '运输费', 0.50, '自定义公式',
    8, '运输费用，根据距离和重量计算', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '质检费', 20.00, '固定单价',
    9, '质检费用，按批次计算', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '仓储费', 0.01, '按重量计算',
    10, '仓储费用，按公斤天计算', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
);

SELECT '成功添加了 ' || COUNT(*) || ' 条报价辅材测试数据' AS result FROM quote_accessories; 