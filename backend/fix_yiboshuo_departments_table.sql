-- 修正yiboshuo departments表结构
-- 使其与模型定义一致

-- 1. 先检查当前表结构和依赖关系
SELECT 'Current departments table structure:' as info;
\d yiboshuo.departments;

-- 2. 删除现有的departments表 (CASCADE会自动处理外键依赖)
DROP TABLE IF EXISTS yiboshuo.departments CASCADE;

-- 3. 重新创建departments表，使用正确的结构
CREATE TABLE yiboshuo.departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dept_code VARCHAR(50) UNIQUE NOT NULL,
    dept_name VARCHAR(100) NOT NULL,
    parent_id UUID,
    is_blown_film BOOLEAN DEFAULT FALSE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES yiboshuo.departments(id)
);

-- 4. 创建索引
CREATE INDEX idx_departments_dept_code ON yiboshuo.departments(dept_code);
CREATE INDEX idx_departments_dept_name ON yiboshuo.departments(dept_name);
CREATE INDEX idx_departments_parent_id ON yiboshuo.departments(parent_id);
CREATE INDEX idx_departments_is_enabled ON yiboshuo.departments(is_enabled);

-- 5. 添加触发器更新时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_departments_updated_at ON yiboshuo.departments;
CREATE TRIGGER update_departments_updated_at
    BEFORE UPDATE ON yiboshuo.departments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 6. 添加注释
COMMENT ON TABLE yiboshuo.departments IS '部门管理表';
COMMENT ON COLUMN yiboshuo.departments.id IS '部门ID';
COMMENT ON COLUMN yiboshuo.departments.dept_code IS '部门编号';
COMMENT ON COLUMN yiboshuo.departments.dept_name IS '部门名称';
COMMENT ON COLUMN yiboshuo.departments.parent_id IS '上级部门ID';
COMMENT ON COLUMN yiboshuo.departments.is_blown_film IS '是否吹膜';
COMMENT ON COLUMN yiboshuo.departments.description IS '描述';
COMMENT ON COLUMN yiboshuo.departments.sort_order IS '显示排序';
COMMENT ON COLUMN yiboshuo.departments.is_enabled IS '是否启用';
COMMENT ON COLUMN yiboshuo.departments.created_by IS '创建人';
COMMENT ON COLUMN yiboshuo.departments.updated_by IS '修改人';
COMMENT ON COLUMN yiboshuo.departments.created_at IS '创建时间';
COMMENT ON COLUMN yiboshuo.departments.updated_at IS '更新时间';

-- 7. 插入一些测试数据
INSERT INTO yiboshuo.departments (dept_code, dept_name, parent_id, is_blown_film, description, sort_order, is_enabled, created_by) VALUES
('DEPT001', '生产部', NULL, true, '负责生产管理', 1, true, gen_random_uuid()),
('DEPT002', '吹膜车间', (SELECT id FROM yiboshuo.departments WHERE dept_code = 'DEPT001'), true, '吹膜生产车间', 2, true, gen_random_uuid()),
('DEPT003', '质量部', NULL, false, '负责质量控制', 3, true, gen_random_uuid()),
('DEPT004', '仓储部', NULL, false, '负责仓储管理', 4, true, gen_random_uuid()),
('DEPT005', '销售部', NULL, false, '负责销售业务', 5, true, gen_random_uuid());

-- 8. 重新创建被CASCADE删除的外键约束
-- 检查哪些表需要重新创建外键约束
SELECT 'Recreating foreign key constraints...' as info;

-- 重新创建positions表的外键约束
ALTER TABLE yiboshuo.positions 
ADD CONSTRAINT positions_department_id_fkey 
FOREIGN KEY (department_id) REFERENCES yiboshuo.departments(id);

-- 重新创建employees表的外键约束
ALTER TABLE yiboshuo.employees 
ADD CONSTRAINT employees_department_id_fkey 
FOREIGN KEY (department_id) REFERENCES yiboshuo.departments(id);

-- 重新创建其他业务表的外键约束
-- inbound_orders
ALTER TABLE yiboshuo.inbound_orders 
ADD CONSTRAINT inbound_orders_department_id_fkey 
FOREIGN KEY (department_id) REFERENCES yiboshuo.departments(id);

-- material_count_plans
ALTER TABLE yiboshuo.material_count_plans 
ADD CONSTRAINT material_count_plans_department_id_fkey 
FOREIGN KEY (department_id) REFERENCES yiboshuo.departments(id);

-- material_inbound_orders
ALTER TABLE yiboshuo.material_inbound_orders 
ADD CONSTRAINT material_inbound_orders_department_id_fkey 
FOREIGN KEY (department_id) REFERENCES yiboshuo.departments(id);

-- material_outbound_orders
ALTER TABLE yiboshuo.material_outbound_orders 
ADD CONSTRAINT material_outbound_orders_department_id_fkey 
FOREIGN KEY (department_id) REFERENCES yiboshuo.departments(id);

ALTER TABLE yiboshuo.material_outbound_orders 
ADD CONSTRAINT material_outbound_orders_requisition_department_id_fkey 
FOREIGN KEY (requisition_department_id) REFERENCES yiboshuo.departments(id);

-- material_transfer_orders
ALTER TABLE yiboshuo.material_transfer_orders 
ADD CONSTRAINT material_transfer_orders_department_id_fkey 
FOREIGN KEY (department_id) REFERENCES yiboshuo.departments(id);

-- outbound_orders
ALTER TABLE yiboshuo.outbound_orders 
ADD CONSTRAINT outbound_orders_department_id_fkey 
FOREIGN KEY (department_id) REFERENCES yiboshuo.departments(id);

-- product_count_plans
ALTER TABLE yiboshuo.product_count_plans 
ADD CONSTRAINT product_count_plans_department_id_fkey 
FOREIGN KEY (department_id) REFERENCES yiboshuo.departments(id);

-- product_transfer_orders
ALTER TABLE yiboshuo.product_transfer_orders 
ADD CONSTRAINT product_transfer_orders_department_id_fkey 
FOREIGN KEY (department_id) REFERENCES yiboshuo.departments(id);

SELECT 'Departments table fix completed successfully!' as result; 