-- 创建 yiboshuo schema 下的 sales 相关表
-- 基于 app/models/business/sales.py

-- 设置 schema
SET search_path TO yiboshuo;

-- 1. 销售订单表
CREATE TABLE IF NOT EXISTS sales_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 基本信息
    order_number VARCHAR(50) NOT NULL,
    order_type VARCHAR(20) DEFAULT 'normal',
    customer_id UUID NOT NULL REFERENCES customer_management(id),
    customer_order_number VARCHAR(100),
    contact_person_id UUID,
    tax_type_id UUID,
    
    -- 金额信息
    order_amount NUMERIC(15, 4) DEFAULT 0,
    deposit NUMERIC(15, 4) DEFAULT 0,
    plate_fee NUMERIC(15, 4) DEFAULT 0,
    plate_fee_percentage NUMERIC(5, 2) DEFAULT 0,
    
    -- 日期信息
    order_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    internal_delivery_date TIMESTAMPTZ,
    salesperson_id UUID,
    contract_date TIMESTAMPTZ,
    
    -- 地址和物流信息
    delivery_address TEXT,
    logistics_info TEXT,
    tracking_number VARCHAR(100),
    warehouse_id UUID,
    
    -- 生产和订单信息
    production_requirements TEXT,
    order_requirements TEXT,
    
    -- 状态字段
    status VARCHAR(20) DEFAULT 'draft',
    is_active BOOLEAN DEFAULT TRUE,
    
    -- 审计字段
    created_by UUID,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 销售订单表索引
CREATE INDEX IF NOT EXISTS idx_sales_orders_order_number ON sales_orders (order_number);
CREATE INDEX IF NOT EXISTS idx_sales_orders_customer_id ON sales_orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_orders_order_date ON sales_orders (order_date);
CREATE INDEX IF NOT EXISTS idx_sales_orders_status ON sales_orders (status);
CREATE INDEX IF NOT EXISTS idx_sales_orders_salesperson_id ON sales_orders (salesperson_id);

-- 2. 销售明细子表
CREATE TABLE IF NOT EXISTS sales_order_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_order_id UUID NOT NULL REFERENCES sales_orders(id),
    
    -- 产品信息
    product_id UUID REFERENCES products(id),
    product_code VARCHAR(50),
    product_name VARCHAR(200),
    
    -- 规格信息
    negative_deviation_percentage NUMERIC(5, 2),
    positive_deviation_percentage NUMERIC(5, 2),
    production_small_quantity NUMERIC(15, 4),
    production_large_quantity NUMERIC(15, 4),
    order_quantity NUMERIC(15, 4) NOT NULL,
    scheduled_delivery_quantity NUMERIC(15, 4) DEFAULT 0,
    sales_unit_id UUID,
    
    -- 价格信息（自动计算）
    unit_price NUMERIC(15, 4),
    amount NUMERIC(15, 4),
    unit VARCHAR(20),
    estimated_thickness_m NUMERIC(10, 4),
    estimated_weight_kg NUMERIC(10, 4),
    estimated_volume NUMERIC(10, 4),
    shipping_quantity NUMERIC(15, 4),
    production_quantity NUMERIC(15, 4),
    
    -- 库存和存储
    usable_inventory NUMERIC(15, 4),
    insufficient_notice TEXT,
    storage_quantity NUMERIC(15, 4),
    
    -- 税收信息
    tax_type_id UUID,
    currency_id UUID,
    material_structure TEXT,
    customer_requirements TEXT,
    storage_requirements TEXT,
    customization_requirements TEXT,
    printing_requirements TEXT,
    outer_box VARCHAR(100),
    
    -- 外币信息
    foreign_currency_unit_price NUMERIC(15, 4),
    foreign_currency_amount NUMERIC(15, 4),
    foreign_currency_id UUID,
    
    -- 生产信息
    internal_delivery_date TIMESTAMPTZ,
    delivery_date TIMESTAMPTZ,
    customer_code VARCHAR(100),
    product_condition VARCHAR(50),
    color_count INTEGER,
    bag_type_id UUID,
    material_structure_auto TEXT,
    storage_requirements_auto TEXT,
    storage_requirements_input TEXT,
    printing_requirements_auto TEXT,
    
    -- 测试信息
    estimated_thickness_count NUMERIC(10, 4),
    packaging_count NUMERIC(10, 4),
    
    -- 尺寸信息
    square_meters_per_piece NUMERIC(10, 4),
    square_meters_count NUMERIC(10, 4),
    paper_tube_weight NUMERIC(10, 4),
    net_weight NUMERIC(10, 4),
    
    -- 生产信息详细
    composite_area VARCHAR(100),
    modified_condition VARCHAR(100),
    customer_specification TEXT,
    
    -- 颜色和印刷
    color_count_auto INTEGER,
    packaging_type VARCHAR(100),
    material_structure_final TEXT,
    storage_method VARCHAR(100),
    customization_requirements_final TEXT,
    printing_requirements_final TEXT,
    outer_box_final VARCHAR(100),
    
    -- 价格计算
    foreign_currency_unit_price_final NUMERIC(15, 4),
    foreign_currency_amount_final NUMERIC(15, 4),
    paper_weight NUMERIC(10, 4),
    other_info VARCHAR(200),
    
    -- 客户信息
    customer_specification_final VARCHAR(100),
    modification_date TIMESTAMPTZ,
    printing_requirements_input TEXT,
    composite_requirements TEXT,
    estimated_bags_count NUMERIC(15, 4),
    packaging_weight NUMERIC(10, 4),
    
    -- 平方和存储
    square_meter_unit_price NUMERIC(15, 4),
    bag_count NUMERIC(15, 4),
    grade VARCHAR(20),
    company_price NUMERIC(15, 4),
    customer_discount NUMERIC(5, 2),
    customer_discount_amount NUMERIC(15, 4),
    internal_period VARCHAR(100),
    
    -- 技术参数
    printing_detail VARCHAR(100),
    sorting_number INTEGER,
    assembly_coefficient NUMERIC(10, 4),
    affiliate_company_id UUID,
    component_name VARCHAR(200),
    
    -- 审计字段
    created_by UUID,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 销售明细表索引
CREATE INDEX IF NOT EXISTS idx_sales_order_details_sales_order_id ON sales_order_details (sales_order_id);
CREATE INDEX IF NOT EXISTS idx_sales_order_details_product_id ON sales_order_details (product_id);
CREATE INDEX IF NOT EXISTS idx_sales_order_details_delivery_date ON sales_order_details (delivery_date);

-- 3. 其他费用子表
CREATE TABLE IF NOT EXISTS sales_order_other_fees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_order_id UUID NOT NULL REFERENCES sales_orders(id),
    
    -- 费用信息
    fee_type VARCHAR(50),
    product_id UUID REFERENCES products(id),
    product_name VARCHAR(200),
    
    -- 尺寸信息
    length NUMERIC(10, 3),
    width NUMERIC(10, 3),
    customer_order_number VARCHAR(100),
    customer_code VARCHAR(100),
    
    -- 价格信息
    price NUMERIC(15, 4),
    quantity NUMERIC(15, 4),
    unit_id UUID,
    amount NUMERIC(15, 4),
    tax_type_id UUID,
    untaxed_price NUMERIC(15, 4),
    untaxed_amount NUMERIC(15, 4),
    tax_amount NUMERIC(15, 4),
    
    -- 外币信息
    foreign_currency_unit_price NUMERIC(15, 4),
    foreign_currency_amount NUMERIC(15, 4),
    foreign_currency_id UUID,
    
    -- 日期信息
    delivery_date TIMESTAMPTZ,
    internal_delivery_date TIMESTAMPTZ,
    customer_requirements TEXT,
    notes TEXT,
    
    -- 排序
    sort_order INTEGER,
    income_quantity NUMERIC(15, 4),
    completion_status VARCHAR(50),
    assembly_coefficient NUMERIC(10, 4),
    sales_material_batch_number VARCHAR(100),
    affiliate_company_id UUID,
    material_note TEXT,
    
    -- 审计字段
    created_by UUID,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 其他费用表索引
CREATE INDEX IF NOT EXISTS idx_sales_order_other_fees_sales_order_id ON sales_order_other_fees (sales_order_id);
CREATE INDEX IF NOT EXISTS idx_sales_order_other_fees_product_id ON sales_order_other_fees (product_id);
CREATE INDEX IF NOT EXISTS idx_sales_order_other_fees_fee_type ON sales_order_other_fees (fee_type);

-- 4. 销售材料子表
CREATE TABLE IF NOT EXISTS sales_order_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_order_id UUID NOT NULL REFERENCES sales_orders(id),
    
    -- 材料信息
    material_id UUID NOT NULL REFERENCES materials(id),
    negative_deviation_percentage NUMERIC(5, 2),
    positive_deviation_percentage NUMERIC(5, 2),
    gift_quantity NUMERIC(15, 4),
    quantity NUMERIC(15, 4) NOT NULL,
    unit_id UUID,
    auxiliary_quantity NUMERIC(15, 4),
    auxiliary_unit_id UUID,
    
    -- 价格信息
    changed_price_before NUMERIC(15, 4),
    price NUMERIC(15, 4),
    amount NUMERIC(15, 4),
    tax_type_id UUID,
    sales_unit_id UUID,
    untaxed_price NUMERIC(15, 4),
    untaxed_amount NUMERIC(15, 4),
    
    -- 外币信息
    foreign_currency_unit_price NUMERIC(15, 4),
    foreign_currency_amount NUMERIC(15, 4),
    foreign_currency_id UUID,
    
    -- 日期信息
    delivery_date TIMESTAMPTZ,
    internal_delivery_date TIMESTAMPTZ,
    customer_requirements TEXT,
    notes TEXT,
    
    -- 排序和其他信息
    sort_order INTEGER,
    income_quantity NUMERIC(15, 4),
    completion_status VARCHAR(50),
    assembly_coefficient NUMERIC(10, 4),
    sales_material_batch_number VARCHAR(100),
    affiliate_company_id UUID,
    material_archive_note TEXT,
    
    -- 审计字段
    created_by UUID,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 销售材料表索引
CREATE INDEX IF NOT EXISTS idx_sales_order_materials_sales_order_id ON sales_order_materials (sales_order_id);
CREATE INDEX IF NOT EXISTS idx_sales_order_materials_material_id ON sales_order_materials (material_id);

-- 5. 送货通知单主表
CREATE TABLE IF NOT EXISTS delivery_notices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notice_number VARCHAR(50) NOT NULL,
    customer_id UUID NOT NULL REFERENCES customer_management(id),
    sales_order_id UUID REFERENCES sales_orders(id),
    delivery_address TEXT,
    delivery_date TIMESTAMPTZ,
    delivery_method VARCHAR(50),
    logistics_info TEXT,
    remark TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    
    created_by UUID,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 送货通知单主表索引
CREATE INDEX IF NOT EXISTS idx_delivery_notices_notice_number ON delivery_notices (notice_number);
CREATE INDEX IF NOT EXISTS idx_delivery_notices_customer_id ON delivery_notices (customer_id);
CREATE INDEX IF NOT EXISTS idx_delivery_notices_sales_order_id ON delivery_notices (sales_order_id);
CREATE INDEX IF NOT EXISTS idx_delivery_notices_delivery_date ON delivery_notices (delivery_date);
CREATE INDEX IF NOT EXISTS idx_delivery_notices_status ON delivery_notices (status);

-- 6. 送货通知明细子表
CREATE TABLE IF NOT EXISTS delivery_notice_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_notice_id UUID NOT NULL REFERENCES delivery_notices(id),
    
    work_order_number VARCHAR(50),
    product_id UUID REFERENCES products(id),
    product_name VARCHAR(200),
    product_code VARCHAR(50),
    specification TEXT,
    auxiliary_quantity NUMERIC(15, 4),
    sales_unit VARCHAR(20),
    order_quantity NUMERIC(15, 4),
    notice_quantity NUMERIC(15, 4),
    gift_quantity NUMERIC(15, 4),
    inventory_quantity NUMERIC(15, 4),
    unit VARCHAR(20),
    price NUMERIC(15, 4),
    amount NUMERIC(15, 4),
    negative_deviation_percentage NUMERIC(5, 2),
    positive_deviation_percentage NUMERIC(5, 2),
    pcs INTEGER,
    production_min_quantity NUMERIC(15, 4),
    production_max_quantity NUMERIC(15, 4),
    order_delivery_date TIMESTAMPTZ,
    internal_delivery_date TIMESTAMPTZ,
    plate_type VARCHAR(50),
    sales_order_number VARCHAR(50),
    customer_order_number VARCHAR(100),
    product_category VARCHAR(100),
    customer_code VARCHAR(100),
    material_structure TEXT,
    tax_amount NUMERIC(15, 4),
    outer_box VARCHAR(100),
    foreign_currency_unit_price NUMERIC(15, 4),
    foreign_currency_amount NUMERIC(15, 4),
    sort_order INTEGER,
    box_count INTEGER,
    total_area NUMERIC(15, 4),
    discount_amount NUMERIC(15, 4),
    notify_undiscount_amount NUMERIC(15, 4),
    grade VARCHAR(20),
    
    created_by UUID,
    updated_by UUID,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 送货通知明细表索引
CREATE INDEX IF NOT EXISTS idx_delivery_notice_details_delivery_notice_id ON delivery_notice_details (delivery_notice_id);
CREATE INDEX IF NOT EXISTS idx_delivery_notice_details_product_id ON delivery_notice_details (product_id);
CREATE INDEX IF NOT EXISTS idx_delivery_notice_details_work_order_number ON delivery_notice_details (work_order_number);

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
        'sales_orders', 'sales_order_details', 'sales_order_other_fees', 
        'sales_order_materials', 'delivery_notices', 'delivery_notice_details'
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
COMMENT ON TABLE sales_orders IS '销售订单表';
COMMENT ON TABLE sales_order_details IS '销售明细子表';
COMMENT ON TABLE sales_order_other_fees IS '其他费用子表';
COMMENT ON TABLE sales_order_materials IS '销售材料子表';
COMMENT ON TABLE delivery_notices IS '送货通知单主表';
COMMENT ON TABLE delivery_notice_details IS '送货通知明细子表';

-- 创建序列和函数来生成订单号
CREATE SEQUENCE IF NOT EXISTS sales_order_number_seq;

-- 生成销售订单号的函数
CREATE OR REPLACE FUNCTION generate_sales_order_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    date_part VARCHAR(6);
    seq_num INTEGER;
    order_number VARCHAR(50);
BEGIN
    -- 获取当前日期部分（格式：YYMMDD）
    date_part := TO_CHAR(CURRENT_DATE, 'YYMMDD');
    
    -- 获取当天的序列号
    SELECT COALESCE(MAX(CAST(SUBSTRING(order_number FROM 9 FOR 4) AS INTEGER)), 0) + 1
    INTO seq_num
    FROM sales_orders
    WHERE order_number LIKE 'SO' || date_part || '%';
    
    -- 生成订单号（格式：SOYYMMDDXXXX）
    order_number := 'SO' || date_part || LPAD(seq_num::text, 4, '0');
    
    RETURN order_number;
END;
$$ LANGUAGE plpgsql;

-- 为销售订单表添加自动生成订单号的触发器
CREATE OR REPLACE FUNCTION auto_generate_sales_order_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.order_number IS NULL OR NEW.order_number = '' THEN
        NEW.order_number := generate_sales_order_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_generate_sales_order_number
    BEFORE INSERT ON sales_orders
    FOR EACH ROW
    EXECUTE FUNCTION auto_generate_sales_order_number();

-- 生成送货通知单号的函数
CREATE OR REPLACE FUNCTION generate_delivery_notice_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    date_part VARCHAR(6);
    seq_num INTEGER;
    notice_number VARCHAR(50);
BEGIN
    -- 获取当前日期部分（格式：YYMMDD）
    date_part := TO_CHAR(CURRENT_DATE, 'YYMMDD');
    
    -- 获取当天的序列号
    SELECT COALESCE(MAX(CAST(SUBSTRING(notice_number FROM 9 FOR 4) AS INTEGER)), 0) + 1
    INTO seq_num
    FROM delivery_notices
    WHERE notice_number LIKE 'DN' || date_part || '%';
    
    -- 生成通知单号（格式：DNYYMMDDXXXX）
    notice_number := 'DN' || date_part || LPAD(seq_num::text, 4, '0');
    
    RETURN notice_number;
END;
$$ LANGUAGE plpgsql;

-- 为送货通知单表添加自动生成单号的触发器
CREATE OR REPLACE FUNCTION auto_generate_delivery_notice_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.notice_number IS NULL OR NEW.notice_number = '' THEN
        NEW.notice_number := generate_delivery_notice_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_generate_delivery_notice_number
    BEFORE INSERT ON delivery_notices
    FOR EACH ROW
    EXECUTE FUNCTION auto_generate_delivery_notice_number();

COMMIT; 