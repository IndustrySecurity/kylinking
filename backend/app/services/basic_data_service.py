# -*- coding: utf-8 -*-
"""
基础档案管理服务层
"""

from app.extensions import db
from app.models.basic_data import Customer, CustomerCategory, Supplier, SupplierCategory, Product, ProductCategory, CalculationParameter
from app.services.module_service import TenantConfigService
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime


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