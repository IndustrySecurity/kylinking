import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import func
from app.extensions import db
from app.models.base import TenantModel


class ColumnConfiguration(TenantModel):
    """列配置模型 - 用于存储各页面的列显示配置"""
    __tablename__ = 'column_configurations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 配置信息
    page_name = db.Column(db.String(100), nullable=False, comment='页面名称')
    config_type = db.Column(db.String(50), nullable=False, comment='配置类型(column_config/column_order)')
    config_data = db.Column(JSONB, nullable=False, comment='配置数据')
    
    # 系统字段
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        db.UniqueConstraint('page_name', 'config_type', name='uq_column_config_page_type'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'page_name': self.page_name,
            'config_type': self.config_type,
            'config_data': self.config_data,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def get_config(cls, page_name, config_type):
        """获取配置"""
        # 先尝试查找启用的配置
        config = cls.query.filter_by(
            page_name=page_name,
            config_type=config_type,
            is_enabled=True
        ).first()
        
        # 如果没有找到启用的配置，查找任何配置（包括禁用的）
        if not config:
            config = cls.query.filter_by(
                page_name=page_name,
                config_type=config_type
            ).first()
        
        return config
    
    @classmethod
    def save_config(cls, page_name, config_type, config_data, user_id):
        """保存配置"""
        # 查找现有配置（包括禁用的）
        existing = cls.query.filter_by(
            page_name=page_name,
            config_type=config_type
        ).first()
        
        if existing:
            # 更新现有配置
            existing.config_data = config_data
            existing.updated_by = user_id
            existing.updated_at = func.now()
            existing.is_enabled = True  # 确保启用
            db.session.commit()
            return existing
        else:
            # 创建新配置
            new_config = cls(
                page_name=page_name,
                config_type=config_type,
                config_data=config_data,
                created_by=user_id
            )
            db.session.add(new_config)
            db.session.commit()
            return new_config
    
    @classmethod
    def delete_config(cls, page_name, config_type):
        """删除配置"""
        config = cls.get_config(page_name, config_type)
        if config:
            config.is_enabled = False
            db.session.commit()
        return config
    
    def __repr__(self):
        return f'<ColumnConfiguration {self.page_name}:{self.config_type}>' 