import json
from flask import g
from app.services.base_service import TenantAwareService
from app.models.dynamic_field import DynamicField, DynamicFieldValue
from sqlalchemy import func
from app.config import DynamicFieldsConfig
from sqlalchemy import inspect, text, func


def get_dynamic_field_service(tenant_id=None, schema_name=None):
    """获取动态字段服务实例"""
    if tenant_id is None:
        tenant_id = getattr(g, 'tenant_id', None)
    if schema_name is None:
        schema_name = getattr(g, 'schema_name', None)
    
    return DynamicFieldService(tenant_id=tenant_id, schema_name=schema_name)


class DynamicFieldService(TenantAwareService):
    """动态字段服务"""
    
    def __init__(self, tenant_id=None, schema_name=None):
        super().__init__(tenant_id, schema_name)
        # 从配置读取分表设置
        self.enable_model_partitioning = DynamicFieldsConfig.ENABLE_MODEL_PARTITIONING
    
    def get_model_fields(self, model_name, page_name='default'):
        """获取指定模型指定页面的字段定义"""
        fields = self.session.query(DynamicField).filter(
            DynamicField.model_name == model_name,
            DynamicField.page_name == page_name
        ).order_by(DynamicField.display_order).all()
        
        return [field.to_dict() for field in fields]
    
    def get_all_model_fields(self, model_name):
        """获取指定模型的所有字段定义（不限制页面）"""
        fields = self.session.query(DynamicField).filter(
            DynamicField.model_name == model_name
        ).order_by(DynamicField.page_name, DynamicField.display_order).all()
        
        return [field.to_dict() for field in fields]
    
    def get_page_fields(self, model_name, page_name):
        """获取指定模型指定页面的字段定义（新增方法）"""
        return self.get_model_fields(model_name, page_name)
    
    def create_field(self, model_name, page_name, field_data):
        """创建字段定义"""
        # 确保页面名称不是空字符串
        if not page_name or not page_name.strip():
            page_name = 'default'
        else:
            page_name = page_name.strip()
        
        field_data_copy = field_data.copy()
        display_order = field_data_copy.pop('display_order', 0)
        
        field = self.create_with_tenant(
            DynamicField,
            model_name=model_name,
            page_name=page_name,
            display_order=display_order,
            **field_data_copy
        )
        
        # 提交事务以确保ID生成
        self.session.commit()
        
        return field.to_dict()
    
    def update_field(self, field_id, field_data):
        """更新字段定义"""
        field = self.session.query(DynamicField).filter(DynamicField.id == field_id).first()
        if not field:
            return None
        
        # 检查页面名称是否发生变化
        old_page_name = field.page_name
        new_page_name = None
        
        # 确保页面名称不是空字符串
        if 'page_name' in field_data:
            page_name = field_data['page_name']
            if not page_name or not page_name.strip():
                new_page_name = 'default'
            else:
                new_page_name = page_name.strip()
        
        # 如果页面名称发生变化，迁移数据
        if new_page_name and new_page_name != old_page_name:
            self._migrate_field_values(field.model_name, field.field_name, old_page_name, new_page_name)
        
        for key, value in field_data.items():
            if hasattr(field, key):
                setattr(field, key, value)
        
        # 确保事务提交
        self.session.commit()
        return field.to_dict()
    
    def _migrate_field_values(self, model_name, field_name, old_page_name, new_page_name):
        """迁移字段值从旧页面到新页面"""
        # 查找所有使用旧页面名称的字段值
        old_values = self.session.query(DynamicFieldValue).filter(
            DynamicFieldValue.model_name == model_name,
            DynamicFieldValue.page_name == old_page_name,
            DynamicFieldValue.field_name == field_name
        ).all()
        
        for old_value in old_values:
            # 检查新页面是否已存在相同的记录和字段
            existing_value = self.session.query(DynamicFieldValue).filter(
                DynamicFieldValue.model_name == model_name,
                DynamicFieldValue.page_name == new_page_name,
                DynamicFieldValue.record_id == old_value.record_id,
                DynamicFieldValue.field_name == field_name
            ).first()
            
            if existing_value:
                # 如果新页面已存在，更新值并删除旧值
                existing_value.field_value = old_value.field_value
                self.session.delete(old_value)
            else:
                # 如果新页面不存在，创建新值并删除旧值
                self.create_with_tenant(
                    DynamicFieldValue,
                    model_name=model_name,
                    page_name=new_page_name,
                    record_id=old_value.record_id,
                    field_name=field_name,
                    field_value=old_value.field_value
                )
                self.session.delete(old_value)
        
        self.session.commit()
    
    def delete_field(self, field_id):
        """删除字段定义"""
        field = self.session.query(DynamicField).filter(DynamicField.id == field_id).first()
        if field:
            try:
                # 先删除所有相关的动态字段值
                values = self.session.query(DynamicFieldValue).filter(
                    DynamicFieldValue.model_name == field.model_name,
                    DynamicFieldValue.field_name == field.field_name
                ).all()
                
                for value in values:
                    self.session.delete(value)
                
                # 清理相关的列配置（在单独的事务中处理）
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"开始清理字段 {field.field_name} 的列配置...")
                try:
                    self._cleanup_field_column_config(field)
                    logger.info(f"字段 {field.field_name} 的列配置清理完成")
                except Exception as cleanup_error:
                    # 清理失败不影响字段删除
                    logger.warning(f"清理字段配置失败，但继续删除字段: {str(cleanup_error)}")
                    logger.exception("清理字段配置的详细错误信息:")
                
                # 然后删除字段定义
                self.session.delete(field)
                self.session.commit()
                return True
            except Exception as e:
                self.session.rollback()
                raise ValueError(f"删除字段失败: {str(e)}")
        return False
    
    def _cleanup_field_column_config(self, field):
        """清理字段相关的列配置"""
        try:
            from app.models.column_configuration import ColumnConfiguration
            from flask import g, current_app
            from sqlalchemy import text, func
            
            # 获取字段名称
            field_name = field.field_name
            
            # 确保在正确的 schema 中执行
            schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"开始清理字段 {field_name} 的列配置，当前schema: {schema_name}")
            
            # 设置正确的 schema 搜索路径
            if schema_name != 'public':
                self.session.execute(text(f'SET search_path TO {schema_name}, public'))
                logger.info(f"已设置搜索路径到: {schema_name}")
            
            # 查找所有相关的列配置 - 清理所有类型的配置
            all_configs = self.session.query(ColumnConfiguration).all()
            
            logger.info(f"在schema {schema_name} 中找到 {len(all_configs)} 个配置")
            
            configs_updated = False
            for config in all_configs:
                logger.info(f"检查配置: page_name={config.page_name}, config_type={config.config_type}")
                
                updated = False
                
                # 处理列配置（字典格式）
                if config.config_type == 'column_config' and config.config_data and isinstance(config.config_data, dict):
                    if field_name in config.config_data:
                        logger.info(f"在列配置中找到字段 {field_name}，准备删除")
                        del config.config_data[field_name]
                        updated = True
                        logger.info(f"已从列配置中删除字段 {field_name}")
                        
                        # 如果配置数据为空，删除整个配置
                        if not config.config_data:
                            logger.info(f"配置数据为空，删除整个配置")
                            self.session.delete(config)
                            configs_updated = True
                            continue
                
                # 处理列顺序配置（列表格式）
                elif config.config_type == 'column_order' and config.config_data and isinstance(config.config_data, list):
                    if field_name in config.config_data:
                        logger.info(f"在列顺序中找到字段 {field_name}，准备删除")
                        config.config_data.remove(field_name)
                        updated = True
                        logger.info(f"已从列顺序中删除字段 {field_name}")
                        
                        # 如果顺序列表为空，删除整个配置
                        if not config.config_data:
                            logger.info(f"顺序列表为空，删除整个配置")
                            self.session.delete(config)
                            configs_updated = True
                            continue
                
                # 如果有更新，标记更新时间
                if updated:
                    config.updated_at = func.now()
                    configs_updated = True
                    logger.info(f"已更新配置: {config.page_name}:{config.config_type}")
            
            # 如果有更新，提交事务
            if configs_updated:
                self.session.commit()
                logger.info(f"已清理字段 {field_name} 的所有列配置")
            else:
                logger.info(f"字段 {field_name} 没有找到需要清理的列配置")
                            
        except Exception as e:
            # 清理配置失败不影响字段删除，只记录日志
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"清理字段 {field.field_name} 的列配置失败: {str(e)}")
            # 回滚清理操作，但不影响主删除操作
            try:
                self.session.rollback()
            except:
                pass
    
    def get_record_dynamic_values(self, model_name, record_id, page_name='default'):
        """获取记录的动态字段值"""
        # 注意：此查询需要确保有以下索引：
        # CREATE INDEX idx_dynamic_field_values_model_page_record ON dynamic_field_values(model_name, page_name, record_id);
        # CREATE INDEX idx_dynamic_field_values_model_field ON dynamic_field_values(model_name, field_name);
        values = self.session.query(DynamicFieldValue).filter(
            DynamicFieldValue.model_name == model_name,
            DynamicFieldValue.page_name == page_name,
            DynamicFieldValue.record_id == str(record_id)
        ).all()
        
        result = {}
        for value in values:
            result[value.field_name] = value.field_value
            
        return result
    
    def get_record_page_values(self, model_name, page_name, record_id):
        """获取记录指定页面的动态字段值（新增方法）"""
        return self.get_record_dynamic_values(model_name, record_id, page_name)
    
    def save_record_dynamic_values(self, model_name, record_id, values, page_name='default'):
        """保存记录的动态字段值"""
        record_id_str = str(record_id)
        
        for field_name, field_value in values.items():
            # 先清理该记录在其他页面的相同字段数据（避免重复）
            other_page_values = self.session.query(DynamicFieldValue).filter(
                DynamicFieldValue.model_name == model_name,
                DynamicFieldValue.record_id == record_id_str,
                DynamicFieldValue.field_name == field_name,
                DynamicFieldValue.page_name != page_name
            ).all()
            
            for other_value in other_page_values:
                self.session.delete(other_value)
            
            # 查找当前页面的现有值
            existing_value = self.session.query(DynamicFieldValue).filter(
                DynamicFieldValue.model_name == model_name,
                DynamicFieldValue.page_name == page_name,
                DynamicFieldValue.record_id == record_id_str,
                DynamicFieldValue.field_name == field_name
            ).first()
            
            if existing_value:
                # 更新现有值
                existing_value.field_value = str(field_value) if field_value is not None else None
            else:
                # 创建新值
                self.create_with_tenant(
                    DynamicFieldValue,
                    model_name=model_name,
                    page_name=page_name,
                    record_id=record_id_str,
                    field_name=field_name,
                    field_value=str(field_value) if field_value is not None else None
                )
        
        self.session.commit()
        return True
    
    def save_record_page_values(self, model_name, page_name, record_id, values):
        """保存记录指定页面的动态字段值（新增方法）"""
        return self.save_record_dynamic_values(model_name, record_id, values, page_name)
    
    def delete_record_page_values(self, model_name, page_name, record_id):
        """删除记录指定页面的所有动态字段值"""
        record_id_str = str(record_id)
        
        # 删除该记录指定页面的所有动态字段值
        values = self.session.query(DynamicFieldValue).filter(
            DynamicFieldValue.model_name == model_name,
            DynamicFieldValue.page_name == page_name,
            DynamicFieldValue.record_id == record_id_str
        ).all()
        
        for value in values:
            self.session.delete(value)
        
        self.session.commit()
        return True
    
    def cleanup_duplicate_values(self, model_name, record_id):
        """清理记录中重复的动态字段值（保留最新的）"""
        record_id_str = str(record_id)
        
        # 查找所有重复的字段值（相同字段名在不同页面）
        duplicates = self.session.query(
            DynamicFieldValue.field_name,
            DynamicFieldValue.page_name,
            DynamicFieldValue.id,
            DynamicFieldValue.created_at
        ).filter(
            DynamicFieldValue.model_name == model_name,
            DynamicFieldValue.record_id == record_id_str
        ).order_by(
            DynamicFieldValue.field_name,
            DynamicFieldValue.created_at.desc()
        ).all()
        
        # 按字段名分组，保留每个字段的最新值
        field_latest = {}
        to_delete = []
        
        for dup in duplicates:
            field_name = dup.field_name
            if field_name not in field_latest:
                field_latest[field_name] = dup
            else:
                to_delete.append(dup.id)
        
        # 删除重复的记录
        if to_delete:
            self.session.query(DynamicFieldValue).filter(
                DynamicFieldValue.id.in_(to_delete)
            ).delete(synchronize_session=False)
            self.session.commit()
        
        return len(to_delete) 
    
    def get_table_name(self, model_name):
        """获取动态字段值表名，支持按模型分表"""
        return DynamicFieldsConfig.get_table_name(model_name, 'dynamic_field_values')
    
    def create_model_table_if_not_exists(self, model_name):
        """为指定模型创建独立的动态字段值表"""
        table_name = f'dynamic_field_values_{model_name}'
        
        # 检查表是否存在
        inspector = inspect(self.session.bind)
        if table_name not in inspector.get_table_names(schema=self.schema_name):
            # 创建表
            create_table_sql = f"""
            CREATE TABLE {self.schema_name}.{table_name} (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                page_name VARCHAR(100) NOT NULL,
                record_id VARCHAR(255) NOT NULL,
                field_name VARCHAR(100) NOT NULL,
                field_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(page_name, record_id, field_name)
            );
            CREATE INDEX idx_{table_name}_page_record ON {self.schema_name}.{table_name}(page_name, record_id);
            CREATE INDEX idx_{table_name}_field ON {self.schema_name}.{table_name}(field_name);
            """
            self.session.execute(text(create_table_sql))
            self.session.commit()
        
        return table_name 
    
    def get_model_data_stats(self, model_name):
        """获取指定模型的数据统计信息"""
        stats = {
            'model_name': model_name,
            'total_records': 0,
            'total_fields': 0,
            'pages': [],
            'recommendations': []
        }
        
        # 统计字段定义
        field_count = self.session.query(DynamicField).filter(
            DynamicField.model_name == model_name
        ).count()
        stats['total_fields'] = field_count
        
        # 统计字段值
        value_count = self.session.query(DynamicFieldValue).filter(
            DynamicFieldValue.model_name == model_name
        ).count()
        stats['total_records'] = value_count
        
        # 统计页面分布
        pages = self.session.query(
            DynamicFieldValue.page_name,
            func.count(DynamicFieldValue.id).label('count')
        ).filter(
            DynamicFieldValue.model_name == model_name
        ).group_by(DynamicFieldValue.page_name).all()
        
        stats['pages'] = [{'page_name': p.page_name, 'count': p.count} for p in pages]
        
        # 生成建议
        if value_count > DynamicFieldsConfig.PARTITIONING_THRESHOLD:
            stats['recommendations'].append(f"数据量({value_count})超过阈值({DynamicFieldsConfig.PARTITIONING_THRESHOLD})，建议启用分表")
        
        if field_count > DynamicFieldsConfig.MAX_FIELDS_PER_PAGE:
            stats['recommendations'].append(f"字段数({field_count})超过建议值({DynamicFieldsConfig.MAX_FIELDS_PER_PAGE})，建议优化字段设计")
        
        return stats
    
    def get_all_models_stats(self):
        """获取所有模型的数据统计信息"""
        models = self.session.query(DynamicFieldValue.model_name).distinct().all()
        stats = []
        
        for model in models:
            model_name = model.model_name
            stats.append(self.get_model_data_stats(model_name))
        
        return stats 