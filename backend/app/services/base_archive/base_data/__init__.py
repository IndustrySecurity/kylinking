# -*- coding: utf-8 -*-
"""
基础数据服务模块
"""

from .customer_service import CustomerService
from .supplier_service import SupplierService
from .product_management_service import ProductManagementService
from .material_management_service import MaterialService
from .department_service import DepartmentService
from .position_service import PositionService
from .employee_service import EmployeeService
from .team_group_service import TeamGroupService

__all__ = [
    'CustomerService',
    'SupplierService', 
    'ProductManagementService',
    'MaterialService',
    'DepartmentService',
    'PositionService',
    'EmployeeService',
    'TeamGroupService'
]
