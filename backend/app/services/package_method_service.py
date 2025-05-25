# -*- coding: utf-8 -*-
"""
包装方式管理服务
"""

from app.models.basic_data import PackageMethod
from app.models.user import User
from app.extensions import db
from sqlalchemy import and_, or_, text
from flask import g, current_app
import uuid


class PackageMethodService:
    """包装方式管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in PackageMethodService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_package_methods(page=1, per_page=20, search=None, enabled_only=False):
        """获取包装方式列表"""
        # 设置schema
        PackageMethodService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, package_name, package_code, description, sort_order, 
            is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.package_methods
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (package_name ILIKE :search OR 
                 package_code ILIKE :search OR 
                 description ILIKE :search)
            """)
            params['search'] = f'%{search}%'
        
        if enabled_only:
            where_conditions.append("is_enabled = true")
        
        # 构建完整查询
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        base_query += " ORDER BY sort_order, created_at"
        
        # 计算总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM {schema_name}.package_methods
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
            
            package_methods = []
            for row in rows:
                package_method_data = {
                    'id': str(row.id),
                    'package_name': row.package_name,
                    'package_code': row.package_code,
                    'description': row.description,
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
                        package_method_data['created_by_name'] = created_user.get_full_name()
                    else:
                        package_method_data['created_by_name'] = '未知用户'
                else:
                    package_method_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        package_method_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        package_method_data['updated_by_name'] = '未知用户'
                else:
                    package_method_data['updated_by_name'] = ''
                
                package_methods.append(package_method_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'package_methods': package_methods,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying package methods: {str(e)}")
            raise ValueError(f'查询包装方式失败: {str(e)}')
    
    @staticmethod
    def get_package_method(package_method_id):
        """获取包装方式详情"""
        # 设置schema
        PackageMethodService._set_schema()
        
        try:
            package_method_uuid = uuid.UUID(package_method_id)
        except ValueError:
            raise ValueError('无效的包装方式ID')
        
        package_method = PackageMethod.query.get(package_method_uuid)
        if not package_method:
            raise ValueError('包装方式不存在')
        
        package_method_data = package_method.to_dict()
        
        # 获取创建人和修改人用户名
        if package_method.created_by:
            created_user = User.query.get(package_method.created_by)
            if created_user:
                package_method_data['created_by_name'] = created_user.get_full_name()
            else:
                package_method_data['created_by_name'] = '未知用户'
        
        if package_method.updated_by:
            updated_user = User.query.get(package_method.updated_by)
            if updated_user:
                package_method_data['updated_by_name'] = updated_user.get_full_name()
            else:
                package_method_data['updated_by_name'] = '未知用户'
        
        return package_method_data
    
    @staticmethod
    def create_package_method(data, created_by):
        """创建包装方式"""
        # 设置schema
        PackageMethodService._set_schema()
        
        # 验证数据
        if not data.get('package_name'):
            raise ValueError('包装方式名称不能为空')
        
        # 检查包装方式名称是否重复
        existing = PackageMethod.query.filter_by(
            package_name=data['package_name']
        ).first()
        if existing:
            raise ValueError('包装方式名称已存在')
        
        # 检查编码是否重复
        if data.get('package_code'):
            existing_code = PackageMethod.query.filter_by(
                package_code=data['package_code']
            ).first()
            if existing_code:
                raise ValueError('包装方式编码已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建包装方式
        package_method = PackageMethod(
            package_name=data['package_name'],
            package_code=data.get('package_code'),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(package_method)
            db.session.commit()
            return package_method.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建包装方式失败: {str(e)}')
    
    @staticmethod
    def update_package_method(package_method_id, data, updated_by):
        """更新包装方式"""
        # 设置schema
        PackageMethodService._set_schema()
        
        try:
            package_method_uuid = uuid.UUID(package_method_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        package_method = PackageMethod.query.get(package_method_uuid)
        if not package_method:
            raise ValueError('包装方式不存在')
        
        # 检查包装方式名称是否重复（排除自己）
        if 'package_name' in data and data['package_name'] != package_method.package_name:
            existing = PackageMethod.query.filter(
                and_(
                    PackageMethod.package_name == data['package_name'],
                    PackageMethod.id != package_method_uuid
                )
            ).first()
            if existing:
                raise ValueError('包装方式名称已存在')
        
        # 检查编码是否重复（排除自己）
        if 'package_code' in data and data['package_code'] != package_method.package_code:
            existing_code = PackageMethod.query.filter(
                and_(
                    PackageMethod.package_code == data['package_code'],
                    PackageMethod.id != package_method_uuid
                )
            ).first()
            if existing_code:
                raise ValueError('包装方式编码已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(package_method, key):
                setattr(package_method, key, value)
        
        package_method.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return package_method.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新包装方式失败: {str(e)}')
    
    @staticmethod
    def delete_package_method(package_method_id):
        """删除包装方式"""
        # 设置schema
        PackageMethodService._set_schema()
        
        try:
            package_method_uuid = uuid.UUID(package_method_id)
        except ValueError:
            raise ValueError('无效的包装方式ID')
        
        package_method = PackageMethod.query.get(package_method_uuid)
        if not package_method:
            raise ValueError('包装方式不存在')
        
        try:
            db.session.delete(package_method)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除包装方式失败: {str(e)}')
    
    @staticmethod
    def batch_update_package_methods(data_list, updated_by):
        """批量更新包装方式（用于可编辑表格）"""
        # 设置schema
        PackageMethodService._set_schema()
        
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的用户ID')
        
        results = []
        errors = []
        
        for index, data in enumerate(data_list):
            try:
                if 'id' in data and data['id']:
                    # 更新现有记录
                    package_method = PackageMethodService.update_package_method(
                        data['id'], data, updated_by
                    )
                    results.append(package_method)
                else:
                    # 创建新记录
                    package_method = PackageMethodService.create_package_method(
                        data, updated_by
                    )
                    results.append(package_method)
            except ValueError as e:
                errors.append({
                    'index': index,
                    'error': str(e),
                    'data': data
                })
        
        if errors:
            # 如果有错误，回滚事务
            db.session.rollback()
            raise ValueError(f'批量更新失败，错误详情: {errors}')
        
        return results
    
    @staticmethod
    def get_enabled_package_methods():
        """获取启用的包装方式列表（用于下拉选择）"""
        # 设置schema
        PackageMethodService._set_schema()
        
        package_methods = PackageMethod.query.filter_by(
            is_enabled=True
        ).order_by(PackageMethod.sort_order, PackageMethod.package_name).all()
        
        return [pm.to_dict() for pm in package_methods]


class DeliveryMethodService:
    """送货方式管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in DeliveryMethodService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_delivery_methods(page=1, per_page=20, search=None, enabled_only=False):
        """获取送货方式列表"""
        # 设置schema
        DeliveryMethodService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, delivery_name, delivery_code, description, sort_order, 
            is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.delivery_methods
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (delivery_name ILIKE :search OR 
                 delivery_code ILIKE :search OR 
                 description ILIKE :search)
            """)
            params['search'] = f'%{search}%'
        
        if enabled_only:
            where_conditions.append("is_enabled = true")
        
        # 构建完整查询
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        base_query += " ORDER BY sort_order, created_at"
        
        # 计算总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM {schema_name}.delivery_methods
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
            
            delivery_methods = []
            for row in rows:
                delivery_method_data = {
                    'id': str(row.id),
                    'delivery_name': row.delivery_name,
                    'delivery_code': row.delivery_code,
                    'description': row.description,
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
                        delivery_method_data['created_by_name'] = created_user.get_full_name()
                    else:
                        delivery_method_data['created_by_name'] = '未知用户'
                else:
                    delivery_method_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        delivery_method_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        delivery_method_data['updated_by_name'] = '未知用户'
                else:
                    delivery_method_data['updated_by_name'] = ''
                
                delivery_methods.append(delivery_method_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'delivery_methods': delivery_methods,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying delivery methods: {str(e)}")
            raise ValueError(f'查询送货方式失败: {str(e)}')
    
    @staticmethod
    def get_delivery_method(delivery_method_id):
        """获取送货方式详情"""
        # 设置schema
        DeliveryMethodService._set_schema()
        
        try:
            delivery_method_uuid = uuid.UUID(delivery_method_id)
        except ValueError:
            raise ValueError('无效的送货方式ID')
        
        from app.models.basic_data import DeliveryMethod
        delivery_method = DeliveryMethod.query.get(delivery_method_uuid)
        if not delivery_method:
            raise ValueError('送货方式不存在')
        
        delivery_method_data = delivery_method.to_dict()
        
        # 获取创建人和修改人用户名
        if delivery_method.created_by:
            created_user = User.query.get(delivery_method.created_by)
            if created_user:
                delivery_method_data['created_by_name'] = created_user.get_full_name()
            else:
                delivery_method_data['created_by_name'] = '未知用户'
        
        if delivery_method.updated_by:
            updated_user = User.query.get(delivery_method.updated_by)
            if updated_user:
                delivery_method_data['updated_by_name'] = updated_user.get_full_name()
            else:
                delivery_method_data['updated_by_name'] = '未知用户'
        
        return delivery_method_data
    
    @staticmethod
    def create_delivery_method(data, created_by):
        """创建送货方式"""
        # 设置schema
        DeliveryMethodService._set_schema()
        
        # 验证数据
        if not data.get('delivery_name'):
            raise ValueError('送货方式名称不能为空')
        
        from app.models.basic_data import DeliveryMethod
        
        # 检查送货方式名称是否重复
        existing = DeliveryMethod.query.filter_by(
            delivery_name=data['delivery_name']
        ).first()
        if existing:
            raise ValueError('送货方式名称已存在')
        
        # 检查编码是否重复
        if data.get('delivery_code'):
            existing_code = DeliveryMethod.query.filter_by(
                delivery_code=data['delivery_code']
            ).first()
            if existing_code:
                raise ValueError('送货方式编码已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建送货方式
        delivery_method = DeliveryMethod(
            delivery_name=data['delivery_name'],
            delivery_code=data.get('delivery_code'),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(delivery_method)
            db.session.commit()
            return delivery_method.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建送货方式失败: {str(e)}')
    
    @staticmethod
    def update_delivery_method(delivery_method_id, data, updated_by):
        """更新送货方式"""
        # 设置schema
        DeliveryMethodService._set_schema()
        
        try:
            delivery_method_uuid = uuid.UUID(delivery_method_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import DeliveryMethod
        delivery_method = DeliveryMethod.query.get(delivery_method_uuid)
        if not delivery_method:
            raise ValueError('送货方式不存在')
        
        # 检查送货方式名称是否重复（排除自己）
        if 'delivery_name' in data and data['delivery_name'] != delivery_method.delivery_name:
            existing = DeliveryMethod.query.filter(
                and_(
                    DeliveryMethod.delivery_name == data['delivery_name'],
                    DeliveryMethod.id != delivery_method_uuid
                )
            ).first()
            if existing:
                raise ValueError('送货方式名称已存在')
        
        # 检查编码是否重复（排除自己）
        if 'delivery_code' in data and data['delivery_code'] != delivery_method.delivery_code:
            existing_code = DeliveryMethod.query.filter(
                and_(
                    DeliveryMethod.delivery_code == data['delivery_code'],
                    DeliveryMethod.id != delivery_method_uuid
                )
            ).first()
            if existing_code:
                raise ValueError('送货方式编码已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(delivery_method, key):
                setattr(delivery_method, key, value)
        
        delivery_method.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return delivery_method.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新送货方式失败: {str(e)}')
    
    @staticmethod
    def delete_delivery_method(delivery_method_id):
        """删除送货方式"""
        # 设置schema
        DeliveryMethodService._set_schema()
        
        try:
            delivery_method_uuid = uuid.UUID(delivery_method_id)
        except ValueError:
            raise ValueError('无效的送货方式ID')
        
        from app.models.basic_data import DeliveryMethod
        delivery_method = DeliveryMethod.query.get(delivery_method_uuid)
        if not delivery_method:
            raise ValueError('送货方式不存在')
        
        try:
            db.session.delete(delivery_method)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除送货方式失败: {str(e)}')
    
    @staticmethod
    def batch_update_delivery_methods(data_list, updated_by):
        """批量更新送货方式（用于可编辑表格）"""
        # 设置schema
        DeliveryMethodService._set_schema()
        
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的用户ID')
        
        results = []
        errors = []
        
        for index, data in enumerate(data_list):
            try:
                if 'id' in data and data['id']:
                    # 更新现有记录
                    delivery_method = DeliveryMethodService.update_delivery_method(
                        data['id'], data, updated_by
                    )
                    results.append(delivery_method)
                else:
                    # 创建新记录
                    delivery_method = DeliveryMethodService.create_delivery_method(
                        data, updated_by
                    )
                    results.append(delivery_method)
            except ValueError as e:
                errors.append({
                    'index': index,
                    'error': str(e),
                    'data': data
                })
        
        if errors:
            # 如果有错误，回滚事务
            db.session.rollback()
            raise ValueError(f'批量更新失败，错误详情: {errors}')
        
        return results
    
    @staticmethod
    def get_enabled_delivery_methods():
        """获取启用的送货方式列表（用于下拉选择）"""
        # 设置schema
        DeliveryMethodService._set_schema()
        
        from app.models.basic_data import DeliveryMethod
        delivery_methods = DeliveryMethod.query.filter_by(
            is_enabled=True
        ).order_by(DeliveryMethod.sort_order, DeliveryMethod.delivery_name).all()
        
        return [dm.to_dict() for dm in delivery_methods] 