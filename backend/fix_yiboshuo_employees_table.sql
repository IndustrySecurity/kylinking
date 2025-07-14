-- 修复 yiboshuo schema 下的 employees 表
-- 基于 app/models/basic_data.py

-- 设置 schema
SET search_path TO yiboshuo;

-- 重新创建正确的 employees 表
CREATE TABLE IF NOT EXISTS employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    employee_name VARCHAR(100) NOT NULL,
    position_id UUID,
    department_id UUID,
    employment_status VARCHAR(20) DEFAULT 'trial',
    business_type VARCHAR(20),
    gender VARCHAR(20),
    mobile_phone VARCHAR(20),
    landline_phone VARCHAR(20),
    emergency_phone VARCHAR(20),
    hire_date DATE,
    birth_date DATE,
    circulation_card_id VARCHAR(50),
    workshop_id VARCHAR(50),
    id_number VARCHAR(50),
    salary_1 NUMERIC(10, 2) DEFAULT 0,
    salary_2 NUMERIC(10, 2) DEFAULT 0,
    salary_3 NUMERIC(10, 2) DEFAULT 0,
    salary_4 NUMERIC(10, 2) DEFAULT 0,
    native_place VARCHAR(200),
    ethnicity VARCHAR(50),
    province VARCHAR(100),
    city VARCHAR(100),
    district VARCHAR(100),
    street VARCHAR(100),
    birth_address TEXT,
    archive_location TEXT,
    household_registration TEXT,
    evaluation_level VARCHAR(50),
    leave_date DATE,
    seniority_wage NUMERIC(10, 2),
    assessment_wage NUMERIC(10, 2),
    contract_start_date DATE,
    contract_end_date DATE,
    expiry_warning_date DATE,
    ufida_code VARCHAR(100),
    kingdee_push BOOLEAN DEFAULT FALSE,
    remarks TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES positions(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_employees_employee_id ON employees(employee_id);
CREATE INDEX IF NOT EXISTS idx_employees_department_id ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_position_id ON employees(position_id);
CREATE INDEX IF NOT EXISTS idx_employees_enabled ON employees(is_enabled);

-- 重新添加触发器
CREATE OR REPLACE FUNCTION update_employees_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER employees_updated_at_trigger
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION update_employees_updated_at();

COMMENT ON TABLE employees IS '员工管理表';
COMMENT ON COLUMN employees.employee_id IS '员工工号';
COMMENT ON COLUMN employees.employee_name IS '员工姓名';
COMMENT ON COLUMN employees.position_id IS '职位ID';
COMMENT ON COLUMN employees.department_id IS '部门ID';
COMMENT ON COLUMN employees.employment_status IS '就业状态：trial-试用期, formal-正式, intern-实习, contract-合同工, temporary-临时工, resigned-离职';
COMMENT ON COLUMN employees.business_type IS '业务类型';
COMMENT ON COLUMN employees.gender IS '性别：male-男, female-女, other-其他';
COMMENT ON COLUMN employees.mobile_phone IS '手机号码';
COMMENT ON COLUMN employees.landline_phone IS '座机号码';
COMMENT ON COLUMN employees.emergency_phone IS '紧急联系电话';
COMMENT ON COLUMN employees.hire_date IS '入职日期';
COMMENT ON COLUMN employees.birth_date IS '出生日期';
COMMENT ON COLUMN employees.circulation_card_id IS '流通卡号';
COMMENT ON COLUMN employees.workshop_id IS '车间ID';
COMMENT ON COLUMN employees.id_number IS '身份证号';
COMMENT ON COLUMN employees.salary_1 IS '基本工资';
COMMENT ON COLUMN employees.salary_2 IS '岗位工资';
COMMENT ON COLUMN employees.salary_3 IS '技能工资';
COMMENT ON COLUMN employees.salary_4 IS '绩效工资';
COMMENT ON COLUMN employees.native_place IS '籍贯';
COMMENT ON COLUMN employees.ethnicity IS '民族';
COMMENT ON COLUMN employees.province IS '省份';
COMMENT ON COLUMN employees.city IS '城市';
COMMENT ON COLUMN employees.district IS '区县';
COMMENT ON COLUMN employees.street IS '街道';
COMMENT ON COLUMN employees.birth_address IS '出生地址';
COMMENT ON COLUMN employees.archive_location IS '档案存放地';
COMMENT ON COLUMN employees.household_registration IS '户口所在地';
COMMENT ON COLUMN employees.evaluation_level IS '评估等级';
COMMENT ON COLUMN employees.leave_date IS '离职日期';
COMMENT ON COLUMN employees.seniority_wage IS '工龄工资';
COMMENT ON COLUMN employees.assessment_wage IS '考核工资';
COMMENT ON COLUMN employees.contract_start_date IS '合同开始日期';
COMMENT ON COLUMN employees.contract_end_date IS '合同结束日期';
COMMENT ON COLUMN employees.expiry_warning_date IS '到期提醒日期';
COMMENT ON COLUMN employees.ufida_code IS '用友编码';
COMMENT ON COLUMN employees.kingdee_push IS '金蝶推送状态';
COMMENT ON COLUMN employees.remarks IS '备注信息';
COMMENT ON COLUMN employees.sort_order IS '排序';
COMMENT ON COLUMN employees.is_enabled IS '是否启用'; 