-- 创建财务管理相关表的SQL脚本
-- 在wanle schema中创建财务管理相关的表

-- 1. 税率管理表
CREATE TABLE IF NOT EXISTS wanle.tax_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tax_name VARCHAR(100) NOT NULL,
    tax_rate NUMERIC(5, 2) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. 币种管理表
CREATE TABLE IF NOT EXISTS wanle.currencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    currency_code VARCHAR(10) NOT NULL,
    currency_name VARCHAR(100) NOT NULL,
    exchange_rate NUMERIC(10, 4) NOT NULL DEFAULT 1.0000,
    is_base_currency BOOLEAN DEFAULT FALSE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. 账户管理表
CREATE TABLE IF NOT EXISTS wanle.account_management (
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
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. 结算方式表
CREATE TABLE IF NOT EXISTS wanle.settlement_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    settlement_name VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. 付款方式表
CREATE TABLE IF NOT EXISTS wanle.payment_methods (
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
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_tax_rates_enabled ON wanle.tax_rates(is_enabled);
CREATE INDEX IF NOT EXISTS idx_tax_rates_default ON wanle.tax_rates(is_default);
CREATE INDEX IF NOT EXISTS idx_currencies_enabled ON wanle.currencies(is_enabled);
CREATE INDEX IF NOT EXISTS idx_currencies_base ON wanle.currencies(is_base_currency);
CREATE INDEX IF NOT EXISTS idx_account_management_enabled ON wanle.account_management(is_enabled);
CREATE INDEX IF NOT EXISTS idx_settlement_methods_enabled ON wanle.settlement_methods(is_enabled);
CREATE INDEX IF NOT EXISTS idx_payment_methods_enabled ON wanle.payment_methods(is_enabled);

-- 插入一些测试数据
-- 税率数据
INSERT INTO wanle.tax_rates (tax_name, tax_rate, is_default, description, sort_order, created_by) VALUES
('增值税13%', 13.00, TRUE, '一般纳税人增值税税率', 1, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('增值税9%', 9.00, FALSE, '交通运输、邮政、基础电信等服务', 2, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('增值税6%', 6.00, FALSE, '现代服务业、金融服务等', 3, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('增值税3%', 3.00, FALSE, '小规模纳税人征收率', 4, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('免税', 0.00, FALSE, '免征增值税', 5, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1));

-- 币种数据
INSERT INTO wanle.currencies (currency_code, currency_name, exchange_rate, is_base_currency, description, sort_order, created_by) VALUES
('CNY', '人民币', 1.0000, TRUE, '中国人民币', 1, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('USD', '美元', 7.2500, FALSE, '美国美元', 2, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('EUR', '欧元', 7.8500, FALSE, '欧元', 3, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('JPY', '日元', 0.0485, FALSE, '日本日元', 4, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('HKD', '港币', 0.9250, FALSE, '香港港币', 5, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1));

-- 结算方式数据
INSERT INTO wanle.settlement_methods (settlement_name, description, sort_order, created_by) VALUES
('现金结算', '现金支付结算', 1, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('银行转账', '通过银行转账结算', 2, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('支票结算', '支票支付结算', 3, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('承兑汇票', '银行承兑汇票结算', 4, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('信用证', '信用证结算', 5, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('托收承付', '托收承付结算', 6, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1));

-- 付款方式数据
INSERT INTO wanle.payment_methods (payment_name, cash_on_delivery, monthly_settlement, description, sort_order, created_by) VALUES
('货到付款', TRUE, FALSE, '货物到达后付款', 1, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('预付款', FALSE, FALSE, '发货前预付全款', 2, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('月结30天', FALSE, TRUE, '月结30天付款', 3, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('月结60天', FALSE, TRUE, '月结60天付款', 4, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('分期付款', FALSE, FALSE, '分期支付货款', 5, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1));

-- 账户管理数据
INSERT INTO wanle.account_management (account_name, account_type, bank_name, bank_account, description, sort_order, created_by) VALUES
('基本户', '基本账户', '中国工商银行', '1234567890123456789', '公司基本账户', 1, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('一般户', '一般账户', '中国建设银行', '9876543210987654321', '公司一般账户', 2, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('专用户', '专用账户', '中国农业银行', '5555666677778888', '专项资金账户', 3, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1)),
('临时户', '临时账户', '中国银行', '1111222233334444', '临时业务账户', 4, (SELECT id FROM system.users WHERE username = 'admin' LIMIT 1));

COMMENT ON TABLE wanle.tax_rates IS '税率管理表';
COMMENT ON TABLE wanle.currencies IS '币种管理表';
COMMENT ON TABLE wanle.account_management IS '账户管理表';
COMMENT ON TABLE wanle.settlement_methods IS '结算方式表';
COMMENT ON TABLE wanle.payment_methods IS '付款方式表'; 