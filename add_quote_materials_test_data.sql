-- 为wanle租户添加报价材料测试数据
-- 首先获取wanle租户的ID
DO $$
DECLARE
    wanle_tenant_id UUID;
    admin_user_id UUID;
BEGIN
    -- 获取wanle租户ID
    SELECT id INTO wanle_tenant_id FROM tenants WHERE name = 'wanle';
    
    -- 获取管理员用户ID（假设是第一个用户）
    SELECT id INTO admin_user_id FROM users LIMIT 1;
    
    -- 如果找到了租户ID，则插入测试数据
    IF wanle_tenant_id IS NOT NULL THEN
        -- 设置搜索路径到wanle schema
        EXECUTE 'SET search_path TO wanle, public';
        
        -- 插入报价材料测试数据
        INSERT INTO quote_materials (
            id, tenant_id, material_name, density, kg_price, 
            layer_1_optional, layer_2_optional, layer_3_optional, layer_4_optional, layer_5_optional,
            sort_order, remarks, is_enabled, created_by, created_at, updated_at
        ) VALUES 
        (
            gen_random_uuid(), wanle_tenant_id, 'PE薄膜', 0.92, 12.50,
            true, true, false, false, false,
            1, '聚乙烯薄膜，适用于包装', true, admin_user_id, NOW(), NOW()
        ),
        (
            gen_random_uuid(), wanle_tenant_id, 'PP薄膜', 0.90, 13.80,
            true, true, true, false, false,
            2, '聚丙烯薄膜，透明度好', true, admin_user_id, NOW(), NOW()
        ),
        (
            gen_random_uuid(), wanle_tenant_id, 'PET薄膜', 1.38, 18.50,
            false, true, true, true, false,
            3, '聚酯薄膜，耐高温', true, admin_user_id, NOW(), NOW()
        ),
        (
            gen_random_uuid(), wanle_tenant_id, 'BOPP薄膜', 0.91, 15.20,
            true, false, true, true, false,
            4, '双向拉伸聚丙烯薄膜', true, admin_user_id, NOW(), NOW()
        ),
        (
            gen_random_uuid(), wanle_tenant_id, 'CPP薄膜', 0.90, 14.60,
            true, true, false, true, true,
            5, '流延聚丙烯薄膜', true, admin_user_id, NOW(), NOW()
        ),
        (
            gen_random_uuid(), wanle_tenant_id, 'PA薄膜', 1.14, 22.30,
            false, false, true, true, true,
            6, '尼龙薄膜，阻隔性好', true, admin_user_id, NOW(), NOW()
        ),
        (
            gen_random_uuid(), wanle_tenant_id, 'EVOH薄膜', 1.19, 35.80,
            false, false, false, true, true,
            7, '乙烯-乙烯醇共聚物薄膜', true, admin_user_id, NOW(), NOW()
        ),
        (
            gen_random_uuid(), wanle_tenant_id, 'AL箔', 2.70, 45.60,
            false, false, false, false, true,
            8, '铝箔，阻隔性极佳', true, admin_user_id, NOW(), NOW()
        ),
        (
            gen_random_uuid(), wanle_tenant_id, '纸张', 0.80, 8.90,
            true, false, false, false, false,
            9, '包装纸张', true, admin_user_id, NOW(), NOW()
        ),
        (
            gen_random_uuid(), wanle_tenant_id, '胶水', 1.05, 25.00,
            false, false, false, false, false,
            10, '复合胶水', true, admin_user_id, NOW(), NOW()
        );
        
        RAISE NOTICE '成功为wanle租户添加了10条报价材料测试数据';
    ELSE
        RAISE NOTICE '未找到wanle租户，请先创建租户';
    END IF;
END $$; 