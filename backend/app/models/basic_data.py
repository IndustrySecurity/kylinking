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


class ProductCategory(BaseModel):
    """产品分类模型"""
    __tablename__ = 'product_categories'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_code = db.Column(db.String(50), unique=True, nullable=False)
    category_name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(UUID(as_uuid=True), db.ForeignKey('product_categories.id'))
    level = db.Column(db.Integer, default=1)
    sort_order = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # 自引用关系
    children = db.relationship('ProductCategory', 
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