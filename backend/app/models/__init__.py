# 导入所有模型，确保SQLAlchemy可以正确加载它们
from app.models.base import SystemModel
from app.models.user import User, Role, Permission, organization_users
from app.models.organization import Organization
from app.models.tenant import Tenant
from app.models.module import (
    SystemModule, 
    ModuleField, 
    TenantModule, 
    TenantFieldConfig, 
    TenantExtension
)
from app.models.basic_data import (
    CustomerCategory,
    Customer,
    SupplierCategory, 
    Supplier,
    ProductCategory,
    Product,
    PackageMethod,
    DeliveryMethod,
    ColorCard,
    Unit,
    Specification,
    Currency,
    LossType
)
from app.models.column_configuration import ColumnConfiguration

# 添加其他可能的模型导入

__all__ = [
    'User', 
    'Role', 
    'Permission', 
    'Organization', 
    'Tenant',
    'SystemModel',
    'organization_users',
    'SystemModule',
    'ModuleField',
    'TenantModule',
    'TenantFieldConfig',
    'TenantExtension',
    'CustomerCategory',
    'Customer',
    'SupplierCategory', 
    'Supplier',
    'ProductCategory',
    'Product',
    'PackageMethod',
    'DeliveryMethod',
    'ColorCard',
    'Unit',
    'Specification',
    'Currency',
    'LossType',
    'ColumnConfiguration'
] 