"""
销售订单服务类
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, or_, desc, asc, func, text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from flask import g, current_app

from app.models.business.sales import SalesOrder, SalesOrderDetail, SalesOrderOtherFee, SalesOrderMaterial
from app.models.basic_data import CustomerManagement, Product, Material, Unit, CustomerContact, Employee, TaxRate
from app.extensions import db
from app.services.base_service import TenantAwareService


class SalesOrderService(TenantAwareService):
    """销售订单服务类"""
    
    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        super().__init__(tenant_id, schema_name, strict_tenant_check=True)
    
    def generate_order_number(self) -> str:
        """生成销售订单号"""
        
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        
        # 查询当天最大订单号
        max_order = self.get_session().query(SalesOrder).filter(
            SalesOrder.order_number.like(f'SO{date_str}%')
        ).order_by(desc(SalesOrder.order_number)).first()
        
        if max_order:
            # 提取序号并加1
            last_seq = int(max_order.order_number[-4:])
            new_seq = last_seq + 1
        else:
            new_seq = 1
            
        return f'SO{date_str}{new_seq:04d}'
    
    def create_sales_order(self, order_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """创建销售订单"""
        try:
            current_app.logger.info(f"开始创建销售订单，用户ID: {user_id}")

            # 创建主订单对象并逐一赋值
            sales_order = self.create_with_tenant(SalesOrder)
            sales_order.order_number = self.generate_order_number()
            sales_order.order_type = order_data.get('order_type', 'normal')
            sales_order.customer_id = order_data.get('customer_id')
            sales_order.customer_order_number = order_data.get('customer_order_number')
            sales_order.contact_person_id = order_data.get('contact_person_id')
            sales_order.tax_type_id = order_data.get('tax_type_id')
            sales_order.order_amount = order_data.get('order_amount', 0)
            sales_order.deposit = order_data.get('deposit', 0)
            sales_order.plate_fee = order_data.get('plate_fee', 0)
            sales_order.plate_fee_percentage = order_data.get('plate_fee_percentage', 0)
            # 处理交货日期/订单日期
            order_date_value = order_data.get('order_date') or order_data.get('delivery_date')
            if order_date_value and isinstance(order_date_value, str):
                try:
                    order_date_value = datetime.fromisoformat(order_date_value.replace('Z', '+00:00'))
                except:
                    order_date_value = None
            sales_order.order_date = order_date_value
            # 处理内部交期
            internal_date_value = order_data.get('internal_delivery_date')
            if internal_date_value and isinstance(internal_date_value, str):
                try:
                    internal_date_value = datetime.fromisoformat(internal_date_value.replace('Z', '+00:00'))
                except:
                    internal_date_value = None
            sales_order.internal_delivery_date = internal_date_value
            sales_order.salesperson_id = order_data.get('salesperson_id')
            # 处理合同日期
            contract_date_value = order_data.get('contract_date')
            if contract_date_value and isinstance(contract_date_value, str):
                try:
                    contract_date_value = datetime.fromisoformat(contract_date_value.replace('Z', '+00:00'))
                except:
                    contract_date_value = None
            sales_order.contract_date = contract_date_value
            sales_order.delivery_address = order_data.get('delivery_address')
            sales_order.logistics_info = order_data.get('logistics_info')
            sales_order.tracking_number = order_data.get('merchandiser_id')
            sales_order.warehouse_id = order_data.get('warehouse_id')
            sales_order.production_requirements = order_data.get('production_requirements')
            sales_order.order_requirements = order_data.get('order_requirements')
            sales_order.status = order_data.get('status', 'draft')
            sales_order.created_by = user_id
            
            current_app.logger.info(f"销售订单主对象创建完成，准备添加到session")
            self.get_session().add(sales_order)
            self.get_session().flush()
            current_app.logger.info(f"销售订单已flush，订单ID: {sales_order.id}")
            
            # 处理订单明细
            if order_data.get('order_details'):
                current_app.logger.info(f"开始处理订单明细，数量: {len(order_data['order_details'])}")
                for detail_data in order_data['order_details']:
                    detail = self.create_with_tenant(SalesOrderDetail)
                    detail.sales_order_id=sales_order.id
                    detail.product_id=detail_data.get('product_id')
                    detail.product_code=detail_data.get('product_code')
                    detail.product_name=detail_data.get('product_name')
                    detail.order_quantity=detail_data.get('order_quantity')
                    detail.unit_price=detail_data.get('unit_price', 0)
                    detail.amount=detail_data.get('amount', 0)
                    detail.unit=detail_data.get('unit')
                    detail.created_by=user_id
                    self.get_session().add(detail)
            
            # 处理其他费用
            if order_data.get('other_fees'):
                current_app.logger.info(f"开始处理其他费用，数量: {len(order_data['other_fees'])}")
                for fee_data in order_data['other_fees']:
                    fee = self.create_with_tenant(SalesOrderOtherFee)
                    fee.sales_order_id=sales_order.id
                    fee.fee_type=fee_data.get('fee_type')
                    fee.product_id=fee_data.get('product_id')
                    fee.price=fee_data.get('price', 0)
                    fee.quantity=fee_data.get('quantity', 1)
                    fee.amount=fee_data.get('amount', 0)
                    fee.created_by=user_id
                    self.get_session().add(fee)
            
            # 处理材料明细
            if order_data.get('material_details'):
                current_app.logger.info(f"开始处理材料明细，数量: {len(order_data['material_details'])}")
                for material_data in order_data['material_details']:
                    material = self.create_with_tenant(SalesOrderMaterial)
                    material.sales_order_id=sales_order.id
                    material.material_id=material_data.get('material_id')
                    material.quantity=material_data.get('quantity')
                    material.price=material_data.get('price', 0)
                    material.amount=material_data.get('amount', 0)
                    material.created_by=user_id
                    self.get_session().add(material)
            
            current_app.logger.info("准备提交事务")
            self.commit()
            current_app.logger.info("事务提交成功，准备获取订单详情")
            
            result = self.get_sales_order_detail(sales_order.id)
            current_app.logger.info("销售订单创建成功")
            return result
            
        except Exception as e:
            current_app.logger.error(f"创建销售订单时发生错误: {str(e)}", exc_info=True)
            self.rollback()
            raise Exception(f"创建销售订单失败: {str(e)}")
    
    def update_sales_order(self, order_id: str, order_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """更新销售订单"""
        try:
            
            # 获取订单
            sales_order = self.get_session().query(SalesOrder).filter_by(id=order_id).first()
            
            if not sales_order:
                raise ValueError("销售订单不存在")
            
            # 更新主订单字段
            for field in ['order_type', 'customer_id', 'customer_order_number', 'contact_person_id',
                         'tax_type_id', 'order_amount', 'deposit', 'plate_fee', 'plate_fee_percentage',
                         'order_date', 'internal_delivery_date', 'salesperson_id', 'contract_date',
                         'delivery_address', 'logistics_info', 'tracking_number', 'warehouse_id',
                         'production_requirements', 'order_requirements', 'status']:
                if field in order_data:
                    # 特殊处理日期字段
                    if field in ['order_date', 'internal_delivery_date', 'contract_date']:
                        date_value = order_data[field]
                        if date_value:
                            if isinstance(date_value, str):
                                try:
                                    # 处理ISO格式的日期字符串
                                    date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                                except:
                                    date_value = None
                        setattr(sales_order, field, date_value)
                    else:
                        setattr(sales_order, field, order_data[field])
            
            # 如果只传了 delivery_date 也要更新 order_date
            if 'delivery_date' in order_data and 'order_date' not in order_data:
                delivery_date_value = order_data['delivery_date']
                if delivery_date_value and isinstance(delivery_date_value, str):
                    try:
                        delivery_date_value = datetime.fromisoformat(delivery_date_value.replace('Z', '+00:00'))
                    except:
                        delivery_date_value = None
                sales_order.order_date = delivery_date_value
            
            sales_order.updated_by = user_id
            
            self.commit()
            
            result = self.get_sales_order_detail(order_id)
            return result
            
        except Exception as e:
            self.rollback()
            raise Exception(f"更新销售订单失败: {str(e)}")
    
    def get_sales_order_detail(self, order_id: str) -> Dict[str, Any]:
        """获取销售订单详情"""
        from sqlalchemy.orm import joinedload
        
        sales_order = self.get_session().query(SalesOrder).options(
            joinedload(SalesOrder.customer),
            joinedload(SalesOrder.contact_person),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.tax_type),
            joinedload(SalesOrder.order_details),
            joinedload(SalesOrder.other_fees),
            joinedload(SalesOrder.material_details)
        ).filter_by(id=order_id).first()
        
        if not sales_order:
            raise ValueError("销售订单不存在")
        
        return sales_order.to_dict()
    
    def get_sales_order_list(self, page: int = 1, page_size: int = 20,
                           filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取销售订单列表"""
        
        # 使用更复杂的查询，包含更多关联信息
        from app.models.basic_data import CustomerContact, Employee
        
        query = self.get_session().query(SalesOrder).options(
            joinedload(SalesOrder.customer)
        )
        
        # 应用过滤条件
        if filters:
            if filters.get('order_number'):
                query = query.filter(SalesOrder.order_number.ilike(f"%{filters['order_number']}%"))
            if filters.get('customer_id'):
                query = query.filter(SalesOrder.customer_id == filters['customer_id'])
            if filters.get('status'):
                query = query.filter(SalesOrder.status == filters['status'])
            if filters.get('salesperson_id'):
                query = query.filter(SalesOrder.salesperson_id == filters['salesperson_id'])
            if filters.get('start_date'):
                query = query.filter(SalesOrder.order_date >= filters['start_date'])
            if filters.get('end_date'):
                query = query.filter(SalesOrder.order_date <= filters['end_date'])
        
        # 排序
        query = query.order_by(desc(SalesOrder.created_at))
        
        # 分页
        total = query.count()
        orders = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 手动构建列表数据，确保包含所有需要的信息
        order_list = []
        for order in orders:
            order_data = {
                'id': str(order.id),
                'order_number': order.order_number,
                'order_type': order.order_type,
                'customer_id': str(order.customer_id) if order.customer_id else None,
                'customer_name': order.customer.customer_name if order.customer else '',
                'customer_code': order.customer.customer_code if order.customer else '',
                'customer_order_number': order.customer_order_number,
                'contact_person_id': str(order.contact_person_id) if order.contact_person_id else None,
                'order_amount': float(order.order_amount) if order.order_amount else 0,
                'deposit': float(order.deposit) if order.deposit else 0,
                'order_date': order.order_date.isoformat() if order.order_date else None,
                'internal_delivery_date': order.internal_delivery_date.isoformat() if order.internal_delivery_date else None,
                'status': order.status,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None,
            }
            
            # 获取联系人信息（手机号）
            if order.contact_person_id:
                try:
                    contact = self.get_session().query(CustomerContact).filter_by(id=order.contact_person_id).first()
                    if contact:
                        order_data['contact_person'] = contact.contact_name if hasattr(contact, 'contact_name') else ''
                        mobile_val = getattr(contact, 'mobile', None) or getattr(contact, 'landline', None) or ''
                        order_data['mobile'] = mobile_val
                        order_data['phone'] = mobile_val
                    else:
                        order_data['contact_person'] = ''
                        order_data['mobile'] = ''
                        order_data['phone'] = ''
                except Exception:
                    order_data['contact_person'] = ''
                    order_data['mobile'] = ''
                    order_data['phone'] = ''
            else:
                order_data['contact_person'] = ''
                order_data['mobile'] = ''
                order_data['phone'] = ''
            
            # 获取业务员信息
            if order.salesperson_id:
                try:
                    salesperson = self.get_session().query(Employee).filter_by(id=order.salesperson_id).first()
                    if salesperson:
                        order_data['salesperson_name'] = salesperson.employee_name
                    else:
                        order_data['salesperson_name'] = ''
                except Exception:
                    order_data['salesperson_name'] = ''
            else:
                order_data['salesperson_name'] = ''
            
            # 获取跟单员信息（tracking_number字段实际存的是跟单员ID）
            if order.tracking_number:
                try:
                    merchandiser = self.get_session().query(Employee).filter_by(id=order.tracking_number).first()
                    if merchandiser:
                        order_data['merchandiser_name'] = merchandiser.employee_name
                    else:
                        order_data['merchandiser_name'] = ''
                except Exception:
                    order_data['merchandiser_name'] = ''
            else:
                order_data['merchandiser_name'] = ''
            
            # 添加送货方式信息
            order_data['delivery_method'] = ''  # 需要从客户信息中获取，暂时留空
            
            # 获取税收信息
            if order.tax_type_id:
                try:
                    tax_rate = self.get_session().query(TaxRate).filter_by(id=order.tax_type_id).first()
                    if tax_rate:
                        order_data['tax_name'] = tax_rate.tax_name
                        order_data['tax_rate'] = float(tax_rate.tax_rate) if tax_rate.tax_rate else 0
                    else:
                        order_data['tax_name'] = ''
                        order_data['tax_rate'] = 0
                except Exception:
                    order_data['tax_name'] = ''
                    order_data['tax_rate'] = 0
            else:
                order_data['tax_name'] = ''
                order_data['tax_rate'] = 0
            
            order_list.append(order_data)
        
        return {
            'orders': order_list,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def approve_sales_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """审批销售订单"""
        try:
            
            sales_order = self.get_session().query(SalesOrder).filter_by(id=order_id).first()
            
            if not sales_order:
                raise ValueError("销售订单不存在")
            
            if sales_order.status != 'draft':
                raise ValueError("只有草稿状态的订单可以审批")
            
            sales_order.status = 'confirmed'
            sales_order.updated_by = user_id
            
            self.commit()
            
            return self.get_sales_order_detail(order_id)
            
        except Exception as e:
            raise Exception(f"审批销售订单失败: {str(e)}")
    
    def cancel_sales_order(self, order_id: str, user_id: str, reason: str = None) -> Dict[str, Any]:
        """取消销售订单"""
        try:
            
            sales_order = self.get_session().query(SalesOrder).filter_by(id=order_id).first()
            
            if not sales_order:
                raise ValueError("销售订单不存在")
            
            if sales_order.status in ['completed', 'cancelled']:
                raise ValueError("已完成或已取消的订单无法取消")
            
            sales_order.status = 'cancelled'
            sales_order.updated_by = user_id
            
            # 可以在这里记录取消原因到备注或日志表
            if reason:
                sales_order.order_requirements = f"{sales_order.order_requirements or ''}\\n取消原因: {reason}"
            
            self.commit()
            
            return self.get_sales_order_detail(order_id)
            
        except Exception as e:
            raise Exception(f"取消销售订单失败: {str(e)}")
    
    def calculate_order_total(self, order_id: str) -> Dict[str, Any]:
        """计算订单总额"""
        
        # 获取订单明细
        details = self.get_session().query(SalesOrderDetail).filter_by(sales_order_id=order_id).all()
        
        # 获取其他费用
        other_fees = self.get_session().query(SalesOrderOtherFee).filter_by(sales_order_id=order_id).all()
        
        # 获取材料费用
        material_fees = self.get_session().query(SalesOrderMaterial).filter_by(sales_order_id=order_id).all()
        
        # 计算总额
        detail_amount = sum(detail.amount or 0 for detail in details)
        fee_amount = sum(fee.amount or 0 for fee in other_fees)
        material_amount = sum(material.amount or 0 for material in material_fees)
        
        total_amount = detail_amount + fee_amount + material_amount
        
        return {
            'detail_amount': detail_amount,
            'fee_amount': fee_amount,
            'material_amount': material_amount,
            'total_amount': total_amount
        }
    
    def get_order_statistics(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取订单统计"""
        
        base_query = self.get_session().query(SalesOrder)
        
        # 应用过滤条件
        if filters:
            if filters.get('start_date'):
                base_query = base_query.filter(SalesOrder.order_date >= filters['start_date'])
            if filters.get('end_date'):
                base_query = base_query.filter(SalesOrder.order_date <= filters['end_date'])
            if filters.get('status'):
                base_query = base_query.filter(SalesOrder.status == filters['status'])
        
        # 统计各状态订单数量
        total_count = base_query.count()
        draft_count = base_query.filter(SalesOrder.status == 'draft').count()
        confirmed_count = base_query.filter(SalesOrder.status == 'confirmed').count()
        completed_count = base_query.filter(SalesOrder.status == 'completed').count()
        cancelled_count = base_query.filter(SalesOrder.status == 'cancelled').count()
        
        return {
            'total_count': total_count,
            'draft_count': draft_count,
            'confirmed_count': confirmed_count,
            'completed_count': completed_count,
            'cancelled_count': cancelled_count
        }
    
    def delete_sales_order(self, order_id: str, user_id: str) -> bool:
        """删除销售订单"""
        try:
            
            # 获取订单
            sales_order = self.get_session().query(SalesOrder).filter_by(id=order_id).first()
            
            if not sales_order:
                raise ValueError("销售订单不存在")
            
            # 检查订单状态，只有草稿状态的订单可以删除
            if sales_order.status != 'draft':
                raise ValueError("只有草稿状态的订单可以删除")
            
            # 删除关联的子表数据（由于使用了cascade="all, delete-orphan"，这些会自动删除）
            # 但为了安全起见，我们手动删除
            self.get_session().query(SalesOrderDetail).filter_by(sales_order_id=order_id).delete()
            self.get_session().query(SalesOrderOtherFee).filter_by(sales_order_id=order_id).delete()
            self.get_session().query(SalesOrderMaterial).filter_by(sales_order_id=order_id).delete()
            
            # 删除主订单
            self.get_session().delete(sales_order)
            self.get_session().commit()
            
            current_app.logger.info(f"销售订单 {order_id} 已被用户 {user_id} 删除")
            return True
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"删除销售订单失败: {str(e)}", exc_info=True)
            raise Exception(f"删除销售订单失败: {str(e)}") 