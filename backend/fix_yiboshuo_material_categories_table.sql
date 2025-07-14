-- 修正yiboshuo material_categories表结构
-- 使其与MaterialCategory模型定义一致

-- 1. 删除现有的material_categories表 (CASCADE会自动处理外键依赖)
DROP TABLE IF EXISTS yiboshuo.material_categories CASCADE;

-- 2. 重新创建material_categories表，使用正确的结构
CREATE TABLE yiboshuo.material_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 基本信息
    material_name VARCHAR(100) NOT NULL,
    material_type VARCHAR(20) NOT NULL,
    
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 约束
    CONSTRAINT material_categories_type_check CHECK (material_type IN ('主材', '辅材'))
);

-- 3. 创建索引
CREATE INDEX idx_material_categories_material_name ON yiboshuo.material_categories(material_name);
CREATE INDEX idx_material_categories_material_type ON yiboshuo.material_categories(material_type);
CREATE INDEX idx_material_categories_is_active ON yiboshuo.material_categories(is_active);
CREATE INDEX idx_material_categories_display_order ON yiboshuo.material_categories(display_order);

-- 4. 添加触发器更新时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_material_categories_updated_at ON yiboshuo.material_categories;
CREATE TRIGGER update_material_categories_updated_at
    BEFORE UPDATE ON yiboshuo.material_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 5. 添加注释
COMMENT ON TABLE yiboshuo.material_categories IS '材料分类表';
COMMENT ON COLUMN yiboshuo.material_categories.id IS '材料分类ID';
COMMENT ON COLUMN yiboshuo.material_categories.material_name IS '材料分类名称';
COMMENT ON COLUMN yiboshuo.material_categories.material_type IS '材料属性(主材/辅材)';
COMMENT ON COLUMN yiboshuo.material_categories.base_unit_id IS '基本单位ID';
COMMENT ON COLUMN yiboshuo.material_categories.auxiliary_unit_id IS '辅助单位ID';
COMMENT ON COLUMN yiboshuo.material_categories.sales_unit_id IS '销售单位ID';
COMMENT ON COLUMN yiboshuo.material_categories.density IS '密度';
COMMENT ON COLUMN yiboshuo.material_categories.square_weight IS '平方克重';
COMMENT ON COLUMN yiboshuo.material_categories.shelf_life IS '保质期(天)';
COMMENT ON COLUMN yiboshuo.material_categories.inspection_standard IS '检验标准';
COMMENT ON COLUMN yiboshuo.material_categories.quality_grade IS '质量等级';
COMMENT ON COLUMN yiboshuo.material_categories.latest_purchase_price IS '最近采购价';
COMMENT ON COLUMN yiboshuo.material_categories.sales_price IS '销售价';
COMMENT ON COLUMN yiboshuo.material_categories.product_quote_price IS '产品报价';
COMMENT ON COLUMN yiboshuo.material_categories.cost_price IS '成本价格';
COMMENT ON COLUMN yiboshuo.material_categories.show_on_kanban IS '看板显示';
COMMENT ON COLUMN yiboshuo.material_categories.account_subject IS '科目';
COMMENT ON COLUMN yiboshuo.material_categories.code_prefix IS '编码前缀';
COMMENT ON COLUMN yiboshuo.material_categories.warning_days IS '预警天数';
COMMENT ON COLUMN yiboshuo.material_categories.carton_param1 IS '纸箱参数1';
COMMENT ON COLUMN yiboshuo.material_categories.carton_param2 IS '纸箱参数2';
COMMENT ON COLUMN yiboshuo.material_categories.carton_param3 IS '纸箱参数3';
COMMENT ON COLUMN yiboshuo.material_categories.carton_param4 IS '纸箱参数4';
COMMENT ON COLUMN yiboshuo.material_categories.enable_batch IS '启用批次';
COMMENT ON COLUMN yiboshuo.material_categories.enable_barcode IS '启用条码';
COMMENT ON COLUMN yiboshuo.material_categories.is_ink IS '是否油墨';
COMMENT ON COLUMN yiboshuo.material_categories.is_accessory IS '是否辅料';
COMMENT ON COLUMN yiboshuo.material_categories.is_consumable IS '是否耗材';
COMMENT ON COLUMN yiboshuo.material_categories.is_recyclable IS '是否可回收';
COMMENT ON COLUMN yiboshuo.material_categories.is_hazardous IS '是否危险品';
COMMENT ON COLUMN yiboshuo.material_categories.is_imported IS '是否进口';
COMMENT ON COLUMN yiboshuo.material_categories.is_customized IS '是否定制';
COMMENT ON COLUMN yiboshuo.material_categories.is_seasonal IS '是否季节性';
COMMENT ON COLUMN yiboshuo.material_categories.is_fragile IS '是否易碎';
COMMENT ON COLUMN yiboshuo.material_categories.is_perishable IS '是否易腐';
COMMENT ON COLUMN yiboshuo.material_categories.is_temperature_sensitive IS '是否温度敏感';
COMMENT ON COLUMN yiboshuo.material_categories.is_moisture_sensitive IS '是否湿度敏感';
COMMENT ON COLUMN yiboshuo.material_categories.is_light_sensitive IS '是否光敏感';
COMMENT ON COLUMN yiboshuo.material_categories.requires_special_storage IS '是否需要特殊存储';
COMMENT ON COLUMN yiboshuo.material_categories.requires_certification IS '是否需要认证';
COMMENT ON COLUMN yiboshuo.material_categories.display_order IS '显示排序';
COMMENT ON COLUMN yiboshuo.material_categories.is_active IS '是否启用';
COMMENT ON COLUMN yiboshuo.material_categories.created_by IS '创建人';
COMMENT ON COLUMN yiboshuo.material_categories.updated_by IS '修改人';
COMMENT ON COLUMN yiboshuo.material_categories.created_at IS '创建时间';
COMMENT ON COLUMN yiboshuo.material_categories.updated_at IS '更新时间';

-- 6. 插入一些测试数据
INSERT INTO yiboshuo.material_categories (material_name, material_type, code_prefix, display_order, is_active, created_by) VALUES
('BOPP薄膜', '主材', 'M', 1, true, gen_random_uuid()),
('CPP薄膜', '主材', 'M', 2, true, gen_random_uuid()),
('PE薄膜', '主材', 'M', 3, true, gen_random_uuid()),
('PET薄膜', '主材', 'M', 4, true, gen_random_uuid()),
('复合胶', '辅材', 'M', 5, true, gen_random_uuid()),
('油墨', '辅材', 'M', 6, true, gen_random_uuid()),
('溶剂', '辅材', 'M', 7, true, gen_random_uuid()),
('纸箱', '辅材', 'M', 8, true, gen_random_uuid());

-- 7. 重新创建被CASCADE删除的外键约束
-- 检查哪些表需要重新创建外键约束
SELECT 'Recreating foreign key constraints for material_categories...' as info;

-- 重新创建materials表的外键约束
ALTER TABLE yiboshuo.materials 
ADD CONSTRAINT materials_material_category_id_fkey 
FOREIGN KEY (material_category_id) REFERENCES yiboshuo.material_categories(id);

SELECT 'Material categories table fix completed successfully!' as result; 