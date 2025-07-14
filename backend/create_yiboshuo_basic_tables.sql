-- 为yiboshuo租户创建基础数据表
-- 基于backend/app/models/basic_data.py

-- 确保使用yiboshuo schema
SET search_path TO yiboshuo;

-- 1. 产品分类表
CREATE TABLE IF NOT EXISTS product_categories (
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 包装方式表
CREATE TABLE IF NOT EXISTS package_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_name VARCHAR(100) NOT NULL,
    package_code VARCHAR(50) UNIQUE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 送货方式表
CREATE TABLE IF NOT EXISTS delivery_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_name VARCHAR(100) NOT NULL,
    delivery_code VARCHAR(50) UNIQUE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 色卡表
CREATE TABLE IF NOT EXISTS color_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    color_code VARCHAR(50) UNIQUE NOT NULL,
    color_name VARCHAR(100) NOT NULL,
    color_value VARCHAR(20) NOT NULL,
    remarks TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 单位表
CREATE TABLE IF NOT EXISTS units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_name VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 客户分类管理表
CREATE TABLE IF NOT EXISTS customer_category_management (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name VARCHAR(100) NOT NULL,
    category_code VARCHAR(50),
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 供应商分类管理表
CREATE TABLE IF NOT EXISTS supplier_category_management (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name VARCHAR(100) NOT NULL,
    category_code VARCHAR(50),
    description TEXT,
    is_plate_making BOOLEAN DEFAULT FALSE,
    is_outsourcing BOOLEAN DEFAULT FALSE,
    is_knife_plate BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 规格表
CREATE TABLE IF NOT EXISTS specifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spec_name VARCHAR(100) NOT NULL,
    length NUMERIC(10, 3) NOT NULL,
    width NUMERIC(10, 3) NOT NULL,
    roll NUMERIC(10, 3) NOT NULL,
    area_sqm NUMERIC(15, 6),
    spec_format VARCHAR(200),
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. 币别表
CREATE TABLE IF NOT EXISTS currencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    currency_code VARCHAR(10) UNIQUE NOT NULL,
    currency_name VARCHAR(100) NOT NULL,
    exchange_rate NUMERIC(10, 4) NOT NULL DEFAULT 1.0000,
    is_base_currency BOOLEAN DEFAULT FALSE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. 税率管理表
CREATE TABLE IF NOT EXISTS tax_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tax_name VARCHAR(100) NOT NULL,
    tax_rate NUMERIC(5, 2) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. 结算方式表
CREATE TABLE IF NOT EXISTS settlement_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    settlement_name VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. 账户管理表
CREATE TABLE IF NOT EXISTS account_management (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_name VARCHAR(200) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    currency_id UUID,
    bank_name VARCHAR(200),
    bank_account VARCHAR(100),
    opening_date DATE,
    opening_address VARCHAR(500),
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. 付款方式表
CREATE TABLE IF NOT EXISTS payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_name VARCHAR(100) NOT NULL,
    cash_on_delivery BOOLEAN DEFAULT FALSE,
    monthly_settlement BOOLEAN DEFAULT FALSE,
    next_month_settlement BOOLEAN DEFAULT FALSE,
    cash_on_delivery_days INTEGER DEFAULT 0,
    monthly_settlement_days INTEGER DEFAULT 0,
    monthly_reconciliation_day INTEGER DEFAULT 0,
    next_month_settlement_count INTEGER DEFAULT 0,
    monthly_payment_day INTEGER DEFAULT 0,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. 油墨选项表
CREATE TABLE IF NOT EXISTS ink_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    option_name VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. 报价运费表
CREATE TABLE IF NOT EXISTS quote_freights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region VARCHAR(100) NOT NULL,
    percentage NUMERIC(5, 2) NOT NULL DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. 材料分类表
CREATE TABLE IF NOT EXISTS material_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_name VARCHAR(100) NOT NULL,
    material_type VARCHAR(20) NOT NULL,
    base_unit_id UUID,
    auxiliary_unit_id UUID,
    sales_unit_id UUID,
    density NUMERIC(10, 4),
    square_weight NUMERIC(10, 4),
    shelf_life INTEGER,
    inspection_standard VARCHAR(200),
    quality_grade VARCHAR(100),
    latest_purchase_price NUMERIC(15, 4),
    sales_price NUMERIC(15, 4),
    product_quote_price NUMERIC(15, 4),
    cost_price NUMERIC(15, 4),
    show_on_kanban BOOLEAN DEFAULT FALSE,
    account_subject VARCHAR(100),
    code_prefix VARCHAR(10) DEFAULT 'M',
    warning_days INTEGER,
    carton_param1 NUMERIC(10, 3),
    carton_param2 NUMERIC(10, 3),
    carton_param3 NUMERIC(10, 3),
    carton_param4 NUMERIC(10, 3),
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
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 17. 计算参数表
CREATE TABLE IF NOT EXISTS calculation_parameters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parameter_name VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 18. 计算方案表
CREATE TABLE IF NOT EXISTS calculation_schemes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_name VARCHAR(100) NOT NULL,
    scheme_category VARCHAR(50) NOT NULL,
    scheme_formula TEXT,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 19. 报损类型表
CREATE TABLE IF NOT EXISTS loss_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loss_type_name VARCHAR(100) NOT NULL,
    process_id UUID,
    loss_category_id UUID,
    is_assessment BOOLEAN DEFAULT FALSE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 20. 机台表
CREATE TABLE IF NOT EXISTS machines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    machine_code VARCHAR(50) UNIQUE NOT NULL,
    machine_name VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    min_width NUMERIC(10, 2),
    max_width NUMERIC(10, 2),
    production_speed NUMERIC(10, 2),
    preparation_time NUMERIC(8, 2),
    difficulty_factor NUMERIC(8, 4),
    circulation_card_id VARCHAR(100),
    max_colors INTEGER,
    kanban_display VARCHAR(200),
    capacity_formula VARCHAR(200),
    gas_unit_price NUMERIC(10, 4),
    power_consumption NUMERIC(10, 2),
    electricity_cost_per_hour NUMERIC(10, 4),
    output_conversion_factor NUMERIC(8, 4),
    plate_change_time NUMERIC(8, 2),
    mes_barcode_prefix VARCHAR(20),
    is_curing_room BOOLEAN DEFAULT FALSE,
    material_name VARCHAR(200),
    remarks TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 21. 报价油墨表
CREATE TABLE IF NOT EXISTS quote_inks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name VARCHAR(100) NOT NULL,
    square_price NUMERIC(10, 4),
    unit_price_formula VARCHAR(200),
    gram_weight NUMERIC(10, 4),
    is_ink BOOLEAN DEFAULT FALSE,
    is_solvent BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 22. 报价材料表
CREATE TABLE IF NOT EXISTS quote_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_name VARCHAR(100) NOT NULL,
    density NUMERIC(10, 4),
    kg_price NUMERIC(15, 4),
    layer_1_optional BOOLEAN DEFAULT FALSE,
    layer_2_optional BOOLEAN DEFAULT FALSE,
    layer_3_optional BOOLEAN DEFAULT FALSE,
    layer_4_optional BOOLEAN DEFAULT FALSE,
    layer_5_optional BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    remarks TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 23. 报价辅材表
CREATE TABLE IF NOT EXISTS quote_accessories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_name VARCHAR(100) NOT NULL,
    unit_price NUMERIC(15, 4),
    calculation_scheme_id UUID,
    sort_order INTEGER DEFAULT 0,
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (calculation_scheme_id) REFERENCES calculation_schemes(id)
);

-- 24. 报价损耗表
CREATE TABLE IF NOT EXISTS quote_losses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bag_type VARCHAR(100) NOT NULL,
    layer_count INTEGER NOT NULL,
    meter_range NUMERIC(10, 2) NOT NULL,
    loss_rate NUMERIC(8, 4) NOT NULL,
    cost NUMERIC(15, 4) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 25. 部门表
CREATE TABLE IF NOT EXISTS departments (
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
    FOREIGN KEY (parent_id) REFERENCES departments(id)
);

-- 26. 职位表
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (parent_position_id) REFERENCES positions(id)
);

-- 27. 员工表
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

-- 28. 仓库表
CREATE TABLE IF NOT EXISTS warehouses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_code VARCHAR(50) UNIQUE NOT NULL,
    warehouse_name VARCHAR(100) NOT NULL,
    warehouse_type VARCHAR(50),
    parent_warehouse_id UUID,
    accounting_method VARCHAR(50),
    circulation_type VARCHAR(50),
    exclude_from_operations BOOLEAN DEFAULT FALSE,
    is_abnormal BOOLEAN DEFAULT FALSE,
    is_carryover_warehouse BOOLEAN DEFAULT FALSE,
    exclude_from_docking BOOLEAN DEFAULT FALSE,
    is_in_stocktaking BOOLEAN DEFAULT FALSE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_warehouse_id) REFERENCES warehouses(id)
);

-- 29. 工序分类表
CREATE TABLE IF NOT EXISTS process_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_name VARCHAR(100) NOT NULL,
    category_type VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    data_collection_mode VARCHAR(50),
    show_data_collection_interface BOOLEAN DEFAULT FALSE,
    -- 自检类型字段
    self_check_type_1 VARCHAR(100),
    self_check_type_2 VARCHAR(100),
    self_check_type_3 VARCHAR(100),
    self_check_type_4 VARCHAR(100),
    self_check_type_5 VARCHAR(100),
    self_check_type_6 VARCHAR(100),
    self_check_type_7 VARCHAR(100),
    self_check_type_8 VARCHAR(100),
    self_check_type_9 VARCHAR(100),
    self_check_type_10 VARCHAR(100),
    -- 工艺预料字段
    process_material_1 VARCHAR(100),
    process_material_2 VARCHAR(100),
    process_material_3 VARCHAR(100),
    process_material_4 VARCHAR(100),
    process_material_5 VARCHAR(100),
    process_material_6 VARCHAR(100),
    process_material_7 VARCHAR(100),
    process_material_8 VARCHAR(100),
    process_material_9 VARCHAR(100),
    process_material_10 VARCHAR(100),
    -- 预留弹出框字段
    reserved_popup_1 VARCHAR(100),
    reserved_popup_2 VARCHAR(100),
    reserved_popup_3 VARCHAR(100),
    reserved_dropdown_1 VARCHAR(100),
    reserved_dropdown_2 VARCHAR(100),
    reserved_dropdown_3 VARCHAR(100),
    -- 数字字段
    number_1 NUMERIC(15, 4),
    number_2 NUMERIC(15, 4),
    number_3 NUMERIC(15, 4),
    number_4 NUMERIC(15, 4),
    -- 大量布尔字段（基础配置）
    report_quantity BOOLEAN DEFAULT FALSE,
    report_personnel BOOLEAN DEFAULT FALSE,
    report_data BOOLEAN DEFAULT FALSE,
    report_kg BOOLEAN DEFAULT FALSE,
    report_number BOOLEAN DEFAULT FALSE,
    report_time BOOLEAN DEFAULT FALSE,
    down_report_time BOOLEAN DEFAULT FALSE,
    machine_speed BOOLEAN DEFAULT FALSE,
    cutting_specs BOOLEAN DEFAULT FALSE,
    aging_room BOOLEAN DEFAULT FALSE,
    reserved_char_1 BOOLEAN DEFAULT FALSE,
    reserved_char_2 BOOLEAN DEFAULT FALSE,
    net_weight BOOLEAN DEFAULT FALSE,
    production_task_display_order BOOLEAN DEFAULT FALSE,
    -- 装箱配置字段
    packing_bags_count BOOLEAN DEFAULT FALSE,
    pallet_barcode BOOLEAN DEFAULT FALSE,
    pallet_bag_loading BOOLEAN DEFAULT FALSE,
    box_loading_count BOOLEAN DEFAULT FALSE,
    seed_bag_count BOOLEAN DEFAULT FALSE,
    defect_bag_count BOOLEAN DEFAULT FALSE,
    report_staff BOOLEAN DEFAULT FALSE,
    shortage_count BOOLEAN DEFAULT FALSE,
    material_specs BOOLEAN DEFAULT FALSE,
    color_mixing_count BOOLEAN DEFAULT FALSE,
    batch_bags BOOLEAN DEFAULT FALSE,
    production_date BOOLEAN DEFAULT FALSE,
    compound BOOLEAN DEFAULT FALSE,
    process_machine_allocation BOOLEAN DEFAULT FALSE,
    -- 持续率配置字段
    continuity_rate BOOLEAN DEFAULT FALSE,
    strip_head_change_count BOOLEAN DEFAULT FALSE,
    plate_support_change_count BOOLEAN DEFAULT FALSE,
    plate_change_count BOOLEAN DEFAULT FALSE,
    lamination_change_count BOOLEAN DEFAULT FALSE,
    plate_making_multiple BOOLEAN DEFAULT FALSE,
    algorithm_time BOOLEAN DEFAULT FALSE,
    timing BOOLEAN DEFAULT FALSE,
    pallet_time BOOLEAN DEFAULT FALSE,
    glue_water_change_count BOOLEAN DEFAULT FALSE,
    glue_drip_bag_change BOOLEAN DEFAULT FALSE,
    pallet_sub_bag_change BOOLEAN DEFAULT FALSE,
    transfer_report_change BOOLEAN DEFAULT FALSE,
    auto_print BOOLEAN DEFAULT FALSE,
    -- 过程管控字段
    process_rate BOOLEAN DEFAULT FALSE,
    color_set_change_count BOOLEAN DEFAULT FALSE,
    mesh_format_change_count BOOLEAN DEFAULT FALSE,
    overtime BOOLEAN DEFAULT FALSE,
    team_date BOOLEAN DEFAULT FALSE,
    sampling_time BOOLEAN DEFAULT FALSE,
    start_reading BOOLEAN DEFAULT FALSE,
    count_times BOOLEAN DEFAULT FALSE,
    blade_count BOOLEAN DEFAULT FALSE,
    power_consumption BOOLEAN DEFAULT FALSE,
    maintenance_time BOOLEAN DEFAULT FALSE,
    end_time BOOLEAN DEFAULT FALSE,
    malfunction_material_collection BOOLEAN DEFAULT FALSE,
    -- 查询/机器相关
    is_query_machine BOOLEAN DEFAULT FALSE,
    -- MES系统集成字段
    mes_report_kg_manual BOOLEAN DEFAULT FALSE,
    mes_kg_auto_calculation BOOLEAN DEFAULT FALSE,
    auto_weighing_once BOOLEAN DEFAULT FALSE,
    mes_process_feedback_clear BOOLEAN DEFAULT FALSE,
    mes_consumption_solvent_by_ton BOOLEAN DEFAULT FALSE,
    -- 生产控制字段
    single_report_open BOOLEAN DEFAULT FALSE,
    multi_condition_open BOOLEAN DEFAULT FALSE,
    mes_line_start_work_order BOOLEAN DEFAULT FALSE,
    mes_material_kg_consumption BOOLEAN DEFAULT FALSE,
    mes_report_not_less_than_kg BOOLEAN DEFAULT FALSE,
    mes_water_consumption_by_ton BOOLEAN DEFAULT FALSE,
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 30. 袋型管理表
CREATE TABLE IF NOT EXISTS bag_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bag_type_name VARCHAR(100) NOT NULL,
    spec_expression VARCHAR(200),
    production_unit_id UUID,
    sales_unit_id UUID,
    difficulty_coefficient NUMERIC(10, 2) DEFAULT 0,
    bag_making_unit_price NUMERIC(10, 2) DEFAULT 0,
    is_roll_film BOOLEAN DEFAULT FALSE,
    is_custom_spec BOOLEAN DEFAULT FALSE,
    is_strict_bag_type BOOLEAN DEFAULT TRUE,
    is_process_judgment BOOLEAN DEFAULT FALSE,
    is_diaper BOOLEAN DEFAULT FALSE,
    is_woven_bag BOOLEAN DEFAULT FALSE,
    is_label BOOLEAN DEFAULT FALSE,
    is_antenna BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (production_unit_id) REFERENCES units(id),
    FOREIGN KEY (sales_unit_id) REFERENCES units(id)
);

-- 31. 袋型结构表
CREATE TABLE IF NOT EXISTS bag_type_structures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bag_type_id UUID NOT NULL,
    structure_name VARCHAR(100) NOT NULL,
    structure_expression_id UUID,
    expand_length_formula_id UUID,
    expand_width_formula_id UUID,
    material_length_formula_id UUID,
    material_width_formula_id UUID,
    single_piece_width_formula_id UUID,
    sort_order INTEGER DEFAULT 0,
    image_url VARCHAR(500),
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bag_type_id) REFERENCES bag_types(id)
);

-- 32. 袋型相关公式表
CREATE TABLE IF NOT EXISTS bag_related_formulas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bag_type_id UUID NOT NULL,
    meter_formula_id UUID,
    square_formula_id UUID,
    material_width_formula_id UUID,
    per_piece_formula_id UUID,
    dimension_description VARCHAR(200),
    sort_order INTEGER DEFAULT 0,
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bag_type_id) REFERENCES bag_types(id)
);

-- 33. 工序表
CREATE TABLE IF NOT EXISTS processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_name VARCHAR(100) NOT NULL,
    process_category_id UUID,
    scheduling_method VARCHAR(50),
    mes_condition_code VARCHAR(100),
    unit_id UUID,
    production_allowance FLOAT,
    return_allowance_kg FLOAT,
    sort_order INTEGER,
    over_production_allowance FLOAT,
    self_check_allowance_kg FLOAT,
    workshop_difference FLOAT,
    max_upload_count INTEGER,
    standard_weight_difference FLOAT,
    workshop_worker_difference FLOAT,
    mes_report_form_code VARCHAR(100),
    ignore_inspection BOOLEAN DEFAULT FALSE,
    unit_price FLOAT,
    return_allowance_upper_kg FLOAT,
    over_production_limit FLOAT,
    -- 布尔配置字段
    mes_verify_quality BOOLEAN DEFAULT FALSE,
    external_processing BOOLEAN DEFAULT FALSE,
    mes_upload_defect_items BOOLEAN DEFAULT FALSE,
    mes_scancode_shelf BOOLEAN DEFAULT FALSE,
    mes_verify_spec BOOLEAN DEFAULT FALSE,
    mes_upload_kg_required BOOLEAN DEFAULT FALSE,
    display_data_collection BOOLEAN DEFAULT FALSE,
    free_inspection BOOLEAN DEFAULT FALSE,
    process_with_machine BOOLEAN DEFAULT FALSE,
    semi_product_usage BOOLEAN DEFAULT FALSE,
    material_usage_required BOOLEAN DEFAULT FALSE,
    -- 公式外键
    pricing_formula_id UUID,
    worker_formula_id UUID,
    material_formula_id UUID,
    output_formula_id UUID,
    time_formula_id UUID,
    energy_formula_id UUID,
    saving_formula_id UUID,
    labor_cost_formula_id UUID,
    pricing_order_formula_id UUID,
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (process_category_id) REFERENCES process_categories(id),
    FOREIGN KEY (unit_id) REFERENCES units(id),
    FOREIGN KEY (pricing_formula_id) REFERENCES calculation_schemes(id),
    FOREIGN KEY (worker_formula_id) REFERENCES calculation_schemes(id),
    FOREIGN KEY (material_formula_id) REFERENCES calculation_schemes(id),
    FOREIGN KEY (output_formula_id) REFERENCES calculation_schemes(id),
    FOREIGN KEY (time_formula_id) REFERENCES calculation_schemes(id),
    FOREIGN KEY (energy_formula_id) REFERENCES calculation_schemes(id),
    FOREIGN KEY (saving_formula_id) REFERENCES calculation_schemes(id),
    FOREIGN KEY (labor_cost_formula_id) REFERENCES calculation_schemes(id),
    FOREIGN KEY (pricing_order_formula_id) REFERENCES calculation_schemes(id)
);

-- 34. 工序机台关联表
CREATE TABLE IF NOT EXISTS process_machines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL,
    machine_id UUID NOT NULL,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (process_id) REFERENCES processes(id),
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- 35. 班组管理表
CREATE TABLE IF NOT EXISTS team_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_code VARCHAR(50) UNIQUE NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    circulation_card_id VARCHAR(50),
    day_shift_hours NUMERIC(8, 2),
    night_shift_hours NUMERIC(8, 2),
    rotating_shift_hours NUMERIC(8, 2),
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 36. 班组人员表
CREATE TABLE IF NOT EXISTS team_group_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_group_id UUID NOT NULL,
    employee_id UUID NOT NULL,
    piece_rate_percentage NUMERIC(5, 2) DEFAULT 0,
    saving_bonus_percentage NUMERIC(5, 2) DEFAULT 0,
    remarks TEXT,
    sort_order INTEGER DEFAULT 0,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_group_id) REFERENCES team_groups(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- 37. 班组机台表
CREATE TABLE IF NOT EXISTS team_group_machines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_group_id UUID NOT NULL,
    machine_id UUID NOT NULL,
    remarks TEXT,
    sort_order INTEGER DEFAULT 0,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_group_id) REFERENCES team_groups(id),
    FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- 38. 班组工序分类表
CREATE TABLE IF NOT EXISTS team_group_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_group_id UUID NOT NULL,
    process_category_id UUID NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_group_id) REFERENCES team_groups(id),
    FOREIGN KEY (process_category_id) REFERENCES process_categories(id)
);

-- 39. 客户管理表
CREATE TABLE IF NOT EXISTS customer_management (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_code VARCHAR(50),
    customer_name VARCHAR(255) NOT NULL,
    customer_category_id UUID,
    tax_rate_id UUID,
    tax_rate NUMERIC(5, 2),
    customer_abbreviation VARCHAR(100),
    customer_level VARCHAR(10),
    parent_customer_id UUID,
    region VARCHAR(100),
    package_method_id UUID,
    barcode_prefix VARCHAR(50),
    business_type VARCHAR(50),
    enterprise_type VARCHAR(50),
    company_address TEXT,
    trademark_start_date DATE,
    trademark_end_date DATE,
    barcode_cert_start_date DATE,
    barcode_cert_end_date DATE,
    contract_start_date DATE,
    contract_end_date DATE,
    business_start_date DATE,
    business_end_date DATE,
    production_permit_start_date DATE,
    production_permit_end_date DATE,
    inspection_report_start_date DATE,
    inspection_report_end_date DATE,
    payment_method_id UUID,
    currency_id UUID,
    settlement_color_difference NUMERIC(10, 4),
    sales_commission NUMERIC(5, 2),
    credit_amount NUMERIC(15, 2),
    registered_capital NUMERIC(15, 2),
    accounts_period INTEGER,
    account_period INTEGER,
    salesperson_id UUID,
    barcode_front_code VARCHAR(50),
    barcode_back_code VARCHAR(50),
    user_barcode VARCHAR(100),
    invoice_water_number VARCHAR(50),
    water_mark_position NUMERIC(10, 2),
    legal_person_certificate VARCHAR(100),
    company_website VARCHAR(255),
    company_legal_person VARCHAR(100),
    province VARCHAR(50),
    city VARCHAR(50),
    district VARCHAR(50),
    organization_code VARCHAR(100),
    reconciliation_date DATE,
    foreign_currency VARCHAR(10),
    remarks TEXT,
    trademark_certificate BOOLEAN DEFAULT FALSE,
    print_authorization BOOLEAN DEFAULT FALSE,
    inspection_report BOOLEAN DEFAULT FALSE,
    free_samples BOOLEAN DEFAULT FALSE,
    advance_payment_control BOOLEAN DEFAULT FALSE,
    warehouse BOOLEAN DEFAULT FALSE,
    old_customer BOOLEAN DEFAULT FALSE,
    customer_archive_review BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (package_method_id) REFERENCES package_methods(id),
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
);

-- 40. 客户联系人表
CREATE TABLE IF NOT EXISTS customer_management_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    contact_name VARCHAR(100),
    position VARCHAR(100),
    mobile VARCHAR(100),
    fax VARCHAR(100),
    qq VARCHAR(100),
    wechat VARCHAR(100),
    email VARCHAR(255),
    department VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_management(id)
);

-- 41. 客户送货地址表
CREATE TABLE IF NOT EXISTS customer_management_delivery_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    delivery_address TEXT,
    contact_name VARCHAR(100),
    contact_method VARCHAR(150),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_management(id)
);

-- 42. 客户开票单位表
CREATE TABLE IF NOT EXISTS customer_management_invoice_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    invoice_unit VARCHAR(255),
    taxpayer_id VARCHAR(100),
    invoice_address VARCHAR(255),
    invoice_phone VARCHAR(100),
    invoice_bank VARCHAR(255),
    invoice_account VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_management(id)
);

-- 43. 客户付款单位表
CREATE TABLE IF NOT EXISTS customer_management_payment_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    payment_unit VARCHAR(255),
    unit_code VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_management(id)
);

-- 44. 客户归属公司表
CREATE TABLE IF NOT EXISTS customer_management_affiliated_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    affiliated_company VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_management(id)
);

-- 45. 供应商管理表
CREATE TABLE IF NOT EXISTS supplier_management (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_code VARCHAR(50),
    supplier_name VARCHAR(255) NOT NULL,
    supplier_abbreviation VARCHAR(100),
    supplier_category_id UUID,
    purchaser_id UUID,
    region VARCHAR(100),
    delivery_method_id UUID,
    tax_rate_id UUID,
    tax_rate NUMERIC(5, 2),
    currency_id UUID,
    payment_method_id UUID,
    deposit_ratio NUMERIC(10, 4) DEFAULT 0,
    delivery_preparation_days INTEGER DEFAULT 0,
    copyright_square_price NUMERIC(15, 4) DEFAULT 0,
    supplier_level VARCHAR(10),
    organization_code VARCHAR(100),
    company_website VARCHAR(255),
    foreign_currency_id UUID,
    barcode_prefix_code VARCHAR(50),
    business_start_date DATE,
    business_end_date DATE,
    production_permit_start_date DATE,
    production_permit_end_date DATE,
    inspection_report_start_date DATE,
    inspection_report_end_date DATE,
    barcode_authorization NUMERIC(15, 4) DEFAULT 0,
    ufriend_code VARCHAR(100),
    enterprise_type VARCHAR(50),
    province VARCHAR(50),
    city VARCHAR(50),
    district VARCHAR(50),
    company_address TEXT,
    remarks TEXT,
    image_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 46. 供应商联系人表
CREATE TABLE IF NOT EXISTS supplier_management_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id UUID NOT NULL,
    contact_name VARCHAR(100),
    landline VARCHAR(100),
    mobile VARCHAR(100),
    fax VARCHAR(100),
    qq VARCHAR(100),
    wechat VARCHAR(100),
    email VARCHAR(255),
    department VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES supplier_management(id)
);

-- 47. 供应商发货地址表
CREATE TABLE IF NOT EXISTS supplier_management_delivery_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id UUID NOT NULL,
    delivery_address TEXT,
    contact_name VARCHAR(100),
    contact_method VARCHAR(150),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES supplier_management(id)
);

-- 48. 供应商开票单位表
CREATE TABLE IF NOT EXISTS supplier_management_invoice_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id UUID NOT NULL,
    invoice_unit VARCHAR(255),
    taxpayer_id VARCHAR(100),
    invoice_address VARCHAR(255),
    invoice_phone VARCHAR(100),
    invoice_bank VARCHAR(255),
    invoice_account VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES supplier_management(id)
);

-- 49. 供应商归属公司表
CREATE TABLE IF NOT EXISTS supplier_management_affiliated_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id UUID NOT NULL,
    affiliated_company VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES supplier_management(id)
);

-- 50. 材料表
CREATE TABLE IF NOT EXISTS materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_code VARCHAR(50),
    material_name VARCHAR(255) NOT NULL,
    material_category_id UUID,
    material_attribute VARCHAR(50),
    unit_id UUID,
    auxiliary_unit_id UUID,
    is_blown_film BOOLEAN DEFAULT FALSE,
    unit_no_conversion BOOLEAN DEFAULT FALSE,
    width_mm NUMERIC(10, 3),
    thickness_um NUMERIC(10, 3),
    specification_model VARCHAR(200),
    density NUMERIC(10, 4),
    conversion_factor NUMERIC(10, 4) DEFAULT 1,
    sales_unit_id UUID,
    inspection_type VARCHAR(20) DEFAULT 'spot_check',
    is_paper BOOLEAN DEFAULT FALSE,
    is_surface_printing_ink BOOLEAN DEFAULT FALSE,
    length_mm NUMERIC(10, 3),
    height_mm NUMERIC(10, 3),
    min_stock_start NUMERIC(15, 3),
    min_stock_end NUMERIC(15, 3),
    max_stock NUMERIC(15, 3),
    shelf_life_days INTEGER,
    warning_days INTEGER DEFAULT 0,
    standard_m_per_roll NUMERIC(10, 3) DEFAULT 0,
    is_carton BOOLEAN DEFAULT FALSE,
    is_uv_ink BOOLEAN DEFAULT FALSE,
    wind_tolerance_mm NUMERIC(10, 3) DEFAULT 0,
    tongue_mm NUMERIC(10, 3) DEFAULT 0,
    purchase_price NUMERIC(15, 4) DEFAULT 0,
    latest_purchase_price NUMERIC(15, 4) DEFAULT 0,
    latest_tax_included_price NUMERIC(15, 4),
    material_formula_id UUID,
    is_paper_core BOOLEAN DEFAULT FALSE,
    is_tube_film BOOLEAN DEFAULT FALSE,
    loss_1 NUMERIC(10, 4),
    loss_2 NUMERIC(10, 4),
    forward_formula VARCHAR(200),
    reverse_formula VARCHAR(200),
    sales_price NUMERIC(15, 4),
    subject_id UUID,
    uf_code VARCHAR(100),
    material_formula_reverse BOOLEAN DEFAULT FALSE,
    is_hot_stamping BOOLEAN DEFAULT FALSE,
    material_position VARCHAR(200),
    carton_spec_volume NUMERIC(15, 6),
    security_code VARCHAR(100),
    substitute_material_category_id UUID,
    scan_batch VARCHAR(100),
    is_woven_bag BOOLEAN DEFAULT FALSE,
    is_zipper BOOLEAN DEFAULT FALSE,
    remarks TEXT,
    is_self_made BOOLEAN DEFAULT FALSE,
    no_interface BOOLEAN DEFAULT FALSE,
    cost_object_required BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_category_id) REFERENCES material_categories(id)
);

-- 51. 材料属性表
CREATE TABLE IF NOT EXISTS material_properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID NOT NULL,
    property_name VARCHAR(100),
    property_value VARCHAR(255),
    property_unit VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

-- 52. 材料供应商表
CREATE TABLE IF NOT EXISTS material_suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID NOT NULL,
    supplier_id UUID,
    supplier_material_code VARCHAR(100),
    supplier_price NUMERIC(15, 4),
    is_primary BOOLEAN DEFAULT FALSE,
    delivery_days INTEGER,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

-- 53. 产品表
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(20) DEFAULT 'finished',
    category_id UUID,
    short_name VARCHAR(100),
    english_name VARCHAR(200),
    brand VARCHAR(100),
    model VARCHAR(100),
    specification TEXT,
    customer_id UUID,
    bag_type_id UUID,
    salesperson_id UUID,
    compound_quantity INTEGER DEFAULT 0,
    small_inventory INTEGER DEFAULT 0,
    large_inventory INTEGER DEFAULT 0,
    international_standard VARCHAR(100),
    domestic_standard VARCHAR(100),
    is_unlimited_quantity BOOLEAN DEFAULT FALSE,
    is_compound_needed BOOLEAN DEFAULT FALSE,
    is_inspection_needed BOOLEAN DEFAULT FALSE,
    is_public_product BOOLEAN DEFAULT FALSE,
    is_packaging_needed BOOLEAN DEFAULT FALSE,
    is_changing BOOLEAN DEFAULT FALSE,
    material_info TEXT,
    compound_amount INTEGER DEFAULT 0,
    sales_amount INTEGER DEFAULT 0,
    contract_amount INTEGER DEFAULT 0,
    inventory_amount INTEGER DEFAULT 0,
    thickness NUMERIC(8, 3),
    width NUMERIC(8, 2),
    length NUMERIC(10, 2),
    material_type VARCHAR(100),
    transparency NUMERIC(5, 2),
    tensile_strength NUMERIC(8, 2),
    base_unit VARCHAR(20) DEFAULT 'm²',
    package_unit VARCHAR(20),
    conversion_rate NUMERIC(10, 4) DEFAULT 1,
    net_weight NUMERIC(10, 3),
    gross_weight NUMERIC(10, 3),
    standard_cost NUMERIC(15, 4),
    standard_price NUMERIC(15, 4),
    currency VARCHAR(10) DEFAULT 'CNY',
    safety_stock NUMERIC(15, 3) DEFAULT 0,
    min_order_qty NUMERIC(15, 3) DEFAULT 1,
    max_order_qty NUMERIC(15, 3),
    lead_time INTEGER DEFAULT 0,
    shelf_life INTEGER,
    storage_condition VARCHAR(200),
    quality_standard VARCHAR(200),
    inspection_method VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active',
    is_sellable BOOLEAN DEFAULT TRUE,
    is_purchasable BOOLEAN DEFAULT TRUE,
    is_producible BOOLEAN DEFAULT TRUE,
    custom_fields JSONB DEFAULT '{}',
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES product_categories(id),
    FOREIGN KEY (customer_id) REFERENCES customer_management(id),
    FOREIGN KEY (bag_type_id) REFERENCES bag_types(id)
);

-- 54. 产品结构表
CREATE TABLE IF NOT EXISTS product_structures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL,
    length INTEGER DEFAULT 0,
    width INTEGER DEFAULT 0,
    height INTEGER DEFAULT 0,
    expand_length INTEGER DEFAULT 0,
    expand_width INTEGER DEFAULT 0,
    expand_height INTEGER DEFAULT 0,
    material_length INTEGER DEFAULT 0,
    material_width INTEGER DEFAULT 0,
    material_height INTEGER DEFAULT 0,
    single_length INTEGER DEFAULT 0,
    single_width INTEGER DEFAULT 0,
    single_height INTEGER DEFAULT 0,
    blue_color VARCHAR(50),
    red_color VARCHAR(50),
    other_color VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 55. 产品客户需求表
CREATE TABLE IF NOT EXISTS product_customer_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL,
    appearance_requirements VARCHAR(200),
    surface_treatment VARCHAR(200),
    printing_requirements VARCHAR(200),
    color_requirements VARCHAR(200),
    pattern_requirements VARCHAR(200),
    cutting_method VARCHAR(200),
    cutting_width INTEGER DEFAULT 0,
    cutting_length INTEGER DEFAULT 0,
    cutting_thickness INTEGER DEFAULT 0,
    optical_distance INTEGER DEFAULT 0,
    optical_width INTEGER DEFAULT 0,
    bag_sealing_up VARCHAR(200),
    bag_sealing_down VARCHAR(200),
    bag_sealing_left VARCHAR(200),
    bag_sealing_right VARCHAR(200),
    bag_sealing_middle VARCHAR(200),
    bag_sealing_inner VARCHAR(200),
    bag_length_tolerance VARCHAR(200),
    bag_width_tolerance VARCHAR(200),
    packaging_method VARCHAR(200),
    packaging_requirements VARCHAR(200),
    packaging_material VARCHAR(200),
    packaging_quantity INTEGER DEFAULT 0,
    packaging_specifications VARCHAR(200),
    tensile_strength VARCHAR(200),
    thermal_shrinkage VARCHAR(200),
    impact_strength VARCHAR(200),
    thermal_tensile_strength VARCHAR(200),
    water_vapor_permeability VARCHAR(200),
    heat_shrinkage_curve VARCHAR(200),
    melt_index VARCHAR(200),
    gas_permeability VARCHAR(200),
    custom_1 VARCHAR(200),
    custom_2 VARCHAR(200),
    custom_3 VARCHAR(200),
    custom_4 VARCHAR(200),
    custom_5 VARCHAR(200),
    custom_6 VARCHAR(200),
    custom_7 VARCHAR(200),
    custom_8 VARCHAR(200),
    custom_9 VARCHAR(200),
    custom_10 VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 56. 产品工序关联表
CREATE TABLE IF NOT EXISTS product_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL,
    process_id UUID NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_required BOOLEAN DEFAULT TRUE,
    duration_hours FLOAT,
    cost_per_unit NUMERIC(10, 4),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (process_id) REFERENCES processes(id)
);

-- 57. 产品材料关联表
CREATE TABLE IF NOT EXISTS product_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL,
    material_id UUID NOT NULL,
    usage_quantity NUMERIC(10, 4),
    usage_unit VARCHAR(20),
    sort_order INTEGER DEFAULT 0,
    is_main_material BOOLEAN DEFAULT FALSE,
    cost_per_unit NUMERIC(10, 4),
    supplier_id UUID,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

-- 58. 产品理化指标表
CREATE TABLE IF NOT EXISTS product_quality_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL,
    tensile_strength_longitudinal VARCHAR(100),
    tensile_strength_transverse VARCHAR(100),
    thermal_shrinkage_longitudinal VARCHAR(100),
    thermal_shrinkage_transverse VARCHAR(100),
    puncture_strength VARCHAR(100),
    optical_properties VARCHAR(100),
    heat_seal_temperature VARCHAR(100),
    heat_seal_tensile_strength VARCHAR(100),
    water_vapor_permeability VARCHAR(100),
    oxygen_permeability VARCHAR(100),
    friction_coefficient VARCHAR(100),
    peel_strength VARCHAR(100),
    test_standard VARCHAR(200),
    test_basis VARCHAR(200),
    indicator_1 VARCHAR(100),
    indicator_2 VARCHAR(100),
    indicator_3 VARCHAR(100),
    indicator_4 VARCHAR(100),
    indicator_5 VARCHAR(100),
    indicator_6 VARCHAR(100),
    indicator_7 VARCHAR(100),
    indicator_8 VARCHAR(100),
    indicator_9 VARCHAR(100),
    indicator_10 VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 59. 产品图片表
CREATE TABLE IF NOT EXISTS product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL,
    image_name VARCHAR(255),
    image_url VARCHAR(500),
    image_type VARCHAR(50),
    file_size INTEGER,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_product_categories_name ON product_categories(category_name);
CREATE INDEX IF NOT EXISTS idx_package_methods_name ON package_methods(package_name);
CREATE INDEX IF NOT EXISTS idx_delivery_methods_name ON delivery_methods(delivery_name);
CREATE INDEX IF NOT EXISTS idx_color_cards_code ON color_cards(color_code);
CREATE INDEX IF NOT EXISTS idx_units_name ON units(unit_name);
CREATE INDEX IF NOT EXISTS idx_customer_category_name ON customer_category_management(category_name);
CREATE INDEX IF NOT EXISTS idx_supplier_category_name ON supplier_category_management(category_name);
CREATE INDEX IF NOT EXISTS idx_specifications_name ON specifications(spec_name);
CREATE INDEX IF NOT EXISTS idx_currencies_code ON currencies(currency_code);
CREATE INDEX IF NOT EXISTS idx_tax_rates_name ON tax_rates(tax_name);
CREATE INDEX IF NOT EXISTS idx_settlement_methods_name ON settlement_methods(settlement_name);
CREATE INDEX IF NOT EXISTS idx_account_management_name ON account_management(account_name);
CREATE INDEX IF NOT EXISTS idx_payment_methods_name ON payment_methods(payment_name);
CREATE INDEX IF NOT EXISTS idx_ink_options_name ON ink_options(option_name);
CREATE INDEX IF NOT EXISTS idx_quote_freights_region ON quote_freights(region);
CREATE INDEX IF NOT EXISTS idx_material_categories_name ON material_categories(material_name);
CREATE INDEX IF NOT EXISTS idx_calculation_parameters_name ON calculation_parameters(parameter_name);
CREATE INDEX IF NOT EXISTS idx_calculation_schemes_name ON calculation_schemes(scheme_name);
CREATE INDEX IF NOT EXISTS idx_loss_types_name ON loss_types(loss_type_name);
CREATE INDEX IF NOT EXISTS idx_machines_code ON machines(machine_code);
CREATE INDEX IF NOT EXISTS idx_machines_name ON machines(machine_name);
CREATE INDEX IF NOT EXISTS idx_quote_inks_name ON quote_inks(category_name);
CREATE INDEX IF NOT EXISTS idx_quote_materials_name ON quote_materials(material_name);
CREATE INDEX IF NOT EXISTS idx_quote_accessories_name ON quote_accessories(material_name);
CREATE INDEX IF NOT EXISTS idx_departments_code ON departments(dept_code);
CREATE INDEX IF NOT EXISTS idx_departments_name ON departments(dept_name);
CREATE INDEX IF NOT EXISTS idx_positions_name ON positions(position_name);
CREATE INDEX IF NOT EXISTS idx_employees_id ON employees(employee_id);
CREATE INDEX IF NOT EXISTS idx_employees_name ON employees(employee_name);
CREATE INDEX IF NOT EXISTS idx_warehouses_code ON warehouses(warehouse_code);
CREATE INDEX IF NOT EXISTS idx_warehouses_name ON warehouses(warehouse_name);
CREATE INDEX IF NOT EXISTS idx_process_categories_name ON process_categories(process_name);
CREATE INDEX IF NOT EXISTS idx_bag_types_name ON bag_types(bag_type_name);
CREATE INDEX IF NOT EXISTS idx_processes_name ON processes(process_name);
CREATE INDEX IF NOT EXISTS idx_team_groups_code ON team_groups(team_code);
CREATE INDEX IF NOT EXISTS idx_team_groups_name ON team_groups(team_name);
CREATE INDEX IF NOT EXISTS idx_customer_management_code ON customer_management(customer_code);
CREATE INDEX IF NOT EXISTS idx_customer_management_name ON customer_management(customer_name);
CREATE INDEX IF NOT EXISTS idx_supplier_management_code ON supplier_management(supplier_code);
CREATE INDEX IF NOT EXISTS idx_supplier_management_name ON supplier_management(supplier_name);
CREATE INDEX IF NOT EXISTS idx_materials_code ON materials(material_code);
CREATE INDEX IF NOT EXISTS idx_materials_name ON materials(material_name);
CREATE INDEX IF NOT EXISTS idx_products_code ON products(product_code);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name);

-- 注释
COMMENT ON SCHEMA yiboshuo IS 'Yiboshuo租户数据schema'; 