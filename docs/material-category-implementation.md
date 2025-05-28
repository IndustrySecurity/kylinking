# 材料分类功能实现文档

## 概述

材料分类功能是基础档案模块的重要组成部分，参考包装方式功能开发，支持多租户SaaS架构，为每个租户提供独立的材料分类管理功能。

## 系统架构

### 多租户架构
- **Schema级隔离**：每个租户拥有独立的数据库schema
- **租户上下文**：通过`TenantContext`管理当前租户的schema切换
- **中间件支持**：`TenantMiddleware`自动识别租户并设置上下文

### 当前租户配置
- **测试租户**：wanle
- **Schema名称**：wanle
- **数据库**：saas_platform

## 数据模型设计

### 表结构：material_categories

```sql
CREATE TABLE material_categories (
    -- 主键和基本信息
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    material_code VARCHAR(20) NOT NULL UNIQUE,  -- 材料编号：字母+8位数字，自动生成
    material_name VARCHAR(200) NOT NULL,        -- 材料分类名称
    material_type VARCHAR(20) NOT NULL DEFAULT 'main', -- 材料属性：main主材/auxiliary辅材
    
    -- 单位相关字段
    base_unit_id UUID,                          -- 基础单位ID
    auxiliary_unit_id UUID,                     -- 辅助单位ID
    sales_unit_id UUID,                         -- 销售单位ID
    
    -- 物理属性
    density NUMERIC(10,4),                      -- 密度
    square_weight NUMERIC(10,4),                -- 平方克重
    shelf_life INTEGER,                         -- 保质期（天）
    
    -- 检验质量
    inspection_standard VARCHAR(200),           -- 检验标准
    quality_grade VARCHAR(50),                  -- 质量等级
    
    -- 价格信息
    latest_purchase_price NUMERIC(15,4),        -- 最近采购价
    sales_price NUMERIC(15,4),                  -- 销售价
    product_quote_price NUMERIC(15,4),          -- 产品报价
    cost_price NUMERIC(15,4),                   -- 成本价格
    
    -- 业务配置
    show_on_kanban BOOLEAN NOT NULL DEFAULT FALSE, -- 看板显示
    account_subject VARCHAR(100),               -- 科目
    code_prefix VARCHAR(10),                    -- 编码前缀
    warning_days INTEGER,                       -- 预警天数
    
    -- 纸箱参数
    carton_param1 NUMERIC(10,2),                -- 纸箱参数1
    carton_param2 NUMERIC(10,2),                -- 纸箱参数2
    carton_param3 NUMERIC(10,2),                -- 纸箱参数3
    carton_param4 NUMERIC(10,2),                -- 纸箱参数4
    
    -- 材料属性标识（17个布尔字段）
    enable_batch BOOLEAN NOT NULL DEFAULT FALSE,           -- 启用批次
    enable_barcode BOOLEAN NOT NULL DEFAULT FALSE,         -- 启用条码
    is_ink BOOLEAN NOT NULL DEFAULT FALSE,                 -- 是否油墨
    is_accessory BOOLEAN NOT NULL DEFAULT FALSE,           -- 是否配件
    is_consumable BOOLEAN NOT NULL DEFAULT FALSE,          -- 是否耗材
    is_recyclable BOOLEAN NOT NULL DEFAULT FALSE,          -- 是否可回收
    is_hazardous BOOLEAN NOT NULL DEFAULT FALSE,           -- 是否危险品
    is_imported BOOLEAN NOT NULL DEFAULT FALSE,            -- 是否进口
    is_customized BOOLEAN NOT NULL DEFAULT FALSE,          -- 是否定制
    is_seasonal BOOLEAN NOT NULL DEFAULT FALSE,            -- 是否季节性
    is_fragile BOOLEAN NOT NULL DEFAULT FALSE,             -- 是否易碎
    is_perishable BOOLEAN NOT NULL DEFAULT FALSE,          -- 是否易腐
    is_temperature_sensitive BOOLEAN NOT NULL DEFAULT FALSE, -- 是否温度敏感
    is_moisture_sensitive BOOLEAN NOT NULL DEFAULT FALSE,  -- 是否湿度敏感
    is_light_sensitive BOOLEAN NOT NULL DEFAULT FALSE,     -- 是否光敏感
    requires_special_storage BOOLEAN NOT NULL DEFAULT FALSE, -- 需要特殊存储
    requires_certification BOOLEAN NOT NULL DEFAULT FALSE, -- 需要认证
    
    -- 通用字段
    created_by UUID,                            -- 创建人
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_by UUID,                            -- 修改人
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 修改时间
    display_order INTEGER NOT NULL DEFAULT 0,   -- 显示排序
    is_active BOOLEAN NOT NULL DEFAULT TRUE     -- 是否启用
);
```

### 索引设计
- `idx_wanle_material_categories_code`：材料编号索引
- `idx_wanle_material_categories_name`：材料名称索引
- `idx_wanle_material_categories_type`：材料类型索引
- `idx_wanle_material_categories_active`：启用状态索引

### 触发器
- `trigger_update_material_categories_updated_at`：自动更新修改时间

## 后端实现

### 1. 数据模型 (`backend/app/models/basic_data.py`)
```python
class MaterialCategory(TenantModel):
    """材料分类模型，存储在租户schema"""
    __tablename__ = 'material_categories'
    
    # 继承TenantModel，自动支持多租户
    # 包含所有业务字段和通用字段
    # 实现to_dict()、get_enabled_list()、generate_material_code()方法
```

### 2. 服务层 (`backend/app/services/material_category_service.py`)
```python
class MaterialCategoryService:
    """材料分类服务层"""
    
    # 完整的CRUD操作
    # 支持分页、搜索、过滤
    # 材料编号自动生成逻辑
    # 数据验证和错误处理
```

### 3. API接口 (`backend/app/api/tenant/basic_data.py`)
```python
# RESTful API接口
GET    /material-categories          # 获取列表
GET    /material-categories/{id}     # 获取详情
POST   /material-categories          # 创建
PUT    /material-categories/{id}     # 更新
DELETE /material-categories/{id}     # 删除
PUT    /material-categories/batch    # 批量更新
GET    /material-categories/options  # 获取选项数据
```

## 前端实现

### 1. API封装 (`frontend/src/api/materialCategory.js`)
```javascript
// 封装所有后端API调用
export const materialCategoryApi = {
  getMaterialCategories,
  getMaterialCategoryById,
  createMaterialCategory,
  updateMaterialCategory,
  deleteMaterialCategory,
  batchUpdateMaterialCategories,
  getMaterialCategoryOptions
};
```

### 2. 页面组件 (`frontend/src/pages/base-archive/MaterialCategoryManagement.jsx`)

#### 创新的用户交互设计
- **可编辑表格**：支持行内编辑，提高操作效率
- **详情弹窗**：分组显示字段，便于查看完整信息
- **列设置抽屉**：支持自定义列显示和位置
- **配置持久化**：列配置保存到localStorage

#### 字段分组显示
1. **基本信息**：材料编号、名称、属性等
2. **单位信息**：基础单位、辅助单位、销售单位
3. **物理属性**：密度、平方克重、保质期
4. **检验质量**：检验标准、质量等级
5. **价格信息**：采购价、销售价、报价、成本价
6. **业务配置**：看板显示、科目、编码前缀、预警天数
7. **纸箱参数**：4个数字参数
8. **材料属性标识**：17个布尔标识
9. **其他信息**：备注等

#### 功能特性
- **行内编辑**：双击或点击编辑按钮进入编辑模式
- **新增记录**：支持添加新的材料分类
- **删除确认**：安全删除操作
- **搜索过滤**：支持按名称、类型、状态过滤
- **分页显示**：支持大数据量展示
- **详情查看**：弹窗显示完整信息
- **列配置**：自定义显示列和顺序
- **权限控制**：集成用户权限管理

### 3. 路由配置 (`frontend/src/App.jsx`)
```javascript
<Route path="/base-archive/material-categories" element={
  <ProtectedRoute>
    <MainLayout>
      <MaterialCategoryManagement />
    </MainLayout>
  </ProtectedRoute>
} />
```

### 4. 导航入口 (`frontend/src/pages/base-archive/BaseData.jsx`)
```javascript
{
  key: 'materialCategories',
  title: '材料分类',
  icon: <AppstoreOutlined />,
  path: '/base-archive/material-categories',
  color: '#722ed1'
}
```

## 数据库迁移

### 迁移文件：`2cb76157aa48_在租户schema中添加材料分类表.py`

```python
def upgrade():
    """在所有租户schema中创建材料分类表"""
    
    # 获取所有活跃租户schema
    result = connection.execute(sa.text("""
        SELECT schema_name FROM system.tenants 
        WHERE is_active = TRUE AND schema_name != 'public'
    """))
    
    # 为每个租户schema创建表
    for schema_name in tenant_schemas:
        # 设置搜索路径
        connection.execute(sa.text(f"SET search_path TO {schema_name}, public"))
        
        # 创建表、索引、触发器
        # ...
```

### 执行状态
- ✅ 迁移文件已创建
- ✅ wanle schema中表已创建
- ✅ 索引和触发器已创建
- ✅ 测试数据已插入

## 测试数据

在wanle schema中已插入测试数据：

| 材料编号 | 材料分类 | 材料属性 | 密度 | 平方克重 | 最近采购价 | 销售价 | 状态 |
|----------|----------|----------|------|----------|------------|--------|------|
| A00000001 | 塑料薄膜 | main | 0.92 | 25.5 | 12.50 | 15.00 | 启用 |
| A00000002 | 纸质包装 | auxiliary | 0.75 | 80.0 | 8.00 | 10.00 | 启用 |
| A00000003 | 金属材料 | main | 2.70 | 150.0 | 25.00 | 30.00 | 启用 |

## 技术特点

### 1. 多租户支持
- Schema级数据隔离
- 租户上下文自动切换
- 中间件透明处理

### 2. 创新交互设计
- 可编辑表格 + 详情弹窗 + 列设置
- 字段分组显示
- 自定义列配置

### 3. 材料编号自动生成
- 格式：字母前缀 + 8位数字
- 自动递增
- 只读显示

### 4. 完整的数据验证
- 前端表单验证
- 后端数据验证
- 错误处理机制

### 5. 用户体验优化
- 响应式设计
- 加载状态提示
- 操作反馈
- 权限控制

## 部署状态

### Docker环境
- ✅ PostgreSQL容器：saas_postgres_dev
- ✅ 后端容器：saas_backend_dev
- ✅ 前端容器：saas_frontend_dev
- ✅ Nginx容器：saas_nginx_dev
- ✅ Redis容器：saas_redis_dev

### 服务状态
- ✅ 数据库：运行正常
- ✅ 后端API：运行正常
- ✅ 前端应用：运行正常
- ✅ 反向代理：运行正常

### 访问地址
- 前端应用：http://localhost:3000
- 后端API：http://localhost:5000
- 材料分类页面：http://localhost:3000/base-archive/material-categories

## 总结

材料分类功能已完整实现，包括：

1. **完整的数据模型**：支持所有业务字段和通用字段
2. **多租户架构**：每个租户独立的数据存储
3. **创新的用户界面**：可编辑表格 + 分组详情 + 自定义列
4. **完整的API接口**：RESTful设计，支持所有CRUD操作
5. **数据库迁移**：自动在所有租户schema中创建表
6. **测试数据**：已在wanle租户中插入测试数据

相比传统的弹出框模式，采用了更友好的用户交互方式，支持字段分组显示和自定义列配置，提供了更好的用户体验。功能已可投入使用。 