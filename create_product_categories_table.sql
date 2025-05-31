-- 创建产品分类表的SQL脚本
-- 在wanle schema中创建product_categories表

-- 创建产品分类表
CREATE TABLE IF NOT EXISTS wanle.product_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name VARCHAR(255) NOT NULL,
    subject_name VARCHAR(100),
    is_blown_film BOOLEAN DEFAULT FALSE,
    delivery_days INTEGER,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_product_categories_enabled ON wanle.product_categories(is_enabled);
CREATE INDEX IF NOT EXISTS idx_product_categories_sort_order ON wanle.product_categories(sort_order);

-- 插入一些测试数据
INSERT INTO wanle.product_categories (category_name, subject_name, is_blown_film, delivery_days, description, sort_order, created_by) VALUES
('塑料袋', '原材料', TRUE, 7, '各种规格的塑料袋产品', 1, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('包装膜', '原材料', TRUE, 5, '包装用薄膜产品', 2, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('垃圾袋', '成品', FALSE, 3, '家用和商用垃圾袋', 3, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('食品袋', '成品', TRUE, 10, '食品级包装袋', 4, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('购物袋', '成品', FALSE, 5, '环保购物袋', 5, '6e941d77-8d11-41a6-9c0a-97f053725b29');

COMMENT ON TABLE wanle.product_categories IS '产品分类表';
COMMENT ON COLUMN wanle.product_categories.category_name IS '产品分类名称';
COMMENT ON COLUMN wanle.product_categories.subject_name IS '科目名称';
COMMENT ON COLUMN wanle.product_categories.is_blown_film IS '是否吹膜';
COMMENT ON COLUMN wanle.product_categories.delivery_days IS '交货天数';
COMMENT ON COLUMN wanle.product_categories.description IS '描述';
COMMENT ON COLUMN wanle.product_categories.sort_order IS '显示排序';
COMMENT ON COLUMN wanle.product_categories.is_enabled IS '是否启用';
COMMENT ON COLUMN wanle.product_categories.created_by IS '创建人';
COMMENT ON COLUMN wanle.product_categories.updated_by IS '修改人';
COMMENT ON COLUMN wanle.product_categories.created_at IS '创建时间';
COMMENT ON COLUMN wanle.product_categories.updated_at IS '更新时间'; 