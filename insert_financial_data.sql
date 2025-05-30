-- 插入财务管理测试数据
-- 使用正确的管理员用户ID

-- 税率数据
INSERT INTO wanle.tax_rates (tax_name, tax_rate, is_default, description, sort_order, created_by) VALUES
('增值税13%', 13.00, TRUE, '一般纳税人增值税税率', 1, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('增值税9%', 9.00, FALSE, '交通运输、邮政、基础电信等服务', 2, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('增值税6%', 6.00, FALSE, '现代服务业、金融服务等', 3, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('增值税3%', 3.00, FALSE, '小规模纳税人征收率', 4, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('免税', 0.00, FALSE, '免征增值税', 5, '6e941d77-8d11-41a6-9c0a-97f053725b29');

-- 币种数据
INSERT INTO wanle.currencies (currency_code, currency_name, exchange_rate, is_base_currency, description, sort_order, created_by) VALUES
('CNY', '人民币', 1.0000, TRUE, '中国人民币', 1, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('USD', '美元', 7.2500, FALSE, '美国美元', 2, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('EUR', '欧元', 7.8500, FALSE, '欧元', 3, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('JPY', '日元', 0.0485, FALSE, '日本日元', 4, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('HKD', '港币', 0.9250, FALSE, '香港港币', 5, '6e941d77-8d11-41a6-9c0a-97f053725b29');

-- 结算方式数据
INSERT INTO wanle.settlement_methods (settlement_name, description, sort_order, created_by) VALUES
('现金结算', '现金支付结算', 1, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('银行转账', '通过银行转账结算', 2, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('支票结算', '支票支付结算', 3, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('承兑汇票', '银行承兑汇票结算', 4, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('信用证', '信用证结算', 5, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('托收承付', '托收承付结算', 6, '6e941d77-8d11-41a6-9c0a-97f053725b29');

-- 付款方式数据
INSERT INTO wanle.payment_methods (payment_name, cash_on_delivery, monthly_settlement, description, sort_order, created_by) VALUES
('货到付款', TRUE, FALSE, '货物到达后付款', 1, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('预付款', FALSE, FALSE, '发货前预付全款', 2, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('月结30天', FALSE, TRUE, '月结30天付款', 3, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('月结60天', FALSE, TRUE, '月结60天付款', 4, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('分期付款', FALSE, FALSE, '分期支付货款', 5, '6e941d77-8d11-41a6-9c0a-97f053725b29');

-- 账户管理数据
INSERT INTO wanle.account_management (account_name, account_type, bank_name, bank_account, description, sort_order, created_by) VALUES
('基本户', '基本账户', '中国工商银行', '1234567890123456789', '公司基本账户', 1, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('一般户', '一般账户', '中国建设银行', '9876543210987654321', '公司一般账户', 2, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('专用户', '专用账户', '中国农业银行', '5555666677778888', '专项资金账户', 3, '6e941d77-8d11-41a6-9c0a-97f053725b29'),
('临时户', '临时账户', '中国银行', '1111222233334444', '临时业务账户', 4, '6e941d77-8d11-41a6-9c0a-97f053725b29'); 