# 智能制造管理 SaaS 平台设计文档

## 项目概述

本项目旨在为中小型薄膜行业提供一个基于 SaaS 模式的智能制造管理平台。该平台采用 Flask API 和 React 前端技术栈，支持多租户架构，使用 PostgreSQL 实现数据库隔离，并通过 Docker 容器化部署。

## 系统架构

### 整体架构

```
├── 前端层 (React)
│   ├── 租户应用前端
│   └── 管理后台前端
├── 后端层 (Flask)
│   ├── API 服务
│   ├── 租户管理服务
│   ├── 认证授权服务
│   └── 业务逻辑服务
├── 数据层 (PostgreSQL)
│   ├── 主数据库 (租户管理)
│   └── 租户数据库 (每个租户一个独立 Schema)
└── 部署层 (Docker)
    ├── 前端容器
    ├── 后端容器
    └── 数据库容器
```

### 多租户架构

采用 Schema 隔离模式，为每个租户创建独立的 Schema，实现数据隔离，同时共享数据库实例资源：

- **主数据库**：存储租户信息、用户账户等系统级数据
- **租户 Schema**：每个租户拥有独立的 Schema，存储业务数据

## 技术栈选择

### 前端技术栈

- **框架**：React 18
- **UI 组件库**：Ant Design
- **状态管理**：Redux Toolkit
- **路由**：React Router
- **API 调用**：Axios
- **构建工具**：Vite

### 后端技术栈

- **框架**：Flask 2.x
- **API 构建**：Flask-RESTful
- **ORM**：SQLAlchemy
- **数据库迁移**：Alembic
- **认证授权**：Flask-JWT-Extended
- **多租户支持**：自定义中间件

### 数据库

- **数据库**：PostgreSQL 14+
- **多租户实现**：Schema 隔离

### 部署技术

- **容器化**：Docker
- **编排**：Docker Compose
- **网关**：Nginx

## 系统功能模块

### 超级管理员后台

1. **租户管理**
   - 创建、编辑、停用租户
   - 租户资源配置与限制
   - 租户使用情况监控

2. **系统配置**
   - 系统参数配置
   - 账号安全策略设置
   - 系统日志查看

### 租户应用

1. **生产管理**
   - 生产计划管理
   - 生产过程监控
   - 生产数据采集与分析

2. **设备管理**
   - 设备档案管理
   - 设备状态监控
   - 设备维护计划

3. **质量管理**
   - 质量检测记录
   - 质量分析与追溯
   - 质量改进计划

4. **仓储管理**
   - 原材料库存管理
   - 成品库存管理
   - 库存预警

5. **人员管理**
   - 员工信息管理
   - 绩效考核
   - 权限分配

## 数据库设计

### 主数据库表结构

- **tenants**：租户信息表
- **users**：用户账户表
- **roles**：角色表
- **permissions**：权限表
- **user_roles**：用户-角色关联表
- **role_permissions**：角色-权限关联表

### 租户数据库表结构

每个租户拥有相同的表结构，但数据彼此隔离：

- **production_plans**：生产计划表
- **production_records**：生产记录表
- **equipments**：设备表
- **equipment_maintenance**：设备维护记录表
- **quality_inspections**：质量检测记录表
- **inventory_materials**：原材料库存表
- **inventory_products**：成品库存表
- **employees**：员工表
- **departments**：部门表

## API 设计

### 认证 API

- `POST /api/auth/login`：用户登录
- `POST /api/auth/logout`：用户登出
- `POST /api/auth/refresh`：刷新令牌

### 超管 API

- `GET /api/admin/tenants`：获取租户列表
- `POST /api/admin/tenants`：创建租户
- `GET /api/admin/tenants/{id}`：获取租户详情
- `PUT /api/admin/tenants/{id}`：更新租户信息
- `DELETE /api/admin/tenants/{id}`：停用租户

### 租户 API

以生产管理模块为例：

- `GET /api/production/plans`：获取生产计划列表
- `POST /api/production/plans`：创建生产计划
- `GET /api/production/plans/{id}`：获取生产计划详情
- `PUT /api/production/plans/{id}`：更新生产计划
- `DELETE /api/production/plans/{id}`：删除生产计划

## 多租户实现方案

### 租户识别

1. 通过子域名识别租户：`{tenant-id}.domain.com`
2. 用户登录后，后端根据用户所属租户确定数据库 Schema
3. 所有数据库操作自动添加 Schema 前缀

### 数据隔离

1. 在 SQLAlchemy 中实现会话管理，为每个请求设置正确的 Schema
2. 使用中间件拦截请求，根据租户信息设置当前 Schema
3. 数据库连接池按租户隔离

## 部署架构

使用 Docker Compose 编排以下容器：

1. **前端容器**：运行 Nginx + React 静态文件
2. **后端容器**：运行 Flask API 服务
3. **数据库容器**：运行 PostgreSQL 数据库
4. **Redis 容器**：用于缓存和会话管理

## 安全设计

1. **认证**：JWT 令牌认证，支持令牌刷新
2. **授权**：基于 RBAC 的权限控制
3. **数据隔离**：Schema 级别的租户数据隔离
4. **API 安全**：请求限流，SQL 注入防护
5. **密码安全**：密码加盐哈希存储

## 扩展性设计

1. **模块化架构**：核心功能与业务模块分离
2. **API 版本控制**：支持 API 版本管理
3. **插件系统**：支持功能扩展
4. **多语言支持**：国际化框架

## 实施路径

### 阶段一：基础架构搭建

1. 搭建前端和后端项目结构
2. 实现多租户数据库设计
3. 开发认证授权系统
4. 开发租户管理功能

### 阶段二：核心业务功能开发

1. 开发生产管理模块
2. 开发设备管理模块
3. 开发质量管理模块
4. 开发仓储管理模块

### 阶段三：高级功能与优化

1. 开发数据分析与报表功能
2. 实现系统监控与告警
3. 性能优化与压力测试
4. 系统文档完善与用户培训

## 下一步工作计划

1. 建立详细的项目目录结构
2. 实现数据库模型设计
3. 开发租户管理和认证模块
4. 搭建基础的 Docker 部署环境 