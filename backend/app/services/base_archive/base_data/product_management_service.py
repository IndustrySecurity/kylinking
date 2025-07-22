from app.services.base_service import TenantAwareService
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.exc import IntegrityError
from app.models.basic_data import (
    Product, ProductStructure, ProductCustomerRequirement, 
    ProductProcess, ProductMaterial, ProductQualityIndicator, ProductImage,
    CustomerManagement, BagType, Process, Material, ProductCategory, Currency
)
from app.models.user import User
from datetime import datetime
import uuid
import logging


class ProductManagementService(TenantAwareService):
    """产品管理服务类"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def get_products(self, page=1, per_page=20, search=None, customer_id=None, bag_type_id=None, status=None):
        """获取产品列表"""
        try:
            query = self.session.query(Product)
            
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
            salesperson_ids = set()
            for product in products:
                if product.created_by:
                    user_ids.add(product.created_by)
                if product.updated_by:
                    user_ids.add(product.updated_by)
                if product.salesperson_id:
                    salesperson_ids.add(product.salesperson_id)
            
            users = {}
            if user_ids:
                user_list = self.session.query(User).filter(User.id.in_(user_ids)).all()
                users = {str(user.id): user.get_full_name() for user in user_list}
            
            # 获取业务员信息
            salespersons = {}
            if salesperson_ids:
                from app.models.basic_data import Employee
                salesperson_list = self.session.query(Employee).filter(Employee.id.in_(salesperson_ids)).all()
                salespersons = {str(sp.id): sp.employee_name for sp in salesperson_list}
            
            # 转换为字典并添加用户信息
            result_products = []
            for product in products:
                product_dict = product.to_dict()
                product_dict['created_by_name'] = users.get(str(product.created_by), '')
                product_dict['updated_by_name'] = users.get(str(product.updated_by), '')
                product_dict['salesperson_name'] = salespersons.get(str(product.salesperson_id), '')
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

    def get_product_detail(self, product_id):
        """获取产品详情，包含所有子表数据"""
        try:
            from app.models.basic_data import Employee
            
            product = self.session.query(Product).get(uuid.UUID(product_id))
            if not product:
                raise ValueError("产品不存在")
            
            # 获取产品基本信息
            product_dict = product.to_dict()
            
            # 获取业务员信息
            if product.salesperson_id:
                salesperson = self.session.query(Employee).get(product.salesperson_id)
                if salesperson:
                    product_dict['salesperson_name'] = salesperson.employee_name
            
            # 获取创建人信息  
            if product.created_by:
                creator = self.session.query(Employee).get(product.created_by)
                if creator:
                    product_dict['creator_name'] = creator.employee_name
            
            # 获取产品结构
            structures = self.session.query(ProductStructure).filter(
                ProductStructure.product_id == product.id
            ).all()
            product_dict['structures'] = [structure.to_dict() for structure in structures] if structures else []
            
            # 获取客户需求
            requirements = self.session.query(ProductCustomerRequirement).filter(
                ProductCustomerRequirement.product_id == product.id
            ).all()
            product_dict['customer_requirements'] = [req.to_dict() for req in requirements] if requirements else []
            
            # 获取工序
            processes = self.session.query(ProductProcess).filter(
                ProductProcess.product_id == product.id
            ).order_by(ProductProcess.sort_order).all()
            product_dict['product_processes'] = [process.to_dict() for process in processes] if processes else []
            
            # 获取材料
            materials = self.session.query(ProductMaterial).filter(
                ProductMaterial.product_id == product.id
            ).order_by(ProductMaterial.sort_order).all()
            product_dict['product_materials'] = [material.to_dict() for material in materials] if materials else []
            
            # 获取理化指标
            quality_indicators = self.session.query(ProductQualityIndicator).filter(
                ProductQualityIndicator.product_id == product.id
            ).all()
            product_dict['quality_indicators'] = [qi.to_dict() for qi in quality_indicators] if quality_indicators else []
            
            # 获取图片
            images = self.session.query(ProductImage).filter(
                ProductImage.product_id == product.id
            ).order_by(ProductImage.sort_order).all()
            product_dict['product_images'] = [image.to_dict() for image in images] if images else []
            
            return product_dict
            
        except Exception as e:
            raise ValueError(f"获取产品详情失败: {str(e)}")

    def create_product(self, data, created_by):
        """创建产品及相关数据"""
        try:
            # 验证必填字段
            if not data.get('product_name'):
                raise ValueError("产品名称不能为空")
            
            # 生成产品编码
            if not data.get('product_code'):
                data['product_code'] = self._generate_product_code()
            
            # 准备产品数据
            product_data = {
                'product_code': data['product_code'],
                'product_name': data['product_name'],
                'product_type': data.get('product_type', 'finished'),
                'category_id': uuid.UUID(data['category_id']) if data.get('category_id') else None,
                
                # 基本信息
                'short_name': data.get('short_name'),
                'english_name': data.get('english_name'),
                'brand': data.get('brand'),
                'model': data.get('model'),
                'specification': data.get('specification'),
                'unit_id': uuid.UUID(data['unit_id']) if data.get('unit_id') else None,
                
                # 产品管理界面字段
                'customer_id': uuid.UUID(data['customer_id']) if data.get('customer_id') else None,
                'bag_type_id': uuid.UUID(data['bag_type_id']) if data.get('bag_type_id') else None,
                'salesperson_id': uuid.UUID(data['salesperson_id']) if data.get('salesperson_id') else uuid.UUID(created_by),
                'compound_quantity': data.get('compound_quantity', 0),
                'small_inventory': data.get('small_inventory', 0),
                'large_inventory': data.get('large_inventory', 0),
                'international_standard': data.get('international_standard'),
                'domestic_standard': data.get('domestic_standard'),
                'is_unlimited_quantity': data.get('is_unlimited_quantity', False),
                'is_compound_needed': data.get('is_compound_needed', False),
                'is_inspection_needed': data.get('is_inspection_needed', False),
                'is_public_product': data.get('is_public_product', False),
                'is_packaging_needed': data.get('is_packaging_needed', False),
                'is_changing': data.get('is_changing', False),
                'material_info': data.get('material_info'),
                'compound_amount': data.get('compound_amount', 0),
                'sales_amount': data.get('sales_amount', 0),
                'contract_amount': data.get('contract_amount', 0),
                'inventory_amount': data.get('inventory_amount', 0),
                
                # 技术参数
                'thickness': data.get('thickness'),
                'width': data.get('width'),
                'length': data.get('length'),
                'material_type': data.get('material_type'),
                'transparency': data.get('transparency'),
                'tensile_strength': data.get('tensile_strength'),
                
                # 包装信息
                'package_unit_id': data.get('package_unit_id'),
                'conversion_rate': data.get('conversion_rate', 1),
                'net_weight': data.get('net_weight'),
                'gross_weight': data.get('gross_weight'),
                
                # 价格信息
                'standard_cost': data.get('standard_cost'),
                'standard_price': data.get('standard_price'),
                'currency': data.get('currency', 'CNY'),
                
                # 库存信息
                'safety_stock': data.get('safety_stock', 0),
                'min_order_qty': data.get('min_order_qty', 1),
                'max_order_qty': data.get('max_order_qty'),
                
                # 生产信息
                'lead_time': data.get('lead_time', 0),
                'shelf_life': data.get('shelf_life'),
                'storage_condition': data.get('storage_condition'),
                
                # 质量标准
                'quality_standard': data.get('quality_standard'),
                'inspection_method': data.get('inspection_method'),
                
                # 自定义字段
                'custom_fields': data.get('custom_fields', {}),
                
                # 系统字段
                'status': data.get('status', 'active'),
                'is_sellable': data.get('is_sellable', True),
                'is_purchasable': data.get('is_purchasable', True),
                'is_producible': data.get('is_producible', True),
            }
            
            # 使用继承的create_with_tenant方法
            product = self.create_with_tenant(Product, **product_data)
            self.session.flush()  # 获取product.id
            
            # 创建产品结构（如果选择了袋型，自动填入结构数据）
            if data.get('bag_type_id') and data.get('auto_fill_structure', True):
                self._create_product_structure_from_bag_type(
                    product.id, data['bag_type_id']
                )
            elif data.get('structure'):
                self._save_product_structure(product.id, data['structure'])
            
            # 创建客户需求
            if data.get('customer_requirements'):
                self._save_customer_requirements(product.id, data['customer_requirements'])
            
            # 创建工序关联
            if data.get('product_processes'):
                self._save_product_processes(product.id, data['product_processes'])
            
            # 创建材料关联
            if data.get('product_materials'):
                self._save_product_materials(product.id, data['product_materials'])
            
            # 创建理化指标
            if data.get('quality_indicators'):
                self._save_quality_indicators(product.id, data['quality_indicators'])
            
            # 创建图片
            if data.get('product_images'):
                self._save_product_images(product.id, data['product_images'])
            
            self.commit()
            
            return self.get_product_detail(str(product.id))
            
        except IntegrityError:
            self.rollback()
            raise ValueError("产品编码已存在")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建产品失败: {str(e)}")

    def update_product(self, product_id, data, updated_by):
        """更新产品及相关数据"""
        try:
            product = self.session.query(Product).get(uuid.UUID(product_id))
            if not product:
                raise ValueError("产品不存在")
            
            # 更新字段
            for key, value in data.items():
                # 跳过子表关系字段，避免赋值给关系属性
                if key in ['product_processes', 'product_materials', 'structure', 'customer_requirements', 'quality_indicators', 'product_images', 'structures']:
                    continue
                if hasattr(product, key):
                    # 处理外键字段的UUID转换
                    if key in ['category_id', 'unit_id', 'customer_id', 'bag_type_id', 'salesperson_id', 'package_unit_id'] and value:
                        try:
                            setattr(product, key, uuid.UUID(value))
                        except (ValueError, TypeError):
                            # 如果UUID转换失败，跳过这个字段
                            continue
                    else:
                        setattr(product, key, value)
            
            product.updated_by = uuid.UUID(updated_by)
            
            # 更新子表数据
            if 'structure' in data:
                self._save_product_structure(product.id, data['structure'])
            
            if 'customer_requirements' in data:
                self._save_customer_requirements(product.id, data['customer_requirements'])
            
            if 'product_processes' in data:
                self._save_product_processes(product.id, data['product_processes'])
            
            if 'product_materials' in data:
                self._save_product_materials(product.id, data['product_materials'])
            
            if 'quality_indicators' in data:
                self._save_quality_indicators(product.id, data['quality_indicators'])
            
            if 'product_images' in data:
                self._save_product_images(product.id, data['product_images'])
            
            self.commit()
            
            return self.get_product_detail(str(product.id))
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新产品失败: {str(e)}")

    def delete_product(self, product_id):
        """删除产品"""
        try:
            product = self.session.query(Product).get(uuid.UUID(product_id))
            if not product:
                raise ValueError("产品不存在")
            
            # 删除所有子表数据
            self.session.query(ProductStructure).filter(ProductStructure.product_id == product.id).delete()
            self.session.query(ProductCustomerRequirement).filter(ProductCustomerRequirement.product_id == product.id).delete()
            self.session.query(ProductProcess).filter(ProductProcess.product_id == product.id).delete()
            self.session.query(ProductMaterial).filter(ProductMaterial.product_id == product.id).delete()
            self.session.query(ProductQualityIndicator).filter(ProductQualityIndicator.product_id == product.id).delete()
            self.session.query(ProductImage).filter(ProductImage.product_id == product.id).delete()
            
            # 删除产品
            self.session.delete(product)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除产品失败: {str(e)}")

    def _generate_product_code(self):
        """生成产品编码"""
        # 查找当前租户schema中最新的产品编码
        last_product = self.session.query(Product).filter(
            Product.product_code.like('P%')
        ).order_by(desc(Product.product_code)).first()
        
        if last_product:
            try:
                # 提取数字部分并转换为整数
                last_num = int(last_product.product_code[1:])
                new_num = last_num + 1
            except (ValueError, IndexError):
                # 如果解析失败，从1开始
                new_num = 1
        else:
            new_num = 1
        
        # 生成8位数字的产品编码
        return f'P{new_num:08d}'

    def _create_product_structure_from_bag_type(self, product_id, bag_type_id):
        """根据袋型自动创建产品结构"""
        try:
            from app.models.basic_data import BagTypeStructure
            
            # 获取袋型结构
            bag_structures = self.session.query(BagTypeStructure).filter(
                BagTypeStructure.bag_type_id == uuid.UUID(bag_type_id)
            ).order_by(BagTypeStructure.sort_order).all()
            
            for bag_structure in bag_structures:
                structure_data = {
                    'product_id': product_id,
                    # 可以从袋型结构中复制一些数据，这里先创建空结构
                    'length': 0,
                    'width': 0,
                    'height': 0
                }
                self.create_with_tenant(ProductStructure, **structure_data)
                
        except Exception as e:
            raise ValueError(f"从袋型创建产品结构失败: {str(e)}")

    def _save_product_structure(self, product_id, structure_data):
        """保存产品结构"""
        try:
            # 删除现有结构
            self.session.query(ProductStructure).filter(ProductStructure.product_id == product_id).delete()
            
            # 创建新结构 - 只有当structure_data不为空且包含有效数据时才创建
            if structure_data and isinstance(structure_data, dict) and len(structure_data) > 0:
                # 检查是否有任何非空值
                has_valid_data = any(value is not None and value != '' for value in structure_data.values())
                if has_valid_data:
                    new_structure_data = {
                        'product_id': product_id,
                        **structure_data
                    }
                    self.create_with_tenant(ProductStructure, **new_structure_data)
                
        except Exception as e:
            raise ValueError(f"保存产品结构失败: {str(e)}")

    def _save_customer_requirements(self, product_id, requirements_data):
        """保存客户需求"""
        try:
            # 删除现有需求
            self.session.query(ProductCustomerRequirement).filter(
                ProductCustomerRequirement.product_id == product_id
            ).delete()
            
            # 创建新需求 - 只有当requirements_data不为空且包含有效数据时才创建
            if requirements_data and isinstance(requirements_data, dict) and len(requirements_data) > 0:
                # 检查是否有任何非空值
                has_valid_data = any(value is not None and value != '' for value in requirements_data.values())
                if has_valid_data:
                    new_requirement_data = {
                        'product_id': product_id,
                        **requirements_data
                    }
                    self.create_with_tenant(ProductCustomerRequirement, **new_requirement_data)
                
        except Exception as e:
            raise ValueError(f"保存客户需求失败: {str(e)}")

    def _save_product_processes(self, product_id, processes_data):
        """保存产品工序"""
        try:
            # 删除现有工序
            self.session.query(ProductProcess).filter(ProductProcess.product_id == product_id).delete()
            
            # 创建新工序 - 确保processes_data是列表
            if processes_data and isinstance(processes_data, list):
                for process_data in processes_data:
                    if isinstance(process_data, dict) and 'process_id' in process_data:
                        new_process_data = {
                            'product_id': product_id,
                            'process_id': uuid.UUID(process_data['process_id']),
                            'sort_order': process_data.get('sort_order', 0),
                            'is_required': process_data.get('is_required', True),
                            'duration_hours': process_data.get('duration_hours'),
                            'cost_per_unit': process_data.get('cost_per_unit'),
                            'notes': process_data.get('notes')
                        }
                        self.create_with_tenant(ProductProcess, **new_process_data)
                
        except Exception as e:
            raise ValueError(f"保存产品工序失败: {str(e)}")

    def _save_product_materials(self, product_id, materials_data):
        """保存产品材料"""
        try:
            # 删除现有材料
            self.session.query(ProductMaterial).filter(ProductMaterial.product_id == product_id).delete()
            
            # 创建新材料 - 确保materials_data是列表
            if materials_data and isinstance(materials_data, list):
                for material_data in materials_data:
                    if isinstance(material_data, dict) and 'material_id' in material_data:
                        new_material_data = {
                            'product_id': product_id,
                            'material_id': uuid.UUID(material_data['material_id']),
                            'usage_quantity': material_data.get('usage_quantity'),
                            'usage_unit': material_data.get('usage_unit'),
                            'sort_order': material_data.get('sort_order', 0),
                            'is_main_material': material_data.get('is_main_material', False),
                            'cost_per_unit': material_data.get('cost_per_unit'),
                            'supplier_id': uuid.UUID(material_data['supplier_id']) if material_data.get('supplier_id') else None,
                            'notes': material_data.get('notes')
                        }
                        self.create_with_tenant(ProductMaterial, **new_material_data)
                
        except Exception as e:
            raise ValueError(f"保存产品材料失败: {str(e)}")

    def _save_quality_indicators(self, product_id, indicators_data):
        """保存理化指标"""
        try:
            # 删除现有指标
            self.session.query(ProductQualityIndicator).filter(
                ProductQualityIndicator.product_id == product_id
            ).delete()
            
            # 创建新指标 - 确保indicators_data是字典
            if indicators_data and isinstance(indicators_data, dict) and len(indicators_data) > 0:
                # 检查是否有任何非空值
                has_valid_data = any(value is not None and value != '' for value in indicators_data.values())
                if has_valid_data:
                    new_indicator_data = {
                        'product_id': product_id,
                        **indicators_data
                    }
                    self.create_with_tenant(ProductQualityIndicator, **new_indicator_data)
                
        except Exception as e:
            raise ValueError(f"保存理化指标失败: {str(e)}")

    def _save_product_images(self, product_id, images_data):
        """保存产品图片"""
        try:
            # 删除现有图片
            self.session.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
            
            # 创建新图片 - 确保images_data是列表
            if images_data and isinstance(images_data, list):
                for image_data in images_data:
                    if isinstance(image_data, dict):
                        new_image_data = {
                            'product_id': product_id,
                            'image_url': image_data.get('image_url'),
                            'image_name': image_data.get('image_name'),
                            'image_type': image_data.get('image_type'),
                            'file_size': image_data.get('file_size'),
                            'sort_order': image_data.get('sort_order', 0)
                        }
                        self.create_with_tenant(ProductImage, **new_image_data)
                
        except Exception as e:
            raise ValueError(f"保存产品图片失败: {str(e)}")

    def get_form_options(self):
        """获取产品管理表单的选项数据"""
        try:
            from app.models.basic_data import (
                ProductCategory, CustomerManagement, Employee, 
                Currency, Material
            )
            
            # 获取产品分类
            try:
                product_categories = self.session.query(ProductCategory).filter(
                    ProductCategory.is_enabled == True
                ).order_by(ProductCategory.sort_order, ProductCategory.category_name).all()
            except Exception as e:
                self.logger.error(f"获取产品分类失败: {str(e)}")
                product_categories = []
            
            # 获取客户
            try:
                customers = self.session.query(CustomerManagement).filter(
                    CustomerManagement.is_enabled == True
                ).order_by(CustomerManagement.customer_name).all()
            except Exception as e:
                self.logger.error(f"获取客户失败: {str(e)}")
                customers = []
            
            # 获取员工（业务员）
            try:
                employees = self.session.query(Employee).filter(
                    Employee.is_enabled == True
                ).order_by(Employee.employee_name).all()
            except Exception as e:
                self.logger.error(f"获取员工失败: {str(e)}")
                employees = []
            
            # 获取币种
            try:
                currencies = self.session.query(Currency).filter(
                    Currency.is_enabled == True
                ).order_by(Currency.currency_name).all()
            except Exception as e:
                self.logger.error(f"获取币种失败: {str(e)}")
                currencies = []
            
            # 获取材料
            try:
                materials = self.session.query(Material).filter(
                    Material.is_enabled == True
                ).order_by(Material.material_name).all()
            except Exception as e:
                self.logger.error(f"获取材料失败: {str(e)}")
                materials = []
            
            # 尝试获取袋型（如果模型存在的话）
            bag_types = []
            try:
                from app.models.basic_data import BagType
                bag_types = self.session.query(BagType).filter(
                    BagType.is_enabled == True
                ).order_by(BagType.bag_type_name).all()
            except Exception as e:
                self.logger.error(f"获取袋型失败: {str(e)}")
                bag_types = []
            
            # 尝试获取工序（如果模型存在的话）
            processes = []
            try:
                from app.models.basic_data import Process
                processes = self.session.query(Process).filter(
                    Process.is_enabled == True
                ).order_by(Process.process_name).all()
            except Exception as e:
                self.logger.error(f"获取工序失败: {str(e)}")
                processes = []

            # 获取单位
            units = []
            try:
                from app.models.basic_data import Unit
                units = self.session.query(Unit).filter(
                    Unit.is_enabled == True
                ).order_by(Unit.unit_name).all()
            except Exception as e:
                self.logger.error(f"获取单位失败: {str(e)}")
                units = []
            
            SCHEDULING_METHODS = [
                ('investment_m', '投产m'),
                ('investment_kg', '投产kg'),
                ('production_piece', '投产(个)'),
                ('production_m', '产出m'),
                ('production_kg', '产出kg'),
                ('production_piece_out', '产出(个)'),
                ('production_set', '产出(套)'),
                ('production_sheet', '产出(张)')
            ]
            scheduling_method_map = {value: label for value, label in SCHEDULING_METHODS}
            return {
                'product_categories': [
                    {'value': str(cat.id), 'label': cat.category_name}
                    for cat in product_categories
                ],
                'customers': [
                    {'value': str(cust.id), 'label': f'{cust.customer_code} - {cust.customer_name}', 'sales_person_id': cust.salesperson_id}
                    for cust in customers
                ],
                'employees': [
                    {'value': str(emp.id), 'label': emp.employee_name}
                    for emp in employees
                ],
                'currencies': [
                    {'value': str(curr.id), 'label': f'{curr.currency_name} ({curr.currency_code})'}
                    for curr in currencies
                ],
                'bagTypes': [
                    {'value': str(bag.id), 'label': bag.bag_type_name}
                    for bag in bag_types
                ] if bag_types else [],
                'processes': [
                    {'value': str(proc.id), 'label': proc.process_name, 'process_category_name': proc.process_category.process_name, 'scheduling_method':scheduling_method_map[proc.scheduling_method], 'unit': proc.unit.unit_name}
                    for proc in processes
                ] if processes else [],
                'materials': [
                    {'value': str(mat.id), 'label': mat.material_name,'material_code': mat.material_code, 'material_category_name': mat.material_category.material_name, 'material_attribute': mat.material_category.material_type}
                    for mat in materials
                ],
                'units': [
                    {'value': str(unit.id), 'label': unit.unit_name}
                    for unit in units
                ],
                'product_types': [
                    {'value': 'finished', 'label': '成品'},
                    {'value': 'semi_finished', 'label': '半成品'},
                    {'value': 'raw_material', 'label': '原材料'},
                    {'value': 'spare_part', 'label': '备件'}
                ],
                'status_options': [
                    {'value': 'active', 'label': '启用'},
                    {'value': 'inactive', 'label': '停用'},
                    {'value': 'development', 'label': '开发中'},
                    {'value': 'obsolete', 'label': '淘汰'}
                ]
            }
            
        except Exception as e:
            # 如果发生致命错误，记录详细信息并抛出异常
            error_msg = f"获取产品表单选项失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)

    def get_product_options(self):
        """获取产品列表"""
        try:
            products = self.session.query(Product).filter(
                Product.is_enabled == True
            ).order_by(Product.product_name).all()
            return [
                {'value': str(product.id), 'label': product.product_name}
                for product in products
            ]
        except Exception as e:
            self.logger.error(f"获取产品列表失败: {str(e)}")
            return []


def get_product_management_service(tenant_id: str = None, schema_name: str = None) -> ProductManagementService:
    """获取产品管理服务实例"""
    return ProductManagementService(tenant_id=tenant_id, schema_name=schema_name) 