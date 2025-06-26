"""
销售相关模型
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import TenantModel
from app.extensions import db


class SalesOrder(TenantModel):
    """销售订单表"""
    __tablename__ = 'sales_orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    order_number = Column(String(50), nullable=False, comment='销售单号')  # 自动生成
    order_type = Column(String(20), default='normal', comment='订单类型')  # 正常订单/打样订单/查库订单/版费订单/加急订单/备货订单
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customer_management.id'), nullable=False, comment='客户ID')  # 外键
    customer_order_number = Column(String(100), comment='客户订单号')  # 手工输入
    contact_person_id = Column(UUID(as_uuid=True), comment='联系人ID')  # 外键，根据客户表选择
    tax_type_id = Column(UUID(as_uuid=True), comment='税收ID')  # 外键，根据税收表选择
    
    # 金额信息
    order_amount = Column(Numeric(15, 4), default=0, comment='订金')  # 手工输入，默认0
    deposit = Column(Numeric(15, 4), default=0, comment='订金')  # 手工输入，默认0
    plate_fee = Column(Numeric(15, 4), default=0, comment='版费订金')  # 手工输入，默认0
    plate_fee_percentage = Column(Numeric(5, 2), default=0, comment='版费订金%')  # 手工输入，默认0
    
    # 日期信息
    order_date = Column(DateTime, default=datetime.utcnow, comment='交货日期')  # 选择
    internal_delivery_date = Column(DateTime, comment='内部交期')  # 选择
    salesperson_id = Column(UUID(as_uuid=True), comment='业务员ID')  # 外键，根据选择的客户填入
    contract_date = Column(DateTime, comment='合同日期')  # 选择
    
    # 地址和物流信息
    delivery_address = Column(Text, comment='送货地址')  # 选择，根据选择的客户相关的子表选择
    logistics_info = Column(Text, comment='物流信息')  # 选择
    tracking_number = Column(String(100), comment='跟单员')  # 选择
    warehouse_id = Column(UUID(as_uuid=True), comment='归属公司')  # 选择
    
    # 生产和订单信息
    production_requirements = Column(Text, comment='生产要求')  # 手工输入
    order_requirements = Column(Text, comment='订单要求')  # 手工输入
    
    # 状态字段
    status = Column(String(20), default='draft', comment='订单状态')  # draft/confirmed/production/shipped/completed/cancelled
    is_active = Column(Boolean, default=True, comment='是否有效')
    
    # 关联关系
    customer = relationship("CustomerManagement", back_populates="sales_orders")
    order_details = relationship("SalesOrderDetail", back_populates="sales_order", cascade="all, delete-orphan")
    other_fees = relationship("SalesOrderOtherFee", back_populates="sales_order", cascade="all, delete-orphan")
    material_details = relationship("SalesOrderMaterial", back_populates="sales_order", cascade="all, delete-orphan")


class SalesOrderDetail(TenantModel):
    """销售明细子表"""
    __tablename__ = 'sales_order_details'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_order_id = Column(UUID(as_uuid=True), ForeignKey('sales_orders.id'), nullable=False, comment='销售订单ID')
    
    # 产品信息
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), comment='产品ID')  # 外键
    product_code = Column(String(50), comment='产品编号')  # 选择（是/否）手工输入
    product_name = Column(String(200), comment='产品名称')  # 选择
    
    # 规格信息
    negative_deviation_percentage = Column(Numeric(5, 2), comment='负偏差%')  # 手工输入
    positive_deviation_percentage = Column(Numeric(5, 2), comment='正偏差%')  # 手工输入
    production_small_quantity = Column(Numeric(15, 4), comment='生产最小数')  # 手工输入
    production_large_quantity = Column(Numeric(15, 4), comment='生产最大数')  # 手工输入
    order_quantity = Column(Numeric(15, 4), nullable=False, comment='订单数量')  # 手工输入
    sales_unit_id = Column(UUID(as_uuid=True), comment='销售单位ID')  # 自动，根据选择的产品自动填入
    
    # 价格信息（自动计算）
    unit_price = Column(Numeric(15, 4), comment='订单联数')  # 自动
    amount = Column(Numeric(15, 4), comment='订单数量单位')  # 自动
    unit = Column(String(20), comment='单位')  # 自动，根据选择的产品自动填入，支持修改
    estimated_thickness_m = Column(Numeric(10, 4), comment='预测厚M')  # 手工输入
    estimated_weight_kg = Column(Numeric(10, 4), comment='预测厚kg')  # 手工输入
    estimated_volume = Column(Numeric(10, 4), comment='预测厚数')  # 手工输入
    shipping_quantity = Column(Numeric(15, 4), comment='赠送数')  # 手工输入
    production_quantity = Column(Numeric(15, 4), comment='生产数')  # 手工输入
    
    # 库存和存储
    usable_inventory = Column(Numeric(15, 4), comment='可用库存')  # 手工输入
    insufficient_notice = Column(Text, comment='不足通知')  # 根据库存表选择
    storage_quantity = Column(Numeric(15, 4), comment='存库数')  # 手工输入
    
    # 税收信息
    tax_type_id = Column(UUID(as_uuid=True), comment='税收ID')  # 根据选择的产品自动填入
    currency_id = Column(UUID(as_uuid=True), comment='币种ID')  # 根据选择的产品自动填入
    material_structure = Column(Text, comment='材质结构')  # 自动
    customer_requirements = Column(Text, comment='客户要求')  # 自动
    storage_requirements = Column(Text, comment='存库要求')  # 自动
    customization_requirements = Column(Text, comment='客户化要求')  # 自动
    printing_requirements = Column(Text, comment='印刷要求')  # 自动
    outer_box = Column(String(100), comment='外箱')  # 自动
    
    # 外币信息
    foreign_currency_unit_price = Column(Numeric(15, 4), comment='外币单价')  # 手工输入
    foreign_currency_amount = Column(Numeric(15, 4), comment='外币金额')  # 手工输入
    foreign_currency_id = Column(UUID(as_uuid=True), comment='外币ID')  # 选择
    
    # 生产信息
    internal_delivery_date = Column(DateTime, comment='内部交期')  # 选择
    delivery_date = Column(DateTime, comment='交货日期')  # 选择
    customer_code = Column(String(100), comment='客户代号')  # 手工输入
    product_condition = Column(String(50), comment='产品条件')  # 选择
    color_count = Column(Integer, comment='色数')  # 自动
    bag_type_id = Column(UUID(as_uuid=True), comment='袋型ID')  # 自动
    material_structure_auto = Column(Text, comment='材质结构')  # 自动
    storage_requirements_auto = Column(Text, comment='存库要求')  # 自动
    storage_requirements_input = Column(Text, comment='存库要求')  # 自动
    printing_requirements_auto = Column(Text, comment='印刷要求')  # 自动
    
    # 测试信息
    estimated_thickness_count = Column(Numeric(10, 4), comment='预测厚计数')  # 自动
    packaging_count = Column(Numeric(10, 4), comment='包装计数')  # 自动
    
    # 尺寸信息
    square_meters_per_piece = Column(Numeric(10, 4), comment='平方米单价')  # 自动
    square_meters_count = Column(Numeric(10, 4), comment='平方米计数')  # 自动
    paper_tube_weight = Column(Numeric(10, 4), comment='纸管重量')  # 手工输入
    net_weight = Column(Numeric(10, 4), comment='地膜')  # 手工输入
    
    # 生产信息详细
    composite_area = Column(String(100), comment='复合条件')  # 选择（是/否）
    modified_condition = Column(String(100), comment='改版共计')  # 手工输入
    customer_specification = Column(Text, comment='客户规格')  # 手工输入
    
    # 颜色和印刷
    color_count_auto = Column(Integer, comment='色数')  # 自动
    packaging_type = Column(String(100), comment='包装')  # 自动
    material_structure_final = Column(Text, comment='材质结构')  # 自动
    storage_method = Column(String(100), comment='存库方式')  # 自动
    customization_requirements_final = Column(Text, comment='客户化要求')  # 自动
    printing_requirements_final = Column(Text, comment='印刷要求')  # 自动
    outer_box_final = Column(String(100), comment='外箱')  # 自动
    
    # 价格计算
    foreign_currency_unit_price_final = Column(Numeric(15, 4), comment='外币单价')  # 手工输入
    foreign_currency_amount_final = Column(Numeric(15, 4), comment='外币金额')  # 手工输入
    paper_weight = Column(Numeric(10, 4), comment='平方米')  # 手工输入
    other_info = Column(String(200), comment='其他')  # 手工输入
    
    # 客户信息
    customer_specification_final = Column(String(100), comment='客户规格')  # 选择（是/否）
    modification_date = Column(DateTime, comment='委托共计')  # 选择
    printing_requirements_input = Column(Text, comment='印刷要求')  # 手工输入
    composite_requirements = Column(Text, comment='复合要求')  # 手工输入
    estimated_bags_count = Column(Numeric(15, 4), comment='预测厚袋数')  # 自动
    packaging_weight = Column(Numeric(10, 4), comment='包装重量')  # 自动
    
    # 平方和存储
    square_meter_unit_price = Column(Numeric(15, 4), comment='平方米单价')  # 自动
    bag_count = Column(Numeric(15, 4), comment='袋数')  # 手工输入
    grade = Column(String(20), comment='等级')  # 选择
    company_price = Column(Numeric(15, 4), comment='公司价格')  # 手工输入
    customer_discount = Column(Numeric(5, 2), comment='客户折扣')  # 手工输入
    customer_discount_amount = Column(Numeric(15, 4), comment='客户折扣单价')  # 手工输入
    internal_period = Column(String(100), comment='内部期')  # 手工输入
    
    # 技术参数
    printing_detail = Column(String(100), comment='特殊条件')  # 手工输入
    sorting_number = Column(Integer, comment='排序')  # 手工输入
    assembly_coefficient = Column(Numeric(10, 4), comment='汇率')  # 手工输入
    affiliate_company_id = Column(UUID(as_uuid=True), comment='所属公司ID')  # 选择
    component_name = Column(String(200), comment='部件名称')  # 手工输入
    
    # 关联关系
    sales_order = relationship("SalesOrder", back_populates="order_details")
    product = relationship("Product")


class SalesOrderOtherFee(TenantModel):
    """其他费用子表"""
    __tablename__ = 'sales_order_other_fees'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_order_id = Column(UUID(as_uuid=True), ForeignKey('sales_orders.id'), nullable=False, comment='销售订单ID')
    
    # 费用信息
    fee_type = Column(String(50), comment='费用类型')  # 选择：版费/模具费/包装费/运费/其它/改版费/免版费
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), comment='产品ID')  # 选择
    product_name = Column(String(200), comment='产品名称')  # 选择
    
    # 尺寸信息
    length = Column(Numeric(10, 3), comment='版长')  # 手工输入
    width = Column(Numeric(10, 3), comment='版周')  # 手工输入
    customer_order_number = Column(String(100), comment='客户订单号')  # 手工输入
    customer_code = Column(String(100), comment='客户代号')  # 手工输入
    
    # 价格信息
    price = Column(Numeric(15, 4), comment='价格')  # 手工输入
    quantity = Column(Numeric(15, 4), comment='数量')  # 手工输入
    unit_id = Column(UUID(as_uuid=True), comment='单位ID')  # 选择，根据单位表选择，外键
    amount = Column(Numeric(15, 4), comment='金额')  # 自动
    tax_type_id = Column(UUID(as_uuid=True), comment='税收ID')  # 选择，根据税收表选择，外键
    untaxed_price = Column(Numeric(15, 4), comment='未税价格')  # 自动
    untaxed_amount = Column(Numeric(15, 4), comment='未税金额')  # 自动
    tax_amount = Column(Numeric(15, 4), comment='税额')  # 自动
    
    # 外币信息
    foreign_currency_unit_price = Column(Numeric(15, 4), comment='外币单价')  # 手工输入
    foreign_currency_amount = Column(Numeric(15, 4), comment='外币金额')  # 手工输入
    foreign_currency_id = Column(UUID(as_uuid=True), comment='外币ID')  # 手工输入
    
    # 日期信息
    delivery_date = Column(DateTime, comment='交货日期')  # 选择
    internal_delivery_date = Column(DateTime, comment='内部交期')  # 选择
    customer_requirements = Column(Text, comment='客户要求')  # 手工输入
    notes = Column(Text, comment='备注')  # 手工输入
    
    # 排序
    sort_order = Column(Integer, comment='排序')  # 手工输入
    income_quantity = Column(Numeric(15, 4), comment='入库数量')  # 手工输入
    completion_status = Column(String(50), comment='完工状态')  # 手工输入
    assembly_coefficient = Column(Numeric(10, 4), comment='汇率')  # 手工输入
    sales_material_batch_number = Column(String(100), comment='销售材料批号')  # 手工输入
    affiliate_company_id = Column(UUID(as_uuid=True), comment='所属公司ID')  # 手工输入
    material_note = Column(Text, comment='材料档案备注')  # 手工输入
    
    # 关联关系
    sales_order = relationship("SalesOrder", back_populates="other_fees")
    product = relationship("Product")


class SalesOrderMaterial(TenantModel):
    """销售材料子表"""
    __tablename__ = 'sales_order_materials'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_order_id = Column(UUID(as_uuid=True), ForeignKey('sales_orders.id'), nullable=False, comment='销售订单ID')
    
    # 材料信息
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=False, comment='材料ID')  # 根据材料表选择，外键
    negative_deviation_percentage = Column(Numeric(5, 2), comment='负偏差%')  # 手工输入
    positive_deviation_percentage = Column(Numeric(5, 2), comment='正偏差%')  # 手工输入
    gift_quantity = Column(Numeric(15, 4), comment='赠送数')  # 手工输入
    quantity = Column(Numeric(15, 4), nullable=False, comment='数量')  # 手工输入
    unit_id = Column(UUID(as_uuid=True), comment='单位ID')  # 自动
    auxiliary_quantity = Column(Numeric(15, 4), comment='辅助数')  # 手工输入
    auxiliary_unit_id = Column(UUID(as_uuid=True), comment='辅助单位ID')  # 自动
    
    # 价格信息
    changed_price_before = Column(Numeric(15, 4), comment='变更前价格')  # 手工输入
    price = Column(Numeric(15, 4), comment='价格')  # 自动
    amount = Column(Numeric(15, 4), comment='金额')  # 自动
    tax_type_id = Column(UUID(as_uuid=True), comment='税收ID')  # 根据税收表选择，外键
    sales_unit_id = Column(UUID(as_uuid=True), comment='销售单位ID')  # 选择
    untaxed_price = Column(Numeric(15, 4), comment='未税价格')  # 自动
    untaxed_amount = Column(Numeric(15, 4), comment='未税金额')  # 自动
    
    # 外币信息
    foreign_currency_unit_price = Column(Numeric(15, 4), comment='外币单价')  # 手工输入
    foreign_currency_amount = Column(Numeric(15, 4), comment='外币金额')  # 手工输入
    foreign_currency_id = Column(UUID(as_uuid=True), comment='外币ID')  # 手工输入
    
    # 日期信息
    delivery_date = Column(DateTime, comment='交货日期')  # 选择
    internal_delivery_date = Column(DateTime, comment='内部交期')  # 选择
    customer_requirements = Column(Text, comment='客户要求')  # 手工输入
    notes = Column(Text, comment='备注')  # 手工输入
    
    # 排序和其他信息
    sort_order = Column(Integer, comment='排序')  # 手工输入
    income_quantity = Column(Numeric(15, 4), comment='入库数量')  # 手工输入
    completion_status = Column(String(50), comment='完工状态')  # 手工输入
    assembly_coefficient = Column(Numeric(10, 4), comment='汇率')  # 手工输入
    sales_material_batch_number = Column(String(100), comment='销售材料批号')  # 手工输入
    affiliate_company_id = Column(UUID(as_uuid=True), comment='所属公司ID')  # 手工输入
    material_archive_note = Column(Text, comment='材料档案备注')  # 手工输入
    
    # 关联关系
    sales_order = relationship("SalesOrder", back_populates="material_details")
    material = relationship("Material") 