# -*- coding: utf-8 -*-
"""
基础档案管理数据模型
"""

from app.extensions import db
from app.models.base import BaseModel, TenantModel
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import text, func
import time
from datetime import datetime


# CustomerCategory 已移至下方的 CustomerCategoryManagement 模型


# Customer 已移至下方的 CustomerManagement 模型


# SupplierCategory 已移至下方的 SupplierCategoryManagement 模型


# Supplier 已移至下方的 SupplierManagement 模型


class ProductCategory(TenantModel):
    """产品分类模型"""
    __tablename__ = 'product_categories'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    category_name = db.Column(db.String(255), nullable=False, comment='产品分类名称')
    subject_name = db.Column(db.String(100), comment='科目名称')
    is_blown_film = db.Column(db.Boolean, default=False, comment='是否吹膜')
    delivery_days = db.Column(db.Integer, comment='交货天数')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'category_name': self.category_name,
            'subject_name': self.subject_name,
            'is_blown_film': self.is_blown_film,
            'delivery_days': self.delivery_days,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            from app.models.user import User
            created_user = User.get_by_id(self.created_by) if self.created_by else None
            updated_user = User.get_by_id(self.updated_by) if self.updated_by else None
            
            result.update({
                'created_by_name': created_user.get_full_name() if created_user else None,
                'updated_by_name': updated_user.get_full_name() if updated_user else None,
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的产品分类列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.category_name).all()
    
    def __repr__(self):
        return f'<ProductCategory {self.category_name}>'


class PackageMethod(TenantModel):
    """包装方式模型"""
    __tablename__ = 'package_methods'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_name = db.Column(db.String(100), nullable=False, comment='包装方式名称')
    package_code = db.Column(db.String(50), unique=True, nullable=True, comment='包装方式编码')
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'package_name': self.package_name,
            'package_code': self.package_code,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户名信息，需要关联用户表
            pass
            
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的包装方式列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.created_at).all()
    
    def __repr__(self):
        return f'<PackageMethod {self.package_name}>'


class DeliveryMethod(TenantModel):
    """送货方式模型"""
    __tablename__ = 'delivery_methods'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_name = db.Column(db.String(100), nullable=False, comment='送货方式名称')
    delivery_code = db.Column(db.String(50), unique=True, nullable=True, comment='送货方式编码')
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'delivery_name': self.delivery_name,
            'delivery_code': self.delivery_code,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的送货方式列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.delivery_name).all()
    
    def __repr__(self):
        return f'<DeliveryMethod {self.delivery_name}>'


class ColorCard(TenantModel):
    """色卡模型"""
    __tablename__ = 'color_cards'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    color_code = db.Column(db.String(50), unique=True, nullable=False, comment='色卡编号(SK开头+8位数字)')
    color_name = db.Column(db.String(100), nullable=False, comment='色卡名称')
    color_value = db.Column(db.String(20), nullable=False, comment='色值(十六进制)')
    remarks = db.Column(db.Text, comment='备注')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'color_code': self.color_code,
            'color_name': self.color_name,
            'color_value': self.color_value,
            'remarks': self.remarks,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的色卡列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.color_name).all()
    
    @classmethod
    def generate_color_code(cls):
        """生成色卡编号 SK + 8位自增数字"""
        # 设置schema路径
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
        
        # 获取当前最大编号
        latest = cls.query.filter(
            cls.color_code.like('SK%')
        ).order_by(cls.color_code.desc()).first()
        
        if latest and latest.color_code.startswith('SK'):
            try:
                # 提取数字部分并加1
                number_part = latest.color_code[2:]
                next_number = int(number_part) + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        # 格式化为8位数字
        return f"SK{next_number:08d}"
    
    def __repr__(self):
        return f'<ColorCard {self.color_name}({self.color_code})>'


class Unit(TenantModel):
    """单位模型"""
    __tablename__ = 'units'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_name = db.Column(db.String(100), nullable=False, comment='单位名称')
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'unit_name': self.unit_name,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户信息的查询逻辑
            pass
            
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的单位列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.unit_name).all()
    
    def __repr__(self):
        return f'<Unit {self.unit_name}>'


class CustomerCategoryManagement(TenantModel):
    """客户分类管理模型"""
    __tablename__ = 'customer_category_management'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name = db.Column(db.String(100), nullable=False, comment='客户分类名称')
    category_code = db.Column(db.String(50), nullable=True, comment='客户分类编码')
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'category_name': self.category_name,
            'category_code': self.category_code,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户信息的查询逻辑
            pass
            
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的客户分类列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.category_name).all()
    
    def __repr__(self):
        return f'<CustomerCategoryManagement {self.category_name}>'


class SupplierCategoryManagement(TenantModel):
    """供应商分类管理模型"""
    __tablename__ = 'supplier_category_management'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name = db.Column(db.String(100), nullable=False, comment='供应商分类名称')
    category_code = db.Column(db.String(50), nullable=True, comment='供应商分类编码')
    description = db.Column(db.Text, comment='描述')
    
    # 特殊业务字段
    is_plate_making = db.Column(db.Boolean, default=False, comment='制版')
    is_outsourcing = db.Column(db.Boolean, default=False, comment='外发')
    is_knife_plate = db.Column(db.Boolean, default=False, comment='刀板')
    
    # 通用字段
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'category_name': self.category_name,
            'category_code': self.category_code,
            'description': self.description,
            'is_plate_making': self.is_plate_making,
            'is_outsourcing': self.is_outsourcing,
            'is_knife_plate': self.is_knife_plate,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户信息的查询逻辑
            pass
            
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的供应商分类列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.category_name).all()
    
    def __repr__(self):
        return f'<SupplierCategoryManagement {self.category_name}>'


class Specification(TenantModel):
    """规格模型"""
    __tablename__ = 'specifications'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spec_name = db.Column(db.String(100), nullable=False, comment='规格名称')
    length = db.Column(db.Numeric(10, 3), nullable=False, comment='长(m)')
    width = db.Column(db.Numeric(10, 3), nullable=False, comment='宽(mm)')
    roll = db.Column(db.Numeric(10, 3), nullable=False, comment='卷')
    area_sqm = db.Column(db.Numeric(15, 6), comment='面积(平方米)')
    spec_format = db.Column(db.String(200), comment='规格格式(长×宽×卷)')
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def calculate_area_and_format(self):
        """计算面积和格式字符串"""
        if self.length and self.width and self.roll:
            # 长(m) × 宽(mm转换为m) × 卷 = 平方米
            # 宽度从mm转换为m需要除以1000
            width_in_meters = float(self.width) / 1000
            self.area_sqm = float(self.length) * width_in_meters * float(self.roll)
            
            # 格式字符串：长×宽×卷
            self.spec_format = f"{self.length}×{self.width}×{self.roll}"
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'spec_name': self.spec_name,
            'length': float(self.length) if self.length else None,
            'width': float(self.width) if self.width else None,
            'roll': float(self.roll) if self.roll else None,
            'area_sqm': float(self.area_sqm) if self.area_sqm else None,
            'spec_format': self.spec_format,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户信息的查询逻辑
            pass
            
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的规格列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.spec_name).all()
    
    def __repr__(self):
        return f'<Specification {self.spec_name}>'


class Currency(TenantModel):
    """币别模型"""
    __tablename__ = 'currencies'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    currency_code = db.Column(db.String(10), unique=True, nullable=False, comment='币别代码(如CNY,USD)')
    currency_name = db.Column(db.String(100), nullable=False, comment='币别名称')
    exchange_rate = db.Column(db.Numeric(10, 4), nullable=False, default=1.0000, comment='汇率')
    is_base_currency = db.Column(db.Boolean, default=False, comment='是否本位币')
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'currency_code': self.currency_code,
            'currency_name': self.currency_name,
            'exchange_rate': float(self.exchange_rate) if self.exchange_rate else 1.0,
            'is_base_currency': self.is_base_currency,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户信息的查询逻辑
            pass
            
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的币别列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.currency_code).all()
    
    @classmethod
    def get_base_currency(cls):
        """获取本位币"""
        return cls.query.filter_by(is_base_currency=True, is_enabled=True).first()
    
    def set_as_base_currency(self):
        """设置为本位币（会将其他币别的本位币标记移除）"""
        # 先将所有币别的本位币标记设为False
        Currency.query.filter_by(is_base_currency=True).update({'is_base_currency': False})
        # 设置当前币别为本位币
        self.is_base_currency = True
        db.session.commit()
    
    def __repr__(self):
        return f'<Currency {self.currency_name}({self.currency_code})>' 


class TaxRate(TenantModel):
    """税率管理模型"""
    __tablename__ = 'tax_rates'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    tax_name = db.Column(db.String(100), nullable=False, comment='税收')
    tax_rate = db.Column(db.Numeric(5, 2), nullable=False, comment='税率%')
    is_default = db.Column(db.Boolean, default=False, comment='评审默认')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'tax_name': self.tax_name,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'is_default': self.is_default,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            data.update({
                'created_by': str(self.created_by) if self.created_by else None,
                'updated_by': str(self.updated_by) if self.updated_by else None,
            })
        
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的税率列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.tax_name).all()
    
    @classmethod
    def get_default_tax_rate(cls):
        """获取默认税率"""
        return cls.query.filter_by(is_default=True, is_enabled=True).first()
    
    def set_as_default(self):
        """设置为默认税率"""
        # 先取消其他税率的默认状态
        cls = self.__class__
        cls.query.filter_by(is_default=True).update({'is_default': False})
        # 设置当前税率为默认
        self.is_default = True
        db.session.commit()
    
    def __repr__(self):
        return f'<TaxRate {self.tax_name}: {self.tax_rate}%>'


class SettlementMethod(TenantModel):
    """结算方式模型"""
    __tablename__ = 'settlement_methods'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 专享字段
    settlement_name = db.Column(db.String(100), nullable=False, comment='结算方式')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'settlement_name': self.settlement_name,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            result.update({
                'created_by': str(self.created_by) if self.created_by else None,
                'updated_by': str(self.updated_by) if self.updated_by else None,
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的结算方式列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.created_at).all()
    
    def __repr__(self):
        return f'<SettlementMethod {self.settlement_name}>'


class AccountManagement(TenantModel):
    """账户管理模型"""
    __tablename__ = 'account_management'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 专享字段
    account_name = db.Column(db.String(200), nullable=False, comment='账户名称')
    account_type = db.Column(db.String(50), nullable=False, comment='账户类型')
    currency_id = db.Column(UUID(as_uuid=True), comment='币别ID')
    bank_name = db.Column(db.String(200), comment='开户银行')
    bank_account = db.Column(db.String(100), comment='银行账户')
    opening_date = db.Column(db.Date, comment='开户日期')
    opening_address = db.Column(db.String(500), comment='开户地址')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'account_name': self.account_name,
            'account_type': self.account_type,
            'currency_id': str(self.currency_id) if self.currency_id else None,
            'bank_name': self.bank_name,
            'bank_account': self.bank_account,
            'opening_date': self.opening_date.isoformat() if self.opening_date else None,
            'opening_address': self.opening_address,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户信息的查询逻辑
            result.update({
                'created_by': str(self.created_by) if self.created_by else None,
                'updated_by': str(self.updated_by) if self.updated_by else None,
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的账户列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.created_at).all()
    
    def __repr__(self):
        return f'<AccountManagement {self.account_name}>'


class PaymentMethod(TenantModel):
    """付款方式模型"""
    __tablename__ = 'payment_methods'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 专享字段
    payment_name = db.Column(db.String(100), nullable=False, comment='付款方式')
    cash_on_delivery = db.Column(db.Boolean, default=False, comment='货到付款')
    monthly_settlement = db.Column(db.Boolean, default=False, comment='月结')
    next_month_settlement = db.Column(db.Boolean, default=False, comment='次月结')
    cash_on_delivery_days = db.Column(db.Integer, default=0, comment='货到付款日')
    monthly_settlement_days = db.Column(db.Integer, default=0, comment='月结天数')
    monthly_reconciliation_day = db.Column(db.Integer, default=0, comment='每月对账日')
    next_month_settlement_count = db.Column(db.Integer, default=0, comment='次月月结数')
    monthly_payment_day = db.Column(db.Integer, default=0, comment='每月付款日')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'payment_name': self.payment_name,
            'cash_on_delivery': self.cash_on_delivery,
            'monthly_settlement': self.monthly_settlement,
            'next_month_settlement': self.next_month_settlement,
            'cash_on_delivery_days': self.cash_on_delivery_days,
            'monthly_settlement_days': self.monthly_settlement_days,
            'monthly_reconciliation_day': self.monthly_reconciliation_day,
            'next_month_settlement_count': self.next_month_settlement_count,
            'monthly_payment_day': self.monthly_payment_day,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户信息的查询逻辑
            result.update({
                'created_by_name': '',  # 需要根据created_by查询用户名
                'updated_by_name': '',  # 需要根据updated_by查询用户名
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的付款方式列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.payment_name).all()
    
    def __repr__(self):
        return f'<PaymentMethod {self.payment_name}>'


class InkOption(TenantModel):
    """油墨选项模型"""
    __tablename__ = 'ink_options'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    option_name = db.Column(db.String(100), nullable=False, comment='选项名称')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    description = db.Column(db.Text, comment='描述')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'option_name': self.option_name,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'description': self.description,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户信息的查询逻辑
            pass
            
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的油墨选项列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.option_name).all()
    
    def __repr__(self):
        return f'<InkOption {self.option_name}>'


class QuoteFreight(TenantModel):
    """报价运费模型"""
    __tablename__ = 'quote_freights'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region = db.Column(db.String(100), nullable=False, comment='区域')
    percentage = db.Column(db.Numeric(5, 2), nullable=False, default=0, comment='百分比')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    description = db.Column(db.Text, comment='描述')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'region': self.region,
            'percentage': float(self.percentage) if self.percentage else 0,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'description': self.description,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户信息的查询逻辑
            pass
            
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的报价运费列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.region).all()
    
    def __repr__(self):
        return f'<QuoteFreight {self.region}>'


class MaterialCategory(TenantModel):
    """材料分类模型"""
    __tablename__ = 'material_categories'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    material_name = db.Column(db.String(100), nullable=False, comment='材料分类名称')
    material_type = db.Column(db.String(20), nullable=False, comment='材料属性(主材/辅材)')
    
    # 单位信息
    base_unit_id = db.Column(UUID(as_uuid=True), comment='基本单位ID')
    auxiliary_unit_id = db.Column(UUID(as_uuid=True), comment='辅助单位ID')
    sales_unit_id = db.Column(UUID(as_uuid=True), comment='销售单位ID')
    
    # 物理属性
    density = db.Column(db.Numeric(10, 4), comment='密度')
    square_weight = db.Column(db.Numeric(10, 4), comment='平方克重')
    shelf_life = db.Column(db.Integer, comment='保质期(天)')
    
    # 检验质量
    inspection_standard = db.Column(db.String(200), comment='检验标准')
    quality_grade = db.Column(db.String(100), comment='质量等级')
    
    # 价格信息
    latest_purchase_price = db.Column(db.Numeric(15, 4), comment='最近采购价')
    sales_price = db.Column(db.Numeric(15, 4), comment='销售价')
    product_quote_price = db.Column(db.Numeric(15, 4), comment='产品报价')
    cost_price = db.Column(db.Numeric(15, 4), comment='成本价格')
    
    # 业务配置
    show_on_kanban = db.Column(db.Boolean, default=False, comment='看板显示')
    account_subject = db.Column(db.String(100), comment='科目')
    code_prefix = db.Column(db.String(10), default='M', comment='编码前缀')
    warning_days = db.Column(db.Integer, comment='预警天数')
    
    # 纸箱参数
    carton_param1 = db.Column(db.Numeric(10, 3), comment='纸箱参数1')
    carton_param2 = db.Column(db.Numeric(10, 3), comment='纸箱参数2')
    carton_param3 = db.Column(db.Numeric(10, 3), comment='纸箱参数3')
    carton_param4 = db.Column(db.Numeric(10, 3), comment='纸箱参数4')
    
    # 材料属性标识
    enable_batch = db.Column(db.Boolean, default=False, comment='启用批次')
    enable_barcode = db.Column(db.Boolean, default=False, comment='启用条码')
    is_ink = db.Column(db.Boolean, default=False, comment='是否油墨')
    is_accessory = db.Column(db.Boolean, default=False, comment='是否辅料')
    is_consumable = db.Column(db.Boolean, default=False, comment='是否耗材')
    is_recyclable = db.Column(db.Boolean, default=False, comment='是否可回收')
    is_hazardous = db.Column(db.Boolean, default=False, comment='是否危险品')
    is_imported = db.Column(db.Boolean, default=False, comment='是否进口')
    is_customized = db.Column(db.Boolean, default=False, comment='是否定制')
    is_seasonal = db.Column(db.Boolean, default=False, comment='是否季节性')
    is_fragile = db.Column(db.Boolean, default=False, comment='是否易碎')
    is_perishable = db.Column(db.Boolean, default=False, comment='是否易腐')
    is_temperature_sensitive = db.Column(db.Boolean, default=False, comment='是否温度敏感')
    is_moisture_sensitive = db.Column(db.Boolean, default=False, comment='是否湿度敏感')
    is_light_sensitive = db.Column(db.Boolean, default=False, comment='是否光敏感')
    requires_special_storage = db.Column(db.Boolean, default=False, comment='是否需要特殊存储')
    requires_certification = db.Column(db.Boolean, default=False, comment='是否需要认证')
    
    # 通用字段
    display_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    __table_args__ = (
        db.CheckConstraint("material_type IN ('主材', '辅材')", name='material_categories_type_check'),
    )
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'material_name': self.material_name,
            'material_type': self.material_type,
            'base_unit_id': str(self.base_unit_id) if self.base_unit_id else None,
            'auxiliary_unit_id': str(self.auxiliary_unit_id) if self.auxiliary_unit_id else None,
            'sales_unit_id': str(self.sales_unit_id) if self.sales_unit_id else None,
            'density': float(self.density) if self.density else None,
            'square_weight': float(self.square_weight) if self.square_weight else None,
            'shelf_life': self.shelf_life,
            'inspection_standard': self.inspection_standard,
            'quality_grade': self.quality_grade,
            'latest_purchase_price': float(self.latest_purchase_price) if self.latest_purchase_price else None,
            'sales_price': float(self.sales_price) if self.sales_price else None,
            'product_quote_price': float(self.product_quote_price) if self.product_quote_price else None,
            'cost_price': float(self.cost_price) if self.cost_price else None,
            'show_on_kanban': self.show_on_kanban,
            'account_subject': self.account_subject,
            'code_prefix': self.code_prefix,
            'warning_days': self.warning_days,
            'carton_param1': float(self.carton_param1) if self.carton_param1 else None,
            'carton_param2': float(self.carton_param2) if self.carton_param2 else None,
            'carton_param3': float(self.carton_param3) if self.carton_param3 else None,
            'carton_param4': float(self.carton_param4) if self.carton_param4 else None,
            'enable_batch': self.enable_batch,
            'enable_barcode': self.enable_barcode,
            'is_ink': self.is_ink,
            'is_accessory': self.is_accessory,
            'is_consumable': self.is_consumable,
            'is_recyclable': self.is_recyclable,
            'is_hazardous': self.is_hazardous,
            'is_imported': self.is_imported,
            'is_customized': self.is_customized,
            'is_seasonal': self.is_seasonal,
            'is_fragile': self.is_fragile,
            'is_perishable': self.is_perishable,
            'is_temperature_sensitive': self.is_temperature_sensitive,
            'is_moisture_sensitive': self.is_moisture_sensitive,
            'is_light_sensitive': self.is_light_sensitive,
            'requires_special_storage': self.requires_special_storage,
            'requires_certification': self.requires_certification,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            from app.models.user import User
            created_user = User.get_by_id(self.created_by) if self.created_by else None
            updated_user = User.get_by_id(self.updated_by) if self.updated_by else None
            
            result.update({
                'created_by_name': created_user.get_full_name() if created_user else None,
                'updated_by_name': updated_user.get_full_name() if updated_user else None,
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的材料分类列表"""
        return cls.query.filter_by(is_active=True).order_by(cls.display_order, cls.material_name).all()
    
    def __repr__(self):
        return f'<MaterialCategory {self.material_name}>'


class CalculationParameter(TenantModel):
    """计算参数模型"""
    __tablename__ = 'calculation_parameters'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parameter_name = db.Column(db.String(100), nullable=False, comment='计算参数')
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'parameter_name': self.parameter_name,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            from app.models.user import User
            created_user = User.get_by_id(self.created_by) if self.created_by else None
            updated_user = User.get_by_id(self.updated_by) if self.updated_by else None
            
            data.update({
                'created_by_name': created_user.get_full_name() if created_user else None,
                'updated_by_name': updated_user.get_full_name() if updated_user else None,
            })
        
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的计算参数列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.parameter_name).all()
    
    def __repr__(self):
        return f'<CalculationParameter {self.parameter_name}>'


class CalculationScheme(TenantModel):
    """计算方案模型"""
    __tablename__ = 'calculation_schemes'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_name = db.Column(db.String(100), nullable=False, comment='方案名称')
    scheme_category = db.Column(db.String(50), nullable=False, comment='方案分类')
    scheme_formula = db.Column(db.Text, comment='方案公式')
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 方案分类常量
    SCHEME_CATEGORIES = [
        ('bag_spec', '袋型规格'),
        ('bag_formula', '袋型公式'),
        ('bag_quote', '袋型报价'),
        ('material_usage', '材料用料'),
        ('material_quote', '材料报价'),
        ('process_quote', '工序报价'),
        ('process_loss', '工序损耗'),
        ('process_bonus', '工序节约奖'),
        ('process_piece', '工序计件'),
        ('process_other', '工序其它'),
        ('multiple_formula', '倍送公式')
    ]
    
    __table_args__ = (
        db.CheckConstraint(
            "scheme_category IN ('bag_spec', 'bag_formula', 'bag_quote', 'material_usage', 'material_quote', 'process_quote', 'process_loss', 'process_bonus', 'process_piece', 'process_other', 'multiple_formula')", 
            name='calculation_schemes_category_check'
        ),
    )
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'scheme_name': self.scheme_name,
            'scheme_category': self.scheme_category,
            'scheme_formula': self.scheme_formula,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            from app.models.user import User
            created_user = User.get_by_id(self.created_by) if self.created_by else None
            updated_user = User.get_by_id(self.updated_by) if self.updated_by else None
            
            data.update({
                'created_by_name': created_user.get_full_name() if created_user else None,
                'updated_by_name': updated_user.get_full_name() if updated_user else None,
            })
        
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的计算方案列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.scheme_name).all()
    
    @classmethod
    def get_scheme_categories(cls):
        """获取方案分类选项"""
        return [{'value': value, 'label': label} for value, label in cls.SCHEME_CATEGORIES]
    
    def __repr__(self):
        return f'<CalculationScheme {self.scheme_name}>'


class LossType(TenantModel):
    """报损类型模型"""
    __tablename__ = 'loss_types'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loss_type_name = db.Column(db.String(100), nullable=False, comment='报损类型名称')
    process_id = db.Column(UUID(as_uuid=True), comment='工序ID')
    loss_category_id = db.Column(UUID(as_uuid=True), comment='报损分类ID')
    is_assessment = db.Column(db.Boolean, default=False, comment='是否考核')
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'loss_type_name': self.loss_type_name,
            'process_id': str(self.process_id) if self.process_id else None,
            'loss_category_id': str(self.loss_category_id) if self.loss_category_id else None,
            'is_assessment': self.is_assessment,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            from app.models.user import User
            if self.created_by:
                created_user = User.query.get(self.created_by)
                data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
            else:
                data['created_by_name'] = '系统'
                
            if self.updated_by:
                updated_user = User.query.get(self.updated_by)
                data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
            else:
                data['updated_by_name'] = ''
            
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的报损类型列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.loss_type_name).all()
    
    def __repr__(self):
        return f'<LossType {self.loss_type_name}>'


class Machine(TenantModel):
    """机台模型"""
    __tablename__ = 'machines'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    machine_code = db.Column(db.String(50), unique=True, nullable=False, comment='机台编号(自动生成)')
    machine_name = db.Column(db.String(100), nullable=False, comment='机台名称')
    model = db.Column(db.String(100), comment='型号')
    
    # 门幅参数
    min_width = db.Column(db.Numeric(10, 2), comment='最小上机门幅(mm)')
    max_width = db.Column(db.Numeric(10, 2), comment='最大上机门幅(mm)')
    
    # 生产参数
    production_speed = db.Column(db.Numeric(10, 2), comment='生产均速(m/h)')
    preparation_time = db.Column(db.Numeric(8, 2), comment='准备时间(h)')
    difficulty_factor = db.Column(db.Numeric(8, 4), comment='难易系数')
    circulation_card_id = db.Column(db.String(100), comment='流转卡标识')
    max_colors = db.Column(db.Integer, comment='最大印色')
    kanban_display = db.Column(db.String(200), comment='看板显示')
    
    # 产能配置
    capacity_formula = db.Column(db.String(200), comment='产能公式')
    gas_unit_price = db.Column(db.Numeric(10, 4), comment='燃气单价')
    power_consumption = db.Column(db.Numeric(10, 2), comment='功耗(kw)')
    electricity_cost_per_hour = db.Column(db.Numeric(10, 4), comment='电费(/h)')
    output_conversion_factor = db.Column(db.Numeric(8, 4), comment='产量换算倍数')
    plate_change_time = db.Column(db.Numeric(8, 2), comment='换版时间')
    
    # MES配置
    mes_barcode_prefix = db.Column(db.String(20), comment='MES条码前缀')
    is_curing_room = db.Column(db.Boolean, default=False, comment='是否熟化室')
    
    # 材料配置
    material_name = db.Column(db.String(200), comment='材料名称')
    
    # 通用字段
    remarks = db.Column(db.Text, comment='备注')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'machine_code': self.machine_code,
            'machine_name': self.machine_name,
            'model': self.model,
            'min_width': float(self.min_width) if self.min_width else None,
            'max_width': float(self.max_width) if self.max_width else None,
            'production_speed': float(self.production_speed) if self.production_speed else None,
            'preparation_time': float(self.preparation_time) if self.preparation_time else None,
            'difficulty_factor': float(self.difficulty_factor) if self.difficulty_factor else None,
            'circulation_card_id': self.circulation_card_id,
            'max_colors': self.max_colors,
            'kanban_display': self.kanban_display,
            'capacity_formula': self.capacity_formula,
            'gas_unit_price': float(self.gas_unit_price) if self.gas_unit_price else None,
            'power_consumption': float(self.power_consumption) if self.power_consumption else None,
            'electricity_cost_per_hour': float(self.electricity_cost_per_hour) if self.electricity_cost_per_hour else None,
            'output_conversion_factor': float(self.output_conversion_factor) if self.output_conversion_factor else None,
            'plate_change_time': float(self.plate_change_time) if self.plate_change_time else None,
            'mes_barcode_prefix': self.mes_barcode_prefix,
            'is_curing_room': self.is_curing_room,
            'material_name': self.material_name,
            'remarks': self.remarks,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            result.update({
                'created_by_name': getattr(self.created_by_user, 'username', '') if hasattr(self, 'created_by_user') and self.created_by_user else '',
                'updated_by_name': getattr(self.updated_by_user, 'username', '') if hasattr(self, 'updated_by_user') and self.updated_by_user else '',
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的机台列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.machine_name).all()
    
    @classmethod
    def generate_machine_code(cls):
        """生成机台编号"""
        from sqlalchemy import func, text
        from flask import g, current_app
        
        # 设置schema路径
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
        
        # 获取当前最大编号
        max_code = db.session.query(func.max(cls.machine_code)).scalar()
        
        if max_code:
            # 提取数字部分并加1
            try:
                num_part = int(max_code.replace('MT', ''))
                new_num = num_part + 1
            except (ValueError, AttributeError):
                new_num = 1
        else:
            new_num = 1
        
        # 生成新编号，格式：MT + 4位数字
        return f"MT{new_num:04d}"
    
    def __repr__(self):
        return f'<Machine {self.machine_name}>'


class QuoteInk(TenantModel):
    """报价油墨模型"""
    __tablename__ = 'quote_inks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    category_name = db.Column(db.String(100), nullable=False, comment='分类名称')
    square_price = db.Column(db.Numeric(10, 4), comment='平方价')
    unit_price_formula = db.Column(db.String(200), comment='单价计算公式')
    gram_weight = db.Column(db.Numeric(10, 4), comment='克重')
    
    # 类型标识
    is_ink = db.Column(db.Boolean, default=False, comment='油墨')
    is_solvent = db.Column(db.Boolean, default=False, comment='溶剂')
    
    # 通用字段
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    description = db.Column(db.Text, comment='描述')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'category_name': self.category_name,
            'square_price': float(self.square_price) if self.square_price else None,
            'unit_price_formula': self.unit_price_formula,
            'gram_weight': float(self.gram_weight) if self.gram_weight else None,
            'is_ink': self.is_ink,
            'is_solvent': self.is_solvent,
            'sort_order': self.sort_order,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            result.update({
                'created_by_name': getattr(self.created_by_user, 'username', '') if hasattr(self, 'created_by_user') and self.created_by_user else '',
                'updated_by_name': getattr(self.updated_by_user, 'username', '') if hasattr(self, 'updated_by_user') and self.updated_by_user else '',
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的报价油墨列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.category_name).all()
    
    def __repr__(self):
        return f'<QuoteInk {self.category_name}>'


class QuoteMaterial(TenantModel):
    """报价材料模型"""
    __tablename__ = 'quote_materials'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    material_name = db.Column(db.String(100), nullable=False, comment='材料名称')
    density = db.Column(db.Numeric(10, 4), comment='密度')
    kg_price = db.Column(db.Numeric(15, 4), comment='公斤价')
    
    # 层级选项
    layer_1_optional = db.Column(db.Boolean, default=False, comment='一层可选')
    layer_2_optional = db.Column(db.Boolean, default=False, comment='二层可选')
    layer_3_optional = db.Column(db.Boolean, default=False, comment='三层可选')
    layer_4_optional = db.Column(db.Boolean, default=False, comment='四层可选')
    layer_5_optional = db.Column(db.Boolean, default=False, comment='五层可选')
    
    # 通用字段
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    remarks = db.Column(db.Text, comment='备注')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'material_name': self.material_name,
            'density': float(self.density) if self.density else None,
            'kg_price': float(self.kg_price) if self.kg_price else None,
            'layer_1_optional': self.layer_1_optional,
            'layer_2_optional': self.layer_2_optional,
            'layer_3_optional': self.layer_3_optional,
            'layer_4_optional': self.layer_4_optional,
            'layer_5_optional': self.layer_5_optional,
            'sort_order': self.sort_order,
            'remarks': self.remarks,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户名信息，需要关联用户表
            pass
            
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的报价材料列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.created_at).all()
    
    def __repr__(self):
        return f'<QuoteMaterial {self.material_name}>'


class QuoteAccessory(TenantModel):
    """报价辅材模型"""
    __tablename__ = 'quote_accessories'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    material_name = db.Column(db.String(100), nullable=False, comment='材料名称')
    unit_price = db.Column(db.Numeric(15, 4), comment='单价')
    # 修改为关联计算方案ID，只选择材料报价分类的方案
    calculation_scheme_id = db.Column(UUID(as_uuid=True), db.ForeignKey('calculation_schemes.id'), comment='单价计算方案ID')
    
    # 通用字段
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    description = db.Column(db.Text, comment='描述')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联计算方案
    calculation_scheme = db.relationship('CalculationScheme', backref='quote_accessories', lazy='select')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'material_name': self.material_name,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'calculation_scheme_id': str(self.calculation_scheme_id) if self.calculation_scheme_id else None,
            'calculation_scheme_name': self.calculation_scheme.scheme_name if self.calculation_scheme else None,
            'sort_order': self.sort_order,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            result.update({
                'created_by_name': getattr(self.created_by_user, 'username', '') if hasattr(self, 'created_by_user') and self.created_by_user else '',
                'updated_by_name': getattr(self.updated_by_user, 'username', '') if hasattr(self, 'updated_by_user') and self.updated_by_user else '',
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的报价辅材列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.created_at).all()
    
    def __repr__(self):
        return f'<QuoteAccessory {self.material_name}>'


class QuoteLoss(TenantModel):
    """报价损耗模型"""
    __tablename__ = 'quote_losses'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 专享字段
    bag_type = db.Column(db.String(100), nullable=False, comment='袋型')
    layer_count = db.Column(db.Integer, nullable=False, comment='层数')
    meter_range = db.Column(db.Numeric(10, 2), nullable=False, comment='米数区间')
    loss_rate = db.Column(db.Numeric(8, 4), nullable=False, comment='损耗')
    cost = db.Column(db.Numeric(15, 4), nullable=False, comment='费用')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'bag_type': self.bag_type,
            'layer_count': self.layer_count,
            'meter_range': float(self.meter_range) if self.meter_range else None,
            'loss_rate': float(self.loss_rate) if self.loss_rate else None,
            'cost': float(self.cost) if self.cost else None,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            # 这里可以添加用户名信息，需要关联用户表
            pass
            
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的报价损耗列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.created_at).all()
    
    def __repr__(self):
        return f'<QuoteLoss {self.bag_type}-{self.layer_count}层>'


class Department(TenantModel):
    """部门管理模型"""
    __tablename__ = 'departments'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 专享字段
    dept_code = db.Column(db.String(50), unique=True, nullable=False, comment='部门编号')
    dept_name = db.Column(db.String(100), nullable=False, comment='部门名称')
    parent_id = db.Column(UUID(as_uuid=True), db.ForeignKey('departments.id'), comment='上级部门ID')
    is_blown_film = db.Column(db.Boolean, default=False, comment='是否吹膜')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 自引用关系
    parent = db.relationship('Department', remote_side=[id], backref='children')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'dept_code': self.dept_code,
            'dept_name': self.dept_name,
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'parent_name': self.parent.dept_name if self.parent else None,
            'is_blown_film': self.is_blown_film,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            from app.models.user import User
            
            # 获取创建人信息
            created_by_name = None
            if self.created_by:
                try:
                    created_user = db.session.query(User).filter_by(id=self.created_by).first()
                    created_by_name = created_user.get_full_name() if created_user else None
                except Exception:
                    created_by_name = None
            
            # 获取修改人信息
            updated_by_name = None
            if self.updated_by:
                try:
                    updated_user = db.session.query(User).filter_by(id=self.updated_by).first()
                    updated_by_name = updated_user.get_full_name() if updated_user else None
                except Exception:
                    updated_by_name = None
            
            result.update({
                'created_by_name': created_by_name,
                'updated_by_name': updated_by_name,
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的部门列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.dept_name).all()
    
    @classmethod
    def get_department_tree(cls):
        """获取部门树形结构"""
        departments = cls.get_enabled_list()
        
        # 构建树形结构
        dept_dict = {dept.id: dept.to_dict() for dept in departments}
        tree = []
        
        for dept in departments:
            dept_data = dept_dict[dept.id]
            if dept.parent_id:
                parent = dept_dict.get(dept.parent_id)
                if parent:
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(dept_data)
            else:
                tree.append(dept_data)
        
        return tree
    
    @classmethod
    def generate_dept_code(cls):
        """生成部门编号 DEPT + 4位自增数字"""
        from sqlalchemy import func
        
        # 获取当前最大编号
        max_code = db.session.query(func.max(cls.dept_code)).scalar()
        
        if max_code and max_code.startswith('DEPT'):
            try:
                # 提取数字部分并加1
                number_part = max_code[4:]
                next_number = int(number_part) + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        # 格式化为4位数字
        return f"DEPT{next_number:04d}"
    
    def __repr__(self):
        return f'<Department {self.dept_name}({self.dept_code})>'


class Position(TenantModel):
    """职位管理模型"""
    __tablename__ = 'positions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    position_name = db.Column(db.String(100), nullable=False, comment='职位名称')
    department_id = db.Column(UUID(as_uuid=True), db.ForeignKey('departments.id'), nullable=False, comment='部门ID')
    parent_position_id = db.Column(UUID(as_uuid=True), db.ForeignKey('positions.id'), nullable=True, comment='上级职位ID')
    
    # 薪资和绩效
    hourly_wage = db.Column(db.Numeric(10, 2), comment='职位工资/小时')
    standard_pass_rate = db.Column(db.Numeric(5, 2), comment='标准合格率(%)')
    
    # 职位标识
    is_supervisor = db.Column(db.Boolean, default=False, comment='是否主管')
    is_machine_operator = db.Column(db.Boolean, default=False, comment='是否机长')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联关系
    department = db.relationship('Department', backref='positions', lazy='select')
    parent_position = db.relationship('Position', remote_side=[id], backref='sub_positions')
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'position_name': self.position_name,
            'department_id': str(self.department_id) if self.department_id else None,
            'department_name': self.department.dept_name if self.department else None,
            'parent_position_id': str(self.parent_position_id) if self.parent_position_id else None,
            'parent_position_name': self.parent_position.position_name if self.parent_position else None,
            'hourly_wage': float(self.hourly_wage) if self.hourly_wage else None,
            'standard_pass_rate': float(self.standard_pass_rate) if self.standard_pass_rate else None,
            'is_supervisor': self.is_supervisor,
            'is_machine_operator': self.is_machine_operator,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            from app.models.user import User
            
            # 获取创建人信息
            created_by_name = None
            if self.created_by:
                try:
                    created_user = db.session.query(User).filter_by(id=self.created_by).first()
                    created_by_name = created_user.get_full_name() if created_user else None
                except Exception:
                    created_by_name = None
            
            # 获取修改人信息
            updated_by_name = None
            if self.updated_by:
                try:
                    updated_user = db.session.query(User).filter_by(id=self.updated_by).first()
                    updated_by_name = updated_user.get_full_name() if updated_user else None
                except Exception:
                    updated_by_name = None
            
            result.update({
                'created_by_name': created_by_name,
                'updated_by_name': updated_by_name,
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的职位列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.position_name).all()
    
    def __repr__(self):
        return f'<Position {self.position_name}>'


class Employee(TenantModel):
    """员工管理模型"""
    __tablename__ = 'employees'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    employee_id = db.Column(db.String(50), unique=True, nullable=False, comment='员工工号')
    employee_name = db.Column(db.String(100), nullable=False, comment='员工姓名')
    position_id = db.Column(UUID(as_uuid=True), db.ForeignKey('positions.id'), comment='职位ID')
    department_id = db.Column(UUID(as_uuid=True), db.ForeignKey('departments.id'), comment='部门ID(根据职位自动填入)')
    
    # 在职状态和基本信息
    employment_status = db.Column(db.String(20), default='trial', comment='在职状态(trial试用/active在职/leave离职/suspended停职)')
    business_type = db.Column(db.String(20), comment='业务类型(salesperson业务员/purchaser采购员/comprehensive综合/delivery_person送货员)')
    gender = db.Column(db.String(20), comment='性别(male男/female女/confidential保密)')
    mobile_phone = db.Column(db.String(20), comment='手机')
    landline_phone = db.Column(db.String(20), comment='电话')
    emergency_phone = db.Column(db.String(20), comment='紧急电话')
    hire_date = db.Column(db.Date, comment='入职日期')
    birth_date = db.Column(db.Date, comment='出生日期')
    circulation_card_id = db.Column(db.String(50), comment='流转卡标识')
    workshop_id = db.Column(db.String(50), comment='车间工号')
    id_number = db.Column(db.String(50), comment='身份证号')
    
    # 工资信息
    salary_1 = db.Column(db.Numeric(10, 2), default=0, comment='工资1')
    salary_2 = db.Column(db.Numeric(10, 2), default=0, comment='工资2')
    salary_3 = db.Column(db.Numeric(10, 2), default=0, comment='工资3')
    salary_4 = db.Column(db.Numeric(10, 2), default=0, comment='工资4')
    
    # 籍贯和地址信息
    native_place = db.Column(db.String(200), comment='籍贯')
    ethnicity = db.Column(db.String(50), comment='民族')
    province = db.Column(db.String(100), comment='省/自治区')
    city = db.Column(db.String(100), comment='地/市')
    district = db.Column(db.String(100), comment='区/县')
    street = db.Column(db.String(100), comment='街/乡')
    birth_address = db.Column(db.Text, comment='出生地址')
    archive_location = db.Column(db.Text, comment='档案所在地')
    household_registration = db.Column(db.Text, comment='户口所在地')
    
    # 合同和工作信息
    evaluation_level = db.Column(db.String(50), comment='评量流程级别(finance财务/technology工艺/supply供应/marketing营销)')
    leave_date = db.Column(db.Date, comment='离职日期')
    seniority_wage = db.Column(db.Numeric(10, 2), comment='工龄工资')
    assessment_wage = db.Column(db.Numeric(10, 2), comment='考核工资')
    contract_start_date = db.Column(db.Date, comment='合同签订日期')
    contract_end_date = db.Column(db.Date, comment='合同终止日期')
    expiry_warning_date = db.Column(db.Date, comment='到期预警日期')
    ufida_code = db.Column(db.String(100), comment='用友编码')
    
    # 系统配置
    kingdee_push = db.Column(db.Boolean, default=False, comment='金蝶推送')
    
    # 备注
    remarks = db.Column(db.Text, comment='备注')
    
    # 通用字段
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联关系
    position = db.relationship('Position', backref='employees', lazy='select')
    department = db.relationship('Department', backref='employees', lazy='select')
    
    __table_args__ = (
        db.CheckConstraint("employment_status IN ('trial', 'active', 'leave')", name='employees_status_check'),
        db.CheckConstraint("gender IN ('male', 'female', 'confidential')", name='employees_gender_check'),
        db.CheckConstraint("business_type IN ('salesperson', 'purchaser', 'comprehensive', 'delivery_person')", name='employees_business_type_check'),
        db.CheckConstraint("evaluation_level IN ('finance', 'technology', 'supply', 'marketing')", name='employees_evaluation_level_check'),
    )
    
    def to_dict(self, include_user_info=False, include_relations=True):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'position_id': str(self.position_id) if self.position_id else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'employment_status': self.employment_status,
            'business_type': self.business_type,
            'gender': self.gender,
            'mobile_phone': self.mobile_phone,
            'landline_phone': self.landline_phone,
            'emergency_phone': self.emergency_phone,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'circulation_card_id': self.circulation_card_id,
            'workshop_id': self.workshop_id,
            'id_number': self.id_number,
            'salary_1': float(self.salary_1) if self.salary_1 else 0,
            'salary_2': float(self.salary_2) if self.salary_2 else 0,
            'salary_3': float(self.salary_3) if self.salary_3 else 0,
            'salary_4': float(self.salary_4) if self.salary_4 else 0,
            'native_place': self.native_place,
            'ethnicity': self.ethnicity,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'street': self.street,
            'birth_address': self.birth_address,
            'archive_location': self.archive_location,
            'household_registration': self.household_registration,
            'evaluation_level': self.evaluation_level,
            'leave_date': self.leave_date.isoformat() if self.leave_date else None,
            'seniority_wage': float(self.seniority_wage) if self.seniority_wage else None,
            'assessment_wage': float(self.assessment_wage) if self.assessment_wage else None,
            'contract_start_date': self.contract_start_date.isoformat() if self.contract_start_date else None,
            'contract_end_date': self.contract_end_date.isoformat() if self.contract_end_date else None,
            'expiry_warning_date': self.expiry_warning_date.isoformat() if self.expiry_warning_date else None,
            'ufida_code': self.ufida_code,
            'kingdee_push': self.kingdee_push,
            'remarks': self.remarks,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # 添加关联对象信息（带错误处理）
        if include_relations:
            try:
                if self.position:
                    result['position'] = {
                        'id': str(self.position.id),
                        'position_name': self.position.position_name
                    }
            except Exception as e:
                result['position'] = None
                
            try:
                if self.department:
                    result['department'] = {
                        'id': str(self.department.id),
                        'dept_name': self.department.dept_name
                    }
            except Exception as e:
                result['department'] = None
        
        # 如果需要用户信息
        if include_user_info:
            if hasattr(self, 'created_by_name'):
                result['created_by_name'] = self.created_by_name
            if hasattr(self, 'updated_by_name'):
                result['updated_by_name'] = self.updated_by_name
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的员工列表"""
        return cls.query.filter(cls.is_enabled == True).order_by(cls.sort_order, cls.employee_name).all()
    
    @classmethod 
    def generate_employee_id(cls):
        """生成员工工号"""
        
        # 使用当前年份后两位 + 4位序号
        year_suffix = str(datetime.now().year)[-2:]
        
        # 查询当前年份的最大序号
        prefix = year_suffix
        max_id = db.session.query(cls.employee_id).filter(
            cls.employee_id.like(f'{prefix}%')
        ).order_by(cls.employee_id.desc()).first()
        
        if max_id and max_id[0]:
            try:
                sequence = int(max_id[0][2:]) + 1  # 提取后4位并加1
            except (ValueError, IndexError):
                sequence = 1
        else:
            sequence = 1
        
        return f"{prefix}{sequence:04d}"
    
    def __repr__(self):
        return f'<Employee {self.employee_id}: {self.employee_name}>'


class Warehouse(TenantModel):
    """仓库管理模型"""
    __tablename__ = 'warehouses'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    warehouse_code = db.Column(db.String(50), unique=True, nullable=False, comment='仓库编号(自动生成)')
    warehouse_name = db.Column(db.String(100), nullable=False, comment='仓库名称')
    warehouse_type = db.Column(db.String(50), comment='仓库类型')
    parent_warehouse_id = db.Column(UUID(as_uuid=True), db.ForeignKey('warehouses.id'), comment='上级仓库ID')
    accounting_method = db.Column(db.String(50), comment='核算方式')
    
    # 业务配置
    circulation_type = db.Column(db.String(50), comment='流转类型')
    exclude_from_operations = db.Column(db.Boolean, default=False, comment='不参与运行')
    is_abnormal = db.Column(db.Boolean, default=False, comment='异常')
    is_carryover_warehouse = db.Column(db.Boolean, default=False, comment='结转仓')
    exclude_from_docking = db.Column(db.Boolean, default=False, comment='不对接')
    is_in_stocktaking = db.Column(db.Boolean, default=False, comment='盘点中')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 自引用关系
    parent_warehouse = db.relationship('Warehouse', remote_side=[id], backref='sub_warehouses')
    
    # 仓库类型常量
    WAREHOUSE_TYPES = [
        ('material', '材料'),
        ('finished_goods', '成品'),
        ('semi_finished', '半成品'),
        ('plate_roller', '版辊')
    ]
    
    # 核算方式常量
    ACCOUNTING_METHODS = [
        ('individual_cost', '个别计价'),
        ('monthly_average', '全月平均')
    ]
    
    # 流转类型常量
    CIRCULATION_TYPES = [
        ('on_site_circulation', '现场流转')
    ]
    
    __table_args__ = (
        db.CheckConstraint(
            "warehouse_type IN ('material', 'finished_goods', 'semi_finished', 'plate_roller')", 
            name='warehouses_type_check'
        ),
        db.CheckConstraint(
            "accounting_method IN ('individual_cost', 'monthly_average')", 
            name='warehouses_accounting_method_check'
        ),
        db.CheckConstraint(
            "circulation_type IN ('on_site_circulation')", 
            name='warehouses_circulation_type_check'
        ),
    )
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'warehouse_code': self.warehouse_code,
            'warehouse_name': self.warehouse_name,
            'warehouse_type': self.warehouse_type,
            'parent_warehouse_id': str(self.parent_warehouse_id) if self.parent_warehouse_id else None,
            'accounting_method': self.accounting_method,
            'circulation_type': self.circulation_type,
            'exclude_from_operations': self.exclude_from_operations,
            'is_abnormal': self.is_abnormal,
            'is_carryover_warehouse': self.is_carryover_warehouse,
            'exclude_from_docking': self.exclude_from_docking,
            'is_in_stocktaking': self.is_in_stocktaking,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # 添加上级仓库信息
        if self.parent_warehouse:
            data['parent_warehouse_name'] = self.parent_warehouse.warehouse_name
        
        if include_user_info:
            from app.models.user import User
            if self.created_by:
                created_user = User.query.get(self.created_by)
                data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
            else:
                data['created_by_name'] = '系统'
                
            if self.updated_by:
                updated_user = User.query.get(self.updated_by)
                data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
            else:
                data['updated_by_name'] = ''
        
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的仓库列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.warehouse_name).all()
    
    @classmethod
    def get_warehouse_types(cls):
        """获取仓库类型选项"""
        return [{'value': value, 'label': label} for value, label in cls.WAREHOUSE_TYPES]
    
    @classmethod
    def get_accounting_methods(cls):
        """获取核算方式选项"""
        return [{'value': value, 'label': label} for value, label in cls.ACCOUNTING_METHODS]
    
    @classmethod
    def get_circulation_types(cls):
        """获取流转类型选项"""
        return [{'value': value, 'label': label} for value, label in cls.CIRCULATION_TYPES]
    
    @classmethod
    def get_warehouse_tree(cls):
        """获取仓库树形结构"""
        try:
            # 获取所有启用的仓库
            warehouses = cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.warehouse_name).all()
            
            # 构建树形结构
            warehouse_dict = {str(warehouse.id): warehouse.to_dict() for warehouse in warehouses}
            tree = []
            
            for warehouse_dict_item in warehouse_dict.values():
                if warehouse_dict_item['parent_warehouse_id']:
                    parent = warehouse_dict.get(warehouse_dict_item['parent_warehouse_id'])
                    if parent:
                        if 'children' not in parent:
                            parent['children'] = []
                        parent['children'].append(warehouse_dict_item)
                else:
                    tree.append(warehouse_dict_item)
            
            return tree
        except Exception as e:
            print(f"获取仓库树形结构失败: {str(e)}")
            return []
    
    @classmethod
    def generate_warehouse_code(cls):
        """生成仓库编号"""
        try:
            # 使用更简单和可靠的方法生成编号
            # 查询所有以WH开头的仓库编号
            existing_codes = db.session.query(cls.warehouse_code).filter(
                cls.warehouse_code.like('WH%')
            ).all()
            
            # 提取数字部分
            max_number = 0
            for (code,) in existing_codes:
                if code and code.startswith('WH') and len(code) >= 3:
                    try:
                        number_part = code[2:]  # 去掉WH前缀
                        number = int(number_part)
                        max_number = max(max_number, number)
                    except ValueError:
                        continue
            
            # 生成新编号
            next_number = max_number + 1
            new_code = f"WH{next_number:05d}"
            
            # 确保新编号不存在（双重检查）
            while db.session.query(cls).filter(cls.warehouse_code == new_code).first():
                next_number += 1
                new_code = f"WH{next_number:05d}"
            
            return new_code
            
        except Exception as e:
            # 如果生成失败，使用时间戳方式
            print(f"仓库编号生成异常: {str(e)}")
            import time
            timestamp = int(time.time()) % 100000
            return f"WH{timestamp:05d}"
    
    def __repr__(self):
        return f'<Warehouse {self.warehouse_name}>'


class ProcessCategory(TenantModel):
    """工序分类模型"""
    __tablename__ = 'process_categories'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    process_name = db.Column(db.String(100), nullable=False, comment='工序分类')
    category_type = db.Column(db.String(50), comment='类型')  # 空或淋膜
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    data_collection_mode = db.Column(db.String(50), comment='数据自动采集模式')
    show_data_collection_interface = db.Column(db.Boolean, default=False, comment='显示数据采集界面')
    
    # 自检类型字段 (1-10)
    self_check_type_1 = db.Column(db.String(100), comment='自检1')
    self_check_type_2 = db.Column(db.String(100), comment='自检2')
    self_check_type_3 = db.Column(db.String(100), comment='自检3')
    self_check_type_4 = db.Column(db.String(100), comment='自检4')
    self_check_type_5 = db.Column(db.String(100), comment='自检5')
    self_check_type_6 = db.Column(db.String(100), comment='自检6')
    self_check_type_7 = db.Column(db.String(100), comment='自检7')
    self_check_type_8 = db.Column(db.String(100), comment='自检8')
    self_check_type_9 = db.Column(db.String(100), comment='自检9')
    self_check_type_10 = db.Column(db.String(100), comment='自检10')
    
    # 工艺预料字段 (1-10)
    process_material_1 = db.Column(db.String(100), comment='工艺1')
    process_material_2 = db.Column(db.String(100), comment='工艺2')
    process_material_3 = db.Column(db.String(100), comment='工艺3')
    process_material_4 = db.Column(db.String(100), comment='工艺4')
    process_material_5 = db.Column(db.String(100), comment='工艺5')
    process_material_6 = db.Column(db.String(100), comment='工艺6')
    process_material_7 = db.Column(db.String(100), comment='工艺7')
    process_material_8 = db.Column(db.String(100), comment='工艺8')
    process_material_9 = db.Column(db.String(100), comment='工艺9')
    process_material_10 = db.Column(db.String(100), comment='工艺10')
    
    # 预留弹出框字段
    reserved_popup_1 = db.Column(db.String(100), comment='弹出1')
    reserved_popup_2 = db.Column(db.String(100), comment='弹出2')
    reserved_popup_3 = db.Column(db.String(100), comment='弹出3')
    reserved_dropdown_1 = db.Column(db.String(100), comment='下拉1')
    reserved_dropdown_2 = db.Column(db.String(100), comment='下拉2')
    reserved_dropdown_3 = db.Column(db.String(100), comment='下拉3')
    
    # 数字字段
    number_1 = db.Column(db.Numeric(15, 4), comment='数字1')
    number_2 = db.Column(db.Numeric(15, 4), comment='数字2')
    number_3 = db.Column(db.Numeric(15, 4), comment='数字3')
    number_4 = db.Column(db.Numeric(15, 4), comment='数字4')
    
    # 基础配置字段
    report_quantity = db.Column(db.Boolean, default=False, comment='上报数量')
    report_personnel = db.Column(db.Boolean, default=False, comment='上报人员')
    report_data = db.Column(db.Boolean, default=False, comment='上报数据')
    report_kg = db.Column(db.Boolean, default=False, comment='上报KG')
    report_number = db.Column(db.Boolean, default=False, comment='报号')
    report_time = db.Column(db.Boolean, default=False, comment='上报时间')
    down_report_time = db.Column(db.Boolean, default=False, comment='下报时间')
    machine_speed = db.Column(db.Boolean, default=False, comment='机速')
    cutting_specs = db.Column(db.Boolean, default=False, comment='分切规格')
    aging_room = db.Column(db.Boolean, default=False, comment='熟化室')
    reserved_char_1 = db.Column(db.Boolean, default=False, comment='预留字符1')
    reserved_char_2 = db.Column(db.Boolean, default=False, comment='预留字符2')
    net_weight = db.Column(db.Boolean, default=False, comment='净重')
    production_task_display_order = db.Column(db.Boolean, default=False, comment='生产任务显示序号')
    
    # 装箱配置字段
    packing_bags_count = db.Column(db.Boolean, default=False, comment='装箱袋数')
    pallet_barcode = db.Column(db.Boolean, default=False, comment='托盘条码')
    pallet_bag_loading = db.Column(db.Boolean, default=False, comment='托盘装袋数')
    box_loading_count = db.Column(db.Boolean, default=False, comment='入托箱数')
    seed_bag_count = db.Column(db.Boolean, default=False, comment='种袋数')
    defect_bag_count = db.Column(db.Boolean, default=False, comment='除袋数')
    report_staff = db.Column(db.Boolean, default=False, comment='上报人员')
    shortage_count = db.Column(db.Boolean, default=False, comment='缺数')
    material_specs = db.Column(db.Boolean, default=False, comment='材料规格')
    color_mixing_count = db.Column(db.Boolean, default=False, comment='合色数')
    batch_bags = db.Column(db.Boolean, default=False, comment='批袋')
    production_date = db.Column(db.Boolean, default=False, comment='生产日期')
    compound = db.Column(db.Boolean, default=False, comment='复合')
    process_machine_allocation = db.Column(db.Boolean, default=False, comment='工艺分机台')
    
    # 持续率配置字段
    continuity_rate = db.Column(db.Boolean, default=False, comment='持续率')
    strip_head_change_count = db.Column(db.Boolean, default=False, comment='换条头数')
    plate_support_change_count = db.Column(db.Boolean, default=False, comment='换版支数')
    plate_change_count = db.Column(db.Boolean, default=False, comment='换版次数')
    lamination_change_count = db.Column(db.Boolean, default=False, comment='换贴合报')
    plate_making_multiple = db.Column(db.Boolean, default=False, comment='制版倍送')
    algorithm_time = db.Column(db.Boolean, default=False, comment='换算时间')
    timing = db.Column(db.Boolean, default=False, comment='计时')
    pallet_time = db.Column(db.Boolean, default=False, comment='托盘时间')
    glue_water_change_count = db.Column(db.Boolean, default=False, comment='换胶水数')
    glue_drip_bag_change = db.Column(db.Boolean, default=False, comment='换条胶袋')
    pallet_sub_bag_change = db.Column(db.Boolean, default=False, comment='换压报料')
    transfer_report_change = db.Column(db.Boolean, default=False, comment='换转报料')
    auto_print = db.Column(db.Boolean, default=False, comment='自动打印')
    
    # 过程管控字段
    process_rate = db.Column(db.Boolean, default=False, comment='过程率')
    color_set_change_count = db.Column(db.Boolean, default=False, comment='换套色数')
    mesh_format_change_count = db.Column(db.Boolean, default=False, comment='换网格数')
    overtime = db.Column(db.Boolean, default=False, comment='加班')
    team_date = db.Column(db.Boolean, default=False, comment='班组日期')
    sampling_time = db.Column(db.Boolean, default=False, comment='打样时间')
    start_reading = db.Column(db.Boolean, default=False, comment='开始读数')
    count_times = db.Column(db.Boolean, default=False, comment='计次')
    blade_count = db.Column(db.Boolean, default=False, comment='刀刃数')
    power_consumption = db.Column(db.Boolean, default=False, comment='用电量')
    maintenance_time = db.Column(db.Boolean, default=False, comment='维修时间')
    end_time = db.Column(db.Boolean, default=False, comment='结束时间')
    malfunction_material_collection = db.Column(db.Boolean, default=False, comment='故障次数领料')
    
    # 查询/机器相关
    is_query_machine = db.Column(db.Boolean, default=False, comment='是否询机')
    
    # MES系统集成字段
    mes_report_kg_manual = db.Column(db.Boolean, default=False, comment='MES上报kg取用里kg')
    mes_kg_auto_calculation = db.Column(db.Boolean, default=False, comment='MES上报kg自动接算')
    auto_weighing_once = db.Column(db.Boolean, default=False, comment='自动称重一次')
    mes_process_feedback_clear = db.Column(db.Boolean, default=False, comment='MES工艺反馈空工艺')
    mes_consumption_solvent_by_ton = db.Column(db.Boolean, default=False, comment='MES消耗溶剂用里按吨')
    
    # 生产控制字段
    single_report_open = db.Column(db.Boolean, default=False, comment='单报装打开')
    multi_condition_open = db.Column(db.Boolean, default=False, comment='多条件同时开工')
    mes_line_start_work_order = db.Column(db.Boolean, default=False, comment='MES线本单开工单')
    mes_material_kg_consumption = db.Column(db.Boolean, default=False, comment='MES上报材料kg用里消费kg')
    mes_report_not_less_than_kg = db.Column(db.Boolean, default=False, comment='MES上报数不能小于上报kg')
    mes_water_consumption_by_ton = db.Column(db.Boolean, default=False, comment='MES耗水用里按吨')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')

    # 定义选择项常量
    CATEGORY_TYPES = [
        ('laminating', '淋膜')
    ]
    
    DATA_COLLECTION_MODES = [
        ('auto_weighing_scanning', '自动称重扫码模式'),
        ('auto_meter_scanning', '自动取米扫码模式'),
        ('auto_scanning', '自动扫码模式'),
        ('auto_weighing', '自动称重模式'),
        ('weighing_only', '仅称重模式'),
        ('scanning_summary_weighing', '扫码汇总称重模式')
    ]
    
    __table_args__ = (
        db.CheckConstraint("category_type IN ('', 'laminating')", name='process_categories_type_check'),
        db.CheckConstraint("data_collection_mode IN ('', 'auto_weighing_scanning', 'auto_meter_scanning', 'auto_scanning', 'auto_weighing', 'weighing_only', 'scanning_summary_weighing')", name='process_categories_collection_mode_check'),
    )

    def to_dict(self, include_user_info=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'process_name': self.process_name,
            'category_type': self.category_type,
            'sort_order': self.sort_order,
            'data_collection_mode': self.data_collection_mode,
            'show_data_collection_interface': self.show_data_collection_interface,
            
            # 自检类型字段
            'self_check_type_1': self.self_check_type_1,
            'self_check_type_2': self.self_check_type_2,
            'self_check_type_3': self.self_check_type_3,
            'self_check_type_4': self.self_check_type_4,
            'self_check_type_5': self.self_check_type_5,
            'self_check_type_6': self.self_check_type_6,
            'self_check_type_7': self.self_check_type_7,
            'self_check_type_8': self.self_check_type_8,
            'self_check_type_9': self.self_check_type_9,
            'self_check_type_10': self.self_check_type_10,
            
            # 工艺预料字段
            'process_material_1': self.process_material_1,
            'process_material_2': self.process_material_2,
            'process_material_3': self.process_material_3,
            'process_material_4': self.process_material_4,
            'process_material_5': self.process_material_5,
            'process_material_6': self.process_material_6,
            'process_material_7': self.process_material_7,
            'process_material_8': self.process_material_8,
            'process_material_9': self.process_material_9,
            'process_material_10': self.process_material_10,
            
            # 预留字段
            'reserved_popup_1': self.reserved_popup_1,
            'reserved_popup_2': self.reserved_popup_2,
            'reserved_popup_3': self.reserved_popup_3,
            'reserved_dropdown_1': self.reserved_dropdown_1,
            'reserved_dropdown_2': self.reserved_dropdown_2,
            'reserved_dropdown_3': self.reserved_dropdown_3,
            
            # 数字字段
            'number_1': float(self.number_1) if self.number_1 else None,
            'number_2': float(self.number_2) if self.number_2 else None,
            'number_3': float(self.number_3) if self.number_3 else None,
            'number_4': float(self.number_4) if self.number_4 else None,
            
            # 基础配置字段
            'report_quantity': self.report_quantity,
            'report_personnel': self.report_personnel,
            'report_data': self.report_data,
            'report_kg': self.report_kg,
            'report_number': self.report_number,
            'report_time': self.report_time,
            'down_report_time': self.down_report_time,
            'machine_speed': self.machine_speed,
            'cutting_specs': self.cutting_specs,
            'aging_room': self.aging_room,
            'reserved_char_1': self.reserved_char_1,
            'reserved_char_2': self.reserved_char_2,
            'net_weight': self.net_weight,
            'production_task_display_order': self.production_task_display_order,
            
            # 装箱配置字段
            'packing_bags_count': self.packing_bags_count,
            'pallet_barcode': self.pallet_barcode,
            'pallet_bag_loading': self.pallet_bag_loading,
            'box_loading_count': self.box_loading_count,
            'seed_bag_count': self.seed_bag_count,
            'defect_bag_count': self.defect_bag_count,
            'report_staff': self.report_staff,
            'shortage_count': self.shortage_count,
            'material_specs': self.material_specs,
            'color_mixing_count': self.color_mixing_count,
            'batch_bags': self.batch_bags,
            'production_date': self.production_date,
            'compound': self.compound,
            'process_machine_allocation': self.process_machine_allocation,
            
            # 持续率配置字段
            'continuity_rate': self.continuity_rate,
            'strip_head_change_count': self.strip_head_change_count,
            'plate_support_change_count': self.plate_support_change_count,
            'plate_change_count': self.plate_change_count,
            'lamination_change_count': self.lamination_change_count,
            'plate_making_multiple': self.plate_making_multiple,
            'algorithm_time': self.algorithm_time,
            'timing': self.timing,
            'pallet_time': self.pallet_time,
            'glue_water_change_count': self.glue_water_change_count,
            'glue_drip_bag_change': self.glue_drip_bag_change,
            'pallet_sub_bag_change': self.pallet_sub_bag_change,
            'transfer_report_change': self.transfer_report_change,
            'auto_print': self.auto_print,
            
            # 过程管控字段
            'process_rate': self.process_rate,
            'color_set_change_count': self.color_set_change_count,
            'mesh_format_change_count': self.mesh_format_change_count,
            'overtime': self.overtime,
            'team_date': self.team_date,
            'sampling_time': self.sampling_time,
            'start_reading': self.start_reading,
            'count_times': self.count_times,
            'blade_count': self.blade_count,
            'power_consumption': self.power_consumption,
            'maintenance_time': self.maintenance_time,
            'end_time': self.end_time,
            'malfunction_material_collection': self.malfunction_material_collection,
            'is_query_machine': self.is_query_machine,
            
            # MES字段
            'mes_report_kg_manual': self.mes_report_kg_manual,
            'mes_kg_auto_calculation': self.mes_kg_auto_calculation,
            'auto_weighing_once': self.auto_weighing_once,
            'mes_process_feedback_clear': self.mes_process_feedback_clear,
            'mes_consumption_solvent_by_ton': self.mes_consumption_solvent_by_ton,
            'single_report_open': self.single_report_open,
            'multi_condition_open': self.multi_condition_open,
            'mes_line_start_work_order': self.mes_line_start_work_order,
            'mes_material_kg_consumption': self.mes_material_kg_consumption,
            'mes_report_not_less_than_kg': self.mes_report_not_less_than_kg,
            'mes_water_consumption_by_ton': self.mes_water_consumption_by_ton,
            
            # 通用字段
            'description': self.description,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            from app.models.user import User
            # 获取创建人信息
            created_by_user = None
            if self.created_by:
                created_by_user = User.query.get(self.created_by)
            
            # 获取修改人信息
            updated_by_user = None
            if self.updated_by:
                updated_by_user = User.query.get(self.updated_by)
            
            result.update({
                'created_by': str(self.created_by) if self.created_by else None,
                'updated_by': str(self.updated_by) if self.updated_by else None,
                'created_by_username': created_by_user.get_full_name() if created_by_user else None,
                'updated_by_username': updated_by_user.get_full_name() if updated_by_user else None,
            })
        
        return result

    @classmethod
    def get_enabled_list(cls):
        """获取启用的工序分类列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.process_name).all()
    
    @classmethod
    def get_category_type_options(cls):
        """获取类型选项"""
        return [{'value': value, 'label': label} for value, label in cls.CATEGORY_TYPES]
    
    @classmethod
    def get_data_collection_mode_options(cls):
        """获取数据自动采集模式选项"""
        return [{'value': value, 'label': label} for value, label in cls.DATA_COLLECTION_MODES]

    def __repr__(self):
        return f'<ProcessCategory {self.process_name}>'


class BagType(TenantModel):
    """袋型管理模型"""
    __tablename__ = 'bag_types'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    bag_type_name = db.Column(db.String(100), nullable=False, comment='袋型名称')
    spec_expression = db.Column(db.String(200), comment='规格表达式')
    production_unit_id = db.Column(UUID(as_uuid=True), db.ForeignKey('units.id'), comment='生产单位ID')
    sales_unit_id = db.Column(UUID(as_uuid=True), db.ForeignKey('units.id'), comment='销售单位ID')
    
    # 数值字段
    difficulty_coefficient = db.Column(db.Numeric(10, 2), default=0, comment='难易系数')
    bag_making_unit_price = db.Column(db.Numeric(10, 2), default=0, comment='制袋单价')
    
    # 布尔字段
    is_roll_film = db.Column(db.Boolean, default=False, comment='卷膜')
    is_custom_spec = db.Column(db.Boolean, default=False, comment='自定规格')
    is_strict_bag_type = db.Column(db.Boolean, default=True, comment='严格袋型')
    is_process_judgment = db.Column(db.Boolean, default=False, comment='工序判断')
    is_diaper = db.Column(db.Boolean, default=False, comment='是否纸尿裤')
    is_woven_bag = db.Column(db.Boolean, default=False, comment='是否编织袋')
    is_label = db.Column(db.Boolean, default=False, comment='是否标签')
    is_antenna = db.Column(db.Boolean, default=False, comment='是否天线')
    
    # 通用字段
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    description = db.Column(db.Text, comment='描述')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联关系
    production_unit = db.relationship('Unit', foreign_keys=[production_unit_id], backref='production_bag_types', lazy='select')
    sales_unit = db.relationship('Unit', foreign_keys=[sales_unit_id], backref='sales_bag_types', lazy='select')
    
    __table_args__ = (
        db.CheckConstraint(
            "difficulty_coefficient >= 0", 
            name='bag_types_difficulty_coefficient_check'
        ),
        db.CheckConstraint(
            "bag_making_unit_price >= 0", 
            name='bag_types_unit_price_check'
        ),
        db.UniqueConstraint('bag_type_name', name='uk_bag_types_name'),
    )
    
    def to_dict(self, include_user_info=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'bag_type_name': self.bag_type_name,
            'spec_expression': self.spec_expression,
            'production_unit_id': str(self.production_unit_id) if self.production_unit_id else None,
            'sales_unit_id': str(self.sales_unit_id) if self.sales_unit_id else None,
            'difficulty_coefficient': float(self.difficulty_coefficient) if self.difficulty_coefficient else 0,
            'bag_making_unit_price': float(self.bag_making_unit_price) if self.bag_making_unit_price else 0,
            'sort_order': self.sort_order,
            'is_roll_film': self.is_roll_film,
            'is_custom_spec': self.is_custom_spec,
            'is_strict_bag_type': self.is_strict_bag_type,
            'is_process_judgment': self.is_process_judgment,
            'is_diaper': self.is_diaper,
            'is_woven_bag': self.is_woven_bag,
            'is_label': self.is_label,
            'is_antenna': self.is_antenna,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # 添加单位名称
        if self.production_unit:
            data['production_unit_name'] = self.production_unit.unit_name
        if self.sales_unit:
            data['sales_unit_name'] = self.sales_unit.unit_name
        
        if include_user_info:
            from app.models.user import User
            if self.created_by:
                created_user = User.query.get(self.created_by)
                data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
            else:
                data['created_by_name'] = '系统'
                
            if self.updated_by:
                updated_user = User.query.get(self.updated_by)
                data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
            else:
                data['updated_by_name'] = ''
        
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的袋型列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.bag_type_name).all()
    
    def __repr__(self):
        return f'<BagType {self.bag_type_name}>'


class BagTypeStructure(TenantModel):
    """袋型结构模型"""
    __tablename__ = 'bag_type_structures'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联信息
    bag_type_id = db.Column(UUID(as_uuid=True), db.ForeignKey('bag_types.id'), nullable=False, comment='袋型ID')
    
    # 基本信息
    structure_name = db.Column(db.String(100), nullable=False, comment='结构名称')
    
    # 公式字段（引用public schema中的计算方案）
    structure_expression_id = db.Column(UUID(as_uuid=True), comment='结构表达式ID')
    expand_length_formula_id = db.Column(UUID(as_uuid=True), comment='展开长公式ID')
    expand_width_formula_id = db.Column(UUID(as_uuid=True), comment='展开宽公式ID')
    material_length_formula_id = db.Column(UUID(as_uuid=True), comment='用料长公式ID')
    material_width_formula_id = db.Column(UUID(as_uuid=True), comment='用料宽公式ID')
    single_piece_width_formula_id = db.Column(UUID(as_uuid=True), comment='单片宽公式ID')
    
    # 通用字段
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    image_url = db.Column(db.String(500), comment='图片地址')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联关系
    bag_type = db.relationship('BagType', backref='structures', lazy='select')
    
    __table_args__ = (
        db.Index('idx_bag_type_structures_bag_type_id', 'bag_type_id'),
        db.Index('idx_bag_type_structures_sort_order', 'sort_order'),
    )
    
    def to_dict(self, include_user_info=False, include_formulas=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'bag_type_id': str(self.bag_type_id),
            'structure_name': self.structure_name,
            'structure_expression_id': str(self.structure_expression_id) if self.structure_expression_id else None,
            'expand_length_formula_id': str(self.expand_length_formula_id) if self.expand_length_formula_id else None,
            'expand_width_formula_id': str(self.expand_width_formula_id) if self.expand_width_formula_id else None,
            'material_length_formula_id': str(self.material_length_formula_id) if self.material_length_formula_id else None,
            'material_width_formula_id': str(self.material_width_formula_id) if self.material_width_formula_id else None,
            'single_piece_width_formula_id': str(self.single_piece_width_formula_id) if self.single_piece_width_formula_id else None,
            'sort_order': self.sort_order,
            'image_url': self.image_url,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            from app.models.user import User
            if self.created_by:
                created_user = User.query.get(self.created_by)
                data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
            else:
                data['created_by_name'] = '系统'
                
            if self.updated_by:
                updated_user = User.query.get(self.updated_by)
                data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
            else:
                data['updated_by_name'] = ''
        
        if include_formulas:
            # 获取计算方案信息
            from app.models.basic_data import CalculationScheme
            formulas = {}
            
            if self.structure_expression_id:
                scheme = CalculationScheme.query.get(self.structure_expression_id)
                formulas['structure_expression'] = scheme.scheme_name if scheme else None
            
            if self.expand_length_formula_id:
                scheme = CalculationScheme.query.get(self.expand_length_formula_id)
                formulas['expand_length_formula'] = scheme.scheme_name if scheme else None
            
            if self.expand_width_formula_id:
                scheme = CalculationScheme.query.get(self.expand_width_formula_id)
                formulas['expand_width_formula'] = scheme.scheme_name if scheme else None
            
            if self.material_length_formula_id:
                scheme = CalculationScheme.query.get(self.material_length_formula_id)
                formulas['material_length_formula'] = scheme.scheme_name if scheme else None
            
            if self.material_width_formula_id:
                scheme = CalculationScheme.query.get(self.material_width_formula_id)
                formulas['material_width_formula'] = scheme.scheme_name if scheme else None
            
            if self.single_piece_width_formula_id:
                scheme = CalculationScheme.query.get(self.single_piece_width_formula_id)
                formulas['single_piece_width_formula'] = scheme.scheme_name if scheme else None
            
            data.update(formulas)
            
        return data
    
    def __repr__(self):
        return f'<BagTypeStructure {self.structure_name}>'


class BagRelatedFormula(TenantModel):
    """袋型相关公式模型"""
    __tablename__ = 'bag_related_formulas'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    bag_type_id = db.Column(UUID(as_uuid=True), db.ForeignKey('bag_types.id'), nullable=False, comment='袋型ID')
    
    # 公式字段（关联计算方案）
    meter_formula_id = db.Column(UUID(as_uuid=True), comment='米数公式ID')
    square_formula_id = db.Column(UUID(as_uuid=True), comment='平方公式ID')
    material_width_formula_id = db.Column(UUID(as_uuid=True), comment='料宽公式ID')
    per_piece_formula_id = db.Column(UUID(as_uuid=True), comment='元/个公式ID')
    
    # 尺寸维度（手工输入）
    dimension_description = db.Column(db.String(200), comment='尺寸维度')
    
    # 通用字段
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    description = db.Column(db.Text, comment='描述')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联关系
    bag_type = db.relationship('BagType', backref='related_formulas', lazy='select')
    
    __table_args__ = (
        db.Index('idx_bag_related_formulas_bag_type_id', 'bag_type_id'),
        db.Index('idx_bag_related_formulas_sort_order', 'sort_order'),
    )
    
    def to_dict(self, include_user_info=False, include_formulas=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'bag_type_id': str(self.bag_type_id),
            'meter_formula_id': str(self.meter_formula_id) if self.meter_formula_id else None,
            'square_formula_id': str(self.square_formula_id) if self.square_formula_id else None,
            'material_width_formula_id': str(self.material_width_formula_id) if self.material_width_formula_id else None,
            'per_piece_formula_id': str(self.per_piece_formula_id) if self.per_piece_formula_id else None,
            'dimension_description': self.dimension_description,
            'sort_order': self.sort_order,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            from app.models.user import User
            if self.created_by:
                created_user = User.query.get(self.created_by)
                data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
            else:
                data['created_by_name'] = '系统'
                
            if self.updated_by:
                updated_user = User.query.get(self.updated_by)
                data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
            else:
                data['updated_by_name'] = ''
        
        if include_formulas:
            # 获取袋型信息
            if self.bag_type:
                data['bag_type_name'] = self.bag_type.bag_type_name
            
            # 获取计算方案信息
            from app.models.basic_data import CalculationScheme
            
            if self.meter_formula_id:
                scheme = CalculationScheme.query.get(self.meter_formula_id)
                data['meter_formula'] = {
                    'id': str(scheme.id),
                    'name': scheme.scheme_name,
                    'formula': scheme.scheme_formula
                } if scheme else None
            
            if self.square_formula_id:
                scheme = CalculationScheme.query.get(self.square_formula_id)
                data['square_formula'] = {
                    'id': str(scheme.id),
                    'name': scheme.scheme_name,
                    'formula': scheme.scheme_formula
                } if scheme else None
            
            if self.material_width_formula_id:
                scheme = CalculationScheme.query.get(self.material_width_formula_id)
                data['material_width_formula'] = {
                    'id': str(scheme.id),
                    'name': scheme.scheme_name,
                    'formula': scheme.scheme_formula
                } if scheme else None
            
            if self.per_piece_formula_id:
                scheme = CalculationScheme.query.get(self.per_piece_formula_id)
                data['per_piece_formula'] = {
                    'id': str(scheme.id),
                    'name': scheme.scheme_name,
                    'formula': scheme.scheme_formula
                } if scheme else None
            
        return data
    
    def __repr__(self):
        return f'<BagRelatedFormula {self.bag_type.bag_type_name if self.bag_type else "N/A"}>'


class Process(TenantModel):
    """工序模型"""
    __tablename__ = 'processes'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    process_name = db.Column(db.String(100), nullable=False, comment='工序名称')
    process_category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('process_categories.id'), comment='工序分类')
    scheduling_method = db.Column(db.String(50), comment='排程方式')
    mes_condition_code = db.Column(db.String(100), comment='MES条码前缀')
    unit_id = db.Column(UUID(as_uuid=True), db.ForeignKey('units.id'), comment='单位')
    
    # 报产配置
    production_allowance = db.Column(db.Float, comment='报产允许差')
    return_allowance_kg = db.Column(db.Float, comment='下返废品允许kg')
    sort_order = db.Column(db.Integer, comment='排序')
    over_production_allowance = db.Column(db.Float, comment='超产允许差')
    self_check_allowance_kg = db.Column(db.Float, comment='自检废品允许kg')
    workshop_difference = db.Column(db.Float, comment='工序门幅偏差')
    max_upload_count = db.Column(db.Integer, comment='最大上报数')
    standard_weight_difference = db.Column(db.Float, comment='标准重量差异')
    workshop_worker_difference = db.Column(db.Float, comment='工序工人偏差')
    
    # MES系统配置
    mes_report_form_code = db.Column(db.String(100), comment='MES报表表号前缀')
    ignore_inspection = db.Column(db.Boolean, default=False, comment='不考核允许来料')
    unit_price = db.Column(db.Float, comment='考核单价')
    return_allowance_upper_kg = db.Column(db.Float, comment='上返废品允许kg')
    over_production_limit = db.Column(db.Float, comment='超产允许值')
    
    # 布尔配置字段 - MES相关
    mes_verify_quality = db.Column(db.Boolean, default=False, comment='MES首检合格开工')
    external_processing = db.Column(db.Boolean, default=False, comment='工序外发')
    mes_upload_defect_items = db.Column(db.Boolean, default=False, comment='MES上报废品手填')
    mes_scancode_shelf = db.Column(db.Boolean, default=False, comment='MES扫码上架')
    mes_verify_spec = db.Column(db.Boolean, default=False, comment='MES检验合格领用')
    mes_upload_kg_required = db.Column(db.Boolean, default=False, comment='MES上报数kg必填')
    
    # 生产相关布尔配置
    display_data_collection = db.Column(db.Boolean, default=False, comment='显示数据采集面板')
    free_inspection = db.Column(db.Boolean, default=False, comment='免检')
    process_with_machine = db.Column(db.Boolean, default=False, comment='生产排程多机台生产')
    semi_product_usage = db.Column(db.Boolean, default=False, comment='本工序半成品领用')
    material_usage_required = db.Column(db.Boolean, default=False, comment='辅材用量必填')
    
    # 报价相关公式（外键）
    pricing_formula_id = db.Column(UUID(as_uuid=True), db.ForeignKey('calculation_schemes.id'), comment='报价拟合公式')
    worker_formula_id = db.Column(UUID(as_uuid=True), db.ForeignKey('calculation_schemes.id'), comment='工单拟合公式')
    material_formula_id = db.Column(UUID(as_uuid=True), db.ForeignKey('calculation_schemes.id'), comment='工单材料公式')
    output_formula_id = db.Column(UUID(as_uuid=True), db.ForeignKey('calculation_schemes.id'), comment='产量上报拟合')
    time_formula_id = db.Column(UUID(as_uuid=True), db.ForeignKey('calculation_schemes.id'), comment='计件工时公式')
    energy_formula_id = db.Column(UUID(as_uuid=True), db.ForeignKey('calculation_schemes.id'), comment='计件产能公式')
    saving_formula_id = db.Column(UUID(as_uuid=True), db.ForeignKey('calculation_schemes.id'), comment='节约公式')
    labor_cost_formula_id = db.Column(UUID(as_uuid=True), db.ForeignKey('calculation_schemes.id'), comment='计件工资公式')
    pricing_order_formula_id = db.Column(UUID(as_uuid=True), db.ForeignKey('calculation_schemes.id'), comment='报价工序公式')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联工序分类
    process_category = db.relationship('ProcessCategory', foreign_keys=[process_category_id], lazy='joined')
    
    # 关联机台
    machines = db.relationship('ProcessMachine', back_populates='process', cascade='all, delete-orphan')

    # 关联单位
    unit = db.relationship('Unit',  foreign_keys=[unit_id], lazy='joined')
    
    # 选项常量
    SCHEDULING_METHODS = [
        ('investment_m', '投产m'),
        ('investment_kg', '投产kg'),
        ('production_piece', '投产(个)'),
        ('production_output', '产出m'),
        ('production_kg', '产出kg'),
        ('production_piece_out', '产出(个)'),
        ('production_set', '产出(套)'),
        ('production_sheet', '产出(张)')
    ]
    
    def to_dict(self, include_machines=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'process_name': self.process_name,
            'process_category_id': str(self.process_category_id) if self.process_category_id else None,
            'process_category_name': self.process_category.process_name if self.process_category else None,
            'scheduling_method': self.scheduling_method,
            'mes_condition_code': self.mes_condition_code,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit_name': self.unit.unit_name if self.unit else None,
            'production_allowance': float(self.production_allowance) if self.production_allowance is not None else None,
            'return_allowance_kg': float(self.return_allowance_kg) if self.return_allowance_kg is not None else None,
            'sort_order': self.sort_order,
            'over_production_allowance': float(self.over_production_allowance) if self.over_production_allowance is not None else None,
            'self_check_allowance_kg': float(self.self_check_allowance_kg) if self.self_check_allowance_kg is not None else None,
            'workshop_difference': float(self.workshop_difference) if self.workshop_difference is not None else None,
            'max_upload_count': self.max_upload_count,
            'standard_weight_difference': float(self.standard_weight_difference) if self.standard_weight_difference is not None else None,
            'workshop_worker_difference': float(self.workshop_worker_difference) if self.workshop_worker_difference is not None else None,
            'mes_report_form_code': self.mes_report_form_code,
            'ignore_inspection': self.ignore_inspection,
            'unit_price': float(self.unit_price) if self.unit_price is not None else None,
            'return_allowance_upper_kg': float(self.return_allowance_upper_kg) if self.return_allowance_upper_kg is not None else None,
            'over_production_limit': float(self.over_production_limit) if self.over_production_limit is not None else None,
            'mes_verify_quality': self.mes_verify_quality,
            'external_processing': self.external_processing,
            'mes_upload_defect_items': self.mes_upload_defect_items,
            'mes_scancode_shelf': self.mes_scancode_shelf,
            'mes_verify_spec': self.mes_verify_spec,
            'mes_upload_kg_required': self.mes_upload_kg_required,
            'display_data_collection': self.display_data_collection,
            'free_inspection': self.free_inspection,
            'process_with_machine': self.process_with_machine,
            'semi_product_usage': self.semi_product_usage,
            'material_usage_required': self.material_usage_required,
            'pricing_formula_id': str(self.pricing_formula_id) if self.pricing_formula_id else None,
            'worker_formula_id': str(self.worker_formula_id) if self.worker_formula_id else None,
            'material_formula_id': str(self.material_formula_id) if self.material_formula_id else None,
            'output_formula_id': str(self.output_formula_id) if self.output_formula_id else None,
            'time_formula_id': str(self.time_formula_id) if self.time_formula_id else None,
            'energy_formula_id': str(self.energy_formula_id) if self.energy_formula_id else None,
            'saving_formula_id': str(self.saving_formula_id) if self.saving_formula_id else None,
            'labor_cost_formula_id': str(self.labor_cost_formula_id) if self.labor_cost_formula_id else None,
            'pricing_order_formula_id': str(self.pricing_order_formula_id) if self.pricing_order_formula_id else None,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
        
        if include_machines:
            result['machines'] = [pm.to_dict() for pm in self.machines]
            
        return result
    
    @staticmethod
    def get_scheduling_method_options():
        """获取排程方式选项"""
        return [{'value': option[0], 'label': option[1]} for option in Process.SCHEDULING_METHODS]


class ProcessMachine(TenantModel):
    """工序机台关联模型"""
    __tablename__ = 'process_machines'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = db.Column(UUID(as_uuid=True), db.ForeignKey('processes.id'), nullable=False)
    machine_id = db.Column(UUID(as_uuid=True), db.ForeignKey('machines.id'), nullable=False)
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 关联
    process = db.relationship('Process', back_populates='machines')
    machine = db.relationship('Machine')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'process_id': str(self.process_id),
            'machine_id': str(self.machine_id),
            'machine_name': self.machine.machine_name if self.machine else None,
            'machine_code': self.machine.machine_code if self.machine else None,
            'sort_order': self.sort_order
        }


class TeamGroup(TenantModel):
    """班组管理模型"""
    __tablename__ = 'team_groups'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    team_code = db.Column(db.String(50), unique=True, nullable=False, comment='班组编号(自动生成)')
    team_name = db.Column(db.String(100), nullable=False, comment='班组名称')
    circulation_card_id = db.Column(db.String(50), comment='流转卡标识')
    
    # 工作标准时间（单位：小时）
    day_shift_hours = db.Column(db.Numeric(8, 2), comment='白班工作标准时间(H)')
    night_shift_hours = db.Column(db.Numeric(8, 2), comment='晚班工作标准时间(H)')
    rotating_shift_hours = db.Column(db.Numeric(8, 2), comment='倒班第一天工作标准时间(H)')
    
    # 通用字段
    description = db.Column(db.Text, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联关系
    team_members = db.relationship('TeamGroupMember', backref='team_group', lazy='dynamic', cascade='all, delete-orphan')
    team_machines = db.relationship('TeamGroupMachine', backref='team_group', lazy='dynamic', cascade='all, delete-orphan')
    team_processes = db.relationship('TeamGroupProcess', backref='team_group', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_team_groups_team_code', 'team_code'),
        db.Index('idx_team_groups_team_name', 'team_name'),
        {'comment': '班组管理表'}
    )
    
    def to_dict(self, include_details=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'team_code': self.team_code,
            'team_name': self.team_name,
            'circulation_card_id': self.circulation_card_id,
            'day_shift_hours': float(self.day_shift_hours) if self.day_shift_hours else None,
            'night_shift_hours': float(self.night_shift_hours) if self.night_shift_hours else None,
            'rotating_shift_hours': float(self.rotating_shift_hours) if self.rotating_shift_hours else None,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_details:
            result.update({
                'team_members': [member.to_dict() for member in self.team_members],
                'team_machines': [machine.to_dict() for machine in self.team_machines], 
                'team_processes': [process.to_dict() for process in self.team_processes]
            })
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的班组列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order.asc(), cls.team_name.asc()).all()
    
    @classmethod
    def generate_team_code(cls):
        """生成班组编号"""
        from sqlalchemy import func, text
        # 查询当前最大编号
        max_code = cls.query.with_entities(
            func.max(func.cast(func.substr(cls.team_code, 3), db.Integer))
        ).filter(
            func.length(cls.team_code) == 10,
            func.substr(cls.team_code, 1, 2) == 'TG'
        ).scalar()
        
        if max_code:
            new_number = max_code + 1
        else:
            new_number = 1
        
        return f"TG{new_number:08d}"
    
    def __repr__(self):
        return f'<TeamGroup {self.team_name}>'


class TeamGroupMember(TenantModel):
    """班组人员模型"""
    __tablename__ = 'team_group_members'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联信息
    team_group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('team_groups.id'), nullable=False, comment='班组ID')
    employee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('employees.id'), nullable=False, comment='员工ID')
    
    # 业务信息
    piece_rate_percentage = db.Column(db.Numeric(5, 2), default=0, comment='计件%')
    saving_bonus_percentage = db.Column(db.Numeric(5, 2), default=0, comment='节约奖%')
    remarks = db.Column(db.Text, comment='备注')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联关系
    employee = db.relationship('Employee', backref='team_memberships', lazy='select')
    
    __table_args__ = (
        db.UniqueConstraint('team_group_id', 'employee_id', name='uq_team_group_employee'),
        db.Index('idx_team_group_members_team_id', 'team_group_id'),
        db.Index('idx_team_group_members_employee_id', 'employee_id'),
        {'comment': '班组人员表'}
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'team_group_id': str(self.team_group_id),
            'employee_id': str(self.employee_id),
            'employee_name': self.employee.employee_name if self.employee else None,
            'employee_code': self.employee.employee_id if self.employee else None,
            'position_name': self.employee.position.position_name if self.employee and self.employee.position else None,
            'piece_rate_percentage': float(self.piece_rate_percentage) if self.piece_rate_percentage else 0,
            'saving_bonus_percentage': float(self.saving_bonus_percentage) if self.saving_bonus_percentage else 0,
            'remarks': self.remarks,
            'sort_order': self.sort_order,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<TeamGroupMember {self.employee.employee_name if self.employee else "Unknown"}>'


class TeamGroupMachine(TenantModel):
    """班组机台模型"""
    __tablename__ = 'team_group_machines'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联信息
    team_group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('team_groups.id'), nullable=False, comment='班组ID')
    machine_id = db.Column(UUID(as_uuid=True), db.ForeignKey('machines.id'), nullable=False, comment='机台ID')
    
    # 业务信息
    remarks = db.Column(db.Text, comment='备注')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联关系
    machine = db.relationship('Machine', backref='team_assignments', lazy='select')
    
    __table_args__ = (
        db.UniqueConstraint('team_group_id', 'machine_id', name='uq_team_group_machine'),
        db.Index('idx_team_group_machines_team_id', 'team_group_id'),
        db.Index('idx_team_group_machines_machine_id', 'machine_id'),
        {'comment': '班组机台表'}
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'team_group_id': str(self.team_group_id),
            'machine_id': str(self.machine_id),
            'machine_name': self.machine.machine_name if self.machine else None,
            'machine_code': self.machine.machine_code if self.machine else None,
            'remarks': self.remarks,
            'sort_order': self.sort_order,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<TeamGroupMachine {self.machine.machine_name if self.machine else "Unknown"}>'


class TeamGroupProcess(TenantModel):
    """班组工序分类模型"""
    __tablename__ = 'team_group_processes'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联信息
    team_group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('team_groups.id'), nullable=False, comment='班组ID')
    process_category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('process_categories.id'), nullable=False, comment='工序分类ID')
    
    # 业务信息
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联关系
    process_category = db.relationship('ProcessCategory', backref='team_assignments', lazy='select')
    
    __table_args__ = (
        db.UniqueConstraint('team_group_id', 'process_category_id', name='uq_team_group_process'),
        db.Index('idx_team_group_processes_team_id', 'team_group_id'),
        db.Index('idx_team_group_processes_process_id', 'process_category_id'),
        {'comment': '班组工序分类表'}
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'team_group_id': str(self.team_group_id),
            'process_category_id': str(self.process_category_id),
            'process_category_name': self.process_category.process_name if self.process_category else None,
            'sort_order': self.sort_order,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<TeamGroupProcess {self.process_category.process_name if self.process_category else "Unknown"}>'


class CustomerManagement(TenantModel):
    """客户管理模型 - 完整字段版本"""
    __tablename__ = 'customer_management'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息字段（根据用户表格）
    customer_code = db.Column(db.String(50), comment='客户编号')  # 自动生成
    customer_name = db.Column(db.String(255), nullable=False, comment='客户名称')  # 手工输入
    customer_category_id = db.Column(UUID(as_uuid=True), comment='客户分类ID')  # 选择
    tax_rate_id = db.Column(UUID(as_uuid=True), comment='税收ID')  # 选择
    tax_rate = db.Column(db.Numeric(5, 2), comment='税率%')  # 自动填入
    customer_abbreviation = db.Column(db.String(100), comment='客户简称')  # 手工输入
    customer_level = db.Column(db.String(10), comment='客户等级')  # 选择: 空/A/B
    parent_customer_id = db.Column(UUID(as_uuid=True), comment='上级客户ID')  # 选择
    region = db.Column(db.String(100), comment='区域')  # 选择省份
    package_method_id = db.Column(UUID(as_uuid=True), db.ForeignKey('package_methods.id'), comment='包装方式ID')  # 选择
    barcode_prefix = db.Column(db.String(50), comment='条码前缀')  # 手工输入
    business_type = db.Column(db.String(50), comment='经营业务类')  # 选择: 空/供应商/经销/代理/贸易/备案/物流配送
    enterprise_type = db.Column(db.String(50), comment='企业类型')  # 选择: 空/个人/个体工商户/有限责任公司
    company_address = db.Column(db.Text, comment='公司地址')  # 手工输入
    
    # 日期字段 - 商标书(起始日期&截止日期)
    trademark_start_date = db.Column(db.Date, comment='商标书(起始日期)')
    trademark_end_date = db.Column(db.Date, comment='商标书(截止日期)')
    # 条码证书(起始日期&截止日期)
    barcode_cert_start_date = db.Column(db.Date, comment='条码证书(起始日期)')
    barcode_cert_end_date = db.Column(db.Date, comment='条码证书(截止日期)')
    # 合同期限(起始日期&截止日期)
    contract_start_date = db.Column(db.Date, comment='合同期限(起始日期)')
    contract_end_date = db.Column(db.Date, comment='合同期限(截止日期)')
    # 营业期限(起始日期&截止日期)
    business_start_date = db.Column(db.Date, comment='营业期限(起始日期)')
    business_end_date = db.Column(db.Date, comment='营业期限(截止日期)')
    # 生产许可(起始日期&截止日期)
    production_permit_start_date = db.Column(db.Date, comment='生产许可(起始日期)')
    production_permit_end_date = db.Column(db.Date, comment='生产许可(截止日期)')
    # 检测报告(起始日期&截止日期)
    inspection_report_start_date = db.Column(db.Date, comment='检测报告(起始日期)')
    inspection_report_end_date = db.Column(db.Date, comment='检测报告(截止日期)')
    
    # 选择字段
    payment_method_id = db.Column(UUID(as_uuid=True), comment='付款方式ID')  # 选择
    currency_id = db.Column(UUID(as_uuid=True), db.ForeignKey('currencies.id'), comment='币别ID')  # 选择
    
    # 数字字段
    settlement_color_difference = db.Column(db.Numeric(10, 4), comment='定金比例%')  # 手工输入
    sales_commission = db.Column(db.Numeric(5, 2), comment='销售提成%')  # 手工输入
    credit_amount = db.Column(db.Numeric(15, 2), comment='信用额度')  # 手工输入
    registered_capital = db.Column(db.Numeric(15, 2), comment='注册资金')  # 手工输入
    accounts_period = db.Column(db.Integer, comment='账款期限')  # 手工输入
    account_period = db.Column(db.Integer, comment='账期')  # 手工输入
    
    # 业务员字段
    salesperson_id = db.Column(UUID(as_uuid=True), comment='业务员ID')  # 选择
    
    # 编码字段
    barcode_front_code = db.Column(db.String(50), comment='编码前缀')  # 手工输入
    barcode_back_code = db.Column(db.String(50), comment='编码后缀')  # 手工输入
    user_barcode = db.Column(db.String(100), comment='用友编码')  # 手工输入
    
    # 流水号相关
    invoice_water_number = db.Column(db.String(50), comment='当前流水号')  # 手工输入
    water_mark_position = db.Column(db.Numeric(10, 2), comment='流水与位数')  # 手工输入
    legal_person_certificate = db.Column(db.String(100), comment='法人身份证')  # 手工输入
    company_website = db.Column(db.String(255), comment='公司网址')  # 手工输入
    company_legal_person = db.Column(db.String(100), comment='公司法人')  # 手工输入
    
    # 地址字段
    province = db.Column(db.String(50), comment='省份')  # 选择
    city = db.Column(db.String(50), comment='市')  # 选择
    district = db.Column(db.String(50), comment='县/区')  # 选择
    organization_code = db.Column(db.String(100), comment='组织机构代码')  # 手工输入
    reconciliation_date = db.Column(db.Date, comment='对账日期')  # 选择
    foreign_currency = db.Column(db.String(10), comment='外币')  # 选择
    remarks = db.Column(db.Text, comment='备注')  # 手工输入
    
    # 布尔字段(勾选)
    trademark_certificate = db.Column(db.Boolean, default=False, comment='商标证书')
    print_authorization = db.Column(db.Boolean, default=False, comment='印刷委托书')
    inspection_report = db.Column(db.Boolean, default=False, comment='检验报告')
    free_samples = db.Column(db.Boolean, default=False, comment='免费样用')
    advance_payment_control = db.Column(db.Boolean, default=False, comment='放开管控')
    warehouse = db.Column(db.Boolean, default=False, comment='定置')
    old_customer = db.Column(db.Boolean, default=False, comment='旧客户')
    customer_archive_review = db.Column(db.Boolean, default=False, comment='客户简称重复')
    
    # 标准字段
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 关联关系 - 暂时简化避免初始化问题
    # customer_category = db.relationship('CustomerCategoryManagement', 
    #                                   primaryjoin='CustomerManagement.customer_category_id == CustomerCategoryManagement.id')
    # parent_customer = db.relationship('CustomerManagement', remote_side=[id],
    #                                 primaryjoin='CustomerManagement.parent_customer_id == CustomerManagement.id')
    # package_method = db.relationship('PackageMethod',
    #                                primaryjoin='CustomerManagement.package_method_id == PackageMethod.id')
    # tax_rate_rel = db.relationship('TaxRate',
    #                              primaryjoin='CustomerManagement.tax_rate_id == TaxRate.id')
    # payment_method = db.relationship('PaymentMethod',
    #                                primaryjoin='CustomerManagement.payment_method_id == PaymentMethod.id')
    # currency = db.relationship('Currency',
    #                          primaryjoin='CustomerManagement.currency_id == Currency.id')
    
    # 子表关联
    contacts = db.relationship('CustomerContact', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    delivery_addresses = db.relationship('CustomerDeliveryAddress', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    invoice_units = db.relationship('CustomerInvoiceUnit', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    payment_units = db.relationship('CustomerPaymentUnit', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    affiliated_companies = db.relationship('CustomerAffiliatedCompany', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    
    # 销售订单关联
    sales_orders = db.relationship('SalesOrder', back_populates='customer', lazy='dynamic')
    
    # 选项常量
    CUSTOMER_LEVELS = [
        ('A', 'A'),
        ('B', 'B')
    ]
    
    BUSINESS_TYPES = [
        ('supplier', '供应商'),
        ('dealer', '经销'),
        ('agent', '代理'),
        ('trade', '贸易'),
        ('record', '备案'),
        ('logistics', '物流配送')
    ]
    
    ENTERPRISE_TYPES = [
        ('state_owned', '国有企业'),
        ('private', '民营企业'),
        ('foreign', '外资企业'),
        ('joint_venture', '合资企业'),
        ('individual', '个体工商户')
    ]
    
    PROVINCES = [
        ('北京', '北京'),
        ('天津', '天津'),
        ('河北', '河北'),
        ('山西', '山西'),
        ('内蒙古', '内蒙古'),
        ('辽宁', '辽宁'),
        ('吉林', '吉林'),
        ('黑龙江', '黑龙江'),
        ('上海', '上海'),
        ('江苏', '江苏'),
        ('浙江', '浙江'),
        ('安徽', '安徽'),
        ('福建', '福建'),
        ('江西', '江西'),
        ('山东', '山东'),
        ('河南', '河南'),
        ('湖北', '湖北'),
        ('湖南', '湖南'),
        ('广东', '广东'),
        ('广西', '广西'),
        ('海南', '海南'),
        ('重庆', '重庆'),
        ('四川', '四川'),
        ('贵州', '贵州'),
        ('云南', '云南'),
        ('西藏', '西藏'),
        ('陕西', '陕西'),
        ('甘肃', '甘肃'),
        ('青海', '青海'),
        ('宁夏', '宁夏'),
        ('新疆', '新疆'),
        ('台湾', '台湾'),
        ('香港', '香港'),
        ('澳门', '澳门')
    ]
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self, include_details=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'customer_name': self.customer_name,
            'customer_category_id': str(self.customer_category_id) if self.customer_category_id else None,
            'customer_category_name': None,  # 暂时禁用关系查询
            'customer_code': self.customer_code,
            'customer_abbreviation': self.customer_abbreviation,
            'customer_level': self.customer_level,
            'parent_customer_id': str(self.parent_customer_id) if self.parent_customer_id else None,
            'parent_customer_name': None,  # 暂时禁用关系查询
            'region': self.region,
            'package_method_id': str(self.package_method_id) if self.package_method_id else None,
            'package_method_name': None,  # 暂时禁用关系查询
            'barcode_prefix': self.barcode_prefix,
            'business_type': self.business_type,
            'enterprise_type': self.enterprise_type,
            'organization_code': self.organization_code,
            
            # 日期字段
            'trademark_start_date': self.trademark_start_date.isoformat() if self.trademark_start_date else None,
            'trademark_end_date': self.trademark_end_date.isoformat() if self.trademark_end_date else None,
            'barcode_cert_start_date': self.barcode_cert_start_date.isoformat() if self.barcode_cert_start_date else None,
            'barcode_cert_end_date': self.barcode_cert_end_date.isoformat() if self.barcode_cert_end_date else None,
            'contract_start_date': self.contract_start_date.isoformat() if self.contract_start_date else None,
            'contract_end_date': self.contract_end_date.isoformat() if self.contract_end_date else None,
            'business_start_date': self.business_start_date.isoformat() if self.business_start_date else None,
            'business_end_date': self.business_end_date.isoformat() if self.business_end_date else None,
            'production_permit_start_date': self.production_permit_start_date.isoformat() if self.production_permit_start_date else None,
            'production_permit_end_date': self.production_permit_end_date.isoformat() if self.production_permit_end_date else None,
            'inspection_report_start_date': self.inspection_report_start_date.isoformat() if self.inspection_report_start_date else None,
            'inspection_report_end_date': self.inspection_report_end_date.isoformat() if self.inspection_report_end_date else None,
            
            # 金额字段
            'registered_capital': float(self.registered_capital) if self.registered_capital else None,
            'accounts_period': float(self.accounts_period) if self.accounts_period else None,
            'account_period': float(self.account_period) if self.account_period else None,
            'tax_rate_id': str(self.tax_rate_id) if self.tax_rate_id else None,
            'tax_rate': float(self.tax_rate) if self.tax_rate else None,
            'credit_amount': float(self.credit_amount) if self.credit_amount else None,
            'sales_commission': float(self.sales_commission) if self.sales_commission else None,
            'settlement_color_difference': float(self.settlement_color_difference) if self.settlement_color_difference else None,
            
            # 业务相关字段
            'salesperson_id': str(self.salesperson_id) if self.salesperson_id else None,
            'company_website': self.company_website,
            'company_legal_person': self.company_legal_person,
            'company_address': self.company_address,
            'legal_person_certificate': self.legal_person_certificate,
            'barcode_front_code': self.barcode_front_code,
            'barcode_back_code': self.barcode_back_code,
            'user_barcode': self.user_barcode,
            'invoice_water_number': self.invoice_water_number,
            'water_mark_position': float(self.water_mark_position) if self.water_mark_position else None,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'reconciliation_date': self.reconciliation_date.isoformat() if self.reconciliation_date else None,
            'foreign_currency': self.foreign_currency,
            'remarks': self.remarks,
            
            # 布尔字段
            'trademark_certificate': self.trademark_certificate,
            'print_authorization': self.print_authorization,
            'inspection_report': self.inspection_report,
            'free_samples': self.free_samples,
            'advance_payment_control': self.advance_payment_control,
            'warehouse': self.warehouse,
            'old_customer': self.old_customer,
            'customer_archive_review': self.customer_archive_review,
            
            # 标准字段
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'region': self.region,
            'payment_method_id': str(self.payment_method_id) if self.payment_method_id else None,
            'currency_id': str(self.currency_id) if self.currency_id else None
        }
        
        code = self.enterprise_type
        data['enterprise_type_name'] = dict(self.ENTERPRISE_TYPES).get(code, code)
        if include_details:
            data.update({
                'contacts': [contact.to_dict() for contact in self.contacts],
                'delivery_addresses': [addr.to_dict() for addr in self.delivery_addresses],
                'invoice_units': [unit.to_dict() for unit in self.invoice_units],
                'payment_units': [unit.to_dict() for unit in self.payment_units],
                'affiliated_companies': [company.to_dict() for company in self.affiliated_companies]
            })
        
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的客户列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.customer_name).all()
    
    @classmethod
    def get_business_type_options(cls):
        """获取经营业务类型选项"""
        return [{'value': value, 'label': label} for value, label in cls.BUSINESS_TYPES]
    
    @classmethod
    def get_enterprise_type_options(cls):
        """获取企业类型选项"""
        return [{'value': value, 'label': label} for value, label in cls.ENTERPRISE_TYPES]
    
    def __repr__(self):
        return f'<CustomerManagement {self.customer_name}>'


class CustomerContact(TenantModel):
    """客户联系人子表"""
    __tablename__ = 'customer_management_contacts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customer_management.id'), nullable=False)
    contact_name = db.Column(db.String(100), comment='联系人')
    position = db.Column(db.String(100), comment='职位')
    mobile = db.Column(db.String(100), comment='手机')
    fax = db.Column(db.String(100), comment='传真')
    qq = db.Column(db.String(100), comment='QQ')
    wechat = db.Column(db.String(100), comment='微信')
    email = db.Column(db.String(255), comment='邮箱')
    department = db.Column(db.String(100), comment='部门')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'customer_id': str(self.customer_id),
            'contact_name': self.contact_name,
            'position': self.position,
            'mobile': self.mobile,
            'fax': self.fax,
            'qq': self.qq,
            'wechat': self.wechat,
            'email': self.email,
            'department': self.department,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CustomerDeliveryAddress(TenantModel):
    """送货地址子表"""
    __tablename__ = 'customer_management_delivery_addresses'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customer_management.id'), nullable=False)
    delivery_address = db.Column(db.Text, comment='送货地址')
    contact_name = db.Column(db.String(100), comment='联系人')
    contact_method = db.Column(db.String(150), comment='联系方式')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'customer_id': str(self.customer_id),
            'delivery_address': self.delivery_address,
            'contact_name': self.contact_name,
            'contact_method': self.contact_method,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CustomerInvoiceUnit(TenantModel):
    """开票单位子表"""
    __tablename__ = 'customer_management_invoice_units'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customer_management.id'), nullable=False)
    invoice_unit = db.Column(db.String(255), comment='开票单位')
    taxpayer_id = db.Column(db.String(100), comment='纳税人识别号')
    invoice_address = db.Column(db.String(255), comment='开票地址')
    invoice_phone = db.Column(db.String(100), comment='电话')
    invoice_bank = db.Column(db.String(255), comment='开票银行')
    invoice_account = db.Column(db.String(100), comment='开票账户')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'customer_id': str(self.customer_id),
            'invoice_unit': self.invoice_unit,
            'taxpayer_id': self.taxpayer_id,
            'invoice_address': self.invoice_address,
            'invoice_phone': self.invoice_phone,
            'invoice_bank': self.invoice_bank,
            'invoice_account': self.invoice_account,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CustomerPaymentUnit(TenantModel):
    """付款单位子表"""
    __tablename__ = 'customer_management_payment_units'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customer_management.id'), nullable=False)
    payment_unit = db.Column(db.String(255), comment='付款单位')
    unit_code = db.Column(db.String(100), comment='单位编号')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'customer_id': str(self.customer_id),
            'payment_unit': self.payment_unit,
            'unit_code': self.unit_code,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CustomerAffiliatedCompany(TenantModel):
    """归属公司子表"""
    __tablename__ = 'customer_management_affiliated_companies'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customer_management.id'), nullable=False)
    affiliated_company = db.Column(db.String(255), comment='归属公司')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'customer_id': str(self.customer_id),
            'affiliated_company': self.affiliated_company,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SupplierManagement(TenantModel):
    """供应商管理模型"""
    __tablename__ = 'supplier_management'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息字段
    supplier_code = db.Column(db.String(50), comment='供应商编号')  # 自动生成
    supplier_name = db.Column(db.String(255), nullable=False, comment='供应商名称')  # 手工输入
    supplier_abbreviation = db.Column(db.String(100), comment='供应商简称')  # 手工输入
    supplier_category_id = db.Column(UUID(as_uuid=True), comment='供应商分类ID')  # 选择
    purchaser_id = db.Column(UUID(as_uuid=True), comment='采购员ID')  # 选择，根据员工表选择
    is_disabled = db.Column(db.Boolean, default=False, comment='是否停用')  # bool
    region = db.Column(db.String(100), comment='区域')  # 选择省份
    delivery_method_id = db.Column(UUID(as_uuid=True), comment='送货方式ID')  # 选择
    tax_rate_id = db.Column(UUID(as_uuid=True), comment='税收ID')  # 选择
    tax_rate = db.Column(db.Numeric(5, 2), comment='税率%')  # 自动填入
    currency_id = db.Column(UUID(as_uuid=True), comment='币别ID')  # 选择，默认本位币
    payment_method_id = db.Column(UUID(as_uuid=True), comment='付款方式ID')  # 选择
    
    # 数字字段
    deposit_ratio = db.Column(db.Numeric(10, 4), default=0, comment='定金比例')  # 手工输入，默认0
    delivery_preparation_days = db.Column(db.Integer, default=0, comment='交期预备(天)')  # 手工输入，默认0
    copyright_square_price = db.Column(db.Numeric(15, 4), default=0, comment='版权平方价')  # 手工输入，默认0
    supplier_level = db.Column(db.String(10), comment='供应商等级')  # 选择: A/B
    
    # 编码和网址字段
    organization_code = db.Column(db.String(100), comment='组织机构代码')  # 手工输入
    company_website = db.Column(db.String(255), comment='公司网址')  # 手工输入
    foreign_currency_id = db.Column(UUID(as_uuid=True), comment='外币ID')  # 选择
    barcode_prefix_code = db.Column(db.String(50), comment='条码前缀码')  # 手工输入
    
    # 日期字段
    business_start_date = db.Column(db.Date, comment='营业期限(起始日期)')  # 日期型
    business_end_date = db.Column(db.Date, comment='营业期限(截止日期)')  # 日期型
    production_permit_start_date = db.Column(db.Date, comment='生产许可(起始日期)')  # 日期型
    production_permit_end_date = db.Column(db.Date, comment='生产许可(截止日期)')  # 日期型
    inspection_report_start_date = db.Column(db.Date, comment='检测报告(起始日期)')  # 日期型
    inspection_report_end_date = db.Column(db.Date, comment='检测报告(截止日期)')  # 日期型
    
    # 其他字段
    barcode_authorization = db.Column(db.Numeric(15, 4), default=0, comment='条码授权')  # 数字，手工输入，默认0
    ufriend_code = db.Column(db.String(100), comment='用友编码')  # 手工输入
    enterprise_type = db.Column(db.String(50), comment='企业类型')  # 选择: 空/个人/个体工商户/有限责任公司
    
    # 地址字段
    province = db.Column(db.String(50), comment='省份')  # 选择
    city = db.Column(db.String(50), comment='市')  # 选择
    district = db.Column(db.String(50), comment='县/区')  # 选择
    company_address = db.Column(db.Text, comment='公司地址')  # 手工输入
    remarks = db.Column(db.Text, comment='备注')  # 手工输入
    image_url = db.Column(db.String(500), comment='图片')  # 图片
    
    # 标准字段
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 子表关联 - 暂时简化避免初始化问题
    contacts = db.relationship('SupplierContact', backref='supplier', lazy='dynamic', cascade='all, delete-orphan')
    delivery_addresses = db.relationship('SupplierDeliveryAddress', backref='supplier', lazy='dynamic', cascade='all, delete-orphan')
    invoice_units = db.relationship('SupplierInvoiceUnit', backref='supplier', lazy='dynamic', cascade='all, delete-orphan')
    affiliated_companies = db.relationship('SupplierAffiliatedCompany', backref='supplier', lazy='dynamic', cascade='all, delete-orphan')
    
    # 选项常量
    SUPPLIER_LEVELS = [
        ('A', 'A'),
        ('B', 'B')
    ]
    
    ENTERPRISE_TYPES = [
        ('individual', '个人'),
        ('individual_business', '个体工商户'),
        ('limited_company', '有限责任公司')
    ]
    
    PROVINCES = [
        ('北京', '北京'),
        ('天津', '天津'),
        ('河北', '河北'),
        ('山西', '山西'),
        ('内蒙古', '内蒙古'),
        ('辽宁', '辽宁'),
        ('吉林', '吉林'),
        ('黑龙江', '黑龙江'),
        ('上海', '上海'),
        ('江苏', '江苏'),
        ('浙江', '浙江'),
        ('安徽', '安徽'),
        ('福建', '福建'),
        ('江西', '江西'),
        ('山东', '山东'),
        ('河南', '河南'),
        ('湖北', '湖北'),
        ('湖南', '湖南'),
        ('广东', '广东'),
        ('广西', '广西'),
        ('海南', '海南'),
        ('重庆', '重庆'),
        ('四川', '四川'),
        ('贵州', '贵州'),
        ('云南', '云南'),
        ('西藏', '西藏'),
        ('陕西', '陕西'),
        ('甘肃', '甘肃'),
        ('青海', '青海'),
        ('宁夏', '宁夏'),
        ('新疆', '新疆'),
        ('台湾', '台湾'),
        ('香港', '香港'),
        ('澳门', '澳门')
    ]
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self, include_details=False):
        """转换为字典"""
        data = {
            'id': str(self.id),
            'supplier_code': self.supplier_code,
            'supplier_name': self.supplier_name,
            'supplier_abbreviation': self.supplier_abbreviation,
            'supplier_category_id': str(self.supplier_category_id) if self.supplier_category_id else None,
            'purchaser_id': str(self.purchaser_id) if self.purchaser_id else None,
            'is_disabled': self.is_disabled,
            'region': self.region,
            'delivery_method_id': str(self.delivery_method_id) if self.delivery_method_id else None,
            'tax_rate_id': str(self.tax_rate_id) if self.tax_rate_id else None,
            'tax_rate': float(self.tax_rate) if self.tax_rate else None,
            'currency_id': str(self.currency_id) if self.currency_id else None,
            'payment_method_id': str(self.payment_method_id) if self.payment_method_id else None,
            'deposit_ratio': float(self.deposit_ratio) if self.deposit_ratio else None,
            'delivery_preparation_days': self.delivery_preparation_days,
            'copyright_square_price': float(self.copyright_square_price) if self.copyright_square_price else None,
            'supplier_level': self.supplier_level,
            'organization_code': self.organization_code,
            'company_website': self.company_website,
            'foreign_currency_id': str(self.foreign_currency_id) if self.foreign_currency_id else None,
            'barcode_prefix_code': self.barcode_prefix_code,
            'business_start_date': self.business_start_date.isoformat() if self.business_start_date else None,
            'business_end_date': self.business_end_date.isoformat() if self.business_end_date else None,
            'production_permit_start_date': self.production_permit_start_date.isoformat() if self.production_permit_start_date else None,
            'production_permit_end_date': self.production_permit_end_date.isoformat() if self.production_permit_end_date else None,
            'inspection_report_start_date': self.inspection_report_start_date.isoformat() if self.inspection_report_start_date else None,
            'inspection_report_end_date': self.inspection_report_end_date.isoformat() if self.inspection_report_end_date else None,
            'barcode_authorization': float(self.barcode_authorization) if self.barcode_authorization else None,
            'ufriend_code': self.ufriend_code,
            'enterprise_type': self.enterprise_type,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'company_address': self.company_address,
            'remarks': self.remarks,
            'image_url': self.image_url,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
        
        if include_details:
            data.update({
                'contacts': [contact.to_dict() for contact in self.contacts],
                'delivery_addresses': [addr.to_dict() for addr in self.delivery_addresses],
                'invoice_units': [unit.to_dict() for unit in self.invoice_units],
                'affiliated_companies': [company.to_dict() for company in self.affiliated_companies]
            })
        
        return data
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的供应商列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.supplier_name).all()
    
    @classmethod
    def get_supplier_level_options(cls):
        """获取供应商等级选项"""
        return [{'value': value, 'label': label} for value, label in cls.SUPPLIER_LEVELS]
    
    @classmethod
    def get_enterprise_type_options(cls):
        """获取企业类型选项"""
        return [{'value': value, 'label': label} for value, label in cls.ENTERPRISE_TYPES]
    
    def __repr__(self):
        return f'<SupplierManagement {self.supplier_name}>'


class SupplierContact(TenantModel):
    """供应商联系人子表"""
    __tablename__ = 'supplier_management_contacts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('supplier_management.id'), nullable=False)
    contact_name = db.Column(db.String(100), comment='联系人')
    landline = db.Column(db.String(100), comment='座机')
    mobile = db.Column(db.String(100), comment='手机')
    fax = db.Column(db.String(100), comment='传真')
    qq = db.Column(db.String(100), comment='QQ')
    wechat = db.Column(db.String(100), comment='微信')
    email = db.Column(db.String(255), comment='e-mail')
    department = db.Column(db.String(100), comment='部门')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'supplier_id': str(self.supplier_id),
            'contact_name': self.contact_name,
            'landline': self.landline,
            'mobile': self.mobile,
            'fax': self.fax,
            'qq': self.qq,
            'wechat': self.wechat,
            'email': self.email,
            'department': self.department,
            'sort_order': self.sort_order
        }


class SupplierDeliveryAddress(TenantModel):
    """供应商发货地址子表"""
    __tablename__ = 'supplier_management_delivery_addresses'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('supplier_management.id'), nullable=False)
    delivery_address = db.Column(db.Text, comment='发货地址')
    contact_name = db.Column(db.String(100), comment='联系人')
    contact_method = db.Column(db.String(150), comment='联系方式')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'supplier_id': str(self.supplier_id),
            'delivery_address': self.delivery_address,
            'contact_name': self.contact_name,
            'contact_method': self.contact_method,
            'sort_order': self.sort_order
        }


class SupplierInvoiceUnit(TenantModel):
    """供应商开票单位子表"""
    __tablename__ = 'supplier_management_invoice_units'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('supplier_management.id'), nullable=False)
    invoice_unit = db.Column(db.String(255), comment='开票单位')
    taxpayer_id = db.Column(db.String(100), comment='纳税人识别号')
    invoice_address = db.Column(db.String(255), comment='开票地址')
    invoice_phone = db.Column(db.String(100), comment='电话')
    invoice_bank = db.Column(db.String(255), comment='开票银行')
    invoice_account = db.Column(db.String(100), comment='开票账户')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'supplier_id': str(self.supplier_id),
            'invoice_unit': self.invoice_unit,
            'taxpayer_id': self.taxpayer_id,
            'invoice_address': self.invoice_address,
            'invoice_phone': self.invoice_phone,
            'invoice_bank': self.invoice_bank,
            'invoice_account': self.invoice_account,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SupplierAffiliatedCompany(TenantModel):
    """供应商归属公司子表"""
    __tablename__ = 'supplier_management_affiliated_companies'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('supplier_management.id'), nullable=False)
    affiliated_company = db.Column(db.String(255), comment='归属公司')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'supplier_id': str(self.supplier_id),
            'affiliated_company': self.affiliated_company,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Material(TenantModel):
    """材料模型"""
    __tablename__ = 'materials'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息字段
    material_code = db.Column(db.String(50), comment='材料编号')  # 自动生成，格式：MT00001349
    material_name = db.Column(db.String(255), nullable=False, comment='材料名称')  # 手工输入
    material_category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('material_categories.id'), comment='材料分类ID')  # 选择
    material_attribute = db.Column(db.String(50), comment='材料属性')  # 自动根据材料分类填入
    unit_id = db.Column(UUID(as_uuid=True), comment='单位ID')  # 自动根据材料分类填入
    auxiliary_unit_id = db.Column(UUID(as_uuid=True), comment='辅助单位ID')  # 自动根据材料分类填入
    
    # 布尔字段(勾选)
    is_blown_film = db.Column(db.Boolean, default=False, comment='是否吹膜')  # 勾选
    unit_no_conversion = db.Column(db.Boolean, default=False, comment='单位不换算')  # 勾选
    
    # 尺寸字段（自动根据材料分类填入）
    width_mm = db.Column(db.Numeric(10, 3), comment='宽mm')  # 自动
    thickness_um = db.Column(db.Numeric(10, 3), comment='厚μm')  # 自动
    specification_model = db.Column(db.String(200), comment='规格型号')  # 自动
    density = db.Column(db.Numeric(10, 4), comment='密度')  # 自动
    
    # 手工输入字段
    conversion_factor = db.Column(db.Numeric(10, 4), default=1, comment='换算系数')  # 手工输入，默认1
    sales_unit_id = db.Column(UUID(as_uuid=True), comment='销售单位ID')  # 选择
    inspection_type = db.Column(db.String(20), default='spot_check', comment='检验类型')  # 选择：免检/抽检/全检，默认抽检
    
    # 自动填入的布尔字段
    is_paper = db.Column(db.Boolean, default=False, comment='是否卷纸')  # 自动
    is_surface_printing_ink = db.Column(db.Boolean, default=False, comment='表印油墨')  # 自动
    length_mm = db.Column(db.Numeric(10, 3), comment='长mm')  # 自动
    height_mm = db.Column(db.Numeric(10, 3), comment='高mm')  # 自动
    
    # 库存管理字段
    min_stock_start = db.Column(db.Numeric(15, 3), comment='最小库存(起)')  # 手工输入
    min_stock_end = db.Column(db.Numeric(15, 3), comment='最小库存(止)')  # 手工输入
    max_stock = db.Column(db.Numeric(15, 3), comment='最大库存')  # 手工输入
    shelf_life_days = db.Column(db.Integer, comment='保质期/天')  # 自动
    warning_days = db.Column(db.Integer, default=0, comment='预警天数')  # 手工输入，默认0
    standard_m_per_roll = db.Column(db.Numeric(10, 3), default=0, comment='标准m/卷')  # 手工输入，默认0
    
    # 更多自动填入的布尔字段
    is_carton = db.Column(db.Boolean, default=False, comment='是否纸箱')  # 自动
    is_uv_ink = db.Column(db.Boolean, default=False, comment='UV油墨')  # 勾选
    wind_tolerance_mm = db.Column(db.Numeric(10, 3), default=0, comment='风差mm')  # 手工输入，默认0
    tongue_mm = db.Column(db.Numeric(10, 3), default=0, comment='舌头mm')  # 手工输入，默认0
    
    # 价格字段
    purchase_price = db.Column(db.Numeric(15, 4), default=0, comment='采购价')  # 手工输入，默认0
    latest_purchase_price = db.Column(db.Numeric(15, 4), default=0, comment='最近采购价')  # 手工输入，默认0
    latest_tax_included_price = db.Column(db.Numeric(15, 4), comment='最近含税单价')  # 手工输入
    
    # 选择字段
    material_formula_id = db.Column(UUID(as_uuid=True), comment='用料公式ID')  # 选择，根据计算方表选择方案分类为材料用料的项
    is_paper_core = db.Column(db.Boolean, default=False, comment='是否纸芯')  # 自动
    is_tube_film = db.Column(db.Boolean, default=False, comment='是否筒膜')  # 勾选
    
    # 损耗字段
    loss_1 = db.Column(db.Numeric(10, 4), comment='损耗1')  # 手工输入
    loss_2 = db.Column(db.Numeric(10, 4), comment='损耗2')  # 手工输入
    forward_formula = db.Column(db.String(200), comment='正算公式')  # 选择
    reverse_formula = db.Column(db.String(200), comment='反算公式')  # 选择
    sales_price = db.Column(db.Numeric(15, 4), comment='销售价')  # 手工输入
    subject_id = db.Column(UUID(as_uuid=True), comment='科目ID')  # 选择
    uf_code = db.Column(db.String(100), comment='用友编码')  # 手工输入
    
    # 更多布尔字段
    material_formula_reverse = db.Column(db.Boolean, default=False, comment='用料公式反算')  # 勾选
    is_hot_stamping = db.Column(db.Boolean, default=False, comment='是否烫金')  # 勾选
    material_position = db.Column(db.String(200), comment='材料位置')  # 手工输入
    carton_spec_volume = db.Column(db.Numeric(15, 6), comment='纸箱规格体积')  # 手工输入
    security_code = db.Column(db.String(100), comment='保密编码')  # 选择
    substitute_material_category_id = db.Column(UUID(as_uuid=True), comment='替代材料分类ID')  # 选择
    scan_batch = db.Column(db.String(100), comment='扫码批次')  # 手工输入
    
    # 最后的布尔字段
    is_woven_bag = db.Column(db.Boolean, default=False, comment='是否编织袋')  # 勾选
    is_zipper = db.Column(db.Boolean, default=False, comment='是否拉链')  # 自动
    remarks = db.Column(db.Text, comment='备注')  # 手工输入
    is_self_made = db.Column(db.Boolean, default=False, comment='是否自制')  # 勾选
    no_interface = db.Column(db.Boolean, default=False, comment='不对接')  # 勾选
    cost_object_required = db.Column(db.Boolean, default=False, comment='成本对象必填')  # 勾选
    
    # 标准字段
    sort_order = db.Column(db.Integer, default=0, comment='显示排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    
    # 子表关联
    properties = db.relationship('MaterialProperty', backref='material', lazy='dynamic', cascade='all, delete-orphan')
    suppliers = db.relationship('MaterialSupplier', backref='material', lazy='dynamic', cascade='all, delete-orphan')
    
    # 外键关联关系
    material_category = db.relationship('MaterialCategory', backref='materials', lazy='select')
    
    # 选项常量
    INSPECTION_TYPES = [
        ('exempt', '免检'),
        ('spot_check', '抽检'),
        ('full_check', '全检')
    ]
    
    __table_args__ = (
        db.Index('idx_material_management_code', 'material_code'),
        db.Index('idx_material_management_name', 'material_name'),
        db.Index('idx_material_management_category', 'material_category_id'),
        # TenantModel自动处理schema
    )
    
    def to_dict(self, include_details=False):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'material_code': self.material_code,
            'material_name': self.material_name,
            'material_category_id': str(self.material_category_id) if self.material_category_id else None,
            'material_attribute': self.material_attribute,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'auxiliary_unit_id': str(self.auxiliary_unit_id) if self.auxiliary_unit_id else None,
            'is_blown_film': self.is_blown_film,
            'unit_no_conversion': self.unit_no_conversion,
            'width_mm': float(self.width_mm) if self.width_mm else None,
            'thickness_um': float(self.thickness_um) if self.thickness_um else None,
            'specification_model': self.specification_model,
            'density': float(self.density) if self.density else None,
            'conversion_factor': float(self.conversion_factor) if self.conversion_factor else 1,
            'sales_unit_id': str(self.sales_unit_id) if self.sales_unit_id else None,
            'inspection_type': self.inspection_type,
            'is_paper': self.is_paper,
            'is_surface_printing_ink': self.is_surface_printing_ink,
            'length_mm': float(self.length_mm) if self.length_mm else None,
            'height_mm': float(self.height_mm) if self.height_mm else None,
            'min_stock_start': float(self.min_stock_start) if self.min_stock_start else None,
            'min_stock_end': float(self.min_stock_end) if self.min_stock_end else None,
            'max_stock': float(self.max_stock) if self.max_stock else None,
            'shelf_life_days': self.shelf_life_days,
            'warning_days': self.warning_days,
            'standard_m_per_roll': float(self.standard_m_per_roll) if self.standard_m_per_roll else 0,
            'is_carton': self.is_carton,
            'is_uv_ink': self.is_uv_ink,
            'wind_tolerance_mm': float(self.wind_tolerance_mm) if self.wind_tolerance_mm else 0,
            'tongue_mm': float(self.tongue_mm) if self.tongue_mm else 0,
            'purchase_price': float(self.purchase_price) if self.purchase_price else 0,
            'latest_purchase_price': float(self.latest_purchase_price) if self.latest_purchase_price else 0,
            'latest_tax_included_price': float(self.latest_tax_included_price) if self.latest_tax_included_price else None,
            'material_formula_id': str(self.material_formula_id) if self.material_formula_id else None,
            'is_paper_core': self.is_paper_core,
            'is_tube_film': self.is_tube_film,
            'loss_1': float(self.loss_1) if self.loss_1 else None,
            'loss_2': float(self.loss_2) if self.loss_2 else None,
            'forward_formula': self.forward_formula,
            'reverse_formula': self.reverse_formula,
            'sales_price': float(self.sales_price) if self.sales_price else None,
            'subject_id': str(self.subject_id) if self.subject_id else None,
            'uf_code': self.uf_code,
            'material_formula_reverse': self.material_formula_reverse,
            'is_hot_stamping': self.is_hot_stamping,
            'material_position': self.material_position,
            'carton_spec_volume': float(self.carton_spec_volume) if self.carton_spec_volume else None,
            'security_code': self.security_code,
            'substitute_material_category_id': str(self.substitute_material_category_id) if self.substitute_material_category_id else None,
            'scan_batch': self.scan_batch,
            'is_woven_bag': self.is_woven_bag,
            'is_zipper': self.is_zipper,
            'remarks': self.remarks,
            'is_self_made': self.is_self_made,
            'no_interface': self.no_interface,
            'cost_object_required': self.cost_object_required,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_details:
            result['properties'] = [prop.to_dict() for prop in self.properties]
            result['suppliers'] = [supplier.to_dict() for supplier in self.suppliers]
        
        return result
    
    @classmethod
    def get_enabled_list(cls):
        """获取启用的材料列表"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.sort_order, cls.material_name).all()
    
    @classmethod
    def generate_material_code(cls):
        """生成材料编号"""
        # 设置schema路径
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
        
        # 查询所有以MT开头的编号
        results = db.session.query(cls.material_code).filter(
            cls.material_code.like('MT%')
        ).all()
        
        max_number = 0
        if results:
            # 遍历所有编号，找到最大的数字
            for result in results:
                code = result[0]
                try:
                    # 提取数字部分
                    number_str = code[2:]  # 去掉MT前缀
                    number = int(number_str)
                    if number > max_number:
                        max_number = number
                except (ValueError, TypeError):
                    continue
        
        # 新编号 = 最大编号 + 1
        new_number = max_number + 1
        
        # 格式化为8位数字
        return f"MT{new_number:08d}"
    
    @classmethod
    def get_inspection_type_options(cls):
        """获取检验类型选项"""
        return [{'value': k, 'label': v} for k, v in cls.INSPECTION_TYPES]
    
    def __repr__(self):
        return f'<Material {self.material_name}>'


class MaterialProperty(TenantModel):
    """材料属性子表"""
    __tablename__ = 'material_properties'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id = db.Column(UUID(as_uuid=True), db.ForeignKey('materials.id'), nullable=False)
    property_name = db.Column(db.String(100), comment='属性名称')
    property_value = db.Column(db.String(255), comment='属性值')
    property_unit = db.Column(db.String(50), comment='属性单位')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'material_id': str(self.material_id),
            'property_name': self.property_name,
            'property_value': self.property_value,
            'property_unit': self.property_unit,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class MaterialSupplier(TenantModel):
    """材料供应商子表"""
    __tablename__ = 'material_suppliers'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id = db.Column(UUID(as_uuid=True), db.ForeignKey('materials.id'), nullable=False)
    supplier_id = db.Column(UUID(as_uuid=True), comment='供应商ID')
    supplier_material_code = db.Column(db.String(100), comment='供应商材料编码')
    supplier_price = db.Column(db.Numeric(15, 4), comment='供应商价格')
    is_primary = db.Column(db.Boolean, default=False, comment='是否主供应商')
    delivery_days = db.Column(db.Integer, comment='交货天数')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # TenantModel自动处理schema
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'material_id': str(self.material_id),
            'supplier_id': str(self.supplier_id) if self.supplier_id else None,
            'supplier_material_code': self.supplier_material_code,
            'supplier_price': float(self.supplier_price) if self.supplier_price else None,
            'is_primary': self.is_primary,
            'delivery_days': self.delivery_days,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Product(TenantModel):
    """产品档案模型"""
    __tablename__ = 'products'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_code = db.Column(db.String(50), unique=True, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_type = db.Column(db.String(20), default='finished')  # finished/semi/material
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('product_categories.id'))
    
    # 基本信息
    short_name = db.Column(db.String(100))
    english_name = db.Column(db.String(200))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    specification = db.Column(db.Text)
    
    # 产品管理界面新增字段
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customer_management.id'), comment='客户ID')
    bag_type_id = db.Column(UUID(as_uuid=True), db.ForeignKey('bag_types.id'), comment='袋型ID')
    salesperson_id = db.Column(UUID(as_uuid=True), comment='业务员ID')
    
    # 界面中的其他基础字段
    compound_quantity = db.Column(db.Integer, default=0, comment='复合量')
    small_inventory = db.Column(db.Integer, default=0, comment='最小库存')
    large_inventory = db.Column(db.Integer, default=0, comment='最大库存')
    international_standard = db.Column(db.String(100), comment='国际')
    domestic_standard = db.Column(db.String(100), comment='国内')
    
    # 布尔字段
    is_unlimited_quantity = db.Column(db.Boolean, default=False, comment='无限制数量')
    is_compound_needed = db.Column(db.Boolean, default=False, comment='需要复合')
    is_inspection_needed = db.Column(db.Boolean, default=False, comment='检验手续')
    is_public_product = db.Column(db.Boolean, default=False, comment='公共产品')
    is_packaging_needed = db.Column(db.Boolean, default=False, comment='包装')
    is_changing = db.Column(db.Boolean, default=False, comment='改版')
    
    # 材料字段
    material_info = db.Column(db.Text, comment='材料')
    
    # 数量字段
    compound_amount = db.Column(db.Integer, default=0, comment='复合量')
    sales_amount = db.Column(db.Integer, default=0, comment='销售量')
    contract_amount = db.Column(db.Integer, default=0, comment='合约量')
    inventory_amount = db.Column(db.Integer, default=0, comment='库存量')
    
    # 技术参数 (薄膜产品特有)
    thickness = db.Column(db.Numeric(8, 3))  # 厚度(μm)
    width = db.Column(db.Numeric(8, 2))  # 宽度(mm)
    length = db.Column(db.Numeric(10, 2))  # 长度(m)
    material_type = db.Column(db.String(100))  # 材料类型
    transparency = db.Column(db.Numeric(5, 2))  # 透明度(%)
    tensile_strength = db.Column(db.Numeric(8, 2))  # 拉伸强度(MPa)
    
    # 包装信息
    base_unit = db.Column(db.String(20), default='m²')  # 基本单位
    package_unit = db.Column(db.String(20))  # 包装单位
    conversion_rate = db.Column(db.Numeric(10, 4), default=1)  # 换算率
    net_weight = db.Column(db.Numeric(10, 3))  # 净重(kg)
    gross_weight = db.Column(db.Numeric(10, 3))  # 毛重(kg)
    
    # 价格信息
    standard_cost = db.Column(db.Numeric(15, 4))  # 标准成本
    standard_price = db.Column(db.Numeric(15, 4))  # 标准售价
    currency = db.Column(db.String(10), default='CNY')
    
    # 库存信息
    safety_stock = db.Column(db.Numeric(15, 3), default=0)  # 安全库存
    min_order_qty = db.Column(db.Numeric(15, 3), default=1)  # 最小订单量
    max_order_qty = db.Column(db.Numeric(15, 3))  # 最大订单量
    
    # 生产信息
    lead_time = db.Column(db.Integer, default=0)  # 生产周期(天)
    shelf_life = db.Column(db.Integer)  # 保质期(天)
    storage_condition = db.Column(db.String(200))  # 存储条件
    
    # 质量标准
    quality_standard = db.Column(db.String(200))  # 质量标准
    inspection_method = db.Column(db.String(200))  # 检验方法
    
    # 系统字段
    status = db.Column(db.String(20), default='active')
    is_sellable = db.Column(db.Boolean, default=True)  # 可销售
    is_purchasable = db.Column(db.Boolean, default=True)  # 可采购
    is_producible = db.Column(db.Boolean, default=True)  # 可生产
    
    # 租户模块配置支持
    custom_fields = db.Column(JSONB, default={})
    
    # 审计字段
    created_by = db.Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = db.Column(UUID(as_uuid=True), comment='修改人')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    category = db.relationship('ProductCategory', backref='products', lazy='select')
    customer = db.relationship('CustomerManagement', backref='products')
    bag_type = db.relationship('BagType', backref='products')
    
    __table_args__ = (
        db.CheckConstraint("status IN ('active', 'inactive', 'pending')", name='products_status_check'),
        db.CheckConstraint("product_type IN ('finished', 'semi', 'material')", name='products_type_check'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'product_code': self.product_code,
            'product_name': self.product_name,
            'product_type': self.product_type,
            'category': self.category.to_dict() if self.category else None,
            
            # 基本信息
            'short_name': self.short_name,
            'english_name': self.english_name,
            'brand': self.brand,
            'model': self.model,
            'specification': self.specification,
            
            # 产品管理界面新增字段
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'customer_name': self.customer.customer_name if self.customer else None,
            'bag_type_id': str(self.bag_type_id) if self.bag_type_id else None,
            'bag_type_name': self.bag_type.bag_type_name if self.bag_type else None,
            'salesperson_id': str(self.salesperson_id) if self.salesperson_id else None,
            'compound_quantity': self.compound_quantity,
            'small_inventory': self.small_inventory,
            'large_inventory': self.large_inventory,
            'international_standard': self.international_standard,
            'domestic_standard': self.domestic_standard,
            'is_unlimited_quantity': self.is_unlimited_quantity,
            'is_compound_needed': self.is_compound_needed,
            'is_inspection_needed': self.is_inspection_needed,
            'is_public_product': self.is_public_product,
            'is_packaging_needed': self.is_packaging_needed,
            'is_changing': self.is_changing,
            'material_info': self.material_info,
            'compound_amount': self.compound_amount,
            'sales_amount': self.sales_amount,
            'contract_amount': self.contract_amount,
            'inventory_amount': self.inventory_amount,
            
            # 技术参数
            'thickness': float(self.thickness) if self.thickness else None,
            'width': float(self.width) if self.width else None,
            'length': float(self.length) if self.length else None,
            'material_type': self.material_type,
            'transparency': float(self.transparency) if self.transparency else None,
            'tensile_strength': float(self.tensile_strength) if self.tensile_strength else None,
            
            # 包装信息
            'base_unit': self.base_unit,
            'package_unit': self.package_unit,
            'conversion_rate': float(self.conversion_rate) if self.conversion_rate else 1,
            'net_weight': float(self.net_weight) if self.net_weight else None,
            'gross_weight': float(self.gross_weight) if self.gross_weight else None,
            
            # 价格信息
            'standard_cost': float(self.standard_cost) if self.standard_cost else None,
            'standard_price': float(self.standard_price) if self.standard_price else None,
            'currency': self.currency,
            
            # 库存信息
            'safety_stock': float(self.safety_stock) if self.safety_stock else 0,
            'min_order_qty': float(self.min_order_qty) if self.min_order_qty else 1,
            'max_order_qty': float(self.max_order_qty) if self.max_order_qty else None,
            
            # 生产信息
            'lead_time': self.lead_time,
            'shelf_life': self.shelf_life,
            'storage_condition': self.storage_condition,
            
            # 质量标准
            'quality_standard': self.quality_standard,
            'inspection_method': self.inspection_method,
            
            # 系统字段
            'status': self.status,
            'is_sellable': self.is_sellable,
            'is_purchasable': self.is_purchasable,
            'is_producible': self.is_producible,
            
            # 自定义字段
            'custom_fields': self.custom_fields or {},
            
            # 审计字段
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# 在Product模型的末尾添加新的产品管理相关模型

class ProductStructure(TenantModel):
    """产品结构模型"""
    __tablename__ = 'product_structures'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False, comment='产品ID')
    
    # 产品结构字段 - 对应界面图片中的产品结构区域
    length = db.Column(db.Integer, default=0, comment='长度')
    width = db.Column(db.Integer, default=0, comment='宽度')
    height = db.Column(db.Integer, default=0, comment='高度')
    
    # 展开数据
    expand_length = db.Column(db.Integer, default=0, comment='展开长')
    expand_width = db.Column(db.Integer, default=0, comment='展开宽')
    expand_height = db.Column(db.Integer, default=0, comment='展开高')
    
    # 材料数据
    material_length = db.Column(db.Integer, default=0, comment='材料长')
    material_width = db.Column(db.Integer, default=0, comment='材料宽')
    material_height = db.Column(db.Integer, default=0, comment='材料高')
    
    # 单片数据
    single_length = db.Column(db.Integer, default=0, comment='单片长')
    single_width = db.Column(db.Integer, default=0, comment='单片宽')
    single_height = db.Column(db.Integer, default=0, comment='单片高')
    
    # 其他结构字段
    blue_color = db.Column(db.String(50), comment='蓝色')
    red_color = db.Column(db.String(50), comment='红色')
    other_color = db.Column(db.String(50), comment='其他颜色')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    product = db.relationship('Product', backref='product_structures')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'length': self.length,
            'width': self.width,
            'height': self.height,
            'expand_length': self.expand_length,
            'expand_width': self.expand_width,
            'expand_height': self.expand_height,
            'material_length': self.material_length,
            'material_width': self.material_width,
            'material_height': self.material_height,
            'single_length': self.single_length,
            'single_width': self.single_width,
            'single_height': self.single_height,
            'blue_color': self.blue_color,
            'red_color': self.red_color,
            'other_color': self.other_color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ProductCustomerRequirement(TenantModel):
    """产品客户需求模型"""
    __tablename__ = 'product_customer_requirements'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False, comment='产品ID')
    
    # 外观性能需求 - 对应界面图片中的外观性能需求区域
    appearance_requirements = db.Column(db.String(200), comment='外观需求')
    surface_treatment = db.Column(db.String(200), comment='表面处理')
    printing_requirements = db.Column(db.String(200), comment='印刷需求')
    color_requirements = db.Column(db.String(200), comment='颜色需求')
    pattern_requirements = db.Column(db.String(200), comment='图案需求')
    
    # 分切需求 - 对应界面图片中的分切需求区域
    cutting_method = db.Column(db.String(200), comment='分切方式')
    cutting_width = db.Column(db.Integer, default=0, comment='分切宽度')
    cutting_length = db.Column(db.Integer, default=0, comment='分切长度')
    cutting_thickness = db.Column(db.Integer, default=0, comment='分切厚度')
    optical_distance = db.Column(db.Integer, default=0, comment='光标距离')
    optical_width = db.Column(db.Integer, default=0, comment='光标宽度')
    
    # 制袋需求 - 对应界面图片中的制袋需求区域
    bag_sealing_up = db.Column(db.String(200), comment='封口上')
    bag_sealing_down = db.Column(db.String(200), comment='封口下')
    bag_sealing_left = db.Column(db.String(200), comment='封口左')
    bag_sealing_right = db.Column(db.String(200), comment='封口右')
    bag_sealing_middle = db.Column(db.String(200), comment='封口中')
    bag_sealing_inner = db.Column(db.String(200), comment='封口内')
    bag_length_tolerance = db.Column(db.String(200), comment='袋长公差')
    bag_width_tolerance = db.Column(db.String(200), comment='袋宽公差')
    
    # 包装需求 - 对应界面图片中的包装需求区域
    packaging_method = db.Column(db.String(200), comment='包装方式')
    packaging_requirements = db.Column(db.String(200), comment='包装需求')
    packaging_material = db.Column(db.String(200), comment='包装材料')
    packaging_quantity = db.Column(db.Integer, default=0, comment='包装数量')
    packaging_specifications = db.Column(db.String(200), comment='包装规格')
    
    # 理化需求 - 对应界面图片中的理化需求区域
    tensile_strength = db.Column(db.String(200), comment='拉伸强度')
    thermal_shrinkage = db.Column(db.String(200), comment='热缩率')
    impact_strength = db.Column(db.String(200), comment='冲击强度')
    thermal_tensile_strength = db.Column(db.String(200), comment='热拉伸强度')
    water_vapor_permeability = db.Column(db.String(200), comment='水蒸气透过率')
    heat_shrinkage_curve = db.Column(db.String(200), comment='热缩曲线')
    melt_index = db.Column(db.String(200), comment='熔指')
    gas_permeability = db.Column(db.String(200), comment='气体透过率')
    
    # 其他字段
    custom_1 = db.Column(db.String(200), comment='预留1')
    custom_2 = db.Column(db.String(200), comment='预留2')
    custom_3 = db.Column(db.String(200), comment='预留3')
    custom_4 = db.Column(db.String(200), comment='预留4')
    custom_5 = db.Column(db.String(200), comment='预留5')
    custom_6 = db.Column(db.String(200), comment='预留6')
    custom_7 = db.Column(db.String(200), comment='预留7')
    custom_8 = db.Column(db.String(200), comment='预留8')
    custom_9 = db.Column(db.String(200), comment='预留9')
    custom_10 = db.Column(db.String(200), comment='预留10')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    product = db.relationship('Product', backref='customer_requirements')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'appearance_requirements': self.appearance_requirements,
            'surface_treatment': self.surface_treatment,
            'printing_requirements': self.printing_requirements,
            'color_requirements': self.color_requirements,
            'pattern_requirements': self.pattern_requirements,
            'cutting_method': self.cutting_method,
            'cutting_width': self.cutting_width,
            'cutting_length': self.cutting_length,
            'cutting_thickness': self.cutting_thickness,
            'optical_distance': self.optical_distance,
            'optical_width': self.optical_width,
            'bag_sealing_up': self.bag_sealing_up,
            'bag_sealing_down': self.bag_sealing_down,
            'bag_sealing_left': self.bag_sealing_left,
            'bag_sealing_right': self.bag_sealing_right,
            'bag_sealing_middle': self.bag_sealing_middle,
            'bag_sealing_inner': self.bag_sealing_inner,
            'bag_length_tolerance': self.bag_length_tolerance,
            'bag_width_tolerance': self.bag_width_tolerance,
            'packaging_method': self.packaging_method,
            'packaging_requirements': self.packaging_requirements,
            'packaging_material': self.packaging_material,
            'packaging_quantity': self.packaging_quantity,
            'packaging_specifications': self.packaging_specifications,
            'tensile_strength': self.tensile_strength,
            'thermal_shrinkage': self.thermal_shrinkage,
            'impact_strength': self.impact_strength,
            'thermal_tensile_strength': self.thermal_tensile_strength,
            'water_vapor_permeability': self.water_vapor_permeability,
            'heat_shrinkage_curve': self.heat_shrinkage_curve,
            'melt_index': self.melt_index,
            'gas_permeability': self.gas_permeability,
            'custom_1': self.custom_1,
            'custom_2': self.custom_2,
            'custom_3': self.custom_3,
            'custom_4': self.custom_4,
            'custom_5': self.custom_5,
            'custom_6': self.custom_6,
            'custom_7': self.custom_7,
            'custom_8': self.custom_8,
            'custom_9': self.custom_9,
            'custom_10': self.custom_10,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ProductProcess(TenantModel):
    """产品工序关联模型"""
    __tablename__ = 'product_processes'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False, comment='产品ID')
    process_id = db.Column(UUID(as_uuid=True), db.ForeignKey('processes.id'), nullable=False, comment='工序ID')
    
    # 工序相关信息
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    is_required = db.Column(db.Boolean, default=True, comment='是否必需')
    duration_hours = db.Column(db.Float, comment='工时(小时)')
    cost_per_unit = db.Column(db.Numeric(10, 4), comment='单位成本')
    notes = db.Column(db.Text, comment='备注')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    product = db.relationship('Product', backref='product_processes')
    process = db.relationship('Process', backref='product_processes')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'process_id': str(self.process_id),
            'process_name': self.process.process_name if self.process else None,
            'process_category_name': self.process.process_category.process_name if self.process and self.process.process_category else None,
            'sort_order': self.sort_order,
            'is_required': self.is_required,
            'duration_hours': float(self.duration_hours) if self.duration_hours else None,
            'cost_per_unit': float(self.cost_per_unit) if self.cost_per_unit else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ProductMaterial(TenantModel):
    """产品材料关联模型"""
    __tablename__ = 'product_materials'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False, comment='产品ID')
    material_id = db.Column(UUID(as_uuid=True), db.ForeignKey('materials.id'), nullable=False, comment='材料ID')
    
    # 材料使用信息
    usage_quantity = db.Column(db.Numeric(10, 4), comment='用量')
    usage_unit = db.Column(db.String(20), comment='用量单位')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    is_main_material = db.Column(db.Boolean, default=False, comment='是否主材料')
    cost_per_unit = db.Column(db.Numeric(10, 4), comment='单位成本')
    supplier_id = db.Column(UUID(as_uuid=True), comment='供应商ID')
    notes = db.Column(db.Text, comment='备注')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    product = db.relationship('Product', backref='product_materials')
    material = db.relationship('Material', backref='product_materials')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'material_id': str(self.material_id),
            'material_name': self.material.material_name if self.material else None,
            'material_code': self.material.material_code if self.material else None,
            'material_category_name': self.material.material_category.material_name if self.material and self.material.material_category else None,
            'usage_quantity': float(self.usage_quantity) if self.usage_quantity else None,
            'usage_unit': self.usage_unit,
            'sort_order': self.sort_order,
            'is_main_material': self.is_main_material,
            'cost_per_unit': float(self.cost_per_unit) if self.cost_per_unit else None,
            'supplier_id': str(self.supplier_id) if self.supplier_id else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ProductQualityIndicator(TenantModel):
    """产品理化指标模型"""
    __tablename__ = 'product_quality_indicators'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False, comment='产品ID')
    
    # 理化指标 - 对应界面图片中的理化指标区域
    tensile_strength_longitudinal = db.Column(db.String(100), comment='拉伸强度纵向')
    tensile_strength_transverse = db.Column(db.String(100), comment='拉伸强度横向')
    thermal_shrinkage_longitudinal = db.Column(db.String(100), comment='热缩率纵向')
    thermal_shrinkage_transverse = db.Column(db.String(100), comment='热缩率横向')
    
    # 穿刺强度
    puncture_strength = db.Column(db.String(100), comment='穿刺强度')
    
    # 光学性能
    optical_properties = db.Column(db.String(100), comment='光学性能')
    
    # 热封温度
    heat_seal_temperature = db.Column(db.String(100), comment='热封温度')
    
    # 热封拉伸强度
    heat_seal_tensile_strength = db.Column(db.String(100), comment='热封拉伸强度')
    
    # 水蒸气透过率
    water_vapor_permeability = db.Column(db.String(100), comment='水蒸气透过率')
    
    # 氧气透过率
    oxygen_permeability = db.Column(db.String(100), comment='氧气透过率')
    
    # 磨擦系数
    friction_coefficient = db.Column(db.String(100), comment='磨擦系数')
    
    # 剥离强度
    peel_strength = db.Column(db.String(100), comment='剥离强度')
    
    # 检测标准
    test_standard = db.Column(db.String(200), comment='检测标准')
    
    # 检测依据
    test_basis = db.Column(db.String(200), comment='检测依据')
    
    # 预留指标字段
    indicator_1 = db.Column(db.String(100), comment='预留1')
    indicator_2 = db.Column(db.String(100), comment='预留2')
    indicator_3 = db.Column(db.String(100), comment='预留3')
    indicator_4 = db.Column(db.String(100), comment='预留4')
    indicator_5 = db.Column(db.String(100), comment='预留5')
    indicator_6 = db.Column(db.String(100), comment='预留6')
    indicator_7 = db.Column(db.String(100), comment='预留7')
    indicator_8 = db.Column(db.String(100), comment='预留8')
    indicator_9 = db.Column(db.String(100), comment='预留9')
    indicator_10 = db.Column(db.String(100), comment='预留10')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    product = db.relationship('Product', backref='quality_indicators')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'tensile_strength_longitudinal': self.tensile_strength_longitudinal,
            'tensile_strength_transverse': self.tensile_strength_transverse,
            'thermal_shrinkage_longitudinal': self.thermal_shrinkage_longitudinal,
            'thermal_shrinkage_transverse': self.thermal_shrinkage_transverse,
            'puncture_strength': self.puncture_strength,
            'optical_properties': self.optical_properties,
            'heat_seal_temperature': self.heat_seal_temperature,
            'heat_seal_tensile_strength': self.heat_seal_tensile_strength,
            'water_vapor_permeability': self.water_vapor_permeability,
            'oxygen_permeability': self.oxygen_permeability,
            'friction_coefficient': self.friction_coefficient,
            'peel_strength': self.peel_strength,
            'test_standard': self.test_standard,
            'test_basis': self.test_basis,
            'indicator_1': self.indicator_1,
            'indicator_2': self.indicator_2,
            'indicator_3': self.indicator_3,
            'indicator_4': self.indicator_4,
            'indicator_5': self.indicator_5,
            'indicator_6': self.indicator_6,
            'indicator_7': self.indicator_7,
            'indicator_8': self.indicator_8,
            'indicator_9': self.indicator_9,
            'indicator_10': self.indicator_10,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ProductImage(TenantModel):
    """产品图片模型"""
    __tablename__ = 'product_images'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False, comment='产品ID')
    
    # 图片信息
    image_name = db.Column(db.String(255), comment='图片名称')
    image_url = db.Column(db.String(500), comment='图片URL')
    image_type = db.Column(db.String(50), comment='图片类型')  # 图片1, 图片2, 图片3, 图片4
    file_size = db.Column(db.Integer, comment='文件大小(字节)')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    product = db.relationship('Product', backref='product_images')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'image_name': self.image_name,
            'image_url': self.image_url,
            'image_type': self.image_type,
            'file_size': self.file_size,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ===== 向后兼容别名 =====
# 为了保证现有代码继续工作，创建别名指向新的管理模型

# 客户相关别名
Customer = CustomerManagement
CustomerCategory = CustomerCategoryManagement

# 供应商相关别名  
Supplier = SupplierManagement
SupplierCategory = SupplierCategoryManagement