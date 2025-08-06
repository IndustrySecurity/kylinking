from app.services.base_service import TenantAwareService
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.exc import IntegrityError
from app.models.basic_data import (
    Product, ProductProcess, ProductMaterial, ProductImage,
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
            
            # 产品结构数据现在直接存储在products表中
            product_dict['structures'] = []
            if any([
                product.struct_length, product.struct_width, product.struct_height,
                product.side_width, product.bottom_width, product.struct_thickness,
                product.total_thickness, product.volume, product.weight,
                product.density
            ]):
                product_dict['structures'] = [{
                    'length': product.struct_length,
                    'width': product.struct_width,
                    'height': product.struct_height,
                    'side_width': product.side_width,
                    'bottom_width': product.bottom_width,
                    'thickness': product.struct_thickness,
                    'total_thickness': product.total_thickness,
                    'volume': product.volume,
                    'weight': product.weight,
                    'expand_length': product.expand_length,
                    'expand_width': product.expand_width,
                    'expand_height': product.expand_height,
                    'material_length': product.material_length,
                    'material_width': product.material_width,
                    'material_height': product.material_height,
                    'single_length': product.single_length,
                    'single_width': product.single_width,
                    'single_height': product.single_height,
                    'blue_color': product.blue_color,
                    'red_color': product.red_color,
                    'other_color': product.other_color,
                    'cut_length': product.cut_length,
                    'cut_width': product.cut_width,
                    'cut_thickness': product.cut_thickness,
                    'cut_area': product.cut_area,
                    'light_eye_length': product.light_eye_length,
                    'light_eye_width': product.light_eye_width,
                    'light_eye_distance': product.light_eye_distance,
                    'edge_sealing_width': product.edge_sealing_width,
                    'bag_making_fee': product.bag_making_fee,
                    'container_fee': product.container_fee,
                    'cuff_fee': product.cuff_fee,
                    'pallet_length': product.pallet_length,
                    'pallet_width': product.pallet_width,
                    'pallet_height': product.pallet_height,
                    'pallet_1': product.pallet_1,
                    'pallet_2': product.pallet_2,
                    'pallet_3': product.pallet_3,
                    'winding_diameter': product.winding_diameter,
                    'density': product.density,
                    'seal_top': product.seal_top,
                    'seal_left': product.seal_left,
                    'seal_right': product.seal_right,
                    'seal_middle': product.seal_middle,
                    'sealing_temperature': product.sealing_temperature,
                    'sealing_width': product.sealing_width,
                    'sealing_strength': product.sealing_strength,
                    'sealing_method': product.sealing_method,
                    'power': product.power
                }]
            
            # 客户需求数据现在直接存储在products表中
            product_dict['customer_requirements'] = []
            if any([
                product.appearance_requirements, product.surface_treatment,
                product.printing_requirements, product.color_requirements,
                product.pattern_requirements, product.cutting_method
            ]):
                product_dict['customer_requirements'] = [{
                    'appearance_requirements': product.appearance_requirements,
                    'surface_treatment': product.surface_treatment,
                    'printing_requirements': product.printing_requirements,
                    'color_requirements': product.color_requirements,
                    'pattern_requirements': product.pattern_requirements,
                    'cutting_method': product.cutting_method,
                    'cutting_width': product.cutting_width,
                    'cutting_length': product.cutting_length,
                    'cutting_thickness': product.cutting_thickness,
                    'optical_distance': product.optical_distance,
                    'optical_width': product.optical_width,
                    'bag_sealing_up': product.bag_sealing_up,
                    'bag_sealing_down': product.bag_sealing_down,
                    'bag_sealing_left': product.bag_sealing_left,
                    'bag_sealing_right': product.bag_sealing_right,
                    'bag_sealing_middle': product.bag_sealing_middle,
                    'bag_sealing_inner': product.bag_sealing_inner,
                    'bag_length_tolerance': product.bag_length_tolerance,
                    'bag_width_tolerance': product.bag_width_tolerance,
                    'packaging_method': product.packaging_method,
                    'packaging_requirements': product.packaging_requirements,
                    'packaging_material': product.packaging_material,
                    'packaging_quantity': product.packaging_quantity,
                    'packaging_specifications': product.packaging_specifications,
                    'tensile_strength': product.req_tensile_strength,
                    'thermal_shrinkage': product.thermal_shrinkage,
                    'impact_strength': product.impact_strength,
                    'thermal_tensile_strength': product.thermal_tensile_strength,
                    'water_vapor_permeability': product.water_vapor_permeability,
                    'heat_shrinkage_curve': product.heat_shrinkage_curve,
                    'melt_index': product.melt_index,
                    'gas_permeability': product.gas_permeability,
                    'custom_1': product.custom_1,
                    'custom_2': product.custom_2,
                    'custom_3': product.custom_3,
                    'custom_4': product.custom_4,
                    'custom_5': product.custom_5,
                    'custom_6': product.custom_6,
                    'custom_7': product.custom_7
                }]
            
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
            
            # 理化指标数据现在直接存储在products表中
            product_dict['quality_indicators'] = []
            if any([
                product.tensile_strength_longitudinal, product.tensile_strength_transverse,
                product.thermal_shrinkage_longitudinal, product.thermal_shrinkage_transverse,
                product.puncture_strength, product.optical_properties
            ]):
                product_dict['quality_indicators'] = [{
                    'tensile_strength_longitudinal': product.tensile_strength_longitudinal,
                    'tensile_strength_transverse': product.tensile_strength_transverse,
                    'thermal_shrinkage_longitudinal': product.thermal_shrinkage_longitudinal,
                    'thermal_shrinkage_transverse': product.thermal_shrinkage_transverse,
                    'puncture_strength': product.puncture_strength,
                    'optical_properties': product.optical_properties,
                    'heat_seal_temperature': product.heat_seal_temperature,
                    'heat_seal_tensile_strength': product.heat_seal_tensile_strength,
                    'water_vapor_permeability': product.quality_water_vapor_permeability,
                    'oxygen_permeability': product.oxygen_permeability,
                    'friction_coefficient': product.friction_coefficient,
                    'peel_strength': product.peel_strength,
                    'test_standard': product.test_standard,
                    'test_basis': product.test_basis,
                    'indicator_1': product.indicator_1,
                    'indicator_2': product.indicator_2,
                    'indicator_3': product.indicator_3,
                    'indicator_4': product.indicator_4,
                    'indicator_5': product.indicator_5,
                    'indicator_6': product.indicator_6,
                    'indicator_7': product.indicator_7,
                    'indicator_8': product.indicator_8,
                    'indicator_9': product.indicator_9,
                    'indicator_10': product.indicator_10
                }]
            
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
                'salesperson_id': uuid.UUID(data['salesperson_id']) if data.get('salesperson_id') else None,
                'compound_quantity': data.get('compound_quantity'),
                'small_inventory': data.get('small_inventory'),
                'large_inventory': data.get('large_inventory'),
                'international_standard': data.get('international_standard'),
                'domestic_standard': data.get('domestic_standard'),
                'is_unlimited_quantity': data.get('is_unlimited_quantity', False),
                'is_compound_needed': data.get('is_compound_needed', False),
                'is_inspection_needed': data.get('is_inspection_needed', False),
                'is_public_product': data.get('is_public_product', False),
                'is_packaging_needed': data.get('is_packaging_needed', False),
                'is_changing': data.get('is_changing', False),
                'material_info': data.get('material_info'),
                'compound_amount': data.get('compound_amount'),
                'sales_amount': data.get('sales_amount'),
                'contract_amount': data.get('contract_amount'),
                'inventory_amount': data.get('inventory_amount'),
                
                # 技术参数
                'thickness': data.get('thickness'),
                'width': data.get('width'),
                'length': data.get('length'),
                'material_type': data.get('material_type'),
                'transparency': data.get('transparency'),
                'tensile_strength': data.get('tensile_strength'),
                'density': data.get('density'),
                
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
                'safety_stock': data.get('safety_stock'),
                'min_order_qty': data.get('min_order_qty', 1),
                'max_order_qty': data.get('max_order_qty'),
                
                # 生产信息
                'lead_time': data.get('lead_time'),
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
                # 直接更新产品表中的结构字段
                structure_data = data['structure']
                if isinstance(structure_data, dict):
                    for key, value in structure_data.items():
                        # 只保存非空值
                        if value is not None and value != '':
                            if hasattr(product, f'struct_{key}'):
                                setattr(product, f'struct_{key}', value)
                            elif hasattr(product, key):
                                setattr(product, key, value)
            
            # 处理客户需求数据
            if data.get('customer_requirements'):
                requirements_data = data['customer_requirements']
                if isinstance(requirements_data, dict):
                    for key, value in requirements_data.items():
                        # 只保存非空值
                        if value is not None and value != '':
                            if hasattr(product, key):
                                setattr(product, key, value)
            
            # 处理理化指标数据
            if data.get('quality_indicators'):
                indicators_data = data['quality_indicators']
                if isinstance(indicators_data, dict):
                    for key, value in indicators_data.items():
                        # 只保存非空值
                        if value is not None and value != '':
                            if hasattr(product, key):
                                setattr(product, key, value)
            
            # 创建工序关联
            if data.get('product_processes'):
                self._save_product_processes(product.id, data['product_processes'])
            
            # 创建材料关联
            if data.get('product_materials'):
                self._save_product_materials(product.id, data['product_materials'])
            
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
                if key in ['product_processes', 'product_materials', 'product_images', 'structures']:
                    continue
                if hasattr(product, key):
                    # 处理外键字段的UUID转换
                    if key in ['category_id', 'unit_id', 'customer_id', 'bag_type_id', 'salesperson_id', 'package_unit_id']:
                        if value:
                            try:
                                setattr(product, key, uuid.UUID(value))
                            except (ValueError, TypeError):
                                # 如果UUID转换失败，跳过这个字段
                                continue
                        else:
                            # 如果值为空，设置为None
                            setattr(product, key, None)
                    else:
                        setattr(product, key, value)
            
            product.updated_by = uuid.UUID(updated_by)
            
            # 处理结构数据
            if 'structure' in data:
                structure_data = data['structure']
                if isinstance(structure_data, dict):
                    for key, value in structure_data.items():
                        # 只保存非空值
                        if value is not None and value != '':
                            if hasattr(product, f'struct_{key}'):
                                setattr(product, f'struct_{key}', value)
                            elif hasattr(product, key):
                                setattr(product, key, value)
            
            # 处理客户需求数据
            if 'customer_requirements' in data:
                requirements_data = data['customer_requirements']
                if isinstance(requirements_data, dict):
                    for key, value in requirements_data.items():
                        # 只保存非空值
                        if value is not None and value != '':
                            if hasattr(product, key):
                                setattr(product, key, value)
            
            # 处理理化指标数据
            if 'quality_indicators' in data:
                indicators_data = data['quality_indicators']
                if isinstance(indicators_data, dict):
                    for key, value in indicators_data.items():
                        # 只保存非空值
                        if value is not None and value != '':
                            if hasattr(product, key):
                                setattr(product, key, value)
            
            # 更新子表数据
            if 'product_processes' in data:
                self._save_product_processes(product.id, data['product_processes'])
            
            if 'product_materials' in data:
                self._save_product_materials(product.id, data['product_materials'])
            
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
            self.session.query(ProductProcess).filter(ProductProcess.product_id == product.id).delete()
            self.session.query(ProductMaterial).filter(ProductMaterial.product_id == product.id).delete()
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
            bag_type = self.session.query(BagType).get(uuid.UUID(bag_type_id))
            if not bag_type:
                return
            
            # 更新产品表中的结构字段
            product = self.session.query(Product).get(product_id)
            if product:
                product.struct_length = bag_type.length
                product.struct_width = bag_type.width
                product.struct_height = bag_type.height
                product.side_width = bag_type.side_width
                product.bottom_width = bag_type.bottom_width
                product.struct_thickness = bag_type.thickness
                product.total_thickness = bag_type.total_thickness
                product.volume = bag_type.volume
                product.weight = bag_type.weight
                product.expand_length = bag_type.expand_length
                product.expand_width = bag_type.expand_width
                product.expand_height = bag_type.expand_height
                product.material_length = bag_type.material_length
                product.material_width = bag_type.material_width
                product.material_height = bag_type.material_height
                product.single_length = bag_type.single_length
                product.single_width = bag_type.single_width
                product.single_height = bag_type.single_height
                product.blue_color = bag_type.blue_color
                product.red_color = bag_type.red_color
                product.other_color = bag_type.other_color
                product.cut_length = bag_type.cut_length
                product.cut_width = bag_type.cut_width
                product.cut_thickness = bag_type.cut_thickness
                product.cut_area = bag_type.cut_area
                product.light_eye_length = bag_type.light_eye_length
                product.light_eye_width = bag_type.light_eye_width
                product.light_eye_distance = bag_type.light_eye_distance
                product.edge_sealing_width = bag_type.edge_sealing_width
                product.bag_making_fee = bag_type.bag_making_fee
                product.container_fee = bag_type.container_fee
                product.cuff_fee = bag_type.cuff_fee
                product.pallet_length = bag_type.pallet_length
                product.pallet_width = bag_type.pallet_width
                product.pallet_height = bag_type.pallet_height
                product.pallet_1 = bag_type.pallet_1
                product.pallet_2 = bag_type.pallet_2
                product.pallet_3 = bag_type.pallet_3
                product.winding_diameter = bag_type.winding_diameter
                product.density = bag_type.density
                product.seal_top = bag_type.seal_top
                product.seal_left = bag_type.seal_left
                product.seal_right = bag_type.seal_right
                product.seal_middle = bag_type.seal_middle
                product.sealing_temperature = bag_type.sealing_temperature
                product.sealing_width = bag_type.sealing_width
                product.sealing_strength = bag_type.sealing_strength
                product.sealing_method = bag_type.sealing_method
                product.power = bag_type.power
            
        except Exception as e:
            raise ValueError(f"根据袋型创建产品结构失败: {str(e)}")



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
                            'unit_id': uuid.UUID(process_data['unit_id']) if process_data.get('unit_id') else None,
                            'curing': process_data.get('curing', False),
                            'roll_out_direction': process_data.get('roll_out_direction'),
                            'weight_gain': process_data.get('weight_gain', 0),
                            'total_gram_weight': process_data.get('total_gram_weight', 0),
                            'weight_gain_upper_limit': process_data.get('weight_gain_upper_limit', 0),
                            'weight_gain_lower_limit': process_data.get('weight_gain_lower_limit', 0),
                            'lamination_width': process_data.get('lamination_width', 0),
                            'lamination_thickness': process_data.get('lamination_thickness', 0),
                            'lamination_density': process_data.get('lamination_density', 0),
                            'process_requirements': process_data.get('process_requirements'),
                            'piece_rate_unit_price': process_data.get('piece_rate_unit_price', 0),
                            'difficulty_level': process_data.get('difficulty_level'),
                            'surface_print': process_data.get('surface_print', 0),
                            'reverse_print': process_data.get('reverse_print', 0),
                            'inkjet_code': process_data.get('inkjet_code', 0),
                            'solvent': process_data.get('solvent', 0),
                            'adhesive_amount': process_data.get('adhesive_amount', 0),
                            'solid_content': process_data.get('solid_content', 0),
                            'no_material_needed': process_data.get('no_material_needed', False),
                            'mes_semi_finished_usage': process_data.get('mes_semi_finished_usage', False),
                            'mes_multi_process_semi_finished': process_data.get('mes_multi_process_semi_finished', False),
                            'min_hourly_output': process_data.get('min_hourly_output', 0),
                            'standard_hourly_output': process_data.get('standard_hourly_output', 0),
                            'semi_finished_coefficient': process_data.get('semi_finished_coefficient', 0)
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
                        process_id = material_data.get('process_id')
                        if not process_id or process_id == '' or process_id == 'null':
                            material_name_for_error = material_data.get('material_name') or '未知材料'
                            raise ValueError(f"材料 '{material_name_for_error}' 必须选择工序")
                        
                        new_material_data = {
                            'product_id': product_id,
                            'material_id': uuid.UUID(material_data['material_id']),
                            'process_id': uuid.UUID(material_data['process_id']),
                            'sort_order': material_data.get('sort_order', 0),
                            'layer_number': material_data.get('layer_number'),
                            'supplier_id': uuid.UUID(material_data['supplier_id']) if material_data.get('supplier_id') else None,
                            'material_process': material_data.get('material_process'),
                            'remarks': material_data.get('remarks'),
                            'hot_stamping_film_length': material_data.get('hot_stamping_film_length', 0),
                            'hot_stamping_film_width': material_data.get('hot_stamping_film_width', 0),
                            'material_file_remarks': material_data.get('material_file_remarks')
                        }
                        self.create_with_tenant(ProductMaterial, **new_material_data)
                
        except Exception as e:
            raise ValueError(f"保存产品材料失败: {str(e)}")



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
            
            # 获取供应商
            suppliers = []
            try:
                from app.models.basic_data import SupplierManagement
                suppliers = self.session.query(SupplierManagement).filter(
                    SupplierManagement.is_enabled == True
                ).order_by(SupplierManagement.supplier_name).all()
            except Exception as e:
                self.logger.error(f"获取供应商失败: {str(e)}")
                suppliers = []
            
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
                    {
                        'value': str(proc.id), 
                        'label': proc.process_name, 
                        'process_category_name': proc.process_category.process_name if proc.process_category else '', 
                        'scheduling_method': scheduling_method_map.get(proc.scheduling_method, ''), 
                        'unit_id': str(proc.unit_id) if proc.unit_id else '',
                        'unit_name': proc.unit.unit_name if proc.unit else ''
                    }
                    for proc in processes
                ] if processes else [],
                'materials': [
                    {
                        'value': str(mat.id), 
                        'label': mat.material_name,
                        'material_code': mat.material_code, 
                        'material_category_name': mat.material_category.material_name if mat.material_category else '', 
                        'material_attribute': self._get_material_type_display_name(mat.material_category.material_type) if mat.material_category else ''
                    }
                    for mat in materials
                ],
                'units': [
                    {'value': str(unit.id), 'label': unit.unit_name}
                    for unit in units
                ],
                'suppliers': [
                    {'value': str(supplier.id), 'label': supplier.supplier_name}
                    for supplier in suppliers
                ],
                'product_types': [
                    {'value': 'finished', 'label': '成品'},
                    {'value': 'semi', 'label': '半成品'},
                    {'value': 'material', 'label': '原材料'}
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

    def _get_material_type_display_name(self, material_type):
        """获取材料类型的显示名称"""
        material_type_map = {
            'raw_material': '原材料',
            'main_material': '主材',
            'auxiliary_material': '辅材',
            'main': '主材',
            'auxiliary': '辅材',
            'packaging': '包装材料',
            'consumable': '耗材',
            'accessory': '配件',
            'semi_finished': '半成品',
            'finished_product': '成品',
            '主材': '主材',
            '辅材': '辅材'
        }
        return material_type_map.get(material_type, material_type)

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