from sqlalchemy import Column, String, DateTime, Text, Numeric, Boolean, Integer, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import TenantModel, BaseModel
import uuid
from decimal import Decimal

# 延迟导入以避免循环导入问题
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.basic_data import Employee, Department, Unit


class Inventory(TenantModel):
    """
    库存表 - 记录每个仓库中每种产品/材料的当前库存数量
    """
    
    __tablename__ = 'inventories'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联字段
    warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='仓库ID')
    product_id = Column(UUID(as_uuid=True), comment='产品ID')
    material_id = Column(UUID(as_uuid=True), comment='材料ID')
    
    # 库存信息
    current_quantity = Column(Numeric(15, 3), default=0, nullable=False, comment='当前数量')
    available_quantity = Column(Numeric(15, 3), default=0, nullable=False, comment='可用数量')
    reserved_quantity = Column(Numeric(15, 3), default=0, nullable=False, comment='预留数量')
    in_transit_quantity = Column(Numeric(15, 3), default=0, nullable=False, comment='在途数量')
    
    # 单位信息
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='单位ID')
    
    # 成本信息
    unit_cost = Column(Numeric(15, 4), comment='单位成本')
    total_cost = Column(Numeric(18, 4), comment='总成本')
    
    # 批次信息
    batch_number = Column(String(100), comment='批次号')
    production_date = Column(DateTime, comment='生产日期')
    expiry_date = Column(DateTime, comment='到期日期')
    
    # 位置信息
    location_code = Column(String(100), comment='库位编码')
    storage_area = Column(String(100), comment='存储区域')
    
    # 库存状态
    inventory_status = Column(String(20), default='normal', comment='库存状态')  # normal/blocked/quarantine/damaged
    quality_status = Column(String(20), default='qualified', comment='质量状态')  # qualified/unqualified/pending
    
    # 安全库存设定
    safety_stock = Column(Numeric(15, 3), default=0, comment='安全库存')
    min_stock = Column(Numeric(15, 3), default=0, comment='最小库存')
    max_stock = Column(Numeric(15, 3), comment='最大库存')
    
    # 盘点信息
    last_count_date = Column(DateTime, comment='最后盘点日期')
    last_count_quantity = Column(Numeric(15, 3), comment='最后盘点数量')
    variance_quantity = Column(Numeric(15, 3), default=0, comment='差异数量')
    
    # 扩展字段
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 系统字段
    is_active = Column(Boolean, default=True, comment='是否有效')
    notes = Column(Text, comment='备注')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 库存状态常量
    INVENTORY_STATUS_CHOICES = [
        ('normal', '正常'),
        ('blocked', '冻结'),
        ('quarantine', '隔离'),
        ('damaged', '损坏')
    ]
    
    QUALITY_STATUS_CHOICES = [
        ('qualified', '合格'),
        ('unqualified', '不合格'),
        ('pending', '待检')
    ]
    
    # 关联关系
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')
    
    # 索引
    __table_args__ = (
        Index('ix_inventory_warehouse_product', 'warehouse_id', 'product_id'),
        Index('ix_inventory_warehouse_material', 'warehouse_id', 'material_id'),
        Index('ix_inventory_batch', 'batch_number'),
        Index('ix_inventory_location', 'warehouse_id', 'location_code'),
        Index('ix_inventory_status', 'inventory_status', 'quality_status'),
        Index('ix_inventory_unit', 'unit_id'),
    )
    
    def __init__(self, warehouse_id, unit_id, created_by, product_id=None, material_id=None, 
                 current_quantity=0, available_quantity=0, **kwargs):
        """
        初始化库存记录
        """
        self.warehouse_id = warehouse_id
        self.product_id = product_id
        self.material_id = material_id
        self.current_quantity = current_quantity
        self.available_quantity = available_quantity
        self.unit_id = unit_id
        self.created_by = created_by
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_quantity(self, quantity_change, transaction_type, updated_by):
        """
        更新库存数量
        """
        self.current_quantity += quantity_change
        if transaction_type not in ['reserve', 'unreserve']:
            self.available_quantity += quantity_change
        self.updated_by = updated_by
        self.updated_at = func.now()
    
    def reserve_quantity(self, quantity, updated_by):
        """
        预留库存
        """
        if self.available_quantity >= quantity:
            self.available_quantity -= quantity
            self.reserved_quantity += quantity
            self.updated_by = updated_by
            self.updated_at = func.now()
            return True
        return False
    
    def unreserve_quantity(self, quantity, updated_by):
        """
        取消预留
        """
        if self.reserved_quantity >= quantity:
            self.reserved_quantity -= quantity
            self.available_quantity += quantity
            self.updated_by = updated_by
            self.updated_at = func.now()
            return True
        return False
    
    def calculate_total_cost(self):
        """
        计算总成本
        """
        if self.unit_cost:
            # 确保两个值都是Decimal类型以避免类型错误
            unit_cost = Decimal(str(self.unit_cost)) if not isinstance(self.unit_cost, Decimal) else self.unit_cost
            current_quantity = Decimal(str(self.current_quantity)) if not isinstance(self.current_quantity, Decimal) else self.current_quantity
            self.total_cost = current_quantity * unit_cost
    
    def is_below_safety_stock(self):
        """
        检查是否低于安全库存
        """
        return self.current_quantity <= self.safety_stock
    
    def is_expired(self):
        """
        检查是否过期
        """
        if self.expiry_date:
            return self.expiry_date <= func.now()
        return False
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'warehouse_id': str(self.warehouse_id) if self.warehouse_id else None,
            'product_id': str(self.product_id) if self.product_id else None,
            'material_id': str(self.material_id) if self.material_id else None,
            'current_quantity': float(self.current_quantity) if self.current_quantity else 0,
            'available_quantity': float(self.available_quantity) if self.available_quantity else 0,
            'reserved_quantity': float(self.reserved_quantity) if self.reserved_quantity else 0,
            'in_transit_quantity': float(self.in_transit_quantity) if self.in_transit_quantity else 0,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit_name': self.unit.unit_name if self.unit else None,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'total_cost': float(self.total_cost) if self.total_cost else None,
            'batch_number': self.batch_number,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'location_code': self.location_code,
            'storage_area': self.storage_area,
            'inventory_status': self.inventory_status,
            'quality_status': self.quality_status,
            'safety_stock': float(self.safety_stock) if self.safety_stock else 0,
            'min_stock': float(self.min_stock) if self.min_stock else 0,
            'max_stock': float(self.max_stock) if self.max_stock else None,
            'last_count_date': self.last_count_date.isoformat() if self.last_count_date else None,
            'last_count_quantity': float(self.last_count_quantity) if self.last_count_quantity else None,
            'variance_quantity': float(self.variance_quantity) if self.variance_quantity else 0,
            'custom_fields': self.custom_fields,
            'is_active': self.is_active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        item_name = f"Product:{self.product_id}" if self.product_id else f"Material:{self.material_id}"
        return f'<Inventory {item_name} @Warehouse:{self.warehouse_id} Qty:{self.current_quantity}>'


class InventoryTransaction(TenantModel):
    """
    库存流水表 - 记录所有库存变动的详细记录
    """
    
    __tablename__ = 'inventory_transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联字段
    inventory_id = Column(UUID(as_uuid=True), nullable=False, comment='库存ID')
    warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='仓库ID')
    product_id = Column(UUID(as_uuid=True), comment='产品ID')
    material_id = Column(UUID(as_uuid=True), comment='材料ID')
    
    # 交易信息
    transaction_number = Column(String(100), unique=True, nullable=False, comment='流水号')
    transaction_type = Column(String(20), nullable=False, comment='交易类型')
    transaction_date = Column(DateTime, default=func.now(), nullable=False, comment='交易时间')
    
    # 数量变动
    quantity_change = Column(Numeric(15, 3), nullable=False, comment='数量变动')
    quantity_before = Column(Numeric(15, 3), nullable=False, comment='变动前数量')
    quantity_after = Column(Numeric(15, 3), nullable=False, comment='变动后数量')
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='单位ID')
    
    # 成本信息
    unit_price = Column(Numeric(15, 4), comment='单价')
    total_amount = Column(Numeric(18, 4), comment='总金额')
    
    # 业务关联
    source_document_type = Column(String(50), comment='源单据类型')  # purchase_order/sales_order/production_order/adjustment
    source_document_id = Column(UUID(as_uuid=True), comment='源单据ID')
    source_document_number = Column(String(100), comment='源单据号')
    
    # 批次和位置信息
    batch_number = Column(String(100), comment='批次号')
    from_location = Column(String(100), comment='来源库位')
    to_location = Column(String(100), comment='目标库位')
    
    # 业务伙伴信息
    customer_id = Column(UUID(as_uuid=True), comment='客户ID')
    supplier_id = Column(UUID(as_uuid=True), comment='供应商ID')
    
    # 审核信息
    approval_status = Column(String(20), default='pending', comment='审核状态')  # pending/approved/rejected
    approved_by = Column(UUID(as_uuid=True), comment='审核人')
    approved_at = Column(DateTime, comment='审核时间')
    
    # 扩展信息
    reason = Column(String(500), comment='变动原因')
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 系统字段
    is_cancelled = Column(Boolean, default=False, comment='是否已取消')
    cancelled_by = Column(UUID(as_uuid=True), comment='取消人')
    cancelled_at = Column(DateTime, comment='取消时间')
    cancel_reason = Column(String(500), comment='取消原因')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 交易类型常量
    TRANSACTION_TYPES = [
        ('in', '入库'),
        ('out', '出库'),
        ('transfer_in', '调拨入库'),
        ('transfer_out', '调拨出库'),
        ('adjustment_in', '盘盈'),
        ('adjustment_out', '盘亏'),
        ('production_in', '生产入库'),
        ('production_out', '生产出库'),
        ('purchase_in', '采购入库'),
        ('sales_out', '销售出库'),
        ('return_in', '退货入库'),
        ('return_out', '退货出库'),
        ('reserve', '预留'),
        ('unreserve', '取消预留'),
        ('scrap', '报废'),
        ('damage', '损坏'),
        ('count_adjust', '盘点调整')
    ]
    
    SOURCE_DOCUMENT_TYPES = [
        ('purchase_order', '采购订单'),
        ('sales_order', '销售订单'),
        ('production_order', '生产订单'),
        ('transfer_order', '调拨单'),
        ('adjustment_order', '调整单'),
        ('count_order', '盘点单'),
        ('scrap_order', '报废单'),
        ('return_order', '退货单'),
        ('manual', '手工录入')
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已审核'),
        ('rejected', '已拒绝')
    ]
    
    # 关联关系
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')
    
    # 索引
    __table_args__ = (
        Index('ix_inventory_transaction_inventory', 'inventory_id'),
        Index('ix_inventory_transaction_warehouse', 'warehouse_id'),
        Index('ix_inventory_transaction_type_date', 'transaction_type', 'transaction_date'),
        Index('ix_inventory_transaction_source', 'source_document_type', 'source_document_id'),
        Index('ix_inventory_transaction_number', 'transaction_number'),
        Index('ix_inventory_transaction_batch', 'batch_number'),
        Index('ix_inventory_transaction_status', 'approval_status', 'is_cancelled'),
        Index('ix_inventory_transaction_unit', 'unit_id'),
    )
    
    def __init__(self, inventory_id, warehouse_id, transaction_type, quantity_change, 
                 quantity_before, quantity_after, unit_id, created_by, **kwargs):
        """
        初始化库存交易记录
        """
        self.inventory_id = inventory_id
        self.warehouse_id = warehouse_id
        self.transaction_type = transaction_type
        self.quantity_change = quantity_change
        self.quantity_before = quantity_before
        self.quantity_after = quantity_after
        self.unit_id = unit_id
        self.created_by = created_by
        
        # 生成流水号
        if not kwargs.get('transaction_number'):
            self.transaction_number = self.generate_transaction_number()
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def generate_transaction_number():
        """
        生成流水号 - 按顺序生成
        """
        from datetime import datetime
        from sqlalchemy import func
        from app.extensions import db
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # 查询当天的最大序号
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取当天的最大序号 - 修复查询语法
        try:
            max_order = db.session.query(func.max(
                func.cast(func.substring(InventoryTransaction.transaction_number, -4), func.Integer)
            )).filter(
                InventoryTransaction.created_at >= today_start,
                InventoryTransaction.created_at <= today_end
            ).scalar()
        except Exception as e:
            # 如果查询失败，使用简单的计数方法
            count = db.session.query(InventoryTransaction).filter(
                InventoryTransaction.created_at >= today_start,
                InventoryTransaction.created_at <= today_end
            ).count()
            max_order = count
        
        # 序号从1开始，如果没有记录则为0，所以下一个序号为max_order + 1
        next_sequence = (max_order or 0) + 1
        
        # 格式化为4位数字，不足补0
        sequence_str = f"{next_sequence:04d}"
        
        return f"TXN{timestamp}{sequence_str}"
    
    def approve(self, approved_by):
        """
        审核通过
        """
        self.approval_status = 'approved'
        self.approved_by = approved_by
        self.approved_at = func.now()
    
    def reject(self, approved_by, reason=None):
        """
        审核拒绝
        """
        self.approval_status = 'rejected'
        self.approved_by = approved_by
        self.approved_at = func.now()
        if reason:
            self.notes = f"{self.notes or ''}\n拒绝原因: {reason}".strip()
    
    def cancel(self, cancelled_by, reason):
        """
        取消交易
        """
        self.is_cancelled = True
        self.cancelled_by = cancelled_by
        self.cancelled_at = func.now()
        self.cancel_reason = reason
    
    def calculate_total_amount(self):
        """
        计算总金额
        """
        if self.unit_price:
            # 确保两个值都是Decimal类型以避免类型错误
            unit_price = Decimal(str(self.unit_price)) if not isinstance(self.unit_price, Decimal) else self.unit_price
            quantity_change = Decimal(str(abs(self.quantity_change))) if not isinstance(self.quantity_change, Decimal) else abs(self.quantity_change)
            self.total_amount = quantity_change * unit_price
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'inventory_id': str(self.inventory_id),
            'warehouse_id': str(self.warehouse_id),
            'product_id': str(self.product_id) if self.product_id else None,
            'material_id': str(self.material_id) if self.material_id else None,
            'transaction_number': self.transaction_number,
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'quantity_change': float(self.quantity_change),
            'quantity_before': float(self.quantity_before),
            'quantity_after': float(self.quantity_after),
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit_name': self.unit.unit_name if self.unit else None,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'source_document_type': self.source_document_type,
            'source_document_id': str(self.source_document_id) if self.source_document_id else None,
            'source_document_number': self.source_document_number,
            'batch_number': self.batch_number,
            'from_location': self.from_location,
            'to_location': self.to_location,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'supplier_id': str(self.supplier_id) if self.supplier_id else None,
            'approval_status': self.approval_status,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'reason': self.reason,
            'notes': self.notes,
            'custom_fields': self.custom_fields,
            'is_cancelled': self.is_cancelled,
            'cancelled_by': str(self.cancelled_by) if self.cancelled_by else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancel_reason': self.cancel_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<InventoryTransaction {self.transaction_number} {self.transaction_type} {self.quantity_change}>'


class InventoryCountPlan(TenantModel):
    """
    盘点计划表
    """
    
    __tablename__ = 'inventory_count_plans'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 盘点基本信息
    plan_number = Column(String(100), unique=True, nullable=False, comment='盘点计划号')
    plan_name = Column(String(200), nullable=False, comment='盘点计划名称')
    count_type = Column(String(20), nullable=False, comment='盘点类型')  # full/partial/spot
    
    # 盘点范围
    warehouse_ids = Column(JSONB, comment='盘点仓库ID列表')
    product_categories = Column(JSONB, comment='产品分类')
    material_categories = Column(JSONB, comment='材料分类')
    location_codes = Column(JSONB, comment='库位编码列表')
    
    # 盘点时间
    plan_start_date = Column(DateTime, nullable=False, comment='计划开始时间')
    plan_end_date = Column(DateTime, nullable=False, comment='计划结束时间')
    actual_start_date = Column(DateTime, comment='实际开始时间')
    actual_end_date = Column(DateTime, comment='实际结束时间')
    
    # 盘点状态
    status = Column(String(20), default='draft', comment='状态')  # draft/confirmed/in_progress/completed/cancelled
    
    # 盘点人员
    count_team = Column(JSONB, comment='盘点小组')
    supervisor_id = Column(UUID(as_uuid=True), comment='监盘人ID')
    
    # 盘点说明
    description = Column(Text, comment='盘点说明')
    notes = Column(Text, comment='备注')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    count_records = relationship("InventoryCountRecord", back_populates="count_plan", cascade="all, delete-orphan")
    
    # 盘点类型常量
    COUNT_TYPES = [
        ('full', '全盘'),
        ('partial', '部分盘点'),
        ('spot', '抽盘'),
        ('cycle', '循环盘点')
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('in_progress', '盘点中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    
    def __init__(self, plan_name, count_type, plan_start_date, plan_end_date, created_by, **kwargs):
        """
        初始化盘点计划
        """
        self.plan_name = plan_name
        self.count_type = count_type
        self.plan_start_date = plan_start_date
        self.plan_end_date = plan_end_date
        self.created_by = created_by
        
        # 生成计划号
        if not kwargs.get('plan_number'):
            self.plan_number = self.generate_plan_number()
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def generate_plan_number():
        """
        生成盘点计划号 - 按顺序生成
        """
        from datetime import datetime
        from sqlalchemy import func
        from app.extensions import db
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 查询当天的最大序号
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取当天的最大序号 - 修复查询语法
        try:
            max_order = db.session.query(func.max(
                func.cast(func.substring(InventoryCountPlan.plan_number, -3), func.Integer)
            )).filter(
                InventoryCountPlan.created_at >= today_start,
                InventoryCountPlan.created_at <= today_end
            ).scalar()
        except Exception as e:
            # 如果查询失败，使用简单的计数方法
            count = db.session.query(InventoryCountPlan).filter(
                InventoryCountPlan.created_at >= today_start,
                InventoryCountPlan.created_at <= today_end
            ).count()
            max_order = count
        
        # 序号从1开始，如果没有记录则为0，所以下一个序号为max_order + 1
        next_sequence = (max_order or 0) + 1
        
        # 格式化为3位数字，不足补0
        sequence_str = f"{next_sequence:03d}"
        
        return f"CNT{timestamp}{sequence_str}"
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'plan_number': self.plan_number,
            'plan_name': self.plan_name,
            'count_type': self.count_type,
            'warehouse_ids': self.warehouse_ids,
            'product_categories': self.product_categories,
            'material_categories': self.material_categories,
            'location_codes': self.location_codes,
            'plan_start_date': self.plan_start_date.isoformat() if self.plan_start_date else None,
            'plan_end_date': self.plan_end_date.isoformat() if self.plan_end_date else None,
            'actual_start_date': self.actual_start_date.isoformat() if self.actual_start_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'status': self.status,
            'count_team': self.count_team,
            'supervisor_id': str(self.supervisor_id) if self.supervisor_id else None,
            'description': self.description,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<InventoryCountPlan {self.plan_number} {self.plan_name}>'


class InventoryCountRecord(TenantModel):
    """
    盘点记录表
    """
    
    __tablename__ = 'inventory_count_records'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联盘点计划
    count_plan_id = Column(UUID(as_uuid=True), ForeignKey('inventory_count_plans.id'), nullable=False, comment='盘点计划ID')
    
    # 关联库存
    inventory_id = Column(UUID(as_uuid=True), nullable=False, comment='库存ID')
    warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='仓库ID')
    product_id = Column(UUID(as_uuid=True), comment='产品ID')
    material_id = Column(UUID(as_uuid=True), comment='材料ID')
    
    # 盘点数据
    book_quantity = Column(Numeric(15, 3), nullable=False, comment='账面数量')
    actual_quantity = Column(Numeric(15, 3), comment='实盘数量')
    variance_quantity = Column(Numeric(15, 3), comment='差异数量')
    variance_rate = Column(Numeric(8, 4), comment='差异率%')
    
    # 盘点详情
    batch_number = Column(String(100), comment='批次号')
    location_code = Column(String(100), comment='库位编码')
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='单位ID')
    
    # 盘点人员和时间
    count_by = Column(UUID(as_uuid=True), comment='盘点人')
    count_date = Column(DateTime, comment='盘点时间')
    recount_by = Column(UUID(as_uuid=True), comment='复盘人')
    recount_date = Column(DateTime, comment='复盘时间')
    
    # 差异处理
    variance_reason = Column(String(500), comment='差异原因')
    is_adjusted = Column(Boolean, default=False, comment='是否已调整')
    adjustment_transaction_id = Column(UUID(as_uuid=True), comment='调整流水ID')
    
    # 状态
    status = Column(String(20), default='pending', comment='状态')  # pending/counted/recounted/adjusted
    
    # 备注
    notes = Column(Text, comment='备注')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    count_plan = relationship("InventoryCountPlan", back_populates="count_records")
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')
    
    # 状态常量
    STATUS_CHOICES = [
        ('pending', '待盘点'),
        ('counted', '已盘点'),
        ('recounted', '已复盘'),
        ('adjusted', '已调整')
    ]
    
    def __init__(self, count_plan_id, inventory_id, warehouse_id, book_quantity, unit_id, created_by, **kwargs):
        """
        初始化盘点记录
        """
        self.count_plan_id = count_plan_id
        self.inventory_id = inventory_id
        self.warehouse_id = warehouse_id
        self.book_quantity = book_quantity
        self.unit_id = unit_id
        self.created_by = created_by
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_variance(self):
        """
        计算差异
        """
        if self.actual_quantity is not None:
            self.variance_quantity = self.actual_quantity - self.book_quantity
            if self.book_quantity != 0:
                self.variance_rate = (self.variance_quantity / self.book_quantity) * 100
            else:
                self.variance_rate = 100 if self.actual_quantity > 0 else 0
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'count_plan_id': str(self.count_plan_id),
            'inventory_id': str(self.inventory_id),
            'warehouse_id': str(self.warehouse_id),
            'product_id': str(self.product_id) if self.product_id else None,
            'material_id': str(self.material_id) if self.material_id else None,
            'book_quantity': float(self.book_quantity),
            'actual_quantity': float(self.actual_quantity) if self.actual_quantity is not None else None,
            'variance_quantity': float(self.variance_quantity) if self.variance_quantity is not None else None,
            'variance_rate': float(self.variance_rate) if self.variance_rate is not None else None,
            'batch_number': self.batch_number,
            'location_code': self.location_code,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit_name': self.unit.unit_name if self.unit else None,
            'count_by': str(self.count_by) if self.count_by else None,
            'count_date': self.count_date.isoformat() if self.count_date else None,
            'recount_by': str(self.recount_by) if self.recount_by else None,
            'recount_date': self.recount_date.isoformat() if self.recount_date else None,
            'variance_reason': self.variance_reason,
            'is_adjusted': self.is_adjusted,
            'adjustment_transaction_id': str(self.adjustment_transaction_id) if self.adjustment_transaction_id else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<InventoryCountRecord Plan:{self.count_plan_id} Inventory:{self.inventory_id}>'


class InboundOrder(TenantModel):
    """
    入库单主表
    """
    
    __tablename__ = 'inbound_orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 单据信息
    order_number = Column(String(100), unique=True, nullable=False, comment='入库单号')
    order_date = Column(DateTime, default=func.now(), nullable=False, comment='发生日期')
    order_type = Column(String(20), default='finished_goods', comment='入库类型')  # finished_goods/raw_materials/semi_finished
    
    # 仓库信息
    warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='仓库ID')
    warehouse_name = Column(String(200), comment='仓库名称')
    
    # 入库人员信息 - 改为外键关联
    inbound_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), comment='入库人ID')
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), comment='部门ID')
    
    # 托盘信息
    pallet_barcode = Column(String(200), comment='托盘条码')
    pallet_count = Column(Integer, default=0, comment='托盘套数')
    
    # 单据状态
    status = Column(String(20), default='draft', comment='单据状态')  # draft/confirmed/in_progress/completed/cancelled
    is_outbound = Column(Boolean, default=False, comment='是否已出库')
    
    # 审核信息
    approval_status = Column(String(20), default='pending', comment='审核状态')  # pending/approved/rejected
    approved_by = Column(UUID(as_uuid=True), comment='审核人')
    approved_at = Column(DateTime, comment='审核时间')
    
    # 业务关联
    source_document_type = Column(String(50), comment='来源单据类型')  # production_order/purchase_order/transfer_order
    source_document_id = Column(UUID(as_uuid=True), comment='来源单据ID')
    source_document_number = Column(String(100), comment='来源单据号')
    
    # 客户供应商信息
    customer_id = Column(UUID(as_uuid=True), comment='客户ID')
    supplier_id = Column(UUID(as_uuid=True), comment='供应商ID')
    
    # 扩展字段
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    details = relationship("InboundOrderDetail", back_populates="inbound_order", cascade="all, delete-orphan")
    inbound_person = relationship("Employee", foreign_keys=[inbound_person_id], lazy='select')
    department = relationship("Department", foreign_keys=[department_id], lazy='select')
    
    # 入库类型常量
    ORDER_TYPES = [
        ('finished_goods', '成品入库'),
        ('raw_materials', '原材料入库'),
        ('semi_finished', '半成品入库'),
        ('other', '其他入库')
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('in_progress', '执行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已审核'),
        ('rejected', '已拒绝')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_inbound_order_number', 'order_number'),
        Index('ix_inbound_order_date', 'order_date'),
        Index('ix_inbound_order_warehouse', 'warehouse_id'),
        Index('ix_inbound_order_status', 'status', 'approval_status'),
        Index('ix_inbound_order_source', 'source_document_type', 'source_document_id'),
    )
    
    def __init__(self, warehouse_id, order_type, created_by, **kwargs):
        """
        初始化入库单
        """
        self.warehouse_id = warehouse_id
        self.order_type = order_type
        self.created_by = created_by
        
        # 生成入库单号
        if not kwargs.get('order_number'):
            self.order_number = self.generate_order_number(order_type)
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def generate_order_number(order_type='finished_goods'):
        """
        生成入库单号 - 按顺序生成
        """
        from datetime import datetime
        from sqlalchemy import func, text
        from app.extensions import db
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        prefix_map = {
            'finished_goods': 'FIN',
            'raw_materials': 'RAW',
            'semi_finished': 'SEM',
            'other': 'OTH'
        }
        prefix = prefix_map.get(order_type, 'INB')
        
        # 查询当天该类型的最大序号
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取当天该类型的最大序号
        # 获取当天的最大序号 - 修复查询语法
        try:
            max_order = db.session.query(func.max(
                func.cast(func.substring(InboundOrder.order_number, -4), func.Integer)
            )).filter(
                InboundOrder.order_type == order_type,
                InboundOrder.created_at >= today_start,
                InboundOrder.created_at <= today_end
            ).scalar()
        except Exception as e:
            # 如果查询失败，使用简单的计数方法
            count = db.session.query(InboundOrder).filter(
                InboundOrder.order_type == order_type,
                InboundOrder.created_at >= today_start,
                InboundOrder.created_at <= today_end
            ).count()
            max_order = count
        
        # 序号从1开始，如果没有记录则为0，所以下一个序号为max_order + 1
        next_sequence = (max_order or 0) + 1
        
        # 格式化为4位数字，不足补0
        sequence_str = f"{next_sequence:04d}"
        
        return f"{prefix}{timestamp}{sequence_str}"
    
    def calculate_totals(self):
        """
        计算汇总数据
        """
        if self.details:
            self.total_quantity = sum(detail.inbound_quantity for detail in self.details)
            self.total_kg_quantity = sum(detail.inbound_kg_quantity or 0 for detail in self.details)
            self.total_m_quantity = sum(detail.inbound_m_quantity or 0 for detail in self.details)
            self.total_roll_quantity = sum(detail.inbound_roll_quantity or 0 for detail in self.details)
            self.total_box_quantity = sum(detail.box_quantity or 0 for detail in self.details)
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'order_type': self.order_type,
            'warehouse_id': str(self.warehouse_id) if self.warehouse_id else None,
            'warehouse_name': self.warehouse_name,
            'inbound_person_id': str(self.inbound_person_id) if self.inbound_person_id else None,
            'inbound_person': self.inbound_person.employee_name if self.inbound_person else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'department': self.department.dept_name if self.department else None,
            'pallet_barcode': self.pallet_barcode,
            'pallet_count': self.pallet_count,
            'status': self.status,
            'is_outbound': self.is_outbound,
            'approval_status': self.approval_status,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'source_document_type': self.source_document_type,
            'source_document_id': str(self.source_document_id) if self.source_document_id else None,
            'source_document_number': self.source_document_number,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'supplier_id': str(self.supplier_id) if self.supplier_id else None,
            'notes': self.notes,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'details': [detail.to_dict() for detail in self.details] if self.details else []
        }
    
    def __repr__(self):
        return f'<InboundOrder {self.order_number} {self.order_type}>'


class InboundOrderDetail(TenantModel):
    """
    入库单明细表
    """
    
    __tablename__ = 'inbound_order_details'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联主表
    inbound_order_id = Column(UUID(as_uuid=True), ForeignKey('inbound_orders.id'), nullable=False, comment='入库单ID')
    
    # 产品信息
    product_id = Column(UUID(as_uuid=True), comment='产品ID')
    product_name = Column(String(200), comment='产品名称')
    product_code = Column(String(100), comment='产品编码')
    product_spec = Column(String(500), comment='产品规格')
    
    # 数量信息
    inbound_quantity = Column(Numeric(15, 3), nullable=False, default=0, comment='入库数')
    inbound_kg_quantity = Column(Numeric(15, 3), comment='入库kg数')
    inbound_m_quantity = Column(Numeric(15, 3), comment='入库m数')
    inbound_roll_quantity = Column(Numeric(15, 3), comment='入库卷数')
    box_quantity = Column(Numeric(15, 3), comment='装箱数')
    case_quantity = Column(Integer, comment='箱数')
    
    # 单位信息
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='基本单位ID')
    kg_unit = Column(String(20), default='kg', comment='重量单位')
    m_unit = Column(String(20), default='m', comment='长度单位')
    
    # 批次信息
    batch_number = Column(String(100), comment='批次号')
    production_date = Column(DateTime, comment='生产日期')
    expiry_date = Column(DateTime, comment='到期日期')
    
    # 质量信息
    quality_status = Column(String(20), default='qualified', comment='质量状态')  # qualified/unqualified/pending
    quality_certificate = Column(String(200), comment='质检证书')
    
    # 成本信息
    unit_cost = Column(Numeric(15, 4), comment='单位成本')
    total_cost = Column(Numeric(18, 4), comment='总成本')
    
    # 库位信息
    location_code = Column(String(100), comment='建议库位')
    actual_location_code = Column(String(100), comment='实际库位')
    
    # 包装信息
    package_quantity = Column(Numeric(15, 3), comment='包装数量')
    package_unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), comment='包装单位ID')
    
    # 行号和排序
    line_number = Column(Integer, comment='行号')
    sort_order = Column(Integer, default=0, comment='排序')
    
    # 扩展字段
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    inbound_order = relationship("InboundOrder", back_populates="details")
    package_unit = relationship("Unit", foreign_keys=[package_unit_id], lazy='select')
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')
    
    # 质量状态常量
    QUALITY_STATUS_CHOICES = [
        ('qualified', '合格'),
        ('unqualified', '不合格'),
        ('pending', '待检')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_inbound_detail_order', 'inbound_order_id'),
        Index('ix_inbound_detail_product', 'product_id'),
        Index('ix_inbound_detail_batch', 'batch_number'),
        Index('ix_inbound_detail_location', 'location_code'),
    )
    
    def __init__(self, inbound_order_id, inbound_quantity, unit_id, created_by, **kwargs):
        """
        初始化入库单明细
        """
        self.inbound_order_id = inbound_order_id
        self.inbound_quantity = inbound_quantity
        self.unit_id = unit_id
        self.created_by = created_by
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_total_cost(self):
        """
        计算总成本
        """
        if self.unit_cost and self.inbound_quantity:
            # 确保两个值都是Decimal类型以避免类型错误
            unit_cost = Decimal(str(self.unit_cost)) if not isinstance(self.unit_cost, Decimal) else self.unit_cost
            inbound_quantity = Decimal(str(self.inbound_quantity)) if not isinstance(self.inbound_quantity, Decimal) else self.inbound_quantity
            self.total_cost = unit_cost * inbound_quantity
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'inbound_order_id': str(self.inbound_order_id),
            'product_id': str(self.product_id) if self.product_id else None,
            'product_name': self.product_name,
            'product_code': self.product_code,
            'product_spec': self.product_spec,
            'inbound_quantity': float(self.inbound_quantity) if self.inbound_quantity else 0,
            'inbound_kg_quantity': float(self.inbound_kg_quantity) if self.inbound_kg_quantity is not None else None,
            'inbound_m_quantity': float(self.inbound_m_quantity) if self.inbound_m_quantity is not None else None,
            'inbound_roll_quantity': float(self.inbound_roll_quantity) if self.inbound_roll_quantity is not None else None,
            'box_quantity': float(self.box_quantity) if self.box_quantity else None,
            'case_quantity': self.case_quantity,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'kg_unit': self.kg_unit,
            'm_unit': self.m_unit,
            'batch_number': self.batch_number,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'quality_status': self.quality_status,
            'quality_certificate': self.quality_certificate,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'total_cost': float(self.total_cost) if self.total_cost else None,
            'location_code': self.location_code,
            'actual_location_code': self.actual_location_code,
            'package_quantity': float(self.package_quantity) if self.package_quantity else None,
            'package_unit_id': str(self.package_unit_id) if self.package_unit_id else None,
            'package_unit_name': self.package_unit.unit_name if self.package_unit else None,
            'line_number': self.line_number,
            'sort_order': self.sort_order,
            'notes': self.notes,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<InboundOrderDetail {self.product_name} Qty:{self.inbound_quantity}>'


class OutboundOrder(TenantModel):
    """
    出库单主表
    """
    
    __tablename__ = 'outbound_orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 单据信息
    order_number = Column(String(100), unique=True, nullable=False, comment='出库单号')
    order_date = Column(DateTime, default=func.now(), nullable=False, comment='发生日期')
    order_type = Column(String(20), default='finished_goods', comment='出库类型')  # finished_goods/raw_materials/semi_finished
    
    # 仓库信息
    warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='仓库ID')
    warehouse_name = Column(String(200), comment='仓库名称')
    
    # 出库人员信息 - 改为外键关联
    outbound_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), comment='出库人ID')
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), comment='部门ID')
    
    # 托盘信息
    pallet_barcode = Column(String(200), comment='托盘条码')
    pallet_count = Column(Integer, default=0, comment='托盘套数')
    
    # 单据状态
    status = Column(String(20), default='draft', comment='单据状态')  # draft/confirmed/in_progress/completed/cancelled
    
    # 审核信息
    approval_status = Column(String(20), default='pending', comment='审核状态')  # pending/approved/rejected
    approved_by = Column(UUID(as_uuid=True), comment='审核人')
    approved_at = Column(DateTime, comment='审核时间')
    
    # 业务关联
    source_document_type = Column(String(50), comment='来源单据类型')  # sales_order/transfer_order/production_order
    source_document_id = Column(UUID(as_uuid=True), comment='来源单据ID')
    source_document_number = Column(String(100), comment='来源单据号')
    
    # 客户信息
    customer_id = Column(UUID(as_uuid=True), comment='客户ID')
    customer_name = Column(String(200), comment='客户名称')
    
    # 物流信息
    delivery_address = Column(Text, comment='配送地址')
    delivery_contact = Column(String(100), comment='联系人')
    delivery_phone = Column(String(50), comment='联系电话')
    expected_delivery_date = Column(DateTime, comment='预计发货日期')
    actual_delivery_date = Column(DateTime, comment='实际发货日期')
    
    # 扩展字段
    remark = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    details = relationship("OutboundOrderDetail", back_populates="outbound_order", cascade="all, delete-orphan")
    outbound_person = relationship("Employee", foreign_keys=[outbound_person_id], lazy='select')
    department = relationship("Department", foreign_keys=[department_id], lazy='select')
    
    # 出库类型常量
    ORDER_TYPES = [
        ('finished_goods', '成品出库'),
        ('raw_materials', '原材料出库'),
        ('semi_finished', '半成品出库'),
        ('other', '其他出库')
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('in_progress', '执行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已审核'),
        ('rejected', '已拒绝')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_outbound_order_number', 'order_number'),
        Index('ix_outbound_order_date', 'order_date'),
        Index('ix_outbound_order_warehouse', 'warehouse_id'),
        Index('ix_outbound_order_status', 'status', 'approval_status'),
        Index('ix_outbound_order_source', 'source_document_type', 'source_document_id'),
        Index('ix_outbound_order_customer', 'customer_id'),
    )
    
    def __init__(self, warehouse_id, order_type, created_by, **kwargs):
        """
        初始化出库单
        """
        self.warehouse_id = warehouse_id
        self.order_type = order_type
        self.created_by = created_by
        
        # 生成出库单号
        if not kwargs.get('order_number'):
            self.order_number = self.generate_order_number(order_type)
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def generate_order_number(order_type='finished_goods'):
        """
        生成出库单号 - 按顺序生成
        """
        from datetime import datetime
        from sqlalchemy import func, text
        from app.extensions import db
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        prefix_map = {
            'finished_goods': 'OUT',
            'raw_materials': 'ORM',
            'semi_finished': 'OSM',
            'other': 'OOT'
        }
        prefix = prefix_map.get(order_type, 'OUT')
        
        # 查询当天该类型的最大序号
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取当天该类型的最大序号
        # 获取当天的最大序号 - 修复查询语法
        try:
            max_order = db.session.query(func.max(
                func.cast(func.substring(OutboundOrder.order_number, -4), func.Integer)
            )).filter(
                OutboundOrder.order_type == order_type,
                OutboundOrder.created_at >= today_start,
                OutboundOrder.created_at <= today_end
            ).scalar()
        except Exception as e:
            # 如果查询失败，使用简单的计数方法
            count = db.session.query(OutboundOrder).filter(
                OutboundOrder.order_type == order_type,
                OutboundOrder.created_at >= today_start,
                OutboundOrder.created_at <= today_end
            ).count()
            max_order = count
        
        # 序号从1开始，如果没有记录则为0，所以下一个序号为max_order + 1
        next_sequence = (max_order or 0) + 1
        
        # 格式化为4位数字，不足补0
        sequence_str = f"{next_sequence:04d}"
        
        return f"{prefix}{timestamp}{sequence_str}"
    
    def calculate_totals(self):
        """
        计算汇总数据
        """
        if self.details:
            self.total_quantity = sum(detail.outbound_quantity for detail in self.details)
            self.total_kg_quantity = sum(detail.outbound_kg_quantity or 0 for detail in self.details)
            self.total_m_quantity = sum(detail.outbound_m_quantity or 0 for detail in self.details)
            self.total_roll_quantity = sum(detail.outbound_roll_quantity or 0 for detail in self.details)
            self.total_box_quantity = sum(detail.box_quantity or 0 for detail in self.details)
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'order_type': self.order_type,
            'warehouse_id': str(self.warehouse_id) if self.warehouse_id else None,
            'warehouse_name': self.warehouse_name,
            'outbound_person_id': str(self.outbound_person_id) if self.outbound_person_id else None,
            'outbound_person': self.outbound_person.employee_name if self.outbound_person else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'department': self.department.dept_name if self.department else None,
            'pallet_barcode': self.pallet_barcode,
            'pallet_count': self.pallet_count,
            'status': self.status,
            'approval_status': self.approval_status,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'source_document_type': self.source_document_type,
            'source_document_id': str(self.source_document_id) if self.source_document_id else None,
            'source_document_number': self.source_document_number,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'customer_name': self.customer_name,
            'delivery_address': self.delivery_address,
            'delivery_contact': self.delivery_contact,
            'delivery_phone': self.delivery_phone,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'remark': self.remark,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'details': [detail.to_dict() for detail in self.details] if self.details else []
        }
    
    def __repr__(self):
        return f'<OutboundOrder {self.order_number} {self.order_type}>'


class OutboundOrderDetail(TenantModel):
    """
    出库单明细表
    """
    
    __tablename__ = 'outbound_order_details'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联主表
    outbound_order_id = Column(UUID(as_uuid=True), ForeignKey('outbound_orders.id'), nullable=False, comment='出库单ID')
    
    # 产品信息
    product_id = Column(UUID(as_uuid=True), comment='产品ID')
    product_name = Column(String(200), comment='产品名称')
    product_code = Column(String(100), comment='产品编码')
    product_spec = Column(String(500), comment='产品规格')
    
    # 数量信息
    outbound_quantity = Column(Numeric(15, 3), nullable=False, default=0, comment='出库数')
    outbound_kg_quantity = Column(Numeric(15, 3), comment='出库kg数')
    outbound_m_quantity = Column(Numeric(15, 3), comment='出库m数')
    outbound_roll_quantity = Column(Numeric(15, 3), comment='出库卷数')
    box_quantity = Column(Numeric(15, 3), comment='装箱数')
    case_quantity = Column(Integer, comment='箱数')
    
    # 单位信息
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='基本单位ID')
    kg_unit = Column(String(20), default='kg', comment='重量单位')
    m_unit = Column(String(20), default='m', comment='长度单位')
    
    # 批次信息
    batch_number = Column(String(100), comment='批次号')
    production_date = Column(DateTime, comment='生产日期')
    expiry_date = Column(DateTime, comment='到期日期')
    
    # 质量信息
    quality_status = Column(String(20), default='qualified', comment='质量状态')  # qualified/unqualified/pending
    quality_certificate = Column(String(200), comment='质检证书')
    
    # 成本信息
    unit_cost = Column(Numeric(15, 4), comment='单位成本')
    total_cost = Column(Numeric(18, 4), comment='总成本')
    
    # 库位信息
    location_code = Column(String(100), comment='出库库位')
    actual_location_code = Column(String(100), comment='实际出库库位')

        # 包装信息
    package_quantity = Column(Numeric(15, 3), comment='包装数量')
    package_unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), comment='包装单位ID')
    
    # 库存关联
    inventory_id = Column(UUID(as_uuid=True), comment='库存ID')
    available_quantity = Column(Numeric(15, 3), comment='可用库存数量')
    
    # 行号和排序
    line_number = Column(Integer, comment='行号')
    sort_order = Column(Integer, default=0, comment='排序')
    
    # 扩展字段
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    outbound_order = relationship("OutboundOrder", back_populates="details")
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')
    package_unit = relationship("Unit", foreign_keys=[package_unit_id], lazy='select')

    # 质量状态常量
    QUALITY_STATUS_CHOICES = [
        ('qualified', '合格'),
        ('unqualified', '不合格'),
        ('pending', '待检')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_outbound_detail_order', 'outbound_order_id'),
        Index('ix_outbound_detail_product', 'product_id'),
        Index('ix_outbound_detail_batch', 'batch_number'),
        Index('ix_outbound_detail_location', 'location_code'),
        Index('ix_outbound_detail_inventory', 'inventory_id'),
    )
    
    def __init__(self, outbound_order_id, outbound_quantity, unit_id, created_by, **kwargs):
        """
        初始化出库单明细
        """
        self.outbound_order_id = outbound_order_id
        self.outbound_quantity = outbound_quantity
        self.unit_id = unit_id
        self.created_by = created_by
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_total_cost(self):
        """
        计算总成本
        """
        if self.unit_cost and self.outbound_quantity:
            # 确保两个值都是Decimal类型以避免类型错误
            unit_cost = Decimal(str(self.unit_cost)) if not isinstance(self.unit_cost, Decimal) else self.unit_cost
            outbound_quantity = Decimal(str(self.outbound_quantity)) if not isinstance(self.outbound_quantity, Decimal) else self.outbound_quantity
            self.total_cost = unit_cost * outbound_quantity
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'outbound_order_id': str(self.outbound_order_id),
            'product_id': str(self.product_id) if self.product_id else None,
            'product_name': self.product_name,
            'product_code': self.product_code,
            'product_spec': self.product_spec,
            'outbound_quantity': float(self.outbound_quantity) if self.outbound_quantity else 0,
            'outbound_kg_quantity': float(self.outbound_kg_quantity) if self.outbound_kg_quantity else None,
            'outbound_m_quantity': float(self.outbound_m_quantity) if self.outbound_m_quantity else None,
            'outbound_roll_quantity': float(self.outbound_roll_quantity) if self.outbound_roll_quantity else None,
            'box_quantity': float(self.box_quantity) if self.box_quantity else None,
            'case_quantity': self.case_quantity,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit_name': self.unit.unit_name if self.unit else None,
            'kg_unit': self.kg_unit,
            'm_unit': self.m_unit,
            'batch_number': self.batch_number,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'quality_status': self.quality_status,
            'quality_certificate': self.quality_certificate,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'total_cost': float(self.total_cost) if self.total_cost else None,
            'location_code': self.location_code,
            'actual_location_code': self.actual_location_code,
            'inventory_id': str(self.inventory_id) if self.inventory_id else None,
            'available_quantity': float(self.available_quantity) if self.available_quantity else None,
            'package_quantity': float(self.package_quantity) if self.package_quantity else None,
            'package_unit_id': str(self.package_unit_id) if self.package_unit_id else None,
            'package_unit_name': self.package_unit.unit_name if self.package_unit else None,
            'line_number': self.line_number,
            'sort_order': self.sort_order,
            'notes': self.notes,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<OutboundOrderDetail {self.product_name} Qty:{self.outbound_quantity}>'


class MaterialInboundOrder(TenantModel):
    """
    材料入库单主表
    """
    
    __tablename__ = 'material_inbound_orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 单据信息
    order_number = Column(String(100), unique=True, nullable=False, comment='入库单号')
    order_date = Column(DateTime, default=func.now(), nullable=False, comment='发生日期')
    order_type = Column(String(20), default='material', comment='入库类型')  # material/auxiliary/packaging
    
    # 仓库信息
    warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='仓库ID')
    warehouse_name = Column(String(200), comment='仓库名称')
    
    # 入库人员信息 - 改为外键关联
    inbound_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), comment='入库人ID')
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), comment='部门ID')
    
    # 托盘信息
    pallet_barcode = Column(String(200), comment='托盘条码')
    pallet_count = Column(Integer, default=0, comment='托盘套数')
    
    # 单据状态
    status = Column(String(20), default='draft', comment='单据状态')  # draft/confirmed/in_progress/completed/cancelled
    is_outbound = Column(Boolean, default=False, comment='是否已出库')
    
    # 审核信息
    approval_status = Column(String(20), default='pending', comment='审核状态')  # pending/approved/rejected
    approved_by = Column(UUID(as_uuid=True), comment='审核人')
    approved_at = Column(DateTime, comment='审核时间')
    
    # 业务关联
    source_document_type = Column(String(50), comment='来源单据类型')  # purchase_order/transfer_order/adjustment_order
    source_document_id = Column(UUID(as_uuid=True), comment='来源单据ID')
    source_document_number = Column(String(100), comment='来源单据号')
    
    # 供应商信息
    supplier_id = Column(UUID(as_uuid=True), comment='供应商ID')
    supplier_name = Column(String(200), comment='供应商名称')
    
    # 扩展字段
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    details = relationship("MaterialInboundOrderDetail", back_populates="material_inbound_order", cascade="all, delete-orphan")
    inbound_person = relationship("Employee", foreign_keys=[inbound_person_id], lazy='select')
    department = relationship("Department", foreign_keys=[department_id], lazy='select')
    
    # 入库类型常量
    ORDER_TYPES = [
        ('purchase', '采购入库'),
        ('return', '退货入库'),
        ('other', '其他入库')
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('in_progress', '执行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已审核'),
        ('rejected', '已拒绝')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_material_inbound_order_number', 'order_number'),
        Index('ix_material_inbound_order_date', 'order_date'),
        Index('ix_material_inbound_order_warehouse', 'warehouse_id'),
        Index('ix_material_inbound_order_status', 'status', 'approval_status'),
        Index('ix_material_inbound_order_source', 'source_document_type', 'source_document_id'),
        Index('ix_material_inbound_order_supplier', 'supplier_id'),
    )
    
    def __init__(self, warehouse_id, order_type, created_by, **kwargs):
        """
        初始化材料入库单
        """
        self.warehouse_id = warehouse_id
        self.order_type = order_type
        self.created_by = created_by
        
        # 生成入库单号
        if not kwargs.get('order_number'):
            self.order_number = self.generate_order_number(order_type)
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def generate_order_number(order_type='material'):
        """
        生成材料入库单号 - 按顺序生成
        """
        from datetime import datetime
        from sqlalchemy import func, text
        from app.extensions import db
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 查询当天的最大序号
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取当天的最大序号 - 修复查询语法
        try:
            max_order = db.session.query(func.max(
                func.cast(func.substring(MaterialInboundOrder.order_number, -4), func.Integer)
            )).filter(
                MaterialInboundOrder.created_at >= today_start,
                MaterialInboundOrder.created_at <= today_end
            ).scalar()
        except Exception as e:
            # 如果查询失败，使用简单的计数方法
            count = db.session.query(MaterialInboundOrder).filter(
                MaterialInboundOrder.created_at >= today_start,
                MaterialInboundOrder.created_at <= today_end
            ).count()
            max_order = count
        
        # 序号从1开始，如果没有记录则为0，所以下一个序号为max_order + 1
        next_sequence = (max_order or 0) + 1
        
        # 格式化为4位数字，不足补0
        sequence_str = f"{next_sequence:04d}"
        
        prefix_map = {
            'material': 'MIN',
            'auxiliary': 'AIN',
            'packaging': 'PIN',
            'other': 'OIN'
        }
        prefix = prefix_map.get(order_type, 'MIN')
        
        return f"{prefix}{timestamp}{sequence_str}"
    
    def calculate_totals(self):
        """
        计算汇总数据
        """
        if self.details:
            self.total_quantity = sum(detail.inbound_quantity for detail in self.details)
            self.total_weight = sum(detail.inbound_weight or 0 for detail in self.details)
            self.total_amount = sum(detail.total_amount or 0 for detail in self.details)
    
    def to_dict(self):
        """
        转换为字典
        """
        # 安全地获取关联对象的属性
        try:
            inbound_person_name = self.inbound_person.employee_name if self.inbound_person else None
        except:
            inbound_person_name = None
        
        try:
            department_name = self.department.dept_name if self.department else None
        except:
            department_name = None
        
        return {
            'id': str(self.id),
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'order_type': self.order_type,
            'warehouse_id': str(self.warehouse_id) if self.warehouse_id else None,
            'warehouse_name': self.warehouse_name,
            'inbound_person_id': str(self.inbound_person_id) if self.inbound_person_id else None,
            'inbound_person': inbound_person_name,
            'department_id': str(self.department_id) if self.department_id else None,
            'department': department_name,
            'pallet_barcode': self.pallet_barcode,
            'pallet_count': self.pallet_count,
            'status': self.status,
            'is_outbound': self.is_outbound,
            'approval_status': self.approval_status,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'source_document_type': self.source_document_type,
            'source_document_id': str(self.source_document_id) if self.source_document_id else None,
            'source_document_number': self.source_document_number,
            'supplier_id': str(self.supplier_id) if self.supplier_id else None,
            'supplier_name': self.supplier_name,
            'notes': self.notes,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # 'details': [detail.to_dict() for detail in self.details] if self.details else []  # 避免懒加载
        }
    
    def __repr__(self):
        return f'<MaterialInboundOrder {self.order_number} {self.order_type}>'


class MaterialInboundOrderDetail(TenantModel):
    """
    材料入库单明细表
    """
    
    __tablename__ = 'material_inbound_order_details'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联主表
    material_inbound_order_id = Column(UUID(as_uuid=True), ForeignKey('material_inbound_orders.id'), nullable=False, comment='材料入库单ID')
    
    # 材料信息
    material_id = Column(UUID(as_uuid=True), comment='材料ID')
    material_name = Column(String(200), comment='材料名称')
    material_code = Column(String(100), comment='材料编码')
    material_spec = Column(String(500), comment='材料规格')
    
    # 数量信息
    inbound_quantity = Column(Numeric(15, 3), nullable=False, default=0, comment='入库数量')
    inbound_weight = Column(Numeric(15, 3), comment='入库重量(kg)')
    inbound_length = Column(Numeric(15, 3), comment='入库长度(m)')
    inbound_rolls = Column(Numeric(15, 3), comment='入库卷数')
    
    # 单位信息
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='基本单位ID')
    weight_unit = Column(String(20), default='kg', comment='重量单位')
    length_unit = Column(String(20), default='m', comment='长度单位')
    
    # 批次信息
    batch_number = Column(String(100), comment='批次号')
    production_date = Column(DateTime, comment='生产日期')
    expiry_date = Column(DateTime, comment='到期日期')
    
    # 质量信息
    quality_status = Column(String(20), default='qualified', comment='质量状态')  # qualified/unqualified/pending
    quality_certificate = Column(String(200), comment='质检证书')
    
    # 成本信息
    unit_price = Column(Numeric(15, 4), comment='单价')
    total_amount = Column(Numeric(18, 4), comment='总金额')
    
    # 库位信息
    location_code = Column(String(100), comment='建议库位')
    actual_location_code = Column(String(100), comment='实际库位')
    
    # 行号和排序
    line_number = Column(Integer, comment='行号')
    sort_order = Column(Integer, default=0, comment='排序')
    
    # 扩展字段
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    material_inbound_order = relationship("MaterialInboundOrder", back_populates="details")
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')
    
    # 质量状态常量
    QUALITY_STATUS_CHOICES = [
        ('qualified', '合格'),
        ('unqualified', '不合格'),
        ('pending', '待检')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_material_inbound_detail_order', 'material_inbound_order_id'),
        Index('ix_material_inbound_detail_material', 'material_id'),
        Index('ix_material_inbound_detail_batch', 'batch_number'),
        Index('ix_material_inbound_detail_location', 'location_code'),
    )
    
    def __init__(self, material_inbound_order_id, inbound_quantity, unit_id, created_by, **kwargs):
        """
        初始化材料入库单明细
        """
        self.material_inbound_order_id = material_inbound_order_id
        self.inbound_quantity = inbound_quantity
        self.unit_id = unit_id
        self.created_by = created_by
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_total_amount(self):
        """
        计算总金额
        """
        if self.unit_price and self.inbound_quantity:
            # 确保两个值都是Decimal类型以避免类型错误
            unit_price = Decimal(str(self.unit_price)) if not isinstance(self.unit_price, Decimal) else self.unit_price
            inbound_quantity = Decimal(str(self.inbound_quantity)) if not isinstance(self.inbound_quantity, Decimal) else self.inbound_quantity
            self.total_amount = unit_price * inbound_quantity
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'order_id': str(self.material_inbound_order_id),
            'material_id': str(self.material_id) if self.material_id else None,
            'material_name': self.material_name,
            'material_code': self.material_code,
            'specification': self.material_spec,
            'inbound_quantity': float(self.inbound_quantity) if self.inbound_quantity else 0,
            'weight': float(self.inbound_weight) if self.inbound_weight else None,
            'length': float(self.inbound_length) if self.inbound_length else None,
            'roll_count': float(self.inbound_rolls) if self.inbound_rolls else None,
            # 添加前端需要的字段别名
            'inbound_weight': float(self.inbound_weight) if self.inbound_weight else None,
            'inbound_length': float(self.inbound_length) if self.inbound_length else None,
            'inbound_rolls': float(self.inbound_rolls) if self.inbound_rolls else None,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit': self.unit.unit_name if self.unit else None,  # 添加单位名称
            'weight_unit': self.weight_unit,
            'length_unit': self.length_unit,
            'batch_number': self.batch_number,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'quality_status': self.quality_status,
            'quality_certificate': self.quality_certificate,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'suggested_location': self.location_code,
            'actual_location': self.actual_location_code,
            'line_number': self.line_number,
            'sort_order': self.sort_order,
            'notes': self.notes,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<MaterialInboundOrderDetail {self.material_name} Qty:{self.inbound_quantity}>'


class MaterialOutboundOrder(TenantModel):
    """
    材料出库单主表
    """
    
    __tablename__ = 'material_outbound_orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 单据信息
    order_number = Column(String(100), unique=True, nullable=False, comment='出库单号')
    order_date = Column(DateTime, default=func.now(), nullable=False, comment='发生日期')
    order_type = Column(String(20), default='material', comment='出库类型')  # material/auxiliary/packaging
    
    # 仓库信息
    warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='仓库ID')
    warehouse_name = Column(String(200), comment='仓库名称')
    
    # 出库人员信息 - 改为外键关联
    outbound_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), comment='出库人ID')
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), comment='部门ID')
    
    # 托盘信息
    pallet_barcode = Column(String(200), comment='托盘条码')
    pallet_count = Column(Integer, default=0, comment='托盘套数')
    
    # 单据状态
    status = Column(String(20), default='draft', comment='单据状态')  # draft/confirmed/in_progress/completed/cancelled
    
    # 审核信息
    approval_status = Column(String(20), default='pending', comment='审核状态')  # pending/approved/rejected
    approved_by = Column(UUID(as_uuid=True), comment='审核人')
    approved_at = Column(DateTime, comment='审核时间')
    
    # 业务关联
    source_document_type = Column(String(50), comment='来源单据类型')  # production_order/transfer_order/requisition_order
    source_document_id = Column(UUID(as_uuid=True), comment='来源单据ID')
    source_document_number = Column(String(100), comment='来源单据号')
    
    # 领用部门信息 - 改为外键关联
    requisition_department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), comment='领用部门ID')
    requisition_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), comment='领用人ID')
    requisition_purpose = Column(String(200), comment='领用用途')
    
    # 扩展字段
    remark = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    details = relationship("MaterialOutboundOrderDetail", back_populates="material_outbound_order", cascade="all, delete-orphan")
    outbound_person = relationship("Employee", foreign_keys=[outbound_person_id], lazy='select')
    department = relationship("Department", foreign_keys=[department_id], lazy='select')
    requisition_department = relationship("Department", foreign_keys=[requisition_department_id], lazy='select')
    requisition_person = relationship("Employee", foreign_keys=[requisition_person_id], lazy='select')
    
    # 出库类型常量
    ORDER_TYPES = [
        ('material', '材料出库'),
        ('auxiliary', '辅料出库'),
        ('packaging', '包装出库'),
        ('other', '其他出库')
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('in_progress', '执行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已审核'),
        ('rejected', '已拒绝')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_material_outbound_order_number', 'order_number'),
        Index('ix_material_outbound_order_date', 'order_date'),
        Index('ix_material_outbound_order_warehouse', 'warehouse_id'),
        Index('ix_material_outbound_order_status', 'status', 'approval_status'),
        Index('ix_material_outbound_order_source', 'source_document_type', 'source_document_id'),
        Index('ix_material_outbound_order_requisition_dept', 'requisition_department_id'),
        Index('ix_material_outbound_order_requisition_person', 'requisition_person_id'),
    )
    
    def __init__(self, warehouse_id, order_type, created_by, **kwargs):
        """
        初始化材料出库单
        """
        self.warehouse_id = warehouse_id
        self.order_type = order_type
        self.created_by = created_by
        
        # 生成出库单号
        if not kwargs.get('order_number'):
            self.order_number = self.generate_order_number(order_type)
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def generate_order_number(order_type='material'):
        """
        生成材料出库单号 - 按顺序生成
        """
        from datetime import datetime
        from sqlalchemy import func, text
        from app.extensions import db
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 查询当天的最大序号
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取当天的最大序号 - 修复查询语法
        try:
            max_order = db.session.query(func.max(
                func.cast(func.substring(MaterialOutboundOrder.order_number, -4), func.Integer)
            )).filter(
                MaterialOutboundOrder.created_at >= today_start,
                MaterialOutboundOrder.created_at <= today_end
            ).scalar()
        except Exception as e:
            # 如果查询失败，使用简单的计数方法
            count = db.session.query(MaterialOutboundOrder).filter(
                MaterialOutboundOrder.created_at >= today_start,
                MaterialOutboundOrder.created_at <= today_end
            ).count()
            max_order = count
        
        # 序号从1开始，如果没有记录则为0，所以下一个序号为max_order + 1
        next_sequence = (max_order or 0) + 1
        
        # 格式化为4位数字，不足补0
        sequence_str = f"{next_sequence:04d}"
        
        prefix_map = {
            'material': 'MOUT',
            'auxiliary': 'AOUT',
            'packaging': 'POUT',
            'other': 'OOUT'
        }
        prefix = prefix_map.get(order_type, 'MOUT')
        
        return f"{prefix}{timestamp}{sequence_str}"
    
    def calculate_totals(self):
        """
        计算汇总数据
        """
        if self.details:
            self.total_quantity = sum(detail.outbound_quantity for detail in self.details)
            self.total_weight = sum(detail.outbound_weight or 0 for detail in self.details)
            self.total_amount = sum(detail.total_amount or 0 for detail in self.details)
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'order_type': self.order_type,
            'warehouse_id': str(self.warehouse_id) if self.warehouse_id else None,
            'warehouse_name': self.warehouse_name,
            'outbound_person_id': str(self.outbound_person_id) if self.outbound_person_id else None,
            'outbound_person': self.outbound_person.employee_name if self.outbound_person else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'department': self.department.dept_name if self.department else None,
            'pallet_barcode': self.pallet_barcode,
            'pallet_count': self.pallet_count,
            'status': self.status,
            'approval_status': self.approval_status,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'source_document_type': self.source_document_type,
            'source_document_id': str(self.source_document_id) if self.source_document_id else None,
            'source_document_number': self.source_document_number,
            'requisition_department_id': str(self.requisition_department_id) if self.requisition_department_id else None,
            'requisition_department': self.requisition_department.dept_name if self.requisition_department else None,
            'requisition_person_id': str(self.requisition_person_id) if self.requisition_person_id else None,
            'requisition_person': self.requisition_person.employee_name if self.requisition_person else None,
            'requisition_purpose': self.requisition_purpose,
            'remark': self.remark,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'details': [detail.to_dict() for detail in self.details] if self.details else []
        }
    
    def __repr__(self):
        return f'<MaterialOutboundOrder {self.order_number} {self.order_type}>'


class MaterialOutboundOrderDetail(TenantModel):
    """
    材料出库单明细表
    """
    
    __tablename__ = 'material_outbound_order_details'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联主表
    material_outbound_order_id = Column(UUID(as_uuid=True), ForeignKey('material_outbound_orders.id'), nullable=False, comment='材料出库单ID')
    
    # 材料信息
    material_id = Column(UUID(as_uuid=True), comment='材料ID')
    material_name = Column(String(200), comment='材料名称')
    material_code = Column(String(100), comment='材料编码')
    material_spec = Column(String(500), comment='材料规格')
    
    # 数量信息
    outbound_quantity = Column(Numeric(15, 3), nullable=False, default=0, comment='出库数量')
    outbound_weight = Column(Numeric(15, 3), comment='出库重量(kg)')
    outbound_length = Column(Numeric(15, 3), comment='出库长度(m)')
    outbound_rolls = Column(Numeric(15, 3), comment='出库卷数')
    
    # 单位信息
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='基本单位ID')
    weight_unit = Column(String(20), default='kg', comment='重量单位')
    length_unit = Column(String(20), default='m', comment='长度单位')
    
    # 批次信息
    batch_number = Column(String(100), comment='批次号')
    production_date = Column(DateTime, comment='生产日期')
    expiry_date = Column(DateTime, comment='到期日期')
    
    # 质量信息
    quality_status = Column(String(20), default='qualified', comment='质量状态')  # qualified/unqualified/pending
    quality_certificate = Column(String(200), comment='质检证书')
    
    # 成本信息
    unit_price = Column(Numeric(15, 4), comment='单价')
    total_amount = Column(Numeric(18, 4), comment='总金额')
    
    # 库位信息
    location_code = Column(String(100), comment='出库库位')
    actual_location_code = Column(String(100), comment='实际出库库位')
    
    # 库存关联
    inventory_id = Column(UUID(as_uuid=True), comment='库存ID')
    available_quantity = Column(Numeric(15, 3), comment='可用库存数量')
    
    # 行号和排序
    line_number = Column(Integer, comment='行号')
    sort_order = Column(Integer, default=0, comment='排序')
    
    # 扩展字段
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    material_outbound_order = relationship("MaterialOutboundOrder", back_populates="details")
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')

    # 质量状态常量
    QUALITY_STATUS_CHOICES = [
        ('qualified', '合格'),
        ('unqualified', '不合格'),
        ('pending', '待检')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_material_outbound_detail_order', 'material_outbound_order_id'),
        Index('ix_material_outbound_detail_material', 'material_id'),
        Index('ix_material_outbound_detail_batch', 'batch_number'),
        Index('ix_material_outbound_detail_location', 'location_code'),
        Index('ix_material_outbound_detail_inventory', 'inventory_id'),
    )
    
    def __init__(self, material_outbound_order_id, outbound_quantity, unit_id, created_by, **kwargs):
        """
        初始化材料出库单明细
        """
        self.material_outbound_order_id = material_outbound_order_id
        self.outbound_quantity = outbound_quantity
        self.unit_id = unit_id
        self.created_by = created_by
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_total_amount(self):
        """
        计算总金额
        """
        if self.unit_price and self.outbound_quantity:
            # 确保两个值都是Decimal类型以避免类型错误
            unit_price = Decimal(str(self.unit_price)) if not isinstance(self.unit_price, Decimal) else self.unit_price
            outbound_quantity = Decimal(str(self.outbound_quantity)) if not isinstance(self.outbound_quantity, Decimal) else self.outbound_quantity
            self.total_amount = unit_price * outbound_quantity
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'material_outbound_order_id': str(self.material_outbound_order_id),
            'material_id': str(self.material_id) if self.material_id else None,
            'material_name': self.material_name,
            'material_code': self.material_code,
            'material_spec': self.material_spec,
            'outbound_quantity': float(self.outbound_quantity) if self.outbound_quantity else 0,
            'outbound_weight': float(self.outbound_weight) if self.outbound_weight else None,
            'outbound_length': float(self.outbound_length) if self.outbound_length else None,
            'outbound_rolls': float(self.outbound_rolls) if self.outbound_rolls else None,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit': self.unit.unit_name if self.unit else None,  # 添加单位名称
            'weight_unit': self.weight_unit,
            'length_unit': self.length_unit,
            'batch_number': self.batch_number,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'quality_status': self.quality_status,
            'quality_certificate': self.quality_certificate,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'location_code': self.location_code,
            'actual_location_code': self.actual_location_code,
            'inventory_id': str(self.inventory_id) if self.inventory_id else None,
            'available_quantity': float(self.available_quantity) if self.available_quantity else None,
            'line_number': self.line_number,
            'sort_order': self.sort_order,
            'notes': self.notes,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<MaterialOutboundOrderDetail {self.material_name} Qty:{self.outbound_quantity}>'


# 注释：材料库存将使用统一的inventory表，不需要单独的MaterialInventory表


# 注释：材料库存变动记录将使用统一的inventory_transactions表，不需要单独的MaterialInventoryTransaction表 


class MaterialCountPlan(TenantModel):
    """
    材料盘点计划表
    """
    
    __tablename__ = 'material_count_plans'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 盘点基本信息
    count_number = Column(String(100), unique=True, nullable=False, comment='盘点单号')
    warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='仓库ID')
    warehouse_name = Column(String(200), nullable=False, comment='仓库名称')
    warehouse_code = Column(String(100), comment='仓库编号')
    
    # 盘点人员信息 - 改为外键关联
    count_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False, comment='盘点人ID')
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), comment='部门ID')
    
    # 盘点时间
    count_date = Column(DateTime, nullable=False, comment='发生日期')
    
    # 盘点状态
    status = Column(String(20), default='draft', comment='状态')  # draft/in_progress/completed
    
    # 备注
    notes = Column(Text, comment='备注')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    count_records = relationship("MaterialCountRecord", back_populates="count_plan", cascade="all, delete-orphan")
    count_person = relationship("Employee", foreign_keys=[count_person_id], lazy='select')
    department = relationship("Department", foreign_keys=[department_id], lazy='select')
    
    # 状态常量
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('adjusted', '已调整')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_material_count_plan_number', 'count_number'),
        Index('ix_material_count_plan_warehouse', 'warehouse_id'),
        Index('ix_material_count_plan_person', 'count_person_id'),
        Index('ix_material_count_plan_department', 'department_id'),
        Index('ix_material_count_plan_date', 'count_date'),
        Index('ix_material_count_plan_status', 'status'),
    )
    
    def __init__(self, warehouse_id, warehouse_name, count_person_id, count_date, created_by, **kwargs):
        """
        初始化材料盘点计划
        """
        self.warehouse_id = warehouse_id
        self.warehouse_name = warehouse_name
        self.count_person_id = count_person_id
        self.count_date = count_date
        self.created_by = created_by
        
        # 生成盘点单号
        if not kwargs.get('count_number'):
            self.count_number = self.generate_count_number()
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def generate_count_number():
        """
        生成盘点单号 - 按顺序生成
        """
        from datetime import datetime
        from sqlalchemy import func, text
        from app.extensions import db
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 查询当天的最大序号
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取当天的最大序号
        # 获取当天的最大序号 - 修复查询语法
        try:
            max_order = db.session.query(func.max(
                func.cast(func.substring(MaterialCountPlan.count_number, -4), func.Integer)
            )).filter(
                MaterialCountPlan.created_at >= today_start,
                MaterialCountPlan.created_at <= today_end
            ).scalar()
        except Exception as e:
            # 如果查询失败，使用简单的计数方法
            count = db.session.query(MaterialCountPlan).filter(
                MaterialCountPlan.created_at >= today_start,
                MaterialCountPlan.created_at <= today_end
            ).count()
            max_order = count
        
        # 序号从1开始，如果没有记录则为0，所以下一个序号为max_order + 1
        next_sequence = (max_order or 0) + 1
        
        # 格式化为4位数字，不足补0
        sequence_str = f"{next_sequence:04d}"
        
        return f"PD{timestamp}{sequence_str}"
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'count_number': self.count_number,
            'warehouse_id': str(self.warehouse_id),
            'warehouse_name': self.warehouse_name,
            'warehouse_code': self.warehouse_code,
            'count_person_id': str(self.count_person_id),
            'count_person': self.count_person.employee_name if self.count_person else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'department': self.department.dept_name if self.department else None,
            'count_date': self.count_date.isoformat() if self.count_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<MaterialCountPlan {self.count_number}>'


class MaterialCountRecord(TenantModel):
    """
    材料盘点记录表
    """
    
    __tablename__ = 'material_count_records'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联盘点计划
    count_plan_id = Column(UUID(as_uuid=True), ForeignKey('material_count_plans.id'), nullable=False, comment='盘点计划ID')
    
    # 关联库存
    inventory_id = Column(UUID(as_uuid=True), comment='库存ID')
    material_id = Column(UUID(as_uuid=True), nullable=False, comment='材料ID')
    
    # 材料信息
    material_code = Column(String(100), comment='材料编码')
    material_name = Column(String(200), nullable=False, comment='材料名称')
    material_spec = Column(String(200), comment='规格')
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='单位ID')
    
    # 盘点数据
    book_quantity = Column(Numeric(15, 3), nullable=False, default=0, comment='账面数量')
    actual_quantity = Column(Numeric(15, 3), comment='实盘数量')
    variance_quantity = Column(Numeric(15, 3), comment='差异数量')
    variance_rate = Column(Numeric(8, 4), comment='差异率%')
    
    # 批次和位置信息
    batch_number = Column(String(100), comment='批次号')
    location_code = Column(String(100), comment='库位')
    
    # 差异处理
    variance_reason = Column(String(500), comment='差异原因')
    is_adjusted = Column(Boolean, default=False, comment='是否已调整')
    
    # 状态
    status = Column(String(20), default='pending', comment='状态')  # pending/counted/adjusted
    
    # 备注
    notes = Column(Text, comment='备注')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    count_plan = relationship("MaterialCountPlan", back_populates="count_records")
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')
    
    # 状态常量
    STATUS_CHOICES = [
        ('pending', '待盘点'),
        ('counted', '已盘点'),
        ('adjusted', '已调整')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_material_count_records_plan', 'count_plan_id'),
        Index('ix_material_count_records_material', 'material_id'),
        Index('ix_material_count_records_status', 'status'),
    )
    
    def __init__(self, count_plan_id, material_id, material_name, unit_id, book_quantity, created_by, **kwargs):
        """
        初始化材料盘点记录
        """
        self.count_plan_id = count_plan_id
        self.material_id = material_id
        self.material_name = material_name
        self.unit_id = unit_id
        self.book_quantity = book_quantity
        self.created_by = created_by
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_variance(self):
        """
        计算差异
        """
        if self.actual_quantity is not None:
            self.variance_quantity = self.actual_quantity - self.book_quantity
            if self.book_quantity != 0:
                self.variance_rate = (self.variance_quantity / self.book_quantity) * 100
            else:
                self.variance_rate = 100 if self.actual_quantity > 0 else 0
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'count_plan_id': str(self.count_plan_id),
            'inventory_id': str(self.inventory_id) if self.inventory_id else None,
            'material_id': str(self.material_id),
            'material_code': self.material_code,
            'material_name': self.material_name,
            'material_spec': self.material_spec,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit': self.unit.unit_name if self.unit else None,
            'book_quantity': float(self.book_quantity),
            'actual_quantity': float(self.actual_quantity) if self.actual_quantity is not None else None,
            'variance_quantity': float(self.variance_quantity) if self.variance_quantity is not None else None,
            'variance_rate': float(self.variance_rate) if self.variance_rate is not None else None,
            'batch_number': self.batch_number,
            'location_code': self.location_code,
            'variance_reason': self.variance_reason,
            'is_adjusted': self.is_adjusted,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<MaterialCountRecord {self.material_name} Book:{self.book_quantity} Actual:{self.actual_quantity}>'


class MaterialTransferOrder(TenantModel):
    """
    材料调拨单主表
    """
    
    __tablename__ = 'material_transfer_orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 单据信息
    transfer_number = Column(String(100), unique=True, nullable=False, comment='调拨单号')
    transfer_date = Column(DateTime, default=func.now(), nullable=False, comment='发生日期')
    transfer_type = Column(String(20), default='warehouse', comment='调拨类型')  # warehouse/department/project
    
    # 调出信息
    from_warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='调出仓库ID')
    from_warehouse_name = Column(String(200), comment='调出仓库名称')
    from_warehouse_code = Column(String(100), comment='调出仓库编码')
    
    # 调入信息
    to_warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='调入仓库ID')
    to_warehouse_name = Column(String(200), comment='调入仓库名称')
    to_warehouse_code = Column(String(100), comment='调入仓库编码')
    
    # 调拨人员信息
    transfer_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), comment='调拨人ID')
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), comment='部门ID')
    
    # 单据状态
    status = Column(String(20), default='draft', comment='单据状态')  # draft/confirmed/in_transit/completed/cancelled
    
    # 审核信息
    approval_status = Column(String(20), default='pending', comment='审核状态')  # pending/approved/rejected
    approved_by = Column(UUID(as_uuid=True), comment='审核人')
    approved_at = Column(DateTime, comment='审核时间')
    
    # 执行信息
    executed_by = Column(UUID(as_uuid=True), comment='执行人')
    executed_at = Column(DateTime, comment='执行时间')
    
    # 业务关联
    source_document_type = Column(String(50), comment='来源单据类型')  # requisition/production/manual
    source_document_id = Column(UUID(as_uuid=True), comment='来源单据ID')
    source_document_number = Column(String(100), comment='来源单据号')
    
    # 统计信息
    total_items = Column(Integer, default=0, comment='总条目数')
    total_quantity = Column(Numeric(15, 3), default=0, comment='总数量')
    total_amount = Column(Numeric(18, 4), default=0, comment='总金额')
    
    # 物流信息
    transporter = Column(String(200), comment='承运人')
    transport_method = Column(String(50), comment='运输方式')  # manual/vehicle/logistics
    expected_arrival_date = Column(DateTime, comment='预计到达时间')
    actual_arrival_date = Column(DateTime, comment='实际到达时间')
    
    # 扩展字段
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    details = relationship("MaterialTransferOrderDetail", back_populates="transfer_order", cascade="all, delete-orphan")
    transfer_person = relationship("Employee", foreign_keys=[transfer_person_id], lazy='select')
    department = relationship("Department", foreign_keys=[department_id], lazy='select')
    
    # 调拨类型常量
    TRANSFER_TYPES = [
        ('warehouse', '仓库调拨'),
        ('department', '部门调拨'),
        ('project', '项目调拨'),
        ('emergency', '紧急调拨')
    ]
    
    # 状态常量
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('in_transit', '运输中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已审核'),
        ('rejected', '已拒绝')
    ]
    
    TRANSPORT_METHODS = [
        ('manual', '人工搬运'),
        ('vehicle', '车辆运输'),
        ('logistics', '物流配送'),
        ('pipeline', '管道输送')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_material_transfer_order_number', 'transfer_number'),
        Index('ix_material_transfer_order_from_warehouse', 'from_warehouse_id'),
        Index('ix_material_transfer_order_to_warehouse', 'to_warehouse_id'),
        Index('ix_material_transfer_order_person', 'transfer_person_id'),
        Index('ix_material_transfer_order_department', 'department_id'),
        Index('ix_material_transfer_order_date', 'transfer_date'),
        Index('ix_material_transfer_order_status', 'status'),
    )
    
    def __init__(self, from_warehouse_id, to_warehouse_id, transfer_type, created_by, **kwargs):
        """
        初始化材料调拨单
        """
        self.from_warehouse_id = from_warehouse_id
        self.to_warehouse_id = to_warehouse_id
        self.transfer_type = transfer_type
        self.created_by = created_by
        
        # 生成调拨单号
        if not kwargs.get('transfer_number'):
            self.transfer_number = self.generate_transfer_number()
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def generate_transfer_number():
        """
        生成调拨单号 - 按顺序生成
        """
        from datetime import datetime
        from sqlalchemy import func, text
        from app.extensions import db
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 查询当天的最大序号
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取当天的最大序号
        # 获取当天的最大序号 - 修复查询语法
        try:
            max_order = db.session.query(func.max(
                func.cast(func.substring(MaterialTransferOrder.transfer_number, -4), func.Integer)
            )).filter(
                MaterialTransferOrder.created_at >= today_start,
                MaterialTransferOrder.created_at <= today_end
            ).scalar()
        except Exception as e:
            # 如果查询失败，使用简单的计数方法
            count = db.session.query(MaterialTransferOrder).filter(
                MaterialTransferOrder.created_at >= today_start,
                MaterialTransferOrder.created_at <= today_end
            ).count()
            max_order = count
        
        # 序号从1开始，如果没有记录则为0，所以下一个序号为max_order + 1
        next_sequence = (max_order or 0) + 1
        
        # 格式化为4位数字，不足补0
        sequence_str = f"{next_sequence:04d}"
        
        return f"DB{timestamp}{sequence_str}"
    
    def calculate_totals(self):
        """
        计算总计信息
        """
        if self.details:
            self.total_items = len(self.details)
            self.total_quantity = sum(detail.transfer_quantity for detail in self.details)
            self.total_amount = sum(detail.total_amount or 0 for detail in self.details)
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'transfer_number': self.transfer_number,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'transfer_type': self.transfer_type,
            'from_warehouse_id': str(self.from_warehouse_id),
            'from_warehouse_name': self.from_warehouse_name,
            'from_warehouse_code': self.from_warehouse_code,
            'to_warehouse_id': str(self.to_warehouse_id),
            'to_warehouse_name': self.to_warehouse_name,
            'to_warehouse_code': self.to_warehouse_code,
            'transfer_person_id': str(self.transfer_person_id) if self.transfer_person_id else None,
            'transfer_person': self.transfer_person.employee_name if self.transfer_person else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'department': self.department.dept_name if self.department else None,
            'status': self.status,
            'approval_status': self.approval_status,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'executed_by': str(self.executed_by) if self.executed_by else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'source_document_type': self.source_document_type,
            'source_document_number': self.source_document_number,
            'total_items': self.total_items,
            'total_quantity': float(self.total_quantity) if self.total_quantity else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'transporter': self.transporter,
            'transport_method': self.transport_method,
            'expected_arrival_date': self.expected_arrival_date.isoformat() if self.expected_arrival_date else None,
            'actual_arrival_date': self.actual_arrival_date.isoformat() if self.actual_arrival_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<MaterialTransferOrder {self.transfer_number}>'


class MaterialTransferOrderDetail(TenantModel):
    """
    材料调拨单明细表
    """
    
    __tablename__ = 'material_transfer_order_details'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联主表
    transfer_order_id = Column(UUID(as_uuid=True), ForeignKey('material_transfer_orders.id'), nullable=False, comment='调拨单ID')
    
    # 材料信息
    material_id = Column(UUID(as_uuid=True), nullable=False, comment='材料ID')
    material_name = Column(String(200), nullable=False, comment='材料名称')
    material_code = Column(String(100), comment='材料编码')
    material_spec = Column(String(500), comment='材料规格')
    
    # 库存信息
    from_inventory_id = Column(UUID(as_uuid=True), comment='调出库存ID')
    current_stock = Column(Numeric(15, 3), comment='当前库存数量')
    available_quantity = Column(Numeric(15, 3), comment='可用库存数量')
    
    # 调拨数量信息
    transfer_quantity = Column(Numeric(15, 3), nullable=False, default=0, comment='调拨数量')
    actual_transfer_quantity = Column(Numeric(15, 3), comment='实际调拨数量')
    received_quantity = Column(Numeric(15, 3), comment='已收货数量')
    
    # 单位信息
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='基本单位ID')
    
    # 批次信息
    batch_number = Column(String(100), comment='批次号')
    production_date = Column(DateTime, comment='生产日期')
    expiry_date = Column(DateTime, comment='到期日期')
    
    # 成本信息
    unit_price = Column(Numeric(15, 4), comment='单价')
    total_amount = Column(Numeric(18, 4), comment='总金额')
    
    # 库位信息
    from_location_code = Column(String(100), comment='调出库位')
    to_location_code = Column(String(100), comment='建议入库位')
    actual_to_location_code = Column(String(100), comment='实际入库位')
    
    # 质量信息
    quality_status = Column(String(20), default='qualified', comment='质量状态')  # qualified/unqualified/pending
    quality_certificate = Column(String(200), comment='质检证书')
    
    # 状态
    detail_status = Column(String(20), default='pending', comment='明细状态')  # pending/confirmed/in_transit/received/cancelled
    
    # 行号和排序
    line_number = Column(Integer, comment='行号')
    sort_order = Column(Integer, default=0, comment='排序')
    
    # 扩展字段
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    transfer_order = relationship("MaterialTransferOrder", back_populates="details")
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')
    
    # 状态常量
    DETAIL_STATUS_CHOICES = [
        ('pending', '待调拨'),
        ('confirmed', '已确认'),
        ('in_transit', '运输中'),
        ('received', '已收货'),
        ('cancelled', '已取消')
    ]
    
    QUALITY_STATUS_CHOICES = [
        ('qualified', '合格'),
        ('unqualified', '不合格'),
        ('pending', '待检')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_material_transfer_detail_order', 'transfer_order_id'),
        Index('ix_material_transfer_detail_material', 'material_id'),
        Index('ix_material_transfer_detail_status', 'detail_status'),
    )
    
    def __init__(self, transfer_order_id, material_id, material_name, unit_id, transfer_quantity, created_by, **kwargs):
        """
        初始化材料调拨明细
        """
        self.transfer_order_id = transfer_order_id
        self.material_id = material_id
        self.material_name = material_name
        self.unit_id = unit_id
        self.transfer_quantity = transfer_quantity
        self.created_by = created_by
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_total_amount(self):
        """
        计算总金额
        """
        if self.unit_price and self.transfer_quantity:
            self.total_amount = self.unit_price * self.transfer_quantity
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'transfer_order_id': str(self.transfer_order_id),
            'material_id': str(self.material_id),
            'material_name': self.material_name,
            'material_code': self.material_code,
            'material_spec': self.material_spec,
            'from_inventory_id': str(self.from_inventory_id) if self.from_inventory_id else None,
            'current_stock': float(self.current_stock) if self.current_stock else 0,
            'available_quantity': float(self.available_quantity) if self.available_quantity else 0,
            'transfer_quantity': float(self.transfer_quantity),
            'actual_transfer_quantity': float(self.actual_transfer_quantity) if self.actual_transfer_quantity else None,
            'received_quantity': float(self.received_quantity) if self.received_quantity else None,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit_name': self.unit.unit_name if self.unit else None,
            'batch_number': self.batch_number,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'from_location_code': self.from_location_code,
            'to_location_code': self.to_location_code,
            'actual_to_location_code': self.actual_to_location_code,
            'quality_status': self.quality_status,
            'quality_certificate': self.quality_certificate,
            'detail_status': self.detail_status,
            'line_number': self.line_number,
            'sort_order': self.sort_order,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<MaterialTransferOrderDetail {self.material_name} {self.transfer_quantity}{self.unit_id}>'


# 在文件末尾添加成品盘点功能

class ProductCountPlan(TenantModel):
    """
    成品盘点计划表
    """
    
    __tablename__ = 'product_count_plans'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 盘点基本信息
    count_number = Column(String(100), unique=True, nullable=False, comment='盘点单号')
    warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='仓库ID')
    warehouse_name = Column(String(200), nullable=False, comment='仓库名称')
    warehouse_code = Column(String(100), comment='仓库编号')
    
    # 盘点人员信息 - 改为外键关联
    count_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True, comment='盘点人ID')
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), comment='部门ID')
    
    # 盘点时间
    count_date = Column(DateTime, nullable=False, comment='发生日期')
    
    # 盘点状态
    status = Column(String(20), default='draft', comment='状态')  # draft/in_progress/completed
    
    # 备注
    notes = Column(Text, comment='备注')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    count_records = relationship("ProductCountRecord", back_populates="count_plan", cascade="all, delete-orphan")
    count_person = relationship("Employee", foreign_keys=[count_person_id], lazy='select')
    department = relationship("Department", foreign_keys=[department_id], lazy='select')
    
    # 状态常量
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('adjusted', '已调整')
    ]
    
    # 索引
    __table_args__ = (
        Index('idx_product_count_plans_warehouse', 'warehouse_id'),
        Index('idx_product_count_plans_count_date', 'count_date'),
        Index('idx_product_count_plans_status', 'status'),
        {'schema': None}  # 使用租户模式
    )
    
    def __init__(self, warehouse_id, warehouse_name, count_person_id, count_date, created_by, **kwargs):
        self.warehouse_id = warehouse_id
        self.warehouse_name = warehouse_name
        self.count_person_id = count_person_id
        self.count_date = count_date
        self.created_by = created_by
        
        # 生成盘点单号
        self.count_number = self.generate_count_number()
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def generate_count_number():
        """生成盘点单号 格式：PD + YYYYMMDD + 3位序号"""
        from datetime import datetime
        from app.extensions import db
        from sqlalchemy import func
        
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        
        # 查询当天已有的盘点单数量
        count = db.session.query(func.count(ProductCountPlan.id)).filter(
            func.date(ProductCountPlan.created_at) == today.date()
        ).scalar() or 0
        
        sequence = str(count + 1).zfill(3)
        return f'PD{date_str}{sequence}'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'count_number': self.count_number,
            'warehouse_id': str(self.warehouse_id),
            'warehouse_name': self.warehouse_name,
            'warehouse_code': self.warehouse_code,
            'count_person_id': str(self.count_person_id) if self.count_person_id else None,
            'count_person_name': self.count_person.employee_name if self.count_person else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'department_name': self.department.dept_name if self.department else None,
            'count_date': self.count_date.isoformat() if self.count_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ProductCountPlan {self.count_number}>'


class ProductCountRecord(TenantModel):
    """
    成品盘点记录表
    """
    
    __tablename__ = 'product_count_records'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联盘点计划
    count_plan_id = Column(UUID(as_uuid=True), ForeignKey('product_count_plans.id'), nullable=False, comment='盘点计划ID')
    
    # 关联库存
    inventory_id = Column(UUID(as_uuid=True), comment='库存ID')
    product_id = Column(UUID(as_uuid=True), nullable=False, comment='产品ID')
    
    # 产品信息
    product_code = Column(String(100), comment='产品编码')
    product_name = Column(String(200), nullable=False, comment='产品名称')
    product_spec = Column(String(200), comment='产品规格')
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='基本单位ID')
    
    # 盘点数据
    book_quantity = Column(Numeric(15, 3), nullable=False, default=0, comment='账面数量')
    actual_quantity = Column(Numeric(15, 3), comment='实盘数量')
    variance_quantity = Column(Numeric(15, 3), comment='差异数量')
    variance_rate = Column(Numeric(8, 4), comment='差异率%')
    
    # 批次和位置信息
    batch_number = Column(String(100), comment='批次号')
    production_date = Column(DateTime, comment='生产日期')
    expiry_date = Column(DateTime, comment='到期日期')
    location_code = Column(String(100), comment='库位')
    
    # 产品特有字段
    customer_id = Column(UUID(as_uuid=True), comment='客户ID')
    customer_name = Column(String(200), comment='客户名称')
    bag_type_id = Column(UUID(as_uuid=True), comment='袋型ID')
    bag_type_name = Column(String(100), comment='袋型名称')
    
    # 包装信息
    package_unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), comment='包装单位ID')
    package_quantity = Column(Numeric(15, 3), comment='包装数量')
    net_weight = Column(Numeric(10, 3), comment='净重(kg)')
    gross_weight = Column(Numeric(10, 3), comment='毛重(kg)')
    
    # 差异处理
    variance_reason = Column(String(500), comment='差异原因')
    is_adjusted = Column(Boolean, default=False, comment='是否已调整')
    
    # 状态
    status = Column(String(20), default='pending', comment='状态')  # pending/counted/adjusted
    
    # 备注
    notes = Column(Text, comment='备注')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    count_plan = relationship("ProductCountPlan", back_populates="count_records")
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')
    package_unit = relationship("Unit", foreign_keys=[package_unit_id], lazy='select')
    
    # 状态常量
    STATUS_CHOICES = [
        ('pending', '待盘点'),
        ('counted', '已盘点'),
        ('adjusted', '已调整')
    ]
    
    # 索引
    __table_args__ = (
        Index('idx_product_count_records_count_plan', 'count_plan_id'),
        Index('idx_product_count_records_product', 'product_id'),
        Index('idx_product_count_records_status', 'status'),
        {'schema': None}  # 使用租户模式
    )
    
    def __init__(self, count_plan_id, product_id, product_name, unit_id, book_quantity, created_by, **kwargs):
        self.count_plan_id = count_plan_id
        self.product_id = product_id
        self.product_name = product_name
        self.unit_id = unit_id
        self.book_quantity = book_quantity
        self.created_by = created_by
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_variance(self):
        """计算差异数量和差异率"""
        if self.actual_quantity is not None:
            self.variance_quantity = self.actual_quantity - self.book_quantity
            if self.book_quantity != 0:
                self.variance_rate = (self.variance_quantity / self.book_quantity) * 100
            else:
                self.variance_rate = 100.0 if self.actual_quantity > 0 else 0.0
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'count_plan_id': str(self.count_plan_id),
            'inventory_id': str(self.inventory_id) if self.inventory_id else None,
            'product_id': str(self.product_id),
            'product_code': self.product_code,
            'product_name': self.product_name,
            'product_spec': self.product_spec,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit_name': self.unit.unit_name if self.unit else None,
            'book_quantity': float(self.book_quantity) if self.book_quantity else 0,
            'actual_quantity': float(self.actual_quantity) if self.actual_quantity else None,
            'variance_quantity': float(self.variance_quantity) if self.variance_quantity else None,
            'variance_rate': float(self.variance_rate) if self.variance_rate else None,
            'batch_number': self.batch_number,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'location_code': self.location_code,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'customer_name': self.customer_name,
            'bag_type_id': str(self.bag_type_id) if self.bag_type_id else None,
            'bag_type_name': self.bag_type_name,
            'package_unit_id': str(self.package_unit_id) if self.package_unit_id else None,
            'package_unit_name': self.package_unit.unit_name if self.package_unit else None,
            'package_quantity': float(self.package_quantity) if self.package_quantity else None,
            'net_weight': float(self.net_weight) if self.net_weight else None,
            'gross_weight': float(self.gross_weight) if self.gross_weight else None,
            'variance_reason': self.variance_reason,
            'is_adjusted': self.is_adjusted,
            'status': self.status,
            'notes': self.notes,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ProductCountRecord {self.product_name} Qty:{self.book_quantity}>'


class ProductTransferOrder(TenantModel):
    """
    成品调拨单主表
    """
    
    __tablename__ = 'product_transfer_orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 单据信息
    transfer_number = Column(String(100), unique=True, nullable=False, comment='调拨单号')
    transfer_date = Column(DateTime, default=func.now(), nullable=False, comment='发生日期')
    transfer_type = Column(String(20), default='warehouse', comment='调拨类型')  # warehouse/department/project
    
    # 调出信息
    from_warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='调出仓库ID')
    from_warehouse_name = Column(String(200), comment='调出仓库名称')
    from_warehouse_code = Column(String(100), comment='调出仓库编码')
    
    # 调入信息
    to_warehouse_id = Column(UUID(as_uuid=True), nullable=False, comment='调入仓库ID')
    to_warehouse_name = Column(String(200), comment='调入仓库名称')
    to_warehouse_code = Column(String(100), comment='调入仓库编码')
    
    # 调拨人员信息
    transfer_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), comment='调拨人ID')
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), comment='部门ID')
    
    # 单据状态
    status = Column(String(20), default='draft', comment='单据状态')  # draft/confirmed/in_transit/completed/cancelled
    
    # 审核信息
    approval_status = Column(String(20), default='pending', comment='审核状态')  # pending/approved/rejected
    approved_by = Column(UUID(as_uuid=True), comment='审核人')
    approved_at = Column(DateTime, comment='审核时间')
    
    # 执行信息
    executed_by = Column(UUID(as_uuid=True), comment='执行人')
    executed_at = Column(DateTime, comment='执行时间')
    
    # 业务关联
    source_document_type = Column(String(50), comment='来源单据类型')  # sales_order/production/manual
    source_document_id = Column(UUID(as_uuid=True), comment='来源单据ID')
    source_document_number = Column(String(100), comment='来源单据号')
    
    # 统计信息
    total_items = Column(Integer, default=0, comment='总条目数')
    total_quantity = Column(Numeric(15, 3), default=0, comment='总数量')
    total_amount = Column(Numeric(18, 4), default=0, comment='总金额')
    
    # 物流信息
    transporter = Column(String(200), comment='承运人')
    transport_method = Column(String(50), comment='运输方式')  # manual/vehicle/logistics
    expected_arrival_date = Column(DateTime, comment='预计到达时间')
    actual_arrival_date = Column(DateTime, comment='实际到达时间')
    
    # 扩展字段
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    details = relationship("ProductTransferOrderDetail", back_populates="transfer_order", cascade="all, delete-orphan")
    transfer_person = relationship("Employee", foreign_keys=[transfer_person_id], lazy='select')
    department = relationship("Department", foreign_keys=[department_id], lazy='select')
    
    # 调拨类型常量
    TRANSFER_TYPES = [
        ('warehouse', '仓库调拨'),
        ('department', '部门调拨'),
        ('project', '项目调拨'),
        ('emergency', '紧急调拨')
    ]
    
    # 状态常量
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('in_transit', '运输中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已审核'),
        ('rejected', '已拒绝')
    ]
    
    TRANSPORT_METHODS = [
        ('manual', '人工搬运'),
        ('vehicle', '车辆运输'),
        ('logistics', '物流配送'),
        ('forklift', '叉车运输')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_product_transfer_order_number', 'transfer_number'),
        Index('ix_product_transfer_order_from_warehouse', 'from_warehouse_id'),
        Index('ix_product_transfer_order_to_warehouse', 'to_warehouse_id'),
        Index('ix_product_transfer_order_person', 'transfer_person_id'),
        Index('ix_product_transfer_order_department', 'department_id'),
        Index('ix_product_transfer_order_date', 'transfer_date'),
        Index('ix_product_transfer_order_status', 'status'),
    )
    
    def __init__(self, from_warehouse_id, to_warehouse_id, transfer_type, created_by, **kwargs):
        """
        初始化成品调拨单
        """
        self.from_warehouse_id = from_warehouse_id
        self.to_warehouse_id = to_warehouse_id
        self.transfer_type = transfer_type
        self.created_by = created_by
        
        # 生成调拨单号
        if not kwargs.get('transfer_number'):
            self.transfer_number = self.generate_transfer_number()
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def generate_transfer_number():
        """
        生成调拨单号 - 按顺序生成
        """
        from datetime import datetime
        from sqlalchemy import func, text
        from app.extensions import db
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 查询当天的最大序号
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取当天的最大序号
        # 获取当天的最大序号 - 修复查询语法
        try:
            max_order = db.session.query(func.max(
                func.cast(func.substring(ProductTransferOrder.transfer_number, -4), func.Integer)
            )).filter(
                ProductTransferOrder.created_at >= today_start,
                ProductTransferOrder.created_at <= today_end
            ).scalar()
        except Exception as e:
            # 如果查询失败，使用简单的计数方法
            count = db.session.query(ProductTransferOrder).filter(
                ProductTransferOrder.created_at >= today_start,
                ProductTransferOrder.created_at <= today_end
            ).count()
            max_order = count
        
        # 序号从1开始，如果没有记录则为0，所以下一个序号为max_order + 1
        next_sequence = (max_order or 0) + 1
        
        # 格式化为4位数字，不足补0
        sequence_str = f"{next_sequence:04d}"
        
        return f"PT{timestamp}{sequence_str}"
    
    def calculate_totals(self):
        """
        计算总计信息
        """
        if self.details:
            self.total_items = len(self.details)
            self.total_quantity = sum(detail.transfer_quantity for detail in self.details)
            self.total_amount = sum(detail.total_amount or 0 for detail in self.details)
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'transfer_number': self.transfer_number,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'transfer_type': self.transfer_type,
            'from_warehouse_id': str(self.from_warehouse_id),
            'from_warehouse_name': self.from_warehouse_name,
            'from_warehouse_code': self.from_warehouse_code,
            'to_warehouse_id': str(self.to_warehouse_id),
            'to_warehouse_name': self.to_warehouse_name,
            'to_warehouse_code': self.to_warehouse_code,
            'transfer_person_id': str(self.transfer_person_id) if self.transfer_person_id else None,
            'transfer_person': self.transfer_person.employee_name if self.transfer_person else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'department': self.department.dept_name if self.department else None,
            'status': self.status,
            'approval_status': self.approval_status,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'executed_by': str(self.executed_by) if self.executed_by else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'source_document_type': self.source_document_type,
            'source_document_number': self.source_document_number,
            'total_items': self.total_items,
            'total_quantity': float(self.total_quantity) if self.total_quantity else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'transporter': self.transporter,
            'transport_method': self.transport_method,
            'expected_arrival_date': self.expected_arrival_date.isoformat() if self.expected_arrival_date else None,
            'actual_arrival_date': self.actual_arrival_date.isoformat() if self.actual_arrival_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ProductTransferOrder {self.transfer_number}>'


class ProductTransferOrderDetail(TenantModel):
    """
    成品调拨单明细表
    """
    
    __tablename__ = 'product_transfer_order_details'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联主表
    transfer_order_id = Column(UUID(as_uuid=True), ForeignKey('product_transfer_orders.id'), nullable=False, comment='调拨单ID')
    
    # 产品信息
    product_id = Column(UUID(as_uuid=True), nullable=False, comment='产品ID')
    product_name = Column(String(200), nullable=False, comment='产品名称')
    product_code = Column(String(100), comment='产品编码')
    product_spec = Column(String(500), comment='产品规格')
    
    # 库存信息
    from_inventory_id = Column(UUID(as_uuid=True), comment='调出库存ID')
    current_stock = Column(Numeric(15, 3), comment='当前库存数量')
    available_quantity = Column(Numeric(15, 3), comment='可用库存数量')
    
    # 调拨数量信息
    transfer_quantity = Column(Numeric(15, 3), nullable=False, default=0, comment='调拨数量')
    actual_transfer_quantity = Column(Numeric(15, 3), comment='实际调拨数量')
    received_quantity = Column(Numeric(15, 3), comment='已收货数量')
    
    # 单位信息
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False, comment='基本单位ID')
    weight_unit = Column(String(20), default='kg', comment='重量单位')
    length_unit = Column(String(20), default='m', comment='长度单位')
    
    # 批次信息
    batch_number = Column(String(100), comment='批次号')
    production_date = Column(DateTime, comment='生产日期')
    expiry_date = Column(DateTime, comment='到期日期')
    
    # 成本信息
    unit_cost = Column(Numeric(15, 4), comment='单位成本')
    total_amount = Column(Numeric(18, 4), comment='总金额')
    
    # 库位信息
    from_location_code = Column(String(100), comment='调出库位')
    to_location_code = Column(String(100), comment='建议入库位')
    actual_to_location_code = Column(String(100), comment='实际入库位')
    
    # 质量信息
    quality_status = Column(String(20), default='qualified', comment='质量状态')  # qualified/unqualified/pending
    quality_certificate = Column(String(200), comment='质检证书')
    
    # 产品特有字段
    customer_id = Column(UUID(as_uuid=True), comment='客户ID')
    customer_name = Column(String(200), comment='客户名称')
    bag_type_id = Column(UUID(as_uuid=True), comment='袋型ID')
    bag_type_name = Column(String(100), comment='袋型名称')
    
    # 包装信息
    package_unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), comment='包装单位ID')
    package_quantity = Column(Numeric(15, 3), comment='包装数量')
    net_weight = Column(Numeric(10, 3), comment='净重(kg)')
    gross_weight = Column(Numeric(10, 3), comment='毛重(kg)')
    
    # 状态
    detail_status = Column(String(20), default='pending', comment='明细状态')  # pending/confirmed/in_transit/received/cancelled
    
    # 行号和排序
    line_number = Column(Integer, comment='行号')
    sort_order = Column(Integer, default=0, comment='排序')
    
    # 扩展字段
    notes = Column(Text, comment='备注')
    custom_fields = Column(JSONB, default={}, comment='自定义字段')
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), nullable=False, comment='创建人')
    updated_by = Column(UUID(as_uuid=True), comment='更新人')
    
    # 关联关系
    transfer_order = relationship("ProductTransferOrder", back_populates="details")
    unit = relationship("Unit", foreign_keys=[unit_id], lazy='select')
    package_unit = relationship("Unit", foreign_keys=[package_unit_id], lazy='select')
    # 状态常量
    DETAIL_STATUS_CHOICES = [
        ('pending', '待调拨'),
        ('confirmed', '已确认'),
        ('in_transit', '运输中'),
        ('received', '已收货'),
        ('cancelled', '已取消')
    ]
    
    QUALITY_STATUS_CHOICES = [
        ('qualified', '合格'),
        ('unqualified', '不合格'),
        ('pending', '待检')
    ]
    
    # 索引
    __table_args__ = (
        Index('ix_product_transfer_detail_order', 'transfer_order_id'),
        Index('ix_product_transfer_detail_product', 'product_id'),
        Index('ix_product_transfer_detail_inventory', 'from_inventory_id'),
        Index('ix_product_transfer_detail_status', 'detail_status'),
    )
    
    def __init__(self, transfer_order_id, product_id, product_name, unit_id, transfer_quantity, created_by, **kwargs):
        """
        初始化成品调拨单明细
        """
        self.transfer_order_id = transfer_order_id
        self.product_id = product_id
        self.product_name = product_name
        self.unit_id = unit_id
        self.transfer_quantity = transfer_quantity
        self.created_by = created_by
        
        # 设置其他可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_total_amount(self):
        """
        计算总金额
        """
        if self.unit_cost and self.transfer_quantity:
            self.total_amount = self.unit_cost * self.transfer_quantity
    
    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': str(self.id),
            'transfer_order_id': str(self.transfer_order_id),
            'product_id': str(self.product_id),
            'product_name': self.product_name,
            'product_code': self.product_code,
            'product_spec': self.product_spec,
            'from_inventory_id': str(self.from_inventory_id) if self.from_inventory_id else None,
            'current_stock': float(self.current_stock) if self.current_stock else 0,
            'available_quantity': float(self.available_quantity) if self.available_quantity else 0,
            'transfer_quantity': float(self.transfer_quantity),
            'actual_transfer_quantity': float(self.actual_transfer_quantity) if self.actual_transfer_quantity else None,
            'received_quantity': float(self.received_quantity) if self.received_quantity else 0,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'unit': self.unit.unit_name if self.unit else None,
            'unit_name': self.unit.unit_name if self.unit else None,  # 为了兼容性，同时提供 unit 和 unit_name
            'weight_unit': self.weight_unit,
            'length_unit': self.length_unit,
            'batch_number': self.batch_number,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'from_location_code': self.from_location_code,
            'to_location_code': self.to_location_code,
            'actual_to_location_code': self.actual_to_location_code,
            'quality_status': self.quality_status,
            'quality_certificate': self.quality_certificate,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'customer_name': self.customer_name,
            'bag_type_id': str(self.bag_type_id) if self.bag_type_id else None,
            'bag_type_name': self.bag_type_name,
            'package_unit_id': str(self.package_unit_id) if self.package_unit_id else None,
            'package_unit_name': self.package_unit.unit_name if self.package_unit else None,
            'package_quantity': float(self.package_quantity) if self.package_quantity else None,
            'net_weight': float(self.net_weight) if self.net_weight else None,
            'gross_weight': float(self.gross_weight) if self.gross_weight else None,
            'detail_status': self.detail_status,
            'line_number': self.line_number,
            'sort_order': self.sort_order,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ProductTransferOrderDetail {self.product_name}: {self.transfer_quantity}{self.unit_id}>'