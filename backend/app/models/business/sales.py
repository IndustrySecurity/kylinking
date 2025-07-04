"""
销售相关模型
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text, ForeignKey, func
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
    order_date = Column(DateTime, default=func.now(), comment='交货日期')  # 选择
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
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), comment='创建人ID')
    updated_by = Column(UUID(as_uuid=True), comment='更新人ID')

    # 关联关系
    customer = relationship("CustomerManagement", back_populates="sales_orders")
    order_details = relationship("SalesOrderDetail", back_populates="sales_order", cascade="all, delete-orphan")
    other_fees = relationship("SalesOrderOtherFee", back_populates="sales_order", cascade="all, delete-orphan")
    material_details = relationship("SalesOrderMaterial", back_populates="sales_order", cascade="all, delete-orphan")
    delivery_notices = relationship("DeliveryNotice", back_populates="sales_order")

    def to_dict(self):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'order_number': self.order_number,
            'order_type': self.order_type,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'customer_order_number': self.customer_order_number,
            'contact_person_id': str(self.contact_person_id) if self.contact_person_id else None,
            'tax_type_id': str(self.tax_type_id) if self.tax_type_id else None,
            'order_amount': float(self.order_amount) if self.order_amount else 0,
            'deposit': float(self.deposit) if self.deposit else 0,
            'plate_fee': float(self.plate_fee) if self.plate_fee else 0,
            'plate_fee_percentage': float(self.plate_fee_percentage) if self.plate_fee_percentage else 0,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'internal_delivery_date': self.internal_delivery_date.isoformat() if self.internal_delivery_date else None,
            'salesperson_id': str(self.salesperson_id) if self.salesperson_id else None,
            'contract_date': self.contract_date.isoformat() if self.contract_date else None,
            'delivery_address': self.delivery_address,
            'logistics_info': self.logistics_info,
            'tracking_number': self.tracking_number,
            'warehouse_id': str(self.warehouse_id) if self.warehouse_id else None,
            'production_requirements': self.production_requirements,
            'order_requirements': self.order_requirements,
            'status': self.status,
            'is_active': self.is_active,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # 添加客户信息
        if hasattr(self, 'customer') and self.customer:
            result['customer'] = {
                'id': str(self.customer.id),
                'customer_name': self.customer.customer_name,
                'customer_code': self.customer.customer_code
            }
        
        # 添加联系人信息
        if self.contact_person_id:
            try:
                from app.models.basic_data import CustomerContact
                from app.extensions import db
                contact = db.session.query(CustomerContact).filter_by(id=self.contact_person_id).first()
                if contact:
                    result['contact_person'] = {
                        'id': str(contact.id),
                        'contact_name': getattr(contact, 'contact_name', '') or getattr(contact, 'name', ''),
                        'mobile': getattr(contact, 'mobile', '') or getattr(contact, 'landline', ''),
                        'phone': getattr(contact, 'mobile', '') or getattr(contact, 'landline', '')
                    }
                else:
                    result['contact_person'] = None
            except Exception as e:
                # 如果查询失败，设置为空
                result['contact_person'] = None
        
        # 添加税收信息
        if self.tax_type_id:
            try:
                from app.models.basic_data import TaxRate
                from app.extensions import db
                tax_rate = db.session.query(TaxRate).filter_by(id=self.tax_type_id).first()
                if tax_rate:
                    result['tax_name'] = tax_rate.tax_name
                    result['tax_rate'] = float(tax_rate.tax_rate) if tax_rate.tax_rate else 0
            except Exception:
                pass
        
        # 添加订单明细
        if hasattr(self, 'order_details'):
            result['order_details'] = [detail.to_dict() for detail in self.order_details]
        
        # 添加其他费用
        if hasattr(self, 'other_fees'):
            result['other_fees'] = [fee.to_dict() for fee in self.other_fees]
        
        # 添加材料明细
        if hasattr(self, 'material_details'):
            result['material_details'] = [material.to_dict() for material in self.material_details]
        
        return result

    @classmethod
    def generate_order_number(cls):
        """生成唯一销售单号（格式：SOYYMMDDXXXX，如SO2507030001表示2025年7月3日第1个订单）"""
        # 获取当前日期
        now = datetime.now()
        date_part = now.strftime('%y%m%d')  # 如250703表示2025年7月3日
        
        # 查询当天最大单号
        max_order = db.session.query(cls.order_number).filter(
            cls.order_number.like(f'SO{date_part}%')
        ).order_by(cls.order_number.desc()).first()
        
        # 计算新单号
        if max_order and max_order[0]:
            try:
                # 提取序号部分并加1
                current_sequence = int(max_order[0][8:])  # 从第9位开始的数字部分
                new_sequence = current_sequence + 1
            except (ValueError, IndexError):
                # 处理异常情况，默认从1开始
                new_sequence = 1
        else:
            # 当天无记录，从0001开始
            new_sequence = 1
        
        # 格式化新单号（如SO2507030001）
        return f"SO{date_part}{new_sequence:04d}"


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
    scheduled_delivery_quantity = Column(Numeric(15, 4), default=0, comment='已安排送货数')  # 新增字段
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
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), comment='创建人ID')
    updated_by = Column(UUID(as_uuid=True), comment='更新人ID')

    # 关联关系
    sales_order = relationship("SalesOrder", back_populates="order_details")
    product = relationship("Product")

    def to_dict(self):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'sales_order_id': str(self.sales_order_id),
            'product_id': str(self.product_id) if self.product_id else None,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'negative_deviation_percentage': float(self.negative_deviation_percentage) if self.negative_deviation_percentage else None,
            'positive_deviation_percentage': float(self.positive_deviation_percentage) if self.positive_deviation_percentage else None,
            'production_small_quantity': float(self.production_small_quantity) if self.production_small_quantity else None,
            'production_large_quantity': float(self.production_large_quantity) if self.production_large_quantity else None,
            'order_quantity': float(self.order_quantity) if self.order_quantity else None,
            'scheduled_delivery_quantity': float(self.scheduled_delivery_quantity) if self.scheduled_delivery_quantity else 0,
            'sales_unit_id': str(self.sales_unit_id) if self.sales_unit_id else None,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'amount': float(self.amount) if self.amount else None,
            'unit': self.unit,
            'estimated_thickness_m': float(self.estimated_thickness_m) if self.estimated_thickness_m else None,
            'estimated_weight_kg': float(self.estimated_weight_kg) if self.estimated_weight_kg else None,
            'estimated_volume': float(self.estimated_volume) if self.estimated_volume else None,
            'shipping_quantity': float(self.shipping_quantity) if self.shipping_quantity else None,
            'production_quantity': float(self.production_quantity) if self.production_quantity else None,
            'usable_inventory': float(self.usable_inventory) if self.usable_inventory else None,
            'insufficient_notice': self.insufficient_notice,
            'storage_quantity': float(self.storage_quantity) if self.storage_quantity else None,
            'tax_type_id': str(self.tax_type_id) if self.tax_type_id else None,
            'currency_id': str(self.currency_id) if self.currency_id else None,
            'material_structure': self.material_structure,
            'customer_requirements': self.customer_requirements,
            'storage_requirements': self.storage_requirements,
            'customization_requirements': self.customization_requirements,
            'printing_requirements': self.printing_requirements,
            'outer_box': self.outer_box,
            'foreign_currency_unit_price': float(self.foreign_currency_unit_price) if self.foreign_currency_unit_price else None,
            'foreign_currency_amount': float(self.foreign_currency_amount) if self.foreign_currency_amount else None,
            'foreign_currency_id': str(self.foreign_currency_id) if self.foreign_currency_id else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'internal_delivery_date': self.internal_delivery_date.isoformat() if self.internal_delivery_date else None,
            'customer_code': self.customer_code,
            'product_condition': self.product_condition,
            'color_count': self.color_count,
            'bag_type_id': str(self.bag_type_id) if self.bag_type_id else None,
            'material_structure_auto': self.material_structure_auto,
            'storage_requirements_auto': self.storage_requirements_auto,
            'storage_requirements_input': self.storage_requirements_input,
            'printing_requirements_auto': self.printing_requirements_auto,
            'estimated_thickness_count': float(self.estimated_thickness_count) if self.estimated_thickness_count else None,
            'packaging_count': float(self.packaging_count) if self.packaging_count else None,
            'square_meters_per_piece': float(self.square_meters_per_piece) if self.square_meters_per_piece else None,
            'square_meters_count': float(self.square_meters_count) if self.square_meters_count else None,
            'paper_tube_weight': float(self.paper_tube_weight) if self.paper_tube_weight else None,
            'net_weight': float(self.net_weight) if self.net_weight else None,
            'composite_area': self.composite_area,
            'modified_condition': self.modified_condition,
            'customer_specification': self.customer_specification,
            'color_count_auto': self.color_count_auto,
            'packaging_type': self.packaging_type,
            'material_structure_final': self.material_structure_final,
            'storage_method': self.storage_method,
            'customization_requirements_final': self.customization_requirements_final,
            'printing_requirements_final': self.printing_requirements_final,
            'outer_box_final': self.outer_box_final,
            'foreign_currency_unit_price_final': float(self.foreign_currency_unit_price_final) if self.foreign_currency_unit_price_final else None,
            'foreign_currency_amount_final': float(self.foreign_currency_amount_final) if self.foreign_currency_amount_final else None,
            'paper_weight': float(self.paper_weight) if self.paper_weight else None,
            'other_info': self.other_info,
            'customer_specification_final': self.customer_specification_final,
            'modification_date': self.modification_date.isoformat() if self.modification_date else None,
            'printing_requirements_input': self.printing_requirements_input,
            'composite_requirements': self.composite_requirements,
            'estimated_bags_count': float(self.estimated_bags_count) if self.estimated_bags_count else None,
            'packaging_weight': float(self.packaging_weight) if self.packaging_weight else None,
            'square_meter_unit_price': float(self.square_meter_unit_price) if self.square_meter_unit_price else None,
            'bag_count': float(self.bag_count) if self.bag_count else None,
            'grade': self.grade,
            'company_price': float(self.company_price) if self.company_price else None,
            'customer_discount': float(self.customer_discount) if self.customer_discount else None,
            'customer_discount_amount': float(self.customer_discount_amount) if self.customer_discount_amount else None,
            'internal_period': self.internal_period,
            'printing_detail': self.printing_detail,
            'sorting_number': self.sorting_number,
            'assembly_coefficient': float(self.assembly_coefficient) if self.assembly_coefficient else None,
            'affiliate_company_id': str(self.affiliate_company_id) if self.affiliate_company_id else None,
            'component_name': self.component_name,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # 添加产品信息
        if hasattr(self, 'product') and self.product:
            result['product'] = {
                'id': str(self.product.id),
                'product_code': self.product.product_code,
                'product_name': self.product.product_name
            }
        
        return result


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
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), comment='创建人ID')
    updated_by = Column(UUID(as_uuid=True), comment='更新人ID')

    # 关联关系
    sales_order = relationship("SalesOrder", back_populates="other_fees")
    product = relationship("Product")

    def to_dict(self):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'sales_order_id': str(self.sales_order_id),
            'fee_type': self.fee_type,
            'product_id': str(self.product_id) if self.product_id else None,
            'product_name': self.product_name,
            'length': float(self.length) if self.length else None,
            'width': float(self.width) if self.width else None,
            'customer_order_number': self.customer_order_number,
            'customer_code': self.customer_code,
            'price': float(self.price) if self.price else None,
            'quantity': float(self.quantity) if self.quantity else None,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'amount': float(self.amount) if self.amount else None,
            'tax_type_id': str(self.tax_type_id) if self.tax_type_id else None,
            'untaxed_price': float(self.untaxed_price) if self.untaxed_price else None,
            'untaxed_amount': float(self.untaxed_amount) if self.untaxed_amount else None,
            'tax_amount': float(self.tax_amount) if self.tax_amount else None,
            'foreign_currency_unit_price': float(self.foreign_currency_unit_price) if self.foreign_currency_unit_price else None,
            'foreign_currency_amount': float(self.foreign_currency_amount) if self.foreign_currency_amount else None,
            'foreign_currency_id': str(self.foreign_currency_id) if self.foreign_currency_id else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'internal_delivery_date': self.internal_delivery_date.isoformat() if self.internal_delivery_date else None,
            'customer_requirements': self.customer_requirements,
            'notes': self.notes,
            'sort_order': self.sort_order,
            'income_quantity': float(self.income_quantity) if self.income_quantity else None,
            'completion_status': self.completion_status,
            'assembly_coefficient': float(self.assembly_coefficient) if self.assembly_coefficient else None,
            'sales_material_batch_number': self.sales_material_batch_number,
            'affiliate_company_id': str(self.affiliate_company_id) if self.affiliate_company_id else None,
            'material_note': self.material_note,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # 添加产品信息
        if hasattr(self, 'product') and self.product:
            result['product'] = {
                'id': str(self.product.id),
                'product_code': self.product.product_code,
                'product_name': self.product.product_name
            }
        
        return result


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
    
    # 审计字段
    created_by = Column(UUID(as_uuid=True), comment='创建人ID')
    updated_by = Column(UUID(as_uuid=True), comment='更新人ID')

    # 关联关系
    sales_order = relationship("SalesOrder", back_populates="material_details")
    material = relationship("Material")

    def to_dict(self):
        """转换为字典"""
        result = {
            'id': str(self.id),
            'sales_order_id': str(self.sales_order_id),
            'material_id': str(self.material_id) if self.material_id else None,
            'negative_deviation_percentage': float(self.negative_deviation_percentage) if self.negative_deviation_percentage else None,
            'positive_deviation_percentage': float(self.positive_deviation_percentage) if self.positive_deviation_percentage else None,
            'gift_quantity': float(self.gift_quantity) if self.gift_quantity else None,
            'quantity': float(self.quantity) if self.quantity else None,
            'unit_id': str(self.unit_id) if self.unit_id else None,
            'auxiliary_quantity': float(self.auxiliary_quantity) if self.auxiliary_quantity else None,
            'auxiliary_unit_id': str(self.auxiliary_unit_id) if self.auxiliary_unit_id else None,
            'changed_price_before': float(self.changed_price_before) if self.changed_price_before else None,
            'price': float(self.price) if self.price else None,
            'amount': float(self.amount) if self.amount else None,
            'tax_type_id': str(self.tax_type_id) if self.tax_type_id else None,
            'sales_unit_id': str(self.sales_unit_id) if self.sales_unit_id else None,
            'untaxed_price': float(self.untaxed_price) if self.untaxed_price else None,
            'untaxed_amount': float(self.untaxed_amount) if self.untaxed_amount else None,
            'foreign_currency_unit_price': float(self.foreign_currency_unit_price) if self.foreign_currency_unit_price else None,
            'foreign_currency_amount': float(self.foreign_currency_amount) if self.foreign_currency_amount else None,
            'foreign_currency_id': str(self.foreign_currency_id) if self.foreign_currency_id else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'internal_delivery_date': self.internal_delivery_date.isoformat() if self.internal_delivery_date else None,
            'customer_requirements': self.customer_requirements,
            'notes': self.notes,
            'sort_order': self.sort_order,
            'income_quantity': float(self.income_quantity) if self.income_quantity else None,
            'completion_status': self.completion_status,
            'assembly_coefficient': float(self.assembly_coefficient) if self.assembly_coefficient else None,
            'sales_material_batch_number': self.sales_material_batch_number,
            'affiliate_company_id': str(self.affiliate_company_id) if self.affiliate_company_id else None,
            'material_archive_note': self.material_archive_note,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # 添加材料信息
        if hasattr(self, 'material') and self.material:
            result['material'] = {
                'id': str(self.material.id),
                'material_code': self.material.material_code,
                'material_name': self.material.material_name
            }
        
        return result


class DeliveryNotice(TenantModel):
    """送货通知单主表"""
    __tablename__ = 'delivery_notices'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notice_number = Column(String(50), nullable=False, comment='通知单号 (自动生成)')
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customer_management.id'), nullable=False, comment='客户ID (外键)')
    sales_order_id = Column(UUID(as_uuid=True), ForeignKey('sales_orders.id'), nullable=True, comment='销售订单ID (外键)')
    delivery_address = Column(Text, comment='送货地址')
    delivery_date = Column(DateTime, comment='送货日期')
    delivery_method = Column(String(50), comment='送货方式')
    logistics_info = Column(Text, comment='物流信息')
    remark = Column(Text, comment='备注')
    status = Column(String(20), default='draft', comment='状态(draft/confirmed/shipped/completed/cancelled)')
    
    created_by = Column(UUID(as_uuid=True), comment='创建人ID')
    updated_by = Column(UUID(as_uuid=True), comment='更新人ID')

    # 关联关系
    customer = relationship("CustomerManagement", backref="delivery_notices")
    details = relationship("DeliveryNoticeDetail", back_populates="delivery_notice", cascade="all, delete-orphan")
    sales_order = relationship("SalesOrder", back_populates="delivery_notices")

    def to_dict(self):
        """将模型对象转换为字典"""
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # 格式化特殊字段
        data['id'] = str(self.id)
        data['customer_id'] = str(self.customer_id) if self.customer_id else None
        data['sales_order_id'] = str(self.sales_order_id) if self.sales_order_id else None
        data['delivery_date'] = self.delivery_date.isoformat() if self.delivery_date else None
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        data['created_by'] = str(self.created_by) if self.created_by else None
        data['updated_by'] = str(self.updated_by) if self.updated_by else None

        # 添加关联数据
        if self.customer:
            data['customer'] = {
                'id': str(self.customer.id),
                'customer_name': self.customer.customer_name,
                'customer_code': self.customer.customer_code
            }
        if self.details:
            data['details'] = [detail.to_dict() for detail in self.details]
            
        return data


class DeliveryNoticeDetail(TenantModel):
    """送货通知明细子表"""
    __tablename__ = 'delivery_notice_details'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_notice_id = Column(UUID(as_uuid=True), ForeignKey('delivery_notices.id'), nullable=False, comment='送货通知单ID 外键')
    
    work_order_number = Column(String(50), comment='工单号')
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), comment='产品ID 外键')
    product_name = Column(String(200), comment='产品名称')
    product_code = Column(String(50), comment='产品编号')
    specification = Column(Text, comment='规格')
    auxiliary_quantity = Column(Numeric(15, 4), comment='订单辅数')
    sales_unit = Column(String(20), comment='销售单位')
    order_quantity = Column(Numeric(15, 4), comment='订单数量')
    notice_quantity = Column(Numeric(15, 4), comment='通知数量')
    gift_quantity = Column(Numeric(15, 4), comment='赠送数')
    inventory_quantity = Column(Numeric(15, 4), comment='库存数')
    unit = Column(String(20), comment='单位')
    price = Column(Numeric(15, 4), comment='价格')
    amount = Column(Numeric(15, 4), comment='金额')
    negative_deviation_percentage = Column(Numeric(5, 2), comment='负偏差%')
    positive_deviation_percentage = Column(Numeric(5, 2), comment='正偏差%')
    pcs = Column(Integer, comment='件数')
    production_min_quantity = Column(Numeric(15, 4), comment='生产最小数')
    production_max_quantity = Column(Numeric(15, 4), comment='生产最大数')
    order_delivery_date = Column(DateTime, comment='订单交期')
    internal_delivery_date = Column(DateTime, comment='内部交期')
    plate_type = Column(String(50), comment='版辊类型')
    sales_order_number = Column(String(50), comment='销售单号')
    customer_order_number = Column(String(100), comment='客户订单号')
    product_category = Column(String(100), comment='产品分类')
    customer_code = Column(String(100), comment='客户代号')
    material_structure = Column(Text, comment='材质结构')
    tax_amount = Column(Numeric(15, 4), comment='税额')
    outer_box = Column(String(100), comment='外箱')
    foreign_currency_unit_price = Column(Numeric(15, 4), comment='外币单价')
    foreign_currency_amount = Column(Numeric(15, 4), comment='外币金额')
    sort_order = Column(Integer, comment='排序')
    box_count = Column(Integer, comment='箱数')
    total_area = Column(Numeric(15, 4), comment='总面积')
    discount_amount = Column(Numeric(15, 4), comment='折扣金额')
    notify_undiscount_amount = Column(Numeric(15, 4), comment='通知未折数')
    grade = Column(String(20), comment='等级')
    
    created_by = Column(UUID(as_uuid=True), comment='创建人ID')
    updated_by = Column(UUID(as_uuid=True), comment='更新人ID')

    # 关联关系
    delivery_notice = relationship("DeliveryNotice", back_populates="details")
    product = relationship("Product", backref="delivery_notice_details")

    def to_dict(self):
        """将模型对象转换为字典"""
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # 格式化特殊字段
        data['id'] = str(self.id)
        data['delivery_notice_id'] = str(self.delivery_notice_id)
        data['product_id'] = str(self.product_id) if self.product_id else None
        data['order_delivery_date'] = self.order_delivery_date.isoformat() if self.order_delivery_date else None
        data['internal_delivery_date'] = self.internal_delivery_date.isoformat() if self.internal_delivery_date else None
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        data['created_by'] = str(self.created_by) if self.created_by else None
        data['updated_by'] = str(self.updated_by) if self.updated_by else None
        
        # 格式化数字字段
        for key in ['auxiliary_quantity', 'order_quantity', 'notice_quantity', 'gift_quantity', 'inventory_quantity', 'price', 'amount', 'negative_deviation_percentage', 'positive_deviation_percentage', 'production_min_quantity', 'production_max_quantity', 'tax_amount', 'foreign_currency_unit_price', 'foreign_currency_amount', 'total_area', 'discount_amount', 'notify_undiscount_amount']:
            if data.get(key) is not None:
                data[key] = float(data[key])

        if self.product:
            data['product'] = {
                'id': str(self.product.id),
                'product_name': self.product.product_name,
                'product_code': self.product.product_code
            }
        return data 