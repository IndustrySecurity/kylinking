-- 在wanle租户schema中创建材料分类表
SET search_path TO wanle, public;

CREATE TABLE IF NOT EXISTS material_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 基本信息
    material_name VARCHAR(100) NOT NULL,
    material_type VARCHAR(20) NOT NULL CHECK (material_type IN ('主材', '辅材')),
    
    -- 单位信息
    base_unit_id UUID,
    auxiliary_unit_id UUID,
    sales_unit_id UUID,
    
    -- 物理属性
    density NUMERIC(10, 4),
    square_weight NUMERIC(10, 4),
    shelf_life INTEGER,
    
    -- 检验质量
    inspection_standard VARCHAR(200),
    quality_grade VARCHAR(100),
    
    -- 价格信息
    latest_purchase_price NUMERIC(15, 4),
    sales_price NUMERIC(15, 4),
    product_quote_price NUMERIC(15, 4),
    cost_price NUMERIC(15, 4),
    
    -- 业务配置
    show_on_kanban BOOLEAN DEFAULT FALSE,
    account_subject VARCHAR(100),
    code_prefix VARCHAR(10) DEFAULT 'M',
    warning_days INTEGER,
    
    -- 纸箱参数
    carton_param1 NUMERIC(10, 3),
    carton_param2 NUMERIC(10, 3),
    carton_param3 NUMERIC(10, 3),
    carton_param4 NUMERIC(10, 3),
    
    -- 材料属性标识
    enable_batch BOOLEAN DEFAULT FALSE,
    enable_barcode BOOLEAN DEFAULT FALSE,
    is_ink BOOLEAN DEFAULT FALSE,
    is_accessory BOOLEAN DEFAULT FALSE,
    is_consumable BOOLEAN DEFAULT FALSE,
    is_recyclable BOOLEAN DEFAULT FALSE,
    is_hazardous BOOLEAN DEFAULT FALSE,
    is_imported BOOLEAN DEFAULT FALSE,
    is_customized BOOLEAN DEFAULT FALSE,
    is_seasonal BOOLEAN DEFAULT FALSE,
    is_fragile BOOLEAN DEFAULT FALSE,
    is_perishable BOOLEAN DEFAULT FALSE,
    is_temperature_sensitive BOOLEAN DEFAULT FALSE,
    is_moisture_sensitive BOOLEAN DEFAULT FALSE,
    is_light_sensitive BOOLEAN DEFAULT FALSE,
    requires_special_storage BOOLEAN DEFAULT FALSE,
    requires_certification BOOLEAN DEFAULT FALSE,
    
    -- 通用字段
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_material_categories_name ON material_categories(material_name);
CREATE INDEX IF NOT EXISTS idx_material_categories_type ON material_categories(material_type);
CREATE INDEX IF NOT EXISTS idx_material_categories_active ON material_categories(is_active);
CREATE INDEX IF NOT EXISTS idx_material_categories_order ON material_categories(display_order);

-- 添加注释
COMMENT ON TABLE material_categories IS '材料分类表';
COMMENT ON COLUMN material_categories.material_name IS '材料分类名称';
COMMENT ON COLUMN material_categories.material_type IS '材料属性(主材/辅材)';
COMMENT ON COLUMN material_categories.base_unit_id IS '基本单位ID';
COMMENT ON COLUMN material_categories.auxiliary_unit_id IS '辅助单位ID';
COMMENT ON COLUMN material_categories.sales_unit_id IS '销售单位ID';
COMMENT ON COLUMN material_categories.density IS '密度';
COMMENT ON COLUMN material_categories.square_weight IS '平方克重';
COMMENT ON COLUMN material_categories.shelf_life IS '保质期(天)';
COMMENT ON COLUMN material_categories.inspection_standard IS '检验标准';
COMMENT ON COLUMN material_categories.quality_grade IS '质量等级';
COMMENT ON COLUMN material_categories.latest_purchase_price IS '最近采购价';
COMMENT ON COLUMN material_categories.sales_price IS '销售价';
COMMENT ON COLUMN material_categories.product_quote_price IS '产品报价';
COMMENT ON COLUMN material_categories.cost_price IS '成本价格';
COMMENT ON COLUMN material_categories.show_on_kanban IS '看板显示';
COMMENT ON COLUMN material_categories.account_subject IS '科目';
COMMENT ON COLUMN material_categories.code_prefix IS '编码前缀';
COMMENT ON COLUMN material_categories.warning_days IS '预警天数';
COMMENT ON COLUMN material_categories.display_order IS '显示排序';
COMMENT ON COLUMN material_categories.is_active IS '是否启用';
COMMENT ON COLUMN material_categories.created_by IS '创建人';
COMMENT ON COLUMN material_categories.updated_by IS '修改人';

-- 插入一些测试数据
INSERT INTO material_categories (
    material_name, material_type, display_order, is_active, created_by
) VALUES 
    ('BOPP薄膜', '主材', 1, TRUE, (SELECT id FROM public.users WHERE username = 'admin' LIMIT 1)),
    ('PE薄膜', '主材', 2, TRUE, (SELECT id FROM public.users WHERE username = 'admin' LIMIT 1)),
    ('油墨', '辅材', 3, TRUE, (SELECT id FROM public.users WHERE username = 'admin' LIMIT 1)),
    ('胶水', '辅材', 4, TRUE, (SELECT id FROM public.users WHERE username = 'admin' LIMIT 1))
ON CONFLICT DO NOTHING; 