# -*- coding: utf-8 -*-
"""
基础档案管理数据模型
"""

from app.extensions import db
from app.models.base import BaseModel, TenantModel
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import text


class CustomerCategory(BaseModel):
    """客户分类模型"""
    __tablename__ = 'customer_categories'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_code = db.Column(db.String(50), unique=True, nullable=False)
    category_name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customer_categories.id'))
    level = db.Column(db.Integer, default=1)
    sort_order = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # 自引用关系
    children = db.relationship('CustomerCategory', 
                             backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'category_code': self.category_code,
            'category_name': self.category_name,
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'level': self.level,
            'sort_order': self.sort_order,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'children_count': self.children.count()
        }


class Customer(BaseModel):
    """客户档案模型"""
    __tablename__ = 'customers'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_code = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_type = db.Column(db.String(20), default='enterprise')  # enterprise/individual
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customer_categories.id'))
    
    # 基本信息
    legal_name = db.Column(db.String(200))
    unified_credit_code = db.Column(db.String(50))  # 统一社会信用代码
    tax_number = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    scale = db.Column(db.String(20))  # large/medium/small/micro
    
    # 联系信息
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(50))
    contact_email = db.Column(db.String(100))
    contact_address = db.Column(db.Text)
    postal_code = db.Column(db.String(20))
    
    # 业务信息
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    payment_terms = db.Column(db.Integer, default=30)  # 付款天数
    currency = db.Column(db.String(10), default='CNY')
    price_level = db.Column(db.String(20), default='standard')
    sales_person_id = db.Column(UUID(as_uuid=True))
    
    # 系统字段
    status = db.Column(db.String(20), default='active')  # active/inactive/pending
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(UUID(as_uuid=True))
    approved_at = db.Column(db.DateTime)
    
    # 租户模块配置支持
    custom_fields = db.Column(JSONB, default={})
    
    # 关联关系
    category = db.relationship('CustomerCategory', backref='customers', lazy='select')
    
    __table_args__ = (
        db.CheckConstraint("status IN ('active', 'inactive', 'pending')", name='customers_status_check'),
        db.CheckConstraint("customer_type IN ('enterprise', 'individual')", name='customers_type_check'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'customer_code': self.customer_code,
            'customer_name': self.customer_name,
            'customer_type': self.customer_type,
            'category': self.category.to_dict() if self.category else None,
            
            # 基本信息
            'legal_name': self.legal_name,
            'unified_credit_code': self.unified_credit_code,
            'tax_number': self.tax_number,
            'industry': self.industry,
            'scale': self.scale,
            
            # 联系信息
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'contact_address': self.contact_address,
            'postal_code': self.postal_code,
            
            # 业务信息
            'credit_limit': float(self.credit_limit) if self.credit_limit else 0,
            'payment_terms': self.payment_terms,
            'currency': self.currency,
            'price_level': self.price_level,
            'sales_person_id': str(self.sales_person_id) if self.sales_person_id else None,
            
            # 系统字段
            'status': self.status,
            'is_approved': self.is_approved,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            
            # 自定义字段
            'custom_fields': self.custom_fields or {},
            
            # 审计字段
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class SupplierCategory(BaseModel):
    """供应商分类模型"""
    __tablename__ = 'supplier_categories'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_code = db.Column(db.String(50), unique=True, nullable=False)
    category_name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(UUID(as_uuid=True), db.ForeignKey('supplier_categories.id'))
    level = db.Column(db.Integer, default=1)
    sort_order = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # 自引用关系
    children = db.relationship('SupplierCategory', 
                             backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'category_code': self.category_code,
            'category_name': self.category_name,
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'level': self.level,
            'sort_order': self.sort_order,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'children_count': self.children.count()
        }


class Supplier(BaseModel):
    """供应商档案模型"""
    __tablename__ = 'suppliers'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_code = db.Column(db.String(50), unique=True, nullable=False)
    supplier_name = db.Column(db.String(200), nullable=False)
    supplier_type = db.Column(db.String(20), default='material')  # material/service/both
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('supplier_categories.id'))
    
    # 基本信息
    legal_name = db.Column(db.String(200))
    unified_credit_code = db.Column(db.String(50))
    business_license = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    established_date = db.Column(db.Date)
    
    # 联系信息
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(50))
    contact_email = db.Column(db.String(100))
    office_address = db.Column(db.Text)
    factory_address = db.Column(db.Text)
    
    # 业务信息
    payment_terms = db.Column(db.Integer, default=30)
    currency = db.Column(db.String(10), default='CNY')
    quality_level = db.Column(db.String(20), default='qualified')  # excellent/good/qualified/poor
    cooperation_level = db.Column(db.String(20), default='ordinary')  # strategic/important/ordinary
    
    # 评估信息
    quality_score = db.Column(db.Numeric(3, 1), default=0)  # 0-10分
    delivery_score = db.Column(db.Numeric(3, 1), default=0)
    service_score = db.Column(db.Numeric(3, 1), default=0)
    price_score = db.Column(db.Numeric(3, 1), default=0)
    overall_score = db.Column(db.Numeric(3, 1), default=0)
    
    # 系统字段
    status = db.Column(db.String(20), default='active')
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(UUID(as_uuid=True))
    approved_at = db.Column(db.DateTime)
    
    # 租户模块配置支持
    custom_fields = db.Column(JSONB, default={})
    
    # 关联关系
    category = db.relationship('SupplierCategory', backref='suppliers', lazy='select')
    
    __table_args__ = (
        db.CheckConstraint("status IN ('active', 'inactive', 'pending')", name='suppliers_status_check'),
        db.CheckConstraint("supplier_type IN ('material', 'service', 'both')", name='suppliers_type_check'),
        db.CheckConstraint("quality_level IN ('excellent', 'good', 'qualified', 'poor')", name='suppliers_quality_check'),
        db.CheckConstraint("cooperation_level IN ('strategic', 'important', 'ordinary')", name='suppliers_cooperation_check'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'supplier_code': self.supplier_code,
            'supplier_name': self.supplier_name,
            'supplier_type': self.supplier_type,
            'category': self.category.to_dict() if self.category else None,
            
            # 基本信息
            'legal_name': self.legal_name,
            'unified_credit_code': self.unified_credit_code,
            'business_license': self.business_license,
            'industry': self.industry,
            'established_date': self.established_date.isoformat() if self.established_date else None,
            
            # 联系信息
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'office_address': self.office_address,
            'factory_address': self.factory_address,
            
            # 业务信息
            'payment_terms': self.payment_terms,
            'currency': self.currency,
            'quality_level': self.quality_level,
            'cooperation_level': self.cooperation_level,
            
            # 评估信息
            'quality_score': float(self.quality_score) if self.quality_score else 0,
            'delivery_score': float(self.delivery_score) if self.delivery_score else 0,
            'service_score': float(self.service_score) if self.service_score else 0,
            'price_score': float(self.price_score) if self.price_score else 0,
            'overall_score': float(self.overall_score) if self.overall_score else 0,
            
            # 系统字段
            'status': self.status,
            'is_approved': self.is_approved,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            
            # 自定义字段
            'custom_fields': self.custom_fields or {},
            
            # 审计字段
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


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


class Product(BaseModel):
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
    
    # 关联关系
    category = db.relationship('ProductCategory', backref='products', lazy='select')
    
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
        from sqlalchemy import func
        
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
    unit_price_formula = db.Column(db.String(200), comment='单价计算公式')
    
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
            'material_name': self.material_name,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'unit_price_formula': self.unit_price_formula,
            'sort_order': self.sort_order,
            'description': self.description,
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