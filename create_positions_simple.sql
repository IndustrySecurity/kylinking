-- 在mytenant schema下创建职位表
SET search_path TO mytenant, public;

-- 创建职位表
CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    position_name VARCHAR(100) NOT NULL,
    department_id UUID NOT NULL,
    parent_position_id UUID,
    hourly_wage NUMERIC(10, 2),
    standard_pass_rate NUMERIC(5, 2),
    is_supervisor BOOLEAN DEFAULT FALSE,
    is_machine_operator BOOLEAN DEFAULT FALSE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_positions_department_id ON positions(department_id);
CREATE INDEX IF NOT EXISTS idx_positions_enabled ON positions(is_enabled);
CREATE INDEX IF NOT EXISTS idx_positions_sort_order ON positions(sort_order);

-- 插入测试数据
DO $$
DECLARE
    dept_id UUID;
    user_id UUID;
    pos_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO pos_count FROM positions;
    
    IF pos_count = 0 THEN
        SELECT id INTO dept_id FROM departments WHERE is_enabled = true LIMIT 1;
        SELECT id INTO user_id FROM system.users LIMIT 1;
        
        IF dept_id IS NOT NULL AND user_id IS NOT NULL THEN
            INSERT INTO positions (position_name, department_id, hourly_wage, standard_pass_rate, 
                                 is_supervisor, is_machine_operator, description, sort_order, created_by) 
            VALUES 
                ('总经理', dept_id, 200.00, 95.00, true, false, '公司总经理', 1, user_id),
                ('生产主管', dept_id, 80.00, 90.00, true, false, '生产部门主管', 2, user_id),
                ('操作员', dept_id, 30.00, 85.00, false, true, '生产线操作员', 3, user_id);
            
            RAISE NOTICE '职位表创建成功并插入了测试数据！';
        ELSE
            RAISE NOTICE '职位表已创建但未插入测试数据';
        END IF;
    END IF;
END $$;

SELECT COUNT(*) as record_count FROM positions; 