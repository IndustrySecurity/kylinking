# KylinKing租户模块管理系统设计

## 概述

KylinKing租户模块管理系统是一个全局设计，用于管理多租户SaaS系统中的功能模块配置。该系统支持：

- **模块级配置**：租户管理员可以启用/禁用不同的功能模块
- **字段级配置**：每个模块内的字段可以被租户自定义配置
- **扩展性支持**：支持租户间的差异化配置和自定义扩展

## 系统架构

### 数据模型层

#### 1. SystemModule (系统模块)
```sql
-- 存储在system schema
CREATE TABLE system_modules (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,      -- 模块名称
    display_name VARCHAR(255) NOT NULL,     -- 显示名称
    description TEXT,                       -- 模块描述
    category VARCHAR(100),                  -- 模块分类
    version VARCHAR(20) DEFAULT '1.0.0',   -- 版本
    icon VARCHAR(255),                      -- 图标
    sort_order INTEGER DEFAULT 0,          -- 排序
    is_core BOOLEAN DEFAULT FALSE,         -- 是否核心模块
    is_active BOOLEAN DEFAULT TRUE,        -- 是否激活
    dependencies JSON DEFAULT '[]',        -- 依赖模块列表
    default_config JSON DEFAULT '{}',      -- 默认配置
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. ModuleField (模块字段)
```sql
-- 存储在system schema
CREATE TABLE module_fields (
    id UUID PRIMARY KEY,
    module_id UUID REFERENCES system_modules(id),
    field_name VARCHAR(100) NOT NULL,      -- 字段名称
    display_name VARCHAR(255) NOT NULL,    -- 显示名称
    field_type VARCHAR(50) NOT NULL,       -- 字段类型
    description TEXT,                      -- 字段描述
    is_required BOOLEAN DEFAULT FALSE,     -- 是否必填
    is_system_field BOOLEAN DEFAULT FALSE, -- 是否系统字段
    is_configurable BOOLEAN DEFAULT TRUE,  -- 是否可配置
    sort_order INTEGER DEFAULT 0,         -- 排序
    validation_rules JSON DEFAULT '{}',   -- 验证规则
    field_options JSON DEFAULT '{}',      -- 字段选项
    default_value JSON,                   -- 默认值
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 3. TenantModule (租户模块配置)
```sql
-- 存储在system schema
CREATE TABLE tenant_modules (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    module_id UUID REFERENCES system_modules(id),
    is_enabled BOOLEAN DEFAULT TRUE,       -- 是否启用
    is_visible BOOLEAN DEFAULT TRUE,       -- 是否显示
    custom_config JSON DEFAULT '{}',      -- 自定义配置
    custom_permissions JSON DEFAULT '{}', -- 自定义权限
    configured_by UUID REFERENCES users(id),
    configured_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, module_id)
);
```

#### 4. TenantFieldConfig (租户字段配置)
```sql
-- 存储在system schema
CREATE TABLE tenant_field_configs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    field_id UUID REFERENCES module_fields(id),
    is_enabled BOOLEAN DEFAULT TRUE,       -- 是否启用
    is_visible BOOLEAN DEFAULT TRUE,       -- 是否显示
    is_required BOOLEAN DEFAULT FALSE,     -- 是否必填
    is_readonly BOOLEAN DEFAULT FALSE,     -- 是否只读
    custom_label VARCHAR(255),             -- 自定义标签
    custom_placeholder VARCHAR(255),       -- 自定义占位符
    custom_help_text TEXT,                -- 自定义帮助文本
    custom_validation_rules JSON DEFAULT '{}', -- 自定义验证规则
    custom_options JSON DEFAULT '{}',     -- 自定义选项
    custom_default_value JSON,            -- 自定义默认值
    display_order INTEGER DEFAULT 0,      -- 显示顺序
    column_width INTEGER,                  -- 列宽度
    field_group VARCHAR(100),             -- 字段分组
    configured_by UUID REFERENCES users(id),
    configured_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, field_id)
);
```

#### 5. TenantExtension (租户扩展)
```sql
-- 存储在system schema
CREATE TABLE tenant_extensions (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    extension_type VARCHAR(100) NOT NULL,  -- 扩展类型
    extension_name VARCHAR(255) NOT NULL,  -- 扩展名称
    extension_key VARCHAR(100) NOT NULL,   -- 扩展唯一标识
    extension_config JSON DEFAULT '{}',   -- 扩展配置
    extension_schema JSON DEFAULT '{}',   -- 扩展结构定义
    extension_metadata JSON DEFAULT '{}', -- 扩展元数据
    is_active BOOLEAN DEFAULT TRUE,       -- 是否激活
    module_id UUID REFERENCES system_modules(id), -- 关联模块
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, extension_key)
);
```

### 服务层

#### ModuleService
负责系统模块和字段的管理：
- `create_system_module()` - 创建系统模块
- `add_module_field()` - 添加模块字段
- `get_available_modules()` - 获取可用模块列表
- `configure_tenant_module()` - 配置租户模块
- `get_module_fields()` - 获取模块字段
- `configure_tenant_field()` - 配置租户字段

#### TenantExtensionService
负责租户扩展管理：
- `create_extension()` - 创建扩展
- `get_tenant_extensions()` - 获取租户扩展
- `update_extension()` - 更新扩展

#### TenantConfigService
负责租户配置的综合管理：
- `get_tenant_config_summary()` - 获取配置概要
- `initialize_tenant_modules()` - 初始化租户模块
- `export_tenant_config()` - 导出配置

### API层

#### 超级管理员API (`/api/admin/modules`)
```bash
GET    /api/admin/modules/                    # 获取系统模块列表
POST   /api/admin/modules/                    # 创建系统模块
GET    /api/admin/modules/{id}/fields         # 获取模块字段
POST   /api/admin/modules/{id}/fields         # 添加模块字段
GET    /api/admin/modules/statistics          # 获取使用统计
```

#### 租户管理员API (`/api/tenant/modules`)
```bash
GET    /api/tenant/modules/                   # 获取租户模块列表
GET    /api/tenant/modules/config             # 获取配置概要
POST   /api/tenant/modules/config/initialize  # 初始化配置
GET    /api/tenant/modules/config/export      # 导出配置

POST   /api/tenant/modules/{id}/configure     # 配置模块
GET    /api/tenant/modules/{id}/fields        # 获取模块字段
POST   /api/tenant/modules/{id}/fields/{field_id}/configure # 配置字段

GET    /api/tenant/modules/extensions         # 获取扩展列表
POST   /api/tenant/modules/extensions         # 创建扩展
PUT    /api/tenant/modules/extensions/{id}    # 更新扩展
```

## 功能特性

### 1. 模块级管理

**核心功能：**
- ✅ 模块启用/禁用控制
- ✅ 模块可见性控制
- ✅ 模块依赖关系管理
- ✅ 核心模块保护（不可禁用）
- ✅ 自定义模块配置

**使用场景：**
```python
# 启用生产计划模块
ModuleService.configure_tenant_module(
    tenant_id="tenant-123",
    module_id="production-planning-module-id",
    is_enabled=True,
    is_visible=True,
    custom_config={
        "enable_auto_scheduling": True,
        "planning_horizon_days": 60
    }
)
```

### 2. 字段级配置

**核心功能：**
- ✅ 字段启用/禁用
- ✅ 字段可见性控制
- ✅ 自定义字段标签
- ✅ 自定义验证规则
- ✅ 字段分组和排序
- ✅ 系统字段保护

**配置示例：**
```python
# 自定义"计划开始日期"字段
ModuleService.configure_tenant_field(
    tenant_id="tenant-123",
    field_id="planned_start_date_field_id",
    custom_label="预计开工日期",
    custom_help_text="请选择计划开始生产的日期",
    is_required=True,
    custom_validation_rules={
        "min_date": "today",
        "max_date_offset": 90
    }
)
```

### 3. 扩展性支持

**扩展类型：**
- `custom_field` - 自定义字段
- `custom_workflow` - 自定义工作流
- `custom_report` - 自定义报表
- `custom_integration` - 自定义集成

**创建扩展：**
```python
# 创建自定义字段扩展
TenantExtensionService.create_extension(
    tenant_id="tenant-123",
    extension_type="custom_field",
    extension_name="客户特殊要求",
    extension_key="customer_special_requirements",
    extension_schema={
        "field_type": "text",
        "max_length": 500,
        "required": False
    },
    module_id="production-planning-module-id"
)
```

## 使用指南

### 1. 系统初始化

```bash
# 1. 运行初始化脚本
cd backend
python scripts/init_system_modules.py

# 2. 为租户初始化默认配置
curl -X POST http://localhost:5000/api/tenant/modules/config/initialize \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. 租户模块配置

```javascript
// 前端配置示例
import TenantModuleConfig from './components/TenantModuleConfig';

function App() {
  return (
    <div>
      <TenantModuleConfig />
    </div>
  );
}
```

### 3. 字段配置

租户管理员可以通过界面配置字段：
- **基础设置**：启用/禁用、显示/隐藏、必填/可选
- **显示设置**：自定义标签、占位符、帮助文本
- **验证设置**：自定义验证规则
- **布局设置**：字段分组、显示顺序、列宽度

## 权限控制

### 角色权限
- **超级管理员**：管理所有系统模块和字段定义
- **租户管理员**：配置本租户的模块和字段
- **普通用户**：使用已配置的模块功能

### 配置限制
- 系统字段不能被禁用或删除
- 核心模块不能被禁用
- 依赖关系检查（不能禁用被依赖的模块）

## 数据流转

### 1. 模块数据流
```
SystemModule → TenantModule → 前端模块显示
     ↓              ↓
ModuleField → TenantFieldConfig → 前端字段配置
```

### 2. 配置继承
- 租户配置覆盖系统默认配置
- 字段配置继承模块配置
- 扩展配置补充标准功能

## 监控和统计

### 配置概要统计
```json
{
  "enabled_modules": 8,
  "total_modules": 10,
  "module_coverage": 80.0,
  "custom_field_configs": 15,
  "extensions": 3
}
```

### 使用情况分析
- 各模块的启用率统计
- 字段配置使用情况
- 扩展功能使用分析

## 扩展开发

### 自定义字段扩展
```python
# 创建自定义字段类型
class CustomFieldExtension:
    def __init__(self, config):
        self.config = config
    
    def validate(self, value):
        # 自定义验证逻辑
        pass
    
    def render(self, context):
        # 自定义渲染逻辑
        pass
```

### 集成扩展
```python
# 第三方系统集成
class ERPIntegrationExtension:
    def sync_production_plan(self, plan_data):
        # 同步到ERP系统
        pass
    
    def receive_material_info(self):
        # 从ERP获取物料信息
        pass
```

## 最佳实践

### 1. 模块设计
- 保持模块功能单一且独立
- 合理定义模块依赖关系
- 提供完整的默认配置

### 2. 字段配置
- 区分系统字段和可配置字段
- 提供清晰的字段描述和帮助信息
- 设置合理的验证规则

### 3. 扩展开发
- 遵循统一的扩展接口规范
- 提供完整的配置文档
- 确保扩展的向后兼容性

## 故障排除

### 常见问题

**Q: 模块启用后前端不显示？**
A: 检查模块的`is_visible`配置和用户权限

**Q: 字段配置不生效？**
A: 确认字段的`is_configurable`属性为true

**Q: 扩展无法加载？**
A: 检查扩展的配置格式和依赖关系

### 调试方法
```bash
# 查看租户配置
curl -X GET http://localhost:5000/api/tenant/modules/config/export \
  -H "Authorization: Bearer YOUR_TOKEN"

# 检查模块字段
curl -X GET http://localhost:5000/api/tenant/modules/{module_id}/fields \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 未来规划

### 短期目标
- [ ] 添加模块模板功能
- [ ] 支持字段条件显示
- [ ] 增加配置版本管理

### 长期目标
- [ ] 可视化配置编辑器
- [ ] 多语言字段标签支持
- [ ] 高级工作流配置

---

通过这个全面的租户模块管理系统，KylinKing可以为不同的租户提供灵活的功能配置，满足各种业务场景的需求，同时保持系统的一致性和可维护性。 