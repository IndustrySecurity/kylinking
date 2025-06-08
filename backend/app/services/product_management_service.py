from sqlalchemy import and_, or_, func, desc
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.basic_data import (
    Product, ProductStructure, ProductCustomerRequirement, 
    ProductProcess, ProductMaterial, ProductQualityIndicator, ProductImage,
    CustomerManagement, BagType, Process, Material
)
from app.models.user import User
from datetime import datetime
import uuid


class ProductManagementService:
    """产品管理服务类"""

    @staticmethod
    def get_products(page=1, per_page=20, search=None, customer_id=None, bag_type_id=None, status=None):
        """获取产品列表"""
        try:
            query = db.session.query(Product)
            
            # 搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    or_(
                        Product.product_code.ilike(search_pattern),
                        Product.product_name.ilike(search_pattern),
                        Product.specification.ilike(search_pattern)
                    )
                )
            
            # 客户筛选
            if customer_id:
                query = query.filter(Product.customer_id == uuid.UUID(customer_id))
            
            # 袋型筛选
            if bag_type_id:
                query = query.filter(Product.bag_type_id == uuid.UUID(bag_type_id))
            
            # 状态筛选
            if status:
                query = query.filter(Product.status == status)
            
            # 排序
            query = query.order_by(desc(Product.created_at))
            
            # 分页
            total = query.count()
            products = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 获取用户信息
            user_ids = set()
            for product in products:
                if product.created_by:
                    user_ids.add(product.created_by)
                if product.updated_by:
                    user_ids.add(product.updated_by)
            
            users = {}
            if user_ids:
                user_list = db.session.query(User).filter(User.id.in_(user_ids)).all()
                users = {str(user.id): user.get_full_name() for user in user_list}
            
            # 转换为字典并添加用户信息
            result_products = []
            for product in products:
                product_dict = product.to_dict()
                product_dict['created_by_name'] = users.get(str(product.created_by), '')
                product_dict['updated_by_name'] = users.get(str(product.updated_by), '')
                result_products.append(product_dict)
            
            return {
                'products': result_products,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取产品列表失败: {str(e)}")

    @staticmethod
    def get_product_detail(product_id):
        """获取产品详情，包含所有子表数据"""
        try:
            from app.models.basic_data import Employee
            
            product = db.session.query(Product).get(uuid.UUID(product_id))
            if not product:
                raise ValueError("产品不存在")
            
            # 获取产品基本信息
            product_dict = product.to_dict()
            
            # 获取业务员信息
            if product.salesperson_id:
                salesperson = db.session.query(Employee).get(product.salesperson_id)
                if salesperson:
                    product_dict['salesperson_name'] = salesperson.employee_name
            
            # 获取创建人信息  
            if product.created_by:
                creator = db.session.query(Employee).get(product.created_by)
                if creator:
                    product_dict['creator_name'] = creator.employee_name
            
            # 获取产品结构
            structures = db.session.query(ProductStructure).filter(
                ProductStructure.product_id == product.id
            ).all()
            product_dict['structures'] = [structure.to_dict() for structure in structures]
            
            # 获取客户需求
            requirements = db.session.query(ProductCustomerRequirement).filter(
                ProductCustomerRequirement.product_id == product.id
            ).all()
            product_dict['customer_requirements'] = [req.to_dict() for req in requirements]
            
            # 获取工序
            processes = db.session.query(ProductProcess).filter(
                ProductProcess.product_id == product.id
            ).order_by(ProductProcess.sort_order).all()
            product_dict['product_processes'] = [process.to_dict() for process in processes]
            
            # 获取材料
            materials = db.session.query(ProductMaterial).filter(
                ProductMaterial.product_id == product.id
            ).order_by(ProductMaterial.sort_order).all()
            product_dict['product_materials'] = [material.to_dict() for material in materials]
            
            # 获取理化指标
            quality_indicators = db.session.query(ProductQualityIndicator).filter(
                ProductQualityIndicator.product_id == product.id
            ).all()
            product_dict['quality_indicators'] = [qi.to_dict() for qi in quality_indicators]
            
            # 获取图片
            images = db.session.query(ProductImage).filter(
                ProductImage.product_id == product.id
            ).order_by(ProductImage.sort_order).all()
            product_dict['product_images'] = [image.to_dict() for image in images]
            
            return product_dict
            
        except Exception as e:
            raise ValueError(f"获取产品详情失败: {str(e)}")

    @staticmethod
    def create_product(data, created_by):
        """创建产品及相关数据"""
        try:
            # 验证必填字段
            if not data.get('product_name'):
                raise ValueError("产品名称不能为空")
            
            # 生成产品编码
            if not data.get('product_code'):
                data['product_code'] = ProductManagementService._generate_product_code()
            
            # 创建产品基本信息
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
                
                # 产品管理界面字段
                customer_id=uuid.UUID(data['customer_id']) if data.get('customer_id') else None,
                bag_type_id=uuid.UUID(data['bag_type_id']) if data.get('bag_type_id') else None,
                salesperson_id=uuid.UUID(data['salesperson_id']) if data.get('salesperson_id') else uuid.UUID(created_by),
                compound_quantity=data.get('compound_quantity', 0),
                small_inventory=data.get('small_inventory', 0),
                large_inventory=data.get('large_inventory', 0),
                international_standard=data.get('international_standard'),
                domestic_standard=data.get('domestic_standard'),
                is_unlimited_quantity=data.get('is_unlimited_quantity', False),
                is_compound_needed=data.get('is_compound_needed', False),
                is_inspection_needed=data.get('is_inspection_needed', False),
                is_public_product=data.get('is_public_product', False),
                is_packaging_needed=data.get('is_packaging_needed', False),
                is_changing=data.get('is_changing', False),
                material_info=data.get('material_info'),
                compound_amount=data.get('compound_amount', 0),
                sales_amount=data.get('sales_amount', 0),
                contract_amount=data.get('contract_amount', 0),
                inventory_amount=data.get('inventory_amount', 0),
                
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
                
                # 系统字段
                status=data.get('status', 'active'),
                is_sellable=data.get('is_sellable', True),
                is_purchasable=data.get('is_purchasable', True),
                is_producible=data.get('is_producible', True),
                
                # 审计字段
                created_by=uuid.UUID(created_by)
            )
            
            db.session.add(product)
            db.session.flush()  # 获取product.id
            
            # 创建产品结构（如果选择了袋型，自动填入结构数据）
            if data.get('bag_type_id') and data.get('auto_fill_structure', True):
                ProductManagementService._create_product_structure_from_bag_type(
                    product.id, data['bag_type_id']
                )
            elif data.get('structure'):
                ProductManagementService._save_product_structure(product.id, data['structure'])
            
            # 创建客户需求
            if data.get('customer_requirements'):
                ProductManagementService._save_customer_requirements(product.id, data['customer_requirements'])
            
            # 创建工序关联
            if data.get('product_processes'):
                ProductManagementService._save_product_processes(product.id, data['product_processes'])
            
            # 创建材料关联
            if data.get('product_materials'):
                ProductManagementService._save_product_materials(product.id, data['product_materials'])
            
            # 创建理化指标
            if data.get('quality_indicators'):
                ProductManagementService._save_quality_indicators(product.id, data['quality_indicators'])
            
            # 创建图片
            if data.get('product_images'):
                ProductManagementService._save_product_images(product.id, data['product_images'])
            
            db.session.commit()
            
            return ProductManagementService.get_product_detail(str(product.id))
            
        except IntegrityError:
            db.session.rollback()
            raise ValueError("产品编码已存在")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建产品失败: {str(e)}")

    @staticmethod
    def update_product(product_id, data, updated_by):
        """更新产品及相关数据"""
        try:
            product = db.session.query(Product).get(uuid.UUID(product_id))
            if not product:
                raise ValueError("产品不存在")
            
            # 更新产品基本字段
            basic_fields = [
                'product_name', 'product_type', 'category_id', 'short_name', 'english_name',
                'brand', 'model', 'specification', 'customer_id', 'bag_type_id', 'salesperson_id',
                'compound_quantity', 'small_inventory', 'large_inventory', 'international_standard',
                'domestic_standard', 'is_unlimited_quantity', 'is_compound_needed', 'is_inspection_needed',
                'is_public_product', 'is_packaging_needed', 'is_changing', 'material_info',
                'compound_amount', 'sales_amount', 'contract_amount', 'inventory_amount',
                'thickness', 'width', 'length', 'material_type', 'transparency', 'tensile_strength',
                'base_unit', 'package_unit', 'conversion_rate', 'net_weight', 'gross_weight',
                'standard_cost', 'standard_price', 'currency', 'safety_stock', 'min_order_qty',
                'max_order_qty', 'status', 'is_sellable', 'is_purchasable', 'is_producible'
            ]
            
            for field in basic_fields:
                if field in data:
                    if field.endswith('_id') and data[field]:
                        setattr(product, field, uuid.UUID(data[field]))
                    else:
                        setattr(product, field, data[field])
            
            product.updated_by = uuid.UUID(updated_by)
            product.updated_at = datetime.utcnow()
            
            # 更新子表数据
            if 'structure' in data:
                ProductManagementService._save_product_structure(product.id, data['structure'])
            
            if 'customer_requirements' in data:
                ProductManagementService._save_customer_requirements(product.id, data['customer_requirements'])
            
            if 'product_processes' in data:
                ProductManagementService._save_product_processes(product.id, data['product_processes'])
            
            if 'product_materials' in data:
                ProductManagementService._save_product_materials(product.id, data['product_materials'])
            
            if 'quality_indicators' in data:
                ProductManagementService._save_quality_indicators(product.id, data['quality_indicators'])
            
            if 'product_images' in data:
                ProductManagementService._save_product_images(product.id, data['product_images'])
            
            db.session.commit()
            
            return ProductManagementService.get_product_detail(str(product.id))
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"更新产品失败: {str(e)}")

    @staticmethod
    def delete_product(product_id):
        """删除产品"""
        try:
            product = db.session.query(Product).get(uuid.UUID(product_id))
            if not product:
                raise ValueError("产品不存在")
            
            # 删除所有子表数据
            db.session.query(ProductStructure).filter(ProductStructure.product_id == product.id).delete()
            db.session.query(ProductCustomerRequirement).filter(ProductCustomerRequirement.product_id == product.id).delete()
            db.session.query(ProductProcess).filter(ProductProcess.product_id == product.id).delete()
            db.session.query(ProductMaterial).filter(ProductMaterial.product_id == product.id).delete()
            db.session.query(ProductQualityIndicator).filter(ProductQualityIndicator.product_id == product.id).delete()
            db.session.query(ProductImage).filter(ProductImage.product_id == product.id).delete()
            
            # 删除产品
            db.session.delete(product)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"删除产品失败: {str(e)}")

    @staticmethod
    def _generate_product_code():
        """生成产品编码"""
        # 设置schema路径
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
        
        # 查找最新的产品编码
        last_product = db.session.query(Product).filter(
            Product.product_code.like('P%')
        ).order_by(desc(Product.product_code)).first()
        
        if last_product:
            try:
                last_num = int(last_product.product_code[1:])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'P{new_num:08d}'

    @staticmethod
    def _create_product_structure_from_bag_type(product_id, bag_type_id):
        """根据袋型自动创建产品结构"""
        try:
            from app.models.basic_data import BagTypeStructure
            
            # 获取袋型结构
            bag_structures = db.session.query(BagTypeStructure).filter(
                BagTypeStructure.bag_type_id == uuid.UUID(bag_type_id)
            ).order_by(BagTypeStructure.sort_order).all()
            
            for bag_structure in bag_structures:
                structure = ProductStructure(
                    product_id=product_id,
                    # 可以从袋型结构中复制一些数据，这里先创建空结构
                    length=0,
                    width=0,
                    height=0
                )
                db.session.add(structure)
                
        except Exception as e:
            raise ValueError(f"从袋型创建产品结构失败: {str(e)}")

    @staticmethod
    def _save_product_structure(product_id, structure_data):
        """保存产品结构"""
        try:
            # 删除现有结构
            db.session.query(ProductStructure).filter(ProductStructure.product_id == product_id).delete()
            
            # 创建新结构
            if structure_data:
                structure = ProductStructure(
                    product_id=product_id,
                    **structure_data
                )
                db.session.add(structure)
                
        except Exception as e:
            raise ValueError(f"保存产品结构失败: {str(e)}")

    @staticmethod
    def _save_customer_requirements(product_id, requirements_data):
        """保存客户需求"""
        try:
            # 删除现有需求
            db.session.query(ProductCustomerRequirement).filter(
                ProductCustomerRequirement.product_id == product_id
            ).delete()
            
            # 创建新需求
            if requirements_data:
                requirement = ProductCustomerRequirement(
                    product_id=product_id,
                    **requirements_data
                )
                db.session.add(requirement)
                
        except Exception as e:
            raise ValueError(f"保存客户需求失败: {str(e)}")

    @staticmethod
    def _save_product_processes(product_id, processes_data):
        """保存产品工序"""
        try:
            # 删除现有工序
            db.session.query(ProductProcess).filter(ProductProcess.product_id == product_id).delete()
            
            # 创建新工序
            for process_data in processes_data:
                product_process = ProductProcess(
                    product_id=product_id,
                    process_id=uuid.UUID(process_data['process_id']),
                    sort_order=process_data.get('sort_order', 0),
                    is_required=process_data.get('is_required', True),
                    duration_hours=process_data.get('duration_hours'),
                    cost_per_unit=process_data.get('cost_per_unit'),
                    notes=process_data.get('notes')
                )
                db.session.add(product_process)
                
        except Exception as e:
            raise ValueError(f"保存产品工序失败: {str(e)}")

    @staticmethod
    def _save_product_materials(product_id, materials_data):
        """保存产品材料"""
        try:
            # 删除现有材料
            db.session.query(ProductMaterial).filter(ProductMaterial.product_id == product_id).delete()
            
            # 创建新材料
            for material_data in materials_data:
                product_material = ProductMaterial(
                    product_id=product_id,
                    material_id=uuid.UUID(material_data['material_id']),
                    usage_quantity=material_data.get('usage_quantity'),
                    usage_unit=material_data.get('usage_unit'),
                    sort_order=material_data.get('sort_order', 0),
                    is_main_material=material_data.get('is_main_material', False),
                    cost_per_unit=material_data.get('cost_per_unit'),
                    supplier_id=uuid.UUID(material_data['supplier_id']) if material_data.get('supplier_id') else None,
                    notes=material_data.get('notes')
                )
                db.session.add(product_material)
                
        except Exception as e:
            raise ValueError(f"保存产品材料失败: {str(e)}")

    @staticmethod
    def _save_quality_indicators(product_id, indicators_data):
        """保存理化指标"""
        try:
            # 删除现有指标
            db.session.query(ProductQualityIndicator).filter(
                ProductQualityIndicator.product_id == product_id
            ).delete()
            
            # 创建新指标
            if indicators_data:
                indicator = ProductQualityIndicator(
                    product_id=product_id,
                    **indicators_data
                )
                db.session.add(indicator)
                
        except Exception as e:
            raise ValueError(f"保存理化指标失败: {str(e)}")

    @staticmethod
    def _save_product_images(product_id, images_data):
        """保存产品图片"""
        try:
            # 删除现有图片
            db.session.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
            
            # 创建新图片
            for image_data in images_data:
                image = ProductImage(
                    product_id=product_id,
                    image_name=image_data.get('image_name'),
                    image_url=image_data.get('image_url'),
                    image_type=image_data.get('image_type'),
                    file_size=image_data.get('file_size'),
                    sort_order=image_data.get('sort_order', 0)
                )
                db.session.add(image)
                
        except Exception as e:
            raise ValueError(f"保存产品图片失败: {str(e)}")

    @staticmethod
    def get_form_options():
        """获取表单选项数据"""
        try:
            from app.models.basic_data import Employee
            from flask import g, current_app
            from sqlalchemy import text
            
            # 设置schema路径（用于多租户支持）
            schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
            if schema_name != 'public':
                db.session.execute(text(f'SET search_path TO {schema_name}, public'))
            
            # 获取客户列表
            customers = db.session.query(CustomerManagement).filter(
                CustomerManagement.is_enabled == True
            ).order_by(CustomerManagement.customer_name).all()
            
            # 获取袋型列表
            bag_types = db.session.query(BagType).filter(
                BagType.is_enabled == True
            ).order_by(BagType.bag_type_name).all()
            
            # 获取工序列表
            processes = db.session.query(Process).filter(
                Process.is_enabled == True
            ).order_by(Process.process_name).all()
            
            # 获取材料列表
            materials = db.session.query(Material).filter(
                Material.is_enabled == True
            ).order_by(Material.material_name).all()
            
            # 获取员工列表（业务员）
            employees = db.session.query(Employee).filter(
                Employee.is_enabled == True
            ).order_by(Employee.employee_name).all()
            
            return {
                'customers': [{'id': str(c.id), 'name': c.customer_name, 'customer_name': c.customer_name, 'sales_person_id': str(c.salesperson_id) if hasattr(c, 'salesperson_id') and c.salesperson_id else None} for c in customers],
                'bagTypes': [{'id': str(b.id), 'name': b.bag_type_name, 'bag_type_name': b.bag_type_name, 'width': getattr(b, 'width', 0), 'length': getattr(b, 'length', 0), 'thickness': getattr(b, 'thickness', 0)} for b in bag_types],
                'processes': [{'id': str(p.id), 'name': p.process_name, 'process_name': p.process_name, 'process_category_name': getattr(p.process_category, 'process_name', '') if hasattr(p, 'process_category') and p.process_category else '', 'scheduling_method': getattr(p, 'scheduling_method', '') or '', 'unit': getattr(p, 'unit', '') or ''} for p in processes],
                'materials': [{'id': str(m.id), 'name': m.material_name, 'material_name': m.material_name, 'material_code': m.material_code or '', 'material_category_name': getattr(m.material_category, 'material_name', '') if hasattr(m, 'material_category') and m.material_category else '', 'material_attribute': getattr(m, 'material_attribute', '') or ''} for m in materials],
                'employees': [{'id': str(e.id), 'name': e.employee_name, 'employee_name': e.employee_name} for e in employees]
            }
            
        except Exception as e:
            current_app.logger.error(f"获取表单选项失败: {str(e)}")
            raise ValueError(f"获取表单选项失败: {str(e)}") 