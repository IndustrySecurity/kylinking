# -*- coding: utf-8 -*-
"""
基础档案管理服务层
"""

from app.extensions import db
from app.models.basic_data import Customer, CustomerCategory, Supplier, SupplierCategory, Product, ProductCategory, CalculationParameter, CalculationScheme, Department, Position
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
    def get_customers(page=1, per_page=20, search=None, category_id=None, status=None, 
                     tenant_config=None):
        """获取客户列表"""
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
        customer = db.session.query(Customer).get(uuid.UUID(customer_id))
        if not customer:
            raise ValueError("客户不存在")
        return customer.to_dict()
    
    @staticmethod
    def create_customer(data, created_by):
        """创建客户"""
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
    def get_suppliers(page=1, per_page=20, search=None, category_id=None, status=None):
        """获取供应商列表"""
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
    def get_products(page=1, per_page=20, search=None, category_id=None, status=None, 
                    product_type=None):
        """获取产品列表"""
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
    def get_calculation_parameters(page=1, per_page=20, search=None):
        """获取计算参数列表"""
        from app.models.basic_data import CalculationParameter
        
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
        
        param = CalculationParameter.query.get(uuid.UUID(param_id))
        if not param:
            raise ValueError("计算参数不存在")
        return param.to_dict(include_user_info=True)
    
    @staticmethod
    def create_calculation_parameter(data, created_by):
        """创建计算参数"""
        from app.models.basic_data import CalculationParameter
        
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
        
        try:
            param = CalculationParameter.query.get(uuid.UUID(param_id))
            if not param:
                raise ValueError("计算参数不存在")
            
            db.session.delete(param)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"删除计算参数失败: {str(e)}")
    
    @staticmethod
    def batch_update_calculation_parameters(updates, updated_by):
        """批量更新计算参数"""
        from app.models.basic_data import CalculationParameter
        
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
            
            return results
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"批量更新计算参数失败: {str(e)}")
    
    @staticmethod
    def get_calculation_parameter_options():
        """获取计算参数选项数据"""
        from app.models.basic_data import CalculationParameter
        
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
    
    @staticmethod
    def get_calculation_schemes(page=1, per_page=20, search=None, category=None):
        """获取计算方案列表"""
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
        scheme = db.session.query(CalculationScheme).get(uuid.UUID(scheme_id))
        if not scheme:
            raise ValueError("计算方案不存在")
        return scheme.to_dict()
    
    @staticmethod
    def create_calculation_scheme(data, created_by):
        """创建计算方案"""
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
        try:
            return CalculationScheme.get_scheme_categories()
        except Exception as e:
            raise ValueError(f"获取方案分类失败: {str(e)}")
    
    @staticmethod
    def validate_formula(formula):
        """验证公式语法"""
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
            
            # 4. 检查运算符
            operators = ['如果', '那么', '否则', '结束', '并且', '或者', '>', '<', '>=', '<=', '=', '<>', '+', '-', '*', '/']
            invalid_chars = re.findall(r'[^\w\s\[\]\'"().,><=+\-*/#%\u4e00-\u9fa5]', formula)
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
            
            # 6. 数字格式检查
            numbers = re.findall(r'\b\d+\.?\d*\b', formula)
            for num in numbers:
                try:
                    float(num)
                except ValueError:
                    errors.append(f"数字格式错误: {num}")
            
            # 7. 参数存在性检查（检查参数是否在系统中定义）
            from app.models.basic_data import CalculationParameter
            existing_params = db.session.query(CalculationParameter.parameter_name).filter(
                CalculationParameter.is_enabled == True
            ).all()
            existing_param_names = [p[0] for p in existing_params]
            
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
            
            # 8. 格式建议
            if formula and not re.search(r'\s', formula):
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
        """获取计算方案选项数据"""
        try:
            schemes = CalculationScheme.get_enabled_list()
            return [
                {
                    'value': str(scheme.id),
                    'label': scheme.scheme_name,
                    'category': scheme.scheme_category
                }
                for scheme in schemes
            ]
        except Exception as e:
            raise ValueError(f"获取计算方案选项失败: {str(e)}")


class DepartmentService:
    """部门管理服务"""
    
    @staticmethod
    def get_departments(page=1, per_page=20, search=None):
        """获取部门列表"""
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
        department = db.session.query(Department).get(uuid.UUID(dept_id))
        if not department:
            raise ValueError("部门不存在")
        return department.to_dict(include_user_info=True)
    
    @staticmethod
    def create_department(data, created_by):
        """创建部门"""
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
        try:
            return Department.get_department_tree()
        except Exception as e:
            raise ValueError(f"获取部门树形结构失败: {str(e)}")


class PositionService:
    """职位管理服务"""
    
    @staticmethod
    def get_positions(page=1, per_page=20, search=None, department_id=None):
        """获取职位列表"""
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
                'positions': [pos.to_dict() for pos in positions],
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
            
            return position.to_dict()
            
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
            
            return position.to_dict()
            
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
            
            return position.to_dict()
            
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