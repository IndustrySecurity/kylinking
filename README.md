# KylinKing云膜智能管理系统

KylinKing云膜智能管理系统是一个基于SaaS架构的智能薄膜制造管理平台，旨在为薄膜制造企业提供全面的生产管理解决方案。

## 技术栈

### 后端
- Python 3.9+
- Flask 2.0+
- PostgreSQL 13+
- Redis 6+
- SQLAlchemy
- JWT认证
- Flask-Migrate
- Flask-CORS
- Gunicorn

### 前端
- React 18+
- Ant Design 5+
- Vite
- React Router 6+
- Axios
- Redux Toolkit
- Styled Components

### 部署
- Docker
- Docker Compose
- Nginx
- Let's Encrypt

## 功能特性

- 多租户架构
- 用户认证与授权
- 角色权限管理
- **租户模块管理** - 全局设计的模块配置系统
  - 模块启用/禁用控制
  - 字段级别配置管理
  - 租户间差异化扩展
  - 自定义字段和验证规则
- 生产计划管理
- 设备管理
- 质量控制
- 库存管理
- 报表分析
- 系统监控

### 租户模块管理亮点
- ✅ **模块级控制**: 租户管理员可以启用/禁用功能模块
- ✅ **字段级配置**: 支持自定义字段标签、验证规则、显示方式
- ✅ **扩展性支持**: 允许租户创建自定义字段和集成
- ✅ **权限保护**: 系统字段和核心模块受保护
- ✅ **配置导出**: 支持配置的导入导出功能

## 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- Node.js 16+
- npm 8+

### 开发环境设置

1. 克隆仓库
```bash
git clone https://github.com/your-username/kylinking-saas.git
cd kylinking-saas
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

3. 启动开发环境
```bash
docker-compose -f docker/docker-compose.dev.yml up -d
```

4. 访问应用
- 前端: http://localhost:3000
- 后端API: http://localhost:5000/api
- 默认管理员账号: admin@kylinking.com
- 默认密码: admin123

### 生产环境部署

1. 配置环境变量
```bash
cp .env.example .env.prod
# 编辑.env.prod文件，设置生产环境变量
```

2. 构建和启动服务
```bash
docker-compose -f docker/docker-compose.prod.yml up -d
```

3. 配置SSL证书
```bash
# 使用Let's Encrypt获取SSL证书
certbot certonly --nginx -d www.kylinking.com
```

4. 重启Nginx
```bash
docker-compose -f docker/docker-compose.prod.yml restart nginx
```

## 项目结构

```
kylinking-saas/
├── backend/                 # Flask后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── migrations/         # 数据库迁移
│   ├── tests/              # 测试用例
│   └── wsgi.py            # WSGI入口
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/         # 页面
│   │   ├── services/      # API服务
│   │   └── utils/         # 工具函数
│   └── public/            # 静态资源
├── docker/                # Docker配置
│   ├── nginx/             # Nginx配置
│   └── postgres/          # PostgreSQL配置
└── docs/                  # 文档
```

## 开发指南

### 后端开发

1. 创建新的API路由
```python
# backend/app/api/example.py
from flask import Blueprint, jsonify

bp = Blueprint('example', __name__)

@bp.route('/example', methods=['GET'])
def get_example():
    return jsonify({'message': 'Example API'})
```

2. 创建新的数据模型
```python
# backend/app/models/example.py
from app.extensions import db

class Example(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
```

3. 运行数据库迁移
```bash
flask db migrate -m "Add example model"
flask db upgrade
```

### 前端开发

1. 创建新的组件
```jsx
// frontend/src/components/Example.jsx
import React from 'react';
import { Card } from 'antd';

const Example = () => {
  return (
    <Card title="Example Component">
      Content
    </Card>
  );
};

export default Example;
```

2. 创建新的页面
```jsx
// frontend/src/pages/Example.jsx
import React from 'react';
import { Layout } from 'antd';
import Example from '../components/Example';

const ExamplePage = () => {
  return (
    <Layout>
      <Example />
    </Layout>
  );
};

export default ExamplePage;
```

## 测试

### 后端测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_example.py

# 运行带覆盖率报告的测试
pytest --cov=app tests/
```

### 前端测试
```bash
# 运行单元测试
npm test

# 运行端到端测试
npm run test:e2e
```

## 部署

### 开发环境
```bash
# 启动所有服务
docker-compose -f docker/docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker/docker-compose.dev.yml logs -f

# 停止服务
docker-compose -f docker/docker-compose.dev.yml down
```

### 生产环境
```bash
# 构建和启动服务
docker-compose -f docker/docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker/docker-compose.prod.yml logs -f

# 停止服务
docker-compose -f docker/docker-compose.prod.yml down
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者: [Your Name](mailto:your.email@example.com)
- 项目主页: [https://www.kylinking.com](https://www.kylinking.com) 