# -*- coding: utf-8 -*-
"""
Supplier 服务
"""

from app.services.base_service import TenantAwareService
from app.models.basic_data import SupplierManagement, SupplierCategoryManagement
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re
import logging

class SupplierService(TenantAwareService):
    """供应商档案服务"""
    
    def __init__(self, tenant_id=None, schema_name=None):
        super().__init__(tenant_id=tenant_id, schema_name=schema_name)
        self.logger = logging.getLogger(__name__)  # 添加logger初始化
    
    def generate_code(self, entity_type):
        """生成编码"""
        prefixes = {
            'customer': 'C',
            'supplier': 'S', 
            'product': 'P',
            'material': 'M'
        }
        
        prefix = prefixes.get(entity_type, 'X')
        
        # 获取当前最大编号
        if entity_type == 'supplier':
            max_code = self.session.query(func.max(SupplierManagement.supplier_code)).scalar()
        else:
            raise ValueError(f"不支持的实体类型: {entity_type}")
        
        if max_code:
            # 提取数字部分并加1
            try:
                number = int(max_code[1:]) + 1
            except (ValueError, IndexError):
                number = 1
        else:
            number = 1
        
        return f"{prefix}{number:06d}"
    
    def get_suppliers(self, page=1, per_page=20, search=None, category_id=None, status=None):
        """获取供应商列表"""
        query = self.session.query(SupplierManagement)
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                SupplierManagement.supplier_code.ilike(search_pattern),
                SupplierManagement.supplier_name.ilike(search_pattern)
            ))
        
        # 分类筛选
        if category_id:
            query = query.filter(SupplierManagement.supplier_category_id == uuid.UUID(category_id))
        
        # 状态筛选
        if status:
            query = query.filter(SupplierManagement.is_enabled == (status == 'active'))
        
        # 排序
        query = query.order_by(SupplierManagement.created_at.desc())
        
        # 分页
        total = query.count()
        suppliers = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'suppliers': [supplier.to_dict() for supplier in suppliers],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def create_supplier(self, data, created_by):
        """创建供应商"""
        try:
            # 生成供应商编码
            if not data.get('supplier_code'):
                data['supplier_code'] = self.generate_code('supplier')
            
            # 准备供应商数据
            supplier_data = {
                'supplier_code': data['supplier_code'],
                'supplier_name': data['supplier_name'],
                'supplier_category_id': uuid.UUID(data['supplier_category_id']) if data.get('supplier_category_id') else None,
                
                # 基本信息
                'legal_name': data.get('legal_name'),
                'unified_credit_code': data.get('unified_credit_code'),
                'business_license': data.get('business_license'),
                'industry': data.get('industry'),
                'established_date': data.get('established_date'),
                
                # 联系信息
                'contact_person': data.get('contact_person'),
                'contact_phone': data.get('contact_phone'),
                'contact_email': data.get('contact_email'),
                'office_address': data.get('office_address'),
                'factory_address': data.get('factory_address'),
                
                # 业务信息
                'payment_terms': data.get('payment_terms', 30),
                'currency': data.get('currency', 'CNY'),
                'quality_level': data.get('quality_level', 'qualified'),
                'cooperation_level': data.get('cooperation_level', 'ordinary'),
                
                # 自定义字段
                'custom_fields': data.get('custom_fields', {}),
            }
            
            # 使用继承的create_with_tenant方法
            supplier = self.create_with_tenant(SupplierManagement, **supplier_data)
            self.commit()
            
            return supplier.to_dict()
            
        except IntegrityError:
            self.rollback()
            raise ValueError("供应商编码已存在")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建供应商失败: {str(e)}")
    
    def get_supplier_by_id(self, supplier_id):
        """根据ID获取供应商"""
        supplier = self.session.query(SupplierManagement).get(uuid.UUID(supplier_id))
        if not supplier:
            return None
        return supplier.to_dict()
    
    def update_supplier(self, supplier_id, data, updated_by):
        """更新供应商"""
        try:
            supplier = self.session.query(SupplierManagement).get(uuid.UUID(supplier_id))
            if not supplier:
                return None
            
            # 更新字段
            update_fields = [
                'supplier_name', 'legal_name', 'unified_credit_code',
                'business_license', 'industry', 'contact_person',
                'contact_phone', 'contact_email', 'office_address',
                'factory_address', 'payment_terms', 'currency',
                'quality_level', 'cooperation_level'
            ]
            
            for field in update_fields:
                if field in data:
                    setattr(supplier, field, data[field])
            
            if 'supplier_category_id' in data:
                supplier.supplier_category_id = uuid.UUID(data['supplier_category_id']) if data['supplier_category_id'] else None
            
            supplier.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            return supplier.to_dict()
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新供应商失败: {str(e)}")
    
    def delete_supplier(self, supplier_id):
        """删除供应商"""
        try:
            supplier = self.session.query(SupplierManagement).get(uuid.UUID(supplier_id))
            if not supplier:
                return False
            
            self.session.delete(supplier)
            self.commit()
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除供应商失败: {str(e)}")
    
    def get_form_options(self):
        """获取供应商表单选项数据"""
        try:
            from app.models.basic_data import (
                SupplierCategoryManagement, DeliveryMethod, TaxRate, 
                Currency, PaymentMethod, Employee
            )
            
            # 获取供应商分类
            try:
                categories = self.session.query(SupplierCategoryManagement).filter(
                    SupplierCategoryManagement.is_enabled == True
                ).order_by(SupplierCategoryManagement.category_name).all()
            except Exception as e:
                self.logger.error(f"获取供应商分类失败: {str(e)}")
                categories = []
            
            # 获取送货方式
            try:
                delivery_methods = self.session.query(DeliveryMethod).filter(
                    DeliveryMethod.is_enabled == True
                ).order_by(DeliveryMethod.delivery_name).all()
            except Exception as e:
                self.logger.error(f"获取送货方式失败: {str(e)}")
                delivery_methods = []
            
            # 获取税率
            try:
                tax_rates = self.session.query(TaxRate).filter(
                    TaxRate.is_enabled == True
                ).order_by(TaxRate.tax_name).all()
            except Exception as e:
                self.logger.error(f"获取税率失败: {str(e)}")
                tax_rates = []
            
            # 获取币别
            try:
                currencies = self.session.query(Currency).filter(
                    Currency.is_enabled == True
                ).order_by(Currency.currency_name).all()
            except Exception as e:
                self.logger.error(f"获取币别失败: {str(e)}")
                currencies = []
            
            # 获取付款方式
            try:
                payment_methods = self.session.query(PaymentMethod).filter(
                    PaymentMethod.is_enabled == True
                ).order_by(PaymentMethod.payment_name).all()
            except Exception as e:
                self.logger.error(f"获取付款方式失败: {str(e)}")
                payment_methods = []
            
            # 获取员工（采购员）
            try:
                employees = self.session.query(Employee).filter(
                    Employee.is_enabled == True
                ).order_by(Employee.employee_name).all()
            except Exception as e:
                self.logger.error(f"获取员工失败: {str(e)}")
                employees = []
            
            return {
                'supplier_categories': [
                    {'value': str(cat.id), 'label': cat.category_name}
                    for cat in categories
                ],
                'delivery_methods': [
                    {'value': str(dm.id), 'label': dm.delivery_name}
                    for dm in delivery_methods
                ],
                'tax_rates': [
                    {'value': str(tr.id), 'label': tr.tax_name, 'rate': float(tr.tax_rate)}
                    for tr in tax_rates
                ],
                'currencies': [
                    {'value': str(cur.id), 'label': cur.currency_name}
                    for cur in currencies
                ],
                'payment_methods': [
                    {'value': str(pm.id), 'label': pm.payment_name}
                    for pm in payment_methods
                ],
                'employees': [
                    {'value': str(emp.id), 'label': emp.employee_name}
                    for emp in employees
                ],
                'supplier_levels': [
                    {'value': 'A', 'label': 'A'},
                    {'value': 'B', 'label': 'B'}
                ],
                'enterprise_types': [
                    {'value': 'individual', 'label': '个人'},
                    {'value': 'individual_business', 'label': '个体工商户'},
                    {'value': 'limited_company', 'label': '有限责任公司'}
                ],
                'provinces': [
                    {'value': '北京', 'label': '北京'},
                    {'value': '天津', 'label': '天津'},
                    {'value': '河北', 'label': '河北'},
                    {'value': '山西', 'label': '山西'},
                    {'value': '内蒙古', 'label': '内蒙古'},
                    {'value': '辽宁', 'label': '辽宁'},
                    {'value': '吉林', 'label': '吉林'},
                    {'value': '黑龙江', 'label': '黑龙江'},
                    {'value': '上海', 'label': '上海'},
                    {'value': '江苏', 'label': '江苏'},
                    {'value': '浙江', 'label': '浙江'},
                    {'value': '安徽', 'label': '安徽'},
                    {'value': '福建', 'label': '福建'},
                    {'value': '江西', 'label': '江西'},
                    {'value': '山东', 'label': '山东'},
                    {'value': '河南', 'label': '河南'},
                    {'value': '湖北', 'label': '湖北'},
                    {'value': '湖南', 'label': '湖南'},
                    {'value': '广东', 'label': '广东'},
                    {'value': '广西', 'label': '广西'},
                    {'value': '海南', 'label': '海南'},
                    {'value': '重庆', 'label': '重庆'},
                    {'value': '四川', 'label': '四川'},
                    {'value': '贵州', 'label': '贵州'},
                    {'value': '云南', 'label': '云南'},
                    {'value': '西藏', 'label': '西藏'},
                    {'value': '陕西', 'label': '陕西'},
                    {'value': '甘肃', 'label': '甘肃'},
                    {'value': '青海', 'label': '青海'},
                    {'value': '宁夏', 'label': '宁夏'},
                    {'value': '新疆', 'label': '新疆'},
                    {'value': '台湾', 'label': '台湾'},
                    {'value': '香港', 'label': '香港'},
                    {'value': '澳门', 'label': '澳门'}
                ]
            }
            
        except Exception as e:
            raise ValueError(f"获取表单选项失败: {str(e)}")


def get_supplier_service(tenant_id: str = None, schema_name: str = None) -> SupplierService:
    """获取供应商服务实例"""
    return SupplierService(tenant_id=tenant_id, schema_name=schema_name)


