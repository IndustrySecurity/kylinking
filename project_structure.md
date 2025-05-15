# 项目目录结构

## 后端结构 (Flask API)

```
backend/
│
├── app/                          # 应用核心目录
│   ├── __init__.py              # 应用初始化
│   ├── config.py                # 配置文件
│   ├── extensions.py            # 扩展插件初始化
│   │
│   ├── api/                     # API 路由
│   │   ├── __init__.py
│   │   ├── auth/                # 认证相关 API
│   │   ├── admin/               # 管理员 API
│   │   └── tenant/              # 租户业务 API
│   │
│   ├── models/                  # 数据库模型
│   │   ├── __init__.py
│   │   ├── base.py              # 模型基类
│   │   ├── tenant.py            # 租户模型
│   │   ├── user.py              # 用户模型
│   │   └── business/            # 业务模型 (租户数据)
│   │
│   ├── schemas/                 # 数据验证与序列化
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── tenant.py
│   │   └── business/
│   │
│   ├── services/                # 业务服务层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── tenant_service.py
│   │   └── business/
│   │
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── tenant_context.py    # 多租户上下文
│   │   ├── security.py          # 安全相关工具
│   │   └── validators.py        # 通用验证器
│   │
│   └── middleware/              # 中间件
│       ├── __init__.py
│       └── tenant_middleware.py # 租户识别与切换中间件
│
├── migrations/                  # 数据库迁移
│
├── tests/                       # 测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_tenant.py
│   └── test_business/
│
├── .env.example                 # 环境变量示例
├── .flaskenv                    # Flask 环境变量
├── .gitignore
├── requirements.txt             # 依赖列表
├── Dockerfile                   # Docker 构建文件
└── wsgi.py                      # WSGI 入口点
```

## 前端结构 (React)

```
frontend/
│
├── public/                      # 静态资源
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
│
├── src/                         # 源代码
│   ├── index.js                 # 入口文件
│   ├── App.jsx                  # 根组件
│   │
│   ├── api/                     # API 调用
│   │   ├── index.js
│   │   ├── auth.js
│   │   ├── admin.js
│   │   └── tenant/
│   │
│   ├── components/              # 通用组件
│   │   ├── common/              # 公共组件
│   │   ├── layout/              # 布局组件
│   │   └── forms/               # 表单组件
│   │
│   ├── pages/                   # 页面组件
│   │   ├── admin/               # 管理员后台
│   │   │   ├── Dashboard.jsx
│   │   │   ├── TenantManagement.jsx
│   │   │   └── SystemSettings.jsx
│   │   │
│   │   └── tenant/              # 租户应用
│   │       ├── Dashboard.jsx
│   │       ├── production/
│   │       ├── equipment/
│   │       ├── quality/
│   │       ├── inventory/
│   │       └── employee/
│   │
│   ├── hooks/                   # 自定义 Hooks
│   │   ├── useAuth.js
│   │   ├── useTenant.js
│   │   └── useApi.js
│   │
│   ├── store/                   # Redux 状态管理
│   │   ├── index.js
│   │   ├── slices/
│   │   └── middleware/
│   │
│   ├── utils/                   # 工具函数
│   │   ├── index.js
│   │   ├── auth.js
│   │   ├── formatters.js
│   │   └── validators.js
│   │
│   ├── constants/               # 常量定义
│   │   ├── index.js
│   │   ├── apiEndpoints.js
│   │   └── messages.js
│   │
│   └── styles/                  # 样式文件
│       ├── index.css
│       ├── variables.scss
│       └── themes/
│
├── .env.development             # 开发环境变量
├── .env.production              # 生产环境变量
├── .eslintrc.js                 # ESLint 配置
├── .prettierrc                  # Prettier 配置
├── .gitignore
├── package.json                 # 依赖和脚本
├── vite.config.js               # Vite 配置
└── Dockerfile                   # Docker 构建文件
```

## Docker 部署结构

```
docker/
│
├── docker-compose.yml           # Docker Compose 配置
├── docker-compose.dev.yml       # 开发环境配置
├── docker-compose.prod.yml      # 生产环境配置
│
├── nginx/                       # Nginx 配置
│   ├── nginx.conf
│   ├── conf.d/
│   └── ssl/
│
└── postgres/                    # PostgreSQL 初始化
    └── init-db.sql              # 初始化脚本
```

## 项目根目录

```
.
├── backend/                     # 后端应用
├── frontend/                    # 前端应用
├── docker/                      # Docker 配置
├── docs/                        # 项目文档
│   ├── api/                     # API 文档
│   ├── database/                # 数据库文档
│   └── deployment/              # 部署文档
│
├── .gitignore
├── README.md                    # 项目说明
└── LICENSE                      # 许可证
``` 