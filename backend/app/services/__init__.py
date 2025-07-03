# -*- coding: utf-8 -*-
"""
服务层统一导入管理 - 安全导入版本
"""

# 基础服务类
from .base_service import BaseService, TenantAwareService, ServiceFactory

# ==================== 安全导入策略 ====================
# 使用try-except包装所有导入，避免语法错误导致应用启动失败

# 基础分类管理服务
try:
    from .base_archive.base_category.customer_category_service import CustomerCategoryService
except Exception as e:
    print(f"❌ CustomerCategoryService导入失败: {e}")
    CustomerCategoryService = None

try:
    from .base_archive.base_category.supplier_category_service import SupplierCategoryService  
except Exception as e:
    print(f"❌ SupplierCategoryService导入失败: {e}")
    SupplierCategoryService = None

try:
    from .base_archive.base_category.process_category_service import ProcessCategoryService
except Exception as e:
    print(f"❌ ProcessCategoryService导入失败: {e}")
    ProcessCategoryService = None

try:
    from .base_archive.base_category.product_category_service import ProductCategoryService
except Exception as e:
    print(f"❌ ProductCategoryService导入失败: {e}")
    ProductCategoryService = None

try:
    from .base_archive.base_category.material_category_service import MaterialCategoryService
except Exception as e:
    print(f"❌ MaterialCategoryService导入失败: {e}")
    MaterialCategoryService = None

# 基础数据管理服务
try:
    from .base_archive.base_data.customer_service import CustomerService
except Exception as e:
    print(f"❌ CustomerService导入失败: {e}")
    CustomerService = None

try:
    from .base_archive.base_data.supplier_service import SupplierService
except Exception as e:
    print(f"❌ SupplierService导入失败: {e}")
    SupplierService = None

try:
    from .base_archive.base_data.department_service import DepartmentService
except Exception as e:
    print(f"❌ DepartmentService导入失败: {e}")
    DepartmentService = None

try:
    from .base_archive.base_data.position_service import PositionService
except Exception as e:
    print(f"❌ PositionService导入失败: {e}")
    PositionService = None

try:
    from .base_archive.base_data.employee_service import EmployeeService
except Exception as e:
    print(f"❌ EmployeeService导入失败: {e}")
    EmployeeService = None

try:
    from .base_archive.base_data.product_management_service import ProductManagementService
except Exception as e:
    print(f"❌ ProductManagementService导入失败: {e}")
    ProductManagementService = None

try:
    from .base_archive.base_data.material_management_service import MaterialService
except Exception as e:
    print(f"❌ MaterialService导入失败: {e}")
    MaterialService = None

# 生产档案服务 - 大部分有语法错误，暂时跳过
try:
    from .base_archive.production.production_archive.color_card_service import ColorCardService
except Exception as e:
    print(f"❌ ColorCardService导入失败: {e}")
    ColorCardService = None

try:
    from .base_archive.production.production_archive.delivery_method_service import DeliveryMethodService
except Exception as e:
    print(f"❌ DeliveryMethodService导入失败: {e}")
    DeliveryMethodService = None

try:
    from .base_archive.production.production_archive.unit_service import UnitService
except Exception as e:
    print(f"❌ UnitService导入失败: {e}")
    UnitService = None

try:
    from .base_archive.production.production_archive.specification_service import SpecificationService
except Exception as e:
    print(f"❌ SpecificationService导入失败: {e}")
    SpecificationService = None

# 财务管理服务
try:
    from .base_archive.financial_management.currency_service import CurrencyService
except Exception as e:
    print(f"❌ CurrencyService导入失败: {e}")
    CurrencyService = None

# 业务服务
try:
    from .business.sales.sales_order_service import SalesOrderService
except Exception as e:
    print(f"❌ SalesOrderService导入失败: {e}")
    SalesOrderService = None

try:
    from .business.inventory.inventory_service import InventoryService
except Exception as e:
    print(f"❌ InventoryService导入失败: {e}")
    InventoryService = None

try:
    from .business.inventory.material_inbound_service import MaterialInboundService
except Exception as e:
    print(f"❌ MaterialInboundService导入失败: {e}")
    MaterialInboundService = None

try:
    from .business.inventory.material_outbound_service import MaterialOutboundService
except Exception as e:
    print(f"❌ MaterialOutboundService导入失败: {e}")
    MaterialOutboundService = None

try:
    from .business.inventory.product_outbound_service import ProductOutboundService
except Exception as e:
    print(f"❌ ProductOutboundService导入失败: {e}")
    ProductOutboundService = None

try:
    from .business.inventory.product_inbound_service import ProductInboundService
except Exception as e:
    print(f"❌ ProductInboundService导入失败: {e}")
    ProductInboundService = None

try:
    from .business.inventory.material_count_service import MaterialCountService
except Exception as e:
    print(f"❌ MaterialCountService导入失败: {e}")
    MaterialCountService = None

# 其他核心服务
try:
    from .module_service import ModuleService
except Exception as e:
    print(f"❌ ModuleService导入失败: {e}")
    ModuleService = None

# 只导出成功导入的服务
__all__ = [
    'BaseService',
    'TenantAwareService', 
    'ServiceFactory',
]

# 动态添加成功导入的服务到__all__
services_to_check = [
    'CustomerCategoryService', 'SupplierCategoryService', 'ProcessCategoryService',
    'ProductCategoryService', 'MaterialCategoryService', 'CustomerService', 
    'SupplierService', 'DepartmentService', 'PositionService', 'EmployeeService',
    'ProductManagementService', 'MaterialService', 'ColorCardService',
    'DeliveryMethodService', 'UnitService', 'SpecificationService',
    'CurrencyService', 'SalesOrderService', 'InventoryService',
    'MaterialInboundService', 'MaterialOutboundService', 'ProductOutboundService',
    'ProductInboundService', 'MaterialCountService', 'ModuleService'
]

for service_name in services_to_check:
    if globals().get(service_name) is not None:
        __all__.append(service_name)

print(f"✅ 成功导入 {len(__all__) - 3} 个服务类")

# ==================== 服务创建便捷方法 ====================

def create_service(service_class, tenant_id=None, schema_name=None, **kwargs):
    """创建服务实例的便捷方法"""
    if service_class is None:
        raise ValueError("服务类未正确导入")
    return ServiceFactory.create_service(service_class, tenant_id, schema_name, **kwargs)

def create_tenant_service(service_class, tenant_id, **kwargs):
    """创建租户感知服务实例的便捷方法"""
    if service_class is None:
        raise ValueError("服务类未正确导入")
    return ServiceFactory.create_tenant_service(service_class, tenant_id, **kwargs)


# ==================== 服务分组字典 ====================
# 只包含成功导入的服务

def get_available_services():
    """获取所有成功导入的服务"""
    available = {}
    
    # 基础分类服务
    if CustomerCategoryService:
        available['customer_category'] = CustomerCategoryService
    if SupplierCategoryService:
        available['supplier_category'] = SupplierCategoryService
    if ProcessCategoryService:
        available['process_category'] = ProcessCategoryService
    if ProductCategoryService:
        available['product_category'] = ProductCategoryService
    if MaterialCategoryService:
        available['material_category'] = MaterialCategoryService
    
    # 基础数据服务
    if CustomerService:
        available['customer'] = CustomerService
    if SupplierService:
        available['supplier'] = SupplierService
    if DepartmentService:
        available['department'] = DepartmentService
    if EmployeeService:
        available['employee'] = EmployeeService
    if ProductManagementService:
        available['product_management'] = ProductManagementService
    if MaterialService:
        available['material'] = MaterialService
    
    # 生产档案服务
    if ColorCardService:
        available['color_card'] = ColorCardService
    if DeliveryMethodService:
        available['delivery_method'] = DeliveryMethodService
    if UnitService:
        available['unit'] = UnitService
    if SpecificationService:
        available['specification'] = SpecificationService
    
    # 财务管理服务
    if CurrencyService:
        available['currency'] = CurrencyService
    
    # 业务服务
    if SalesOrderService:
        available['sales_order'] = SalesOrderService
    if InventoryService:
        available['inventory'] = InventoryService
    if MaterialInboundService:
        available['material_inbound'] = MaterialInboundService
    if MaterialOutboundService:
        available['material_outbound'] = MaterialOutboundService
    if ProductOutboundService:
        available['product_outbound'] = ProductOutboundService
    if ProductInboundService:
        available['product_inbound'] = ProductInboundService
    if MaterialCountService:
        available['material_count'] = MaterialCountService
    
    return available 