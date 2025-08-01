# -*- coding: utf-8 -*-
"""
Customer 服务
"""

from app.services.base_service import TenantAwareService
from app.models.basic_data import CustomerManagement
from sqlalchemy import func, and_, or_, inspect
from sqlalchemy.sql import true
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re
import logging
from decimal import Decimal
from typing import Optional

class CustomerService(TenantAwareService):
    """客户档案服务"""
    
    def __init__(self, tenant_id=None, schema_name=None):
        super().__init__(tenant_id=tenant_id, schema_name=schema_name)
        self.logger = logging.getLogger(__name__)  # 添加logger初始化
    
    def generate_code(self, entity_type):
        """生成编码"""
        prefixes = {
            'customer': 'C',
            'supplier': 'S', 
            'product': 'P'
        }
        
        prefix = prefixes.get(entity_type, 'X')
        
        # 获取当前最大编号
        if entity_type == 'customer':
            max_code = self.session.query(func.max(CustomerManagement.customer_code)).scalar()
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
    
    def get_customers(self, page=1, per_page=20, search=None, category_id=None, status=None, 
                     tenant_config=None):
        """获取客户列表"""
        try:
            from app.models.basic_data import CustomerCategoryManagement
            
            # 构建查询，使用左连接获取客户分类名称
            query = self.session.query(
                CustomerManagement,
                CustomerCategoryManagement.category_name.label('customer_category_name')
            ).outerjoin(
                CustomerCategoryManagement,
                CustomerManagement.customer_category_id == CustomerCategoryManagement.id
            )
            
            # 搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    or_(
                        CustomerManagement.customer_name.ilike(search_pattern),
                        CustomerManagement.customer_code.ilike(search_pattern)
                    )
                )
            
            # 分类筛选
            if category_id:
                try:
                    category_uuid = uuid.UUID(category_id)
                    query = query.filter(CustomerManagement.customer_category_id == category_uuid)
                except ValueError:
                    pass
            
            # 状态筛选
            if status is not None:
                query = query.filter(CustomerManagement.is_enabled == (status == 'active'))
            
            # 总数查询（只查询CustomerManagement表）
            total_query = self.session.query(CustomerManagement)
            if search:
                search_pattern = f'%{search}%'
                total_query = total_query.filter(
                    or_(
                        CustomerManagement.customer_name.ilike(search_pattern),
                        CustomerManagement.customer_code.ilike(search_pattern)
                    )
                )
            if category_id:
                try:
                    category_uuid = uuid.UUID(category_id)
                    total_query = total_query.filter(CustomerManagement.customer_category_id == category_uuid)
                except ValueError:
                    pass
            if status is not None:
                total_query = total_query.filter(CustomerManagement.is_enabled == (status == 'active'))
            
            total = total_query.count()
            
            # 排序和分页
            query = query.order_by(CustomerManagement.created_at.desc())
            results = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 转换结果
            customers = []
            for customer, category_name in results:
                customer_dict = customer.to_dict()
                # 添加客户分类名称
                customer_dict['customer_category_name'] = category_name
                customers.append(customer_dict)
            
            return {
                'customers': customers,
                'total': total,
                'current_page': page,
                'per_page': per_page
            }
            
        except Exception as e:
            print(f"获取客户列表失败: {e}")
            return {
                'customers': [],
                'total': 0,
                'current_page': page,
                'per_page': per_page
            }
    
    def get_customer(self, customer_id):
        """获取客户详情（包含子表数据）"""
        try:
            from app.models.basic_data import CustomerCategoryManagement
            
            # 获取客户基本信息和分类名称
            customer_query = self.session.query(
                CustomerManagement,
                CustomerCategoryManagement.category_name.label('customer_category_name')
            ).outerjoin(
                CustomerCategoryManagement,
                CustomerManagement.customer_category_id == CustomerCategoryManagement.id
            ).filter(CustomerManagement.id == uuid.UUID(customer_id))
            
            result = customer_query.first()
            if not result:
                raise ValueError("客户不存在")
            
            customer, customer_category_name = result
            customer_dict = customer.to_dict()
            customer_dict['customer_category_name'] = customer_category_name
            
            # 获取子表数据
            customer_dict['contacts'] = self.get_customer_contacts(customer_id)
            customer_dict['delivery_addresses'] = self.get_customer_delivery_addresses(customer_id)
            customer_dict['invoice_units'] = self.get_customer_invoice_units(customer_id)
            customer_dict['payment_units'] = self.get_customer_payment_units(customer_id)
            customer_dict['affiliated_companies'] = self.get_customer_affiliated_companies(customer_id)
            
            return customer_dict
            
        except Exception as e:
            if "客户不存在" in str(e):
                raise ValueError("客户不存在")
            raise ValueError(f"获取客户详情失败: {str(e)}")
    
    def create_customer(self, data, created_by):
        """创建客户"""
        try:
            # 生成客户编码
            if not data.get('customer_code'):
                data['customer_code'] = self.generate_code('customer')
            
            from app.models.basic_data import Currency, PackageMethod, CustomerManagement

            # -------- UUID 字段统一处理 -------- #
            uuid_fields = [
                'customer_category_id', 'tax_rate_id', 'parent_customer_id',
                'package_method_id', 'payment_method_id', 'currency_id',
                'salesperson_id'
            ]

            for field in uuid_fields:
                if field in data:
                    if data[field]:
                        try:
                            data[field] = uuid.UUID(data[field])
                        except (ValueError, TypeError):
                            data[field] = None
                    else:
                        data[field] = None

            # -------- 数值字段处理 -------- #
            numeric_fields = ['credit_amount', 'registered_capital', 'sales_commission']
            for nf in numeric_fields:
                if nf in data and data[nf] == '':
                    data[nf] = None

            # 校验/回退币别
            if data.get('currency_id'):
                exists = self.session.query(Currency.id).filter(Currency.id == data['currency_id']).first()
                if not exists:
                    base_curr = self.session.query(Currency).filter(Currency.is_base_currency == true()).first() # type: ignore
                    data['currency_id'] = base_curr.id if base_curr else None

            # 校验包装方式
            if data.get('package_method_id'):
                exists = self.session.query(PackageMethod.id).filter(PackageMethod.id == data['package_method_id']).first()
                if not exists:
                    data['package_method_id'] = None

            # -------- 过滤模型字段并准备数据 -------- #
            customer_data = {}
            for key, value in data.items():
                if hasattr(CustomerManagement, key):
                    customer_data[key] = value
            customer_data['customer_code'] = data['customer_code']
            customer_data['customer_name'] = data['customer_name']
            
            # 使用继承的create_with_tenant方法
            customer = self.create_with_tenant(CustomerManagement, **customer_data)
            self.commit()
            
            return customer.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            if 'customer_code' in str(e):
                raise ValueError("客户编码已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建客户失败: {str(e)}")
    
    def update_customer(self, customer_id, data, updated_by):
        """更新客户"""
        try:
            customer = self.session.query(CustomerManagement).get(uuid.UUID(customer_id))
            if not customer:
                raise ValueError("客户不存在")
            
            # -------- 字段安全转换 -------- #
            uuid_fields = [
                'customer_category_id', 'tax_rate_id', 'parent_customer_id',
                'package_method_id', 'payment_method_id', 'currency_id',
                'salesperson_id'
            ]
            for field in uuid_fields:
                if field in data:
                    if data[field]:
                        try:
                            # 确保输入是字符串再转UUID
                            data[field] = uuid.UUID(str(data[field]))
                        except (ValueError, TypeError):
                            data[field] = None
                    else:
                        data[field] = None

            numeric_fields = ['credit_amount', 'registered_capital', 'sales_commission', 'sort_order']
            for nf in numeric_fields:
                if nf in data and data[nf] in [None, '']:
                    data[nf] = None # 空值处理
                elif nf in data and data[nf] is not None:
                    try:
                        # 统一转为Decimal进行处理，以匹配NUMERIC/DECIMAL类型
                        if not isinstance(data[nf], Decimal):
                             data[nf] = Decimal(str(data[nf]))
                    except (ValueError, TypeError):
                        data[nf] = None # 转换失败则置空

            # -------- 过滤模型字段并赋值 -------- #
            model_columns = {c.name for c in inspect(CustomerManagement).c} # type: ignore
            
            for key, value in data.items():
                if key in model_columns and key not in ['id', 'created_at', 'created_by', 'tenant_id']:
                    setattr(customer, key, value)

            # 审计字段
            customer.updated_by = uuid.UUID(updated_by)
            customer.updated_at = datetime.utcnow()
            self.commit()
            return customer.to_dict()
            
        except Exception as e:
            self.rollback()
            self.logger.error(f"更新客户失败: {e}", exc_info=True)
            raise ValueError(f"更新客户失败: {str(e)}")
    
    def delete_customer(self, customer_id):
        """删除客户"""
        try:
            customer = self.session.query(CustomerManagement).get(uuid.UUID(customer_id))
            if not customer:
                raise ValueError("客户不存在")
            
            # 检查是否有关联数据
            # TODO: 检查是否有销售订单等关联数据
            
            self.session.delete(customer)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除客户失败: {str(e)}")
    
    def approve_customer(self, customer_id, approved_by):
        """审批客户"""
        try:
            customer = self.session.query(CustomerManagement).get(uuid.UUID(customer_id))
            if not customer:
                raise ValueError("客户不存在")
            
            # CustomerManagement使用is_enabled字段而不是status
            customer.is_enabled = True
            
            self.commit()
            return customer.to_dict()
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"审批客户失败: {str(e)}")
    
    def get_list(self, page=1, per_page=1000, enabled_only=True):
        """获取客户列表（简化版，用于选项）"""
        query = self.session.query(CustomerManagement)
        
        if enabled_only:
            query = query.filter(CustomerManagement.is_enabled == True)
        
        query = query.order_by(CustomerManagement.customer_name)
        
        # 分页
        total = query.count()
        customers = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'customers': [customer.to_dict() for customer in customers],
            'total': total,
            'page': page,
            'per_page': per_page
        }
    
    def get_customer_contacts(self, customer_id):
        """获取客户联系人"""
        try:
            from app.models.basic_data import CustomerContact
            
            contacts = self.session.query(CustomerContact).filter(
                CustomerContact.customer_id == uuid.UUID(customer_id)
            ).order_by(CustomerContact.created_at).all()
            
            return [contact.to_dict() for contact in contacts]
            
        except Exception as e:
            self.logger.error(f"获取客户联系人失败: {str(e)}")
            return []
    
    def get_customer_order_statistics(self, customer_id):
        """获取客户订单统计"""
        # TODO: 实现客户订单统计逻辑
        return {
            'total_orders': 0,
            'total_amount': 0,
            'pending_orders': 0
        }
    
    def get_form_options(self):
        """获取客户表单选项数据"""
        try:
            from app.models.basic_data import (
                CustomerCategoryManagement, TaxRate, 
                PaymentMethod, Currency, Employee, PackageMethod
            )
            
            # 获取客户分类
            customer_categories = self.session.query(CustomerCategoryManagement).filter(
                CustomerCategoryManagement.is_enabled == True
            ).order_by(CustomerCategoryManagement.category_name).all()
            
            # 获取税率
            tax_rates = self.session.query(TaxRate).filter(
                TaxRate.is_enabled == True
            ).order_by(TaxRate.tax_name).all()
            
            # 获取付款方式
            payment_methods = self.session.query(PaymentMethod).filter(
                PaymentMethod.is_enabled == True
            ).order_by(PaymentMethod.payment_name).all()
            
            # 获取币种
            currencies = self.session.query(Currency).filter(
                Currency.is_enabled == True
            ).order_by(Currency.currency_name).all()
            
            # 获取员工（业务员）
            employees = self.session.query(Employee).filter(
                Employee.is_enabled == True
            ).order_by(Employee.employee_name).all()
            
            # 获取现有客户（用于上级客户选择）
            customers = self.session.query(CustomerManagement).filter(
                CustomerManagement.is_enabled == True
            ).order_by(CustomerManagement.customer_name).all()
            
            # 获取包装方式
            package_methods = self.session.query(PackageMethod).filter(
                PackageMethod.is_enabled == True
            ).order_by(PackageMethod.package_name).all()
            
            return {
                'customer_categories': [
                    {'value': str(cat.id), 'label': cat.category_name}
                    for cat in customer_categories
                ],
                'tax_rates': [
                    {
                        'value': str(tax.id), 
                        'label': f'{tax.tax_name}',
                        'rate': float(tax.tax_rate) if tax.tax_rate else 0
                    }
                    for tax in tax_rates
                ],
                'payment_methods': [
                    {'value': str(pm.id), 'label': pm.payment_name}
                    for pm in payment_methods
                ],
                'package_methods': [
                    {'value': str(pkg.id), 'label': pkg.package_name}
                    for pkg in package_methods
                ],
                'currencies': [
                    {
                        'value': str(curr.id),
                        'label': f'{curr.currency_name} ({curr.currency_code})',
                        'is_base': curr.is_base_currency
                    }
                    for curr in currencies
                ],
                'base_currency_id': str(next((c.id for c in currencies if c.is_base_currency), currencies[0].id)) if currencies else None,
                'employees': [
                    {'value': str(emp.id), 'label': emp.employee_name}
                    for emp in employees
                ],
                'customers': [
                    {'value': str(cust.id), 'label': cust.customer_name}
                    for cust in customers
                ],
                'business_types': [
                    {'value': 'manufacturing', 'label': '制造业'},
                    {'value': 'trading', 'label': '贸易'},
                    {'value': 'service', 'label': '服务业'},
                    {'value': 'other', 'label': '其他'}
                ],
                'enterprise_types': [
                    {'value': code, 'label': name}
                    for code, name in CustomerManagement.ENTERPRISE_TYPES
                ],
            }
            
        except Exception as e:
            raise ValueError(f"获取表单选项失败: {str(e)}")
    
    def get_customer_delivery_addresses(self, customer_id):
        """获取客户收货地址"""
        try:
            from app.models.basic_data import CustomerDeliveryAddress
            
            addresses = self.session.query(CustomerDeliveryAddress).filter(
                CustomerDeliveryAddress.customer_id == uuid.UUID(customer_id)
            ).order_by(CustomerDeliveryAddress.sort_order).all()
            
            return [addr.to_dict() for addr in addresses]
            
        except Exception as e:
            self.logger.error(f"获取客户收货地址失败: {str(e)}")
            return []
    
    def get_customer_invoice_units(self, customer_id):
        """获取客户开票单位"""
        try:
            from app.models.basic_data import CustomerInvoiceUnit
            
            invoice_units = self.session.query(CustomerInvoiceUnit).filter(
                CustomerInvoiceUnit.customer_id == uuid.UUID(customer_id)
            ).order_by(CustomerInvoiceUnit.sort_order).all()
            
            return [unit.to_dict() for unit in invoice_units]
            
        except Exception as e:
            self.logger.error(f"获取客户开票单位失败: {str(e)}")
            return []
    
    def get_customer_payment_units(self, customer_id):
        """获取客户付款单位"""
        try:
            from app.models.basic_data import CustomerPaymentUnit
            
            payment_units = self.session.query(CustomerPaymentUnit).filter(
                CustomerPaymentUnit.customer_id == uuid.UUID(customer_id)
            ).order_by(CustomerPaymentUnit.sort_order).all()
            
            return [unit.to_dict() for unit in payment_units]
            
        except Exception as e:
            self.logger.error(f"获取客户付款单位失败: {str(e)}")
            return []
    
    def get_customer_affiliated_companies(self, customer_id):
        """获取客户归属公司"""
        try:
            from app.models.basic_data import CustomerAffiliatedCompany
            
            companies = self.session.query(CustomerAffiliatedCompany).filter(
                CustomerAffiliatedCompany.customer_id == uuid.UUID(customer_id)
            ).order_by(CustomerAffiliatedCompany.sort_order).all()
            
            return [company.to_dict() for company in companies]
            
        except Exception as e:
            self.logger.error(f"获取客户归属公司失败: {str(e)}")
            return []

    def save_customer_contacts(self, customer_id, contacts_data):
        """保存客户联系人"""
        try:
            from app.models.basic_data import CustomerContact
            
            # 删除现有联系人
            self.session.query(CustomerContact).filter(
                CustomerContact.customer_id == uuid.UUID(customer_id)
            ).delete()
            
            # 创建新联系人
            for contact_data in contacts_data:
                contact = CustomerContact(
                    customer_id=uuid.UUID(customer_id),
                    contact_name=contact_data.get('contact_name'),
                    position=contact_data.get('position'),
                    mobile=contact_data.get('mobile'),
                    fax=contact_data.get('fax'),
                    qq=contact_data.get('qq'),
                    wechat=contact_data.get('wechat'),
                    email=contact_data.get('email'),
                    department=contact_data.get('department'),
                    sort_order=contact_data.get('sort_order', 0)
                )
                self.session.add(contact)
            
            self.session.flush()
            return True
            
        except Exception as e:
            self.logger.error(f"保存客户联系人失败: {str(e)}")
            raise ValueError(f"保存客户联系人失败: {str(e)}")

    def save_customer_delivery_addresses(self, customer_id, addresses_data):
        """保存客户送货地址"""
        try:
            from app.models.basic_data import CustomerDeliveryAddress
            
            # 删除现有地址
            self.session.query(CustomerDeliveryAddress).filter(
                CustomerDeliveryAddress.customer_id == uuid.UUID(customer_id)
            ).delete()
            
            # 创建新地址
            for address_data in addresses_data:
                address = CustomerDeliveryAddress(
                    customer_id=uuid.UUID(customer_id),
                    delivery_address=address_data.get('delivery_address'),
                    contact_name=address_data.get('contact_name'),
                    contact_method=address_data.get('contact_method'),
                    sort_order=address_data.get('sort_order', 0)
                )
                self.session.add(address)
            
            self.session.flush()
            return True
            
        except Exception as e:
            self.logger.error(f"保存客户送货地址失败: {str(e)}")
            raise ValueError(f"保存客户送货地址失败: {str(e)}")

    def save_customer_invoice_units(self, customer_id, invoice_units_data):
        """保存客户开票单位"""
        try:
            from app.models.basic_data import CustomerInvoiceUnit
            
            # 删除现有开票单位
            self.session.query(CustomerInvoiceUnit).filter(
                CustomerInvoiceUnit.customer_id == uuid.UUID(customer_id)
            ).delete()
            
            # 创建新开票单位
            for unit_data in invoice_units_data:
                unit = CustomerInvoiceUnit(
                    customer_id=uuid.UUID(customer_id),
                    invoice_unit=unit_data.get('invoice_unit'),
                    taxpayer_id=unit_data.get('taxpayer_id'),
                    invoice_address=unit_data.get('invoice_address'),
                    invoice_phone=unit_data.get('invoice_phone'),
                    invoice_bank=unit_data.get('invoice_bank'),
                    invoice_account=unit_data.get('invoice_account'),
                    sort_order=unit_data.get('sort_order', 0)
                )
                self.session.add(unit)
            
            self.session.flush()
            return True
            
        except Exception as e:
            self.logger.error(f"保存客户开票单位失败: {str(e)}")
            raise ValueError(f"保存客户开票单位失败: {str(e)}")

    def save_customer_payment_units(self, customer_id, payment_units_data):
        """保存客户付款单位"""
        try:
            from app.models.basic_data import CustomerPaymentUnit
            
            # 删除现有付款单位
            self.session.query(CustomerPaymentUnit).filter(
                CustomerPaymentUnit.customer_id == uuid.UUID(customer_id)
            ).delete()
            
            # 创建新付款单位
            for unit_data in payment_units_data:
                unit = CustomerPaymentUnit(
                    customer_id=uuid.UUID(customer_id),
                    payment_unit=unit_data.get('payment_unit') or '',
                    unit_code=unit_data.get('unit_code') or '',
                    sort_order=unit_data.get('sort_order', 0)
                )
                self.session.add(unit)
            
            self.session.flush()
            return True
            
        except Exception as e:
            self.logger.error(f"保存客户付款单位失败: {str(e)}")
            raise ValueError(f"保存客户付款单位失败: {str(e)}")

    def save_customer_affiliated_companies(self, customer_id, companies_data):
        """保存客户归属公司"""
        try:
            from app.models.basic_data import CustomerAffiliatedCompany
            
            # 删除现有归属公司
            self.session.query(CustomerAffiliatedCompany).filter(
                CustomerAffiliatedCompany.customer_id == uuid.UUID(customer_id)
            ).delete()
            
            # 创建新归属公司
            for company_data in companies_data:
                company = CustomerAffiliatedCompany(
                    customer_id=uuid.UUID(customer_id),
                    affiliated_company=company_data.get('affiliated_company'),
                    sort_order=company_data.get('sort_order', 0)
                )
                self.session.add(company)
            
            self.session.flush()
            return True
            
        except Exception as e:
            self.logger.error(f"保存客户归属公司失败: {str(e)}")
            raise ValueError(f"保存客户归属公司失败: {str(e)}")

    def update_customer_with_subtables(self, customer_id, data, updated_by):
        """更新客户及其子表数据"""
        try:
            # 拆分主表与子表数据，避免将列表/字典直接赋给关系属性
            subtable_keys = ['contacts', 'delivery_addresses', 'invoice_units', 'payment_units', 'affiliated_companies']
            main_data = {k: v for k, v in data.items() if k not in subtable_keys}

            # 更新主表
            customer = self.update_customer(customer_id, main_data, updated_by)
            
            # 更新子表数据
            if 'contacts' in data:
                self.save_customer_contacts(customer_id, data['contacts'])
            
            if 'delivery_addresses' in data:
                self.save_customer_delivery_addresses(customer_id, data['delivery_addresses'])
            
            if 'invoice_units' in data:
                self.save_customer_invoice_units(customer_id, data['invoice_units'])
            
            if 'payment_units' in data:
                self.save_customer_payment_units(customer_id, data['payment_units'])
            
            if 'affiliated_companies' in data:
                self.save_customer_affiliated_companies(customer_id, data['affiliated_companies'])
            
            self.commit()
            return customer
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新客户及子表失败: {str(e)}")

    def create_customer_with_subtables(self, data, created_by):
        """创建客户及其子表数据"""
        try:
            # 创建主表
            customer_data = {k: v for k, v in data.items() 
                           if k not in ['contacts', 'delivery_addresses', 'invoice_units', 'payment_units', 'affiliated_companies']}
            customer = self.create_customer(customer_data, created_by)
            customer_id = customer['id']
            
            # 创建子表数据
            if 'contacts' in data:
                self.save_customer_contacts(customer_id, data['contacts'])
            
            if 'delivery_addresses' in data:
                self.save_customer_delivery_addresses(customer_id, data['delivery_addresses'])
            
            if 'invoice_units' in data:
                self.save_customer_invoice_units(customer_id, data['invoice_units'])
            
            if 'payment_units' in data:
                self.save_customer_payment_units(customer_id, data['payment_units'])
            
            if 'affiliated_companies' in data:
                self.save_customer_affiliated_companies(customer_id, data['affiliated_companies'])
            
            self.commit()
            return customer
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建客户及子表失败: {str(e)}")


def get_customer_service(tenant_id: Optional[str] = None, schema_name: Optional[str] = None) -> CustomerService:
    """获取客户服务实例"""
    return CustomerService(tenant_id=tenant_id, schema_name=schema_name)


