# -*- coding: utf-8 -*-
"""
包装方式管理服务
"""

from app.models.basic_data import PackageMethod, QuoteFreight
from app.models.user import User
from app.extensions import db
from sqlalchemy import and_, or_, text
from flask import g, current_app
import uuid
from flask_jwt_extended import get_jwt_identity
from datetime import datetime


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


class ColorCardService:
    """色卡管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in ColorCardService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_color_cards(page=1, per_page=20, search=None, enabled_only=False):
        """获取色卡列表"""
        # 设置schema
        ColorCardService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, color_code, color_name, color_value, remarks, sort_order, 
            is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.color_cards
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (color_name ILIKE :search OR 
                 color_code ILIKE :search OR 
                 remarks ILIKE :search)
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
        FROM {schema_name}.color_cards
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
            
            color_cards = []
            for row in rows:
                color_card_data = {
                    'id': str(row.id),
                    'color_code': row.color_code,
                    'color_name': row.color_name,
                    'color_value': row.color_value,
                    'remarks': row.remarks,
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
                        color_card_data['created_by_name'] = created_user.get_full_name()
                    else:
                        color_card_data['created_by_name'] = '未知用户'
                else:
                    color_card_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        color_card_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        color_card_data['updated_by_name'] = '未知用户'
                else:
                    color_card_data['updated_by_name'] = ''
                
                color_cards.append(color_card_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'color_cards': color_cards,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying color cards: {str(e)}")
            raise ValueError(f'查询色卡失败: {str(e)}')
    
    @staticmethod
    def get_color_card(color_card_id):
        """获取色卡详情"""
        # 设置schema
        ColorCardService._set_schema()
        
        try:
            color_card_uuid = uuid.UUID(color_card_id)
        except ValueError:
            raise ValueError('无效的色卡ID')
        
        from app.models.basic_data import ColorCard
        color_card = ColorCard.query.get(color_card_uuid)
        if not color_card:
            raise ValueError('色卡不存在')
        
        color_card_data = color_card.to_dict()
        
        # 获取创建人和修改人用户名
        if color_card.created_by:
            created_user = User.query.get(color_card.created_by)
            if created_user:
                color_card_data['created_by_name'] = created_user.get_full_name()
            else:
                color_card_data['created_by_name'] = '未知用户'
        
        if color_card.updated_by:
            updated_user = User.query.get(color_card.updated_by)
            if updated_user:
                color_card_data['updated_by_name'] = updated_user.get_full_name()
            else:
                color_card_data['updated_by_name'] = '未知用户'
        
        return color_card_data
    
    @staticmethod
    def create_color_card(data, created_by):
        """创建色卡"""
        # 设置schema
        ColorCardService._set_schema()
        
        # 验证数据
        if not data.get('color_name'):
            raise ValueError('色卡名称不能为空')
        
        if not data.get('color_value'):
            raise ValueError('色值不能为空')
        
        from app.models.basic_data import ColorCard
        
        # 检查色卡名称是否重复
        existing = ColorCard.query.filter_by(
            color_name=data['color_name']
        ).first()
        if existing:
            raise ValueError('色卡名称已存在')
        
        # 自动生成色卡编号（忽略用户输入的编号）
        color_code = ColorCard.generate_color_code()
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建色卡
        color_card = ColorCard(
            color_code=color_code,
            color_name=data['color_name'],
            color_value=data['color_value'],
            remarks=data.get('remarks'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(color_card)
            db.session.commit()
            return color_card.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建色卡失败: {str(e)}')
    
    @staticmethod
    def update_color_card(color_card_id, data, updated_by):
        """更新色卡"""
        # 设置schema
        ColorCardService._set_schema()
        
        try:
            color_card_uuid = uuid.UUID(color_card_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import ColorCard
        color_card = ColorCard.query.get(color_card_uuid)
        if not color_card:
            raise ValueError('色卡不存在')
        
        # 检查色卡名称是否重复（排除自己）
        if 'color_name' in data and data['color_name'] != color_card.color_name:
            existing = ColorCard.query.filter(
                and_(
                    ColorCard.color_name == data['color_name'],
                    ColorCard.id != color_card_uuid
                )
            ).first()
            if existing:
                raise ValueError('色卡名称已存在')
        
        # 移除色卡编号字段，不允许修改
        if 'color_code' in data:
            del data['color_code']
        
        # 更新字段
        for key, value in data.items():
            if hasattr(color_card, key):
                setattr(color_card, key, value)
        
        color_card.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return color_card.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新色卡失败: {str(e)}')
    
    @staticmethod
    def delete_color_card(color_card_id):
        """删除色卡"""
        # 设置schema
        ColorCardService._set_schema()
        
        try:
            color_card_uuid = uuid.UUID(color_card_id)
        except ValueError:
            raise ValueError('无效的色卡ID')
        
        from app.models.basic_data import ColorCard
        color_card = ColorCard.query.get(color_card_uuid)
        if not color_card:
            raise ValueError('色卡不存在')
        
        try:
            db.session.delete(color_card)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除色卡失败: {str(e)}')
    
    @staticmethod
    def batch_update_color_cards(data_list, updated_by):
        """批量更新色卡（用于可编辑表格）"""
        # 设置schema
        ColorCardService._set_schema()
        
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
                    color_card = ColorCardService.update_color_card(
                        data['id'], data, updated_by
                    )
                    results.append(color_card)
                else:
                    # 创建新记录
                    color_card = ColorCardService.create_color_card(
                        data, updated_by
                    )
                    results.append(color_card)
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
    def get_enabled_color_cards():
        """获取启用的色卡列表（用于下拉选择）"""
        # 设置schema
        ColorCardService._set_schema()
        
        from app.models.basic_data import ColorCard
        color_cards = ColorCard.query.filter_by(
            is_enabled=True
        ).order_by(ColorCard.sort_order, ColorCard.color_name).all()
        
        return [cc.to_dict() for cc in color_cards]


class UnitService:
    """单位管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in UnitService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_units(page=1, per_page=20, search=None, enabled_only=False):
        """获取单位列表"""
        # 设置schema
        UnitService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, unit_name, description, sort_order, 
            is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.units
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (unit_name ILIKE :search OR 
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
        FROM {schema_name}.units
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
            
            units = []
            for row in rows:
                unit_data = {
                    'id': str(row.id),
                    'unit_name': row.unit_name,
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
                        unit_data['created_by_name'] = created_user.get_full_name()
                    else:
                        unit_data['created_by_name'] = '未知用户'
                else:
                    unit_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        unit_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        unit_data['updated_by_name'] = '未知用户'
                else:
                    unit_data['updated_by_name'] = ''
                
                units.append(unit_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'units': units,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying units: {str(e)}")
            raise ValueError(f'查询单位失败: {str(e)}')
    
    @staticmethod
    def get_unit(unit_id):
        """获取单位详情"""
        # 设置schema
        UnitService._set_schema()
        
        try:
            unit_uuid = uuid.UUID(unit_id)
        except ValueError:
            raise ValueError('无效的单位ID')
        
        from app.models.basic_data import Unit
        unit = Unit.query.get(unit_uuid)
        if not unit:
            raise ValueError('单位不存在')
        
        unit_data = unit.to_dict()
        
        # 获取创建人和修改人用户名
        if unit.created_by:
            created_user = User.query.get(unit.created_by)
            if created_user:
                unit_data['created_by_name'] = created_user.get_full_name()
            else:
                unit_data['created_by_name'] = '未知用户'
        
        if unit.updated_by:
            updated_user = User.query.get(unit.updated_by)
            if updated_user:
                unit_data['updated_by_name'] = updated_user.get_full_name()
            else:
                unit_data['updated_by_name'] = '未知用户'
        
        return unit_data
    
    @staticmethod
    def create_unit(data, created_by):
        """创建单位"""
        # 设置schema
        UnitService._set_schema()
        
        # 验证数据
        if not data.get('unit_name'):
            raise ValueError('单位名称不能为空')
        
        from app.models.basic_data import Unit
        
        # 检查单位名称是否重复
        existing = Unit.query.filter_by(
            unit_name=data['unit_name']
        ).first()
        if existing:
            raise ValueError('单位名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建单位
        unit = Unit(
            unit_name=data['unit_name'],
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(unit)
            db.session.commit()
            return unit.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建单位失败: {str(e)}')
    
    @staticmethod
    def update_unit(unit_id, data, updated_by):
        """更新单位"""
        # 设置schema
        UnitService._set_schema()
        
        try:
            unit_uuid = uuid.UUID(unit_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import Unit
        unit = Unit.query.get(unit_uuid)
        if not unit:
            raise ValueError('单位不存在')
        
        # 检查单位名称是否重复（排除自己）
        if 'unit_name' in data and data['unit_name'] != unit.unit_name:
            existing = Unit.query.filter(
                and_(
                    Unit.unit_name == data['unit_name'],
                    Unit.id != unit_uuid
                )
            ).first()
            if existing:
                raise ValueError('单位名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(unit, key):
                setattr(unit, key, value)
        
        unit.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return unit.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新单位失败: {str(e)}')
    
    @staticmethod
    def delete_unit(unit_id):
        """删除单位"""
        # 设置schema
        UnitService._set_schema()
        
        try:
            unit_uuid = uuid.UUID(unit_id)
        except ValueError:
            raise ValueError('无效的单位ID')
        
        from app.models.basic_data import Unit
        unit = Unit.query.get(unit_uuid)
        if not unit:
            raise ValueError('单位不存在')
        
        try:
            db.session.delete(unit)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除单位失败: {str(e)}')
    
    @staticmethod
    def batch_update_units(data_list, updated_by):
        """批量更新单位（用于可编辑表格）"""
        # 设置schema
        UnitService._set_schema()
        
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
                    unit = UnitService.update_unit(
                        data['id'], data, updated_by
                    )
                    results.append(unit)
                else:
                    # 创建新记录
                    unit = UnitService.create_unit(
                        data, updated_by
                    )
                    results.append(unit)
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
    def get_enabled_units():
        """获取启用的单位列表（用于下拉选择）"""
        # 设置schema
        UnitService._set_schema()
        
        from app.models.basic_data import Unit
        units = Unit.query.filter_by(
            is_enabled=True
        ).order_by(Unit.sort_order, Unit.unit_name).all()
        
        return [unit.to_dict() for unit in units]


class CustomerCategoryManagementService:
    """客户分类管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in CustomerCategoryManagementService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_customer_categories(page=1, per_page=20, search=None, enabled_only=False):
        """获取客户分类列表"""
        # 设置schema
        CustomerCategoryManagementService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, category_name, category_code, description, sort_order, 
            is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.customer_category_management
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (category_name ILIKE :search OR 
                 category_code ILIKE :search OR 
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
        FROM {schema_name}.customer_category_management
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
            
            customer_categories = []
            for row in rows:
                category_data = {
                    'id': str(row.id),
                    'category_name': row.category_name,
                    'category_code': row.category_code,
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
                        category_data['created_by_name'] = created_user.get_full_name()
                    else:
                        category_data['created_by_name'] = '未知用户'
                else:
                    category_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        category_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        category_data['updated_by_name'] = '未知用户'
                else:
                    category_data['updated_by_name'] = ''
                
                customer_categories.append(category_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'customer_categories': customer_categories,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying customer categories: {str(e)}")
            raise ValueError(f'查询客户分类失败: {str(e)}')
    
    @staticmethod
    def get_customer_category(category_id):
        """获取客户分类详情"""
        # 设置schema
        CustomerCategoryManagementService._set_schema()
        
        try:
            category_uuid = uuid.UUID(category_id)
        except ValueError:
            raise ValueError('无效的客户分类ID')
        
        from app.models.basic_data import CustomerCategoryManagement
        category = CustomerCategoryManagement.query.get(category_uuid)
        if not category:
            raise ValueError('客户分类不存在')
        
        category_data = category.to_dict()
        
        # 获取创建人和修改人用户名
        if category.created_by:
            created_user = User.query.get(category.created_by)
            if created_user:
                category_data['created_by_name'] = created_user.get_full_name()
            else:
                category_data['created_by_name'] = '未知用户'
        
        if category.updated_by:
            updated_user = User.query.get(category.updated_by)
            if updated_user:
                category_data['updated_by_name'] = updated_user.get_full_name()
            else:
                category_data['updated_by_name'] = '未知用户'
        
        return category_data
    
    @staticmethod
    def create_customer_category(data, created_by):
        """创建客户分类"""
        # 设置schema
        CustomerCategoryManagementService._set_schema()
        
        # 验证数据
        if not data.get('category_name'):
            raise ValueError('客户分类名称不能为空')
        
        from app.models.basic_data import CustomerCategoryManagement
        
        # 检查客户分类名称是否重复
        existing = CustomerCategoryManagement.query.filter_by(
            category_name=data['category_name']
        ).first()
        if existing:
            raise ValueError('客户分类名称已存在')
        
        # 检查编码是否重复
        if data.get('category_code'):
            existing_code = CustomerCategoryManagement.query.filter_by(
                category_code=data['category_code']
            ).first()
            if existing_code:
                raise ValueError('客户分类编码已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建客户分类
        category = CustomerCategoryManagement(
            category_name=data['category_name'],
            category_code=data.get('category_code'),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(category)
            db.session.commit()
            return category.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建客户分类失败: {str(e)}')
    
    @staticmethod
    def update_customer_category(category_id, data, updated_by):
        """更新客户分类"""
        # 设置schema
        CustomerCategoryManagementService._set_schema()
        
        try:
            category_uuid = uuid.UUID(category_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import CustomerCategoryManagement
        category = CustomerCategoryManagement.query.get(category_uuid)
        if not category:
            raise ValueError('客户分类不存在')
        
        # 检查客户分类名称是否重复（排除自己）
        if 'category_name' in data and data['category_name'] != category.category_name:
            existing = CustomerCategoryManagement.query.filter(
                and_(
                    CustomerCategoryManagement.category_name == data['category_name'],
                    CustomerCategoryManagement.id != category_uuid
                )
            ).first()
            if existing:
                raise ValueError('客户分类名称已存在')
        
        # 检查编码是否重复（排除自己）
        if 'category_code' in data and data['category_code'] != category.category_code:
            existing_code = CustomerCategoryManagement.query.filter(
                and_(
                    CustomerCategoryManagement.category_code == data['category_code'],
                    CustomerCategoryManagement.id != category_uuid
                )
            ).first()
            if existing_code:
                raise ValueError('客户分类编码已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        category.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return category.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新客户分类失败: {str(e)}')
    
    @staticmethod
    def delete_customer_category(category_id):
        """删除客户分类"""
        # 设置schema
        CustomerCategoryManagementService._set_schema()
        
        try:
            category_uuid = uuid.UUID(category_id)
        except ValueError:
            raise ValueError('无效的客户分类ID')
        
        from app.models.basic_data import CustomerCategoryManagement
        category = CustomerCategoryManagement.query.get(category_uuid)
        if not category:
            raise ValueError('客户分类不存在')
        
        try:
            db.session.delete(category)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除客户分类失败: {str(e)}')
    
    @staticmethod
    def batch_update_customer_categories(data_list, updated_by):
        """批量更新客户分类（用于可编辑表格）"""
        # 设置schema
        CustomerCategoryManagementService._set_schema()
        
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
                    category = CustomerCategoryManagementService.update_customer_category(
                        data['id'], data, updated_by
                    )
                    results.append(category)
                else:
                    # 创建新记录
                    category = CustomerCategoryManagementService.create_customer_category(
                        data, updated_by
                    )
                    results.append(category)
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
    def get_enabled_customer_categories():
        """获取启用的客户分类列表（用于下拉选择）"""
        # 设置schema
        CustomerCategoryManagementService._set_schema()
        
        from app.models.basic_data import CustomerCategoryManagement
        categories = CustomerCategoryManagement.query.filter_by(
            is_enabled=True
        ).order_by(CustomerCategoryManagement.sort_order, CustomerCategoryManagement.category_name).all()
        
        return [category.to_dict() for category in categories]


class SupplierCategoryManagementService:
    """供应商分类管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in SupplierCategoryManagementService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_supplier_categories(page=1, per_page=20, search=None, enabled_only=False):
        """获取供应商分类列表"""
        # 设置schema
        SupplierCategoryManagementService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, category_name, category_code, description, is_plate_making, 
            is_outsourcing, is_knife_plate, sort_order, is_enabled, 
            created_by, updated_by, created_at, updated_at
        FROM {schema_name}.supplier_category_management
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (category_name ILIKE :search OR 
                 category_code ILIKE :search OR 
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
        FROM {schema_name}.supplier_category_management
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
            
            supplier_categories = []
            for row in rows:
                category_data = {
                    'id': str(row.id),
                    'category_name': row.category_name,
                    'category_code': row.category_code,
                    'description': row.description,
                    'is_plate_making': row.is_plate_making,
                    'is_outsourcing': row.is_outsourcing,
                    'is_knife_plate': row.is_knife_plate,
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
                        category_data['created_by_name'] = created_user.get_full_name()
                    else:
                        category_data['created_by_name'] = '未知用户'
                else:
                    category_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        category_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        category_data['updated_by_name'] = '未知用户'
                else:
                    category_data['updated_by_name'] = ''
                
                supplier_categories.append(category_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'supplier_categories': supplier_categories,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying supplier categories: {str(e)}")
            raise ValueError(f'查询供应商分类失败: {str(e)}')
    
    @staticmethod
    def get_supplier_category(category_id):
        """获取供应商分类详情"""
        # 设置schema
        SupplierCategoryManagementService._set_schema()
        
        try:
            category_uuid = uuid.UUID(category_id)
        except ValueError:
            raise ValueError('无效的供应商分类ID')
        
        from app.models.basic_data import SupplierCategoryManagement
        category = SupplierCategoryManagement.query.get(category_uuid)
        if not category:
            raise ValueError('供应商分类不存在')
        
        category_data = category.to_dict()
        
        # 获取创建人和修改人用户名
        if category.created_by:
            created_user = User.query.get(category.created_by)
            if created_user:
                category_data['created_by_name'] = created_user.get_full_name()
            else:
                category_data['created_by_name'] = '未知用户'
        
        if category.updated_by:
            updated_user = User.query.get(category.updated_by)
            if updated_user:
                category_data['updated_by_name'] = updated_user.get_full_name()
            else:
                category_data['updated_by_name'] = '未知用户'
        
        return category_data
    
    @staticmethod
    def create_supplier_category(data, created_by):
        """创建供应商分类"""
        # 设置schema
        SupplierCategoryManagementService._set_schema()
        
        # 验证数据
        if not data.get('category_name'):
            raise ValueError('供应商分类名称不能为空')
        
        from app.models.basic_data import SupplierCategoryManagement
        
        # 检查供应商分类名称是否重复
        existing = SupplierCategoryManagement.query.filter_by(
            category_name=data['category_name']
        ).first()
        if existing:
            raise ValueError('供应商分类名称已存在')
        
        # 检查编码是否重复
        if data.get('category_code'):
            existing_code = SupplierCategoryManagement.query.filter_by(
                category_code=data['category_code']
            ).first()
            if existing_code:
                raise ValueError('供应商分类编码已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建供应商分类
        category = SupplierCategoryManagement(
            category_name=data['category_name'],
            category_code=data.get('category_code'),
            description=data.get('description'),
            is_plate_making=data.get('is_plate_making', False),
            is_outsourcing=data.get('is_outsourcing', False),
            is_knife_plate=data.get('is_knife_plate', False),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(category)
            db.session.commit()
            return category.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建供应商分类失败: {str(e)}')
    
    @staticmethod
    def update_supplier_category(category_id, data, updated_by):
        """更新供应商分类"""
        # 设置schema
        SupplierCategoryManagementService._set_schema()
        
        try:
            category_uuid = uuid.UUID(category_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import SupplierCategoryManagement
        category = SupplierCategoryManagement.query.get(category_uuid)
        if not category:
            raise ValueError('供应商分类不存在')
        
        # 检查供应商分类名称是否重复（排除自己）
        if 'category_name' in data and data['category_name'] != category.category_name:
            existing = SupplierCategoryManagement.query.filter(
                and_(
                    SupplierCategoryManagement.category_name == data['category_name'],
                    SupplierCategoryManagement.id != category_uuid
                )
            ).first()
            if existing:
                raise ValueError('供应商分类名称已存在')
        
        # 检查编码是否重复（排除自己）
        if 'category_code' in data and data['category_code'] != category.category_code:
            existing_code = SupplierCategoryManagement.query.filter(
                and_(
                    SupplierCategoryManagement.category_code == data['category_code'],
                    SupplierCategoryManagement.id != category_uuid
                )
            ).first()
            if existing_code:
                raise ValueError('供应商分类编码已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        category.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return category.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新供应商分类失败: {str(e)}')
    
    @staticmethod
    def delete_supplier_category(category_id):
        """删除供应商分类"""
        # 设置schema
        SupplierCategoryManagementService._set_schema()
        
        try:
            category_uuid = uuid.UUID(category_id)
        except ValueError:
            raise ValueError('无效的供应商分类ID')
        
        from app.models.basic_data import SupplierCategoryManagement
        category = SupplierCategoryManagement.query.get(category_uuid)
        if not category:
            raise ValueError('供应商分类不存在')
        
        try:
            db.session.delete(category)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除供应商分类失败: {str(e)}')
    
    @staticmethod
    def batch_update_supplier_categories(data_list, updated_by):
        """批量更新供应商分类（用于可编辑表格）"""
        # 设置schema
        SupplierCategoryManagementService._set_schema()
        
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
                    category = SupplierCategoryManagementService.update_supplier_category(
                        data['id'], data, updated_by
                    )
                    results.append(category)
                else:
                    # 创建新记录
                    category = SupplierCategoryManagementService.create_supplier_category(
                        data, updated_by
                    )
                    results.append(category)
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
    def get_enabled_supplier_categories():
        """获取启用的供应商分类列表（用于下拉选择）"""
        # 设置schema
        SupplierCategoryManagementService._set_schema()
        
        from app.models.basic_data import SupplierCategoryManagement
        categories = SupplierCategoryManagement.query.filter_by(
            is_enabled=True
        ).order_by(SupplierCategoryManagement.sort_order, SupplierCategoryManagement.category_name).all()
        
        return [category.to_dict() for category in categories]


class SpecificationService:
    """规格管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in SpecificationService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_specifications(page=1, per_page=20, search=None, enabled_only=False):
        """获取规格列表"""
        # 设置schema
        SpecificationService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, spec_name, length, width, roll, area_sqm, spec_format,
            description, sort_order, is_enabled, created_by, updated_by, 
            created_at, updated_at
        FROM {schema_name}.specifications
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (spec_name ILIKE :search OR 
                 spec_format ILIKE :search OR
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
        FROM {schema_name}.specifications
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
            
            specifications = []
            for row in rows:
                spec_data = {
                    'id': str(row.id),
                    'spec_name': row.spec_name,
                    'length': float(row.length) if row.length else None,
                    'width': float(row.width) if row.width else None,
                    'roll': float(row.roll) if row.roll else None,
                    'area_sqm': float(row.area_sqm) if row.area_sqm else None,
                    'spec_format': row.spec_format,
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
                        spec_data['created_by_name'] = created_user.get_full_name()
                    else:
                        spec_data['created_by_name'] = '未知用户'
                else:
                    spec_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        spec_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        spec_data['updated_by_name'] = '未知用户'
                else:
                    spec_data['updated_by_name'] = ''
                
                specifications.append(spec_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'specifications': specifications,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying specifications: {str(e)}")
            raise ValueError(f'查询规格失败: {str(e)}')
    
    @staticmethod
    def get_specification(spec_id):
        """获取规格详情"""
        # 设置schema
        SpecificationService._set_schema()
        
        try:
            spec_uuid = uuid.UUID(spec_id)
        except ValueError:
            raise ValueError('无效的规格ID')
        
        from app.models.basic_data import Specification
        specification = Specification.query.get(spec_uuid)
        if not specification:
            raise ValueError('规格不存在')
        
        spec_data = specification.to_dict()
        
        # 获取创建人和修改人用户名
        if specification.created_by:
            created_user = User.query.get(specification.created_by)
            if created_user:
                spec_data['created_by_name'] = created_user.get_full_name()
            else:
                spec_data['created_by_name'] = '未知用户'
        
        if specification.updated_by:
            updated_user = User.query.get(specification.updated_by)
            if updated_user:
                spec_data['updated_by_name'] = updated_user.get_full_name()
            else:
                spec_data['updated_by_name'] = '未知用户'
        
        return spec_data
    
    @staticmethod
    def create_specification(data, created_by):
        """创建规格"""
        # 设置schema
        SpecificationService._set_schema()
        
        # 验证数据
        if not data.get('spec_name'):
            raise ValueError('规格名称不能为空')
        
        if not data.get('length') or not data.get('width') or not data.get('roll'):
            raise ValueError('长、宽、卷不能为空')
        
        from app.models.basic_data import Specification
        
        # 检查规格名称是否重复
        existing = Specification.query.filter_by(
            spec_name=data['spec_name']
        ).first()
        if existing:
            raise ValueError('规格名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建规格
        specification = Specification(
            spec_name=data['spec_name'],
            length=data['length'],
            width=data['width'],
            roll=data['roll'],
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        # 计算面积和格式
        specification.calculate_area_and_format()
        
        try:
            db.session.add(specification)
            db.session.commit()
            return specification.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建规格失败: {str(e)}')
    
    @staticmethod
    def update_specification(spec_id, data, updated_by):
        """更新规格"""
        # 设置schema
        SpecificationService._set_schema()
        
        try:
            spec_uuid = uuid.UUID(spec_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import Specification
        specification = Specification.query.get(spec_uuid)
        if not specification:
            raise ValueError('规格不存在')
        
        # 检查规格名称是否重复（排除自己）
        if 'spec_name' in data and data['spec_name'] != specification.spec_name:
            existing = Specification.query.filter(
                and_(
                    Specification.spec_name == data['spec_name'],
                    Specification.id != spec_uuid
                )
            ).first()
            if existing:
                raise ValueError('规格名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(specification, key):
                setattr(specification, key, value)
        
        specification.updated_by = updated_by_uuid
        
        # 重新计算面积和格式
        specification.calculate_area_and_format()
        
        try:
            db.session.commit()
            return specification.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新规格失败: {str(e)}')
    
    @staticmethod
    def delete_specification(spec_id):
        """删除规格"""
        # 设置schema
        SpecificationService._set_schema()
        
        try:
            spec_uuid = uuid.UUID(spec_id)
        except ValueError:
            raise ValueError('无效的规格ID')
        
        from app.models.basic_data import Specification
        specification = Specification.query.get(spec_uuid)
        if not specification:
            raise ValueError('规格不存在')
        
        try:
            db.session.delete(specification)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除规格失败: {str(e)}')
    
    @staticmethod
    def batch_update_specifications(data_list, updated_by):
        """批量更新规格（用于可编辑表格）"""
        # 设置schema
        SpecificationService._set_schema()
        
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
                    specification = SpecificationService.update_specification(
                        data['id'], data, updated_by
                    )
                    results.append(specification)
                else:
                    # 创建新记录
                    specification = SpecificationService.create_specification(
                        data, updated_by
                    )
                    results.append(specification)
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
    def get_enabled_specifications():
        """获取启用的规格列表（用于下拉选择）"""
        # 设置schema
        SpecificationService._set_schema()
        
        from app.models.basic_data import Specification
        specifications = Specification.query.filter_by(
            is_enabled=True
        ).order_by(Specification.sort_order, Specification.spec_name).all()
        
        return [spec.to_dict() for spec in specifications] 

# 币别管理API
class CurrencyService:
    """币别管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in CurrencyService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_currencies(page=1, per_page=20, search=None, enabled_only=False):
        """获取币别列表"""
        # 设置schema
        CurrencyService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, currency_code, currency_name, exchange_rate, is_base_currency,
            description, sort_order, is_enabled, created_by, updated_by, 
            created_at, updated_at
        FROM {schema_name}.currencies
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (currency_code ILIKE :search OR 
                 currency_name ILIKE :search OR 
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
        FROM {schema_name}.currencies
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
            
            currencies = []
            for row in rows:
                currency_data = {
                    'id': str(row.id),
                    'currency_code': row.currency_code,
                    'currency_name': row.currency_name,
                    'exchange_rate': float(row.exchange_rate) if row.exchange_rate else None,
                    'is_base_currency': row.is_base_currency,
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
                        currency_data['created_by_name'] = created_user.get_full_name()
                    else:
                        currency_data['created_by_name'] = '未知用户'
                else:
                    currency_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        currency_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        currency_data['updated_by_name'] = '未知用户'
                else:
                    currency_data['updated_by_name'] = ''
                
                currencies.append(currency_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'currencies': currencies,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying currencies: {str(e)}")
            raise ValueError(f'查询币别失败: {str(e)}')
    
    @staticmethod
    def get_currency(currency_id):
        """获取币别详情"""
        # 设置schema
        CurrencyService._set_schema()
        
        try:
            currency_uuid = uuid.UUID(currency_id)
        except ValueError:
            raise ValueError('无效的币别ID')
        
        from app.models.basic_data import Currency
        currency = Currency.query.get(currency_uuid)
        if not currency:
            raise ValueError('币别不存在')
        
        currency_data = currency.to_dict()
        
        # 获取创建人和修改人用户名
        if currency.created_by:
            created_user = User.query.get(currency.created_by)
            if created_user:
                currency_data['created_by_name'] = created_user.get_full_name()
            else:
                currency_data['created_by_name'] = '未知用户'
        
        if currency.updated_by:
            updated_user = User.query.get(currency.updated_by)
            if updated_user:
                currency_data['updated_by_name'] = updated_user.get_full_name()
            else:
                currency_data['updated_by_name'] = '未知用户'
        
        return currency_data
    
    @staticmethod
    def create_currency(data, created_by):
        """创建币别"""
        # 设置schema
        CurrencyService._set_schema()
        
        # 验证数据
        if not data.get('currency_code'):
            raise ValueError('币别代码不能为空')
        
        if not data.get('currency_name'):
            raise ValueError('币别名称不能为空')
        
        if not data.get('exchange_rate'):
            raise ValueError('汇率不能为空')
        
        from app.models.basic_data import Currency
        
        # 检查币别代码是否重复
        existing = Currency.query.filter_by(
            currency_code=data['currency_code']
        ).first()
        if existing:
            raise ValueError('币别代码已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建币别
        currency = Currency(
            currency_code=data['currency_code'],
            currency_name=data['currency_name'],
            exchange_rate=data['exchange_rate'],
            is_base_currency=data.get('is_base_currency', False),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid,
            updated_by=created_by_uuid
        )
        
        # 如果设置为本位币，需要取消其他币别的本位币标记
        if currency.is_base_currency:
            Currency.query.filter_by(is_base_currency=True).update({'is_base_currency': False})
        
        try:
            db.session.add(currency)
            db.session.commit()
            return currency.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建币别失败: {str(e)}')
    
    @staticmethod
    def update_currency(currency_id, data, updated_by):
        """更新币别"""
        # 设置schema
        CurrencyService._set_schema()
        
        try:
            currency_uuid = uuid.UUID(currency_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import Currency
        currency = Currency.query.get(currency_uuid)
        if not currency:
            raise ValueError('币别不存在')
        
        # 检查币别代码是否重复（排除自己）
        if 'currency_code' in data and data['currency_code'] != currency.currency_code:
            existing = Currency.query.filter(
                Currency.currency_code == data['currency_code'],
                Currency.id != currency_uuid
            ).first()
            if existing:
                raise ValueError('币别代码已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(currency, key):
                setattr(currency, key, value)
        
        currency.updated_by = updated_by_uuid
        
        # 如果设置为本位币，需要取消其他币别的本位币标记
        if currency.is_base_currency:
            Currency.query.filter(Currency.id != currency.id).update({'is_base_currency': False})
        
        try:
            db.session.commit()
            return currency.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新币别失败: {str(e)}')
    
    @staticmethod
    def delete_currency(currency_id):
        """删除币别"""
        # 设置schema
        CurrencyService._set_schema()
        
        try:
            currency_uuid = uuid.UUID(currency_id)
        except ValueError:
            raise ValueError('无效的币别ID')
        
        from app.models.basic_data import Currency
        currency = Currency.query.get(currency_uuid)
        if not currency:
            raise ValueError('币别不存在')
        
        # 检查是否为本位币（本位币不允许删除）
        if currency.is_base_currency:
            raise ValueError('本位币不允许删除')
        
        try:
            db.session.delete(currency)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除币别失败: {str(e)}')
    
    @staticmethod
    def set_base_currency(currency_id):
        """设置为本位币"""
        # 设置schema
        CurrencyService._set_schema()
        
        try:
            currency_uuid = uuid.UUID(currency_id)
        except ValueError:
            raise ValueError('无效的币别ID')
        
        from app.models.basic_data import Currency
        currency = Currency.query.get(currency_uuid)
        if not currency:
            raise ValueError('币别不存在')
        
        try:
            currency.set_as_base_currency()
            return currency.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'设置本位币失败: {str(e)}')
    
    @staticmethod
    def batch_update_currencies(data_list, updated_by):
        """批量更新币别（用于可编辑表格）"""
        # 设置schema
        CurrencyService._set_schema()
        
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
                    currency = CurrencyService.update_currency(
                        data['id'], data, updated_by
                    )
                    results.append(currency)
                else:
                    # 创建新记录
                    currency = CurrencyService.create_currency(
                        data, updated_by
                    )
                    results.append(currency)
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
    def get_enabled_currencies():
        """获取启用的币别列表（用于下拉选择）"""
        # 设置schema
        CurrencyService._set_schema()
        
        from app.models.basic_data import Currency
        currencies = Currency.query.filter_by(
            is_enabled=True
        ).order_by(Currency.sort_order, Currency.currency_name).all()
        
        return [currency.to_dict() for currency in currencies]


class TaxRateService:
    """税率管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in TaxRateService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_tax_rates(page=1, per_page=20, search=None, enabled_only=False):
        """获取税率列表"""
        # 设置schema
        TaxRateService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, tax_name, tax_rate, is_default, description, sort_order, 
            is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.tax_rates
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (tax_name ILIKE :search OR 
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
        FROM {schema_name}.tax_rates
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
            
            tax_rates = []
            for row in rows:
                tax_rate_data = {
                    'id': str(row.id),
                    'tax_name': row.tax_name,
                    'tax_rate': float(row.tax_rate) if row.tax_rate else 0,
                    'is_default': row.is_default,
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
                        tax_rate_data['created_by_name'] = created_user.get_full_name()
                    else:
                        tax_rate_data['created_by_name'] = '未知用户'
                else:
                    tax_rate_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        tax_rate_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        tax_rate_data['updated_by_name'] = '未知用户'
                else:
                    tax_rate_data['updated_by_name'] = ''
                
                tax_rates.append(tax_rate_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'tax_rates': tax_rates,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying tax rates: {str(e)}")
            raise ValueError(f'查询税率失败: {str(e)}')
    
    @staticmethod
    def get_tax_rate(tax_rate_id):
        """获取税率详情"""
        # 设置schema
        TaxRateService._set_schema()
        
        try:
            tax_rate_uuid = uuid.UUID(tax_rate_id)
        except ValueError:
            raise ValueError('无效的税率ID')
        
        from app.models.basic_data import TaxRate
        tax_rate = TaxRate.query.get(tax_rate_uuid)
        if not tax_rate:
            raise ValueError('税率不存在')
        
        tax_rate_data = tax_rate.to_dict()
        
        # 获取创建人和修改人用户名
        if tax_rate.created_by:
            created_user = User.query.get(tax_rate.created_by)
            if created_user:
                tax_rate_data['created_by_name'] = created_user.get_full_name()
            else:
                tax_rate_data['created_by_name'] = '未知用户'
        
        if tax_rate.updated_by:
            updated_user = User.query.get(tax_rate.updated_by)
            if updated_user:
                tax_rate_data['updated_by_name'] = updated_user.get_full_name()
            else:
                tax_rate_data['updated_by_name'] = '未知用户'
        
        return tax_rate_data
    
    @staticmethod
    def create_tax_rate(data, created_by):
        """创建税率"""
        # 设置schema
        TaxRateService._set_schema()
        
        # 验证数据
        if not data.get('tax_name'):
            raise ValueError('税收名称不能为空')
        
        if data.get('tax_rate') is None:
            raise ValueError('税率不能为空')
        
        from app.models.basic_data import TaxRate
        
        # 检查税收名称是否重复
        existing = TaxRate.query.filter_by(
            tax_name=data['tax_name']
        ).first()
        if existing:
            raise ValueError('税收名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建税率
        tax_rate = TaxRate(
            tax_name=data['tax_name'],
            tax_rate=data['tax_rate'],
            is_default=data.get('is_default', False),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        # 如果设置为默认，需要取消其他税率的默认标记
        if tax_rate.is_default:
            TaxRate.query.filter_by(is_default=True).update({'is_default': False})
        
        try:
            db.session.add(tax_rate)
            db.session.commit()
            return tax_rate.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建税率失败: {str(e)}')
    
    @staticmethod
    def update_tax_rate(tax_rate_id, data, updated_by):
        """更新税率"""
        # 设置schema
        TaxRateService._set_schema()
        
        try:
            tax_rate_uuid = uuid.UUID(tax_rate_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import TaxRate
        tax_rate = TaxRate.query.get(tax_rate_uuid)
        if not tax_rate:
            raise ValueError('税率不存在')
        
        # 检查税收名称是否重复（排除自己）
        if 'tax_name' in data and data['tax_name'] != tax_rate.tax_name:
            existing = TaxRate.query.filter(
                TaxRate.tax_name == data['tax_name'],
                TaxRate.id != tax_rate_uuid
            ).first()
            if existing:
                raise ValueError('税收名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(tax_rate, key):
                setattr(tax_rate, key, value)
        
        tax_rate.updated_by = updated_by_uuid
        
        # 如果设置为默认，需要取消其他税率的默认标记
        if tax_rate.is_default:
            TaxRate.query.filter(TaxRate.id != tax_rate.id).update({'is_default': False})
        
        try:
            db.session.commit()
            return tax_rate.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新税率失败: {str(e)}')
    
    @staticmethod
    def delete_tax_rate(tax_rate_id):
        """删除税率"""
        # 设置schema
        TaxRateService._set_schema()
        
        try:
            tax_rate_uuid = uuid.UUID(tax_rate_id)
        except ValueError:
            raise ValueError('无效的税率ID')
        
        from app.models.basic_data import TaxRate
        tax_rate = TaxRate.query.get(tax_rate_uuid)
        if not tax_rate:
            raise ValueError('税率不存在')
        
        try:
            db.session.delete(tax_rate)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除税率失败: {str(e)}')
    
    @staticmethod
    def set_default_tax_rate(tax_rate_id):
        """设置为默认税率"""
        # 设置schema
        TaxRateService._set_schema()
        
        try:
            tax_rate_uuid = uuid.UUID(tax_rate_id)
        except ValueError:
            raise ValueError('无效的税率ID')
        
        from app.models.basic_data import TaxRate
        tax_rate = TaxRate.query.get(tax_rate_uuid)
        if not tax_rate:
            raise ValueError('税率不存在')
        
        try:
            tax_rate.set_as_default()
            return tax_rate.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'设置默认税率失败: {str(e)}')
    
    @staticmethod
    def batch_update_tax_rates(data_list, updated_by):
        """批量更新税率（用于可编辑表格）"""
        # 设置schema
        TaxRateService._set_schema()
        
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
                    tax_rate = TaxRateService.update_tax_rate(
                        data['id'], data, updated_by
                    )
                    results.append(tax_rate)
                else:
                    # 创建新记录
                    tax_rate = TaxRateService.create_tax_rate(
                        data, updated_by
                    )
                    results.append(tax_rate)
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
    def get_enabled_tax_rates():
        """获取启用的税率列表（用于下拉选择）"""
        # 设置schema
        TaxRateService._set_schema()
        
        from app.models.basic_data import TaxRate
        tax_rates = TaxRate.query.filter_by(
            is_enabled=True
        ).order_by(TaxRate.sort_order, TaxRate.tax_name).all()
        
        return [tax_rate.to_dict() for tax_rate in tax_rates]


class SettlementMethodService:
    """结算方式服务类"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in SettlementMethodService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_settlement_methods(page=1, per_page=20, search=None, enabled_only=False):
        """获取结算方式列表"""
        # 设置schema
        SettlementMethodService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, settlement_name, description, sort_order, is_enabled,
            created_by, updated_by, created_at, updated_at
        FROM {schema_name}.settlement_methods
        """
        
        # 构建查询条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (settlement_name ILIKE :search OR 
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
        FROM {schema_name}.settlement_methods
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
            
            settlement_methods = []
            for row in rows:
                settlement_method_data = {
                    'id': str(row.id),
                    'settlement_name': row.settlement_name,
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
                        settlement_method_data['created_by_name'] = created_user.get_full_name()
                    else:
                        settlement_method_data['created_by_name'] = '未知用户'
                else:
                    settlement_method_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        settlement_method_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        settlement_method_data['updated_by_name'] = '未知用户'
                else:
                    settlement_method_data['updated_by_name'] = ''
                
                settlement_methods.append(settlement_method_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'settlement_methods': settlement_methods,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying settlement methods: {str(e)}")
            raise ValueError(f'查询结算方式失败: {str(e)}')
    
    @staticmethod
    def get_settlement_method(settlement_method_id):
        """获取结算方式详情"""
        # 设置schema
        SettlementMethodService._set_schema()
        
        try:
            settlement_method_uuid = uuid.UUID(settlement_method_id)
        except ValueError:
            raise ValueError('无效的结算方式ID')
        
        from app.models.basic_data import SettlementMethod
        settlement_method = SettlementMethod.query.get(settlement_method_uuid)
        if not settlement_method:
            raise ValueError('结算方式不存在')
        
        settlement_method_data = settlement_method.to_dict()
        
        # 获取创建人和修改人用户名
        if settlement_method.created_by:
            created_user = User.query.get(settlement_method.created_by)
            if created_user:
                settlement_method_data['created_by_name'] = created_user.get_full_name()
            else:
                settlement_method_data['created_by_name'] = '未知用户'
        
        if settlement_method.updated_by:
            updated_user = User.query.get(settlement_method.updated_by)
            if updated_user:
                settlement_method_data['updated_by_name'] = updated_user.get_full_name()
            else:
                settlement_method_data['updated_by_name'] = '未知用户'
        
        return settlement_method_data
    
    @staticmethod
    def create_settlement_method(data, created_by):
        """创建结算方式"""
        # 设置schema
        SettlementMethodService._set_schema()
        
        # 验证数据
        if not data.get('settlement_name'):
            raise ValueError('结算方式名称不能为空')
        
        from app.models.basic_data import SettlementMethod
        
        # 检查结算方式名称是否重复
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        check_query = f"""
        SELECT COUNT(*) as count
        FROM {schema_name}.settlement_methods
        WHERE settlement_name = :settlement_name
        """
        result = db.session.execute(text(check_query), {'settlement_name': data['settlement_name']})
        if result.scalar() > 0:
            raise ValueError('结算方式名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建结算方式
        settlement_method = SettlementMethod(
            settlement_name=data['settlement_name'],
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(settlement_method)
            db.session.commit()
            return settlement_method.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建结算方式失败: {str(e)}')
    
    @staticmethod
    def update_settlement_method(settlement_method_id, data, updated_by):
        """更新结算方式"""
        # 设置schema
        SettlementMethodService._set_schema()
        
        try:
            settlement_method_uuid = uuid.UUID(settlement_method_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import SettlementMethod
        settlement_method = SettlementMethod.query.get(settlement_method_uuid)
        if not settlement_method:
            raise ValueError('结算方式不存在')
        
        # 检查结算方式名称是否重复（排除自己）
        if 'settlement_name' in data and data['settlement_name'] != settlement_method.settlement_name:
            existing = SettlementMethod.query.filter(
                and_(
                    SettlementMethod.settlement_name == data['settlement_name'],
                    SettlementMethod.id != settlement_method_uuid
                )
            ).first()
            if existing:
                raise ValueError('结算方式名称已存在')
        
        # 更新字段
        if 'settlement_name' in data:
            settlement_method.settlement_name = data['settlement_name']
        if 'description' in data:
            settlement_method.description = data['description']
        if 'sort_order' in data:
            settlement_method.sort_order = data['sort_order']
        if 'is_enabled' in data:
            settlement_method.is_enabled = data['is_enabled']
        
        settlement_method.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return settlement_method.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新结算方式失败: {str(e)}')
    
    @staticmethod
    def delete_settlement_method(settlement_method_id):
        """删除结算方式"""
        # 设置schema
        SettlementMethodService._set_schema()
        
        try:
            settlement_method_uuid = uuid.UUID(settlement_method_id)
        except ValueError:
            raise ValueError('无效的结算方式ID')
        
        from app.models.basic_data import SettlementMethod
        settlement_method = SettlementMethod.query.get(settlement_method_uuid)
        if not settlement_method:
            raise ValueError('结算方式不存在')
        
        try:
            db.session.delete(settlement_method)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除结算方式失败: {str(e)}')
    
    @staticmethod
    def batch_update_settlement_methods(data_list, updated_by):
        """批量更新结算方式"""
        # 设置schema
        SettlementMethodService._set_schema()
        
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的更新用户ID')
        
        results = []
        
        for data in data_list:
            try:
                if data.get('id') and not data['id'].startswith('temp_'):
                    # 更新现有记录
                    result = SettlementMethodService.update_settlement_method(data['id'], data, updated_by)
                else:
                    # 创建新记录
                    result = SettlementMethodService.create_settlement_method(data, updated_by)
                results.append(result)
            except Exception as e:
                current_app.logger.error(f"Error processing settlement method {data.get('id', 'new')}: {str(e)}")
                continue
        
        return results
    
    @staticmethod
    def get_enabled_settlement_methods():
        """获取启用的结算方式列表"""
        # 设置schema
        SettlementMethodService._set_schema()
        
        from app.models.basic_data import SettlementMethod
        settlement_methods = SettlementMethod.query.filter_by(is_enabled=True).order_by(SettlementMethod.sort_order, SettlementMethod.created_at).all()
        return [sm.to_dict() for sm in settlement_methods]


class AccountManagementService:
    """账户管理服务类"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in AccountManagementService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_accounts(page=1, per_page=20, search=None, enabled_only=False):
        """获取账户列表"""
        # 设置schema
        AccountManagementService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            a.id, a.account_name, a.account_type, a.currency_id, a.bank_name, 
            a.bank_account, a.opening_date, a.opening_address, a.description, 
            a.sort_order, a.is_enabled, a.created_by, a.updated_by, 
            a.created_at, a.updated_at,
            c.currency_name, c.currency_code
        FROM {schema_name}.account_management a
        LEFT JOIN {schema_name}.currencies c ON a.currency_id = c.id
        """
        
        # 构建查询条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (a.account_name ILIKE :search OR 
                 a.account_type ILIKE :search OR
                 a.bank_name ILIKE :search OR
                 a.bank_account ILIKE :search OR
                 a.description ILIKE :search)
            """)
            params['search'] = f'%{search}%'
        
        if enabled_only:
            where_conditions.append("a.is_enabled = true")
        
        # 构建完整查询
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        base_query += " ORDER BY a.sort_order, a.created_at"
        
        # 计算总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM {schema_name}.account_management a
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
            
            accounts = []
            for row in rows:
                account_data = {
                    'id': str(row.id),
                    'account_name': row.account_name,
                    'account_type': row.account_type,
                    'currency_id': str(row.currency_id) if row.currency_id else None,
                    'currency_name': row.currency_name,
                    'currency_code': row.currency_code,
                    'bank_name': row.bank_name,
                    'bank_account': row.bank_account,
                    'opening_date': row.opening_date.isoformat() if row.opening_date else None,
                    'opening_address': row.opening_address,
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
                        account_data['created_by_name'] = created_user.get_full_name()
                    else:
                        account_data['created_by_name'] = '未知用户'
                else:
                    account_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        account_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        account_data['updated_by_name'] = '未知用户'
                else:
                    account_data['updated_by_name'] = ''
                
                accounts.append(account_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'accounts': accounts,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying accounts: {str(e)}")
            raise ValueError(f'查询账户失败: {str(e)}')
    
    @staticmethod
    def get_account(account_id):
        """获取账户详情"""
        # 设置schema
        AccountManagementService._set_schema()
        
        try:
            account_uuid = uuid.UUID(account_id)
        except ValueError:
            raise ValueError('无效的账户ID')
        
        from app.models.basic_data import AccountManagement
        account = AccountManagement.query.get(account_uuid)
        if not account:
            raise ValueError('账户不存在')
        
        account_data = account.to_dict()
        
        # 获取创建人和修改人用户名
        if account.created_by:
            created_user = User.query.get(account.created_by)
            if created_user:
                account_data['created_by_name'] = created_user.get_full_name()
            else:
                account_data['created_by_name'] = '未知用户'
        
        if account.updated_by:
            updated_user = User.query.get(account.updated_by)
            if updated_user:
                account_data['updated_by_name'] = updated_user.get_full_name()
            else:
                account_data['updated_by_name'] = '未知用户'
        
        return account_data
    
    @staticmethod
    def create_account(data, created_by):
        """创建账户"""
        # 设置schema
        AccountManagementService._set_schema()
        
        # 验证数据
        if not data.get('account_name'):
            raise ValueError('账户名称不能为空')
        
        if not data.get('account_type'):
            raise ValueError('账户类型不能为空')
        
        from app.models.basic_data import AccountManagement
        
        # 检查账户名称是否重复
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        check_query = f"""
        SELECT COUNT(*) as count
        FROM {schema_name}.account_management
        WHERE account_name = :account_name
        """
        result = db.session.execute(text(check_query), {'account_name': data['account_name']})
        if result.scalar() > 0:
            raise ValueError('账户名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 处理币别ID
        currency_id = None
        if data.get('currency_id'):
            try:
                currency_id = uuid.UUID(data['currency_id'])
            except ValueError:
                raise ValueError('无效的币别ID')
        
        # 处理开户日期
        opening_date = None
        if data.get('opening_date'):
            from datetime import datetime
            try:
                opening_date = datetime.fromisoformat(data['opening_date'].replace('Z', '+00:00')).date()
            except ValueError:
                raise ValueError('无效的开户日期格式')
        
        # 创建账户
        account = AccountManagement(
            account_name=data['account_name'],
            account_type=data['account_type'],
            currency_id=currency_id,
            bank_name=data.get('bank_name'),
            bank_account=data.get('bank_account'),
            opening_date=opening_date,
            opening_address=data.get('opening_address'),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(account)
            db.session.commit()
            return account.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建账户失败: {str(e)}')
    
    @staticmethod
    def update_account(account_id, data, updated_by):
        """更新账户"""
        # 设置schema
        AccountManagementService._set_schema()
        
        try:
            account_uuid = uuid.UUID(account_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import AccountManagement
        account = AccountManagement.query.get(account_uuid)
        if not account:
            raise ValueError('账户不存在')
        
        # 检查账户名称是否重复（排除自己）
        if 'account_name' in data and data['account_name'] != account.account_name:
            existing = AccountManagement.query.filter(
                and_(
                    AccountManagement.account_name == data['account_name'],
                    AccountManagement.id != account_uuid
                )
            ).first()
            if existing:
                raise ValueError('账户名称已存在')
        
        # 更新字段
        if 'account_name' in data:
            account.account_name = data['account_name']
        if 'account_type' in data:
            account.account_type = data['account_type']
        if 'currency_id' in data:
            if data['currency_id']:
                try:
                    account.currency_id = uuid.UUID(data['currency_id'])
                except ValueError:
                    raise ValueError('无效的币别ID')
            else:
                account.currency_id = None
        if 'bank_name' in data:
            account.bank_name = data['bank_name']
        if 'bank_account' in data:
            account.bank_account = data['bank_account']
        if 'opening_date' in data:
            if data['opening_date']:
                from datetime import datetime
                try:
                    account.opening_date = datetime.fromisoformat(data['opening_date'].replace('Z', '+00:00')).date()
                except ValueError:
                    raise ValueError('无效的开户日期格式')
            else:
                account.opening_date = None
        if 'opening_address' in data:
            account.opening_address = data['opening_address']
        if 'description' in data:
            account.description = data['description']
        if 'sort_order' in data:
            account.sort_order = data['sort_order']
        if 'is_enabled' in data:
            account.is_enabled = data['is_enabled']
        
        account.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return account.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新账户失败: {str(e)}')
    
    @staticmethod
    def delete_account(account_id):
        """删除账户"""
        # 设置schema
        AccountManagementService._set_schema()
        
        try:
            account_uuid = uuid.UUID(account_id)
        except ValueError:
            raise ValueError('无效的账户ID')
        
        from app.models.basic_data import AccountManagement
        account = AccountManagement.query.get(account_uuid)
        if not account:
            raise ValueError('账户不存在')
        
        try:
            db.session.delete(account)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除账户失败: {str(e)}')
    
    @staticmethod
    def batch_update_accounts(data_list, updated_by):
        """批量更新账户"""
        # 设置schema
        AccountManagementService._set_schema()
        
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的更新用户ID')
        
        results = []
        
        for data in data_list:
            try:
                if data.get('id') and not data['id'].startswith('temp_'):
                    # 更新现有记录
                    result = AccountManagementService.update_account(data['id'], data, updated_by)
                else:
                    # 创建新记录
                    result = AccountManagementService.create_account(data, updated_by)
                results.append(result)
            except Exception as e:
                current_app.logger.error(f"Error processing account {data.get('id', 'new')}: {str(e)}")
                continue
        
        return results
    
    @staticmethod
    def get_enabled_accounts():
        """获取启用的账户列表"""
        # 设置schema
        AccountManagementService._set_schema()
        
        from app.models.basic_data import AccountManagement
        accounts = AccountManagement.query.filter_by(is_enabled=True).order_by(AccountManagement.sort_order, AccountManagement.created_at).all()
        return [account.to_dict() for account in accounts]


class PaymentMethodService:
    """付款方式管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in PaymentMethodService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_payment_methods(page=1, per_page=20, search=None, enabled_only=False):
        """获取付款方式列表"""
        # 设置schema
        PaymentMethodService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, payment_name, cash_on_delivery, monthly_settlement, next_month_settlement,
            cash_on_delivery_days, monthly_settlement_days, monthly_reconciliation_day,
            next_month_settlement_count, monthly_payment_day, description, sort_order, 
            is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.payment_methods
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (payment_name ILIKE :search OR 
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
        FROM {schema_name}.payment_methods
        """
        if where_conditions:
            count_query += " WHERE " + " AND ".join(where_conditions)
        
        # 执行查询
        try:
            # 获取总数
            count_result = db.session.execute(text(count_query), params)
            total = count_result.scalar()
            
            # 添加分页
            offset = (page - 1) * per_page
            base_query += f" LIMIT {per_page} OFFSET {offset}"
            
            # 获取数据
            result = db.session.execute(text(base_query), params)
            payment_methods = []
            
            for row in result:
                payment_method_dict = {
                    'id': str(row.id),
                    'payment_name': row.payment_name,
                    'cash_on_delivery': row.cash_on_delivery,
                    'monthly_settlement': row.monthly_settlement,
                    'next_month_settlement': row.next_month_settlement,
                    'cash_on_delivery_days': row.cash_on_delivery_days,
                    'monthly_settlement_days': row.monthly_settlement_days,
                    'monthly_reconciliation_day': row.monthly_reconciliation_day,
                    'next_month_settlement_count': row.next_month_settlement_count,
                    'monthly_payment_day': row.monthly_payment_day,
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
                        payment_method_dict['created_by_name'] = created_user.get_full_name()
                    else:
                        payment_method_dict['created_by_name'] = '未知用户'
                else:
                    payment_method_dict['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        payment_method_dict['updated_by_name'] = updated_user.get_full_name()
                    else:
                        payment_method_dict['updated_by_name'] = '未知用户'
                else:
                    payment_method_dict['updated_by_name'] = ''
                
                payment_methods.append(payment_method_dict)
            
            return {
                'payment_methods': payment_methods,
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting payment methods: {str(e)}")
            raise ValueError(f'获取付款方式列表失败: {str(e)}')
    
    @staticmethod
    def get_payment_method(payment_method_id):
        """获取单个付款方式"""
        # 设置schema
        PaymentMethodService._set_schema()
        
        try:
            payment_method_uuid = uuid.UUID(payment_method_id)
        except ValueError:
            raise ValueError('无效的付款方式ID')
        
        from app.models.basic_data import PaymentMethod
        payment_method = PaymentMethod.query.get(payment_method_uuid)
        if not payment_method:
            raise ValueError('付款方式不存在')
        
        payment_method_data = payment_method.to_dict()
        
        # 获取创建人和修改人用户名
        if payment_method.created_by:
            created_user = User.query.get(payment_method.created_by)
            if created_user:
                payment_method_data['created_by_name'] = created_user.get_full_name()
            else:
                payment_method_data['created_by_name'] = '未知用户'
        else:
            payment_method_data['created_by_name'] = '系统'
        
        if payment_method.updated_by:
            updated_user = User.query.get(payment_method.updated_by)
            if updated_user:
                payment_method_data['updated_by_name'] = updated_user.get_full_name()
            else:
                payment_method_data['updated_by_name'] = '未知用户'
        else:
            payment_method_data['updated_by_name'] = ''
        
        return payment_method_data
    
    @staticmethod
    def create_payment_method(data, created_by):
        """创建付款方式"""
        # 设置schema
        PaymentMethodService._set_schema()
        
        # 验证数据
        if not data.get('payment_name'):
            raise ValueError('付款方式名称不能为空')
        
        # 验证付款方式类型：必须选择一个且只能选择一个
        payment_types = [
            data.get('cash_on_delivery', False),
            data.get('monthly_settlement', False),
            data.get('next_month_settlement', False)
        ]
        selected_count = sum(payment_types)
        
        if selected_count == 0:
            raise ValueError('请选择一种付款方式类型（货到付款、月结或次月结）')
        
        if selected_count > 1:
            raise ValueError('只能选择一种付款方式类型')
        
        from app.models.basic_data import PaymentMethod
        
        # 检查付款方式名称是否重复
        existing = PaymentMethod.query.filter_by(
            payment_name=data['payment_name']
        ).first()
        if existing:
            raise ValueError('付款方式名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建付款方式
        payment_method = PaymentMethod(
            payment_name=data['payment_name'],
            cash_on_delivery=data.get('cash_on_delivery', False),
            monthly_settlement=data.get('monthly_settlement', False),
            next_month_settlement=data.get('next_month_settlement', False),
            cash_on_delivery_days=data.get('cash_on_delivery_days', 0),
            monthly_settlement_days=data.get('monthly_settlement_days', 0),
            monthly_reconciliation_day=data.get('monthly_reconciliation_day', 0),
            next_month_settlement_count=data.get('next_month_settlement_count', 0),
            monthly_payment_day=data.get('monthly_payment_day', 0),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(payment_method)
            db.session.commit()
            return payment_method.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建付款方式失败: {str(e)}')
    
    @staticmethod
    def update_payment_method(payment_method_id, data, updated_by):
        """更新付款方式"""
        # 设置schema
        PaymentMethodService._set_schema()
        
        try:
            payment_method_uuid = uuid.UUID(payment_method_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import PaymentMethod
        payment_method = PaymentMethod.query.get(payment_method_uuid)
        if not payment_method:
            raise ValueError('付款方式不存在')
        
        # 验证付款方式类型：必须选择一个且只能选择一个
        # 获取当前值或使用传入的新值
        cash_on_delivery = data.get('cash_on_delivery', payment_method.cash_on_delivery)
        monthly_settlement = data.get('monthly_settlement', payment_method.monthly_settlement)
        next_month_settlement = data.get('next_month_settlement', payment_method.next_month_settlement)
        
        payment_types = [cash_on_delivery, monthly_settlement, next_month_settlement]
        selected_count = sum(payment_types)
        
        if selected_count == 0:
            raise ValueError('请选择一种付款方式类型（货到付款、月结或次月结）')
        
        if selected_count > 1:
            raise ValueError('只能选择一种付款方式类型')
        
        # 检查付款方式名称是否重复（排除自己）
        if 'payment_name' in data and data['payment_name'] != payment_method.payment_name:
            existing = PaymentMethod.query.filter(
                PaymentMethod.payment_name == data['payment_name'],
                PaymentMethod.id != payment_method_uuid
            ).first()
            if existing:
                raise ValueError('付款方式名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(payment_method, key):
                setattr(payment_method, key, value)
        
        payment_method.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return payment_method.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新付款方式失败: {str(e)}')
    
    @staticmethod
    def delete_payment_method(payment_method_id):
        """删除付款方式"""
        # 设置schema
        PaymentMethodService._set_schema()
        
        try:
            payment_method_uuid = uuid.UUID(payment_method_id)
        except ValueError:
            raise ValueError('无效的付款方式ID')
        
        from app.models.basic_data import PaymentMethod
        payment_method = PaymentMethod.query.get(payment_method_uuid)
        if not payment_method:
            raise ValueError('付款方式不存在')
        
        try:
            db.session.delete(payment_method)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除付款方式失败: {str(e)}')
    
    @staticmethod
    def batch_update_payment_methods(data_list, updated_by):
        """批量更新付款方式"""
        # 设置schema
        PaymentMethodService._set_schema()
        
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
                    payment_method = PaymentMethodService.update_payment_method(
                        data['id'], data, updated_by
                    )
                    results.append(payment_method)
                else:
                    # 创建新记录
                    payment_method = PaymentMethodService.create_payment_method(
                        data, updated_by
                    )
                    results.append(payment_method)
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
    def get_enabled_payment_methods():
        """获取启用的付款方式列表（用于下拉选择）"""
        # 设置schema
        PaymentMethodService._set_schema()
        
        from app.models.basic_data import PaymentMethod
        payment_methods = PaymentMethod.query.filter_by(
            is_enabled=True
        ).order_by(PaymentMethod.sort_order, PaymentMethod.payment_name).all()
        
        return [payment_method.to_dict() for payment_method in payment_methods]


class InkOptionService:
    """油墨选项管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in InkOptionService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_ink_options(page=1, per_page=20, search=None, enabled_only=False):
        """获取油墨选项列表"""
        # 设置schema
        InkOptionService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, option_name, sort_order, 
            is_enabled, description, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.ink_options
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (option_name ILIKE :search OR 
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
        FROM {schema_name}.ink_options
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
            
            ink_options = []
            for row in rows:
                option_data = {
                    'id': str(row.id),
                    'option_name': row.option_name,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'description': row.description,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
                
                # 获取创建人和修改人用户名
                if row.created_by:
                    created_user = User.query.get(row.created_by)
                    if created_user:
                        option_data['created_by_name'] = created_user.get_full_name()
                    else:
                        option_data['created_by_name'] = '未知用户'
                else:
                    option_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        option_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        option_data['updated_by_name'] = '未知用户'
                else:
                    option_data['updated_by_name'] = ''
                
                ink_options.append(option_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'ink_options': ink_options,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying ink options: {str(e)}")
            raise ValueError(f'查询油墨选项失败: {str(e)}')
    
    @staticmethod
    def get_ink_option(option_id):
        """获取油墨选项详情"""
        # 设置schema
        InkOptionService._set_schema()
        
        try:
            option_uuid = uuid.UUID(option_id)
        except ValueError:
            raise ValueError('无效的油墨选项ID')
        
        from app.models.basic_data import InkOption
        option = InkOption.query.get(option_uuid)
        if not option:
            raise ValueError('油墨选项不存在')
        
        option_data = option.to_dict()
        
        # 获取创建人和修改人用户名
        if option.created_by:
            created_user = User.query.get(option.created_by)
            if created_user:
                option_data['created_by_name'] = created_user.get_full_name()
            else:
                option_data['created_by_name'] = '未知用户'
        
        if option.updated_by:
            updated_user = User.query.get(option.updated_by)
            if updated_user:
                option_data['updated_by_name'] = updated_user.get_full_name()
            else:
                option_data['updated_by_name'] = '未知用户'
        
        return option_data
    
    @staticmethod
    def create_ink_option(data, created_by):
        """创建油墨选项"""
        # 设置schema
        InkOptionService._set_schema()
        
        # 验证数据
        if not data.get('option_name'):
            raise ValueError('选项名称不能为空')
        
        from app.models.basic_data import InkOption
        
        # 检查选项名称是否重复
        existing = InkOption.query.filter_by(
            option_name=data['option_name']
        ).first()
        if existing:
            raise ValueError('选项名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建油墨选项
        option = InkOption(
            option_name=data['option_name'],
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            description=data.get('description'),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(option)
            db.session.commit()
            return option.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建油墨选项失败: {str(e)}')
    
    @staticmethod
    def update_ink_option(option_id, data, updated_by):
        """更新油墨选项"""
        # 设置schema
        InkOptionService._set_schema()
        
        try:
            option_uuid = uuid.UUID(option_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import InkOption
        option = InkOption.query.get(option_uuid)
        if not option:
            raise ValueError('油墨选项不存在')
        
        # 检查选项名称是否重复（排除自己）
        if 'option_name' in data and data['option_name'] != option.option_name:
            existing = InkOption.query.filter(
                and_(
                    InkOption.option_name == data['option_name'],
                    InkOption.id != option_uuid
                )
            ).first()
            if existing:
                raise ValueError('选项名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(option, key):
                setattr(option, key, value)
        
        option.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return option.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新油墨选项失败: {str(e)}')
    
    @staticmethod
    def delete_ink_option(option_id):
        """删除油墨选项"""
        # 设置schema
        InkOptionService._set_schema()
        
        try:
            option_uuid = uuid.UUID(option_id)
        except ValueError:
            raise ValueError('无效的油墨选项ID')
        
        from app.models.basic_data import InkOption
        option = InkOption.query.get(option_uuid)
        if not option:
            raise ValueError('油墨选项不存在')
        
        try:
            db.session.delete(option)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除油墨选项失败: {str(e)}')
    
    @staticmethod
    def batch_update_ink_options(data_list, updated_by):
        """批量更新油墨选项（用于可编辑表格）"""
        # 设置schema
        InkOptionService._set_schema()
        
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
                    option = InkOptionService.update_ink_option(
                        data['id'], data, updated_by
                    )
                    results.append(option)
                else:
                    # 创建新记录
                    option = InkOptionService.create_ink_option(
                        data, updated_by
                    )
                    results.append(option)
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
    def get_enabled_ink_options():
        """获取启用的油墨选项列表（用于下拉选择）"""
        # 设置schema
        InkOptionService._set_schema()
        
        from app.models.basic_data import InkOption
        options = InkOption.query.filter_by(
            is_enabled=True
        ).order_by(InkOption.sort_order, InkOption.option_name).all()
        
        return [option.to_dict() for option in options]


class QuoteFreightService:
    """报价运费管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in QuoteFreightService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_quote_freights(page=1, per_page=20, search=None, enabled_only=False):
        """获取报价运费列表"""
        try:
            QuoteFreightService._set_schema()
            
            # 获取当前schema名称
            schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
            
            # 构建基础查询
            base_query = f"""
            SELECT 
                id, region, percentage, sort_order, is_enabled, description,
                created_by, updated_by, created_at, updated_at
            FROM {schema_name}.quote_freights
            """
            
            # 添加搜索条件
            where_conditions = []
            params = {}
            
            if search:
                where_conditions.append("""
                    (region ILIKE :search OR 
                     description ILIKE :search)
                """)
                params['search'] = f'%{search}%'
            
            if enabled_only:
                where_conditions.append("is_enabled = true")
            
            # 构建完整查询
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            base_query += " ORDER BY sort_order, region"
            
            # 计算总数
            count_query = f"""
            SELECT COUNT(*) as total
            FROM {schema_name}.quote_freights
            """
            if where_conditions:
                count_query += " WHERE " + " AND ".join(where_conditions)
            
            # 执行查询
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
            
            quote_freights = []
            for row in rows:
                freight_data = {
                    'id': str(row.id),
                    'region': row.region,
                    'percentage': float(row.percentage) if row.percentage else 0,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'description': row.description,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
                
                # 获取创建人和修改人用户名
                if row.created_by:
                    created_user = User.query.get(row.created_by)
                    if created_user:
                        freight_data['created_by_name'] = created_user.get_full_name()
                    else:
                        freight_data['created_by_name'] = '未知用户'
                else:
                    freight_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        freight_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        freight_data['updated_by_name'] = '未知用户'
                else:
                    freight_data['updated_by_name'] = ''
                
                quote_freights.append(freight_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'quote_freights': quote_freights,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying quote freights: {str(e)}")
            raise ValueError(f'查询报价运费失败: {str(e)}')
    
    @staticmethod
    def get_quote_freight(freight_id):
        """获取报价运费详情"""
        # 设置schema
        QuoteFreightService._set_schema()
        
        try:
            freight_uuid = uuid.UUID(freight_id)
        except ValueError:
            raise ValueError('无效的报价运费ID')
        
        from app.models.basic_data import QuoteFreight
        freight = QuoteFreight.query.get(freight_uuid)
        if not freight:
            raise ValueError('报价运费不存在')
        
        freight_data = freight.to_dict()
        
        # 获取创建人和修改人用户名
        if freight.created_by:
            created_user = User.query.get(freight.created_by)
            if created_user:
                freight_data['created_by_name'] = created_user.get_full_name()
            else:
                freight_data['created_by_name'] = '未知用户'
        
        if freight.updated_by:
            updated_user = User.query.get(freight.updated_by)
            if updated_user:
                freight_data['updated_by_name'] = updated_user.get_full_name()
            else:
                freight_data['updated_by_name'] = '未知用户'
        
        return freight_data
    
    @staticmethod
    def create_quote_freight(data, created_by):
        """创建报价运费"""
        try:
            QuoteFreightService._set_schema()
            
            # 验证必填字段
            if not data.get('region'):
                raise ValueError("区域不能为空")
            
            # 获取当前schema名称
            schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
            
            # 生成UUID
            freight_id = uuid.uuid4()
            
            # 构建插入SQL
            insert_sql = f"""
            INSERT INTO {schema_name}.quote_freights 
            (id, region, percentage, sort_order, is_enabled, description, created_by, updated_by, created_at, updated_at)
            VALUES 
            (:id, :region, :percentage, :sort_order, :is_enabled, :description, :created_by, :updated_by, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            
            # 准备参数
            params = {
                'id': freight_id,
                'region': data.get('region'),
                'percentage': data.get('percentage', 0),
                'sort_order': data.get('sort_order', 0),
                'is_enabled': data.get('is_enabled', True),
                'description': data.get('description', ''),
                'created_by': created_by,
                'updated_by': created_by
            }
            
            # 执行插入
            db.session.execute(text(insert_sql), params)
            db.session.commit()
            
            # 查询并返回创建的记录
            select_sql = f"""
            SELECT id, region, percentage, sort_order, is_enabled, description,
                   created_by, updated_by, created_at, updated_at
            FROM {schema_name}.quote_freights 
            WHERE id = :id
            """
            
            result = db.session.execute(text(select_sql), {'id': freight_id})
            row = result.fetchone()
            
            if row:
                return {
                    'id': str(row.id),
                    'region': row.region,
                    'percentage': float(row.percentage) if row.percentage else 0,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'description': row.description,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
            else:
                raise ValueError("创建记录后无法查询到数据")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating quote freight: {str(e)}")
            raise ValueError(f"创建报价运费失败: {str(e)}")
    
    @staticmethod
    def update_quote_freight(freight_id, data, updated_by):
        """更新报价运费"""
        try:
            QuoteFreightService._set_schema()
            
            # 获取当前schema名称
            schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
            
            # 验证记录是否存在
            check_sql = f"""
            SELECT id FROM {schema_name}.quote_freights WHERE id = :id
            """
            result = db.session.execute(text(check_sql), {'id': freight_id})
            if not result.fetchone():
                raise ValueError("报价运费不存在")
            
            # 构建更新SQL
            update_fields = []
            params = {'id': freight_id, 'updated_by': updated_by}
            
            if 'region' in data:
                update_fields.append("region = :region")
                params['region'] = data['region']
            if 'percentage' in data:
                update_fields.append("percentage = :percentage")
                params['percentage'] = data['percentage']
            if 'sort_order' in data:
                update_fields.append("sort_order = :sort_order")
                params['sort_order'] = data['sort_order']
            if 'is_enabled' in data:
                update_fields.append("is_enabled = :is_enabled")
                params['is_enabled'] = data['is_enabled']
            if 'description' in data:
                update_fields.append("description = :description")
                params['description'] = data['description']
            
            if not update_fields:
                raise ValueError("没有要更新的字段")
            
            update_fields.append("updated_by = :updated_by")
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            update_sql = f"""
            UPDATE {schema_name}.quote_freights 
            SET {', '.join(update_fields)}
            WHERE id = :id
            """
            
            # 执行更新
            db.session.execute(text(update_sql), params)
            db.session.commit()
            
            # 查询并返回更新后的记录
            select_sql = f"""
            SELECT id, region, percentage, sort_order, is_enabled, description,
                   created_by, updated_by, created_at, updated_at
            FROM {schema_name}.quote_freights 
            WHERE id = :id
            """
            
            result = db.session.execute(text(select_sql), {'id': freight_id})
            row = result.fetchone()
            
            if row:
                return {
                    'id': str(row.id),
                    'region': row.region,
                    'percentage': float(row.percentage) if row.percentage else 0,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'description': row.description,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
            else:
                raise ValueError("更新记录后无法查询到数据")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating quote freight: {str(e)}")
            raise ValueError(f"更新报价运费失败: {str(e)}")
    
    @staticmethod
    def delete_quote_freight(freight_id):
        """删除报价运费"""
        # 设置schema
        QuoteFreightService._set_schema()
        
        try:
            freight_uuid = uuid.UUID(freight_id)
        except ValueError:
            raise ValueError('无效的报价运费ID')
        
        from app.models.basic_data import QuoteFreight
        freight = QuoteFreight.query.get(freight_uuid)
        if not freight:
            raise ValueError('报价运费不存在')
        
        try:
            db.session.delete(freight)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除报价运费失败: {str(e)}')
    
    @staticmethod
    def batch_update_quote_freights(data_list, updated_by):
        """批量更新报价运费（用于可编辑表格）"""
        # 设置schema
        QuoteFreightService._set_schema()
        
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
                    freight = QuoteFreightService.update_quote_freight(
                        data['id'], data, updated_by
                    )
                    results.append(freight)
                else:
                    # 创建新记录
                    freight = QuoteFreightService.create_quote_freight(
                        data, updated_by
                    )
                    results.append(freight)
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
    def get_enabled_quote_freights():
        """获取启用的报价运费列表（用于下拉选择）"""
        # 设置schema
        QuoteFreightService._set_schema()
        
        from app.models.basic_data import QuoteFreight
        freights = QuoteFreight.query.filter_by(
            is_enabled=True
        ).order_by(QuoteFreight.sort_order, QuoteFreight.region).all()
        
        return [freight.to_dict() for freight in freights]


class ProductCategoryService:
    """产品分类管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in ProductCategoryService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_product_categories(page=1, per_page=20, search=None, enabled_only=False):
        """获取产品分类列表"""
        # 设置schema
        ProductCategoryService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, category_name, subject_name, is_blown_film, delivery_days,
            description, sort_order, is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.product_categories
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (category_name ILIKE :search OR 
                 subject_name ILIKE :search OR 
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
        FROM {schema_name}.product_categories
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
            
            product_categories = []
            for row in rows:
                product_category_data = {
                    'id': str(row.id),
                    'category_name': row.category_name,
                    'subject_name': row.subject_name,
                    'is_blown_film': row.is_blown_film,
                    'delivery_days': row.delivery_days,
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
                        product_category_data['created_by_name'] = created_user.get_full_name()
                    else:
                        product_category_data['created_by_name'] = '未知用户'
                else:
                    product_category_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        product_category_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        product_category_data['updated_by_name'] = '未知用户'
                else:
                    product_category_data['updated_by_name'] = ''
                
                product_categories.append(product_category_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'product_categories': product_categories,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying product categories: {str(e)}")
            raise ValueError(f'查询产品分类失败: {str(e)}')
    
    @staticmethod
    def get_product_category(product_category_id):
        """获取产品分类详情"""
        # 设置schema
        ProductCategoryService._set_schema()
        
        try:
            product_category_uuid = uuid.UUID(product_category_id)
        except ValueError:
            raise ValueError('无效的产品分类ID')
        
        from app.models.basic_data import ProductCategory
        product_category = ProductCategory.query.get(product_category_uuid)
        if not product_category:
            raise ValueError('产品分类不存在')
        
        product_category_data = product_category.to_dict()
        
        # 获取创建人和修改人用户名
        if product_category.created_by:
            created_user = User.query.get(product_category.created_by)
            if created_user:
                product_category_data['created_by_name'] = created_user.get_full_name()
            else:
                product_category_data['created_by_name'] = '未知用户'
        
        if product_category.updated_by:
            updated_user = User.query.get(product_category.updated_by)
            if updated_user:
                product_category_data['updated_by_name'] = updated_user.get_full_name()
            else:
                product_category_data['updated_by_name'] = '未知用户'
        
        return product_category_data
    
    @staticmethod
    def create_product_category(data, created_by):
        """创建产品分类"""
        # 设置schema
        ProductCategoryService._set_schema()
        
        # 验证数据
        if not data.get('category_name'):
            raise ValueError('产品分类名称不能为空')
        
        from app.models.basic_data import ProductCategory
        
        # 检查产品分类名称是否重复
        existing = ProductCategory.query.filter_by(
            category_name=data['category_name']
        ).first()
        if existing:
            raise ValueError('产品分类名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建产品分类
        product_category = ProductCategory(
            category_name=data['category_name'],
            subject_name=data.get('subject_name'),
            is_blown_film=data.get('is_blown_film', False),
            delivery_days=data.get('delivery_days'),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(product_category)
            db.session.commit()
            return product_category.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建产品分类失败: {str(e)}')
    
    @staticmethod
    def update_product_category(product_category_id, data, updated_by):
        """更新产品分类"""
        # 设置schema
        ProductCategoryService._set_schema()
        
        try:
            product_category_uuid = uuid.UUID(product_category_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import ProductCategory
        product_category = ProductCategory.query.get(product_category_uuid)
        if not product_category:
            raise ValueError('产品分类不存在')
        
        # 检查产品分类名称是否重复（排除自己）
        if 'category_name' in data and data['category_name'] != product_category.category_name:
            existing = ProductCategory.query.filter(
                and_(
                    ProductCategory.category_name == data['category_name'],
                    ProductCategory.id != product_category_uuid
                )
            ).first()
            if existing:
                raise ValueError('产品分类名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(product_category, key):
                setattr(product_category, key, value)
        
        product_category.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return product_category.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新产品分类失败: {str(e)}')
    
    @staticmethod
    def delete_product_category(product_category_id):
        """删除产品分类"""
        # 设置schema
        ProductCategoryService._set_schema()
        
        try:
            product_category_uuid = uuid.UUID(product_category_id)
        except ValueError:
            raise ValueError('无效的产品分类ID')
        
        from app.models.basic_data import ProductCategory
        product_category = ProductCategory.query.get(product_category_uuid)
        if not product_category:
            raise ValueError('产品分类不存在')
        
        try:
            db.session.delete(product_category)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除产品分类失败: {str(e)}')
    
    @staticmethod
    def batch_update_product_categories(data_list, updated_by):
        """批量更新产品分类（用于可编辑表格）"""
        # 设置schema
        ProductCategoryService._set_schema()
        
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
                    product_category = ProductCategoryService.update_product_category(
                        data['id'], data, updated_by
                    )
                    results.append(product_category)
                else:
                    # 创建新记录
                    product_category = ProductCategoryService.create_product_category(
                        data, updated_by
                    )
                    results.append(product_category)
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
    def get_enabled_product_categories():
        """获取启用的产品分类列表（用于下拉选择）"""
        # 设置schema
        ProductCategoryService._set_schema()
        
        from app.models.basic_data import ProductCategory
        product_categories = ProductCategory.query.filter_by(
            is_enabled=True
        ).order_by(ProductCategory.sort_order, ProductCategory.category_name).all()
        
        return [pc.to_dict() for pc in product_categories]


class LossTypeService:
    """报损类型管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in LossTypeService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_loss_types(page=1, per_page=20, search=None, enabled_only=False):
        """获取报损类型列表"""
        # 设置schema
        LossTypeService._set_schema()
        
        from app.models.basic_data import LossType
        
        # 构建查询
        query = LossType.query
        
        # 搜索条件
        if search:
            query = query.filter(LossType.loss_type_name.ilike(f'%{search}%'))
        
        # 启用状态过滤
        if enabled_only:
            query = query.filter(LossType.is_enabled == True)
        
        # 排序
        query = query.order_by(LossType.sort_order, LossType.created_at)
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        loss_types = []
        for loss_type in pagination.items:
            loss_type_data = loss_type.to_dict()
            
            # 简化用户名显示
            loss_type_data['created_by_name'] = '系统用户'
            loss_type_data['updated_by_name'] = '系统用户' if loss_type.updated_by else ''
            
            loss_types.append(loss_type_data)
        
        return {
            'items': loss_types,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    @staticmethod
    def create_loss_type(data, created_by):
        """创建报损类型"""
        # 设置schema
        LossTypeService._set_schema()
        
        # 验证数据
        if not data.get('loss_type_name'):
            raise ValueError('报损类型名称不能为空')
        
        from app.models.basic_data import LossType
        
        # 检查报损类型名称是否重复
        existing = LossType.query.filter_by(
            loss_type_name=data['loss_type_name']
        ).first()
        if existing:
            raise ValueError('报损类型名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建报损类型
        loss_type = LossType(
            loss_type_name=data['loss_type_name'],
            process_id=uuid.UUID(data['process_id']) if data.get('process_id') else None,
            loss_category_id=uuid.UUID(data['loss_category_id']) if data.get('loss_category_id') else None,
            is_assessment=data.get('is_assessment', False),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            db.session.add(loss_type)
            db.session.commit()
            return loss_type.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'创建报损类型失败: {str(e)}')
    
    @staticmethod
    def update_loss_type(loss_type_id, data, updated_by):
        """更新报损类型"""
        # 设置schema
        LossTypeService._set_schema()
        
        try:
            loss_type_uuid = uuid.UUID(loss_type_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import LossType
        loss_type = LossType.query.get(loss_type_uuid)
        if not loss_type:
            raise ValueError('报损类型不存在')
        
        # 检查报损类型名称是否重复（排除自己）
        if 'loss_type_name' in data and data['loss_type_name'] != loss_type.loss_type_name:
            existing = LossType.query.filter(
                and_(
                    LossType.loss_type_name == data['loss_type_name'],
                    LossType.id != loss_type_uuid
                )
            ).first()
            if existing:
                raise ValueError('报损类型名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if key == 'process_id' and value:
                setattr(loss_type, key, uuid.UUID(value))
            elif key == 'loss_category_id' and value:
                setattr(loss_type, key, uuid.UUID(value))
            elif hasattr(loss_type, key):
                setattr(loss_type, key, value)
        
        loss_type.updated_by = updated_by_uuid
        
        try:
            db.session.commit()
            return loss_type.to_dict()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'更新报损类型失败: {str(e)}')
    
    @staticmethod
    def delete_loss_type(loss_type_id):
        """删除报损类型"""
        # 设置schema
        LossTypeService._set_schema()
        
        try:
            loss_type_uuid = uuid.UUID(loss_type_id)
        except ValueError:
            raise ValueError('无效的报损类型ID')
        
        from app.models.basic_data import LossType
        loss_type = LossType.query.get(loss_type_uuid)
        if not loss_type:
            raise ValueError('报损类型不存在')
        
        try:
            db.session.delete(loss_type)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'删除报损类型失败: {str(e)}')
    
    @staticmethod
    def batch_update_loss_types(data_list, updated_by):
        """批量更新报损类型（用于可编辑表格）"""
        # 设置schema
        LossTypeService._set_schema()
        
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
                    loss_type = LossTypeService.update_loss_type(
                        data['id'], data, updated_by
                    )
                    results.append(loss_type)
                else:
                    # 创建新记录
                    loss_type = LossTypeService.create_loss_type(
                        data, updated_by
                    )
                    results.append(loss_type)
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
    def get_enabled_loss_types():
        """获取启用的报损类型列表（用于下拉选择）"""
        # 设置schema
        LossTypeService._set_schema()
        
        from app.models.basic_data import LossType
        loss_types = LossType.query.filter_by(
            is_enabled=True
        ).order_by(LossType.sort_order, LossType.loss_type_name).all()
        
        return [lt.to_dict() for lt in loss_types]


class MachineService:
    """机台服务类"""
    
    @staticmethod
    def _set_schema():
        """设置租户schema"""
        from flask import g
        if hasattr(g, 'tenant_slug') and g.tenant_slug:
            db.session.execute(text(f"SET search_path TO {g.tenant_slug}, public"))
        else:
            # 默认使用wanle schema
            db.session.execute(text("SET search_path TO wanle, public"))

    @staticmethod
    def get_machines(page=1, per_page=20, search=None, enabled_only=False):
        """获取机台列表"""
        try:
            MachineService._set_schema()
            from app.models.basic_data import Machine
            
            query = Machine.query
            
            # 搜索过滤
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    db.or_(
                        Machine.machine_name.ilike(search_pattern),
                        Machine.machine_code.ilike(search_pattern),
                        Machine.model.ilike(search_pattern)
                    )
                )
            
            # 启用状态过滤
            if enabled_only:
                query = query.filter(Machine.is_enabled == True)
            
            # 排序
            query = query.order_by(Machine.sort_order, Machine.machine_name)
            
            # 分页
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            machines = [machine.to_dict() for machine in pagination.items]
            
            return {
                'items': machines,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"获取机台列表失败: {str(e)}")
            raise e

    @staticmethod
    def get_machine(machine_id):
        """获取单个机台"""
        try:
            MachineService._set_schema()
            from app.models.basic_data import Machine
            
            machine = Machine.query.get(machine_id)
            if not machine:
                return None
            
            # 获取用户信息
            from app.models.auth import User
            user_ids = []
            if machine.created_by:
                user_ids.append(machine.created_by)
            if machine.updated_by:
                user_ids.append(machine.updated_by)
            
            users = {}
            if user_ids:
                user_list = User.query.filter(User.id.in_(user_ids)).all()
                users = {str(user.id): user.username for user in user_list}
            
            machine_dict = machine.to_dict()
            machine_dict['created_by_name'] = users.get(str(machine.created_by), '')
            machine_dict['updated_by_name'] = users.get(str(machine.updated_by), '')
            
            return machine_dict
            
        except Exception as e:
            print(f"获取机台失败: {str(e)}")
            raise e

    @staticmethod
    def create_machine(data, created_by):
        """创建机台"""
        try:
            MachineService._set_schema()
            from app.models.basic_data import Machine
            
            # 生成机台编号
            machine_code = Machine.generate_machine_code()
            
            # 创建机台
            machine = Machine(
                machine_code=machine_code,
                machine_name=data.get('machine_name'),
                model=data.get('model'),
                min_width=data.get('min_width'),
                max_width=data.get('max_width'),
                production_speed=data.get('production_speed'),
                preparation_time=data.get('preparation_time'),
                difficulty_factor=data.get('difficulty_factor'),
                circulation_card_id=data.get('circulation_card_id'),
                max_colors=data.get('max_colors'),
                kanban_display=data.get('kanban_display'),
                capacity_formula=data.get('capacity_formula'),
                gas_unit_price=data.get('gas_unit_price'),
                power_consumption=data.get('power_consumption'),
                electricity_cost_per_hour=data.get('electricity_cost_per_hour'),
                output_conversion_factor=data.get('output_conversion_factor'),
                plate_change_time=data.get('plate_change_time'),
                mes_barcode_prefix=data.get('mes_barcode_prefix'),
                is_curing_room=data.get('is_curing_room', False),
                material_name=data.get('material_name'),
                remarks=data.get('remarks'),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=created_by
            )
            
            db.session.add(machine)
            db.session.commit()
            
            return machine.to_dict()
            
        except Exception as e:
            db.session.rollback()
            print(f"创建机台失败: {str(e)}")
            raise e

    @staticmethod
    def update_machine(machine_id, data, updated_by):
        """更新机台"""
        try:
            MachineService._set_schema()
            from app.models.basic_data import Machine
            
            machine = Machine.query.get(machine_id)
            if not machine:
                raise ValueError("机台不存在")
            
            # 更新字段
            if 'machine_name' in data:
                machine.machine_name = data['machine_name']
            if 'model' in data:
                machine.model = data['model']
            if 'min_width' in data:
                machine.min_width = data['min_width']
            if 'max_width' in data:
                machine.max_width = data['max_width']
            if 'production_speed' in data:
                machine.production_speed = data['production_speed']
            if 'preparation_time' in data:
                machine.preparation_time = data['preparation_time']
            if 'difficulty_factor' in data:
                machine.difficulty_factor = data['difficulty_factor']
            if 'circulation_card_id' in data:
                machine.circulation_card_id = data['circulation_card_id']
            if 'max_colors' in data:
                machine.max_colors = data['max_colors']
            if 'kanban_display' in data:
                machine.kanban_display = data['kanban_display']
            if 'capacity_formula' in data:
                machine.capacity_formula = data['capacity_formula']
            if 'gas_unit_price' in data:
                machine.gas_unit_price = data['gas_unit_price']
            if 'power_consumption' in data:
                machine.power_consumption = data['power_consumption']
            if 'electricity_cost_per_hour' in data:
                machine.electricity_cost_per_hour = data['electricity_cost_per_hour']
            if 'output_conversion_factor' in data:
                machine.output_conversion_factor = data['output_conversion_factor']
            if 'plate_change_time' in data:
                machine.plate_change_time = data['plate_change_time']
            if 'mes_barcode_prefix' in data:
                machine.mes_barcode_prefix = data['mes_barcode_prefix']
            if 'is_curing_room' in data:
                machine.is_curing_room = data['is_curing_room']
            if 'material_name' in data:
                machine.material_name = data['material_name']
            if 'remarks' in data:
                machine.remarks = data['remarks']
            if 'sort_order' in data:
                machine.sort_order = data['sort_order']
            if 'is_enabled' in data:
                machine.is_enabled = data['is_enabled']
            
            machine.updated_by = updated_by
            
            db.session.commit()
            
            return machine.to_dict()
            
        except Exception as e:
            db.session.rollback()
            print(f"更新机台失败: {str(e)}")
            raise e

    @staticmethod
    def delete_machine(machine_id):
        """删除机台"""
        try:
            MachineService._set_schema()
            from app.models.basic_data import Machine
            
            machine = Machine.query.get(machine_id)
            if not machine:
                raise ValueError("机台不存在")
            
            db.session.delete(machine)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"删除机台失败: {str(e)}")
            raise e

    @staticmethod
    def batch_update_machines(data_list, updated_by):
        """批量更新机台"""
        try:
            MachineService._set_schema()
            from app.models.basic_data import Machine
            
            updated_machines = []
            
            for item in data_list:
                machine_id = item.get('id')
                if not machine_id:
                    continue
                
                machine = Machine.query.get(machine_id)
                if not machine:
                    continue
                
                # 更新字段
                for field in ['machine_name', 'model', 'min_width', 'max_width', 'production_speed',
                             'preparation_time', 'difficulty_factor', 'circulation_card_id', 'max_colors',
                             'kanban_display', 'capacity_formula', 'gas_unit_price', 'power_consumption',
                             'electricity_cost_per_hour', 'output_conversion_factor', 'plate_change_time',
                             'mes_barcode_prefix', 'is_curing_room', 'material_name', 'remarks',
                             'sort_order', 'is_enabled']:
                    if field in item:
                        setattr(machine, field, item[field])
                
                machine.updated_by = updated_by
                updated_machines.append(machine.to_dict())
            
            db.session.commit()
            
            return updated_machines
            
        except Exception as e:
            db.session.rollback()
            print(f"批量更新机台失败: {str(e)}")
            raise e

    @staticmethod
    def get_enabled_machines():
        """获取启用的机台列表"""
        try:
            MachineService._set_schema()
            from app.models.basic_data import Machine
            
            machines = Machine.get_enabled_list()
            return [machine.to_dict() for machine in machines]
            
        except Exception as e:
            print(f"获取启用机台列表失败: {str(e)}")
            raise e


class QuoteInkService:
    """报价油墨服务类"""
    
    @staticmethod
    def _set_schema():
        """设置租户schema"""
        from flask import g
        if hasattr(g, 'tenant_slug') and g.tenant_slug:
            db.session.execute(text(f"SET search_path TO {g.tenant_slug}, public"))
        else:
            # 默认使用wanle schema
            db.session.execute(text("SET search_path TO wanle, public"))

    @staticmethod
    def get_quote_inks(page=1, per_page=20, search=None, enabled_only=False):
        """获取报价油墨列表"""
        try:
            QuoteInkService._set_schema()
            from app.models.basic_data import QuoteInk
            
            query = QuoteInk.query
            
            # 搜索过滤
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    db.or_(
                        QuoteInk.category_name.ilike(search_pattern),
                        QuoteInk.unit_price_formula.ilike(search_pattern),
                        QuoteInk.description.ilike(search_pattern)
                    )
                )
            
            # 启用状态过滤
            if enabled_only:
                query = query.filter(QuoteInk.is_enabled == True)
            
            # 排序
            query = query.order_by(QuoteInk.sort_order, QuoteInk.category_name)
            
            # 分页
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            quote_inks = [quote_ink.to_dict() for quote_ink in pagination.items]
            
            return {
                'items': quote_inks,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"获取报价油墨列表失败: {str(e)}")
            raise e

    @staticmethod
    def get_quote_ink(quote_ink_id):
        """获取单个报价油墨"""
        try:
            QuoteInkService._set_schema()
            from app.models.basic_data import QuoteInk
            
            quote_ink = QuoteInk.query.get(quote_ink_id)
            if not quote_ink:
                raise ValueError("报价油墨不存在")
            
            return quote_ink.to_dict()
            
        except Exception as e:
            current_app.logger.error(f"获取报价油墨失败: {str(e)}")
            raise e

    @staticmethod
    def create_quote_ink(data, created_by):
        """创建报价油墨"""
        try:
            QuoteInkService._set_schema()
            from app.models.basic_data import QuoteInk
            
            # 验证必填字段
            if not data.get('category_name'):
                raise ValueError("分类名称不能为空")
            
            quote_ink = QuoteInk(
                category_name=data.get('category_name'),
                square_price=data.get('square_price'),
                unit_price_formula=data.get('unit_price_formula'),
                gram_weight=data.get('gram_weight'),
                is_ink=data.get('is_ink', False),
                is_solvent=data.get('is_solvent', False),
                sort_order=data.get('sort_order', 0),
                description=data.get('description'),
                is_enabled=data.get('is_enabled', True),
                created_by=created_by
            )
            
            db.session.add(quote_ink)
            db.session.commit()
            
            return quote_ink.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"创建报价油墨失败: {str(e)}")
            raise e

    @staticmethod
    def update_quote_ink(quote_ink_id, data, updated_by):
        """更新报价油墨"""
        try:
            QuoteInkService._set_schema()
            from app.models.basic_data import QuoteInk
            
            quote_ink = QuoteInk.query.get(quote_ink_id)
            if not quote_ink:
                raise ValueError("报价油墨不存在")
            
            # 更新字段
            if 'category_name' in data:
                quote_ink.category_name = data['category_name']
            if 'square_price' in data:
                quote_ink.square_price = data['square_price']
            if 'unit_price_formula' in data:
                quote_ink.unit_price_formula = data['unit_price_formula']
            if 'gram_weight' in data:
                quote_ink.gram_weight = data['gram_weight']
            if 'is_ink' in data:
                quote_ink.is_ink = data['is_ink']
            if 'is_solvent' in data:
                quote_ink.is_solvent = data['is_solvent']
            if 'sort_order' in data:
                quote_ink.sort_order = data['sort_order']
            if 'description' in data:
                quote_ink.description = data['description']
            if 'is_enabled' in data:
                quote_ink.is_enabled = data['is_enabled']
            
            quote_ink.updated_by = updated_by
            
            db.session.commit()
            
            return quote_ink.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新报价油墨失败: {str(e)}")
            raise e

    @staticmethod
    def delete_quote_ink(quote_ink_id):
        """删除报价油墨"""
        try:
            QuoteInkService._set_schema()
            from app.models.basic_data import QuoteInk
            
            quote_ink = QuoteInk.query.get(quote_ink_id)
            if not quote_ink:
                raise ValueError("报价油墨不存在")
            
            db.session.delete(quote_ink)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"删除报价油墨失败: {str(e)}")
            raise e

    @staticmethod
    def batch_update_quote_inks(data_list, updated_by):
        """批量更新报价油墨"""
        try:
            QuoteInkService._set_schema()
            from app.models.basic_data import QuoteInk
            
            results = []
            for data in data_list:
                if data.get('id'):
                    # 更新现有记录
                    quote_ink = QuoteInk.query.get(data['id'])
                    if quote_ink:
                        result = QuoteInkService.update_quote_ink(data['id'], data, updated_by)
                        results.append(result)
                else:
                    # 创建新记录
                    result = QuoteInkService.create_quote_ink(data, updated_by)
                    results.append(result)
            
            return results
            
        except Exception as e:
            current_app.logger.error(f"批量更新报价油墨失败: {str(e)}")
            raise e

    @staticmethod
    def get_enabled_quote_inks():
        """获取启用的报价油墨列表"""
        try:
            QuoteInkService._set_schema()
            from app.models.basic_data import QuoteInk
            
            quote_inks = QuoteInk.get_enabled_list()
            return [quote_ink.to_dict() for quote_ink in quote_inks]
            
        except Exception as e:
            current_app.logger.error(f"获取启用报价油墨列表失败: {str(e)}")
            raise e


class QuoteMaterialService:
    """报价材料管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in QuoteMaterialService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_quote_materials(page=1, per_page=20, search=None, enabled_only=False):
        """获取报价材料列表"""
        from app.models.basic_data import QuoteMaterial
        from app.models.user import User
        
        # 设置schema
        QuoteMaterialService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, material_name, density, kg_price, layer_1_optional, layer_2_optional,
            layer_3_optional, layer_4_optional, layer_5_optional, sort_order, 
            remarks, is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.quote_materials
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (material_name ILIKE :search OR 
                 remarks ILIKE :search)
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
        FROM {schema_name}.quote_materials
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
            
            quote_materials = []
            for row in rows:
                quote_material_data = {
                    'id': str(row.id),
                    'material_name': row.material_name,
                    'density': float(row.density) if row.density else None,
                    'kg_price': float(row.kg_price) if row.kg_price else None,
                    'layer_1_optional': row.layer_1_optional,
                    'layer_2_optional': row.layer_2_optional,
                    'layer_3_optional': row.layer_3_optional,
                    'layer_4_optional': row.layer_4_optional,
                    'layer_5_optional': row.layer_5_optional,
                    'sort_order': row.sort_order,
                    'remarks': row.remarks,
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
                        quote_material_data['created_by_name'] = created_user.get_full_name()
                    else:
                        quote_material_data['created_by_name'] = '未知用户'
                else:
                    quote_material_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        quote_material_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        quote_material_data['updated_by_name'] = '未知用户'
                else:
                    quote_material_data['updated_by_name'] = ''
                
                quote_materials.append(quote_material_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'quote_materials': quote_materials,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying quote materials: {str(e)}")
            raise ValueError(f'查询报价材料失败: {str(e)}')
    
    @staticmethod
    def get_quote_material(quote_material_id):
        """获取报价材料详情"""
        from app.models.basic_data import QuoteMaterial
        from app.models.user import User
        
        # 设置schema
        QuoteMaterialService._set_schema()
        
        try:
            quote_material_uuid = uuid.UUID(quote_material_id)
        except ValueError:
            raise ValueError('无效的报价材料ID')
        
        quote_material = QuoteMaterial.query.get(quote_material_uuid)
        if not quote_material:
            raise ValueError('报价材料不存在')
        
        quote_material_data = quote_material.to_dict()
        
        # 获取创建人和修改人用户名
        if quote_material.created_by:
            created_user = User.query.get(quote_material.created_by)
            if created_user:
                quote_material_data['created_by_name'] = created_user.get_full_name()
            else:
                quote_material_data['created_by_name'] = '未知用户'
        
        if quote_material.updated_by:
            updated_user = User.query.get(quote_material.updated_by)
            if updated_user:
                quote_material_data['updated_by_name'] = updated_user.get_full_name()
            else:
                quote_material_data['updated_by_name'] = '未知用户'
        
        return quote_material_data
    
    @staticmethod
    def create_quote_material(data, created_by):
        """创建报价材料"""
        from app.models.basic_data import QuoteMaterial
        
        # 设置schema
        QuoteMaterialService._set_schema()
        
        # 验证数据
        if not data.get('material_name'):
            raise ValueError('材料名称不能为空')
        
        # 检查材料名称是否重复
        existing = QuoteMaterial.query.filter_by(
            material_name=data['material_name']
        ).first()
        if existing:
            raise ValueError('材料名称已存在')
        
        try:
            # 创建报价材料
            quote_material = QuoteMaterial(
                material_name=data['material_name'],
                density=data.get('density'),
                kg_price=data.get('kg_price'),
                layer_1_optional=data.get('layer_1_optional', False),
                layer_2_optional=data.get('layer_2_optional', False),
                layer_3_optional=data.get('layer_3_optional', False),
                layer_4_optional=data.get('layer_4_optional', False),
                layer_5_optional=data.get('layer_5_optional', False),
                sort_order=data.get('sort_order', 0),
                remarks=data.get('remarks'),
                is_enabled=data.get('is_enabled', True),
                created_by=created_by
            )
            
            db.session.add(quote_material)
            db.session.commit()
            
            return quote_material.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating quote material: {str(e)}")
            raise ValueError(f'创建报价材料失败: {str(e)}')
    
    @staticmethod
    def update_quote_material(quote_material_id, data, updated_by):
        """更新报价材料"""
        from app.models.basic_data import QuoteMaterial
        
        # 设置schema
        QuoteMaterialService._set_schema()
        
        try:
            quote_material_uuid = uuid.UUID(quote_material_id)
        except ValueError:
            raise ValueError('无效的报价材料ID')
        
        quote_material = QuoteMaterial.query.get(quote_material_uuid)
        if not quote_material:
            raise ValueError('报价材料不存在')
        
        # 验证数据
        if not data.get('material_name'):
            raise ValueError('材料名称不能为空')
        
        # 检查材料名称是否重复（排除自己）
        existing = QuoteMaterial.query.filter(
            QuoteMaterial.material_name == data['material_name'],
            QuoteMaterial.id != quote_material_uuid
        ).first()
        if existing:
            raise ValueError('材料名称已存在')
        
        try:
            # 更新字段
            quote_material.material_name = data['material_name']
            quote_material.density = data.get('density')
            quote_material.kg_price = data.get('kg_price')
            quote_material.layer_1_optional = data.get('layer_1_optional', False)
            quote_material.layer_2_optional = data.get('layer_2_optional', False)
            quote_material.layer_3_optional = data.get('layer_3_optional', False)
            quote_material.layer_4_optional = data.get('layer_4_optional', False)
            quote_material.layer_5_optional = data.get('layer_5_optional', False)
            quote_material.sort_order = data.get('sort_order', 0)
            quote_material.remarks = data.get('remarks')
            quote_material.is_enabled = data.get('is_enabled', True)
            quote_material.updated_by = updated_by
            
            db.session.commit()
            
            return quote_material.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating quote material: {str(e)}")
            raise ValueError(f'更新报价材料失败: {str(e)}')
    
    @staticmethod
    def delete_quote_material(quote_material_id):
        """删除报价材料"""
        from app.models.basic_data import QuoteMaterial
        
        # 设置schema
        QuoteMaterialService._set_schema()
        
        try:
            quote_material_uuid = uuid.UUID(quote_material_id)
        except ValueError:
            raise ValueError('无效的报价材料ID')
        
        quote_material = QuoteMaterial.query.get(quote_material_uuid)
        if not quote_material:
            raise ValueError('报价材料不存在')
        
        try:
            db.session.delete(quote_material)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting quote material: {str(e)}")
            raise ValueError(f'删除报价材料失败: {str(e)}')
    
    @staticmethod
    def batch_update_quote_materials(data_list, updated_by):
        """批量更新报价材料"""
        from app.models.basic_data import QuoteMaterial
        
        # 设置schema
        QuoteMaterialService._set_schema()
        
        try:
            for data in data_list:
                quote_material_id = data.get('id')
                if not quote_material_id:
                    continue
                
                quote_material_uuid = uuid.UUID(quote_material_id)
                quote_material = QuoteMaterial.query.get(quote_material_uuid)
                if quote_material:
                    # 更新字段
                    if 'material_name' in data:
                        quote_material.material_name = data['material_name']
                    if 'density' in data:
                        quote_material.density = data['density']
                    if 'kg_price' in data:
                        quote_material.kg_price = data['kg_price']
                    if 'layer_1_optional' in data:
                        quote_material.layer_1_optional = data['layer_1_optional']
                    if 'layer_2_optional' in data:
                        quote_material.layer_2_optional = data['layer_2_optional']
                    if 'layer_3_optional' in data:
                        quote_material.layer_3_optional = data['layer_3_optional']
                    if 'layer_4_optional' in data:
                        quote_material.layer_4_optional = data['layer_4_optional']
                    if 'layer_5_optional' in data:
                        quote_material.layer_5_optional = data['layer_5_optional']
                    if 'sort_order' in data:
                        quote_material.sort_order = data['sort_order']
                    if 'remarks' in data:
                        quote_material.remarks = data['remarks']
                    if 'is_enabled' in data:
                        quote_material.is_enabled = data['is_enabled']
                    
                    quote_material.updated_by = updated_by
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error batch updating quote materials: {str(e)}")
            raise ValueError(f'批量更新报价材料失败: {str(e)}')
    
    @staticmethod
    def get_enabled_quote_materials():
        """获取启用的报价材料列表"""
        from app.models.basic_data import QuoteMaterial
        
        # 设置schema
        QuoteMaterialService._set_schema()
        
        quote_materials = QuoteMaterial.get_enabled_list()
        return [quote_material.to_dict() for quote_material in quote_materials]


class QuoteAccessoryService:
    """报价辅材管理服务"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in QuoteAccessoryService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @staticmethod
    def get_quote_accessories(page=1, per_page=20, search=None, enabled_only=False):
        """获取报价辅材列表"""
        from app.models.basic_data import QuoteAccessory
        from app.models.user import User
        
        # 设置schema
        QuoteAccessoryService._set_schema()
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        current_app.logger.info(f"Getting quote accessories for schema: {schema_name}")
        
        try:
            # 构建查询
            query = QuoteAccessory.query
            
            # 搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    db.or_(
                        QuoteAccessory.material_name.ilike(search_pattern),
                        QuoteAccessory.description.ilike(search_pattern),
                        QuoteAccessory.unit_price_formula.ilike(search_pattern)
                    )
                )
            
            # 启用状态过滤
            if enabled_only:
                query = query.filter(QuoteAccessory.is_enabled == True)
            
            # 排序
            query = query.order_by(QuoteAccessory.sort_order, QuoteAccessory.created_at)
            
            # 分页
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # 转换为字典
            quote_accessories = []
            for item in pagination.items:
                quote_accessory_dict = item.to_dict()
                
                # 添加创建者和更新者信息
                if item.created_by:
                    created_user = User.query.get(item.created_by)
                    quote_accessory_dict['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
                else:
                    quote_accessory_dict['created_by_name'] = '系统'
                
                if item.updated_by:
                    updated_user = User.query.get(item.updated_by)
                    quote_accessory_dict['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
                else:
                    quote_accessory_dict['updated_by_name'] = ''
                
                quote_accessories.append(quote_accessory_dict)
            
            result = {
                'quote_accessories': quote_accessories,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
            
            current_app.logger.info(f"Found {len(quote_accessories)} quote accessories")
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error getting quote accessories: {str(e)}")
            raise e
    
    @staticmethod
    def get_quote_accessory(quote_accessory_id):
        """获取单个报价辅材"""
        from app.models.basic_data import QuoteAccessory
        
        # 设置schema
        QuoteAccessoryService._set_schema()
        
        try:
            quote_accessory = QuoteAccessory.query.get(quote_accessory_id)
            if not quote_accessory:
                return None
            
            return quote_accessory.to_dict(include_user_info=True)
            
        except Exception as e:
            current_app.logger.error(f"Error getting quote accessory {quote_accessory_id}: {str(e)}")
            raise e
    
    @staticmethod
    def create_quote_accessory(data, created_by):
        """创建报价辅材"""
        from app.models.basic_data import QuoteAccessory
        
        # 设置schema
        QuoteAccessoryService._set_schema()
        
        try:
            quote_accessory = QuoteAccessory(
                material_name=data.get('material_name'),
                unit_price=data.get('unit_price'),
                unit_price_formula=data.get('unit_price_formula'),
                sort_order=data.get('sort_order', 0),
                description=data.get('description'),
                is_enabled=data.get('is_enabled', True),
                created_by=created_by
            )
            
            db.session.add(quote_accessory)
            db.session.commit()
            
            current_app.logger.info(f"Created quote accessory: {quote_accessory.material_name}")
            return quote_accessory.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating quote accessory: {str(e)}")
            raise e
    
    @staticmethod
    def update_quote_accessory(quote_accessory_id, data, updated_by):
        """更新报价辅材"""
        from app.models.basic_data import QuoteAccessory
        
        # 设置schema
        QuoteAccessoryService._set_schema()
        
        try:
            quote_accessory = QuoteAccessory.query.get(quote_accessory_id)
            if not quote_accessory:
                return None
            
            # 更新字段
            if 'material_name' in data:
                quote_accessory.material_name = data['material_name']
            if 'unit_price' in data:
                quote_accessory.unit_price = data['unit_price']
            if 'unit_price_formula' in data:
                quote_accessory.unit_price_formula = data['unit_price_formula']
            if 'sort_order' in data:
                quote_accessory.sort_order = data['sort_order']
            if 'description' in data:
                quote_accessory.description = data['description']
            if 'is_enabled' in data:
                quote_accessory.is_enabled = data['is_enabled']
            
            quote_accessory.updated_by = updated_by
            quote_accessory.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            current_app.logger.info(f"Updated quote accessory: {quote_accessory.material_name}")
            return quote_accessory.to_dict()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating quote accessory {quote_accessory_id}: {str(e)}")
            raise e
    
    @staticmethod
    def delete_quote_accessory(quote_accessory_id):
        """删除报价辅材"""
        from app.models.basic_data import QuoteAccessory
        
        # 设置schema
        QuoteAccessoryService._set_schema()
        
        try:
            quote_accessory = QuoteAccessory.query.get(quote_accessory_id)
            if not quote_accessory:
                return False
            
            material_name = quote_accessory.material_name
            db.session.delete(quote_accessory)
            db.session.commit()
            
            current_app.logger.info(f"Deleted quote accessory: {material_name}")
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting quote accessory {quote_accessory_id}: {str(e)}")
            raise e
    
    @staticmethod
    def batch_update_quote_accessories(data_list, updated_by):
        """批量更新报价辅材"""
        from app.models.basic_data import QuoteAccessory
        
        # 设置schema
        QuoteAccessoryService._set_schema()
        
        try:
            updated_count = 0
            for item_data in data_list:
                quote_accessory_id = item_data.get('id')
                if quote_accessory_id:
                    quote_accessory = QuoteAccessory.query.get(quote_accessory_id)
                    if quote_accessory:
                        # 更新字段
                        for field in ['material_name', 'unit_price', 'unit_price_formula', 'sort_order', 'description', 'is_enabled']:
                            if field in item_data:
                                setattr(quote_accessory, field, item_data[field])
                        
                        quote_accessory.updated_by = updated_by
                        quote_accessory.updated_at = datetime.utcnow()
                        updated_count += 1
            
            db.session.commit()
            current_app.logger.info(f"Batch updated {updated_count} quote accessories")
            return updated_count
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error batch updating quote accessories: {str(e)}")
            raise e
    
    @staticmethod
    def get_enabled_quote_accessories():
        """获取启用的报价辅材列表"""
        from app.models.basic_data import QuoteAccessory
        
        # 设置schema
        QuoteAccessoryService._set_schema()
        
        try:
            quote_accessories = QuoteAccessory.get_enabled_list()
            return [item.to_dict() for item in quote_accessories]
            
        except Exception as e:
            current_app.logger.error(f"Error getting enabled quote accessories: {str(e)}")
            raise e