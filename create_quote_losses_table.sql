-- 创建报价损耗表
CREATE TABLE IF NOT EXISTS wanle.quote_losses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 专享字段
    bag_type VARCHAR(100) NOT NULL,
    layer_count INTEGER NOT NULL,
    meter_range NUMERIC(10,2) NOT NULL,
    loss_rate NUMERIC(8,4) NOT NULL,
    cost NUMERIC(15,4) NOT NULL,
    
    -- 通用字段
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束：袋型+层数+米数区间的组合应该唯一
    UNIQUE(bag_type, layer_count, meter_range)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_quote_losses_bag_type ON wanle.quote_losses(bag_type);
CREATE INDEX IF NOT EXISTS idx_quote_losses_layer_count ON wanle.quote_losses(layer_count);
CREATE INDEX IF NOT EXISTS idx_quote_losses_enabled ON wanle.quote_losses(is_enabled);
CREATE INDEX IF NOT EXISTS idx_quote_losses_sort_order ON wanle.quote_losses(sort_order);
CREATE INDEX IF NOT EXISTS idx_quote_losses_created_at ON wanle.quote_losses(created_at);

-- 添加表注释
COMMENT ON TABLE wanle.quote_losses IS '报价损耗表';
COMMENT ON COLUMN wanle.quote_losses.bag_type IS '袋型';
COMMENT ON COLUMN wanle.quote_losses.layer_count IS '层数';
COMMENT ON COLUMN wanle.quote_losses.meter_range IS '米数区间';
COMMENT ON COLUMN wanle.quote_losses.loss_rate IS '损耗';
COMMENT ON COLUMN wanle.quote_losses.cost IS '费用';
COMMENT ON COLUMN wanle.quote_losses.description IS '描述';
COMMENT ON COLUMN wanle.quote_losses.sort_order IS '显示排序';
COMMENT ON COLUMN wanle.quote_losses.is_enabled IS '是否启用';
COMMENT ON COLUMN wanle.quote_losses.created_by IS '创建人';
COMMENT ON COLUMN wanle.quote_losses.updated_by IS '修改人';

-- 插入测试数据
INSERT INTO wanle.quote_losses (bag_type, layer_count, meter_range, loss_rate, cost, description, sort_order, created_by) VALUES
('三边封', 1, 100.00, 0.0500, 50.0000, '单层三边封袋损耗', 1, '550e8400-e29b-41d4-a716-446655440000'),
('三边封', 2, 100.00, 0.0800, 80.0000, '双层三边封袋损耗', 2, '550e8400-e29b-41d4-a716-446655440000'),
('三边封', 3, 100.00, 0.1200, 120.0000, '三层三边封袋损耗', 3, '550e8400-e29b-41d4-a716-446655440000'),
('中封', 1, 100.00, 0.0600, 60.0000, '单层中封袋损耗', 4, '550e8400-e29b-41d4-a716-446655440000'),
('中封', 2, 100.00, 0.0900, 90.0000, '双层中封袋损耗', 5, '550e8400-e29b-41d4-a716-446655440000'),
('背封', 1, 100.00, 0.0550, 55.0000, '单层背封袋损耗', 6, '550e8400-e29b-41d4-a716-446655440000'),
('四边封', 1, 100.00, 0.0700, 70.0000, '单层四边封袋损耗', 7, '550e8400-e29b-41d4-a716-446655440000'),
('自立袋', 1, 100.00, 0.0800, 80.0000, '单层自立袋损耗', 8, '550e8400-e29b-41d4-a716-446655440000'),
('拉链袋', 1, 100.00, 0.0900, 90.0000, '单层拉链袋损耗', 9, '550e8400-e29b-41d4-a716-446655440000'),
('吸嘴袋', 1, 100.00, 0.1000, 100.0000, '单层吸嘴袋损耗', 10, '550e8400-e29b-41d4-a716-446655440000')
ON CONFLICT (bag_type, layer_count, meter_range) DO NOTHING; 