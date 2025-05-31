-- 直接在wanle schema中添加报价材料测试数据
SET search_path TO wanle, public;

-- 插入报价材料测试数据
INSERT INTO quote_materials (
    id, tenant_id, material_name, density, kg_price, 
    layer_1_optional, layer_2_optional, layer_3_optional, layer_4_optional, layer_5_optional,
    sort_order, remarks, is_enabled, created_by, created_at, updated_at
) VALUES 
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', 'PE薄膜', 0.92, 12.50,
    true, true, false, false, false,
    1, '聚乙烯薄膜，适用于包装', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', 'PP薄膜', 0.90, 13.80,
    true, true, true, false, false,
    2, '聚丙烯薄膜，透明度好', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', 'PET薄膜', 1.38, 18.50,
    false, true, true, true, false,
    3, '聚酯薄膜，耐高温', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', 'BOPP薄膜', 0.91, 15.20,
    true, false, true, true, false,
    4, '双向拉伸聚丙烯薄膜', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', 'CPP薄膜', 0.90, 14.60,
    true, true, false, true, true,
    5, '流延聚丙烯薄膜', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', 'PA薄膜', 1.14, 22.30,
    false, false, true, true, true,
    6, '尼龙薄膜，阻隔性好', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', 'EVOH薄膜', 1.19, 35.80,
    false, false, false, true, true,
    7, '乙烯-乙烯醇共聚物薄膜', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', 'AL箔', 2.70, 45.60,
    false, false, false, false, true,
    8, '铝箔，阻隔性极佳', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '纸张', 0.80, 8.90,
    true, false, false, false, false,
    9, '包装纸张', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
),
(
    gen_random_uuid(), '14753072-f3d1-44aa-8b76-173d9120270b', '胶水', 1.05, 25.00,
    false, false, false, false, false,
    10, '复合胶水', true, '14753072-f3d1-44aa-8b76-173d9120270b', NOW(), NOW()
);

SELECT '成功添加了 ' || COUNT(*) || ' 条报价材料测试数据' AS result FROM quote_materials; 