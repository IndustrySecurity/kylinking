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
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── admin/               # 管理员 API
│   │   │   ├── __init__.py
│   │   │   ├── modules.py       # 模块管理
│   │   │   └── routes.py
│   │   └── tenant/              # 租户业务 API
│   │       ├── __init__.py
│   │       ├── routes.py        # 主路由文件
│   │       ├── modules.py       # 租户模块管理
│   │       ├── business/        # 业务操作 API
│   │       │   ├── __init__.py
│   │       │   ├── inventory/   # 库存管理 API
│   │       │   │   ├── __init__.py
│   │       │   │   ├── inventory.py         # 库存查询API
│   │       │   │   ├── material_inbound.py  # 材料入库API
│   │       │   │   ├── material_outbound.py # 材料出库API
│   │       │   │   ├── material_transfer.py # 材料调拨API
│   │       │   │   ├── outbound_order.py    # 出库订单API
│   │       │   │   ├── product_count.py     # 产品盘点API
│   │       │   │   └── inventory_legacy.py  # Legacy API备份
│   │       │   └── sales/       # 销售管理 API
│   │       │       ├── __init__.py
│   │       │       ├── sales_order.py       # 销售订单API
│   │       │       ├── delivery_notice.py   # 送货通知API
│   │       │       └── sales_legacy.py      # Legacy API备份
│   │       └── base_archive/    # 基础档案 API
│   │           ├── __init__.py
│   │           ├── base_data/   # 基础数据 API
│   │           │   ├── __init__.py
│   │           │   ├── customer.py          # 客户管理API
│   │           │   ├── supplier.py          # 供应商管理API
│   │           │   ├── department.py        # 部门管理API
│   │           │   ├── position.py          # 职位管理API
│   │           │   ├── employee.py          # 员工管理API
│   │           │   ├── material_management.py # 材料管理API
│   │           │   └── product_management.py  # 产品管理API
│   │           ├── base_category/ # 基础分类 API
│   │           │   ├── __init__.py
│   │           │   ├── customer_category.py # 客户分类API
│   │           │   ├── supplier_category.py # 供应商分类API
│   │           │   ├── material_category.py # 材料分类API
│   │           │   ├── product_category.py  # 产品分类API
│   │           │   └── process_category.py  # 工艺分类API
│   │           ├── production/  # 生产档案 API
│   │           │   ├── __init__.py
│   │           │   ├── production_archive/ # 生产档案子模块
│   │           │   │   ├── __init__.py
│   │           │   │   ├── machine.py       # 机台管理API
│   │           │   │   ├── warehouse.py     # 仓库管理API
│   │           │   │   ├── bag_type.py      # 袋型管理API
│   │           │   │   ├── color_card.py    # 色卡管理API
│   │           │   │   ├── delivery_method.py # 送货方式API
│   │           │   │   ├── loss_type.py     # 损耗类型API
│   │           │   │   ├── package_method.py # 包装方式API
│   │           │   │   ├── process.py       # 工艺管理API
│   │           │   │   ├── specification.py # 规格管理API
│   │           │   │   ├── team_group.py    # 班组管理API
│   │           │   │   └── unit.py          # 单位管理API
│   │           │   └── production_config/ # 生产配置子模块
│   │           │       ├── __init__.py
│   │           │       ├── calculation_parameter.py # 计算参数API
│   │           │       ├── calculation_scheme.py    # 计算方案API
│   │           │       ├── ink_option.py            # 油墨选项API
│   │           │       ├── bag_related_formula.py   # 袋相关公式API
│   │           │       ├── quote_accessory.py       # 报价配件API
│   │           │       ├── quote_freight.py         # 报价运费API
│   │           │       ├── quote_ink.py             # 报价油墨API
│   │           │       ├── quote_loss.py            # 报价损耗API
│   │           │       └── quote_material.py        # 报价材料API
│   │           └── financial_management/ # 财务管理 API
│   │               ├── __init__.py
│   │               ├── tax_rate.py          # 税率管理API
│   │               ├── currency.py          # 币种管理API
│   │               ├── payment_method.py    # 付款方式API
│   │               ├── settlement_method.py # 结算方式API
│   │               └── account_management.py # 账户管理API
│   │
│   ├── models/                  # 数据库模型
│   │   ├── __init__.py
│   │   ├── base.py              # 模型基类
│   │   ├── basic_data.py        # 基础数据模型
│   │   ├── module.py            # 模块配置模型
│   │   ├── organization.py      # 组织架构模型
│   │   ├── tenant.py            # 租户模型
│   │   ├── user.py              # 用户模型
│   │   └── business/            # 业务模型 (租户数据)
│   │       ├── __init__.py
│   │       ├── equipment.py     # 设备管理
│   │       ├── inventory.py     # 库存管理
│   │       ├── production.py    # 生产管理
│   │       └── quality.py       # 质量管理
│   │
│   ├── schemas/                 # 数据验证与序列化
│   │   ├── __init__.py
│   │   ├── auth.py              # 认证相关 schema
│   │   └── tenant.py            # 租户相关 schema
│   │
│   ├── services/                # 业务服务层
│   │   ├── __init__.py
│   │   ├── base_service.py      # 基础服务类
│   │   ├── module_service.py    # 模块管理服务
│   │   ├── business/            # 业务服务
│   │   │   ├── __init__.py
│   │   │   ├── inventory/       # 库存业务服务
│   │   │   │   ├── __init__.py
│   │   │   │   ├── inventory_service.py         # 库存服务
│   │   │   │   ├── material_inbound_service.py  # 材料入库服务
│   │   │   │   ├── material_outbound_service.py # 材料出库服务
│   │   │   │   ├── material_transfer_service.py # 材料调拨服务
│   │   │   │   ├── outbound_order_service.py    # 出库订单服务
│   │   │   │   ├── product_count_service.py     # 产品盘点服务
│   │   │   │   └── product_transfer_service.py  # 产品调拨服务
│   │   │   └── sales/           # 销售业务服务
│   │   │       ├── __init__.py
│   │   │       ├── sales_order_service.py       # 销售订单服务
│   │   │       └── delivery_notice_service.py   # 送货通知服务
│   │   └── base_archive/        # 基础档案服务
│   │       ├── __init__.py
│   │       ├── base_data/       # 基础数据服务
│   │       │   ├── __init__.py
│   │       │   ├── customer_service.py          # 客户管理服务
│   │       │   ├── supplier_service.py          # 供应商管理服务
│   │       │   ├── department_service.py        # 部门管理服务
│   │       │   ├── position_service.py          # 职位管理服务
│   │       │   ├── employee_service.py          # 员工管理服务
│   │       │   ├── material_management_service.py # 材料管理服务
│   │       │   └── product_management_service.py  # 产品管理服务
│   │       ├── base_category/   # 基础分类服务
│   │       │   ├── __init__.py
│   │       │   ├── customer_category_service.py # 客户分类服务
│   │       │   ├── supplier_category_service.py # 供应商分类服务
│   │       │   ├── material_category_service.py # 材料分类服务
│   │       │   ├── product_category_service.py  # 产品分类服务
│   │       │   └── process_category_service.py  # 工艺分类服务
│   │       ├── production/      # 生产档案服务
│   │       │   ├── __init__.py
│   │       │   ├── production_archive/ # 生产档案子服务
│   │       │   │   ├── __init__.py
│   │       │   │   ├── machine_service.py       # 机台管理服务
│   │       │   │   ├── warehouse_service.py     # 仓库管理服务
│   │       │   │   ├── bag_type_service.py      # 袋型管理服务
│   │       │   │   ├── color_card_service.py    # 色卡管理服务
│   │       │   │   ├── delivery_method_service.py # 送货方式服务
│   │       │   │   ├── loss_type_service.py     # 损耗类型服务
│   │       │   │   ├── package_method_service.py # 包装方式服务
│   │       │   │   ├── process_service.py       # 工艺管理服务
│   │       │   │   ├── specification_service.py # 规格管理服务
│   │       │   │   ├── team_group_service.py    # 班组管理服务
│   │       │   │   └── unit_service.py          # 单位管理服务
│   │       │   └── production_config/ # 生产配置子服务
│   │       │       ├── __init__.py
│   │       │       ├── calculation_parameter_service.py # 计算参数服务
│   │       │       ├── calculation_scheme_service.py    # 计算方案服务
│   │       │       ├── ink_option_service.py            # 油墨选项服务
│   │       │       ├── bag_related_formula_service.py   # 袋相关公式服务
│   │       │       ├── quote_accessory_service.py       # 报价配件服务
│   │       │       ├── quote_freight_service.py         # 报价运费服务
│   │       │       ├── quote_ink_service.py             # 报价油墨服务
│   │       │       ├── quote_loss_service.py            # 报价损耗服务
│   │       │       └── quote_material_service.py        # 报价材料服务
│   │       └── financial_management/ # 财务管理服务
│   │           ├── __init__.py
│   │           ├── tax_rate_service.py          # 税率管理服务
│   │           ├── currency_service.py          # 币种管理服务
│   │           ├── payment_method_service.py    # 付款方式服务
│   │           ├── settlement_method_service.py # 结算方式服务
│   │           └── account_service.py           # 账户管理服务
│   │
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── database.py          # 数据库工具
│   │   └── tenant_context.py    # 多租户上下文
│   │
│   └── middleware/              # 中间件
│       ├── __init__.py
│       └── tenant_middleware.py # 租户识别与切换中间件
│
├── migrations/                  # 数据库迁移
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/                # 具体迁移文件
│
├── scripts/                     # 脚本文件
│   ├── create_material_count_test_data.py  # 材料盘点测试数据
│   └── init_system_modules.py              # 系统模块初始化
│
├── create_wanle_test_data.py    # 万乐测试数据生成
├── requirements.txt             # 依赖列表
├── Dockerfile                   # Docker 构建文件
├── Dockerfile.dev              # 开发环境 Docker 文件
├── wsgi.py                      # WSGI 入口点
└── REFACTOR_SUMMARY.md          # 重构总结
```

## 前端结构 (React)

```
frontend/
│
├── public/                      # 静态资源
│   └── index.html
│
├── src/                         # 源代码
│   ├── main.jsx                 # 入口文件
│   ├── App.jsx                  # 根组件
│   ├── index.css                # 全局样式
│   ├── debug_login.js           # 调试登录
│   │
│   ├── api/                     # API 调用层
│   │   ├── tenant.js            # 租户 API
│   │   ├── base-category/       # 基础分类 API
│   │   │   ├── customerCategory.js     # 客户分类
│   │   │   ├── materialCategory.js     # 材料分类
│   │   │   ├── processCategoryApi.js   # 工艺分类
│   │   │   ├── productCategory.js      # 产品分类
│   │   │   └── supplierCategory.js     # 供应商分类
│   │   ├── base-data/           # 基础数据 API
│   │   │   ├── customerManagement.js   # 客户管理
│   │   │   ├── department.js           # 部门管理
│   │   │   ├── employee.js             # 员工管理
│   │   │   ├── materialManagement.js   # 材料管理
│   │   │   ├── position.js             # 职位管理
│   │   │   ├── productManagement.js    # 产品管理
│   │   │   └── supplierManagement.js   # 供应商管理
│   │   ├── business/            # 业务相关 API
│   │   │   ├── materialCount.js        # 材料盘点
│   │   │   ├── materialTransfer.js     # 材料调拨
│   │   │   ├── productCount.js         # 产品盘点
│   │   │   └── productTransfer.js      # 产品调拨
│   │   ├── financial-management/ # 财务管理 API
│   │   │   ├── accountManagement.js    # 账户管理
│   │   │   ├── currency.js             # 币种管理
│   │   │   ├── paymentMethod.js        # 付款方式
│   │   │   ├── settlementMethod.js     # 结算方式
│   │   │   └── taxRate.js              # 税率管理
│   │   └── production/          # 生产相关 API
│   │       ├── production-archive/     # 生产档案
│   │       │   ├── bagType.js          # 袋型管理
│   │       │   ├── colorCard.js        # 色卡管理
│   │       │   ├── deliveryMethod.js   # 送货方式
│   │       │   ├── lossTypeApi.js      # 损耗类型
│   │       │   ├── machineApi.js       # 机台管理
│   │       │   ├── packageMethod.js    # 包装方式
│   │       │   ├── processApi.js       # 工艺管理
│   │       │   ├── specification.js    # 规格管理
│   │       │   ├── teamGroup.js        # 班组管理
│   │       │   ├── unit.js             # 单位管理
│   │       │   └── warehouse.js        # 仓库管理
│   │       └── production-config/      # 生产配置
│   │           ├── bagRelatedFormula.js    # 袋相关公式
│   │           ├── calculationParameter.js # 计算参数
│   │           ├── calculationScheme.js    # 计算方案
│   │           ├── inkOption.js            # 油墨选项
│   │           ├── quoteAccessoryApi.js    # 报价配件
│   │           ├── quoteFreight.js         # 报价运费
│   │           ├── quoteInkApi.js          # 报价油墨
│   │           ├── quoteLossApi.js         # 报价损耗
│   │           └── quoteMaterialApi.js     # 报价材料
│   │
│   ├── components/              # 组件
│   │   ├── auth/                # 认证组件
│   │   │   ├── AuthProvider.jsx         # 认证提供者
│   │   │   └── RequireAuth.jsx          # 认证保护组件
│   │   ├── common/              # 通用组件
│   │   ├── layout/              # 布局组件
│   │   │   └── MainLayout.jsx           # 主布局
│   │   └── TenantModuleConfig.jsx       # 租户模块配置
│   │
│   ├── pages/                   # 页面组件
│   │   ├── Dashboard.jsx        # 仪表板
│   │   ├── auth/                # 认证页面
│   │   │   ├── Debug.jsx        # 调试页面
│   │   │   └── Login.jsx        # 登录页面
│   │   ├── admin/               # 管理员后台
│   │   │   ├── Dashboard.jsx            # 管理员仪表板
│   │   │   ├── RoleManagement.jsx       # 角色管理
│   │   │   ├── SystemManagement.jsx     # 系统管理
│   │   │   ├── TenantManagement.jsx     # 租户管理
│   │   │   ├── TenantModuleManagement.jsx # 租户模块管理
│   │   │   ├── UserManagement.jsx       # 用户管理
│   │   │   └── system/                  # 系统管理子页面
│   │   │       ├── OrganizationManagement.jsx # 组织管理
│   │   │       ├── PermissionManagement.jsx   # 权限管理
│   │   │       ├── RoleManagement.jsx         # 角色管理
│   │   │       └── UserManagement.jsx         # 用户管理
│   │   ├── base-archive/        # 基础档案
│   │   │   ├── BaseData.jsx             # 基础数据
│   │   │   ├── FinancialManagement.jsx  # 财务管理
│   │   │   ├── ProductionData.jsx       # 生产数据
│   │   │   ├── base-category/           # 基础分类管理
│   │   │   │   ├── CustomerCategoryManagement.jsx # 客户分类
│   │   │   │   ├── MaterialCategoryManagement.jsx # 材料分类
│   │   │   │   ├── ProcessCategoryManagement.jsx  # 工艺分类
│   │   │   │   ├── ProductCategoryManagement.jsx  # 产品分类
│   │   │   │   └── SupplierCategoryManagement.jsx # 供应商分类
│   │   │   ├── base-data/               # 基础数据管理
│   │   │   │   ├── CustomerManagement.jsx         # 客户管理
│   │   │   │   ├── DepartmentManagement.jsx       # 部门管理
│   │   │   │   ├── EmployeeManagement.jsx         # 员工管理
│   │   │   │   ├── MaterialManagement.jsx         # 材料管理
│   │   │   │   ├── PositionManagement.jsx         # 职位管理
│   │   │   │   ├── ProductManagement.jsx          # 产品管理
│   │   │   │   └── SupplierManagement.jsx         # 供应商管理
│   │   │   ├── financial-management/    # 财务管理
│   │   │   │   ├── AccountManagement.jsx          # 账户管理
│   │   │   │   ├── Currency.jsx                   # 币种管理
│   │   │   │   ├── PaymentMethod.jsx              # 付款方式
│   │   │   │   ├── SettlementMethod.jsx           # 结算方式
│   │   │   │   └── TaxRate.jsx                    # 税率管理
│   │   │   ├── finished-goods-warehouse/ # 成品仓库
│   │   │   └── production/              # 生产相关
│   │   │       ├── production-archive/          # 生产档案
│   │   │       │   ├── BagTypeManagement.jsx    # 袋型管理
│   │   │       │   ├── ColorCardManagement.jsx  # 色卡管理
│   │   │       │   ├── DeliveryMethodManagement.jsx # 送货方式
│   │   │       │   ├── LossTypeManagement.jsx   # 损耗类型
│   │   │       │   ├── MachineManagement.jsx    # 机台管理
│   │   │       │   ├── PackageMethodManagement.jsx # 包装方式
│   │   │       │   ├── ProcessManagement.jsx    # 工艺管理
│   │   │       │   ├── SpecificationManagement.jsx # 规格管理
│   │   │       │   ├── TeamGroupManagement.jsx  # 班组管理
│   │   │       │   ├── UnitManagement.jsx       # 单位管理
│   │   │       │   └── WarehouseManagement.jsx  # 仓库管理
│   │   │       └── production-config/           # 生产配置
│   │   │           ├── BagRelatedFormulaManagement.jsx    # 袋相关公式
│   │   │           ├── CalculationParameterManagement.jsx # 计算参数
│   │   │           ├── CalculationSchemeManagement.jsx    # 计算方案
│   │   │           ├── InkOptionManagement.jsx           # 油墨选项
│   │   │           ├── QuoteAccessoryManagement.jsx      # 报价配件
│   │   │           ├── QuoteFreightManagement.jsx        # 报价运费
│   │   │           ├── QuoteInkManagement.jsx            # 报价油墨
│   │   │           ├── QuoteLossManagement.jsx           # 报价损耗
│   │   │           └── QuoteMaterialManagement.jsx       # 报价材料
│   │   └── business/            # 业务操作
│   │       ├── FinishedGoodsWarehouse.jsx   # 成品仓库
│   │       ├── InventoryOverview.jsx        # 库存总览
│   │       ├── MaterialWarehouse.jsx        # 材料仓库
│   │       ├── SalesManagement.jsx          # 销售管理
│   │       ├── finished-goods/              # 成品相关
│   │       │   ├── BagPickingOutputReport.jsx      # 制袋领料产出报告
│   │       │   ├── BagPickingReturn.jsx            # 制袋领料退料
│   │       │   ├── FinishedGoodsCount.jsx          # 成品盘点
│   │       │   ├── FinishedGoodsInbound.jsx        # 成品入库
│   │       │   ├── FinishedGoodsInboundAccounting.jsx # 成品入库核算
│   │       │   ├── FinishedGoodsOutbound.jsx       # 成品出库
│   │       │   ├── FinishedGoodsPacking.jsx        # 成品包装
│   │       │   ├── FinishedGoodsRework.jsx         # 成品返工
│   │       │   ├── FinishedGoodsToTray.jsx         # 成品上托盘
│   │       │   ├── FinishedGoodsTransfer.jsx       # 成品调拨
│   │       │   ├── FinishedGoodsWeighingSlip.jsx   # 成品过磅单
│   │       │   ├── PackingWeighingSlip.jsx         # 包装过磅单
│   │       │   └── RewindingOutputReport.jsx       # 复卷产出报告
│   │       ├── material-warehouse/          # 材料仓库
│   │       │   ├── MaterialCount.jsx       # 材料盘点
│   │       │   ├── MaterialInbound.jsx     # 材料入库
│   │       │   ├── MaterialOutbound.jsx    # 材料出库
│   │       │   └── MaterialTransfer.jsx    # 材料调拨
│   │       ├── sales/                       # 销售相关
│   │       │   ├── CustomerContract.jsx    # 客户合同
│   │       │   ├── DeliveryNotice.jsx      # 送货通知
│   │       │   ├── DeliveryOrder.jsx       # 送货单
│   │       │   ├── MonthlyPlan.jsx         # 月度计划
│   │       │   ├── ReturnNotice.jsx        # 退货通知
│   │       │   ├── ReturnOrder.jsx         # 退货单
│   │       │   └── SalesOrder.jsx          # 销售订单
│   │       └── semi-finished/               # 半成品相关
│   │           ├── SemiFinishedInbound.jsx  # 半成品入库
│   │           ├── SemiFinishedOutbound.jsx # 半成品出库
│   │           └── SemiFinishedWeighing.jsx # 半成品过磅
│   │
│   ├── hooks/                   # 自定义 Hooks
│   │   └── useApi.js            # API 调用 Hook
│   │
│   ├── mocks/                   # 模拟数据
│   │   ├── browser.js           # 浏览器端模拟
│   │   └── handlers.js          # 请求处理器
│   │
│   ├── services/                # 服务层
│   │   ├── finishedGoodsInboundService.js  # 成品入库服务
│   │   ├── finishedGoodsOutboundService.js # 成品出库服务
│   │   └── inventoryService.js             # 库存服务
│   │
│   ├── styles/                  # 样式文件
│   │   ├── global.scss          # 全局样式
│   │   └── variables.scss       # 样式变量
│   │
│   └── utils/                   # 工具函数
│       ├── auth.js              # 认证工具
│       └── request.js           # 请求工具
│
├── nginx/                       # Nginx 配置
│   └── nginx.conf
├── package.json                 # 依赖和脚本
├── package-lock.json           # 锁定依赖版本
├── vite.config.js              # Vite 配置
├── index.html                  # HTML 模板
├── Dockerfile                  # Docker 构建文件
└── Dockerfile.dev             # 开发环境 Docker 文件
```

## Docker 部署结构

```
docker/
│
├── docker-compose.yml           # Docker Compose 配置
├── docker-compose.dev.yml       # 开发环境配置
├── docker-compose.prod.yml      # 生产环境配置
│
├── auth_response.json            # 认证响应示例
├── nginx/                       # Nginx 配置
│   ├── nginx.conf              # 主配置文件
│   └── conf.d/                 # 配置目录
│       └── default.conf        # 默认配置
│
└── postgres/                    # PostgreSQL 配置
    └── init-db.sql              # 数据库初始化脚本
```

## 文档结构

```
docs/
│
├── material-category-implementation.md    # 材料分类实现说明
├── tenant-module-management.md           # 租户模块管理文档
├── tenant-module-setup-guide.md          # 租户模块设置指南
├── 计算方案管理功能说明.md                # 计算方案管理功能说明
└── modules/                              # 模块文档
    └── basic-data-management.md           # 基础数据管理文档
```

## 项目根目录

```
kylinking/
├── backend/                     # 后端应用
├── frontend/                    # 前端应用
├── docker/                      # Docker 配置
├── docs/                        # 项目文档
├── data/                        # 数据目录
├── .gitignore
├── LICENSE                      # 许可证
├── README.md                    # 项目说明
├── package.json                 # 根目录依赖配置
├── package-lock.json           # 根目录依赖锁定
└── project_structure.md         # 项目结构说明 (本文件)
``` 