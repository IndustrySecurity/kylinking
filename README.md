# KylinKing云膜智能管理系统

KylinKing云膜智能管理系统是一个基于SaaS架构的智能薄膜制造管理平台，旨在为薄膜制造企业提供全面的生产管理解决方案。系统采用现代化的技术栈，支持多租户架构，提供模块化的业务功能。

## 技术栈

### 后端
- Python 3.9+
- Flask 2.0+
- PostgreSQL 13+
- Redis 6+
- SQLAlchemy 2.0+
- Flask-Migrate
- Flask-CORS
- JWT认证
- Gunicorn

### 前端
- React 18+
- Ant Design 5+
- Vite 4+
- React Router 6+
- Axios
- SCSS样式预处理器

### 部署
- Docker & Docker Compose
- Nginx 反向代理
- 多环境部署支持

## 核心功能特性

### 🏢 多租户架构
- **租户隔离**: 完全的数据隔离和资源隔离
- **Schema级隔离**: 每个租户拥有独立的数据库Schema
- **资源管理**: 灵活的资源配置和权限管理

### 👥 用户认证与权限管理
- JWT Token认证机制
- 细粒度的角色权限控制
- 组织架构管理（部门、职位）
- 用户管理和权限分配

### 🔧 租户模块管理系统
- **模块级控制**: 租户管理员可以启用/禁用功能模块
- **字段级配置**: 支持自定义字段标签、验证规则、显示方式
- **扩展性支持**: 允许租户创建自定义字段和集成
- **权限保护**: 系统字段和核心模块受保护
- **配置导出**: 支持配置的导入导出功能

### 📊 基础档案管理

#### 基础分类管理
- **客户分类管理**: 客户分组和分类体系
- **供应商分类管理**: 供应商分类和评级
- **材料分类管理**: 多级材料分类体系
- **产品分类管理**: 产品分类和规格管理
- **工艺分类管理**: 生产工艺分类

#### 基础数据管理
- **客户管理**: 客户信息、联系人、合同管理
- **供应商管理**: 供应商档案、资质管理
- **材料管理**: 材料规格、属性、价格管理
- **产品管理**: 产品档案、BOM、工艺路线
- **员工管理**: 员工档案、技能、绩效管理
- **部门管理**: 组织架构、岗位职责
- **职位管理**: 职位等级、薪酬体系

#### 财务管理
- **币种管理**: 多币种支持、汇率管理
- **付款方式**: 付款条件、账期管理
- **结算方式**: 结算周期、对账规则
- **税率管理**: 税种配置、税率计算
- **账户管理**: 银行账户、资金管理

### 🏭 生产数据管理

#### 生产档案
- **袋型管理**: 产品袋型规格定义
- **色卡管理**: 颜色标准和配色方案
- **规格管理**: 产品规格参数管理
- **单位管理**: 计量单位标准化
- **包装方式**: 包装规格和要求
- **送货方式**: 物流方式和运费标准
- **机台管理**: 设备档案、产能配置
- **班组管理**: 生产班组、人员配置
- **仓库管理**: 仓库布局、库位管理
- **损耗类型**: 生产损耗分类管理

#### 生产配置
- **计算参数**: 生产计算关键参数
- **计算方案**: 成本核算方案配置
- **油墨选项**: 油墨类型和配比管理
- **袋相关公式**: 制袋工艺计算公式
- **报价配件**: 配件价格和规格
- **报价材料**: 材料成本计算
- **报价油墨**: 油墨成本核算
- **报价损耗**: 损耗率计算标准
- **报价运费**: 运输成本计算

### 📦 业务操作管理

#### 材料仓库管理
- **材料入库**: 采购入库、验收管理
- **材料出库**: 生产领料、出库控制
- **材料调拨**: 仓库间调拨、库存平衡
- **材料盘点**: 定期盘点、差异处理

#### 成品仓库管理
- **成品入库**: 生产完工入库管理
- **成品出库**: 销售出库、发货管理
- **成品调拨**: 成品库存调配
- **成品盘点**: 成品库存盘点
- **成品包装**: 包装作业管理
- **成品返工**: 质量问题返工处理
- **过磅管理**: 重量检验和记录
- **托盘管理**: 货物装托和码垛

#### 半成品管理
- **半成品入库**: 工序间流转入库
- **半成品出库**: 后工序领用
- **半成品过磅**: 半成品重量管理

#### 销售管理
- **销售订单**: 订单录入、审核、跟踪
- **客户合同**: 合同管理、条款跟踪
- **月度计划**: 生产销售计划制定
- **送货管理**: 送货单、送货通知
- **退货管理**: 退货单、退货处理

#### 生产报告
- **制袋报告**: 制袋工序产出统计
- **复卷报告**: 复卷工序产出统计
- **领料报告**: 材料消耗统计分析

### 📈 库存管理
- **库存总览**: 实时库存状态监控
- **库存预警**: 库存上下限预警
- **库存分析**: 库存周转率分析
- **呆滞物料**: 呆滞库存识别和处理

## 系统架构特点

### 模块化设计
- 功能模块完全独立，支持按需启用
- 微服务架构思想，便于扩展和维护
- 插件化开发，支持第三方集成

### 数据安全
- 多层次权限控制
- 数据加密传输和存储
- 操作审计日志
- 备份恢复机制

### 性能优化
- Redis缓存机制
- 数据库索引优化
- 前端懒加载和分页
- CDN资源分发

## 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- Node.js 16+
- Python 3.9+

### 开发环境设置

1. **克隆仓库**
```bash
git clone https://github.com/your-username/kylinking.git
cd kylinking
```

2. **配置环境变量**
```bash
# 复制环境变量模板
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 编辑配置文件，设置数据库连接等信息
vim backend/.env
```

3. **启动开发环境**
```bash
# 启动所有服务
docker-compose -f docker/docker-compose.dev.yml up -d

# 查看服务状态
docker-compose -f docker/docker-compose.dev.yml ps
```

4. **初始化数据库**
```bash
# 进入后端容器
docker exec -it kylinking-backend bash

# 执行数据库迁移
flask db upgrade

# 初始化系统模块
python scripts/init_system_modules.py

# 创建测试数据（可选）
python create_wanle_test_data.py
```

5. **访问应用**
- 前端地址: http://localhost:3000
- 后端API: http://localhost:5000/api
- 默认管理员账号: admin@kylinking.com
- 默认密码: admin123

### 生产环境部署

1. **配置生产环境变量**
```bash
cp backend/.env.example backend/.env.prod
cp frontend/.env.example frontend/.env.prod

# 配置生产环境参数
vim backend/.env.prod
vim frontend/.env.prod
```

2. **构建和启动服务**
```bash
# 构建镜像
docker-compose -f docker/docker-compose.prod.yml build

# 启动服务
docker-compose -f docker/docker-compose.prod.yml up -d
```

3. **配置SSL证书**
```bash
# 使用Let's Encrypt获取SSL证书
certbot certonly --nginx -d yourdomain.com

# 更新Nginx配置
docker-compose -f docker/docker-compose.prod.yml restart nginx
```

## 项目结构

```
kylinking/
├── backend/                 # Flask后端应用
│   ├── app/
│   │   ├── api/            # API路由层
│   │   │   ├── tenant/     # 租户业务API
│   │   │   │   ├── business/           # 业务操作API
│   │   │   │   │   ├── inventory/      # 库存管理API
│   │   │   │   │   └── sales/          # 销售管理API
│   │   │   │   └── base_archive/       # 基础档案API
│   │   │   │       ├── base_data/      # 基础数据API
│   │   │   │       ├── base_category/  # 基础分类API
│   │   │   │       ├── production/     # 生产档案API
│   │   │   │       └── financial_management/ # 财务管理API
│   │   │   └── ...
│   │   ├── models/         # 数据模型层
│   │   ├── services/       # 业务逻辑层
│   │   │   ├── base_service.py        # 基础服务类
│   │   │   ├── business/              # 业务服务
│   │   │   │   ├── inventory/         # 库存管理服务
│   │   │   │   └── sales/             # 销售管理服务
│   │   │   └── base_archive/          # 基础档案服务
│   │   │       ├── base_data/         # 基础数据服务
│   │   │       ├── base_category/     # 基础分类服务
│   │   │       ├── production/        # 生产档案服务
│   │   │       └── financial_management/ # 财务管理服务
│   │   ├── schemas/        # 数据验证层
│   │   ├── utils/          # 工具函数
│   │   └── middleware/     # 中间件
│   ├── migrations/         # 数据库迁移文件
│   ├── scripts/            # 脚本工具
│   └── wsgi.py            # WSGI应用入口
├── frontend/               # React前端应用
│   ├── src/
│   │   ├── api/           # API调用层
│   │   │   ├── base-archive/        # 基础档案API
│   │   │   │   ├── base-data/       # 基础数据API
│   │   │   │   ├── base-category/   # 基础分类API
│   │   │   │   ├── production-archive/ # 生产档案API
│   │   │   │   ├── production-config/  # 生产配置API
│   │   │   │   └── financial-management/ # 财务管理API
│   │   │   └── business/            # 业务API
│   │   │       ├── inventory/       # 库存管理API
│   │   │       └── sales/           # 销售管理API
│   │   ├── components/    # React组件
│   │   ├── pages/         # 页面组件
│   │   │   ├── base-archive/        # 基础档案页面
│   │   │   └── business/            # 业务操作页面
│   │   │       ├── material-warehouse/ # 材料仓库
│   │   │       ├── finished-goods/     # 成品管理
│   │   │       └── sales/              # 销售管理
│   │   ├── hooks/         # 自定义Hooks
│   │   ├── services/      # 前端服务层
│   │   ├── styles/        # 样式文件
│   │   └── utils/         # 工具函数
│   └── public/            # 静态资源
├── docker/                # Docker配置
│   ├── nginx/             # Nginx配置
│   └── postgres/          # PostgreSQL配置
├── docs/                  # 项目文档
└── data/                  # 数据存储目录
```

## 开发指南

### 服务层开发规范
```python
# 标准模式 - 继承TenantAwareService
class NewService(TenantAwareService):
    def create_item(self, data, created_by):
        item = self.create_with_tenant(Model, **data)
        self.commit()
        return item.to_dict()
    
    def get_items(self, page=1, per_page=20):
        query = self.session.query(Model)
        # ... 业务逻辑
        return result
```

#### API层开发规范
```python
# 标准模式 - 使用服务层
@bp.route('/items', methods=['GET'])
@jwt_required()
@tenant_required
def get_items():
    service = get_item_service()  # 使用工厂函数
    result = service.get_items(page=page)
    return jsonify({'success': True, 'data': result})
```

#### 工厂函数规范
为每个服务添加工厂函数：
```python
def get_item_service(tenant_id: str = None, schema_name: str = None) -> ItemService:
    """获取项目服务实例"""
    return ItemService(tenant_id=tenant_id, schema_name=schema_name)
```

### 热更新机制
系统采用Docker容器部署，支持代码热更新，**无需手动重启容器**：

- **后端热更新**: Flask开发模式下，修改Python代码会自动重新加载
- **前端热更新**: Vite开发服务器支持HMR（热模块替换），修改React代码立即生效
- **配置更新**: 修改环境变量文件后，使用 `docker-compose restart` 重启对应服务
- **数据库迁移**: 新增迁移文件后，进入容器执行 `flask db upgrade` 即可

**注意**: 生产环境下需要手动重启服务来应用代码更改。

### 后端开发

1. **创建新的业务模块**
```python
# 1. 添加数据模型 (app/models/business/example.py)
class Example(BaseModel):
    __tablename__ = 'examples'
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

# 2. 创建服务层 (app/services/example_service.py)
class ExampleService(TenantAwareService):  # 继承TenantAwareService
    def create_example(self, data, created_by):
        example = self.create_with_tenant(Example, **data)
        self.commit()
        return example.to_dict()

# 3. 添加工厂函数
def get_example_service(tenant_id=None, schema_name=None):
    return ExampleService(tenant_id=tenant_id, schema_name=schema_name)

# 4. 添加API路由 (app/api/tenant/example.py)
@bp.route('/examples', methods=['POST'])
@jwt_required()
@tenant_required
def create_example():
    service = get_example_service()
    result = service.create_example(data, current_user_id)
    return jsonify({'success': True, 'data': result})
```

2. **数据库迁移**
```bash
# 生成迁移文件
flask db migrate -m "Add example model"

# 执行迁移
flask db upgrade
```

### 前端开发

1. **创建新的页面组件**
```jsx
// src/pages/ExampleManagement.jsx
import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form } from 'antd';
import { useApi } from '../hooks/useApi';

const ExampleManagement = () => {
  const [data, setData] = useState([]);
  const { loading, error, request } = useApi();

  const fetchData = async () => {
    const response = await request('/api/examples');
    setData(response.data);
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div>
      <Table dataSource={data} loading={loading} />
    </div>
  );
};

export default ExampleManagement;
```

2. **添加API服务**
```javascript
// src/api/exampleApi.js
import { request } from '../utils/request';

export const exampleApi = {
  getList: () => request.get('/api/examples'),
  create: (data) => request.post('/api/examples', data),
  update: (id, data) => request.put(`/api/examples/${id}`, data),
  delete: (id) => request.delete(`/api/examples/${id}`)
};
```

## 测试

### 后端测试
```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行单元测试
pytest backend/tests/

# 运行覆盖率测试
pytest --cov=app backend/tests/
```

### 前端测试
```bash
# 运行单元测试
npm test

# 运行集成测试
npm run test:integration
```

## 部署管理

### 开发环境
```bash
# 启动开发环境
docker-compose -f docker/docker-compose.dev.yml up -d

# 重新构建服务
docker-compose -f docker/docker-compose.dev.yml up --build

# 查看日志
docker logs saas_backend_dev --tail=50

# 停止服务
docker-compose -f docker/docker-compose.dev.yml down
```

### 生产环境
```bash
# 启动生产环境
docker-compose -f docker/docker-compose.prod.yml up -d

# 滚动更新
docker-compose -f docker/docker-compose.prod.yml up -d --no-deps backend

# 备份数据库
docker exec kylinking-postgres pg_dump -U postgres kylinking > backup.sql

# 恢复数据库
docker exec -i kylinking-postgres psql -U postgres kylinking < backup.sql
```

## 系统监控

### 日志管理
- 应用日志：`/var/log/kylinking/`
- Nginx日志：`/var/log/nginx/`
- 数据库日志：PostgreSQL日志文件

### 性能监控
- 数据库性能监控
- API响应时间监控
- 内存和CPU使用率监控

### 备份策略
- 数据库定时备份
- 应用配置备份
- 文件存储备份

## 故障排除

### 常见问题

1. **数据库连接失败**
```bash
# 检查数据库服务状态
docker-compose ps postgres

# 检查连接配置
cat backend/.env | grep DATABASE_URL
```

2. **前端构建失败**
```bash
# 清理缓存
rm -rf frontend/node_modules
npm install

# 检查Node版本
node --version
```

3. **权限问题**
```bash
# 检查文件权限
ls -la backend/
chmod -R 755 backend/
```

4. **模块导入失败**
如果遇到前端模块导入错误（如MIME类型错误），检查以下内容：
- 确保导入路径与实际文件结构匹配
- 基础档案API路径应使用 `../../../api/base-archive/`
- 业务API路径应使用 `../../../api/business/`
- 检查文件扩展名和路径大小写

## 最近更新

### v1.2.0 (2024年最新版本)

#### 🔧 API路径标准化
- **前端API结构重组**: 将所有基础档案API统一到 `base-archive/` 目录下
  - 基础数据: `api/base-archive/base-data/`
  - 基础分类: `api/base-archive/base-category/`
  - 生产档案: `api/base-archive/production-archive/`
  - 生产配置: `api/base-archive/production-config/`
  - 财务管理: `api/base-archive/financial-management/`
- **业务API重组**: 业务操作API统一到 `business/` 目录下
  - 库存管理: `api/business/inventory/`
  - 销售管理: `api/business/sales/`

#### 🐛 路径兼容性修复
- 修复了大量前端模块导入路径错误
- 添加了后端API路径兼容性别名，确保前端调用正常
- 解决了页面加载时的404错误问题

#### 📱 页面结构优化
- 重新组织了前端页面结构，与API结构保持一致
- 材料仓库页面: `pages/business/material-warehouse/`
- 成品管理页面: `pages/business/finished-goods/`
- 销售管理页面: `pages/business/sales/`

#### ✅ 系统稳定性提升
- 所有API端点经过验证，确保路径正确
- 前端模块导入问题全部修复
- 提升了系统的整体稳定性和用户体验

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 遵循开发规范 - 新代码必须使用TenantAwareService模式
4. 提交代码更改 (`git commit -m 'Add amazing feature'`)
5. 推送到分支 (`git push origin feature/amazing-feature`)
6. 创建 Pull Request

### 代码规范
- Python代码遵循PEP 8规范
- JavaScript代码使用ESLint检查
- 服务层必须继承TenantAwareService
- API层必须使用@tenant_required装饰器
- 提交信息使用约定式提交格式

### 开发流程
1. 功能设计和技术方案评审
2. 确认遵循架构规范和模式
3. 编码实现和单元测试
4. 代码审查和集成测试
5. 部署验证和用户验收

## 版本管理

采用语义化版本控制 (SemVer)：
- 主版本号：不兼容的API修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者: KylinKing开发团队
- 技术支持: support@kylinking.com
- 项目主页: https://www.kylinking.com
- 文档中心: https://docs.kylinking.com

## 致谢

感谢所有为本项目贡献代码和建议的开发者，以及提供技术支持的开源社区。 