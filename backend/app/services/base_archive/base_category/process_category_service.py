# -*- coding: utf-8 -*-
"""
ProcessCategory管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text, or_, and_, String, Text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import uuid
import logging, traceback
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.services.base_service import TenantAwareService
from app.models.basic_data import ProcessCategory
from app.models.user import User


class ProcessCategoryService(TenantAwareService):
    """工序分类服务"""

    def get_process_categories(self, page=1, per_page=20, search=None, enabled_only=False):
        """
        获取工序分类列表
        
        Args:
            page: 页码
            per_page: 每页数量
            search: 搜索关键词
            enabled_only: 是否只显示启用的分类
        """
        try:
            query = self.session.query(ProcessCategory)
            
            # 搜索过滤
            if search:
                search_filter = or_(
                    ProcessCategory.process_name.ilike(f'%{search}%'),
                    ProcessCategory.category_type.ilike(f'%{search}%'),
                    ProcessCategory.description.ilike(f'%{search}%')
                )
                query = query.filter(search_filter)
            
            # 启用状态过滤
            if enabled_only:
                query = query.filter(ProcessCategory.is_enabled == True)
            
            # 排序
            query = query.order_by(ProcessCategory.sort_order, ProcessCategory.process_name)
            
            # 分页
            total = query.count()
            process_categories = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 构建返回数据
            categories_data = []
            for pc in process_categories:
                pc_data = pc.to_dict()
                
                # 添加用户信息
                if pc.created_by:
                    created_user = self.session.query(User).get(pc.created_by)
                    pc_data['created_by_username'] = created_user.get_full_name() if created_user else '未知用户'
                
                if pc.updated_by:
                    updated_user = self.session.query(User).get(pc.updated_by)
                    pc_data['updated_by_username'] = updated_user.get_full_name() if updated_user else '未知用户'
                
                categories_data.append(pc_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            
            return {
                'process_categories': categories_data,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < pages,
                'has_prev': page > 1
            }
        except Exception as e:
            raise ValueError(f'查询工序分类失败: {str(e)}')

    def get_process_category(self, process_category_id):
        """获取单个工序分类"""
        # 允许直接传入 uuid.UUID 或 字符串
        if isinstance(process_category_id, uuid.UUID):
            pc_uuid = process_category_id
        else:
            try:
                pc_uuid = uuid.UUID(str(process_category_id))
            except ValueError:
                raise ValueError('无效的工序分类ID')
        
        process_category = self.session.query(ProcessCategory).get(pc_uuid)
        if not process_category:
            raise ValueError('工序分类不存在')
        
        pc_data = process_category.to_dict()
        
        # 添加用户信息
        if process_category.created_by:
            created_user = self.session.query(User).get(process_category.created_by)
            pc_data['created_by_username'] = created_user.get_full_name() if created_user else '未知用户'
        
        if process_category.updated_by:
            updated_user = self.session.query(User).get(process_category.updated_by)
            pc_data['updated_by_username'] = updated_user.get_full_name() if updated_user else '未知用户'
        
        return pc_data

    def create_process_category(self, data, created_by):
        """创建工序分类"""
        # 验证数据
        if not data.get('process_name'):
            raise ValueError('工序分类名称不能为空')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 检查名称是否重复
        existing = self.session.query(ProcessCategory).filter_by(
            process_name=data['process_name']
        ).first()
        if existing:
            raise ValueError('工序分类名称已存在')
        
        try:
            # 创建工序分类
            process_category = self.create_with_tenant(ProcessCategory,
                process_name=data['process_name'],
                category_type=data.get('category_type'),
                sort_order=data.get('sort_order', 0),
                description=data.get('description'),
                
                # 自检类型字段
                self_check_type_1=data.get('self_check_type_1'),
                self_check_type_2=data.get('self_check_type_2'),
                self_check_type_3=data.get('self_check_type_3'),
                self_check_type_4=data.get('self_check_type_4'),
                self_check_type_5=data.get('self_check_type_5'),
                self_check_type_6=data.get('self_check_type_6'),
                self_check_type_7=data.get('self_check_type_7'),
                self_check_type_8=data.get('self_check_type_8'),
                self_check_type_9=data.get('self_check_type_9'),
                self_check_type_10=data.get('self_check_type_10'),
                
                # 工艺预料字段
                process_material_1=data.get('process_material_1'),
                process_material_2=data.get('process_material_2'),
                process_material_3=data.get('process_material_3'),
                process_material_4=data.get('process_material_4'),
                process_material_5=data.get('process_material_5'),
                process_material_6=data.get('process_material_6'),
                process_material_7=data.get('process_material_7'),
                process_material_8=data.get('process_material_8'),
                process_material_9=data.get('process_material_9'),
                process_material_10=data.get('process_material_10'),
                
                # 预留字段
                reserved_popup_1=data.get('reserved_popup_1'),
                reserved_popup_2=data.get('reserved_popup_2'),
                reserved_dropdown_1=data.get('reserved_dropdown_1'),
                reserved_dropdown_2=data.get('reserved_dropdown_2'),
                reserved_dropdown_3=data.get('reserved_dropdown_3'),
                
                # 数字字段
                number_1=data.get('number_1'),
                number_2=data.get('number_2'),
                number_3=data.get('number_3'),
                number_4=data.get('number_4'),
                
                # 布尔字段组1
                report_quantity=data.get('report_quantity', False),
                has_report_staff=data.get('has_report_staff', False),
                has_specifications=data.get('has_specifications', False),
                has_report_material=data.get('has_report_material', False),
                has_print_qty=data.get('has_print_qty', False),
                has_report_person=data.get('has_report_person', False),
                has_report_defects=data.get('has_report_defects', False),
                has_material_specs=data.get('has_material_specs', False),
                has_combined_color=data.get('has_combined_color', False),
                has_print_batch=data.get('has_print_batch', False),
                has_production_date=data.get('has_production_date', False),
                has_compound_color=data.get('has_compound_color', False),
                
                # 报表字段
                has_report_replacement=data.get('has_report_replacement', False),
                has_replace_support=data.get('has_replace_support', False),
                has_replace_defects=data.get('has_replace_defects', False),
                has_replaced_support=data.get('has_replaced_support', False),
                has_new_material=data.get('has_new_material', False),
                has_multiple_specs=data.get('has_multiple_specs', False),
                has_batch_management=data.get('has_batch_management', False),
                has_self_check=data.get('has_self_check', False),
                
                # 其他设置
                is_enabled=data.get('is_enabled', True),
                auto_report=data.get('auto_report', False),
                requires_signature=data.get('requires_signature', False),
                alert_on_deviation=data.get('alert_on_deviation', False),
                
                created_by=created_by_uuid
            )
            
            self.commit()
            return self.get_process_category(process_category.id)
        except Exception as e:
            self.rollback()
            raise e

    def update_process_category(self, process_category_id, data, updated_by):
        """更新工序分类"""
        try:
            pc_uuid = uuid.UUID(process_category_id)
        except ValueError:
            raise ValueError('无效的工序分类ID')
        
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的更新用户ID')
        
        try:
            process_category = self.session.query(ProcessCategory).get(pc_uuid)
            if not process_category:
                raise ValueError('工序分类不存在')
            
            # 验证数据
            if 'process_name' in data and not data['process_name']:
                raise ValueError('工序分类名称不能为空')
            
            # 检查名称是否重复
            if 'process_name' in data:
                existing = self.session.query(ProcessCategory).filter(
                    and_(
                        ProcessCategory.process_name == data['process_name'],
                        ProcessCategory.id != pc_uuid
                    )
                ).first()
                if existing:
                    raise ValueError('工序分类名称已存在')
            
            # 更新字段
            import logging, traceback
            logger = logging.getLogger(__name__)

            for field, value in data.items():
                # 跳过不可修改字段
                if not hasattr(process_category, field) or field in ['id', 'created_by', 'created_at']:
                    continue

                # 如果是 UUID 对象且目标列非 UUID 类型，转字符串
                if isinstance(value, uuid.UUID):
                    column = getattr(ProcessCategory, field).property.columns[0]
                    if not isinstance(column.type, PGUUID):
                        value = str(value)

                # 如果是列表/字典，递归将内部 UUID 转 str（JSONB 等字段会用到）
                def convert_uuid(obj):
                    if isinstance(obj, uuid.UUID):
                        return str(obj)
                    if isinstance(obj, list):
                        return [convert_uuid(i) for i in obj]
                    if isinstance(obj, dict):
                        return {k: convert_uuid(v) for k, v in obj.items()}
                    return obj

                value = convert_uuid(value)

                try:
                    setattr(process_category, field, value)
                except Exception as set_err:
                    logger.error(
                        "Error setting field '%s' with value %s (%s) on ProcessCategory %s: %s",
                        field, value, type(value), process_category_id, set_err
                    )
                    logger.error("Traceback:\n%s", traceback.format_exc())
                    raise
            
            process_category.updated_by = updated_by_uuid
            self.commit()
            
            return self.get_process_category(process_category.id)
        except Exception as e:
            # 已记录详细信息，再回滚
            self.rollback()
            logger.error("update_process_category failed: %s", e, exc_info=True)
            raise e

    def delete_process_category(self, process_category_id):
        """删除工序分类"""
        try:
            pc_uuid = uuid.UUID(process_category_id)
        except ValueError:
            raise ValueError('无效的工序分类ID')
        
        try:
            process_category = self.session.query(ProcessCategory).get(pc_uuid)
            if not process_category:
                raise ValueError('工序分类不存在')
            
            # 这里可以添加删除前的检查，如是否被其他数据引用
            
            self.session.delete(process_category)

            try:
                self.commit()
            except IntegrityError:
                # 处理外键约束失败
                self.rollback()
                raise ValueError('该工序分类已被工序引用，无法删除')
            
            return True
        except Exception as e:
            self.rollback()
            raise e

    def batch_update_process_categories(self, data_list, updated_by):
        """批量更新工序分类"""
        results = []
        
        for data in data_list:
            category_id = data.get('id')
            if not category_id:
                continue
                
            try:
                # 提取id字段
                update_data = {k: v for k, v in data.items() if k != 'id'}
                result = self.update_process_category(category_id, update_data, updated_by)
                results.append(result)
            except Exception as e:
                results.append({
                    'id': category_id,
                    'error': str(e)
                })
        
        return results

    def get_enabled_process_categories(self):
        """获取所有启用的工序分类"""
        try:
            categories = self.session.query(ProcessCategory).filter(
                ProcessCategory.is_enabled == True
            ).order_by(ProcessCategory.sort_order, ProcessCategory.process_name).all()
            
            return [pc.to_dict() for pc in categories]
        except Exception as e:
            raise e

    def get_category_type_options(self):
        """获取分类类型选项"""
        return ['主工序', '辅助工序', '检验工序', '包装工序']

    def get_data_collection_mode_options(self):
        """获取数据采集模式选项"""
        return ['手动输入', '扫码录入', '自动采集', '批量导入']

