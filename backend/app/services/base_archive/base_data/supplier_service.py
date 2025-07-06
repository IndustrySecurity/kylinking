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
        query = self.session.query(SupplierManagement).outerjoin(
            SupplierCategoryManagement, 
            SupplierManagement.supplier_category_id == SupplierCategoryManagement.id
        )
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                SupplierManagement.supplier_code.ilike(search_pattern),
                SupplierManagement.supplier_name.ilike(search_pattern),
                SupplierManagement.supplier_abbreviation.ilike(search_pattern)
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
        
        # 构建返回数据，包含供应商分类名称
        suppliers_data = []
        for supplier in suppliers:
            supplier_dict = supplier.to_dict()
            # 添加供应商分类名称
            if supplier.supplier_category_id:
                category = self.session.query(SupplierCategoryManagement).get(supplier.supplier_category_id)
                supplier_dict['supplier_category_name'] = category.category_name if category else None
            else:
                supplier_dict['supplier_category_name'] = None
            suppliers_data.append(supplier_dict)
        
        return {
            'suppliers': suppliers_data,
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
                'supplier_abbreviation': data.get('supplier_abbreviation'),
                'supplier_category_id': uuid.UUID(data['supplier_category_id']) if data.get('supplier_category_id') and data.get('supplier_category_id') != '' else None,
                'purchaser_id': uuid.UUID(data['purchaser_id']) if data.get('purchaser_id') and data.get('purchaser_id') != '' else None,
                'region': data.get('region'),
                'delivery_method_id': uuid.UUID(data['delivery_method_id']) if data.get('delivery_method_id') and data.get('delivery_method_id') != '' else None,
                'tax_rate_id': uuid.UUID(data['tax_rate_id']) if data.get('tax_rate_id') and data.get('tax_rate_id') != '' else None,
                'tax_rate': data.get('tax_rate'),
                'currency_id': uuid.UUID(data['currency_id']) if data.get('currency_id') and data.get('currency_id') != '' else None,
                'payment_method_id': uuid.UUID(data['payment_method_id']) if data.get('payment_method_id') and data.get('payment_method_id') != '' else None,
                'deposit_ratio': data.get('deposit_ratio'),
                'delivery_preparation_days': data.get('delivery_preparation_days'),
                'copyright_square_price': data.get('copyright_square_price'),
                'supplier_level': data.get('supplier_level'),
                'organization_code': data.get('organization_code'),
                'company_website': data.get('company_website'),
                'foreign_currency_id': uuid.UUID(data['foreign_currency_id']) if data.get('foreign_currency_id') and data.get('foreign_currency_id') != '' else None,
                'barcode_prefix_code': data.get('barcode_prefix_code'),
                'business_start_date': data.get('business_start_date'),
                'business_end_date': data.get('business_end_date'),
                'production_permit_start_date': data.get('production_permit_start_date'),
                'production_permit_end_date': data.get('production_permit_end_date'),
                'inspection_report_start_date': data.get('inspection_report_start_date'),
                'inspection_report_end_date': data.get('inspection_report_end_date'),
                'barcode_authorization': data.get('barcode_authorization'),
                'ufriend_code': data.get('ufriend_code'),
                'enterprise_type': data.get('enterprise_type'),
                'province': data.get('province'),
                'city': data.get('city'),
                'district': data.get('district'),
                'company_address': data.get('company_address'),
                'remarks': data.get('remarks'),
                'image_url': data.get('image_url'),
                'sort_order': data.get('sort_order', 0),
                'is_enabled': data.get('is_enabled', True),
                'created_by': uuid.UUID(created_by)
            }
            
            # 创建供应商主表
            supplier = self.create_with_tenant(SupplierManagement, **supplier_data)
            
            # 处理子表数据
            from app.models.basic_data import (
                SupplierContact, SupplierDeliveryAddress, 
                SupplierInvoiceUnit, SupplierAffiliatedCompany
            )
            
            # 创建联系人
            if 'contacts' in data and data['contacts']:
                for contact_data in data['contacts']:
                    if contact_data.get('contact_name'):  # 只有填写了联系人名称才创建
                        contact = self.create_with_tenant(SupplierContact,
                            supplier_id=supplier.id,
                            contact_name=contact_data.get('contact_name'),
                            landline=contact_data.get('landline'),
                            mobile=contact_data.get('mobile'),
                            fax=contact_data.get('fax'),
                            qq=contact_data.get('qq'),
                            wechat=contact_data.get('wechat'),
                            email=contact_data.get('email'),
                            department=contact_data.get('department'),
                            sort_order=contact_data.get('sort_order', 0)
                        )
            
            # 创建发货地址
            if 'delivery_addresses' in data and data['delivery_addresses']:
                for addr_data in data['delivery_addresses']:
                    if addr_data.get('delivery_address'):
                        addr = self.create_with_tenant(SupplierDeliveryAddress,
                            supplier_id=supplier.id,
                            delivery_address=addr_data.get('delivery_address'),
                            contact_name=addr_data.get('contact_name'),
                            contact_method=addr_data.get('contact_method'),
                            sort_order=addr_data.get('sort_order', 0)
                        )
            
            # 创建开票单位
            if 'invoice_units' in data and data['invoice_units']:
                for invoice_data in data['invoice_units']:
                    if invoice_data.get('invoice_unit'):
                        invoice = self.create_with_tenant(SupplierInvoiceUnit,
                            supplier_id=supplier.id,
                            invoice_unit=invoice_data.get('invoice_unit'),
                            taxpayer_id=invoice_data.get('taxpayer_id'),
                            invoice_address=invoice_data.get('invoice_address'),
                            invoice_phone=invoice_data.get('invoice_phone'),
                            invoice_bank=invoice_data.get('invoice_bank'),
                            invoice_account=invoice_data.get('invoice_account'),
                            sort_order=invoice_data.get('sort_order', 0)
                        )
            
            # 创建归属公司
            if 'affiliated_companies' in data and data['affiliated_companies']:
                for company_data in data['affiliated_companies']:
                    if company_data.get('affiliated_company'):
                        company = self.create_with_tenant(SupplierAffiliatedCompany,
                            supplier_id=supplier.id,
                            affiliated_company=company_data.get('affiliated_company'),
                            sort_order=company_data.get('sort_order', 0)
                        )
            
            self.commit()
            return supplier.to_dict(include_details=True)
            
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
        return supplier.to_dict(include_details=True)
    
    def update_supplier(self, supplier_id, data, updated_by):
        """更新供应商"""
        try:
            supplier = self.session.query(SupplierManagement).get(uuid.UUID(supplier_id))
            if not supplier:
                return None
            
            # 更新主表字段
            update_fields = [
                'supplier_name', 'supplier_abbreviation', 'region', 
                'tax_rate', 'deposit_ratio', 'delivery_preparation_days',
                'copyright_square_price', 'supplier_level', 'organization_code',
                'company_website', 'barcode_prefix_code', 'business_start_date',
                'business_end_date', 'production_permit_start_date', 
                'production_permit_end_date', 'inspection_report_start_date',
                'inspection_report_end_date', 'barcode_authorization', 
                'ufriend_code', 'enterprise_type', 'province', 'city',
                'district', 'company_address', 'remarks', 'image_url',
                'sort_order', 'is_enabled'
            ]
            
            for field in update_fields:
                if field in data:
                    setattr(supplier, field, data[field])
            
            # 更新关联字段
            if 'supplier_category_id' in data:
                supplier.supplier_category_id = uuid.UUID(data['supplier_category_id']) if data['supplier_category_id'] and data['supplier_category_id'] != '' else None
            
            if 'purchaser_id' in data:
                supplier.purchaser_id = uuid.UUID(data['purchaser_id']) if data['purchaser_id'] and data['purchaser_id'] != '' else None
            
            if 'delivery_method_id' in data:
                supplier.delivery_method_id = uuid.UUID(data['delivery_method_id']) if data['delivery_method_id'] and data['delivery_method_id'] != '' else None
            
            if 'tax_rate_id' in data:
                supplier.tax_rate_id = uuid.UUID(data['tax_rate_id']) if data['tax_rate_id'] and data['tax_rate_id'] != '' else None
            
            if 'currency_id' in data:
                supplier.currency_id = uuid.UUID(data['currency_id']) if data['currency_id'] and data['currency_id'] != '' else None
            
            if 'payment_method_id' in data:
                supplier.payment_method_id = uuid.UUID(data['payment_method_id']) if data['payment_method_id'] and data['payment_method_id'] != '' else None
            
            if 'foreign_currency_id' in data:
                supplier.foreign_currency_id = uuid.UUID(data['foreign_currency_id']) if data['foreign_currency_id'] and data['foreign_currency_id'] != '' else None
            
            supplier.updated_by = uuid.UUID(updated_by)
            
            # 更新子表 - 简单的删除重建策略
            from app.models.basic_data import (
                SupplierContact, SupplierDeliveryAddress, 
                SupplierInvoiceUnit, SupplierAffiliatedCompany
            )
            
            # 删除现有子表数据
            self.session.query(SupplierContact).filter_by(supplier_id=supplier.id).delete()
            self.session.query(SupplierDeliveryAddress).filter_by(supplier_id=supplier.id).delete()
            self.session.query(SupplierInvoiceUnit).filter_by(supplier_id=supplier.id).delete()
            self.session.query(SupplierAffiliatedCompany).filter_by(supplier_id=supplier.id).delete()
            
            # 重新创建子表数据
            if 'contacts' in data and data['contacts']:
                for contact_data in data['contacts']:
                    if contact_data.get('contact_name'):
                        contact = self.create_with_tenant(SupplierContact,
                            supplier_id=supplier.id,
                            contact_name=contact_data.get('contact_name'),
                            landline=contact_data.get('landline'),
                            mobile=contact_data.get('mobile'),
                            fax=contact_data.get('fax'),
                            qq=contact_data.get('qq'),
                            wechat=contact_data.get('wechat'),
                            email=contact_data.get('email'),
                            department=contact_data.get('department'),
                            sort_order=contact_data.get('sort_order', 0)
                        )
            
            if 'delivery_addresses' in data and data['delivery_addresses']:
                for addr_data in data['delivery_addresses']:
                    if addr_data.get('delivery_address'):
                        addr = self.create_with_tenant(SupplierDeliveryAddress,
                            supplier_id=supplier.id,
                            delivery_address=addr_data.get('delivery_address'),
                            contact_name=addr_data.get('contact_name'),
                            contact_method=addr_data.get('contact_method'),
                            sort_order=addr_data.get('sort_order', 0)
                        )
            
            if 'invoice_units' in data and data['invoice_units']:
                for invoice_data in data['invoice_units']:
                    if invoice_data.get('invoice_unit'):
                        invoice = self.create_with_tenant(SupplierInvoiceUnit,
                            supplier_id=supplier.id,
                            invoice_unit=invoice_data.get('invoice_unit'),
                            taxpayer_id=invoice_data.get('taxpayer_id'),
                            invoice_address=invoice_data.get('invoice_address'),
                            invoice_phone=invoice_data.get('invoice_phone'),
                            invoice_bank=invoice_data.get('invoice_bank'),
                            invoice_account=invoice_data.get('invoice_account'),
                            sort_order=invoice_data.get('sort_order', 0)
                        )
            
            if 'affiliated_companies' in data and data['affiliated_companies']:
                for company_data in data['affiliated_companies']:
                    if company_data.get('affiliated_company'):
                        company = self.create_with_tenant(SupplierAffiliatedCompany,
                            supplier_id=supplier.id,
                            affiliated_company=company_data.get('affiliated_company'),
                            sort_order=company_data.get('sort_order', 0)
                        )
            
            self.commit()
            return supplier.to_dict(include_details=True)
            
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


