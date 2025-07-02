# -*- coding: utf-8 -*-
"""
ProcessCategory管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text, or_
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import ProcessCategory
from app.models.user import User


class ProcessCategoryService(TenantAwareService):
    """工序分类服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化ProcessCategory服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_process_categories(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取工序分类列表"""
        
        from app.models.basic_data import ProcessCategory
        from app.models.user import User
        
        query = ProcessCategory.query
        
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
        paginated = query.paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )
        
        process_categories = []
        for pc in paginated.items:
            pc_data = pc.to_dict()
            
            # 获取创建人和修改人用户名
            if pc.created_by:
                created_user = User.query.get(pc.created_by)
                if created_user:
                    pc_data['created_by_name'] = created_user.get_full_name()
                else:
                    pc_data['created_by_name'] = '未知用户'
            
            if pc.updated_by:
                updated_user = User.query.get(pc.updated_by)
                if updated_user:
                    pc_data['updated_by_name'] = updated_user.get_full_name()
                else:
                    pc_data['updated_by_name'] = '未知用户'
            
            process_categories.append(pc_data)
        
        return {
            'process_categories': process_categories,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
    def get_process_category(self, process_category_id):
        """获取单个工序分类"""
        
        try:
            pc_uuid = uuid.UUID(process_category_id)
        except ValueError:
            raise ValueError('无效的工序分类ID')
        
        from app.models.basic_data import ProcessCategory
        from app.models.user import User
        
        process_category = ProcessCategory.query.get(pc_uuid)
        if not process_category:
            raise ValueError('工序分类不存在')
        
        pc_data = process_category.to_dict()
        
        # 获取创建人和修改人用户名
        if process_category.created_by:
            created_user = User.query.get(process_category.created_by)
            if created_user:
                pc_data['created_by_name'] = created_user.get_full_name()
            else:
                pc_data['created_by_name'] = '未知用户'
        
        if process_category.updated_by:
            updated_user = User.query.get(process_category.updated_by)
            if updated_user:
                pc_data['updated_by_name'] = updated_user.get_full_name()
            else:
                pc_data['updated_by_name'] = '未知用户'
        
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
        from app.models.basic_data import ProcessCategory
        existing = ProcessCategory.query.filter_by(
            process_name=data['process_name']
        ).first()
        if existing:
            raise ValueError('工序分类名称已存在')
        
        # 创建工序分类
        process_category = ProcessCategory(
            process_name=data['process_name'],
            category_type=data.get('category_type'),
            sort_order=data.get('sort_order', 0),
            
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
            has_replace_material=data.get('has_replace_material', False),
            has_print_report=data.get('has_print_report', False),
            has_replace_time=data.get('has_replace_time', False),
            has_time=data.get('has_time', False),
            has_hold_time=data.get('has_hold_time', False),
            has_glue_water=data.get('has_glue_water', False),
            has_glue_drop=data.get('has_glue_drop', False),
            has_replacement_sub=data.get('has_replacement_sub', False),
            has_replace_report=data.get('has_replace_report', False),
            has_auto_print=data.get('has_auto_print', False),
            
            # 过程管控字段
            has_color_change=data.get('has_color_change', False),
            has_process_packet=data.get('has_process_packet', False),
            has_additional=data.get('has_additional', False),
            has_work_group_date=data.get('has_work_group_date', False),
            has_shift_time=data.get('has_shift_time', False),
            has_start_time=data.get('has_start_time', False),
            has_time_count=data.get('has_time_count', False),
            has_knife_count=data.get('has_knife_count', False),
            has_electric_count=data.get('has_electric_count', False),
            has_maintenance_time=data.get('has_maintenance_time', False),
            has_result_time=data.get('has_result_time', False),
            has_result_malfunction=data.get('has_result_malfunction', False),
            is_query_machine=data.get('is_query_machine', False),
            
            # MES字段
            mes_report_kg_manual=data.get('mes_report_kg_manual', False),
            mes_kg_auto_fill=data.get('mes_kg_auto_fill', False),
            auto_weighing_once=data.get('auto_weighing_once', False),
            mes_process_feedback_clear=data.get('mes_process_feedback_clear', False),
            mes_consumption_solvent_by_ton=data.get('mes_consumption_solvent_by_ton', False),
            single_report_open=data.get('single_report_open', False),
            multi_condition_open=data.get('multi_condition_open', False),
            mes_line_start_work_order=data.get('mes_line_start_work_order', False),
            mes_material_kg_consumption=data.get('mes_material_kg_consumption', False),
            mes_report_not_less_than_kg=data.get('mes_report_not_less_than_kg', False),
            mes_water_consumption_by_ton=data.get('mes_water_consumption_by_ton', False),
            
            # 其他字段
            data_collection_mode=data.get('data_collection_mode'),
            show_data_collection_interface=data.get('show_data_collection_interface', False),
            description=data.get('description'),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        from app import db
        self.get_session().add(process_category)
        self.get_session().commit()
        
        return process_category.to_dict()
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
        
        from app.models.basic_data import ProcessCategory
        from app import db
        
        process_category = ProcessCategory.query.get(pc_uuid)
        if not process_category:
            raise ValueError('工序分类不存在')
        
        # 检查名称是否重复（排除自己）
        if data.get('process_name') and data['process_name'] != process_category.process_name:
            existing = ProcessCategory.query.filter_by(
                process_name=data['process_name']
            ).first()
            if existing:
                raise ValueError('工序分类名称已存在')
        
        # 更新字段
        for field in ['process_name', 'category_type', 'sort_order', 'data_collection_mode', 
                     'show_data_collection_interface', 'description', 'is_enabled']:
            if field in data:
                setattr(process_category, field, data[field])
        
        # 更新自检和工艺字段
        for i in range(1, 11):
            for prefix in ['self_check_type_', 'process_material_']:
                field = f'{prefix}{i}'
                if field in data:
                    setattr(process_category, field, data[field])
        
        # 更新预留字段和数字字段
        for field in ['reserved_popup_1', 'reserved_popup_2', 'reserved_popup_3',
                     'reserved_dropdown_1', 'reserved_dropdown_2', 'reserved_dropdown_3',
                     'number_1', 'number_2', 'number_3', 'number_4']:
            if field in data:
                setattr(process_category, field, data[field])
        
        process_category.updated_by = updated_by_uuid
        self.get_session().commit()
        
        return process_category.to_dict()
    def delete_process_category(self, process_category_id):
        """删除工序分类"""
        
        try:
            pc_uuid = uuid.UUID(process_category_id)
        except ValueError:
            raise ValueError('无效的工序分类ID')
        
        from app.models.basic_data import ProcessCategory
        from app import db
        
        process_category = ProcessCategory.query.get(pc_uuid)
        if not process_category:
            raise ValueError('工序分类不存在')
        
        self.get_session().delete(process_category)
        self.get_session().commit()
    def batch_update_process_categories(self, data_list, updated_by):
        """批量更新工序分类"""
        
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的更新用户ID')
        
        from app.models.basic_data import ProcessCategory
        from app import db
        
        results = []
        
        for item in data_list:
            if not item.get('id'):
                continue
                
            try:
                pc_uuid = uuid.UUID(item['id'])
            except ValueError:
                continue
            
            process_category = ProcessCategory.query.get(pc_uuid)
            if not process_category:
                continue
            
            # 更新字段
            for field, value in item.items():
                if field != 'id' and hasattr(process_category, field):
                    setattr(process_category, field, value)
            
            process_category.updated_by = updated_by_uuid
            results.append(process_category.to_dict())
        
        self.get_session().commit()
        return results
    def get_enabled_process_categories(self):
        """获取启用的工序分类列表"""
        
        from app.models.basic_data import ProcessCategory
        
        process_categories = ProcessCategory.query.filter(
            ProcessCategory.is_enabled == True
        ).order_by(ProcessCategory.sort_order, ProcessCategory.process_name).all()
        
        return [pc.to_dict() for pc in process_categories]
    def get_category_type_options(self):
        """获取工序分类类型选项"""
        from app.models.basic_data import ProcessCategory
        return ProcessCategory.get_category_type_options()
    def get_data_collection_mode_options(self):
        """获取数据采集模式选项"""
        from app.models.basic_data import ProcessCategory
        return ProcessCategory.get_data_collection_mode_options()

