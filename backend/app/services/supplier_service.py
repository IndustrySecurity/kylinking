from flask import current_app
from sqlalchemy import text, func
from app.extensions import db
from app.models.basic_data import (
    SupplierManagement, SupplierContact, SupplierDeliveryAddress,
    SupplierInvoiceUnit, SupplierAffiliatedCompany,
    SupplierCategoryManagement, DeliveryMethod, TaxRate, 
    Currency, PaymentMethod
)
from flask import g
import uuid
from datetime import datetime


class SupplierService:
    """供应商管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in SupplierService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_form_options():
        """获取表单选项数据"""
        try:
            # 设置schema
            SupplierService._set_schema()
            
            # 获取供应商分类
            supplier_categories = []
            try:
                categories = SupplierCategoryManagement.query.filter_by(is_enabled=True).order_by(SupplierCategoryManagement.sort_order, SupplierCategoryManagement.category_name).all()
                supplier_categories = [{'value': str(cat.id), 'label': cat.category_name} for cat in categories]
            except Exception as e:
                current_app.logger.error(f"Error getting supplier categories: {e}")
            
            # 获取送货方式
            delivery_methods = []
            try:
                methods = DeliveryMethod.query.filter_by(is_enabled=True).order_by(DeliveryMethod.sort_order, DeliveryMethod.delivery_name).all()
                delivery_methods = [{'value': str(method.id), 'label': method.delivery_name} for method in methods]
            except Exception as e:
                current_app.logger.error(f"Error getting delivery methods: {e}")
            
            # 获取税率
            tax_rates = []
            try:
                rates = TaxRate.query.filter_by(is_enabled=True).order_by(TaxRate.sort_order, TaxRate.tax_name).all()
                tax_rates = [{'value': str(rate.id), 'label': rate.tax_name, 'rate': float(rate.tax_rate)} for rate in rates]
            except Exception as e:
                current_app.logger.error(f"Error getting tax rates: {e}")
            
            # 获取币别
            currencies = []
            try:
                curr_list = Currency.query.filter_by(is_enabled=True).order_by(Currency.sort_order, Currency.currency_name).all()
                currencies = [{'value': str(curr.id), 'label': f"{curr.currency_name}({curr.currency_code})", 'is_base': curr.is_base_currency} for curr in curr_list]
            except Exception as e:
                current_app.logger.error(f"Error getting currencies: {e}")
            
            # 获取付款方式
            payment_methods = []
            try:
                methods = PaymentMethod.query.filter_by(is_enabled=True).order_by(PaymentMethod.sort_order, PaymentMethod.payment_name).all()
                payment_methods = [{'value': str(method.id), 'label': method.payment_name} for method in methods]
            except Exception as e:
                current_app.logger.error(f"Error getting payment methods: {e}")
            
            return {
                'supplier_categories': supplier_categories,
                'delivery_methods': delivery_methods,
                'tax_rates': tax_rates,
                'currencies': currencies,
                'payment_methods': payment_methods,
                'supplier_levels': SupplierManagement.get_supplier_level_options(),
                'enterprise_types': SupplierManagement.get_enterprise_type_options(),
                'provinces': [{'value': value, 'label': label} for value, label in SupplierManagement.PROVINCES]
            }
        except Exception as e:
            current_app.logger.error(f"Error getting form options: {e}")
            raise e
    
    @staticmethod
    def get_suppliers_list(page=1, per_page=20, search=None):
        """获取供应商列表"""
        try:
            # 设置schema
            SupplierService._set_schema()
            schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
            
            # 构建基础查询
            base_query = f"""
            SELECT 
                sm.id, sm.supplier_name, sm.supplier_code, sm.supplier_abbreviation, 
                sm.supplier_category_id, sm.supplier_level, sm.region, sm.organization_code,
                sm.company_website, sm.company_address, sm.is_disabled, sm.is_enabled, 
                sm.created_by, sm.updated_by, sm.created_at, sm.updated_at,
                scm.category_name as supplier_category_name,
                dm.delivery_name as delivery_method_name
            FROM {schema_name}.supplier_management sm
            LEFT JOIN {schema_name}.supplier_category_management scm ON sm.supplier_category_id = scm.id
            LEFT JOIN {schema_name}.delivery_methods dm ON sm.delivery_method_id = dm.id
            """
            
            # 构建WHERE条件
            where_conditions = []
            params = {'limit': per_page, 'offset': (page - 1) * per_page}
            
            if search:
                where_conditions.append("""
                    (sm.supplier_name ILIKE :search OR 
                     sm.supplier_code ILIKE :search OR 
                     sm.supplier_abbreviation ILIKE :search OR
                     sm.region ILIKE :search OR
                     sm.organization_code ILIKE :search OR
                     sm.company_address ILIKE :search)
                """)
                params['search'] = f'%{search}%'
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            # 添加排序和分页
            query = base_query + " ORDER BY sm.created_at DESC LIMIT :limit OFFSET :offset"
            
            # 执行查询
            with db.engine.begin() as conn:
                result = conn.execute(text(query), params)
                rows = result.fetchall()
                
                # 构建供应商数据
                suppliers = []
                for row in rows:
                    supplier_data = {
                        'id': str(row.id),
                        'supplier_name': row.supplier_name,
                        'supplier_code': row.supplier_code,
                        'supplier_abbreviation': row.supplier_abbreviation,
                        'supplier_category_id': str(row.supplier_category_id) if row.supplier_category_id else None,
                        'supplier_category_name': row.supplier_category_name,
                        'supplier_level': row.supplier_level,
                        'region': row.region,
                        'organization_code': row.organization_code,
                        'company_website': row.company_website,
                        'company_address': row.company_address,
                        'delivery_method_name': row.delivery_method_name,
                        'is_disabled': row.is_disabled,
                        'is_enabled': row.is_enabled,
                        'created_at': row.created_at.isoformat() if row.created_at else None,
                        'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                        'created_by': str(row.created_by) if row.created_by else None,
                        'updated_by': str(row.updated_by) if row.updated_by else None
                    }
                    suppliers.append(supplier_data)
                
                # 获取总数
                count_query = f"""
                SELECT COUNT(*) as total
                FROM {schema_name}.supplier_management sm
                """
                if where_conditions:
                    count_query += " WHERE " + " AND ".join(where_conditions)
                
                count_params = {k: v for k, v in params.items() if k not in ['limit', 'offset']}
                count_result = conn.execute(text(count_query), count_params)
                total = count_result.scalar()
                
                return {
                    'suppliers': suppliers,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                }
                
        except Exception as e:
            current_app.logger.error(f"Error getting suppliers list: {e}")
            raise e
    
    @staticmethod
    def get_supplier_by_id(supplier_id):
        """根据ID获取供应商详情"""
        try:
            # 设置schema
            SupplierService._set_schema()
            
            supplier = SupplierManagement.query.get(supplier_id)
            if not supplier:
                return None
            
            return supplier.to_dict(include_details=True)
        except Exception as e:
            current_app.logger.error(f"Error getting supplier by id: {e}")
            raise e
    
    @staticmethod
    def create_supplier(data, user_id):
        """创建供应商"""
        try:
            # 设置schema
            SupplierService._set_schema()
            
            supplier = SupplierManagement()
            
            # 生成供应商编号（如果没有提供）
            if not data.get('supplier_code'):
                # 获取当前最大编号
                max_code_result = db.session.execute(
                    text(f"SELECT supplier_code FROM {getattr(g, 'schema_name', 'mytenant')}.supplier_management WHERE supplier_code LIKE 'SUP%' ORDER BY supplier_code DESC LIMIT 1")
                ).first()
                
                if max_code_result and max_code_result[0]:
                    try:
                        max_num = int(max_code_result[0][3:])  # 提取SUP后面的数字
                        new_num = max_num + 1
                    except (ValueError, IndexError):
                        new_num = 1
                else:
                    new_num = 1
                
                supplier_code = f"SUP{new_num:06d}"  # SUP000001格式
            else:
                supplier_code = data['supplier_code']
            
            # 基本信息
            supplier.supplier_name = data['supplier_name']
            supplier.supplier_code = supplier_code
            supplier.supplier_abbreviation = data.get('supplier_abbreviation')
            supplier.supplier_category_id = data.get('supplier_category_id')
            supplier.purchaser_id = data.get('purchaser_id')
            supplier.is_disabled = data.get('is_disabled', False)
            supplier.region = data.get('region')
            supplier.delivery_method_id = data.get('delivery_method_id')
            supplier.tax_rate_id = data.get('tax_rate_id')
            supplier.tax_rate = data.get('tax_rate')
            supplier.currency_id = data.get('currency_id')
            supplier.payment_method_id = data.get('payment_method_id')
            
            # 数字字段
            supplier.deposit_ratio = data.get('deposit_ratio', 0)
            supplier.delivery_preparation_days = data.get('delivery_preparation_days', 0)
            supplier.copyright_square_price = data.get('copyright_square_price', 0)
            supplier.supplier_level = data.get('supplier_level')
            
            # 编码和网址字段
            supplier.organization_code = data.get('organization_code')
            supplier.company_website = data.get('company_website')
            supplier.foreign_currency_id = data.get('foreign_currency_id')
            supplier.barcode_prefix_code = data.get('barcode_prefix_code')
            
            # 日期字段
            if data.get('business_start_date'):
                supplier.business_start_date = datetime.fromisoformat(data['business_start_date']).date()
            if data.get('business_end_date'):
                supplier.business_end_date = datetime.fromisoformat(data['business_end_date']).date()
            if data.get('production_permit_start_date'):
                supplier.production_permit_start_date = datetime.fromisoformat(data['production_permit_start_date']).date()
            if data.get('production_permit_end_date'):
                supplier.production_permit_end_date = datetime.fromisoformat(data['production_permit_end_date']).date()
            if data.get('inspection_report_start_date'):
                supplier.inspection_report_start_date = datetime.fromisoformat(data['inspection_report_start_date']).date()
            if data.get('inspection_report_end_date'):
                supplier.inspection_report_end_date = datetime.fromisoformat(data['inspection_report_end_date']).date()
            
            # 其他字段
            supplier.barcode_authorization = data.get('barcode_authorization', 0)
            supplier.ufriend_code = data.get('ufriend_code')
            supplier.enterprise_type = data.get('enterprise_type')
            supplier.province = data.get('province')
            supplier.city = data.get('city')
            supplier.district = data.get('district')
            supplier.company_address = data.get('company_address')
            supplier.remarks = data.get('remarks')
            supplier.image_url = data.get('image_url')
            
            # 审计字段
            supplier.created_by = user_id
            supplier.updated_by = user_id
            
            db.session.add(supplier)
            db.session.flush()
            
            # 处理子表数据
            SupplierService._handle_sub_tables(supplier.id, data, user_id)
            
            db.session.commit()
            return supplier.to_dict(include_details=True)
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating supplier: {e}")
            raise e
    
    @staticmethod
    def update_supplier(supplier_id, data, user_id):
        """更新供应商"""
        try:
            # 设置schema
            SupplierService._set_schema()
            
            supplier = SupplierManagement.query.get(supplier_id)
            if not supplier:
                return None
            
            
            # 基本信息
            supplier.supplier_name = data['supplier_name']
            supplier.supplier_code = data.get('supplier_code')
            supplier.supplier_abbreviation = data.get('supplier_abbreviation')
            supplier.supplier_category_id = data.get('supplier_category_id')
            supplier.purchaser_id = data.get('purchaser_id')
            supplier.is_disabled = data.get('is_disabled', False)
            supplier.region = data.get('region')
            supplier.delivery_method_id = data.get('delivery_method_id')
            supplier.tax_rate_id = data.get('tax_rate_id')
            supplier.tax_rate = data.get('tax_rate')
            supplier.currency_id = data.get('currency_id')
            supplier.payment_method_id = data.get('payment_method_id')
            
            # 数字字段
            supplier.deposit_ratio = data.get('deposit_ratio', 0)
            supplier.delivery_preparation_days = data.get('delivery_preparation_days', 0)
            supplier.copyright_square_price = data.get('copyright_square_price', 0)
            supplier.supplier_level = data.get('supplier_level')
            
            # 编码和网址字段
            supplier.organization_code = data.get('organization_code')
            supplier.company_website = data.get('company_website')
            supplier.foreign_currency_id = data.get('foreign_currency_id')
            supplier.barcode_prefix_code = data.get('barcode_prefix_code')
            
            # 日期字段
            if data.get('business_start_date'):
                supplier.business_start_date = datetime.fromisoformat(data['business_start_date']).date()
            else:
                supplier.business_start_date = None
                
            if data.get('business_end_date'):
                supplier.business_end_date = datetime.fromisoformat(data['business_end_date']).date()
            else:
                supplier.business_end_date = None
                
            if data.get('production_permit_start_date'):
                supplier.production_permit_start_date = datetime.fromisoformat(data['production_permit_start_date']).date()
            else:
                supplier.production_permit_start_date = None
                
            if data.get('production_permit_end_date'):
                supplier.production_permit_end_date = datetime.fromisoformat(data['production_permit_end_date']).date()
            else:
                supplier.production_permit_end_date = None
                
            if data.get('inspection_report_start_date'):
                supplier.inspection_report_start_date = datetime.fromisoformat(data['inspection_report_start_date']).date()
            else:
                supplier.inspection_report_start_date = None
                
            if data.get('inspection_report_end_date'):
                supplier.inspection_report_end_date = datetime.fromisoformat(data['inspection_report_end_date']).date()
            else:
                supplier.inspection_report_end_date = None
            
            # 其他字段
            supplier.barcode_authorization = data.get('barcode_authorization', 0)
            supplier.ufriend_code = data.get('ufriend_code')
            supplier.enterprise_type = data.get('enterprise_type')
            supplier.province = data.get('province')
            supplier.city = data.get('city')
            supplier.district = data.get('district')
            supplier.company_address = data.get('company_address')
            supplier.remarks = data.get('remarks')
            supplier.image_url = data.get('image_url')
            
            # 审计字段
            supplier.updated_by = user_id
            supplier.updated_at = datetime.utcnow()
            
            # 删除旧的子表数据
            SupplierContact.query.filter_by(supplier_id=supplier_id).delete()
            SupplierDeliveryAddress.query.filter_by(supplier_id=supplier_id).delete()
            SupplierInvoiceUnit.query.filter_by(supplier_id=supplier_id).delete()
            SupplierAffiliatedCompany.query.filter_by(supplier_id=supplier_id).delete()
            
            # 添加新的子表数据
            SupplierService._handle_sub_tables(supplier_id, data, user_id)
            
            db.session.commit()
            return supplier.to_dict(include_details=True)
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating supplier: {e}")
            raise e
    
    @staticmethod
    def delete_supplier(supplier_id):
        """删除供应商"""
        try:
            # 设置schema
            SupplierService._set_schema()
            
            supplier = SupplierManagement.query.get(supplier_id)
            if not supplier:
                return False
            
            db.session.delete(supplier)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting supplier: {e}")
            raise e
    
    @staticmethod
    def _handle_sub_tables(supplier_id, data, user_id):
        """处理子表数据"""
        # 处理联系人
        if 'contacts' in data and data['contacts']:
            for contact_data in data['contacts']:
                contact = SupplierContact()
                contact.supplier_id = supplier_id
                contact.contact_name = contact_data.get('contact_name')
                contact.landline = contact_data.get('landline')
                contact.mobile = contact_data.get('mobile')
                contact.fax = contact_data.get('fax')
                contact.qq = contact_data.get('qq')
                contact.wechat = contact_data.get('wechat')
                contact.email = contact_data.get('email')
                contact.department = contact_data.get('department')
                contact.sort_order = contact_data.get('sort_order', 0)
                db.session.add(contact)
        
        # 处理发货地址
        if 'delivery_addresses' in data and data['delivery_addresses']:
            for addr_data in data['delivery_addresses']:
                addr = SupplierDeliveryAddress()
                addr.supplier_id = supplier_id
                addr.delivery_address = addr_data.get('delivery_address')
                addr.contact_name = addr_data.get('contact_name')
                addr.contact_method = addr_data.get('contact_method')
                addr.sort_order = addr_data.get('sort_order', 0)
                db.session.add(addr)
        
        # 处理开票单位
        if 'invoice_units' in data and data['invoice_units']:
            for unit_data in data['invoice_units']:
                unit = SupplierInvoiceUnit()
                unit.supplier_id = supplier_id
                unit.invoice_unit = unit_data.get('invoice_unit')
                unit.taxpayer_id = unit_data.get('taxpayer_id')
                unit.invoice_address = unit_data.get('invoice_address')
                unit.invoice_phone = unit_data.get('invoice_phone')
                unit.invoice_bank = unit_data.get('invoice_bank')
                unit.invoice_account = unit_data.get('invoice_account')
                unit.sort_order = unit_data.get('sort_order', 0)
                db.session.add(unit)
        
        # 处理归属公司
        if 'affiliated_companies' in data and data['affiliated_companies']:
            for company_data in data['affiliated_companies']:
                company = SupplierAffiliatedCompany()
                company.supplier_id = supplier_id
                company.affiliated_company = company_data.get('affiliated_company')
                company.sort_order = company_data.get('sort_order', 0)
                db.session.add(company) 