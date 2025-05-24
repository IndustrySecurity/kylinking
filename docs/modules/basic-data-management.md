# 基础档案管理模块设计

## 业务需求概述

基础档案管理是ERP系统的核心模块，负责管理企业的基础数据，包括：

### 功能范围
- **客户档案管理**: 客户基本信息、联系方式、信用额度等
- **供应商档案管理**: 供应商基本信息、采购条款、评级等  
- **产品档案管理**: 产品基本信息、规格参数、价格等
- **物料档案管理**: 原材料信息、库存单位、采购信息等

### 核心功能
1. **CRUD操作**: 创建、查询、更新、删除档案
2. **分类管理**: 支持多级分类体系
3. **状态管理**: 有效/停用/待审核状态控制
4. **编码规则**: 自动编码生成和验证
5. **审批流程**: 档案创建和修改的审批机制
6. **导入导出**: 批量数据处理能力
7. **权限控制**: 基于角色的数据访问控制

## 数据模型设计

### 主要实体

#### 1. 客户档案 (Customer)
```sql
CREATE TABLE {tenant_schema}.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_code VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(20) DEFAULT 'enterprise', -- enterprise/individual
    category_id UUID REFERENCES {tenant_schema}.customer_categories(id),
    
    -- 基本信息
    legal_name VARCHAR(200),
    unified_credit_code VARCHAR(50), -- 统一社会信用代码
    tax_number VARCHAR(50),
    industry VARCHAR(100),
    scale VARCHAR(20), -- large/medium/small/micro
    
    -- 联系信息
    contact_person VARCHAR(100),
    contact_phone VARCHAR(50),
    contact_email VARCHAR(100),
    contact_address TEXT,
    postal_code VARCHAR(20),
    
    -- 业务信息
    credit_limit DECIMAL(15,2) DEFAULT 0,
    payment_terms INTEGER DEFAULT 30, -- 付款天数
    currency VARCHAR(10) DEFAULT 'CNY',
    price_level VARCHAR(20) DEFAULT 'standard',
    sales_person_id UUID,
    
    -- 系统字段
    status VARCHAR(20) DEFAULT 'active', -- active/inactive/pending
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by UUID,
    approved_at TIMESTAMP,
    
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_by UUID,
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- 租户模块配置支持
    custom_fields JSONB DEFAULT '{}',
    
    CONSTRAINT customers_status_check CHECK (status IN ('active', 'inactive', 'pending'))
);
```

#### 2. 供应商档案 (Supplier)
```sql
CREATE TABLE {tenant_schema}.suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_code VARCHAR(50) UNIQUE NOT NULL,
    supplier_name VARCHAR(200) NOT NULL,
    supplier_type VARCHAR(20) DEFAULT 'material', -- material/service/both
    category_id UUID REFERENCES {tenant_schema}.supplier_categories(id),
    
    -- 基本信息
    legal_name VARCHAR(200),
    unified_credit_code VARCHAR(50),
    business_license VARCHAR(50),
    industry VARCHAR(100),
    established_date DATE,
    
    -- 联系信息
    contact_person VARCHAR(100),
    contact_phone VARCHAR(50),
    contact_email VARCHAR(100),
    office_address TEXT,
    factory_address TEXT,
    
    -- 业务信息
    payment_terms INTEGER DEFAULT 30,
    currency VARCHAR(10) DEFAULT 'CNY',
    quality_level VARCHAR(20) DEFAULT 'qualified', -- excellent/good/qualified/poor
    cooperation_level VARCHAR(20) DEFAULT 'ordinary', -- strategic/important/ordinary
    
    -- 评估信息
    quality_score DECIMAL(3,1) DEFAULT 0, -- 0-10分
    delivery_score DECIMAL(3,1) DEFAULT 0,
    service_score DECIMAL(3,1) DEFAULT 0,
    price_score DECIMAL(3,1) DEFAULT 0,
    overall_score DECIMAL(3,1) DEFAULT 0,
    
    -- 系统字段
    status VARCHAR(20) DEFAULT 'active',
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by UUID,
    approved_at TIMESTAMP,
    
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_by UUID,
    updated_at TIMESTAMP DEFAULT NOW(),
    
    custom_fields JSONB DEFAULT '{}'
);
```

#### 3. 产品档案 (Product)
```sql
CREATE TABLE {tenant_schema}.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(20) DEFAULT 'finished', -- finished/semi/material
    category_id UUID REFERENCES {tenant_schema}.product_categories(id),
    
    -- 基本信息
    short_name VARCHAR(100),
    english_name VARCHAR(200),
    brand VARCHAR(100),
    model VARCHAR(100),
    specification TEXT,
    
    -- 技术参数 (薄膜产品特有)
    thickness DECIMAL(8,3), -- 厚度(μm)
    width DECIMAL(8,2), -- 宽度(mm)
    length DECIMAL(10,2), -- 长度(m)
    material_type VARCHAR(100), -- 材料类型
    transparency DECIMAL(5,2), -- 透明度(%)
    tensile_strength DECIMAL(8,2), -- 拉伸强度(MPa)
    
    -- 包装信息
    base_unit VARCHAR(20) DEFAULT 'm²', -- 基本单位
    package_unit VARCHAR(20), -- 包装单位
    conversion_rate DECIMAL(10,4) DEFAULT 1, -- 换算率
    net_weight DECIMAL(10,3), -- 净重(kg)
    gross_weight DECIMAL(10,3), -- 毛重(kg)
    
    -- 价格信息
    standard_cost DECIMAL(15,4), -- 标准成本
    standard_price DECIMAL(15,4), -- 标准售价
    currency VARCHAR(10) DEFAULT 'CNY',
    
    -- 库存信息
    safety_stock DECIMAL(15,3) DEFAULT 0, -- 安全库存
    min_order_qty DECIMAL(15,3) DEFAULT 1, -- 最小订单量
    max_order_qty DECIMAL(15,3), -- 最大订单量
    
    -- 生产信息
    lead_time INTEGER DEFAULT 0, -- 生产周期(天)
    shelf_life INTEGER, -- 保质期(天)
    storage_condition VARCHAR(200), -- 存储条件
    
    -- 质量标准
    quality_standard VARCHAR(200), -- 质量标准
    inspection_method VARCHAR(200), -- 检验方法
    
    -- 系统字段
    status VARCHAR(20) DEFAULT 'active',
    is_sellable BOOLEAN DEFAULT TRUE, -- 可销售
    is_purchasable BOOLEAN DEFAULT TRUE, -- 可采购
    is_producible BOOLEAN DEFAULT TRUE, -- 可生产
    
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_by UUID,
    updated_at TIMESTAMP DEFAULT NOW(),
    
    custom_fields JSONB DEFAULT '{}'
);
```

#### 4. 分类管理 (Categories)
```sql
-- 客户分类
CREATE TABLE {tenant_schema}.customer_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES {tenant_schema}.customer_categories(id),
    level INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 产品分类  
CREATE TABLE {tenant_schema}.product_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES {tenant_schema}.product_categories(id),
    level INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API接口设计

### RESTful API规范

#### 客户档案API
```
GET    /api/tenant/basic-data/customers           # 客户列表
POST   /api/tenant/basic-data/customers           # 创建客户
GET    /api/tenant/basic-data/customers/{id}      # 客户详情
PUT    /api/tenant/basic-data/customers/{id}      # 更新客户
DELETE /api/tenant/basic-data/customers/{id}      # 删除客户

GET    /api/tenant/basic-data/customers/search    # 客户搜索
POST   /api/tenant/basic-data/customers/import    # 批量导入
GET    /api/tenant/basic-data/customers/export    # 数据导出
POST   /api/tenant/basic-data/customers/{id}/approve # 审批客户
```

#### 分类管理API
```
GET    /api/tenant/basic-data/categories/customers # 客户分类树
POST   /api/tenant/basic-data/categories/customers # 创建客户分类
GET    /api/tenant/basic-data/categories/products  # 产品分类树
POST   /api/tenant/basic-data/categories/products  # 创建产品分类
```

## 前端页面设计

### 页面结构
```
基础档案管理/
├── 客户档案/
│   ├── 客户列表页
│   ├── 客户详情页
│   ├── 客户新增/编辑页
│   └── 客户分类管理页
├── 供应商档案/
│   ├── 供应商列表页
│   ├── 供应商详情页
│   ├── 供应商新增/编辑页
│   └── 供应商分类管理页
├── 产品档案/
│   ├── 产品列表页
│   ├── 产品详情页
│   ├── 产品新增/编辑页
│   └── 产品分类管理页
└── 系统设置/
    ├── 编码规则设置
    ├── 审批流程配置
    └── 字段配置管理
```

## 租户配置集成

### 字段配置支持
每个档案表都包含 `custom_fields` JSONB字段，用于存储租户自定义的字段数据。

### 配置应用方式
1. **显示控制**: 根据租户字段配置控制字段的显示/隐藏
2. **验证规则**: 应用租户自定义的验证规则
3. **标签定制**: 使用租户自定义的字段标签
4. **布局控制**: 根据配置调整字段的显示顺序和分组

## 开发优先级

### Phase 1: 核心功能 (2周)
- [ ] 数据模型创建和迁移
- [ ] 基础CRUD API开发
- [ ] 客户档案列表和详情页面

### Phase 2: 完善功能 (2周)
- [ ] 供应商和产品档案功能
- [ ] 分类管理功能
- [ ] 搜索和筛选功能

### Phase 3: 高级功能 (2周)
- [ ] 导入导出功能
- [ ] 审批流程集成
- [ ] 租户字段配置集成
- [ ] 权限控制完善

### Phase 4: 优化提升 (1周)
- [ ] 性能优化
- [ ] 用户体验优化
- [ ] 测试和Bug修复 