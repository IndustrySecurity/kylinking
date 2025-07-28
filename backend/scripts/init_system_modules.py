#!/usr/bin/env python3
"""
初始化系统模块脚本
为KylinKing云膜智能管理系统添加基础功能模块
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.module_service import ModuleService
from app.extensions import db
import uuid


def init_production_planning_module():
    """初始化生产计划管理模块"""
    print("初始化生产管理模块...")
    
    module = ModuleService.create_system_module(
        name='production_planning',
        display_name='生产管理',
        description='薄膜生产计划的制定、调度和跟踪管理',
        category='production',
        version='1.0.0',
        icon='icon-production',
        sort_order=10,
        is_core=True,
        dependencies=[],
        default_config={
            'enable_auto_scheduling': True,
            'planning_horizon_days': 30,
            'capacity_utilization_target': 0.85
        }
    )
    
    # 添加字段定义
    fields = [
        {
            'field_name': 'plan_number',
            'display_name': '计划编号',
            'field_type': 'string',
            'description': '生产计划的唯一标识',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 1,
            'validation_rules': {'pattern': '^PP\\d{8}$', 'max_length': 20}
        },
        {
            'field_name': 'product_name',
            'display_name': '产品名称',
            'field_type': 'string',
            'description': '要生产的薄膜产品名称',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 2,
            'validation_rules': {'max_length': 100}
        },
        {
            'field_name': 'planned_start_date',
            'display_name': '计划开始日期',
            'field_type': 'date',
            'description': '计划开始生产的日期',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 3
        },
        {
            'field_name': 'planned_end_date',
            'display_name': '计划结束日期',
            'field_type': 'date',
            'description': '计划完成生产的日期',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 4
        },
        {
            'field_name': 'planned_quantity',
            'display_name': '计划产量',
            'field_type': 'number',
            'description': '计划生产的数量',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 5,
            'validation_rules': {'min': 0, 'max': 999999},
            'field_options': {'unit': 'm²', 'decimal_places': 2}
        },
        {
            'field_name': 'priority',
            'display_name': '优先级',
            'field_type': 'select',
            'description': '生产计划的优先级',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 6,
            'field_options': {
                'options': [
                    {'value': 'urgent', 'label': '紧急'},
                    {'value': 'high', 'label': '高'},
                    {'value': 'medium', 'label': '中'},
                    {'value': 'low', 'label': '低'}
                ]
            },
            'default_value': 'medium'
        },
        {
            'field_name': 'production_line',
            'display_name': '生产线',
            'field_type': 'select',
            'description': '指定的生产线',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 7,
            'field_options': {
                'options': [
                    {'value': 'line_01', 'label': '生产线01'},
                    {'value': 'line_02', 'label': '生产线02'},
                    {'value': 'line_03', 'label': '生产线03'}
                ]
            }
        },
        {
            'field_name': 'status',
            'display_name': '状态',
            'field_type': 'select',
            'description': '生产计划的当前状态',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 8,
            'field_options': {
                'options': [
                    {'value': 'draft', 'label': '草稿'},
                    {'value': 'approved', 'label': '已批准'},
                    {'value': 'in_progress', 'label': '进行中'},
                    {'value': 'completed', 'label': '已完成'},
                    {'value': 'cancelled', 'label': '已取消'}
                ]
            },
            'default_value': 'draft'
        },
        {
            'field_name': 'notes',
            'display_name': '备注',
            'field_type': 'text',
            'description': '生产计划的备注信息',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 9,
            'validation_rules': {'max_length': 500}
        }
    ]
    
    for field_data in fields:
        ModuleService.add_module_field(
            module_id=str(module.id),
            **field_data
        )
    
    print(f"✓ 生产计划管理模块初始化完成，模块ID: {module.id}")
    return module


def init_quality_control_module():
    """初始化质量控制模块"""
    print("初始化质量控制模块...")
    
    module = ModuleService.create_system_module(
        name='quality_control',
        display_name='质量控制',
        description='薄膜产品质量检测、控制和追溯管理',
        category='quality',
        version='1.0.0',
        icon='icon-quality',
        sort_order=20,
        is_core=True,
        dependencies=['production_planning'],
        default_config={
            'auto_sampling': True,
            'quality_threshold': 95.0,
            'enable_spc': True
        }
    )
    
    # 添加字段定义
    fields = [
        {
            'field_name': 'qc_number',
            'display_name': '质检编号',
            'field_type': 'string',
            'description': '质量检测记录的唯一编号',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 1,
            'validation_rules': {'pattern': '^QC\\d{8}$'}
        },
        {
            'field_name': 'batch_number',
            'display_name': '批次号',
            'field_type': 'string',
            'description': '产品批次号',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 2
        },
        {
            'field_name': 'inspection_date',
            'display_name': '检测日期',
            'field_type': 'datetime',
            'description': '质量检测的时间',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 3
        },
        {
            'field_name': 'thickness',
            'display_name': '厚度',
            'field_type': 'number',
            'description': '薄膜厚度测量值',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 4,
            'validation_rules': {'min': 0, 'max': 1000},
            'field_options': {'unit': 'μm', 'decimal_places': 3}
        },
        {
            'field_name': 'tensile_strength',
            'display_name': '拉伸强度',
            'field_type': 'number',
            'description': '薄膜拉伸强度',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 5,
            'validation_rules': {'min': 0},
            'field_options': {'unit': 'MPa', 'decimal_places': 2}
        },
        {
            'field_name': 'transparency',
            'display_name': '透明度',
            'field_type': 'number',
            'description': '薄膜透明度百分比',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 6,
            'validation_rules': {'min': 0, 'max': 100},
            'field_options': {'unit': '%', 'decimal_places': 1}
        },
        {
            'field_name': 'inspector',
            'display_name': '检测员',
            'field_type': 'string',
            'description': '负责检测的人员',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 7
        },
        {
            'field_name': 'result',
            'display_name': '检测结果',
            'field_type': 'select',
            'description': '质量检测的最终结果',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 8,
            'field_options': {
                'options': [
                    {'value': 'pass', 'label': '合格'},
                    {'value': 'fail', 'label': '不合格'},
                    {'value': 'rework', 'label': '返工'}
                ]
            }
        }
    ]
    
    for field_data in fields:
        ModuleService.add_module_field(
            module_id=str(module.id),
            **field_data
        )
    
    print(f"✓ 质量控制模块初始化完成，模块ID: {module.id}")
    return module


def init_inventory_management_module():
    """初始化库存管理模块"""
    print("初始化库存管理模块...")
    
    module = ModuleService.create_system_module(
        name='inventory_management',
        display_name='库存管理',
        description='原材料和成品的库存管理、入库出库追踪',
        category='inventory',
        version='1.0.0',
        icon='icon-inventory',
        sort_order=30,
        is_core=True,
        dependencies=[],
        default_config={
            'auto_reorder': True,
            'safety_stock_days': 7,
            'enable_barcode': True
        }
    )
    
    # 添加字段定义
    fields = [
        {
            'field_name': 'item_code',
            'display_name': '物料编码',
            'field_type': 'string',
            'description': '物料的唯一编码',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 1
        },
        {
            'field_name': 'item_name',
            'display_name': '物料名称',
            'field_type': 'string',
            'description': '物料的名称',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 2
        },
        {
            'field_name': 'category',
            'display_name': '物料类别',
            'field_type': 'select',
            'description': '物料的分类',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 3,
            'field_options': {
                'options': [
                    {'value': 'raw_material', 'label': '原材料'},
                    {'value': 'semi_finished', 'label': '半成品'},
                    {'value': 'finished_goods', 'label': '成品'},
                    {'value': 'consumables', 'label': '耗材'}
                ]
            }
        },
        {
            'field_name': 'current_stock',
            'display_name': '当前库存',
            'field_type': 'number',
            'description': '当前的库存数量',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 4,
            'validation_rules': {'min': 0},
            'field_options': {'decimal_places': 2}
        },
        {
            'field_name': 'unit',
            'display_name': '单位',
            'field_type': 'string',
            'description': '库存单位',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 5
        },
        {
            'field_name': 'safety_stock',
            'display_name': '安全库存',
            'field_type': 'number',
            'description': '安全库存数量',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 6,
            'validation_rules': {'min': 0}
        },
        {
            'field_name': 'reorder_point',
            'display_name': '再订货点',
            'field_type': 'number',
            'description': '触发补货的库存水平',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 7,
            'validation_rules': {'min': 0}
        },
        {
            'field_name': 'warehouse_location',
            'display_name': '仓库位置',
            'field_type': 'string',
            'description': '物料在仓库中的位置',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 8
        }
    ]
    
    for field_data in fields:
        ModuleService.add_module_field(
            module_id=str(module.id),
            **field_data
        )
    
    print(f"✓ 库存管理模块初始化完成，模块ID: {module.id}")
    return module


def init_equipment_management_module():
    """初始化设备管理模块"""
    print("初始化设备管理模块...")
    
    module = ModuleService.create_system_module(
        name='equipment_management',
        display_name='设备管理',
        description='生产设备的维护、保养和状态监控管理',
        category='maintenance',
        version='1.0.0',
        icon='icon-equipment',
        sort_order=40,
        is_core=False,
        dependencies=['production_planning'],
        default_config={
            'predictive_maintenance': True,
            'maintenance_interval_days': 30,
            'enable_iot_monitoring': True
        }
    )
    
    # 添加字段定义（简化示例）
    fields = [
        {
            'field_name': 'equipment_code',
            'display_name': '设备编号',
            'field_type': 'string',
            'description': '设备的唯一编号',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 1
        },
        {
            'field_name': 'equipment_name',
            'display_name': '设备名称',
            'field_type': 'string',
            'description': '设备的名称',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 2
        },
        {
            'field_name': 'status',
            'display_name': '设备状态',
            'field_type': 'select',
            'description': '设备的当前运行状态',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 3,
            'field_options': {
                'options': [
                    {'value': 'running', 'label': '运行中'},
                    {'value': 'idle', 'label': '闲置'},
                    {'value': 'maintenance', 'label': '维护中'},
                    {'value': 'breakdown', 'label': '故障'}
                ]
            }
        }
    ]
    
    for field_data in fields:
        ModuleService.add_module_field(
            module_id=str(module.id),
            **field_data
        )
    
    print(f"✓ 设备管理模块初始化完成，模块ID: {module.id}")
    return module


def init_reporting_module():
    """初始化报表分析模块"""
    print("初始化报表分析模块...")
    
    module = ModuleService.create_system_module(
        name='reporting',
        display_name='报表分析',
        description='生产、质量、库存等各种报表和数据分析',
        category='analytics',
        version='1.0.0',
        icon='icon-chart',
        sort_order=50,
        is_core=False,
        dependencies=['production_planning', 'quality_control', 'inventory_management'],
        default_config={
            'auto_report_generation': True,
            'report_retention_days': 365,
            'enable_dashboard': True
        }
    )
    
    print(f"✓ 报表分析模块初始化完成，模块ID: {module.id}")
    return module


def init_basic_data_module():
    """初始化基础档案模块"""
    print("初始化基础档案模块...")
    
    module = ModuleService.create_system_module(
        name='basic_data',
        display_name='基础档案',
        description='客户、供应商、产品、物料等基础数据管理',
        category='master_data',
        version='1.0.0',
        icon='icon-database',
        sort_order=5,
        is_core=True,
        dependencies=[],
        default_config={
            'enable_customer_management': True,
            'enable_supplier_management': True,
            'enable_product_catalog': True,
            'enable_material_management': True
        }
    )
    
    # 添加字段定义
    fields = [
        {
            'field_name': 'data_type',
            'display_name': '档案类型',
            'field_type': 'select',
            'description': '基础档案的类型',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 1,
            'field_options': {
                'options': [
                    {'value': 'customer', 'label': '客户档案'},
                    {'value': 'supplier', 'label': '供应商档案'},
                    {'value': 'product', 'label': '产品档案'},
                    {'value': 'material', 'label': '物料档案'}
                ]
            }
        },
        {
            'field_name': 'code',
            'display_name': '编码',
            'field_type': 'string',
            'description': '档案编码',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 2,
            'validation_rules': {'max_length': 50}
        },
        {
            'field_name': 'name',
            'display_name': '名称',
            'field_type': 'string',
            'description': '档案名称',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 3,
            'validation_rules': {'max_length': 200}
        },
        {
            'field_name': 'category',
            'display_name': '分类',
            'field_type': 'string',
            'description': '档案分类',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 4,
            'validation_rules': {'max_length': 100}
        },
        {
            'field_name': 'status',
            'display_name': '状态',
            'field_type': 'select',
            'description': '档案状态',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 5,
            'field_options': {
                'options': [
                    {'value': 'active', 'label': '有效'},
                    {'value': 'inactive', 'label': '停用'},
                    {'value': 'pending', 'label': '待审核'}
                ]
            },
            'default_value': 'active'
        }
    ]
    
    for field_data in fields:
        ModuleService.add_module_field(
            module_id=str(module.id),
            **field_data
        )
    
    print(f"✓ 基础档案模块初始化完成，模块ID: {module.id}")
    return module


def init_sales_management_module():
    """初始化销售管理模块"""
    print("初始化销售管理模块...")
    
    module = ModuleService.create_system_module(
        name='sales_management',
        display_name='销售管理',
        description='客户关系、销售订单、报价管理等销售业务流程',
        category='sales',
        version='1.0.0',
        icon='icon-sales',
        sort_order=15,
        is_core=True,
        dependencies=['basic_data'],
        default_config={
            'enable_quotation': True,
            'enable_order_tracking': True,
            'auto_credit_check': True,
            'default_payment_terms': 30
        }
    )
    
    # 添加字段定义
    fields = [
        {
            'field_name': 'order_number',
            'display_name': '订单编号',
            'field_type': 'string',
            'description': '销售订单的唯一编号',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 1,
            'validation_rules': {'pattern': '^SO\\d{8}$', 'max_length': 20}
        },
        {
            'field_name': 'customer_name',
            'display_name': '客户名称',
            'field_type': 'string',
            'description': '销售客户名称',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 2,
            'validation_rules': {'max_length': 200}
        },
        {
            'field_name': 'order_date',
            'display_name': '订单日期',
            'field_type': 'date',
            'description': '销售订单日期',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 3
        },
        {
            'field_name': 'delivery_date',
            'display_name': '交货日期',
            'field_type': 'date',
            'description': '要求交货日期',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 4
        },
        {
            'field_name': 'total_amount',
            'display_name': '订单金额',
            'field_type': 'number',
            'description': '订单总金额',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 5,
            'validation_rules': {'min': 0},
            'field_options': {'currency': 'CNY', 'decimal_places': 2}
        },
        {
            'field_name': 'order_status',
            'display_name': '订单状态',
            'field_type': 'select',
            'description': '销售订单状态',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 6,
            'field_options': {
                'options': [
                    {'value': 'draft', 'label': '草稿'},
                    {'value': 'confirmed', 'label': '已确认'},
                    {'value': 'in_production', 'label': '生产中'},
                    {'value': 'shipped', 'label': '已发货'},
                    {'value': 'delivered', 'label': '已交付'},
                    {'value': 'cancelled', 'label': '已取消'}
                ]
            },
            'default_value': 'draft'
        }
    ]
    
    for field_data in fields:
        ModuleService.add_module_field(
            module_id=str(module.id),
            **field_data
        )
    
    print(f"✓ 销售管理模块初始化完成，模块ID: {module.id}")
    return module


def init_warehouse_management_module():
    """初始化仓库管理模块"""
    print("初始化仓库管理模块...")
    
    module = ModuleService.create_system_module(
        name='warehouse_management',
        display_name='仓库管理',
        description='库存管理、入库出库、库位管理等仓储业务',
        category='warehouse',
        version='1.0.0',
        icon='icon-warehouse',
        sort_order=25,
        is_core=True,
        dependencies=['basic_data'],
        default_config={
            'enable_barcode': True,
            'auto_location_assignment': True,
            'low_stock_warning': True,
            'batch_tracking': True
        }
    )
    
    # 添加字段定义
    fields = [
        {
            'field_name': 'warehouse_code',
            'display_name': '仓库编码',
            'field_type': 'string',
            'description': '仓库的唯一编码',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 1,
            'validation_rules': {'max_length': 20}
        },
        {
            'field_name': 'material_code',
            'display_name': '物料编码',
            'field_type': 'string',
            'description': '库存物料编码',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 2,
            'validation_rules': {'max_length': 50}
        },
        {
            'field_name': 'batch_number',
            'display_name': '批次号',
            'field_type': 'string',
            'description': '物料批次号',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 3,
            'validation_rules': {'max_length': 50}
        },
        {
            'field_name': 'current_stock',
            'display_name': '当前库存',
            'field_type': 'number',
            'description': '当前库存数量',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 4,
            'validation_rules': {'min': 0},
            'field_options': {'decimal_places': 3}
        },
        {
            'field_name': 'location',
            'display_name': '库位',
            'field_type': 'string',
            'description': '物料存储位置',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 5,
            'validation_rules': {'max_length': 50}
        }
    ]
    
    for field_data in fields:
        ModuleService.add_module_field(
            module_id=str(module.id),
            **field_data
        )
    
    print(f"✓ 仓库管理模块初始化完成，模块ID: {module.id}")
    return module


def init_purchase_management_module():
    """初始化采购管理模块"""
    print("初始化采购管理模块...")
    
    module = ModuleService.create_system_module(
        name='purchase_management',
        display_name='采购管理',
        description='采购申请、采购订单、供应商管理等采购业务流程',
        category='purchase',
        version='1.0.0',
        icon='icon-purchase',
        sort_order=30,
        is_core=True,
        dependencies=['basic_data', 'warehouse_management'],
        default_config={
            'enable_approval_workflow': True,
            'auto_reorder_point': True,
            'vendor_evaluation': True,
            'price_comparison': True
        }
    )
    
    # 添加字段定义
    fields = [
        {
            'field_name': 'po_number',
            'display_name': '采购单号',
            'field_type': 'string',
            'description': '采购订单的唯一编号',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 1,
            'validation_rules': {'pattern': '^PO\\d{8}$', 'max_length': 20}
        },
        {
            'field_name': 'supplier_name',
            'display_name': '供应商名称',
            'field_type': 'string',
            'description': '采购供应商名称',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 2,
            'validation_rules': {'max_length': 200}
        },
        {
            'field_name': 'po_date',
            'display_name': '采购日期',
            'field_type': 'date',
            'description': '采购订单日期',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 3
        },
        {
            'field_name': 'expected_date',
            'display_name': '预计到货日期',
            'field_type': 'date',
            'description': '预计物料到货日期',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 4
        },
        {
            'field_name': 'total_amount',
            'display_name': '采购金额',
            'field_type': 'number',
            'description': '采购订单总金额',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 5,
            'validation_rules': {'min': 0},
            'field_options': {'currency': 'CNY', 'decimal_places': 2}
        },
        {
            'field_name': 'po_status',
            'display_name': '采购状态',
            'field_type': 'select',
            'description': '采购订单状态',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 6,
            'field_options': {
                'options': [
                    {'value': 'draft', 'label': '草稿'},
                    {'value': 'approved', 'label': '已审批'},
                    {'value': 'sent', 'label': '已下达'},
                    {'value': 'partial_received', 'label': '部分到货'},
                    {'value': 'received', 'label': '已到货'},
                    {'value': 'closed', 'label': '已关闭'}
                ]
            },
            'default_value': 'draft'
        }
    ]
    
    for field_data in fields:
        ModuleService.add_module_field(
            module_id=str(module.id),
            **field_data
        )
    
    print(f"✓ 采购管理模块初始化完成，模块ID: {module.id}")
    return module


def init_finance_management_module():
    """初始化财务管理模块"""
    print("初始化财务管理模块...")
    
    module = ModuleService.create_system_module(
        name='finance_management',
        display_name='财务管理',
        description='应收应付、财务核算、成本管理等财务业务',
        category='finance',
        version='1.0.0',
        icon='icon-finance',
        sort_order=35,
        is_core=False,
        dependencies=['sales_management', 'purchase_management'],
        default_config={
            'enable_cost_center': True,
            'auto_accounting': True,
            'currency_support': ['CNY', 'USD', 'EUR'],
            'tax_calculation': True
        }
    )
    
    # 添加字段定义
    fields = [
        {
            'field_name': 'voucher_number',
            'display_name': '凭证号',
            'field_type': 'string',
            'description': '财务凭证编号',
            'is_required': True,
            'is_system_field': True,
            'is_configurable': False,
            'sort_order': 1,
            'validation_rules': {'pattern': '^FV\\d{8}$', 'max_length': 20}
        },
        {
            'field_name': 'account_code',
            'display_name': '科目编码',
            'field_type': 'string',
            'description': '会计科目编码',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 2,
            'validation_rules': {'max_length': 20}
        },
        {
            'field_name': 'transaction_date',
            'display_name': '交易日期',
            'field_type': 'date',
            'description': '财务交易发生日期',
            'is_required': True,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 3
        },
        {
            'field_name': 'debit_amount',
            'display_name': '借方金额',
            'field_type': 'number',
            'description': '借方金额',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 4,
            'validation_rules': {'min': 0},
            'field_options': {'currency': 'CNY', 'decimal_places': 2}
        },
        {
            'field_name': 'credit_amount',
            'display_name': '贷方金额',
            'field_type': 'number',
            'description': '贷方金额',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 5,
            'validation_rules': {'min': 0},
            'field_options': {'currency': 'CNY', 'decimal_places': 2}
        },
        {
            'field_name': 'description',
            'display_name': '摘要',
            'field_type': 'string',
            'description': '财务交易描述',
            'is_required': False,
            'is_system_field': False,
            'is_configurable': True,
            'sort_order': 6,
            'validation_rules': {'max_length': 200}
        }
    ]
    
    for field_data in fields:
        ModuleService.add_module_field(
            module_id=str(module.id),
            **field_data
        )
    
    print(f"✓ 财务管理模块初始化完成，模块ID: {module.id}")
    return module


def main():
    """主函数"""
    print("开始初始化KylinKing系统模块...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 创建数据库表
            db.create_all()
            
            # 检查并初始化新模块
            modules_to_init = [
                ('basic_data', '基础档案', init_basic_data_module),
                ('sales_management', '销售管理', init_sales_management_module),
                ('warehouse_management', '仓库管理', init_warehouse_management_module),
                ('purchase_management', '采购管理', init_purchase_management_module),
                ('production_planning', '生产管理', init_production_planning_module),
                ('finance_management', '财务管理', init_finance_management_module)
            ]
            
            initialized_modules = []
            skipped_modules = []
            
            for module_name, module_display_name, init_func in modules_to_init:
                # 检查模块是否已存在
                from app.models.module import SystemModule
                existing_module = db.session.query(SystemModule).filter(
                    SystemModule.name == module_name
                ).first()
                
                if existing_module:
                    print(f"⚠️ 模块 '{module_display_name}' 已存在，跳过初始化")
                    skipped_modules.append(module_display_name)
                else:
                    print(f"🔄 初始化模块 '{module_display_name}'...")
                    module = init_func()
                    initialized_modules.append(module_display_name)
            
            print(f"\n🎉 模块初始化完成！")
            
            if initialized_modules:
                print(f"✅ 新初始化的模块 ({len(initialized_modules)}):")
                for module in initialized_modules:
                    print(f"- {module}")
            
            if skipped_modules:
                print(f"⚠️ 跳过的模块 ({len(skipped_modules)}):")
                for module in skipped_modules:
                    print(f"- {module}")
                    
            # 显示所有现有模块
            from app.models.module import SystemModule
            all_modules = db.session.query(SystemModule).filter(
                SystemModule.is_active == True
            ).order_by(SystemModule.sort_order).all()
            
            print(f"\n📋 系统中所有活跃模块 ({len(all_modules)}):")
            for module in all_modules:
                core_indicator = "(核心模块)" if module.is_core else ""
                print(f"- {module.display_name} {core_indicator}")
            
            print(f"\n💡 下一步:")
            print(f"1. 为租户初始化模块配置: POST /api/admin/modules/tenants/<tenant_id>/initialize")
            print(f"2. 配置租户字段: POST /api/tenant/modules/<module_id>/fields/<field_id>/configure")
            print(f"3. 创建租户扩展: POST /api/tenant/modules/extensions")
            
        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main() 