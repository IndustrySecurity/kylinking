from sqlalchemy import Column, String, DateTime, Text, Numeric, Boolean, Integer, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import TenantModel
import uuid
from decimal import Decimal


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
    unit = Column(String(20), nullable=False, comment='单位')
    
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
    
    # 索引
    __table_args__ = (
        Index('ix_inventory_warehouse_product', 'warehouse_id', 'product_id'),
        Index('ix_inventory_warehouse_material', 'warehouse_id', 'material_id'),
        Index('ix_inventory_batch', 'batch_number'),
        Index('ix_inventory_location', 'warehouse_id', 'location_code'),
        Index('ix_inventory_status', 'inventory_status', 'quality_status'),
    )
    
    def __init__(self, warehouse_id, unit, created_by, product_id=None, material_id=None, 
                 current_quantity=0, available_quantity=0, **kwargs):
        """
        初始化库存记录
        """
        self.warehouse_id = warehouse_id
        self.product_id = product_id
        self.material_id = material_id
        self.current_quantity = current_quantity
        self.available_quantity = available_quantity
        self.unit = unit
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
            'unit': self.unit,
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
    unit = Column(String(20), nullable=False, comment='单位')
    
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
    
    # 索引
    __table_args__ = (
        Index('ix_inventory_transaction_inventory', 'inventory_id'),
        Index('ix_inventory_transaction_warehouse', 'warehouse_id'),
        Index('ix_inventory_transaction_type_date', 'transaction_type', 'transaction_date'),
        Index('ix_inventory_transaction_source', 'source_document_type', 'source_document_id'),
        Index('ix_inventory_transaction_number', 'transaction_number'),
        Index('ix_inventory_transaction_batch', 'batch_number'),
        Index('ix_inventory_transaction_status', 'approval_status', 'is_cancelled'),
    )
    
    def __init__(self, inventory_id, warehouse_id, transaction_type, quantity_change, 
                 quantity_before, quantity_after, unit, created_by, **kwargs):
        """
        初始化库存交易记录
        """
        self.inventory_id = inventory_id
        self.warehouse_id = warehouse_id
        self.transaction_type = transaction_type
        self.quantity_change = quantity_change
        self.quantity_before = quantity_before
        self.quantity_after = quantity_after
        self.unit = unit
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
        生成流水号
        """
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        import random
        random_suffix = str(random.randint(1000, 9999))
        return f"TXN{timestamp}{random_suffix}"
    
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
            'unit': self.unit,
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
        生成盘点计划号
        """
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d')
        import random
        random_suffix = str(random.randint(100, 999))
        return f"CNT{timestamp}{random_suffix}"
    
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
    unit = Column(String(20), nullable=False, comment='单位')
    
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
    
    # 状态常量
    STATUS_CHOICES = [
        ('pending', '待盘点'),
        ('counted', '已盘点'),
        ('recounted', '已复盘'),
        ('adjusted', '已调整')
    ]
    
    def __init__(self, count_plan_id, inventory_id, warehouse_id, book_quantity, unit, created_by, **kwargs):
        """
        初始化盘点记录
        """
        self.count_plan_id = count_plan_id
        self.inventory_id = inventory_id
        self.warehouse_id = warehouse_id
        self.book_quantity = book_quantity
        self.unit = unit
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
            'unit': self.unit,
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
    
    # 入库人员信息
    inbound_person = Column(String(100), comment='入库人')
    department = Column(String(100), comment='部门')
    
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
        生成入库单号
        """
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d')
        import random
        random_suffix = str(random.randint(1000, 9999))
        
        prefix_map = {
            'finished_goods': 'FIN',
            'raw_materials': 'RAW',
            'semi_finished': 'SEM',
            'other': 'OTH'
        }
        prefix = prefix_map.get(order_type, 'INB')
        
        return f"{prefix}{timestamp}{random_suffix}"
    
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
            'inbound_person': self.inbound_person,
            'department': self.department,
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
    unit = Column(String(20), nullable=False, comment='基本单位')
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
    
    def __init__(self, inbound_order_id, inbound_quantity, unit, created_by, **kwargs):
        """
        初始化入库单明细
        """
        self.inbound_order_id = inbound_order_id
        self.inbound_quantity = inbound_quantity
        self.unit = unit
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
            'inbound_kg_quantity': float(self.inbound_kg_quantity) if self.inbound_kg_quantity else None,
            'inbound_m_quantity': float(self.inbound_m_quantity) if self.inbound_m_quantity else None,
            'inbound_roll_quantity': float(self.inbound_roll_quantity) if self.inbound_roll_quantity else None,
            'box_quantity': float(self.box_quantity) if self.box_quantity else None,
            'case_quantity': self.case_quantity,
            'unit': self.unit,
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
            'line_number': self.line_number,
            'sort_order': self.sort_order,
            'notes': self.notes,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<InboundOrderDetail {self.product_name} Qty:{self.inbound_quantity}>' 