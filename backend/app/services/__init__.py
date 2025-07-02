# -*- coding: utf-8 -*-
"""
服务层统一导入管理 - 重新组织后的版本
"""

# 基础服务类
from .base_service import BaseService, TenantAwareService, ServiceFactory

# ==================== 基础档案服务 ====================

# 基础分类管理服务
from .base_archive.base_category.customer_category_service import CustomerCategoryService
from .base_archive.base_category.supplier_category_service import SupplierCategoryService
from .base_archive.base_category.process_category_service import ProcessCategoryService
from .base_archive.base_category.product_category_service import ProductCategoryService
from .base_archive.base_category.material_category_service import MaterialCategoryService

# 基础数据管理服务
from .base_archive.base_data.customer_service import CustomerService
from .base_archive.base_data.supplier_service import SupplierService
from .base_archive.base_data.department_service import DepartmentService
from .base_archive.base_data.position_service import PositionService
from .base_archive.base_data.employee_service import EmployeeService
from .base_archive.base_data.product_management_service import ProductManagementService
from .base_archive.base_data.material_management_service import MaterialService

# 生产档案服务
from .base_archive.production.production_archive.package_method_service import PackageMethodService
from .base_archive.production.production_archive.unit_service import UnitService
from .base_archive.production.production_archive.color_card_service import ColorCardService
from .base_archive.production.production_archive.machine_service import MachineService
from .base_archive.production.production_archive.process_service import ProcessService
from .base_archive.production.production_archive.specification_service import SpecificationService
from .base_archive.production.production_archive.loss_type_service import LossTypeService
from .base_archive.production.production_archive.bag_type_service import BagTypeService
from .base_archive.production.production_archive.warehouse_service import WarehouseService
from .base_archive.production.production_archive.team_group_service import TeamGroupService

# 生产配置服务
from .base_archive.production.production_config.ink_option_service import InkOptionService
from .base_archive.production.production_config.quote_freight_service import QuoteFreightService
from .base_archive.production.production_config.quote_ink_service import QuoteInkService
from .base_archive.production.production_config.quote_material_service import QuoteMaterialService
from .base_archive.production.production_config.quote_accessory_service import QuoteAccessoryService
from .base_archive.production.production_config.quote_loss_service import QuoteLossService
from .base_archive.production.production_archive.delivery_method_service import DeliveryMethodService
from .base_archive.production.production_config.calculation_parameter_service import CalculationParameterService
from .base_archive.production.production_config.calculation_scheme_service import CalculationSchemeService
from .base_archive.production.production_config.bag_related_formula_service import BagRelatedFormulaService

# 财务管理服务
from .base_archive.financial_management.currency_service import CurrencyService
from .base_archive.financial_management.tax_rate_service import TaxRateService
from .base_archive.financial_management.settlement_method_service import SettlementMethodService
from .base_archive.financial_management.account_service import AccountService
from .base_archive.financial_management.payment_method_service import PaymentMethodService

# ==================== 业务服务 ====================

# 销售管理服务
from .business.sales.sales_order_service import SalesOrderService
from .business.sales.delivery_notice_service import DeliveryNoticeService

# 库存管理服务
from .business.inventory.inventory_service import InventoryService
from .business.inventory.material_inbound_service import MaterialInboundService
from .business.inventory.material_outbound_service import MaterialOutboundService
from .business.inventory.material_transfer_service import MaterialTransferService
from .business.inventory.outbound_order_service import OutboundOrderService
from .business.inventory.product_count_service import ProductCountService
from .business.inventory.product_transfer_service import ProductTransferService

# 其他核心服务（暂时保留在根目录）
try:
    from .module_service import ModuleService
except ImportError:
    # 这些服务可能还没有重构，跳过导入错误
    pass

__all__ = [
    # 基础服务类
    'BaseService',
    'TenantAwareService', 
    'ServiceFactory',
    
    # 基础档案 - 基础分类
    'CustomerCategoryService',
    'SupplierCategoryService',
    'ProcessCategoryService',
    'ProductCategoryService',
    'MaterialCategoryService',
    
    # 基础档案 - 基础数据
    'CustomerService',
    'SupplierService',
    'DepartmentService',
    'PositionService',
    'EmployeeService',
    'ProductManagementService',
    'MaterialService',
    
    # 基础档案 - 生产档案
    'PackageMethodService',
    'UnitService',
    'ColorCardService',
    'MachineService',
    'ProcessService',
    'SpecificationService',
    'LossTypeService',
    'BagTypeService',
    'WarehouseService',
    'TeamGroupService',
    
    # 基础档案 - 生产配置
    'InkOptionService',
    'QuoteFreightService',
    'QuoteInkService',
    'QuoteMaterialService',
    'QuoteAccessoryService',
    'QuoteLossService',
    'DeliveryMethodService',
    'CalculationParameterService',
    'CalculationSchemeService',
    'BagRelatedFormulaService',
    
    # 基础档案 - 财务管理
    'CurrencyService',
    'TaxRateService',
    'SettlementMethodService',
    'AccountService',
    'PaymentMethodService',
    
    # 业务功能 - 销售管理
    'SalesOrderService',
    'DeliveryNoticeService',
    
    # 业务功能 - 库存管理
    'InventoryService',
    'MaterialInboundService',
    'MaterialOutboundService',
    'MaterialTransferService',
    'OutboundOrderService',
    'ProductCountService',
    'ProductTransferService',
]


# ==================== 便捷创建方法 ====================

def create_service(service_class, tenant_id=None, schema_name=None, **kwargs):
    """
    创建服务实例的便捷方法
    
    Args:
        service_class: 服务类
        tenant_id: 租户ID
        schema_name: Schema名称
        **kwargs: 其他参数
        
    Returns:
        服务实例
    """
    return ServiceFactory.create_service(service_class, tenant_id, schema_name, **kwargs)


def create_tenant_service(service_class, tenant_id, **kwargs):
    """
    创建租户感知服务实例的便捷方法
    
    Args:
        service_class: 服务类
        tenant_id: 租户ID
        **kwargs: 其他参数
        
    Returns:
        服务实例
    """
    return ServiceFactory.create_tenant_service(service_class, tenant_id, **kwargs)


# ==================== 服务分组字典 ====================

BASE_ARCHIVE_SERVICES = {
    # 基础分类
    'base_category': {
        'customer_category': CustomerCategoryService,
        'supplier_category': SupplierCategoryService,
        'process_category': ProcessCategoryService,
        'product_category': ProductCategoryService,
        'material_category': MaterialCategoryService,
    },
    
    # 基础数据
    'base_data': {
        'customer': CustomerService,
        'supplier': SupplierService,
        'product_management': ProductManagementService,
        'material_management': MaterialService,
    },
    
    # 生产档案
    'production_archive': {
        'package_method': PackageMethodService,
        'unit': UnitService,
        'color_card': ColorCardService,
        'machine': MachineService,
        'process': ProcessService,
        'specification': SpecificationService,
        'loss_type': LossTypeService,
        'bag_type': BagTypeService,
    },
    
    # 生产配置
    'production_config': {
        'ink_option': InkOptionService,
        'quote_freight': QuoteFreightService,
        'quote_ink': QuoteInkService,
        'quote_material': QuoteMaterialService,
        'quote_accessory': QuoteAccessoryService,
        'quote_loss': QuoteLossService,
        'delivery_method': DeliveryMethodService,
        'calculation_parameter': CalculationParameterService,
        'calculation_scheme': CalculationSchemeService,
        'bag_related_formula': BagRelatedFormulaService,
    },
    
    # 财务管理
    'financial_management': {
        'currency': CurrencyService,
        'tax_rate': TaxRateService,
        'settlement_method': SettlementMethodService,
        'account': AccountService,
        'payment_method': PaymentMethodService,
    }
}

BUSINESS_SERVICES = {
    # 销售管理
    'sales': {
        'sales_order': SalesOrderService,
        'delivery_notice': DeliveryNoticeService,
    },
    
    # 库存管理
    'inventory': {
        'inventory': InventoryService,
        'material_inbound': MaterialInboundService,
        'material_outbound': MaterialOutboundService,
        'material_transfer': MaterialTransferService,
        'outbound_order': OutboundOrderService,
        'product_count': ProductCountService,
        'product_transfer': ProductTransferService,
    }
}


def get_service_by_path(service_path: str):
    """
    根据路径获取服务类
    
    Args:
        service_path: 服务路径，如 'base_archive.base_category.customer_category'
        
    Returns:
        服务类
        
    Example:
        service_class = get_service_by_path('base_archive.base_category.customer_category')
        service = create_service(service_class, tenant_id='tenant_123')
    """
    parts = service_path.split('.')
    
    if parts[0] == 'base_archive' and len(parts) == 3:
        category = parts[1]
        service_name = parts[2]
        return BASE_ARCHIVE_SERVICES.get(category, {}).get(service_name)
    
    elif parts[0] == 'business' and len(parts) == 3:
        category = parts[1]
        service_name = parts[2]
        return BUSINESS_SERVICES.get(category, {}).get(service_name)
    
    return None 