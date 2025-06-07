# -*- coding: utf-8 -*-
"""
客户管理服务
"""

from app.models.basic_data import (
    CustomerManagement, CustomerContact, CustomerDeliveryAddress,
    CustomerInvoiceUnit, CustomerPaymentUnit, CustomerAffiliatedCompany,
    CustomerCategoryManagement, PackageMethod
)
from app.models.user import User
from app.extensions import db
from sqlalchemy import and_, or_, text
from flask import g, current_app
import uuid
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime
import json


class CustomerService:
    """客户管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in CustomerService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_list(page=1, per_page=20, search=None, customer_category_id=None, customer_level=None, 
                 business_type=None, enterprise_type=None, region=None, enabled_only=False):
        """获取客户列表"""
        # 设置schema
        CustomerService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            cm.id, cm.customer_code, cm.customer_name, cm.customer_category_id, cm.customer_abbreviation,
            cm.customer_level, cm.parent_customer_id, cm.region, cm.package_method_id,
            cm.barcode_prefix, cm.business_type, cm.enterprise_type, cm.company_address,
            cm.contract_start_date, cm.contract_end_date, cm.business_start_date, cm.business_end_date,
            cm.trademark_start_date, cm.trademark_end_date, cm.barcode_cert_start_date, cm.barcode_cert_end_date,
            cm.production_permit_start_date, cm.production_permit_end_date, cm.inspection_report_start_date, cm.inspection_report_end_date,
            cm.payment_method_id, cm.currency_id, cm.settlement_color_difference, cm.sales_commission,
            cm.credit_amount, cm.registered_capital, cm.accounts_period, cm.account_period,
            cm.salesperson_id, cm.barcode_front_code, cm.barcode_back_code, cm.user_barcode,
            cm.invoice_water_number, cm.water_mark_position, cm.legal_person_certificate,
            cm.company_website, cm.company_legal_person, cm.province, cm.city, cm.district,
            cm.organization_code, cm.reconciliation_date, cm.foreign_currency, cm.remarks,
            cm.trademark_certificate, cm.print_authorization, cm.inspection_report, cm.free_samples,
            cm.advance_payment_control, cm.warehouse, cm.old_customer, cm.customer_archive_review,
            cm.sort_order, cm.is_enabled, cm.created_by, cm.updated_by, cm.created_at, cm.updated_at,
            ccm.category_name as customer_category_name,
            pm.package_name as package_method_name,
            parent_cm.customer_name as parent_customer_name
        FROM {schema_name}.customer_management cm
        LEFT JOIN {schema_name}.customer_category_management ccm ON cm.customer_category_id = ccm.id
        LEFT JOIN {schema_name}.package_methods pm ON cm.package_method_id = pm.id
        LEFT JOIN {schema_name}.customer_management parent_cm ON cm.parent_customer_id = parent_cm.id
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (cm.customer_name ILIKE :search OR 
                 cm.customer_code ILIKE :search OR 
                 cm.customer_abbreviation ILIKE :search OR
                 cm.region ILIKE :search OR
                 cm.barcode_prefix ILIKE :search OR
                 cm.company_address ILIKE :search OR
                 cm.organization_code ILIKE :search)
            """)
            params['search'] = f'%{search}%'
        
        if customer_category_id:
            where_conditions.append("cm.customer_category_id = :customer_category_id")
            params['customer_category_id'] = customer_category_id
        
        if customer_level:
            where_conditions.append("cm.customer_level = :customer_level")
            params['customer_level'] = customer_level
        
        if business_type:
            where_conditions.append("cm.business_type = :business_type")
            params['business_type'] = business_type
        
        if enterprise_type:
            where_conditions.append("cm.enterprise_type = :enterprise_type")
            params['enterprise_type'] = enterprise_type
        
        if region:
            where_conditions.append("cm.region = :region")
            params['region'] = region
        
        if enabled_only:
            where_conditions.append("cm.is_enabled = true")
        
        # 构建完整查询
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        base_query += " ORDER BY cm.created_at DESC"
        
        # 计算总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM {schema_name}.customer_management cm
        """
        if where_conditions:
            count_query += " WHERE " + " AND ".join(where_conditions)
        
        # 执行查询
        try:
            # 获取总数
            count_result = db.session.execute(text(count_query), params)
            total = count_result.scalar()
            
            # 计算分页
            offset = (page - 1) * per_page
            params['limit'] = per_page
            params['offset'] = offset
            
            # 添加分页
            paginated_query = base_query + " LIMIT :limit OFFSET :offset"
            
            # 执行分页查询
            result = db.session.execute(text(paginated_query), params)
            rows = result.fetchall()
            
            customers = []
            for row in rows:
                customer_data = {
                    'id': str(row.id),
                    'customer_code': row.customer_code,
                    'customer_name': row.customer_name,
                    'customer_category_id': str(row.customer_category_id) if row.customer_category_id else None,
                    'customer_category_name': row.customer_category_name,
                    'customer_abbreviation': row.customer_abbreviation,
                    'customer_level': row.customer_level,
                    'parent_customer_id': str(row.parent_customer_id) if row.parent_customer_id else None,
                    'parent_customer_name': row.parent_customer_name,
                    'region': row.region,
                    'package_method_id': str(row.package_method_id) if row.package_method_id else None,
                    'package_method_name': row.package_method_name,
                    'barcode_prefix': row.barcode_prefix,
                    'business_type': row.business_type,
                    'enterprise_type': row.enterprise_type,
                    'company_address': row.company_address,
                    'contract_start_date': row.contract_start_date.isoformat() if row.contract_start_date else None,
                    'contract_end_date': row.contract_end_date.isoformat() if row.contract_end_date else None,
                    'business_start_date': row.business_start_date.isoformat() if row.business_start_date else None,
                    'business_end_date': row.business_end_date.isoformat() if row.business_end_date else None,
                    'trademark_start_date': row.trademark_start_date.isoformat() if row.trademark_start_date else None,
                    'trademark_end_date': row.trademark_end_date.isoformat() if row.trademark_end_date else None,
                    'barcode_cert_start_date': row.barcode_cert_start_date.isoformat() if row.barcode_cert_start_date else None,
                    'barcode_cert_end_date': row.barcode_cert_end_date.isoformat() if row.barcode_cert_end_date else None,
                    'production_permit_start_date': row.production_permit_start_date.isoformat() if row.production_permit_start_date else None,
                    'production_permit_end_date': row.production_permit_end_date.isoformat() if row.production_permit_end_date else None,
                    'inspection_report_start_date': row.inspection_report_start_date.isoformat() if row.inspection_report_start_date else None,
                    'inspection_report_end_date': row.inspection_report_end_date.isoformat() if row.inspection_report_end_date else None,
                    'payment_method_id': str(row.payment_method_id) if row.payment_method_id else None,
                    'currency_id': str(row.currency_id) if row.currency_id else None,
                    'settlement_color_difference': float(row.settlement_color_difference) if row.settlement_color_difference else None,
                    'sales_commission': float(row.sales_commission) if row.sales_commission else None,
                    'credit_amount': float(row.credit_amount) if row.credit_amount else None,
                    'registered_capital': float(row.registered_capital) if row.registered_capital else None,
                    'accounts_period': row.accounts_period,
                    'account_period': row.account_period,
                    'salesperson_id': str(row.salesperson_id) if row.salesperson_id else None,
                    'barcode_front_code': row.barcode_front_code,
                    'barcode_back_code': row.barcode_back_code,
                    'user_barcode': row.user_barcode,
                    'invoice_water_number': row.invoice_water_number,
                    'water_mark_position': float(row.water_mark_position) if row.water_mark_position else None,
                    'legal_person_certificate': row.legal_person_certificate,
                    'company_website': row.company_website,
                    'company_legal_person': row.company_legal_person,
                    'province': row.province,
                    'city': row.city,
                    'district': row.district,
                    'organization_code': row.organization_code,
                    'reconciliation_date': row.reconciliation_date.isoformat() if row.reconciliation_date else None,
                    'foreign_currency': row.foreign_currency,
                    'remarks': row.remarks,
                    'trademark_certificate': row.trademark_certificate,
                    'print_authorization': row.print_authorization,
                    'inspection_report': row.inspection_report,
                    'free_samples': row.free_samples,
                    'advance_payment_control': row.advance_payment_control,
                    'warehouse': row.warehouse,
                    'old_customer': row.old_customer,
                    'customer_archive_review': row.customer_archive_review,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
                
                # 获取创建人和修改人用户名
                if row.created_by:
                    created_user = User.query.get(row.created_by)
                    if created_user:
                        customer_data['created_by_name'] = created_user.get_full_name()
                    else:
                        customer_data['created_by_name'] = '未知用户'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        customer_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        customer_data['updated_by_name'] = '未知用户'
                
                customers.append(customer_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'customers': customers,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying customers: {str(e)}")
            raise ValueError(f'查询客户失败: {str(e)}')

    @staticmethod
    def get_by_id(customer_id):
        """获取客户详细信息"""
        # 设置schema
        CustomerService._set_schema()
        
        try:
            customer_uuid = uuid.UUID(customer_id)
        except ValueError:
            raise ValueError('无效的客户ID')
        
        customer = CustomerManagement.query.get(customer_uuid)
        if not customer:
            raise ValueError('客户不存在')
        
        customer_data = customer.to_dict()
        
        # 获取子表数据
        customer_data['contacts'] = [contact.to_dict() for contact in customer.contacts]
        customer_data['delivery_addresses'] = [addr.to_dict() for addr in customer.delivery_addresses]
        customer_data['invoice_units'] = [unit.to_dict() for unit in customer.invoice_units]
        customer_data['payment_units'] = [unit.to_dict() for unit in customer.payment_units]
        customer_data['affiliated_companies'] = [company.to_dict() for company in customer.affiliated_companies]
        
        # 获取关联信息名称 - 使用查询而不是关系，因为关系在模型中被注释了
        if customer.customer_category_id:
            from app.models.basic_data import CustomerCategoryManagement
            category = CustomerCategoryManagement.query.get(customer.customer_category_id)
            if category:
                customer_data['customer_category_name'] = category.category_name
        
        if customer.package_method_id:
            # 暂时不处理package_method
            pass
        
        if customer.parent_customer_id:
            parent = CustomerManagement.query.get(customer.parent_customer_id)
            if parent:
                customer_data['parent_customer_name'] = parent.customer_name
        
        # 获取创建人和修改人用户名
        if customer.created_by:
            created_user = User.query.get(customer.created_by)
            if created_user:
                customer_data['created_by_name'] = created_user.get_full_name()
        
        if customer.updated_by:
            updated_user = User.query.get(customer.updated_by)
            if updated_user:
                customer_data['updated_by_name'] = updated_user.get_full_name()
        
        return customer_data

    @staticmethod
    def generate_customer_code():
        """生成客户编号：CUS000001 格式"""
        CustomerService._set_schema()
        
        # 查询当前最大编号
        max_code_query = text("""
            SELECT customer_code 
            FROM mytenant.customer_management 
            WHERE customer_code ~ '^CUS[0-9]{6}$' 
            ORDER BY customer_code DESC 
            LIMIT 1
        """)
        
        result = db.session.execute(max_code_query).fetchone()
        
        if result and result[0]:
            # 提取数字部分并加1
            current_num = int(result[0][3:])  # 去掉CUS前缀
            new_num = current_num + 1
        else:
            new_num = 1
        
        return f"CUS{new_num:06d}"

    @staticmethod
    def create(data, created_by):
        """创建客户"""
        # 设置schema
        CustomerService._set_schema()
        
        # 验证数据
        if not data.get('customer_name'):
            raise ValueError('客户名称不能为空')
        
        # 检查客户名称是否重复
        existing = CustomerManagement.query.filter_by(
            customer_name=data['customer_name']
        ).first()
        if existing:
            raise ValueError('客户名称已存在')
        
        try:
            # 创建主记录
            customer = CustomerManagement()
            
            # 自动生成客户编号
            customer.customer_code = CustomerService.generate_customer_code()
            
            # 基本信息
            customer.customer_name = data['customer_name']
            customer.customer_abbreviation = data.get('customer_abbreviation')
            customer.customer_level = data.get('customer_level')
            customer.region = data.get('region')
            customer.barcode_prefix = data.get('barcode_prefix')
            customer.business_type = data.get('business_type')
            customer.enterprise_type = data.get('enterprise_type')
            customer.company_address = data.get('company_address')
            
            # 外键字段 - 只在有值时设置
            if data.get('customer_category_id'):
                customer.customer_category_id = data.get('customer_category_id')
            if data.get('tax_rate_id'):
                customer.tax_rate_id = data.get('tax_rate_id')
            if data.get('tax_rate'):
                customer.tax_rate = data.get('tax_rate')
            if data.get('parent_customer_id'):
                customer.parent_customer_id = data.get('parent_customer_id')
            if data.get('package_method_id'):
                customer.package_method_id = data.get('package_method_id')
            if data.get('payment_method_id'):
                customer.payment_method_id = data.get('payment_method_id')
            if data.get('currency_id'):
                customer.currency_id = data.get('currency_id')
            customer.settlement_color_difference = data.get('settlement_color_difference')
            customer.sales_commission = data.get('sales_commission')
            customer.credit_amount = data.get('credit_amount')
            customer.registered_capital = data.get('registered_capital')
            customer.accounts_period = data.get('accounts_period')
            customer.account_period = data.get('account_period')
            customer.salesperson_id = data.get('salesperson_id')
            customer.barcode_front_code = data.get('barcode_front_code')
            customer.barcode_back_code = data.get('barcode_back_code')
            customer.user_barcode = data.get('user_barcode')
            customer.invoice_water_number = data.get('invoice_water_number')
            customer.water_mark_position = data.get('water_mark_position')
            customer.legal_person_certificate = data.get('legal_person_certificate')
            customer.company_website = data.get('company_website')
            customer.company_legal_person = data.get('company_legal_person')
            customer.province = data.get('province')
            customer.city = data.get('city')
            customer.district = data.get('district')
            customer.organization_code = data.get('organization_code')
            customer.foreign_currency = data.get('foreign_currency')
            customer.remarks = data.get('remarks')
            customer.trademark_certificate = data.get('trademark_certificate', False)
            customer.print_authorization = data.get('print_authorization', False)
            customer.inspection_report = data.get('inspection_report', False)
            customer.free_samples = data.get('free_samples', False)
            customer.advance_payment_control = data.get('advance_payment_control', False)
            customer.warehouse = data.get('warehouse', False)
            customer.old_customer = data.get('old_customer', False)
            customer.customer_archive_review = data.get('customer_archive_review', False)
            customer.sort_order = data.get('sort_order', 0)
            
            # 日期字段
            if data.get('trademark_start_date'):
                customer.trademark_start_date = datetime.strptime(
                    data['trademark_start_date'], '%Y-%m-%d').date()
            if data.get('trademark_end_date'):
                customer.trademark_end_date = datetime.strptime(
                    data['trademark_end_date'], '%Y-%m-%d').date()
            if data.get('barcode_cert_start_date'):
                customer.barcode_cert_start_date = datetime.strptime(
                    data['barcode_cert_start_date'], '%Y-%m-%d').date()
            if data.get('barcode_cert_end_date'):
                customer.barcode_cert_end_date = datetime.strptime(
                    data['barcode_cert_end_date'], '%Y-%m-%d').date()
            if data.get('contract_start_date'):
                customer.contract_start_date = datetime.strptime(
                    data['contract_start_date'], '%Y-%m-%d').date()
            if data.get('contract_end_date'):
                customer.contract_end_date = datetime.strptime(
                    data['contract_end_date'], '%Y-%m-%d').date()
            if data.get('business_start_date'):
                customer.business_start_date = datetime.strptime(
                    data['business_start_date'], '%Y-%m-%d').date()
            if data.get('business_end_date'):
                customer.business_end_date = datetime.strptime(
                    data['business_end_date'], '%Y-%m-%d').date()
            if data.get('production_permit_start_date'):
                customer.production_permit_start_date = datetime.strptime(
                    data['production_permit_start_date'], '%Y-%m-%d').date()
            if data.get('production_permit_end_date'):
                customer.production_permit_end_date = datetime.strptime(
                    data['production_permit_end_date'], '%Y-%m-%d').date()
            if data.get('inspection_report_start_date'):
                customer.inspection_report_start_date = datetime.strptime(
                    data['inspection_report_start_date'], '%Y-%m-%d').date()
            if data.get('inspection_report_end_date'):
                customer.inspection_report_end_date = datetime.strptime(
                    data['inspection_report_end_date'], '%Y-%m-%d').date()
            if data.get('reconciliation_date'):
                customer.reconciliation_date = datetime.strptime(
                    data['reconciliation_date'], '%Y-%m-%d').date()
            
            customer.is_enabled = data.get('is_enabled', True)
            customer.created_by = created_by
            customer.created_at = datetime.now()
            
            db.session.add(customer)
            db.session.flush()  # 获取ID
            
            # 处理子表数据
            CustomerService._save_sub_tables(customer, data)
            
            db.session.commit()
            return customer.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating customer: {str(e)}")
            raise ValueError(f'创建客户失败: {str(e)}')

    @staticmethod
    def update(customer_id, data, updated_by):
        """更新客户"""
        # 设置schema
        CustomerService._set_schema()
        
        try:
            customer_uuid = uuid.UUID(customer_id)
        except ValueError:
            raise ValueError('无效的客户ID')
        
        customer = CustomerManagement.query.get(customer_uuid)
        if not customer:
            raise ValueError('客户不存在')
        
        # 检查客户名称是否重复（排除自己）
        if data.get('customer_name') and data['customer_name'] != customer.customer_name:
            existing = CustomerManagement.query.filter_by(
                customer_name=data['customer_name']
            ).first()
            if existing:
                raise ValueError('客户名称已存在')
        
        try:
            # 更新基本信息
            if 'customer_name' in data:
                customer.customer_name = data['customer_name']
            if 'customer_category_id' in data:
                customer.customer_category_id = data['customer_category_id']
            if 'phone' in data:
                customer.phone = data['phone']
            if 'tax_number' in data:
                customer.tax_number = data['tax_number']
            if 'customer_level' in data:
                customer.customer_level = data['customer_level']
            if 'parent_customer_id' in data:
                customer.parent_customer_id = data['parent_customer_id']
            if 'region' in data:
                customer.region = data['region']
            if 'package_method_id' in data:
                customer.package_method_id = data['package_method_id']
            if 'barcode_prefix' in data:
                customer.barcode_prefix = data['barcode_prefix']
            if 'business_type' in data:
                customer.business_type = data['business_type']
            if 'enterprise_type' in data:
                customer.enterprise_type = data['enterprise_type']
            if 'company_category' in data:
                customer.company_category = data['company_category']
            
            # 更新日期字段
            if 'business_license_start_date' in data:
                customer.business_license_start_date = datetime.strptime(
                    data['business_license_start_date'], '%Y-%m-%d').date() if data['business_license_start_date'] else None
            if 'business_license_end_date' in data:
                customer.business_license_end_date = datetime.strptime(
                    data['business_license_end_date'], '%Y-%m-%d').date() if data['business_license_end_date'] else None
            if 'contract_start_date' in data:
                customer.contract_start_date = datetime.strptime(
                    data['contract_start_date'], '%Y-%m-%d').date() if data['contract_start_date'] else None
            if 'contract_end_date' in data:
                customer.contract_end_date = datetime.strptime(
                    data['contract_end_date'], '%Y-%m-%d').date() if data['contract_end_date'] else None
            if 'permit_start_date' in data:
                customer.permit_start_date = datetime.strptime(
                    data['permit_start_date'], '%Y-%m-%d').date() if data['permit_start_date'] else None
            if 'permit_end_date' in data:
                customer.permit_end_date = datetime.strptime(
                    data['permit_end_date'], '%Y-%m-%d').date() if data['permit_end_date'] else None
            
            if 'is_enabled' in data:
                customer.is_enabled = data['is_enabled']
            
            customer.updated_by = updated_by
            customer.updated_at = datetime.now()
            
            # 更新子表数据
            CustomerService._save_sub_tables(customer, data)
            
            db.session.commit()
            return customer.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating customer: {str(e)}")
            raise ValueError(f'更新客户失败: {str(e)}')

    @staticmethod
    def delete(customer_id):
        """删除客户"""
        # 设置schema
        CustomerService._set_schema()
        
        try:
            customer_uuid = uuid.UUID(customer_id)
        except ValueError:
            raise ValueError('无效的客户ID')
        
        customer = CustomerManagement.query.get(customer_uuid)
        if not customer:
            raise ValueError('客户不存在')
        
        try:
            # 删除子表数据（数据库外键约束会自动处理级联删除）
            # 由于我们设置了CASCADE，直接删除主记录即可
            db.session.delete(customer)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting customer: {str(e)}")
            raise ValueError(f'删除客户失败: {str(e)}')

    @staticmethod
    def toggle_status(customer_id):
        """切换客户状态"""
        # 设置schema
        CustomerService._set_schema()
        
        try:
            customer_uuid = uuid.UUID(customer_id)
        except ValueError:
            raise ValueError('无效的客户ID')
        
        customer = CustomerManagement.query.get(customer_uuid)
        if not customer:
            raise ValueError('客户不存在')
        
        try:
            customer.is_enabled = not customer.is_enabled
            customer.updated_at = datetime.now()
            db.session.commit()
            
            return {
                'id': str(customer.id),
                'is_enabled': customer.is_enabled,
                'customer_name': customer.customer_name
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error toggling customer status: {str(e)}")
            raise ValueError(f'切换客户状态失败: {str(e)}')

    @staticmethod
    def export_data(filters=None):
        """导出客户数据"""
        # 设置schema
        CustomerService._set_schema()
        
        try:
            # 获取所有数据（不分页）
            result = CustomerService.get_list(
                page=1, per_page=10000, 
                search=filters.get('search') if filters else None,
                customer_category_id=filters.get('customer_category_id') if filters else None,
                customer_level=filters.get('customer_level') if filters else None,
                business_type=filters.get('business_type') if filters else None,
                enterprise_type=filters.get('enterprise_type') if filters else None,
                region=filters.get('region') if filters else None
            )
            
            # 准备导出数据（简化版，返回JSON格式）
            export_data = []
            for customer in result['customers']:
                export_data.append({
                    '客户名称': customer['customer_name'],
                    '客户分类': customer['customer_category_name'] or '',
                    '电话': customer['phone'] or '',
                    '税号': customer['tax_number'] or '',
                    '客户等级': customer['customer_level'] or '',
                    '上级客户': customer['parent_customer_name'] or '',
                    '区域': customer['region'] or '',
                    '包装方式': customer['package_method_name'] or '',
                    '条码前缀': customer['barcode_prefix'] or '',
                    '经营业务类': customer['business_type'] or '',
                    '企业类型': customer['enterprise_type'] or '',
                    '公司类别': customer['company_category'] or '',
                    '营业执照起始日期': customer['business_license_start_date'] or '',
                    '营业执照结束日期': customer['business_license_end_date'] or '',
                    '合同起始日期': customer['contract_start_date'] or '',
                    '合同结束日期': customer['contract_end_date'] or '',
                    '许可证起始日期': customer['permit_start_date'] or '',
                    '许可证结束日期': customer['permit_end_date'] or '',
                    '状态': '启用' if customer['is_enabled'] else '禁用',
                    '创建人': customer['created_by_name'] or '',
                    '创建时间': customer['created_at'] or '',
                    '修改人': customer['updated_by_name'] or '',
                    '修改时间': customer['updated_at'] or ''
                })
            
            # 返回JSON格式数据供前端处理
            return json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')
            
        except Exception as e:
            current_app.logger.error(f"Error exporting customers: {str(e)}")
            raise ValueError(f'导出客户数据失败: {str(e)}')

    @staticmethod
    def get_form_options():
        """获取表单选项"""
        # 设置schema
        CustomerService._set_schema()
        
        try:
            # 客户分类选项
            customer_categories = CustomerCategoryManagement.query.filter_by(is_enabled=True).all()
            customer_category_options = [
                {'value': str(cat.id), 'label': cat.category_name}
                for cat in customer_categories
            ]
            
            # 包装方式选项
            package_methods = PackageMethod.query.filter_by(is_enabled=True).all()
            package_method_options = [
                {'value': str(pm.id), 'label': pm.package_name}
                for pm in package_methods
            ]
            
            # 上级客户选项
            parent_customers = CustomerManagement.query.filter_by(is_enabled=True).all()
            parent_customer_options = [
                {'value': str(pc.id), 'label': pc.customer_name}
                for pc in parent_customers
            ]
            
            return {
                'customer_categories': customer_category_options,
                'package_methods': package_method_options,
                'parent_customers': parent_customer_options,
                'business_types': CustomerService.get_business_type_options(),
                'enterprise_types': CustomerService.get_enterprise_type_options()
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting form options: {str(e)}")
            raise ValueError(f'获取表单选项失败: {str(e)}')

    @staticmethod
    def get_business_type_options():
        """获取经营业务类选项"""
        return [
            {'value': '', 'label': '无'},
            {'value': '供应商', 'label': '供应商'},
            {'value': '经销', 'label': '经销'},
            {'value': '代理', 'label': '代理'},
            {'value': '贸易', 'label': '贸易'},
            {'value': '备案', 'label': '备案'},
            {'value': '直销配送', 'label': '直销配送'}
        ]

    @staticmethod
    def get_enterprise_type_options():
        """获取企业类型选项"""
        return [
            {'value': '', 'label': '无'},
            {'value': '个人', 'label': '个人'},
            {'value': '个体工商户', 'label': '个体工商户'},
            {'value': '有限责任公司', 'label': '有限责任公司'}
        ]

    @staticmethod
    def _save_sub_tables(customer, data):
        """保存子表数据"""
        # 保存联系人子表
        if 'contacts' in data:
            # 删除现有联系人
            CustomerContact.query.filter_by(customer_id=customer.id).delete()
            
            for contact_data in data['contacts']:
                if not any(contact_data.values()):  # 如果所有值都为空，跳过
                    continue
                contact = CustomerContact(
                    customer_id=customer.id,
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
                db.session.add(contact)
        
        # 保存送货地址子表
        if 'delivery_addresses' in data:
            # 删除现有送货地址
            CustomerDeliveryAddress.query.filter_by(customer_id=customer.id).delete()
            
            for addr_data in data['delivery_addresses']:
                if not any(addr_data.values()):  # 如果所有值都为空，跳过
                    continue
                address = CustomerDeliveryAddress(
                    customer_id=customer.id,
                    delivery_address=addr_data.get('delivery_address'),
                    contact_name=addr_data.get('contact_name'),
                    contact_method=addr_data.get('contact_method'),
                    sort_order=addr_data.get('sort_order', 0)
                )
                db.session.add(address)
        
        # 保存开票单位子表
        if 'invoice_units' in data:
            # 删除现有开票单位
            CustomerInvoiceUnit.query.filter_by(customer_id=customer.id).delete()
            
            for invoice_data in data['invoice_units']:
                if not any(invoice_data.values()):  # 如果所有值都为空，跳过
                    continue
                invoice_unit = CustomerInvoiceUnit(
                    customer_id=customer.id,
                    invoice_unit=invoice_data.get('invoice_unit'),
                    taxpayer_id=invoice_data.get('taxpayer_id'),
                    invoice_address=invoice_data.get('invoice_address'),
                    invoice_phone=invoice_data.get('invoice_phone'),
                    invoice_bank=invoice_data.get('invoice_bank'),
                    invoice_account=invoice_data.get('invoice_account'),
                    sort_order=invoice_data.get('sort_order', 0)
                )
                db.session.add(invoice_unit)
        
        # 保存付款单位子表
        if 'payment_units' in data:
            # 删除现有付款单位
            CustomerPaymentUnit.query.filter_by(customer_id=customer.id).delete()
            
            for payment_data in data['payment_units']:
                if not any(payment_data.values()):  # 如果所有值都为空，跳过
                    continue
                payment_unit = CustomerPaymentUnit(
                    customer_id=customer.id,
                    payment_unit=payment_data.get('payment_unit'),
                    unit_code=payment_data.get('unit_code'),
                    sort_order=payment_data.get('sort_order', 0)
                )
                db.session.add(payment_unit)
        
        # 保存归属公司子表
        if 'affiliated_companies' in data:
            # 删除现有归属公司
            CustomerAffiliatedCompany.query.filter_by(customer_id=customer.id).delete()
            
            for company_data in data['affiliated_companies']:
                if not any(company_data.values()):  # 如果所有值都为空，跳过
                    continue
                affiliated_company = CustomerAffiliatedCompany(
                    customer_id=customer.id,
                    affiliated_company=company_data.get('affiliated_company'),
                    sort_order=company_data.get('sort_order', 0)
                )
                db.session.add(affiliated_company) 