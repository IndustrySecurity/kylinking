-- 在wanle schema中手动创建quote_materials表
SET search_path TO wanle, public;

CREATE TABLE IF NOT EXISTS quote_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    material_name VARCHAR(100) NOT NULL,
    density NUMERIC(10,4),
    kg_price NUMERIC(15,4),
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_quote_materials_tenant_id ON quote_materials(tenant_id);
CREATE INDEX IF NOT EXISTS ix_quote_materials_material_name ON quote_materials(material_name);
CREATE INDEX IF NOT EXISTS ix_quote_materials_is_enabled ON quote_materials(is_enabled);

SELECT 'quote_materials表创建成功' AS result; 