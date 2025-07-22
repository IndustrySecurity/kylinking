-- 创建 yiboshuo schema 下的 inventory 相关表
-- 基于 app/models/business/inventory.py

-- 设置 schema
SET search_path TO yiboshuo;

-- 1. 库存表
CREATE TABLE IF NOT EXISTS inventories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联字段
    warehouse_id UUID NOT NULL,
    product_id UUID,
    material_id UUID,
    
    -- 库存信息
    current_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    available_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    reserved_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    in_transit_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    
    -- 单位信息
    unit VARCHAR(20) NOT NULL,
    
    -- 成本信息
    unit_cost NUMERIC(15, 4),
    total_cost NUMERIC(18, 4),
    
    -- 批次信息
    batch_number VARCHAR(100),
    production_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,
    
    -- 位置信息
    location_code VARCHAR(100),
    storage_area VARCHAR(100),
    
    -- 库存状态
    inventory_status VARCHAR(20) DEFAULT 'normal',
    quality_status VARCHAR(20) DEFAULT 'qualified',
    
    -- 安全库存设定
    safety_stock NUMERIC(15, 3) DEFAULT 0,
    min_stock NUMERIC(15, 3) DEFAULT 0,
    max_stock NUMERIC(15, 3),
    
    -- 盘点信息
    last_count_date TIMESTAMPTZ,
    last_count_quantity NUMERIC(15, 3),
    variance_quantity NUMERIC(15, 3) DEFAULT 0,
    
    -- 扩展字段
    custom_fields JSONB DEFAULT '{}',
    
    -- 系统字段
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 库存表索引
CREATE INDEX IF NOT EXISTS ix_inventory_warehouse_product ON inventories (warehouse_id, product_id);
CREATE INDEX IF NOT EXISTS ix_inventory_warehouse_material ON inventories (warehouse_id, material_id);
CREATE INDEX IF NOT EXISTS ix_inventory_batch ON inventories (batch_number);
CREATE INDEX IF NOT EXISTS ix_inventory_location ON inventories (warehouse_id, location_code);
CREATE INDEX IF NOT EXISTS ix_inventory_status ON inventories (inventory_status, quality_status);

-- 2. 库存流水表
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联字段
    inventory_id UUID NOT NULL,
    warehouse_id UUID NOT NULL,
    product_id UUID,
    material_id UUID,
    
    -- 交易信息
    transaction_number VARCHAR(100) UNIQUE NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    transaction_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- 数量变动
    quantity_change NUMERIC(15, 3) NOT NULL,
    quantity_before NUMERIC(15, 3) NOT NULL,
    quantity_after NUMERIC(15, 3) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    
    -- 成本信息
    unit_price NUMERIC(15, 4),
    total_amount NUMERIC(18, 4),
    
    -- 业务关联
    source_document_type VARCHAR(50),
    source_document_id UUID,
    source_document_number VARCHAR(100),
    
    -- 批次和位置信息
    batch_number VARCHAR(100),
    from_location VARCHAR(100),
    to_location VARCHAR(100),
    
    -- 业务伙伴信息
    customer_id UUID,
    supplier_id UUID,
    
    -- 审核信息
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    
    -- 扩展信息
    reason VARCHAR(500),
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 系统字段
    is_cancelled BOOLEAN DEFAULT FALSE,
    cancelled_by UUID,
    cancelled_at TIMESTAMPTZ,
    cancel_reason VARCHAR(500),
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 库存流水表索引
CREATE INDEX IF NOT EXISTS ix_inventory_transaction_inventory ON inventory_transactions (inventory_id);
CREATE INDEX IF NOT EXISTS ix_inventory_transaction_warehouse ON inventory_transactions (warehouse_id);
CREATE INDEX IF NOT EXISTS ix_inventory_transaction_type_date ON inventory_transactions (transaction_type, transaction_date);
CREATE INDEX IF NOT EXISTS ix_inventory_transaction_source ON inventory_transactions (source_document_type, source_document_id);
CREATE INDEX IF NOT EXISTS ix_inventory_transaction_number ON inventory_transactions (transaction_number);
CREATE INDEX IF NOT EXISTS ix_inventory_transaction_batch ON inventory_transactions (batch_number);
CREATE INDEX IF NOT EXISTS ix_inventory_transaction_status ON inventory_transactions (approval_status, is_cancelled);

-- 3. 盘点计划表
CREATE TABLE IF NOT EXISTS inventory_count_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 盘点基本信息
    plan_number VARCHAR(100) UNIQUE NOT NULL,
    plan_name VARCHAR(200) NOT NULL,
    count_type VARCHAR(20) NOT NULL,
    
    -- 盘点范围
    warehouse_ids JSONB,
    product_categories JSONB,
    material_categories JSONB,
    location_codes JSONB,
    
    -- 盘点时间
    plan_start_date TIMESTAMPTZ NOT NULL,
    plan_end_date TIMESTAMPTZ NOT NULL,
    actual_start_date TIMESTAMPTZ,
    actual_end_date TIMESTAMPTZ,
    
    -- 盘点状态
    status VARCHAR(20) DEFAULT 'draft',
    
    -- 盘点人员
    count_team JSONB,
    supervisor_id UUID,
    
    -- 盘点说明
    description TEXT,
    notes TEXT,
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. 盘点记录表
CREATE TABLE IF NOT EXISTS inventory_count_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联盘点计划
    count_plan_id UUID NOT NULL REFERENCES inventory_count_plans(id),
    
    -- 关联库存
    inventory_id UUID NOT NULL,
    warehouse_id UUID NOT NULL,
    product_id UUID,
    material_id UUID,
    
    -- 盘点数据
    book_quantity NUMERIC(15, 3) NOT NULL,
    actual_quantity NUMERIC(15, 3),
    variance_quantity NUMERIC(15, 3),
    variance_rate NUMERIC(8, 4),
    
    -- 盘点详情
    batch_number VARCHAR(100),
    location_code VARCHAR(100),
    unit VARCHAR(20) NOT NULL,
    
    -- 盘点人员和时间
    count_by UUID,
    count_date TIMESTAMPTZ,
    recount_by UUID,
    recount_date TIMESTAMPTZ,
    
    -- 差异处理
    variance_reason VARCHAR(500),
    is_adjusted BOOLEAN DEFAULT FALSE,
    adjustment_transaction_id UUID,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending',
    
    -- 备注
    notes TEXT,
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. 入库单主表
CREATE TABLE IF NOT EXISTS inbound_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 单据信息
    order_number VARCHAR(100) UNIQUE NOT NULL,
    order_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    order_type VARCHAR(20) DEFAULT 'finished_goods',
    
    -- 仓库信息
    warehouse_id UUID NOT NULL,
    warehouse_name VARCHAR(200),
    
    -- 入库人员信息
    inbound_person_id UUID REFERENCES employees(id),
    department_id UUID REFERENCES departments(id),
    
    -- 托盘信息
    pallet_barcode VARCHAR(200),
    pallet_count INTEGER DEFAULT 0,
    
    -- 单据状态
    status VARCHAR(20) DEFAULT 'draft',
    
    -- 审核信息
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    
    -- 业务关联
    source_document_type VARCHAR(50),
    source_document_id UUID,
    source_document_number VARCHAR(100),
    
    -- 客户供应商信息
    customer_id UUID,
    supplier_id UUID,
    
    -- 扩展字段
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 入库单主表索引
CREATE INDEX IF NOT EXISTS ix_inbound_order_number ON inbound_orders (order_number);
CREATE INDEX IF NOT EXISTS ix_inbound_order_date ON inbound_orders (order_date);
CREATE INDEX IF NOT EXISTS ix_inbound_order_warehouse ON inbound_orders (warehouse_id);
CREATE INDEX IF NOT EXISTS ix_inbound_order_status ON inbound_orders (status, approval_status);
CREATE INDEX IF NOT EXISTS ix_inbound_order_source ON inbound_orders (source_document_type, source_document_id);

-- 6. 入库单明细表
CREATE TABLE IF NOT EXISTS inbound_order_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联主表
    inbound_order_id UUID NOT NULL REFERENCES inbound_orders(id),
    
    -- 产品信息
    product_id UUID,
    product_name VARCHAR(200),
    product_code VARCHAR(100),
    product_spec VARCHAR(500),
    
    -- 数量信息
    inbound_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    inbound_kg_quantity NUMERIC(15, 3),
    inbound_m_quantity NUMERIC(15, 3),
    inbound_roll_quantity NUMERIC(15, 3),
    box_quantity NUMERIC(15, 3),
    case_quantity INTEGER,
    
    -- 单位信息
    unit VARCHAR(20) NOT NULL,
    kg_unit VARCHAR(20) DEFAULT 'kg',
    m_unit VARCHAR(20) DEFAULT 'm',
    
    -- 批次信息
    batch_number VARCHAR(100),
    production_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,
    
    -- 质量信息
    quality_status VARCHAR(20) DEFAULT 'qualified',
    quality_certificate VARCHAR(200),
    
    -- 成本信息
    unit_cost NUMERIC(15, 4),
    total_cost NUMERIC(18, 4),
    
    -- 库位信息
    location_code VARCHAR(100),
    actual_location_code VARCHAR(100),
    
    -- 包装信息
    package_quantity NUMERIC(15, 3),
    package_unit VARCHAR(20),
    
    -- 行号和排序
    line_number INTEGER,
    sort_order INTEGER DEFAULT 0,
    
    -- 扩展字段
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 入库单明细表索引
CREATE INDEX IF NOT EXISTS ix_inbound_detail_order ON inbound_order_details (inbound_order_id);
CREATE INDEX IF NOT EXISTS ix_inbound_detail_product ON inbound_order_details (product_id);
CREATE INDEX IF NOT EXISTS ix_inbound_detail_batch ON inbound_order_details (batch_number);
CREATE INDEX IF NOT EXISTS ix_inbound_detail_location ON inbound_order_details (location_code);

-- 7. 出库单主表
CREATE TABLE IF NOT EXISTS outbound_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 单据信息
    order_number VARCHAR(100) UNIQUE NOT NULL,
    order_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    order_type VARCHAR(20) DEFAULT 'finished_goods',
    
    -- 仓库信息
    warehouse_id UUID NOT NULL,
    warehouse_name VARCHAR(200),
    
    -- 出库人员信息
    outbound_person_id UUID REFERENCES employees(id),
    department_id UUID REFERENCES departments(id),
    
    -- 托盘信息
    pallet_barcode VARCHAR(200),
    pallet_count INTEGER DEFAULT 0,
    
    -- 单据状态
    status VARCHAR(20) DEFAULT 'draft',
    
    -- 审核信息
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    
    -- 业务关联
    source_document_type VARCHAR(50),
    source_document_id UUID,
    source_document_number VARCHAR(100),
    
    -- 客户信息
    customer_id UUID,
    customer_name VARCHAR(200),
    
    -- 物流信息
    delivery_address TEXT,
    delivery_contact VARCHAR(100),
    delivery_phone VARCHAR(50),
    expected_delivery_date TIMESTAMPTZ,
    actual_delivery_date TIMESTAMPTZ,
    
    -- 扩展字段
    remark TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 出库单主表索引
CREATE INDEX IF NOT EXISTS ix_outbound_order_number ON outbound_orders (order_number);
CREATE INDEX IF NOT EXISTS ix_outbound_order_date ON outbound_orders (order_date);
CREATE INDEX IF NOT EXISTS ix_outbound_order_warehouse ON outbound_orders (warehouse_id);
CREATE INDEX IF NOT EXISTS ix_outbound_order_status ON outbound_orders (status, approval_status);
CREATE INDEX IF NOT EXISTS ix_outbound_order_source ON outbound_orders (source_document_type, source_document_id);
CREATE INDEX IF NOT EXISTS ix_outbound_order_customer ON outbound_orders (customer_id);

-- 8. 出库单明细表
CREATE TABLE IF NOT EXISTS outbound_order_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联主表
    outbound_order_id UUID NOT NULL REFERENCES outbound_orders(id),
    
    -- 产品信息
    product_id UUID,
    product_name VARCHAR(200),
    product_code VARCHAR(100),
    product_spec VARCHAR(500),
    
    -- 数量信息
    outbound_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    outbound_kg_quantity NUMERIC(15, 3),
    outbound_m_quantity NUMERIC(15, 3),
    outbound_roll_quantity NUMERIC(15, 3),
    box_quantity NUMERIC(15, 3),
    case_quantity INTEGER,
    
    -- 单位信息
    unit VARCHAR(20) NOT NULL,
    kg_unit VARCHAR(20) DEFAULT 'kg',
    m_unit VARCHAR(20) DEFAULT 'm',
    
    -- 批次信息
    batch_number VARCHAR(100),
    production_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,
    
    -- 质量信息
    quality_status VARCHAR(20) DEFAULT 'qualified',
    quality_certificate VARCHAR(200),
    
    -- 成本信息
    unit_cost NUMERIC(15, 4),
    total_cost NUMERIC(18, 4),
    
    -- 库位信息
    location_code VARCHAR(100),
    actual_location_code VARCHAR(100),
    
    -- 包装信息
    package_quantity NUMERIC(15, 3),
    package_unit VARCHAR(20),
    
    -- 库存关联
    inventory_id UUID,
    available_quantity NUMERIC(15, 3),
    
    -- 行号和排序
    line_number INTEGER,
    sort_order INTEGER DEFAULT 0,
    
    -- 扩展字段
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 出库单明细表索引
CREATE INDEX IF NOT EXISTS ix_outbound_detail_order ON outbound_order_details (outbound_order_id);
CREATE INDEX IF NOT EXISTS ix_outbound_detail_product ON outbound_order_details (product_id);
CREATE INDEX IF NOT EXISTS ix_outbound_detail_batch ON outbound_order_details (batch_number);
CREATE INDEX IF NOT EXISTS ix_outbound_detail_location ON outbound_order_details (location_code);
CREATE INDEX IF NOT EXISTS ix_outbound_detail_inventory ON outbound_order_details (inventory_id);

-- 9. 材料入库单主表
CREATE TABLE IF NOT EXISTS material_inbound_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 单据信息
    order_number VARCHAR(100) UNIQUE NOT NULL,
    order_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    order_type VARCHAR(20) DEFAULT 'material',
    
    -- 仓库信息
    warehouse_id UUID NOT NULL,
    warehouse_name VARCHAR(200),
    
    -- 入库人员信息
    inbound_person_id UUID REFERENCES employees(id),
    department_id UUID REFERENCES departments(id),
    
    -- 托盘信息
    pallet_barcode VARCHAR(200),
    pallet_count INTEGER DEFAULT 0,
    
    -- 单据状态
    status VARCHAR(20) DEFAULT 'draft',
    
    -- 审核信息
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    
    -- 业务关联
    source_document_type VARCHAR(50),
    source_document_id UUID,
    source_document_number VARCHAR(100),
    
    -- 供应商信息
    supplier_id UUID,
    supplier_name VARCHAR(200),
    
    -- 扩展字段
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 材料入库单主表索引
CREATE INDEX IF NOT EXISTS ix_material_inbound_order_number ON material_inbound_orders (order_number);
CREATE INDEX IF NOT EXISTS ix_material_inbound_order_date ON material_inbound_orders (order_date);
CREATE INDEX IF NOT EXISTS ix_material_inbound_order_warehouse ON material_inbound_orders (warehouse_id);
CREATE INDEX IF NOT EXISTS ix_material_inbound_order_status ON material_inbound_orders (status, approval_status);
CREATE INDEX IF NOT EXISTS ix_material_inbound_order_source ON material_inbound_orders (source_document_type, source_document_id);
CREATE INDEX IF NOT EXISTS ix_material_inbound_order_supplier ON material_inbound_orders (supplier_id);

-- 10. 材料入库单明细表
CREATE TABLE IF NOT EXISTS material_inbound_order_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联主表
    material_inbound_order_id UUID NOT NULL REFERENCES material_inbound_orders(id),
    
    -- 材料信息
    material_id UUID,
    material_name VARCHAR(200),
    material_code VARCHAR(100),
    material_spec VARCHAR(500),
    
    -- 数量信息
    inbound_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    inbound_weight NUMERIC(15, 3),
    inbound_length NUMERIC(15, 3),
    inbound_rolls NUMERIC(15, 3),
    
    -- 单位信息
    unit VARCHAR(20) NOT NULL,
    weight_unit VARCHAR(20) DEFAULT 'kg',
    length_unit VARCHAR(20) DEFAULT 'm',
    
    -- 批次信息
    batch_number VARCHAR(100),
    production_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,
    
    -- 质量信息
    quality_status VARCHAR(20) DEFAULT 'qualified',
    quality_certificate VARCHAR(200),
    
    -- 成本信息
    unit_price NUMERIC(15, 4),
    total_amount NUMERIC(18, 4),
    
    -- 库位信息
    location_code VARCHAR(100),
    actual_location_code VARCHAR(100),
    
    -- 行号和排序
    line_number INTEGER,
    sort_order INTEGER DEFAULT 0,
    
    -- 扩展字段
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 材料入库单明细表索引
CREATE INDEX IF NOT EXISTS ix_material_inbound_detail_order ON material_inbound_order_details (material_inbound_order_id);
CREATE INDEX IF NOT EXISTS ix_material_inbound_detail_material ON material_inbound_order_details (material_id);
CREATE INDEX IF NOT EXISTS ix_material_inbound_detail_batch ON material_inbound_order_details (batch_number);
CREATE INDEX IF NOT EXISTS ix_material_inbound_detail_location ON material_inbound_order_details (location_code);

-- 11. 材料出库单主表
CREATE TABLE IF NOT EXISTS material_outbound_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 单据信息
    order_number VARCHAR(100) UNIQUE NOT NULL,
    order_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    order_type VARCHAR(20) DEFAULT 'material',
    
    -- 仓库信息
    warehouse_id UUID NOT NULL,
    warehouse_name VARCHAR(200),
    
    -- 出库人员信息
    outbound_person_id UUID REFERENCES employees(id),
    department_id UUID REFERENCES departments(id),
    
    -- 托盘信息
    pallet_barcode VARCHAR(200),
    pallet_count INTEGER DEFAULT 0,
    
    -- 单据状态
    status VARCHAR(20) DEFAULT 'draft',
    
    -- 审核信息
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    
    -- 业务关联
    source_document_type VARCHAR(50),
    source_document_id UUID,
    source_document_number VARCHAR(100),
    
    -- 领用部门信息
    requisition_department_id UUID REFERENCES departments(id),
    requisition_person_id UUID REFERENCES employees(id),
    requisition_purpose VARCHAR(200),
    
    -- 扩展字段
    remark TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 材料出库单主表索引
CREATE INDEX IF NOT EXISTS ix_material_outbound_order_number ON material_outbound_orders (order_number);
CREATE INDEX IF NOT EXISTS ix_material_outbound_order_date ON material_outbound_orders (order_date);
CREATE INDEX IF NOT EXISTS ix_material_outbound_order_warehouse ON material_outbound_orders (warehouse_id);
CREATE INDEX IF NOT EXISTS ix_material_outbound_order_status ON material_outbound_orders (status, approval_status);
CREATE INDEX IF NOT EXISTS ix_material_outbound_order_source ON material_outbound_orders (source_document_type, source_document_id);
CREATE INDEX IF NOT EXISTS ix_material_outbound_order_requisition_dept ON material_outbound_orders (requisition_department_id);
CREATE INDEX IF NOT EXISTS ix_material_outbound_order_requisition_person ON material_outbound_orders (requisition_person_id);

-- 12. 材料出库单明细表
CREATE TABLE IF NOT EXISTS material_outbound_order_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联主表
    material_outbound_order_id UUID NOT NULL REFERENCES material_outbound_orders(id),
    
    -- 材料信息
    material_id UUID,
    material_name VARCHAR(200),
    material_code VARCHAR(100),
    material_spec VARCHAR(500),
    
    -- 数量信息
    outbound_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    outbound_weight NUMERIC(15, 3),
    outbound_length NUMERIC(15, 3),
    outbound_rolls NUMERIC(15, 3),
    
    -- 单位信息
    unit VARCHAR(20) NOT NULL,
    weight_unit VARCHAR(20) DEFAULT 'kg',
    length_unit VARCHAR(20) DEFAULT 'm',
    
    -- 批次信息
    batch_number VARCHAR(100),
    production_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,
    
    -- 质量信息
    quality_status VARCHAR(20) DEFAULT 'qualified',
    quality_certificate VARCHAR(200),
    
    -- 成本信息
    unit_price NUMERIC(15, 4),
    total_amount NUMERIC(18, 4),
    
    -- 库位信息
    location_code VARCHAR(100),
    actual_location_code VARCHAR(100),
    
    -- 库存关联
    inventory_id UUID,
    available_quantity NUMERIC(15, 3),
    
    -- 行号和排序
    line_number INTEGER,
    sort_order INTEGER DEFAULT 0,
    
    -- 扩展字段
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 材料出库单明细表索引
CREATE INDEX IF NOT EXISTS ix_material_outbound_detail_order ON material_outbound_order_details (material_outbound_order_id);
CREATE INDEX IF NOT EXISTS ix_material_outbound_detail_material ON material_outbound_order_details (material_id);
CREATE INDEX IF NOT EXISTS ix_material_outbound_detail_batch ON material_outbound_order_details (batch_number);
CREATE INDEX IF NOT EXISTS ix_material_outbound_detail_location ON material_outbound_order_details (location_code);
CREATE INDEX IF NOT EXISTS ix_material_outbound_detail_inventory ON material_outbound_order_details (inventory_id);

-- 13. 材料盘点计划表
CREATE TABLE IF NOT EXISTS material_count_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 盘点基本信息
    count_number VARCHAR(100) UNIQUE NOT NULL,
    warehouse_id UUID NOT NULL,
    warehouse_name VARCHAR(200) NOT NULL,
    warehouse_code VARCHAR(100),
    
    -- 盘点人员信息
    count_person_id UUID NOT NULL REFERENCES employees(id),
    department_id UUID REFERENCES departments(id),
    
    -- 盘点时间
    count_date TIMESTAMPTZ NOT NULL,
    
    -- 盘点状态
    status VARCHAR(20) DEFAULT 'draft',
    
    -- 备注
    notes TEXT,
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 材料盘点计划表索引
CREATE INDEX IF NOT EXISTS ix_material_count_plan_number ON material_count_plans (count_number);
CREATE INDEX IF NOT EXISTS ix_material_count_plan_warehouse ON material_count_plans (warehouse_id);
CREATE INDEX IF NOT EXISTS ix_material_count_plan_person ON material_count_plans (count_person_id);
CREATE INDEX IF NOT EXISTS ix_material_count_plan_department ON material_count_plans (department_id);
CREATE INDEX IF NOT EXISTS ix_material_count_plan_date ON material_count_plans (count_date);
CREATE INDEX IF NOT EXISTS ix_material_count_plan_status ON material_count_plans (status);

-- 14. 材料盘点记录表
CREATE TABLE IF NOT EXISTS material_count_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联盘点计划
    count_plan_id UUID NOT NULL REFERENCES material_count_plans(id),
    
    -- 关联库存
    inventory_id UUID,
    material_id UUID NOT NULL,
    
    -- 材料信息
    material_code VARCHAR(100),
    material_name VARCHAR(200) NOT NULL,
    material_spec VARCHAR(200),
    unit VARCHAR(20) NOT NULL,
    
    -- 盘点数据
    book_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    actual_quantity NUMERIC(15, 3),
    variance_quantity NUMERIC(15, 3),
    variance_rate NUMERIC(8, 4),
    
    -- 批次和位置信息
    batch_number VARCHAR(100),
    location_code VARCHAR(100),
    
    -- 差异处理
    variance_reason VARCHAR(500),
    is_adjusted BOOLEAN DEFAULT FALSE,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending',
    
    -- 备注
    notes TEXT,
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 材料盘点记录表索引
CREATE INDEX IF NOT EXISTS ix_material_count_records_plan ON material_count_records (count_plan_id);
CREATE INDEX IF NOT EXISTS ix_material_count_records_material ON material_count_records (material_id);
CREATE INDEX IF NOT EXISTS ix_material_count_records_status ON material_count_records (status);

-- 15. 材料调拨单主表
CREATE TABLE IF NOT EXISTS material_transfer_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 单据信息
    transfer_number VARCHAR(100) UNIQUE NOT NULL,
    transfer_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    transfer_type VARCHAR(20) DEFAULT 'warehouse',
    
    -- 调出信息
    from_warehouse_id UUID NOT NULL,
    from_warehouse_name VARCHAR(200),
    from_warehouse_code VARCHAR(100),
    
    -- 调入信息
    to_warehouse_id UUID NOT NULL,
    to_warehouse_name VARCHAR(200),
    to_warehouse_code VARCHAR(100),
    
    -- 调拨人员信息
    transfer_person_id UUID REFERENCES employees(id),
    department_id UUID REFERENCES departments(id),
    
    -- 单据状态
    status VARCHAR(20) DEFAULT 'draft',
    
    -- 审核信息
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    
    -- 执行信息
    executed_by UUID,
    executed_at TIMESTAMPTZ,
    
    -- 业务关联
    source_document_type VARCHAR(50),
    source_document_id UUID,
    source_document_number VARCHAR(100),
    
    -- 统计信息
    total_items INTEGER DEFAULT 0,
    total_quantity NUMERIC(15, 3) DEFAULT 0,
    total_amount NUMERIC(18, 4) DEFAULT 0,
    
    -- 物流信息
    transporter VARCHAR(200),
    transport_method VARCHAR(50),
    expected_arrival_date TIMESTAMPTZ,
    actual_arrival_date TIMESTAMPTZ,
    
    -- 扩展字段
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 材料调拨单主表索引
CREATE INDEX IF NOT EXISTS ix_material_transfer_order_number ON material_transfer_orders (transfer_number);
CREATE INDEX IF NOT EXISTS ix_material_transfer_order_from_warehouse ON material_transfer_orders (from_warehouse_id);
CREATE INDEX IF NOT EXISTS ix_material_transfer_order_to_warehouse ON material_transfer_orders (to_warehouse_id);
CREATE INDEX IF NOT EXISTS ix_material_transfer_order_person ON material_transfer_orders (transfer_person_id);
CREATE INDEX IF NOT EXISTS ix_material_transfer_order_department ON material_transfer_orders (department_id);
CREATE INDEX IF NOT EXISTS ix_material_transfer_order_date ON material_transfer_orders (transfer_date);
CREATE INDEX IF NOT EXISTS ix_material_transfer_order_status ON material_transfer_orders (status);

-- 16. 材料调拨单明细表
CREATE TABLE IF NOT EXISTS material_transfer_order_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联主表
    transfer_order_id UUID NOT NULL REFERENCES material_transfer_orders(id),
    
    -- 材料信息
    material_id UUID NOT NULL,
    material_name VARCHAR(200) NOT NULL,
    material_code VARCHAR(100),
    material_spec VARCHAR(500),
    
    -- 库存信息
    from_inventory_id UUID,
    current_stock NUMERIC(15, 3),
    available_quantity NUMERIC(15, 3),
    
    -- 调拨数量信息
    transfer_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    actual_transfer_quantity NUMERIC(15, 3),
    received_quantity NUMERIC(15, 3),
    
    -- 单位信息
    unit VARCHAR(20) NOT NULL,
    
    -- 批次信息
    batch_number VARCHAR(100),
    production_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,
    
    -- 成本信息
    unit_price NUMERIC(15, 4),
    total_amount NUMERIC(18, 4),
    
    -- 库位信息
    from_location_code VARCHAR(100),
    to_location_code VARCHAR(100),
    actual_to_location_code VARCHAR(100),
    
    -- 质量信息
    quality_status VARCHAR(20) DEFAULT 'qualified',
    quality_certificate VARCHAR(200),
    
    -- 状态
    detail_status VARCHAR(20) DEFAULT 'pending',
    
    -- 行号和排序
    line_number INTEGER,
    sort_order INTEGER DEFAULT 0,
    
    -- 扩展字段
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 材料调拨单明细表索引
CREATE INDEX IF NOT EXISTS ix_material_transfer_detail_order ON material_transfer_order_details (transfer_order_id);
CREATE INDEX IF NOT EXISTS ix_material_transfer_detail_material ON material_transfer_order_details (material_id);
CREATE INDEX IF NOT EXISTS ix_material_transfer_detail_status ON material_transfer_order_details (detail_status);

-- 17. 成品盘点计划表
CREATE TABLE IF NOT EXISTS product_count_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 盘点基本信息
    count_number VARCHAR(100) UNIQUE NOT NULL,
    warehouse_id UUID NOT NULL,
    warehouse_name VARCHAR(200) NOT NULL,
    warehouse_code VARCHAR(100),
    
    -- 盘点人员信息
    count_person_id UUID REFERENCES employees(id),
    department_id UUID REFERENCES departments(id),
    
    -- 盘点时间
    count_date TIMESTAMPTZ NOT NULL,
    
    -- 盘点状态
    status VARCHAR(20) DEFAULT 'draft',
    
    -- 备注
    notes TEXT,
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 成品盘点计划表索引
CREATE INDEX IF NOT EXISTS idx_product_count_plans_warehouse ON product_count_plans (warehouse_id);
CREATE INDEX IF NOT EXISTS idx_product_count_plans_count_date ON product_count_plans (count_date);
CREATE INDEX IF NOT EXISTS idx_product_count_plans_status ON product_count_plans (status);

-- 18. 成品盘点记录表
CREATE TABLE IF NOT EXISTS product_count_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联盘点计划
    count_plan_id UUID NOT NULL REFERENCES product_count_plans(id),
    
    -- 关联库存
    inventory_id UUID,
    product_id UUID NOT NULL,
    
    -- 产品信息
    product_code VARCHAR(100),
    product_name VARCHAR(200) NOT NULL,
    product_spec VARCHAR(200),
    base_unit VARCHAR(20) NOT NULL,
    
    -- 盘点数据
    book_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    actual_quantity NUMERIC(15, 3),
    variance_quantity NUMERIC(15, 3),
    variance_rate NUMERIC(8, 4),
    
    -- 批次和位置信息
    batch_number VARCHAR(100),
    production_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,
    location_code VARCHAR(100),
    
    -- 产品特有字段
    customer_id UUID,
    customer_name VARCHAR(200),
    bag_type_id UUID,
    bag_type_name VARCHAR(100),
    
    -- 包装信息
    package_unit VARCHAR(20),
    package_quantity NUMERIC(15, 3),
    net_weight NUMERIC(10, 3),
    gross_weight NUMERIC(10, 3),
    
    -- 差异处理
    variance_reason VARCHAR(500),
    is_adjusted BOOLEAN DEFAULT FALSE,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending',
    
    -- 备注
    notes TEXT,
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 成品盘点记录表索引
CREATE INDEX IF NOT EXISTS idx_product_count_records_count_plan ON product_count_records (count_plan_id);
CREATE INDEX IF NOT EXISTS idx_product_count_records_product ON product_count_records (product_id);
CREATE INDEX IF NOT EXISTS idx_product_count_records_status ON product_count_records (status);

-- 19. 成品调拨单主表
CREATE TABLE IF NOT EXISTS product_transfer_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 单据信息
    transfer_number VARCHAR(100) UNIQUE NOT NULL,
    transfer_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    transfer_type VARCHAR(20) DEFAULT 'warehouse',
    
    -- 调出信息
    from_warehouse_id UUID NOT NULL,
    from_warehouse_name VARCHAR(200),
    from_warehouse_code VARCHAR(100),
    
    -- 调入信息
    to_warehouse_id UUID NOT NULL,
    to_warehouse_name VARCHAR(200),
    to_warehouse_code VARCHAR(100),
    
    -- 调拨人员信息
    transfer_person_id UUID REFERENCES employees(id),
    department_id UUID REFERENCES departments(id),
    
    -- 单据状态
    status VARCHAR(20) DEFAULT 'draft',
    
    -- 审核信息
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    
    -- 执行信息
    executed_by UUID,
    executed_at TIMESTAMPTZ,
    
    -- 业务关联
    source_document_type VARCHAR(50),
    source_document_id UUID,
    source_document_number VARCHAR(100),
    
    -- 统计信息
    total_items INTEGER DEFAULT 0,
    total_quantity NUMERIC(15, 3) DEFAULT 0,
    total_amount NUMERIC(18, 4) DEFAULT 0,
    
    -- 物流信息
    transporter VARCHAR(200),
    transport_method VARCHAR(50),
    expected_arrival_date TIMESTAMPTZ,
    actual_arrival_date TIMESTAMPTZ,
    
    -- 扩展字段
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 成品调拨单主表索引
CREATE INDEX IF NOT EXISTS ix_product_transfer_order_number ON product_transfer_orders (transfer_number);
CREATE INDEX IF NOT EXISTS ix_product_transfer_order_from_warehouse ON product_transfer_orders (from_warehouse_id);
CREATE INDEX IF NOT EXISTS ix_product_transfer_order_to_warehouse ON product_transfer_orders (to_warehouse_id);
CREATE INDEX IF NOT EXISTS ix_product_transfer_order_person ON product_transfer_orders (transfer_person_id);
CREATE INDEX IF NOT EXISTS ix_product_transfer_order_department ON product_transfer_orders (department_id);
CREATE INDEX IF NOT EXISTS ix_product_transfer_order_date ON product_transfer_orders (transfer_date);
CREATE INDEX IF NOT EXISTS ix_product_transfer_order_status ON product_transfer_orders (status);

-- 20. 成品调拨单明细表
CREATE TABLE IF NOT EXISTS product_transfer_order_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联主表
    transfer_order_id UUID NOT NULL REFERENCES product_transfer_orders(id),
    
    -- 产品信息
    product_id UUID NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_code VARCHAR(100),
    product_spec VARCHAR(500),
    
    -- 库存信息
    from_inventory_id UUID,
    current_stock NUMERIC(15, 3),
    available_quantity NUMERIC(15, 3),
    
    -- 调拨数量信息
    transfer_quantity NUMERIC(15, 3) NOT NULL DEFAULT 0,
    actual_transfer_quantity NUMERIC(15, 3),
    received_quantity NUMERIC(15, 3),
    
    -- 单位信息
    unit VARCHAR(20) NOT NULL,
    
    -- 批次信息
    batch_number VARCHAR(100),
    production_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,
    
    -- 成本信息
    unit_cost NUMERIC(15, 4),
    total_amount NUMERIC(18, 4),
    
    -- 库位信息
    from_location_code VARCHAR(100),
    to_location_code VARCHAR(100),
    actual_to_location_code VARCHAR(100),
    
    -- 质量信息
    quality_status VARCHAR(20) DEFAULT 'qualified',
    quality_certificate VARCHAR(200),
    
    -- 产品特有字段
    customer_id UUID,
    customer_name VARCHAR(200),
    bag_type_id UUID,
    bag_type_name VARCHAR(100),
    
    -- 包装信息
    package_unit VARCHAR(20),
    package_quantity NUMERIC(15, 3),
    net_weight NUMERIC(10, 3),
    gross_weight NUMERIC(10, 3),
    
    -- 状态
    detail_status VARCHAR(20) DEFAULT 'pending',
    
    -- 行号和排序
    line_number INTEGER,
    sort_order INTEGER DEFAULT 0,
    
    -- 扩展字段
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- 审计字段
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 成品调拨单明细表索引
CREATE INDEX IF NOT EXISTS ix_product_transfer_detail_order ON product_transfer_order_details (transfer_order_id);
CREATE INDEX IF NOT EXISTS ix_product_transfer_detail_product ON product_transfer_order_details (product_id);
CREATE INDEX IF NOT EXISTS ix_product_transfer_detail_inventory ON product_transfer_order_details (from_inventory_id);
CREATE INDEX IF NOT EXISTS ix_product_transfer_detail_status ON product_transfer_order_details (detail_status);

-- 创建触发器更新时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加更新时间戳触发器
DO $$
DECLARE
    table_name text;
    table_names text[] := ARRAY[
        'inventories', 'inventory_transactions', 'inventory_count_plans', 'inventory_count_records',
        'inbound_orders', 'inbound_order_details', 'outbound_orders', 'outbound_order_details',
        'material_inbound_orders', 'material_inbound_order_details',
        'material_outbound_orders', 'material_outbound_order_details',
        'material_count_plans', 'material_count_records',
        'material_transfer_orders', 'material_transfer_order_details',
        'product_count_plans', 'product_count_records',
        'product_transfer_orders', 'product_transfer_order_details'
    ];
BEGIN
    FOREACH table_name IN ARRAY table_names
    LOOP
        EXECUTE format('
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        ', table_name, table_name);
    END LOOP;
END $$;

-- 创建表注释
COMMENT ON TABLE inventories IS '库存表 - 记录每个仓库中每种产品/材料的当前库存数量';
COMMENT ON TABLE inventory_transactions IS '库存流水表 - 记录所有库存变动的详细记录';
COMMENT ON TABLE inventory_count_plans IS '盘点计划表';
COMMENT ON TABLE inventory_count_records IS '盘点记录表';
COMMENT ON TABLE inbound_orders IS '入库单主表';
COMMENT ON TABLE inbound_order_details IS '入库单明细表';
COMMENT ON TABLE outbound_orders IS '出库单主表';
COMMENT ON TABLE outbound_order_details IS '出库单明细表';
COMMENT ON TABLE material_inbound_orders IS '材料入库单主表';
COMMENT ON TABLE material_inbound_order_details IS '材料入库单明细表';
COMMENT ON TABLE material_outbound_orders IS '材料出库单主表';
COMMENT ON TABLE material_outbound_order_details IS '材料出库单明细表';
COMMENT ON TABLE material_count_plans IS '材料盘点计划表';
COMMENT ON TABLE material_count_records IS '材料盘点记录表';
COMMENT ON TABLE material_transfer_orders IS '材料调拨单主表';
COMMENT ON TABLE material_transfer_order_details IS '材料调拨单明细表';
COMMENT ON TABLE product_count_plans IS '成品盘点计划表';
COMMENT ON TABLE product_count_records IS '成品盘点记录表';
COMMENT ON TABLE product_transfer_orders IS '成品调拨单主表';
COMMENT ON TABLE product_transfer_order_details IS '成品调拨单明细表';

COMMIT; 