# -*- coding: utf-8 -*-
"""
QuoteMaterial管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import QuoteMaterial
from app.models.user import User
from flask import g, current_app


class QuoteMaterialService(TenantAwareService):
    """报价材料管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化QuoteMaterial服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_quote_materials(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取报价材料列表"""
        from app.models.basic_data import QuoteMaterial
        from app.models.user import User
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
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
            count_result = self.get_session().execute(text(count_query), params)
            total = count_result.scalar()
            
            # 计算分页
            offset = (page - 1) * per_page
            params['limit'] = per_page
            params['offset'] = offset
            
            # 添加分页
            paginated_query = base_query + " LIMIT :limit OFFSET :offset"
            
            # 执行分页查询
            result = self.get_session().execute(text(paginated_query), params)
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
    def get_quote_material(self, quote_material_id):
        """获取报价材料详情"""
        from app.models.basic_data import QuoteMaterial
        from app.models.user import User
        
        
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
    def create_quote_material(self, data, created_by):
        """创建报价材料"""
        from app.models.basic_data import QuoteMaterial
        from flask_jwt_extended import get_jwt
        from flask import g, current_app
        
        # 获取当前schema名称
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 获取租户ID
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        if not tenant_id:
            raise ValueError('租户信息缺失')
        
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
            quote_material = QuoteMaterial(
                material_name=data.get('material_name'),
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
            
            self.get_session().add(quote_material)
            self.get_session().commit()
            
            return quote_material.to_dict()
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"Error creating quote material: {str(e)}")
            raise ValueError(f'创建报价材料失败: {str(e)}')
    def update_quote_material(self, quote_material_id, data, updated_by):
        """更新报价材料"""
        from app.models.basic_data import QuoteMaterial
        
        
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
            
            self.get_session().commit()
            
            return quote_material.to_dict()
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"Error updating quote material: {str(e)}")
            raise ValueError(f'更新报价材料失败: {str(e)}')
    def delete_quote_material(self, quote_material_id):
        """删除报价材料"""
        from app.models.basic_data import QuoteMaterial
        
        
        try:
            quote_material_uuid = uuid.UUID(quote_material_id)
        except ValueError:
            raise ValueError('无效的报价材料ID')
        
        quote_material = QuoteMaterial.query.get(quote_material_uuid)
        if not quote_material:
            raise ValueError('报价材料不存在')
        
        try:
            self.get_session().delete(quote_material)
            self.get_session().commit()
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"Error deleting quote material: {str(e)}")
            raise ValueError(f'删除报价材料失败: {str(e)}')
    def batch_update_quote_materials(self, data_list, updated_by):
        """批量更新报价材料"""
        from app.models.basic_data import QuoteMaterial
        
        
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
            
            self.get_session().commit()
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"Error batch updating quote materials: {str(e)}")
            raise ValueError(f'批量更新报价材料失败: {str(e)}')
    def get_enabled_quote_materials(self):
        """获取启用的报价材料列表"""
        from app.models.basic_data import QuoteMaterial
        
        
        quote_materials = QuoteMaterial.get_enabled_list()
        return [quote_material.to_dict() for quote_material in quote_materials]

# 创建服务实例的工厂函数
def get_quote_material_service():
    """获取报价材料服务实例"""
    return QuoteMaterialService()

