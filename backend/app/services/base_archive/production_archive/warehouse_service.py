# -*- coding: utf-8 -*-
"""
Warehouse 服务
"""

from app.services.base_service import TenantAwareService
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class WarehouseService(TenantAwareService):
    """仓库管理服务"""
    
    def get_warehouses(self, page=1, per_page=20, search=None, warehouse_type=None, parent_warehouse_id=None):
        """获取仓库列表"""
        try:
            from app.models.basic_data import Warehouse
            
            # 构建查询
            query = self.session.query(Warehouse)
            
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
    
    def get_warehouse(self, warehouse_id):
        """获取仓库详情"""
        try:
            from app.models.basic_data import Warehouse
            
            warehouse = self.session.query(Warehouse).get(uuid.UUID(warehouse_id))
            if not warehouse:
                raise ValueError("仓库不存在")
            
            return warehouse.to_dict(include_user_info=True)
            
        except Exception as e:
            raise ValueError(f"获取仓库详情失败: {str(e)}")
    
    def create_warehouse(self, data, created_by):
        """创建仓库"""
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
                    existing = self.session.query(Warehouse).filter(
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
                parent_warehouse = self.session.query(Warehouse).get(parent_warehouse_id)
                if not parent_warehouse:
                    raise ValueError("上级仓库不存在")
                if not parent_warehouse.is_enabled:
                    raise ValueError("上级仓库未启用")
            
            # 创建仓库对象
            warehouse = self.create_with_tenant(Warehouse,
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
            
            self.commit()
            
            return warehouse.to_dict(include_user_info=True)
                        
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建仓库失败: {str(e)}")
    
    def update_warehouse(self, warehouse_id, data, updated_by):
        """更新仓库"""
        try:
            from app.models.basic_data import Warehouse
            
            warehouse = self.session.query(Warehouse).get(uuid.UUID(warehouse_id))
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
                    
                    parent_warehouse = self.session.query(Warehouse).get(parent_warehouse_id)
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
            for key, value in data.items():
                if hasattr(warehouse, key):
                    setattr(warehouse, key, value)
            
            warehouse.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            
            return warehouse.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.rollback()
            if 'warehouse_code' in str(e):
                raise ValueError("仓库编号已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新仓库失败: {str(e)}")
    
    def delete_warehouse(self, warehouse_id):
        """删除仓库"""
        try:
            from app.models.basic_data import Warehouse
            
            warehouse = self.session.query(Warehouse).get(uuid.UUID(warehouse_id))
            if not warehouse:
                raise ValueError("仓库不存在")
            
            # 检查是否有子仓库
            children_count = self.session.query(Warehouse).filter(Warehouse.parent_warehouse_id == warehouse.id).count()
            if children_count > 0:
                raise ValueError("存在子仓库，无法删除")
            
            # 这里可以添加其他业务检查，比如检查是否有库存记录等
            
            self.session.delete(warehouse)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除仓库失败: {str(e)}")
    
    def batch_update_warehouses(self, updates, updated_by):
        """批量更新仓库"""
        try:
            from app.models.basic_data import Warehouse
            
            updated_warehouses = []
            
            for update_data in updates:
                warehouse_id = update_data.get('id')
                if not warehouse_id:
                    continue
                
                warehouse = self.session.query(Warehouse).get(uuid.UUID(warehouse_id))
                if not warehouse:
                    continue
                
                # 更新指定字段
                update_fields = ['sort_order', 'is_enabled']
                for field in update_fields:
                    if field in update_data:
                        setattr(warehouse, field, update_data[field])
                
                warehouse.updated_by = uuid.UUID(updated_by)
                updated_warehouses.append(warehouse)
            
            self.commit()
            
            return [warehouse.to_dict(include_user_info=True) for warehouse in updated_warehouses]
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"批量更新仓库失败: {str(e)}")
    
    def get_warehouse_options(self, warehouse_type=None):
        """获取仓库选项数据"""
        try:
            from app.models.basic_data import Warehouse
            
            query = self.session.query(Warehouse).filter(Warehouse.is_enabled == True)
            
            # 按类型筛选
            if warehouse_type:
                query = query.filter(Warehouse.warehouse_type == warehouse_type)
            
            warehouses = query.all()
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
    
    def get_warehouse_tree(self):
        """获取仓库树形结构"""
        try:
            from app.models.basic_data import Warehouse
            
            # 获取所有启用的仓库
            warehouses = self.session.query(Warehouse).filter(
                Warehouse.is_enabled == True
            ).order_by(Warehouse.sort_order, Warehouse.warehouse_name).all()
            
            # 构建树形结构
            warehouse_dict = {str(warehouse.id): warehouse for warehouse in warehouses}
            tree = []
            
            for warehouse in warehouses:
                warehouse_data = warehouse.to_dict()
                warehouse_data['children'] = []
                
                if warehouse.parent_warehouse_id is None:
                    # 根仓库
                    tree.append(warehouse_data)
                else:
                    # 子仓库
                    parent_id = str(warehouse.parent_warehouse_id)
                    if parent_id in warehouse_dict:
                        parent_data = next((d for d in tree if d['id'] == parent_id), None)
                        if parent_data:
                            parent_data['children'].append(warehouse_data)
                        else:
                            # 如果父级不在根级别，需要递归查找
                            def find_and_add_child(nodes, parent_id, child_data):
                                for node in nodes:
                                    if node['id'] == parent_id:
                                        node['children'].append(child_data)
                                        return True
                                    elif node['children'] and find_and_add_child(node['children'], parent_id, child_data):
                                        return True
                                return False
                            
                            find_and_add_child(tree, parent_id, warehouse_data)
            
            return tree
        except Exception as e:
            raise ValueError(f"获取仓库树形结构失败: {str(e)}")
    
    def get_warehouse_types(self):
        """获取仓库类型选项"""
        try:
            # 返回静态的仓库类型选项
            return [
                {'value': 'raw_material', 'label': '原材料仓库'},
                {'value': 'semi_finished', 'label': '半成品仓库'},
                {'value': 'finished_product', 'label': '成品仓库'},
                {'value': 'packaging', 'label': '包材仓库'},
                {'value': 'tool', 'label': '工具仓库'},
                {'value': 'office', 'label': '办公用品仓库'},
                {'value': 'other', 'label': '其他'}
            ]
        except Exception as e:
            raise ValueError(f"获取仓库类型失败: {str(e)}")
    
    def get_accounting_methods(self):
        """获取核算方式选项"""
        try:
            # 返回静态的核算方式选项
            return [
                {'value': 'fifo', 'label': '先进先出'},
                {'value': 'lifo', 'label': '后进先出'},
                {'value': 'weighted_average', 'label': '加权平均'},
                {'value': 'moving_average', 'label': '移动平均'},
                {'value': 'standard_cost', 'label': '标准成本'}
            ]
        except Exception as e:
            raise ValueError(f"获取核算方式失败: {str(e)}")
    
    def get_circulation_types(self):
        """获取流转类型选项"""
        try:
            # 返回静态的流转类型选项
            return [
                {'value': 'on_site_circulation', 'label': '现场流转'},
                {'value': 'warehouse_circulation', 'label': '仓库流转'},
                {'value': 'direct_delivery', 'label': '直接发货'},
                {'value': 'transit', 'label': '在途'}
            ]
        except Exception as e:
            raise ValueError(f"获取流转类型失败: {str(e)}")


