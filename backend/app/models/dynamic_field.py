from app.models.base import TenantModel
from app.extensions import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func


class DynamicField(TenantModel):
    """动态字段定义模型"""
    __tablename__ = 'dynamic_fields'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    model_name = db.Column(db.String(100), nullable=False, index=True)  # 模型名称，如 'customer_category'
    page_name = db.Column(db.String(100), nullable=False, index=True)  # 新增页面名称字段
    field_name = db.Column(db.String(100), nullable=False)              # 字段名称
    field_label = db.Column(db.String(200), nullable=False)             # 显示标签
    field_type = db.Column(db.String(50), nullable=False)               # 字段类型
    field_options = db.Column(db.Text)                                  # 字段选项（如选择框选项）
    is_required = db.Column(db.Boolean, default=False)                  # 是否必填
    is_readonly = db.Column(db.Boolean, default=False)                  # 是否只读
    default_value = db.Column(db.String(500))                                  # 默认值
    help_text = db.Column(db.String(500))                                      # 帮助文本
    display_order = db.Column(db.Integer, default=0)                    # 显示顺序
    is_visible = db.Column(db.Boolean, default=True)                    # 是否可见
    validation_rules = db.Column(db.Text)                               # 验证规则
    # 计算字段相关字段
    is_calculated = db.Column(db.Boolean, default=False)                # 是否为计算字段
    calculation_formula = db.Column(db.Text)                            # 计算公式
    created_by = db.Column(db.String(100))                              # 创建人
    updated_by = db.Column(db.String(100))                              # 更新人
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('model_name', 'page_name', 'field_name', name='uq_dynamic_field'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'model_name': self.model_name,
            'page_name': self.page_name,  # 新增页面名称
            'field_name': self.field_name,
            'field_label': self.field_label,
            'field_type': self.field_type,
            'field_options': self.field_options,
            'is_required': self.is_required,
            'is_readonly': self.is_readonly,
            'default_value': self.default_value,
            'help_text': self.help_text,
            'display_order': self.display_order,
            'is_visible': self.is_visible,
            'validation_rules': self.validation_rules,
            'is_calculated': self.is_calculated,
            'calculation_formula': self.calculation_formula,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class DynamicFieldValue(TenantModel):
    """动态字段值模型"""
    __tablename__ = 'dynamic_field_values'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    model_name = db.Column(db.String(100), nullable=False, index=True)  # 模型名称
    page_name = db.Column(db.String(100), nullable=False, index=True)  # 新增页面名称字段
    record_id = db.Column(db.String(100), nullable=False, index=True)   # 关联记录ID (支持UUID)
    field_name = db.Column(db.String(100), nullable=False)              # 字段名称
    field_value = db.Column(db.Text)                                    # 字段值
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('model_name', 'page_name', 'record_id', 'field_name', name='uq_dynamic_field_value'),
    ) 