-- 在wanle schema中手动创建quote_accessories表
SET search_path TO wanle, public;

CREATE TABLE IF NOT EXISTS quote_accessories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    material_name VARCHAR(100) NOT NULL,
    unit_price NUMERIC(15,4),
    unit_price_formula VARCHAR(200),
    sort_order INTEGER DEFAULT 0,
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_quote_accessories_tenant_id ON quote_accessories(tenant_id);
CREATE INDEX IF NOT EXISTS ix_quote_accessories_material_name ON quote_accessories(material_name);
CREATE INDEX IF NOT EXISTS ix_quote_accessories_is_enabled ON quote_accessories(is_enabled);

SELECT 'quote_accessories表创建成功' AS result; 