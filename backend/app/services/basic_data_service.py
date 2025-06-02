# -*- coding: utf-8 -*-
"""
基础档案管理服务层
"""

from app.extensions import db
from app.models.basic_data import Customer, CustomerCategory, Supplier, SupplierCategory, Product, ProductCategory, CalculationParameter, CalculationScheme, Department, Position, Employee, Warehouse, BagType, BagTypeStructure
from app.models.user import User
from app.services.module_service import TenantConfigService
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re


class BasicDataService:
    """基础档案管理服务"""
    
    @staticmethod
    def get_tenant_models(tenant_schema):
        """根据租户schema获取动态表模型"""
        # 这里需要实现动态的租户表切换
        # 目前先返回基础模型，后续需要实现多租户表切换逻辑
        return {
            'Customer': Customer,
            'CustomerCategory': CustomerCategory,
            'Supplier': Supplier,
            'SupplierCategory': SupplierCategory,
            'Product': Product,
            'ProductCategory': ProductCategory
        }
    
    @staticmethod
    def generate_code(entity_type, tenant_schema=None):
        """生成编码"""
        prefixes = {
            'customer': 'C',
            'supplier': 'S', 
            'product': 'P'
        }
        
        prefix = prefixes.get(entity_type, 'X')
        
        # 获取当前最大编号
        if entity_type == 'customer':
            model = Customer
        elif entity_type == 'supplier':
            model = Supplier
        elif entity_type == 'product':
            model = Product
        else:
            raise ValueError(f"不支持的实体类型: {entity_type}")
        
        # 查询最大编号
        max_code = db.session.query(func.max(model.customer_code if entity_type == 'customer' 
                                           else model.supplier_code if entity_type == 'supplier'
                                           else model.product_code)).scalar()
        
        if max_code:
            # 提取数字部分并加1
            try:
                number = int(max_code[1:]) + 1
            except (ValueError, IndexError):
                number = 1
        else:
            number = 1
        
        return f"{prefix}{number:06d}"


class CustomerService:
    """客户档案服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in CustomerService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_customers(page=1, per_page=20, search=None, category_id=None, status=None, 
                     tenant_config=None):
        """获取客户列表"""
        # 设置schema
        CustomerService._set_schema()
        
        query = db.session.query(Customer)
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                Customer.customer_code.ilike(search_pattern),
                Customer.customer_name.ilike(search_pattern),
                Customer.contact_person.ilike(search_pattern),
                Customer.contact_phone.ilike(search_pattern)
            ))
        
        # 分类筛选
        if category_id:
            query = query.filter(Customer.category_id == uuid.UUID(category_id))
        
        # 状态筛选
        if status:
            query = query.filter(Customer.status == status)
        
        # 应用租户字段配置
        if tenant_config:
            # 这里可以根据租户配置调整查询条件
            pass
        
        # 排序
        query = query.order_by(Customer.created_at.desc())
        
        # 分页
        total = query.count()
        customers = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'customers': [customer.to_dict() for customer in customers],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def get_customer(customer_id):
        """获取客户详情"""
        # 设置schema
        CustomerService._set_schema()
        
        customer = db.session.query(Customer).get(uuid.UUID(customer_id))
        if not customer:
            raise ValueError("客户不存在")
        return customer.to_dict()
    
    @staticmethod
    def create_customer(data, created_by):
        """创建客户"""
        # 设置schema
        CustomerService._set_schema()
        
        try:
            # 生成客户编码
            if not data.get('customer_code'):
                data['customer_code'] = BasicDataService.generate_code('customer')
            
            # 创建客户对象
            customer = Customer(
                customer_code=data['customer_code'],
                customer_name=data['customer_name'],
                customer_type=data.get('customer_type', 'enterprise'),
                category_id=uuid.UUID(data['category_id']) if data.get('category_id') else None,
                
                # 基本信息
                legal_name=data.get('legal_name'),
                unified_credit_code=data.get('unified_credit_code'),
                tax_number=data.get('tax_number'),
                industry=data.get('industry'),
                scale=data.get('scale'),
                
                # 联系信息
                contact_person=data.get('contact_person'),
                contact_phone=data.get('contact_phone'),
                contact_email=data.get('contact_email'),
                contact_address=data.get('contact_address'),
                postal_code=data.get('postal_code'),
                
                # 业务信息
                credit_limit=data.get('credit_limit', 0),
                payment_terms=data.get('payment_terms', 30),
                currency=data.get('currency', 'CNY'),
                price_level=data.get('price_level', 'standard'),
                sales_person_id=uuid.UUID(data['sales_person_id']) if data.get('sales_person_id') else None,
                
                # 自定义字段
                custom_fields=data.get('custom_fields', {}),
                
                # 审计字段
                created_by=uuid.UUID(created_by)
            )
            
            db.session.add(customer)
            db.session.commit()
            
            return customer.to_dict()
            
        except IntegrityError as e:
            db.session.rollback()
            if 'customer_code' in str(e):
                raise ValueError("客户编码已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建客户失败: {str(e)}")
    
    @staticmethod
    def update_customer(customer_id, data, updated_by):
        """更新客户"""
        try:
            customer = db.session.query(Customer).get(uuid.UUID(customer_id))
            if not customer:
                raise ValueError("客户不存在")
            
            # 更新字段
            update_fields = [
                'customer_name', 'customer_type', 'legal_name', 'unified_credit_code',
                'tax_number', 'industry', 'scale', 'contact_person', 'contact_phone',
                'contact_email', 'contact_address', 'postal_code', 'credit_limit',
                'payment_terms', 'currency', 'price_level'
            ]
            
            for field in update_fields:
                if field in data:
                    setattr(customer, field, data[field])
            
            # 处理外键字段
            if 'category_id' in data:
                customer.category_id = uuid.UUID(data['category_id']) if data['category_id'] else None
            
            if 'sales_person_id' in data:
                customer.sales_person_id = uuid.UUID(data['sales_person_id']) if data['sales_person_id'] else None
            
            # 自定义字段
            if 'custom_fields' in data:
                customer.custom_fields = data['custom_fields']
            
            # 审计字段
            customer.updated_by = uuid.UUID(updated_by)
            customer.updated_at = datetime.now()
            
            db.session.commit()
            return customer.to_dict()
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"更新客户失败: {str(e)}")
    
    @staticmethod
    def delete_customer(customer_id):
        """删除客户"""
        try:
            customer = db.session.query(Customer).get(uuid.UUID(customer_id))
            if not customer:
                raise ValueError("客户不存在")
            
            # 检查是否有关联数据
            # TODO: 检查是否有销售订单等关联数据
            
            db.session.delete(customer)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"删除客户失败: {str(e)}")
    
    @staticmethod
    def approve_customer(customer_id, approved_by):
        """审批客户"""
        try:
            customer = db.session.query(Customer).get(uuid.UUID(customer_id))
            if not customer:
                raise ValueError("客户不存在")
            
            customer.is_approved = True
            customer.approved_by = uuid.UUID(approved_by)
            customer.approved_at = datetime.now()
            customer.status = 'active'
            
            db.session.commit()
            return customer.to_dict()
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"审批客户失败: {str(e)}")


class CustomerCategoryService:
    """客户分类服务"""
    
    @staticmethod
    def get_categories(include_inactive=False):
        """获取客户分类树"""
        query = db.session.query(CustomerCategory)
        
        if not include_inactive:
            query = query.filter(CustomerCategory.is_active == True)
        
        categories = query.order_by(CustomerCategory.sort_order, CustomerCategory.category_name).all()
        
        # 构建树形结构
        category_dict = {str(cat.id): cat.to_dict() for cat in categories}
        tree = []
        
        for cat_dict in category_dict.values():
            if cat_dict['parent_id']:
                parent = category_dict.get(cat_dict['parent_id'])
                if parent:
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(cat_dict)
            else:
                tree.append(cat_dict)
        
        return tree
    
    @staticmethod
    def create_category(data):
        """创建客户分类"""
        try:
            # 计算层级
            level = 1
            if data.get('parent_id'):
                parent = db.session.query(CustomerCategory).get(uuid.UUID(data['parent_id']))
                if parent:
                    level = parent.level + 1
            
            category = CustomerCategory(
                category_code=data['category_code'],
                category_name=data['category_name'],
                parent_id=uuid.UUID(data['parent_id']) if data.get('parent_id') else None,
                level=level,
                sort_order=data.get('sort_order', 0),
                description=data.get('description')
            )
            
            db.session.add(category)
            db.session.commit()
            
            return category.to_dict()
            
        except IntegrityError:
            db.session.rollback()
            raise ValueError("分类编码已存在")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建分类失败: {str(e)}")


class SupplierService:
    """供应商档案服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in SupplierService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_suppliers(page=1, per_page=20, search=None, category_id=None, status=None):
        """获取供应商列表"""
        # 设置schema
        SupplierService._set_schema()
        
        query = db.session.query(Supplier)
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                Supplier.supplier_code.ilike(search_pattern),
                Supplier.supplier_name.ilike(search_pattern),
                Supplier.contact_person.ilike(search_pattern),
                Supplier.contact_phone.ilike(search_pattern)
            ))
        
        # 分类筛选
        if category_id:
            query = query.filter(Supplier.category_id == uuid.UUID(category_id))
        
        # 状态筛选
        if status:
            query = query.filter(Supplier.status == status)
        
        # 排序
        query = query.order_by(Supplier.created_at.desc())
        
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
    
    @staticmethod
    def create_supplier(data, created_by):
        """创建供应商"""
        # 设置schema
        SupplierService._set_schema()
        
        try:
            # 生成供应商编码
            if not data.get('supplier_code'):
                data['supplier_code'] = BasicDataService.generate_code('supplier')
            
            supplier = Supplier(
                supplier_code=data['supplier_code'],
                supplier_name=data['supplier_name'],
                supplier_type=data.get('supplier_type', 'material'),
                category_id=uuid.UUID(data['category_id']) if data.get('category_id') else None,
                
                # 基本信息
                legal_name=data.get('legal_name'),
                unified_credit_code=data.get('unified_credit_code'),
                business_license=data.get('business_license'),
                industry=data.get('industry'),
                established_date=data.get('established_date'),
                
                # 联系信息
                contact_person=data.get('contact_person'),
                contact_phone=data.get('contact_phone'),
                contact_email=data.get('contact_email'),
                office_address=data.get('office_address'),
                factory_address=data.get('factory_address'),
                
                # 业务信息
                payment_terms=data.get('payment_terms', 30),
                currency=data.get('currency', 'CNY'),
                quality_level=data.get('quality_level', 'qualified'),
                cooperation_level=data.get('cooperation_level', 'ordinary'),
                
                # 自定义字段
                custom_fields=data.get('custom_fields', {}),
                
                # 审计字段
                created_by=uuid.UUID(created_by)
            )
            
            db.session.add(supplier)
            db.session.commit()
            
            return supplier.to_dict()
            
        except IntegrityError:
            db.session.rollback()
            raise ValueError("供应商编码已存在")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建供应商失败: {str(e)}")


class ProductService:
    """产品档案服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in ProductService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_products(page=1, per_page=20, search=None, category_id=None, status=None, 
                    product_type=None):
        """获取产品列表"""
        # 设置schema
        ProductService._set_schema()
        
        query = db.session.query(Product)
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                Product.product_code.ilike(search_pattern),
                Product.product_name.ilike(search_pattern),
                Product.short_name.ilike(search_pattern),
                Product.brand.ilike(search_pattern),
                Product.model.ilike(search_pattern)
            ))
        
        # 分类筛选
        if category_id:
            query = query.filter(Product.category_id == uuid.UUID(category_id))
        
        # 状态筛选
        if status:
            query = query.filter(Product.status == status)
        
        # 产品类型筛选
        if product_type:
            query = query.filter(Product.product_type == product_type)
        
        # 排序
        query = query.order_by(Product.created_at.desc())
        
        # 分页
        total = query.count()
        products = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'products': [product.to_dict() for product in products],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def create_product(data, created_by):
        """创建产品"""
        try:
            # 生成产品编码
            if not data.get('product_code'):
                data['product_code'] = BasicDataService.generate_code('product')
            
            product = Product(
                product_code=data['product_code'],
                product_name=data['product_name'],
                product_type=data.get('product_type', 'finished'),
                category_id=uuid.UUID(data['category_id']) if data.get('category_id') else None,
                
                # 基本信息
                short_name=data.get('short_name'),
                english_name=data.get('english_name'),
                brand=data.get('brand'),
                model=data.get('model'),
                specification=data.get('specification'),
                
                # 技术参数
                thickness=data.get('thickness'),
                width=data.get('width'),
                length=data.get('length'),
                material_type=data.get('material_type'),
                transparency=data.get('transparency'),
                tensile_strength=data.get('tensile_strength'),
                
                # 包装信息
                base_unit=data.get('base_unit', 'm²'),
                package_unit=data.get('package_unit'),
                conversion_rate=data.get('conversion_rate', 1),
                net_weight=data.get('net_weight'),
                gross_weight=data.get('gross_weight'),
                
                # 价格信息
                standard_cost=data.get('standard_cost'),
                standard_price=data.get('standard_price'),
                currency=data.get('currency', 'CNY'),
                
                # 库存信息
                safety_stock=data.get('safety_stock', 0),
                min_order_qty=data.get('min_order_qty', 1),
                max_order_qty=data.get('max_order_qty'),
                
                # 生产信息
                lead_time=data.get('lead_time', 0),
                shelf_life=data.get('shelf_life'),
                storage_condition=data.get('storage_condition'),
                
                # 质量标准
                quality_standard=data.get('quality_standard'),
                inspection_method=data.get('inspection_method'),
                
                # 系统字段
                is_sellable=data.get('is_sellable', True),
                is_purchasable=data.get('is_purchasable', True),
                is_producible=data.get('is_producible', True),
                
                # 自定义字段
                custom_fields=data.get('custom_fields', {}),
                
                # 审计字段
                created_by=uuid.UUID(created_by)
            )
            
            db.session.add(product)
            db.session.commit()
            
            return product.to_dict()
            
        except IntegrityError:
            db.session.rollback()
            raise ValueError("产品编码已存在")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建产品失败: {str(e)}")


class TenantFieldConfigIntegrationService:
    """租户字段配置集成服务"""
    
    @staticmethod
    def apply_field_config(entity_data, module_name, tenant_id):
        """应用租户字段配置到实体数据"""
        try:
            # 获取租户的字段配置
            field_configs = TenantConfigService.get_tenant_field_configs(tenant_id, module_name)
            
            if not field_configs:
                return entity_data
            
            # 应用字段配置
            for field_config in field_configs:
                field_name = field_config.get('field_name')
                
                if field_name in entity_data:
                    # 应用自定义标签
                    if field_config.get('custom_label'):
                        # 可以在前端使用这个标签
                        pass
                    
                    # 应用显示控制
                    if not field_config.get('is_visible', True):
                        entity_data.pop(field_name, None)
                    
                    # 应用验证规则
                    # 这里可以添加字段验证逻辑
            
            return entity_data
            
        except Exception as e:
            print(f"应用字段配置失败: {str(e)}")
            return entity_data
    
    @staticmethod
    def get_field_metadata(module_name, tenant_id):
        """获取字段元数据（包含租户配置）"""
        try:
            # 获取系统字段定义
            from app.services.module_service import ModuleService
            
            # 根据模块名获取模块ID
            module = ModuleService.get_module_by_name(module_name)
            if not module:
                return {}
            
            # 获取字段定义
            fields = ModuleService.get_module_fields(str(module['id']))
            
            # 获取租户字段配置
            field_configs = TenantConfigService.get_tenant_field_configs(tenant_id, module_name)
            
            # 合并配置
            field_metadata = {}
            for field in fields:
                field_name = field.get('field_name')
                
                # 查找对应的租户配置
                tenant_config = next(
                    (config for config in field_configs if config.get('field_name') == field_name),
                    {}
                )
                
                # 合并配置
                field_metadata[field_name] = {
                    **field,  # 系统字段定义
                    **tenant_config  # 租户自定义配置
                }
            
            return field_metadata
            
        except Exception as e:
            print(f"获取字段元数据失败: {str(e)}")
            return {}


class CalculationParameterService:
    """计算参数服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in CalculationParameterService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_calculation_parameters(page=1, per_page=20, search=None):
        """获取计算参数列表"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        CalculationParameterService._set_schema()
        
        query = CalculationParameter.query
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                CalculationParameter.parameter_name.ilike(search_pattern)
            )
        
        # 排序
        query = query.order_by(CalculationParameter.sort_order, CalculationParameter.parameter_name)
        
        # 分页
        total = query.count()
        if per_page > 0:
            calculation_parameters = query.offset((page - 1) * per_page).limit(per_page).all()
        else:
            calculation_parameters = query.all()
        
        return {
            'calculation_parameters': [param.to_dict(include_user_info=True) for param in calculation_parameters],
            'total': total,
            'current_page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page if per_page > 0 else 1
        }
    
    @staticmethod
    def get_calculation_parameter(param_id):
        """获取计算参数详情"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        CalculationParameterService._set_schema()
        
        param = CalculationParameter.query.get(uuid.UUID(param_id))
        if not param:
            raise ValueError("计算参数不存在")
        return param.to_dict(include_user_info=True)
    
    @staticmethod
    def create_calculation_parameter(data, created_by):
        """创建计算参数"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        CalculationParameterService._set_schema()
        
        try:
            # 验证必填字段
            if not data.get('parameter_name'):
                raise ValueError("计算参数名称不能为空")
            
            # 检查名称是否重复
            existing = CalculationParameter.query.filter_by(
                parameter_name=data['parameter_name']
            ).first()
            if existing:
                raise ValueError("计算参数名称已存在")
            
            # 创建计算参数对象
            param = CalculationParameter(
                parameter_name=data['parameter_name'],
                description=data.get('description'),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            db.session.add(param)
            db.session.commit()
            
            # 清除缓存
            CalculationSchemeService._clear_parameter_cache()
            
            return param.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建计算参数失败: {str(e)}")
    
    @staticmethod
    def update_calculation_parameter(param_id, data, updated_by):
        """更新计算参数"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        CalculationParameterService._set_schema()
        
        try:
            param = CalculationParameter.query.get(uuid.UUID(param_id))
            if not param:
                raise ValueError("计算参数不存在")
            
            # 验证必填字段
            if 'parameter_name' in data and not data['parameter_name']:
                raise ValueError("计算参数名称不能为空")
            
            # 检查名称是否重复（排除自己）
            if 'parameter_name' in data:
                existing = CalculationParameter.query.filter(
                    CalculationParameter.parameter_name == data['parameter_name'],
                    CalculationParameter.id != param.id
                ).first()
                if existing:
                    raise ValueError("计算参数名称已存在")
            
            # 更新字段
            update_fields = ['parameter_name', 'description', 'sort_order', 'is_enabled']
            
            for field in update_fields:
                if field in data:
                    setattr(param, field, data[field])
            
            # 更新审计字段
            param.updated_by = uuid.UUID(updated_by)
            param.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 清除缓存
            CalculationSchemeService._clear_parameter_cache()
            
            return param.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"更新计算参数失败: {str(e)}")
    
    @staticmethod
    def delete_calculation_parameter(param_id):
        """删除计算参数"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        CalculationParameterService._set_schema()
        
        try:
            param = CalculationParameter.query.get(uuid.UUID(param_id))
            if not param:
                raise ValueError("计算参数不存在")
            
            db.session.delete(param)
            db.session.commit()
            
            # 清除缓存
            CalculationSchemeService._clear_parameter_cache()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"删除计算参数失败: {str(e)}")
    
    @staticmethod
    def batch_update_calculation_parameters(updates, updated_by):
        """批量更新计算参数"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        CalculationParameterService._set_schema()
        
        try:
            results = []
            
            for update_data in updates:
                param_id = update_data.get('id')
                if not param_id:
                    continue
                    
                param = CalculationParameter.query.get(uuid.UUID(param_id))
                if not param:
                    continue
                
                # 更新字段
                update_fields = ['parameter_name', 'description', 'sort_order', 'is_enabled']
                
                for field in update_fields:
                    if field in update_data:
                        setattr(param, field, update_data[field])
                
                # 更新审计字段
                param.updated_by = uuid.UUID(updated_by)
                param.updated_at = datetime.utcnow()
                
                results.append(param.to_dict())
            
            db.session.commit()
            
            # 清除缓存
            CalculationSchemeService._clear_parameter_cache()
            
            return results
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"批量更新计算参数失败: {str(e)}")
    
    @staticmethod
    def get_calculation_parameter_options():
        """获取计算参数选项数据"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        CalculationParameterService._set_schema()
        
        try:
            # 获取启用的计算参数
            enabled_params = CalculationParameter.get_enabled_list()
            
            return {
                'calculation_parameters': [
                    {
                        'id': str(param.id),
                        'parameter_name': param.parameter_name,
                        'sort_order': param.sort_order
                    }
                    for param in enabled_params
                ]
            }
            
        except Exception as e:
            raise ValueError(f"获取计算参数选项失败: {str(e)}")


class CalculationSchemeService:
    """计算方案服务"""
    
    # 类级别的参数缓存，避免频繁查询数据库
    _parameter_cache = None
    _cache_timestamp = None
    _cache_timeout = 300  # 5分钟缓存时间

    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in CalculationSchemeService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))

    @classmethod
    def _get_cached_parameters(cls):
        """获取缓存的参数列表"""
        import time
        current_time = time.time()
        
        # 检查缓存是否过期
        if (cls._parameter_cache is None or 
            cls._cache_timestamp is None or 
            current_time - cls._cache_timestamp > cls._cache_timeout):
            
            try:
                # 设置schema
                cls._set_schema()
                
                from app.models.basic_data import CalculationParameter
                existing_params = db.session.query(CalculationParameter.parameter_name).filter(
                    CalculationParameter.is_enabled == True
                ).all()
                cls._parameter_cache = [p[0] for p in existing_params]
                cls._cache_timestamp = current_time
            except Exception:
                # 如果查询失败，返回空列表，但不更新缓存时间，下次会重试
                return []
        
        return cls._parameter_cache or []
    
    @classmethod
    def _clear_parameter_cache(cls):
        """清除参数缓存（在参数更新时调用）"""
        cls._parameter_cache = None
        cls._cache_timestamp = None

    @staticmethod
    def get_calculation_schemes(page=1, per_page=20, search=None, category=None):
        """获取计算方案列表"""
        # 设置schema
        CalculationSchemeService._set_schema()
        
        query = db.session.query(CalculationScheme)
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                CalculationScheme.scheme_name.ilike(search_pattern),
                CalculationScheme.description.ilike(search_pattern)
            ))
        
        # 分类筛选
        if category:
            query = query.filter(CalculationScheme.scheme_category == category)
        
        # 只查询启用的记录
        query = query.filter(CalculationScheme.is_enabled == True)
        
        # 排序
        query = query.order_by(CalculationScheme.sort_order, CalculationScheme.created_at.desc())
        
        # 分页
        total = query.count()
        schemes = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'schemes': [scheme.to_dict() for scheme in schemes],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def get_calculation_scheme(scheme_id):
        """获取计算方案详情"""
        # 设置schema
        CalculationSchemeService._set_schema()
        
        scheme = db.session.query(CalculationScheme).get(uuid.UUID(scheme_id))
        if not scheme:
            raise ValueError("计算方案不存在")
        return scheme.to_dict()
    
    @staticmethod
    def create_calculation_scheme(data, created_by):
        """创建计算方案"""
        # 设置schema
        CalculationSchemeService._set_schema()
        
        try:
            # 验证公式
            if data.get('scheme_formula'):
                validation_result = CalculationSchemeService.validate_formula(data['scheme_formula'])
                if not validation_result['is_valid']:
                    raise ValueError(f"公式验证失败: {validation_result['error']}")
            
            # 创建计算方案对象
            scheme = CalculationScheme(
                scheme_name=data['scheme_name'],
                scheme_category=data['scheme_category'],
                scheme_formula=data.get('scheme_formula', ''),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            db.session.add(scheme)
            db.session.commit()
            
            return scheme.to_dict()
            
        except IntegrityError as e:
            db.session.rollback()
            if 'scheme_name' in str(e):
                raise ValueError("方案名称已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建计算方案失败: {str(e)}")
    
    @staticmethod
    def update_calculation_scheme(scheme_id, data, updated_by):
        """更新计算方案"""
        # 设置schema
        CalculationSchemeService._set_schema()
        
        try:
            scheme = db.session.query(CalculationScheme).get(uuid.UUID(scheme_id))
            if not scheme:
                raise ValueError("计算方案不存在")
            
            # 验证公式
            if 'scheme_formula' in data and data['scheme_formula']:
                validation_result = CalculationSchemeService.validate_formula(data['scheme_formula'])
                if not validation_result['is_valid']:
                    raise ValueError(f"公式验证失败: {validation_result['error']}")
            
            # 更新字段
            update_fields = ['scheme_name', 'scheme_category', 'scheme_formula', 'description', 'sort_order', 'is_enabled']
            
            for field in update_fields:
                if field in data:
                    setattr(scheme, field, data[field])
            
            scheme.updated_by = uuid.UUID(updated_by)
            scheme.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return scheme.to_dict()
            
        except IntegrityError as e:
            db.session.rollback()
            if 'scheme_name' in str(e):
                raise ValueError("方案名称已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"更新计算方案失败: {str(e)}")
    
    @staticmethod
    def delete_calculation_scheme(scheme_id):
        """删除计算方案"""
        # 设置schema
        CalculationSchemeService._set_schema()
        
        try:
            scheme = db.session.query(CalculationScheme).get(uuid.UUID(scheme_id))
            if not scheme:
                raise ValueError("计算方案不存在")
            
            db.session.delete(scheme)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"删除计算方案失败: {str(e)}")
    
    @staticmethod
    def get_scheme_categories():
        """获取方案分类选项"""
        # 设置schema
        CalculationSchemeService._set_schema()
        
        try:
            return CalculationScheme.get_scheme_categories()
        except Exception as e:
            raise ValueError(f"获取方案分类失败: {str(e)}")
    
    @staticmethod
    def validate_formula(formula):
        """验证公式语法"""
        # 设置schema（用于参数验证）
        CalculationSchemeService._set_schema()
        
        try:
            if not formula or not formula.strip():
                return {'is_valid': True, 'error': None, 'warnings': []}
            
            # 统计信息
            param_count = len(re.findall(r'\[([^\]]+)\]', formula))
            string_count = len(re.findall(r"'([^']*)'", formula))
            line_count = formula.count('\n') + 1
            
            errors = []
            warnings = []
            
            # 1. 检查括号匹配
            round_brackets = formula.count('(') - formula.count(')')
            square_brackets = formula.count('[') - formula.count(']')
            single_quotes = formula.count("'")
            
            if round_brackets != 0:
                errors.append(f"圆括号不匹配，多了 {abs(round_brackets)} 个{'左' if round_brackets > 0 else '右'}括号")
            
            if square_brackets != 0:
                errors.append(f"方括号不匹配，多了 {abs(square_brackets)} 个{'左' if square_brackets > 0 else '右'}括号")
            
            if single_quotes % 2 != 0:
                errors.append("单引号不匹配，必须成对出现")
            
            # 2. 检查参数引用格式
            params = re.findall(r'\[([^\]]+)\]', formula)
            for param in params:
                if not param.strip():
                    errors.append("发现空的参数引用: []")
                elif not re.match(r'^[a-zA-Z\u4e00-\u9fa5][a-zA-Z0-9\u4e00-\u9fa5_]*$', param.strip()):
                    warnings.append(f"参数名称格式建议优化: [{param}]")
            
            # 3. 检查字符串格式
            strings = re.findall(r"'([^']*)'", formula)
            for string in strings:
                if not string.strip():
                    warnings.append("发现空字符串: ''")
            
            # 4. 改进的运算符检查
            # 先移除字符串和参数，再检查剩余部分
            temp_formula = formula
            # 移除字符串内容
            temp_formula = re.sub(r"'[^']*'", "STRING", temp_formula)
            # 移除参数内容
            temp_formula = re.sub(r"\[[^\]]+\]", "PARAM", temp_formula)
            
            # 检查是否包含无效字符（更精确的检查）
            # 允许的字符：数字、字母、中文、空格、标点符号、运算符
            valid_pattern = r'^[a-zA-Z0-9\u4e00-\u9fa5\s\(\).,><=+\-*/#%STRINGPARAM]*$'
            if not re.match(valid_pattern, temp_formula):
                # 找出具体的无效字符
                invalid_chars = re.findall(r'[^a-zA-Z0-9\u4e00-\u9fa5\s\(\).,><=+\-*/#%STRINGPARAM]', temp_formula)
                if invalid_chars:
                    unique_chars = list(set(invalid_chars))
                    warnings.append(f"发现特殊字符，请确认是否正确: {', '.join(unique_chars)}")
            
            # 5. 检查基本语法结构
            if '如果' in formula:
                if_count = formula.count('如果')
                then_count = formula.count('那么')
                end_count = formula.count('结束')
                
                if if_count != then_count:
                    errors.append(f"'如果'和'那么'数量不匹配: 如果({if_count}) vs 那么({then_count})")
                
                if if_count != end_count:
                    errors.append(f"'如果'和'结束'数量不匹配: 如果({if_count}) vs 结束({end_count})")
            
            # 6. 改进的数字格式检查
            # 更精确的数字匹配，支持整数、小数、科学记数法
            number_pattern = r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b'
            numbers = re.findall(number_pattern, formula)
            for num in numbers:
                try:
                    float(num)
                except ValueError:
                    errors.append(f"数字格式错误: {num}")
            
            # 7. 参数存在性检查（检查参数是否在系统中定义）
            try:
                # 使用缓存的参数列表
                existing_param_names = CalculationSchemeService._get_cached_parameters()
                
                for param in params:
                    param_name = param.strip()
                    # 检查精确匹配
                    if param_name not in existing_param_names:
                        # 检查大小写不一致的情况
                        similar_params = [p for p in existing_param_names if p.lower() == param_name.lower()]
                        if similar_params:
                            warnings.append(f"参数 '[{param_name}]' 大小写可能不正确，系统中存在: {similar_params}")
                        else:
                            errors.append(f"参数 '[{param_name}]' 在系统中不存在或未启用")
            except Exception as db_error:
                warnings.append(f"无法验证参数存在性: {str(db_error)}")
            
            # 8. 格式建议
            if formula and not re.search(r'\s', formula):
                warnings.append("建议在运算符前后添加空格以提高可读性")
            
            # 9. 检查连续运算符
            consecutive_operators = re.findall(r'[+\-*/>=<]{2,}', formula)
            if consecutive_operators:
                errors.append(f"发现连续的运算符: {', '.join(set(consecutive_operators))}")
            
            # 10. 检查运算符前后的空格（仅警告）
            operators_without_space = re.findall(r'\S[+\-*/>=<]\S', formula)
            if operators_without_space:
                warnings.append("建议在运算符前后添加空格以提高可读性")
            
            is_valid = len(errors) == 0
            
            result = {
                'is_valid': is_valid,
                'error': '; '.join(errors) if errors else None,
                'warnings': warnings,
                'statistics': {
                    'param_count': param_count,
                    'string_count': string_count,
                    'line_count': line_count,
                    'char_count': len(formula)
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': f"验证过程出错: {str(e)}",
                'warnings': [],
                'statistics': {
                    'param_count': 0,
                    'string_count': 0,
                    'line_count': 0,
                    'char_count': 0
                }
            }
    
    @staticmethod
    def get_calculation_scheme_options():
        """获取计算方案选项"""
        # 设置schema
        CalculationSchemeService._set_schema()
        
        try:
            from app.models.basic_data import CalculationScheme
            
            # 使用ORM查询，自动应用租户上下文
            schemes = CalculationScheme.query.filter_by(is_enabled=True).order_by(
                CalculationScheme.sort_order, 
                CalculationScheme.scheme_name
            ).all()
            
            return [
                {
                    'value': str(scheme.id),
                    'label': scheme.scheme_name,
                    'category': scheme.scheme_category,
                    'description': scheme.description or '',
                    'formula': scheme.scheme_formula or ''
                }
                for scheme in schemes
            ]
        except Exception as e:
            raise ValueError(f"获取计算方案选项失败: {str(e)}")

    @staticmethod
    def get_calculation_schemes_by_category(category):
        """根据分类获取计算方案列表"""
        # 设置schema
        CalculationSchemeService._set_schema()
        
        try:
            from app.models.basic_data import CalculationScheme
            
            # 使用ORM查询，自动应用租户上下文
            schemes = CalculationScheme.query.filter_by(
                scheme_category=category,
                is_enabled=True
            ).order_by(
                CalculationScheme.sort_order, 
                CalculationScheme.scheme_name
            ).all()
            
            return [
                {
                    'value': str(scheme.id),
                    'label': scheme.scheme_name,
                    'category': scheme.scheme_category,
                    'description': scheme.description or '',
                    'formula': scheme.scheme_formula or ''
                }
                for scheme in schemes
            ]
        except Exception as e:
            raise ValueError(f"获取{category}分类计算方案失败: {str(e)}")


class DepartmentService:
    """部门管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in DepartmentService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_departments(page=1, per_page=20, search=None):
        """获取部门列表"""
        # 设置schema
        DepartmentService._set_schema()
        
        query = db.session.query(Department)
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                Department.dept_code.ilike(search_pattern),
                Department.dept_name.ilike(search_pattern),
                Department.description.ilike(search_pattern)
            ))
        
        # 只查询启用的记录
        query = query.filter(Department.is_enabled == True)
        
        # 排序
        query = query.order_by(Department.sort_order, Department.dept_name)
        
        # 分页
        total = query.count()
        departments = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'departments': [dept.to_dict(include_user_info=True) for dept in departments],
            'total': total,
            'current_page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def get_department(dept_id):
        """获取部门详情"""
        # 设置schema
        DepartmentService._set_schema()
        
        department = db.session.query(Department).get(uuid.UUID(dept_id))
        if not department:
            raise ValueError("部门不存在")
        return department.to_dict(include_user_info=True)
    
    @staticmethod
    def create_department(data, created_by):
        """创建部门"""
        # 设置schema
        DepartmentService._set_schema()
        
        try:
            # 生成部门编号
            if not data.get('dept_code'):
                data['dept_code'] = Department.generate_dept_code()
            
            # 验证上级部门
            parent_id = None
            if data.get('parent_id'):
                parent_id = uuid.UUID(data['parent_id'])
                parent_dept = db.session.query(Department).get(parent_id)
                if not parent_dept:
                    raise ValueError("上级部门不存在")
                if not parent_dept.is_enabled:
                    raise ValueError("上级部门未启用")
            
            # 创建部门对象
            department = Department(
                dept_code=data['dept_code'],
                dept_name=data['dept_name'],
                parent_id=parent_id,
                is_blown_film=data.get('is_blown_film', False),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            db.session.add(department)
            db.session.commit()
            
            return department.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            db.session.rollback()
            if 'dept_code' in str(e):
                raise ValueError("部门编号已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建部门失败: {str(e)}")
    
    @staticmethod
    def update_department(dept_id, data, updated_by):
        """更新部门"""
        # 设置schema
        DepartmentService._set_schema()
        
        try:
            department = db.session.query(Department).get(uuid.UUID(dept_id))
            if not department:
                raise ValueError("部门不存在")
            
            # 验证上级部门
            if 'parent_id' in data:
                parent_id = None
                if data['parent_id']:
                    parent_id = uuid.UUID(data['parent_id'])
                    # 防止循环引用
                    if parent_id == department.id:
                        raise ValueError("不能将自己设置为上级部门")
                    
                    parent_dept = db.session.query(Department).get(parent_id)
                    if not parent_dept:
                        raise ValueError("上级部门不存在")
                    if not parent_dept.is_enabled:
                        raise ValueError("上级部门未启用")
                    
                    # 检查是否会形成循环引用
                    current_parent = parent_dept
                    while current_parent:
                        if current_parent.parent_id == department.id:
                            raise ValueError("设置此上级部门会形成循环引用")
                        current_parent = current_parent.parent
                
                data['parent_id'] = parent_id
            
            # 更新字段
            update_fields = ['dept_name', 'parent_id', 'is_blown_film', 'description', 'sort_order', 'is_enabled']
            
            for field in update_fields:
                if field in data:
                    setattr(department, field, data[field])
            
            department.updated_by = uuid.UUID(updated_by)
            department.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return department.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            db.session.rollback()
            if 'dept_code' in str(e):
                raise ValueError("部门编号已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"更新部门失败: {str(e)}")
    
    @staticmethod
    def delete_department(dept_id):
        """删除部门"""
        # 设置schema
        DepartmentService._set_schema()
        
        try:
            department = db.session.query(Department).get(uuid.UUID(dept_id))
            if not department:
                raise ValueError("部门不存在")
            
            # 检查是否有子部门
            children_count = db.session.query(Department).filter(Department.parent_id == department.id).count()
            if children_count > 0:
                raise ValueError("存在子部门，无法删除")
            
            db.session.delete(department)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"删除部门失败: {str(e)}")
    
    @staticmethod
    def batch_update_departments(updates, updated_by):
        """批量更新部门"""
        # 设置schema
        DepartmentService._set_schema()
        
        try:
            updated_departments = []
            
            for update_data in updates:
                dept_id = update_data.get('id')
                if not dept_id:
                    continue
                
                department = db.session.query(Department).get(uuid.UUID(dept_id))
                if not department:
                    continue
                
                # 更新字段
                update_fields = ['dept_name', 'is_blown_film', 'description', 'sort_order', 'is_enabled']
                for field in update_fields:
                    if field in update_data:
                        setattr(department, field, update_data[field])
                
                department.updated_by = uuid.UUID(updated_by)
                department.updated_at = datetime.utcnow()
                updated_departments.append(department)
            
            db.session.commit()
            
            return [dept.to_dict(include_user_info=True) for dept in updated_departments]
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"批量更新部门失败: {str(e)}")
    
    @staticmethod
    def get_department_options():
        """获取部门选项数据"""
        # 设置schema
        DepartmentService._set_schema()
        
        try:
            departments = Department.get_enabled_list()
            return [
                {
                    'value': str(dept.id),
                    'label': dept.dept_name,
                    'code': dept.dept_code
                }
                for dept in departments
            ]
        except Exception as e:
            raise ValueError(f"获取部门选项失败: {str(e)}")
    
    @staticmethod
    def get_department_tree():
        """获取部门树形结构"""
        # 设置schema
        DepartmentService._set_schema()
        
        try:
            return Department.get_department_tree()
        except Exception as e:
            raise ValueError(f"获取部门树形结构失败: {str(e)}")


class PositionService:
    """职位管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in PositionService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_positions(page=1, per_page=20, search=None, department_id=None):
        """获取职位列表"""
        # 设置schema
        PositionService._set_schema()
        
        try:
            # 构建查询
            query = db.session.query(Position)
            
            # 搜索条件
            if search:
                query = query.filter(Position.position_name.like(f'%{search}%'))
            
            # 部门筛选
            if department_id:
                query = query.filter(Position.department_id == uuid.UUID(department_id))
            
            # 排序
            query = query.order_by(Position.sort_order, Position.position_name)
            
            # 分页
            total = query.count()
            positions = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 添加用户信息
            for position in positions:
                if position.created_by:
                    creator = db.session.query(User).get(position.created_by)
                    position.created_by_name = creator.get_full_name() if creator else '未知用户'
                if position.updated_by:
                    updater = db.session.query(User).get(position.updated_by)
                    position.updated_by_name = updater.get_full_name() if updater else '未知用户'
            
            return {
                'positions': [pos.to_dict(include_user_info=True) for pos in positions],
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取职位列表失败: {str(e)}")
    
    @staticmethod
    def get_position(position_id):
        """获取职位详情"""
        try:
            position = db.session.query(Position).get(uuid.UUID(position_id))
            if not position:
                raise ValueError("职位不存在")
            
            # 添加用户信息
            if position.created_by:
                creator = db.session.query(User).get(position.created_by)
                position.created_by_name = creator.get_full_name() if creator else '未知用户'
            if position.updated_by:
                updater = db.session.query(User).get(position.updated_by)
                position.updated_by_name = updater.get_full_name() if updater else '未知用户'
            
            return position.to_dict(include_user_info=True)
            
        except Exception as e:
            raise ValueError(f"获取职位详情失败: {str(e)}")
    
    @staticmethod
    def create_position(data, created_by):
        """创建职位"""
        try:
            # 验证部门
            department = db.session.query(Department).get(uuid.UUID(data['department_id']))
            if not department:
                raise ValueError("部门不存在")
            if not department.is_enabled:
                raise ValueError("部门未启用")
            
            # 验证上级职位
            parent_position_id = None
            if data.get('parent_position_id'):
                parent_position_id = uuid.UUID(data['parent_position_id'])
                parent_position = db.session.query(Position).get(parent_position_id)
                if not parent_position:
                    raise ValueError("上级职位不存在")
                if not parent_position.is_enabled:
                    raise ValueError("上级职位未启用")
            
            # 创建职位对象
            position = Position(
                position_name=data['position_name'],
                department_id=uuid.UUID(data['department_id']),
                parent_position_id=parent_position_id,
                hourly_wage=data.get('hourly_wage'),
                standard_pass_rate=data.get('standard_pass_rate'),
                is_supervisor=data.get('is_supervisor', False),
                is_machine_operator=data.get('is_machine_operator', False),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            db.session.add(position)
            db.session.commit()
            
            # 添加用户信息
            creator = db.session.query(User).get(position.created_by)
            position.created_by_name = creator.get_full_name() if creator else '未知用户'
            
            return position.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建职位失败: {str(e)}")
    
    @staticmethod
    def update_position(position_id, data, updated_by):
        """更新职位"""
        try:
            position = db.session.query(Position).get(uuid.UUID(position_id))
            if not position:
                raise ValueError("职位不存在")
            
            # 验证部门
            if 'department_id' in data:
                department = db.session.query(Department).get(uuid.UUID(data['department_id']))
                if not department:
                    raise ValueError("部门不存在")
                if not department.is_enabled:
                    raise ValueError("部门未启用")
            
            # 验证上级职位
            if 'parent_position_id' in data:
                parent_position_id = None
                if data['parent_position_id']:
                    parent_position_id = uuid.UUID(data['parent_position_id'])
                    # 防止循环引用
                    if parent_position_id == position.id:
                        raise ValueError("不能将自己设置为上级职位")
                    
                    parent_position = db.session.query(Position).get(parent_position_id)
                    if not parent_position:
                        raise ValueError("上级职位不存在")
                    if not parent_position.is_enabled:
                        raise ValueError("上级职位未启用")
                    
                    # 检查是否会形成循环引用
                    current_parent = parent_position
                    while current_parent:
                        if current_parent.parent_position_id == position.id:
                            raise ValueError("设置此上级职位会形成循环引用")
                        current_parent = current_parent.parent_position
                
                data['parent_position_id'] = parent_position_id
            
            # 更新字段
            update_fields = [
                'position_name', 'department_id', 'parent_position_id', 
                'hourly_wage', 'standard_pass_rate', 'is_supervisor', 
                'is_machine_operator', 'description', 'sort_order', 'is_enabled'
            ]
            
            for field in update_fields:
                if field in data:
                    setattr(position, field, data[field])
            
            position.updated_by = uuid.UUID(updated_by)
            position.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # 添加用户信息
            if position.updated_by:
                updater = db.session.query(User).get(position.updated_by)
                position.updated_by_name = updater.get_full_name() if updater else '未知用户'
            
            return position.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"更新职位失败: {str(e)}")
    
    @staticmethod
    def delete_position(position_id):
        """删除职位"""
        try:
            position = db.session.query(Position).get(uuid.UUID(position_id))
            if not position:
                raise ValueError("职位不存在")
            
            # 检查是否有下级职位
            children_count = db.session.query(Position).filter(Position.parent_position_id == position.id).count()
            if children_count > 0:
                raise ValueError("存在下级职位，无法删除")
            
            db.session.delete(position)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"删除职位失败: {str(e)}")
    
    @staticmethod
    def get_position_options(department_id=None):
        """获取职位选项数据"""
        try:
            query = db.session.query(Position).filter(Position.is_enabled == True)
            
            # 按部门筛选
            if department_id:
                query = query.filter(Position.department_id == uuid.UUID(department_id))
            
            positions = query.order_by(Position.sort_order, Position.position_name).all()
            
            return [
                {
                    'value': str(pos.id),
                    'label': pos.position_name,
                    'department_id': str(pos.department_id),
                    'department_name': pos.department.dept_name if pos.department else None
                }
                for pos in positions
            ]
        except Exception as e:
            raise ValueError(f"获取职位选项失败: {str(e)}")
    
    @staticmethod
    def get_department_options():
        """获取部门选项数据"""
        try:
            return DepartmentService.get_department_options()
        except Exception as e:
            raise ValueError(f"获取部门选项失败: {str(e)}")


class EmployeeService:
    """员工管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in EmployeeService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_employees(page=1, per_page=20, search=None, department_id=None, position_id=None, employment_status=None):
        """获取员工列表"""
        # 设置schema
        EmployeeService._set_schema()
        
        try:
            # 构建查询
            query = db.session.query(Employee)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    Employee.employee_id.ilike(search_pattern),
                    Employee.employee_name.ilike(search_pattern),
                    Employee.mobile_phone.ilike(search_pattern),
                    Employee.id_number.ilike(search_pattern)
                ))
            
            # 部门筛选
            if department_id:
                query = query.filter(Employee.department_id == uuid.UUID(department_id))
            
            # 职位筛选
            if position_id:
                query = query.filter(Employee.position_id == uuid.UUID(position_id))
            
            # 在职状态筛选
            if employment_status:
                query = query.filter(Employee.employment_status == employment_status)
            
            # 排序
            query = query.order_by(Employee.sort_order, Employee.employee_name)
            
            # 分页
            total = query.count()
            employees = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 添加用户信息
            for employee in employees:
                if employee.created_by:
                    creator = db.session.query(User).get(employee.created_by)
                    employee.created_by_name = creator.get_full_name() if creator else '未知用户'
                if employee.updated_by:
                    updater = db.session.query(User).get(employee.updated_by)
                    employee.updated_by_name = updater.get_full_name() if updater else '未知用户'
            
            return {
                'employees': [emp.to_dict(include_user_info=True) for emp in employees],
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取员工列表失败: {str(e)}")
    
    @staticmethod
    def get_employee(employee_id):
        """获取员工详情"""
        try:
            employee = db.session.query(Employee).get(uuid.UUID(employee_id))
            if not employee:
                raise ValueError("员工不存在")
            
            # 添加用户信息
            if employee.created_by:
                creator = db.session.query(User).get(employee.created_by)
                employee.created_by_name = creator.get_full_name() if creator else '未知用户'
            if employee.updated_by:
                updater = db.session.query(User).get(employee.updated_by)
                employee.updated_by_name = updater.get_full_name() if updater else '未知用户'
            
            return employee.to_dict(include_user_info=True)
            
        except Exception as e:
            raise ValueError(f"获取员工详情失败: {str(e)}")
    
    @staticmethod
    def get_employee_options():
        """获取员工选项列表"""
        try:
            employees = Employee.get_enabled_list()
            return {
                'success': True,
                'data': [
                    {
                        'id': str(emp.id),
                        'employee_id': emp.employee_id,
                        'employee_name': emp.employee_name,
                        'department_name': emp.department.dept_name if emp.department else None,
                        'position_name': emp.position.position_name if emp.position else None
                    }
                    for emp in employees
                ]
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'获取员工选项失败: {str(e)}'
            }

    @staticmethod
    def get_employment_status_options():
        """获取在职状态选项"""
        return [
            {'value': 'trial', 'label': '试用'},
            {'value': 'active', 'label': '在职'},
            {'value': 'leave', 'label': '离职'}
        ]

    @staticmethod
    def get_business_type_options():
        """获取业务类型选项"""
        return [
            {'value': 'salesperson', 'label': '业务员'},
            {'value': 'purchaser', 'label': '采购员'},
            {'value': 'comprehensive', 'label': '综合'},
            {'value': 'delivery_person', 'label': '送货员'}
        ]

    @staticmethod
    def get_gender_options():
        """获取性别选项"""
        return [
            {'value': 'male', 'label': '男'},
            {'value': 'female', 'label': '女'},
            {'value': 'confidential', 'label': '保密'}
        ]

    @staticmethod
    def get_evaluation_level_options():
        """获取评量流程级别选项"""
        return [
            {'value': 'finance', 'label': '财务'},
            {'value': 'technology', 'label': '工艺'},
            {'value': 'supply', 'label': '供应'},
            {'value': 'marketing', 'label': '营销'}
        ]

    @staticmethod
    def auto_fill_department_from_position(position_id):
        """根据职位自动填入部门"""
        try:
            if not position_id:
                return None
                
            position = Position.query.get(position_id)
            if position and position.department_id:
                return str(position.department_id)
            
            return None
        except Exception:
            return None

    @staticmethod
    def create_employee(data, created_by):
        """创建员工"""
        try:
            # 如果提供了职位，自动填入部门
            if data.get('position_id'):
                department_id = EmployeeService.auto_fill_department_from_position(data['position_id'])
                if department_id:
                    data['department_id'] = department_id

            # 生成员工工号
            if not data.get('employee_id'):
                data['employee_id'] = Employee.generate_employee_id()

            # 验证数据
            if Employee.query.filter_by(employee_id=data['employee_id']).first():
                return {
                    'success': False,
                    'message': '员工工号已存在'
                }

            # 创建员工对象
            employee = Employee(
                employee_id=data['employee_id'],
                employee_name=data['employee_name'],
                position_id=data.get('position_id'),
                department_id=data.get('department_id'),
                employment_status=data.get('employment_status', 'trial'),
                business_type=data.get('business_type'),
                gender=data.get('gender'),
                mobile_phone=data.get('mobile_phone'),
                landline_phone=data.get('landline_phone'),
                emergency_phone=data.get('emergency_phone'),
                hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else None,
                birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
                circulation_card_id=data.get('circulation_card_id'),
                workshop_id=data.get('workshop_id'),
                id_number=data.get('id_number'),
                salary_1=data.get('salary_1', 0),
                salary_2=data.get('salary_2', 0),
                salary_3=data.get('salary_3', 0),
                salary_4=data.get('salary_4', 0),
                native_place=data.get('native_place'),
                ethnicity=data.get('ethnicity'),
                province=data.get('province'),
                city=data.get('city'),
                district=data.get('district'),
                street=data.get('street'),
                birth_address=data.get('birth_address'),
                archive_location=data.get('archive_location'),
                household_registration=data.get('household_registration'),
                evaluation_level=data.get('evaluation_level'),
                leave_date=datetime.strptime(data['leave_date'], '%Y-%m-%d').date() if data.get('leave_date') else None,
                seniority_wage=data.get('seniority_wage'),
                assessment_wage=data.get('assessment_wage'),
                contract_start_date=datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date() if data.get('contract_start_date') else None,
                contract_end_date=datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date() if data.get('contract_end_date') else None,
                expiry_warning_date=datetime.strptime(data['expiry_warning_date'], '%Y-%m-%d').date() if data.get('expiry_warning_date') else None,
                ufida_code=data.get('ufida_code'),
                kingdee_push=data.get('kingdee_push', False),
                remarks=data.get('remarks'),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=created_by
            )

            db.session.add(employee)
            db.session.commit()

            return {
                'success': True,
                'message': '员工创建成功',
                'data': employee.to_dict(include_user_info=True)
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'创建员工失败: {str(e)}'
            }

    @staticmethod
    def update_employee(employee_id, data, updated_by):
        """更新员工"""
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                return {
                    'success': False,
                    'message': '员工不存在'
                }

            # 如果修改了职位，自动更新部门
            if 'position_id' in data and data['position_id'] != str(employee.position_id):
                department_id = EmployeeService.auto_fill_department_from_position(data['position_id'])
                if department_id:
                    data['department_id'] = department_id

            # 更新字段
            for key, value in data.items():
                if key in ['hire_date', 'birth_date', 'leave_date', 'contract_start_date', 'contract_end_date', 'expiry_warning_date']:
                    if value:
                        setattr(employee, key, datetime.strptime(value, '%Y-%m-%d').date())
                    else:
                        setattr(employee, key, None)
                elif hasattr(employee, key):
                    setattr(employee, key, value)

            employee.updated_by = updated_by
            db.session.commit()

            return {
                'success': True,
                'message': '员工更新成功',
                'data': employee.to_dict(include_user_info=True)
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新员工失败: {str(e)}'
            }

    @staticmethod
    def delete_employee(employee_id):
        """删除员工"""
        try:
            employee = db.session.query(Employee).get(uuid.UUID(employee_id))
            if not employee:
                raise ValueError("员工不存在")
            
            db.session.delete(employee)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"删除员工失败: {str(e)}")
    
    @staticmethod
    def batch_update_employees(updates, updated_by):
        """批量更新员工"""
        try:
            updated_employees = []
            
            for update_data in updates:
                emp_id = update_data.get('id')
                if not emp_id:
                    continue
                
                employee = db.session.query(Employee).get(uuid.UUID(emp_id))
                if not employee:
                    continue
                
                # 更新指定字段
                update_fields = ['employment_status', 'sort_order', 'is_enabled']
                for field in update_fields:
                    if field in update_data:
                        setattr(employee, field, update_data[field])
                
                employee.updated_by = uuid.UUID(updated_by)
                employee.updated_at = datetime.utcnow()
                updated_employees.append(employee)
            
            db.session.commit()
            
            return [emp.to_dict(include_user_info=True) for emp in updated_employees]
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"批量更新员工失败: {str(e)}")


class WarehouseService:
    """仓库管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in WarehouseService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_warehouses(page=1, per_page=20, search=None, warehouse_type=None, parent_warehouse_id=None):
        """获取仓库列表"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            
            # 构建查询
            query = db.session.query(Warehouse)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    Warehouse.warehouse_code.ilike(search_pattern),
                    Warehouse.warehouse_name.ilike(search_pattern),
                    Warehouse.description.ilike(search_pattern)
                ))
            
            # 仓库类型筛选
            if warehouse_type:
                query = query.filter(Warehouse.warehouse_type == warehouse_type)
            
            # 上级仓库筛选
            if parent_warehouse_id:
                query = query.filter(Warehouse.parent_warehouse_id == uuid.UUID(parent_warehouse_id))
            
            # 排序
            query = query.order_by(Warehouse.sort_order, Warehouse.warehouse_name)
            
            # 分页
            total = query.count()
            warehouses = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'warehouses': [warehouse.to_dict(include_user_info=True) for warehouse in warehouses],
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取仓库列表失败: {str(e)}")
    
    @staticmethod
    def get_warehouse(warehouse_id):
        """获取仓库详情"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            
            warehouse = db.session.query(Warehouse).get(uuid.UUID(warehouse_id))
            if not warehouse:
                raise ValueError("仓库不存在")
            
            return warehouse.to_dict(include_user_info=True)
            
        except Exception as e:
            raise ValueError(f"获取仓库详情失败: {str(e)}")
    
    @staticmethod
    def create_warehouse(data, created_by):
        """创建仓库"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            
            # 生成仓库编号，最多重试3次
            max_retries = 3
            warehouse_code = None
            
            for attempt in range(max_retries):
                try:
                    # 每次重试都生成新的编号
                    warehouse_code = Warehouse.generate_warehouse_code()
                    
                    # 验证编号是否已存在
                    existing = db.session.query(Warehouse).filter(
                        Warehouse.warehouse_code == warehouse_code
                    ).first()
                    
                    if existing:
                        if attempt < max_retries - 1:
                            # 如果编号冲突，继续下一次重试
                            continue
                        else:
                            raise ValueError(f"仓库编号生成失败，请重试")
                    
                    # 编号没有冲突，跳出循环
                    break
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise e
            
            # 验证上级仓库
            parent_warehouse_id = None
            if data.get('parent_warehouse_id'):
                parent_warehouse_id = uuid.UUID(data['parent_warehouse_id'])
                parent_warehouse = db.session.query(Warehouse).get(parent_warehouse_id)
                if not parent_warehouse:
                    raise ValueError("上级仓库不存在")
                if not parent_warehouse.is_enabled:
                    raise ValueError("上级仓库未启用")
            
            # 创建仓库对象
            warehouse = Warehouse(
                warehouse_code=warehouse_code,
                warehouse_name=data['warehouse_name'],
                warehouse_type=data.get('warehouse_type'),
                parent_warehouse_id=parent_warehouse_id,
                accounting_method=data.get('accounting_method'),
                circulation_type=data.get('circulation_type', 'on_site_circulation'),
                exclude_from_operations=data.get('exclude_from_operations', False),
                is_abnormal=data.get('is_abnormal', False),
                is_carryover_warehouse=data.get('is_carryover_warehouse', False),
                exclude_from_docking=data.get('exclude_from_docking', False),
                is_in_stocktaking=data.get('is_in_stocktaking', False),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            db.session.add(warehouse)
            db.session.commit()
            
            return warehouse.to_dict(include_user_info=True)
                        
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建仓库失败: {str(e)}")
    
    @staticmethod
    def update_warehouse(warehouse_id, data, updated_by):
        """更新仓库"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            
            warehouse = db.session.query(Warehouse).get(uuid.UUID(warehouse_id))
            if not warehouse:
                raise ValueError("仓库不存在")
            
            # 验证上级仓库
            if 'parent_warehouse_id' in data:
                parent_warehouse_id = None
                if data['parent_warehouse_id']:
                    parent_warehouse_id = uuid.UUID(data['parent_warehouse_id'])
                    # 防止循环引用
                    if parent_warehouse_id == warehouse.id:
                        raise ValueError("不能将自己设置为上级仓库")
                    
                    parent_warehouse = db.session.query(Warehouse).get(parent_warehouse_id)
                    if not parent_warehouse:
                        raise ValueError("上级仓库不存在")
                    if not parent_warehouse.is_enabled:
                        raise ValueError("上级仓库未启用")
                    
                    # 检查是否会形成循环引用
                    current_parent = parent_warehouse
                    while current_parent:
                        if current_parent.parent_warehouse_id == warehouse.id:
                            raise ValueError("设置此上级仓库会形成循环引用")
                        current_parent = current_parent.parent_warehouse
                
                data['parent_warehouse_id'] = parent_warehouse_id
            
            # 更新字段
            update_fields = [
                'warehouse_name', 'warehouse_type', 'parent_warehouse_id', 
                'accounting_method', 'circulation_type',
                'exclude_from_operations', 'is_abnormal', 'is_carryover_warehouse',
                'exclude_from_docking', 'is_in_stocktaking', 'description', 
                'sort_order', 'is_enabled'
            ]
            
            for field in update_fields:
                if field in data:
                    setattr(warehouse, field, data[field])
            
            warehouse.updated_by = uuid.UUID(updated_by)
            warehouse.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return warehouse.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            db.session.rollback()
            if 'warehouse_code' in str(e):
                raise ValueError("仓库编号已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"更新仓库失败: {str(e)}")
    
    @staticmethod
    def delete_warehouse(warehouse_id):
        """删除仓库"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            
            warehouse = db.session.query(Warehouse).get(uuid.UUID(warehouse_id))
            if not warehouse:
                raise ValueError("仓库不存在")
            
            # 检查是否有子仓库
            children_count = db.session.query(Warehouse).filter(Warehouse.parent_warehouse_id == warehouse.id).count()
            if children_count > 0:
                raise ValueError("存在子仓库，无法删除")
            
            # 这里可以添加其他业务检查，比如检查是否有库存记录等
            
            db.session.delete(warehouse)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"删除仓库失败: {str(e)}")
    
    @staticmethod
    def batch_update_warehouses(updates, updated_by):
        """批量更新仓库"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            
            updated_warehouses = []
            
            for update_data in updates:
                warehouse_id = update_data.get('id')
                if not warehouse_id:
                    continue
                
                warehouse = db.session.query(Warehouse).get(uuid.UUID(warehouse_id))
                if not warehouse:
                    continue
                
                # 更新指定字段
                update_fields = ['sort_order', 'is_enabled']
                for field in update_fields:
                    if field in update_data:
                        setattr(warehouse, field, update_data[field])
                
                warehouse.updated_by = uuid.UUID(updated_by)
                warehouse.updated_at = datetime.utcnow()
                updated_warehouses.append(warehouse)
            
            db.session.commit()
            
            return [warehouse.to_dict(include_user_info=True) for warehouse in updated_warehouses]
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"批量更新仓库失败: {str(e)}")
    
    @staticmethod
    def get_warehouse_options():
        """获取仓库选项数据"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            
            warehouses = Warehouse.get_enabled_list()
            return [
                {
                    'value': str(warehouse.id),
                    'label': warehouse.warehouse_name,
                    'code': warehouse.warehouse_code,
                    'type': warehouse.warehouse_type
                }
                for warehouse in warehouses
            ]
        except Exception as e:
            raise ValueError(f"获取仓库选项失败: {str(e)}")
    
    @staticmethod
    def get_warehouse_tree():
        """获取仓库树形结构"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            return Warehouse.get_warehouse_tree()
        except Exception as e:
            raise ValueError(f"获取仓库树形结构失败: {str(e)}")
    
    @staticmethod
    def get_warehouse_types():
        """获取仓库类型选项"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            return Warehouse.get_warehouse_types()
        except Exception as e:
            raise ValueError(f"获取仓库类型失败: {str(e)}")
    
    @staticmethod
    def get_accounting_methods():
        """获取核算方式选项"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            return Warehouse.get_accounting_methods()
        except Exception as e:
            raise ValueError(f"获取核算方式失败: {str(e)}")
    
    @staticmethod
    def get_circulation_types():
        """获取流转类型选项"""
        # 设置schema
        WarehouseService._set_schema()
        
        try:
            from app.models.basic_data import Warehouse
            return Warehouse.get_circulation_types()
        except Exception as e:
            raise ValueError(f"获取流转类型失败: {str(e)}")


class BagTypeService:
    """袋型管理服务"""
    
    @staticmethod
    def get_bag_types(page=1, per_page=20, search=None, is_enabled=None):
        """获取袋型列表"""
        try:
            from app.models.basic_data import BagType, BagTypeStructure, CalculationScheme
            
            # 构建查询
            query = db.session.query(BagType)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    BagType.bag_type_name.ilike(search_pattern),
                    BagType.spec_expression.ilike(search_pattern),
                    BagType.description.ilike(search_pattern)
                ))
            
            # 启用状态筛选
            if is_enabled is not None:
                query = query.filter(BagType.is_enabled == is_enabled)
            
            # 排序
            query = query.order_by(BagType.sort_order, BagType.bag_type_name)
            
            # 分页
            total = query.count()
            bag_types = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 为每个袋型获取结构信息
            bag_types_with_structures = []
            for bag_type in bag_types:
                bag_type_dict = bag_type.to_dict(include_user_info=True)
                
                # 获取该袋型的结构列表
                structures = db.session.query(BagTypeStructure).filter(
                    BagTypeStructure.bag_type_id == bag_type.id
                ).order_by(BagTypeStructure.sort_order, BagTypeStructure.created_at).all()
                
                # 获取计算方案信息的辅助函数
                def get_scheme_info(scheme_id):
                    if scheme_id:
                        scheme = db.session.query(CalculationScheme).get(scheme_id)
                        if scheme:
                            return {
                                'id': str(scheme.id),
                                'name': scheme.scheme_name,
                                'formula': scheme.scheme_formula
                            }
                    return None
                
                bag_type_dict['structures'] = []
                for structure in structures:
                    # 获取创建人信息
                    created_by_name = None
                    if structure.created_by:
                        from app.models.user import User
                        creator = db.session.query(User).get(structure.created_by)
                        created_by_name = creator.get_full_name() if creator else '未知用户'
                    
                    structure_info = {
                        'id': str(structure.id),
                        'structure_name': structure.structure_name,
                        'image_url': structure.image_url,
                        'sort_order': structure.sort_order,
                        'structure_expression': get_scheme_info(structure.structure_expression_id),
                        'expand_length_formula': get_scheme_info(structure.expand_length_formula_id),
                        'expand_width_formula': get_scheme_info(structure.expand_width_formula_id),
                        'material_length_formula': get_scheme_info(structure.material_length_formula_id),
                        'material_width_formula': get_scheme_info(structure.material_width_formula_id),
                        'single_piece_width_formula': get_scheme_info(structure.single_piece_width_formula_id),
                        'created_at': structure.created_at.isoformat() if structure.created_at else None,
                        'created_by_name': created_by_name
                    }
                    bag_type_dict['structures'].append(structure_info)
                
                bag_types_with_structures.append(bag_type_dict)
            
            return {
                'bag_types': bag_types_with_structures,
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取袋型列表失败: {str(e)}")
    
    @staticmethod
    def get_bag_type(bag_type_id):
        """获取袋型详情"""
        try:
            from app.models.basic_data import BagType
            
            bag_type = db.session.query(BagType).get(uuid.UUID(bag_type_id))
            if not bag_type:
                raise ValueError("袋型不存在")
            
            return bag_type.to_dict(include_user_info=True)
            
        except Exception as e:
            raise ValueError(f"获取袋型详情失败: {str(e)}")
    
    @staticmethod
    def create_bag_type(data, created_by):
        """创建袋型"""
        try:
            from app.models.basic_data import BagType
            
            # 验证袋型名称唯一性
            existing = db.session.query(BagType).filter(
                BagType.bag_type_name == data['bag_type_name']
            ).first()
            if existing:
                raise ValueError("袋型名称已存在")
            
            # 验证单位是否存在
            production_unit_id = None
            sales_unit_id = None
            
            if data.get('production_unit_id'):
                from app.models.basic_data import Unit
                production_unit_id = uuid.UUID(data['production_unit_id'])
                production_unit = db.session.query(Unit).get(production_unit_id)
                if not production_unit:
                    raise ValueError("生产单位不存在")
                if not production_unit.is_enabled:
                    raise ValueError("生产单位未启用")
            
            if data.get('sales_unit_id'):
                from app.models.basic_data import Unit
                sales_unit_id = uuid.UUID(data['sales_unit_id'])
                sales_unit = db.session.query(Unit).get(sales_unit_id)
                if not sales_unit:
                    raise ValueError("销售单位不存在")
                if not sales_unit.is_enabled:
                    raise ValueError("销售单位未启用")
            
            # 创建袋型对象
            bag_type = BagType(
                bag_type_name=data['bag_type_name'],
                spec_expression=data.get('spec_expression'),
                production_unit_id=production_unit_id,
                sales_unit_id=sales_unit_id,
                difficulty_coefficient=data.get('difficulty_coefficient', 0),
                bag_making_unit_price=data.get('bag_making_unit_price', 0),
                sort_order=data.get('sort_order', 0),
                is_roll_film=data.get('is_roll_film', False),
                is_disabled=data.get('is_disabled', False),
                is_custom_spec=data.get('is_custom_spec', False),
                is_strict_bag_type=data.get('is_strict_bag_type', True),
                is_process_judgment=data.get('is_process_judgment', False),
                is_diaper=data.get('is_diaper', False),
                is_woven_bag=data.get('is_woven_bag', False),
                is_label=data.get('is_label', False),
                is_antenna=data.get('is_antenna', False),
                description=data.get('description', ''),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            db.session.add(bag_type)
            db.session.commit()
            
            return bag_type.to_dict(include_user_info=True)
                        
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建袋型失败: {str(e)}")
    
    @staticmethod
    def update_bag_type(bag_type_id, data, updated_by):
        """更新袋型"""
        try:
            from app.models.basic_data import BagType
            
            bag_type = db.session.query(BagType).get(uuid.UUID(bag_type_id))
            if not bag_type:
                raise ValueError("袋型不存在")
            
            # 验证袋型名称唯一性（排除自己）
            if 'bag_type_name' in data and data['bag_type_name'] != bag_type.bag_type_name:
                existing = db.session.query(BagType).filter(
                    BagType.bag_type_name == data['bag_type_name'],
                    BagType.id != bag_type.id
                ).first()
                if existing:
                    raise ValueError("袋型名称已存在")
            
            # 验证单位
            if 'production_unit_id' in data and data['production_unit_id']:
                from app.models.basic_data import Unit
                production_unit = db.session.query(Unit).get(uuid.UUID(data['production_unit_id']))
                if not production_unit:
                    raise ValueError("生产单位不存在")
                if not production_unit.is_enabled:
                    raise ValueError("生产单位未启用")
            
            if 'sales_unit_id' in data and data['sales_unit_id']:
                from app.models.basic_data import Unit
                sales_unit = db.session.query(Unit).get(uuid.UUID(data['sales_unit_id']))
                if not sales_unit:
                    raise ValueError("销售单位不存在")
                if not sales_unit.is_enabled:
                    raise ValueError("销售单位未启用")
            
            # 更新字段
            update_fields = [
                'bag_type_name', 'spec_expression', 'production_unit_id', 'sales_unit_id',
                'difficulty_coefficient', 'bag_making_unit_price', 'sort_order',
                'is_roll_film', 'is_disabled', 'is_custom_spec', 'is_strict_bag_type',
                'is_process_judgment', 'is_diaper', 'is_woven_bag', 'is_label',
                'is_antenna', 'description', 'is_enabled'
            ]
            
            for field in update_fields:
                if field in data:
                    setattr(bag_type, field, data[field])
            
            bag_type.updated_by = uuid.UUID(updated_by)
            bag_type.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return bag_type.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            db.session.rollback()
            if 'bag_type_name' in str(e):
                raise ValueError("袋型名称已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"更新袋型失败: {str(e)}")
    
    @staticmethod
    def delete_bag_type(bag_type_id):
        """删除袋型"""
        try:
            from app.models.basic_data import BagType, BagTypeStructure
            
            bag_type = db.session.query(BagType).get(uuid.UUID(bag_type_id))
            if not bag_type:
                raise ValueError("袋型不存在")
            
            # 先删除相关的袋型结构记录
            db.session.query(BagTypeStructure).filter(
                BagTypeStructure.bag_type_id == bag_type.id
            ).delete()
            
            # 再删除袋型记录
            db.session.delete(bag_type)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"删除袋型失败: {str(e)}")
    
    @staticmethod
    def batch_update_bag_types(updates, updated_by):
        """批量更新袋型"""
        try:
            from app.models.basic_data import BagType
            
            updated_bag_types = []
            
            for update_data in updates:
                bag_type_id = update_data.get('id')
                if not bag_type_id:
                    continue
                
                bag_type = db.session.query(BagType).get(uuid.UUID(bag_type_id))
                if not bag_type:
                    continue
                
                # 更新指定字段
                update_fields = ['sort_order', 'is_enabled']
                for field in update_fields:
                    if field in update_data:
                        setattr(bag_type, field, update_data[field])
                
                bag_type.updated_by = uuid.UUID(updated_by)
                bag_type.updated_at = datetime.utcnow()
                updated_bag_types.append(bag_type)
            
            db.session.commit()
            
            return [bag_type.to_dict(include_user_info=True) for bag_type in updated_bag_types]
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"批量更新袋型失败: {str(e)}")
    
    @staticmethod
    def get_bag_type_options():
        """获取袋型选项数据"""
        try:
            from app.models.basic_data import BagType
            
            bag_types = BagType.get_enabled_list()
            return [
                {
                    'value': str(bag_type.id),
                    'label': bag_type.bag_type_name,
                    'spec_expression': bag_type.spec_expression
                }
                for bag_type in bag_types
            ]
        except Exception as e:
            raise ValueError(f"获取袋型选项失败: {str(e)}")
    
    @staticmethod
    def get_unit_options():
        """获取单位选项数据"""
        try:
            from app.models.basic_data import Unit
            
            units = Unit.get_enabled_list()
            return [
                {
                    'value': str(unit.id),
                    'label': unit.unit_name
                }
                for unit in units
            ]
        except Exception as e:
            raise ValueError(f"获取单位选项失败: {str(e)}")
    
    @staticmethod
    def get_calculation_scheme_options():
        """获取规格表达式选项（从计算方案获取）"""
        try:
            from app.models.basic_data import CalculationScheme
            
            schemes = db.session.query(CalculationScheme).filter(
                CalculationScheme.scheme_category == 'bag_spec',
                CalculationScheme.is_enabled == True
            ).order_by(CalculationScheme.sort_order, CalculationScheme.scheme_name).all()
            
            return [
                {
                    'value': scheme.scheme_formula,
                    'label': scheme.scheme_name,
                    'description': scheme.description
                }
                for scheme in schemes
            ]
        except Exception as e:
            raise ValueError(f"获取规格表达式选项失败: {str(e)}")
    
    @staticmethod
    def get_calculation_schemes_by_category(category):
        """根据分类获取计算方案选项"""
        try:
            from app.models.basic_data import CalculationScheme
            
            schemes = db.session.query(CalculationScheme).filter(
                CalculationScheme.scheme_category == category,
                CalculationScheme.is_enabled == True
            ).order_by(CalculationScheme.sort_order, CalculationScheme.scheme_name).all()
            
            return [
                {
                    'value': str(scheme.id),
                    'label': scheme.scheme_name,
                    'category': scheme.scheme_category,
                    'description': scheme.description or '',
                    'formula': scheme.scheme_formula or ''
                }
                for scheme in schemes
            ]
        except Exception as e:
            raise ValueError(f"获取{category}分类计算方案选项失败: {str(e)}")
    
    @staticmethod
    def get_all_formula_options():
        """获取袋型结构所需的所有公式选项"""
        try:
            return {
                # 结构表达式选项（袋型规格分类）
                'structure_expressions': BagTypeService.get_calculation_schemes_by_category('bag_spec'),
                # 公式选项（袋型公式分类）- 用于展长、展宽、用料长、用料宽、单片宽公式
                'formulas': BagTypeService.get_calculation_schemes_by_category('bag_formula')
            }
        except Exception as e:
            raise ValueError(f"获取袋型结构公式选项失败: {str(e)}")
    
    # ====================== 袋型结构管理 ======================
    
    @staticmethod
    def get_bag_type_structures(bag_type_id):
        """获取袋型结构列表"""
        try:
            from app.models.basic_data import BagTypeStructure
            
            structures = db.session.query(BagTypeStructure).filter(
                BagTypeStructure.bag_type_id == uuid.UUID(bag_type_id)
            ).order_by(BagTypeStructure.sort_order, BagTypeStructure.created_at).all()
            
            return {
                'success': True,
                'data': {
                    'structures': [structure.to_dict(include_user_info=True, include_formulas=True) for structure in structures]
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'获取袋型结构列表失败: {str(e)}'
            }
    
    @staticmethod
    def update_bag_type_structure(structure_id, data, updated_by):
        """更新袋型结构"""
        try:
            from app.models.basic_data import BagTypeStructure
            
            structure = db.session.query(BagTypeStructure).get(uuid.UUID(structure_id))
            if not structure:
                raise ValueError("袋型结构不存在")
            
            # 更新字段
            update_fields = [
                'structure_name', 'structure_expression_id', 'expand_length_formula_id',
                'expand_width_formula_id', 'material_length_formula_id', 
                'material_width_formula_id', 'single_piece_width_formula_id',
                'sort_order', 'image_url'
            ]
            
            for field in update_fields:
                if field in data:
                    value = data[field]
                    if field.endswith('_id') and value:
                        # 处理UUID字段
                        value = uuid.UUID(value)
                    setattr(structure, field, value)
            
            structure.updated_by = uuid.UUID(updated_by)
            structure.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '袋型结构更新成功',
                'data': structure.to_dict(include_user_info=True)
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新袋型结构失败: {str(e)}'
            }
    
    @staticmethod
    def delete_bag_type_structure(structure_id):
        """删除袋型结构"""
        try:
            from app.models.basic_data import BagTypeStructure
            
            structure = db.session.query(BagTypeStructure).get(uuid.UUID(structure_id))
            if not structure:
                raise ValueError("袋型结构不存在")
            
            db.session.delete(structure)
            db.session.commit()
            
            return {
                'success': True,
                'message': '袋型结构删除成功'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'删除袋型结构失败: {str(e)}'
            }
    
    @staticmethod
    def batch_update_bag_type_structures(bag_type_id, structures_data, updated_by):
        """批量更新袋型结构"""
        try:
            from app.models.basic_data import BagTypeStructure, CalculationScheme
            
            # 删除现有结构
            db.session.query(BagTypeStructure).filter(
                BagTypeStructure.bag_type_id == uuid.UUID(bag_type_id)
            ).delete()
            
            # 获取所有有效的计算方案ID，用于验证
            valid_scheme_ids = set()
            schemes = db.session.query(CalculationScheme.id).filter(
                CalculationScheme.is_enabled == True
            ).all()
            valid_scheme_ids = {str(scheme[0]) for scheme in schemes}
            
            # 创建新结构
            for structure_data in structures_data:
                # 处理UUID字段，确保空值转为None，无效值也转为None
                def validate_scheme_id(scheme_id_str):
                    if not scheme_id_str:
                        return None
                    if str(scheme_id_str) not in valid_scheme_ids:
                        # 记录警告但不抛出错误，设为None
                        print(f"警告：计算方案ID {scheme_id_str} 无效，将设为None")
                        return None
                    return uuid.UUID(scheme_id_str)
                
                structure = BagTypeStructure(
                    bag_type_id=uuid.UUID(bag_type_id),
                    structure_name=structure_data.get('structure_name', ''),
                    structure_expression_id=validate_scheme_id(structure_data.get('structure_expression_id')),
                    expand_length_formula_id=validate_scheme_id(structure_data.get('expand_length_formula_id')),
                    expand_width_formula_id=validate_scheme_id(structure_data.get('expand_width_formula_id')),
                    material_length_formula_id=validate_scheme_id(structure_data.get('material_length_formula_id')),
                    material_width_formula_id=validate_scheme_id(structure_data.get('material_width_formula_id')),
                    single_piece_width_formula_id=validate_scheme_id(structure_data.get('single_piece_width_formula_id')),
                    sort_order=structure_data.get('sort_order', 0),
                    image_url=structure_data.get('image_url'),
                    created_by=uuid.UUID(updated_by)
                )
                
                db.session.add(structure)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '袋型结构批量更新成功'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'批量更新袋型结构失败: {str(e)}'
            }