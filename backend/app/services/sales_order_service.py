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
from app.models.basic_data import CustomerManagement, Product, Material, Unit
from app.extensions import db


class SalesOrderService:
    """销售订单服务类"""
    
    def __init__(self):
        pass
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in SalesOrderService")
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    def generate_order_number(self) -> str:
        """生成销售订单号"""
        self._set_schema()
        
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        
        # 查询当天最大订单号
        max_order = db.session.query(SalesOrder).filter(
            SalesOrder.order_number.like(f'SO{date_str}%')
        ).order_by(desc(SalesOrder.order_number)).first()
        
        if max_order:
            # 提取序号并加1
            last_seq = int(max_order.order_number[-4:])
            new_seq = last_seq + 1
        else:
            new_seq = 1
            
        return f'SO{date_str}{new_seq:04d}'
    
    def create_sales_order(self, user_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建销售订单"""
        try:
            self._set_schema()
            db.session.begin()
            
            # 生成订单号
            order_number = self.generate_order_number()
            
            # 创建主订单
            sales_order = SalesOrder(
                order_number=order_number,
                order_type=order_data.get('order_type', 'normal'),
                customer_id=order_data['customer_id'],
                customer_order_number=order_data.get('customer_order_number'),
                contact_person_id=order_data.get('contact_person_id'),
                tax_type_id=order_data.get('tax_type_id'),
                order_amount=order_data.get('order_amount', 0),
                deposit=order_data.get('deposit', 0),
                plate_fee=order_data.get('plate_fee', 0),
                plate_fee_percentage=order_data.get('plate_fee_percentage', 0),
                order_date=order_data.get('order_date'),
                internal_delivery_date=order_data.get('internal_delivery_date'),
                salesperson_id=order_data.get('salesperson_id'),
                contract_date=order_data.get('contract_date'),
                delivery_address=order_data.get('delivery_address'),
                logistics_info=order_data.get('logistics_info'),
                tracking_number=order_data.get('tracking_number'),
                warehouse_id=order_data.get('warehouse_id'),
                production_requirements=order_data.get('production_requirements'),
                order_requirements=order_data.get('order_requirements'),
                status=order_data.get('status', 'draft'),
                created_by=user_id
            )
            
            db.session.add(sales_order)
            db.session.flush()
            
            # 处理订单明细
            if order_data.get('order_details'):
                for detail_data in order_data['order_details']:
                    detail = SalesOrderDetail(
                        sales_order_id=sales_order.id,
                        product_id=detail_data.get('product_id'),
                        product_code=detail_data.get('product_code'),
                        product_name=detail_data.get('product_name'),
                        order_quantity=detail_data['order_quantity'],
                        unit_price=detail_data.get('unit_price', 0),
                        amount=detail_data.get('amount', 0),
                        unit=detail_data.get('unit'),
                        created_by=user_id
                    )
                    db.session.add(detail)
            
            # 处理其他费用
            if order_data.get('other_fees'):
                for fee_data in order_data['other_fees']:
                    fee = SalesOrderOtherFee(
                        sales_order_id=sales_order.id,
                        fee_type=fee_data['fee_type'],
                        product_id=fee_data.get('product_id'),
                        price=fee_data.get('price', 0),
                        quantity=fee_data.get('quantity', 1),
                        amount=fee_data.get('amount', 0),
                        created_by=user_id
                    )
                    db.session.add(fee)
            
            # 处理材料明细
            if order_data.get('material_details'):
                for material_data in order_data['material_details']:
                    material = SalesOrderMaterial(
                        sales_order_id=sales_order.id,
                        material_id=material_data['material_id'],
                        quantity=material_data['quantity'],
                        price=material_data.get('price', 0),
                        amount=material_data.get('amount', 0),
                        created_by=user_id
                    )
                    db.session.add(material)
            
            db.session.commit()
            
            return self.get_sales_order_detail(sales_order.id)
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"创建销售订单失败: {str(e)}")
    
    def update_sales_order(self, user_id: str, order_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新销售订单"""
        try:
            self._set_schema()
            
            # 获取订单
            sales_order = db.session.query(SalesOrder).filter_by(id=order_id).first()
            
            if not sales_order:
                raise ValueError("销售订单不存在")
            
            # 更新主订单字段
            for field in ['order_type', 'customer_id', 'customer_order_number', 'contact_person_id',
                         'tax_type_id', 'order_amount', 'deposit', 'plate_fee', 'plate_fee_percentage',
                         'order_date', 'internal_delivery_date', 'salesperson_id', 'contract_date',
                         'delivery_address', 'logistics_info', 'tracking_number', 'warehouse_id',
                         'production_requirements', 'order_requirements', 'status']:
                if field in order_data:
                    setattr(sales_order, field, order_data[field])
            
            sales_order.updated_by = user_id
            sales_order.updated_at = datetime.utcnow()
            
            # 处理明细更新（这里简化处理，实际项目中可能需要更复杂的逻辑）
            # TODO: 实现明细的增删改逻辑
            
            db.session.commit()
            
            return self.get_sales_order_detail(order_id)
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"更新销售订单失败: {str(e)}")
    
    def get_sales_order_detail(self, order_id: str) -> Dict[str, Any]:
        """获取销售订单详情"""
        self._set_schema()
        
        # 获取主订单
        sales_order = db.session.query(SalesOrder).options(
            joinedload(SalesOrder.order_details),
            joinedload(SalesOrder.other_fees),
            joinedload(SalesOrder.material_details),
            joinedload(SalesOrder.customer)
        ).filter_by(id=order_id).first()
        
        if not sales_order:
            raise ValueError("销售订单不存在")
        
        return sales_order.to_dict()
    
    def get_sales_order_list(self, page: int = 1, page_size: int = 20,
                           filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取销售订单列表"""
        self._set_schema()
        
        query = db.session.query(SalesOrder).options(
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
        
        return {
            'orders': [order.to_dict() for order in orders],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def approve_sales_order(self, user_id: str, order_id: str) -> Dict[str, Any]:
        """审批销售订单"""
        try:
            self._set_schema()
            
            sales_order = db.session.query(SalesOrder).filter_by(id=order_id).first()
            
            if not sales_order:
                raise ValueError("销售订单不存在")
            
            if sales_order.status != 'draft':
                raise ValueError("只有草稿状态的订单可以审批")
            
            sales_order.status = 'confirmed'
            sales_order.updated_by = user_id
            sales_order.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return self.get_sales_order_detail(order_id)
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"审批销售订单失败: {str(e)}")
    
    def cancel_sales_order(self, user_id: str, order_id: str, reason: str = None) -> Dict[str, Any]:
        """取消销售订单"""
        try:
            self._set_schema()
            
            sales_order = db.session.query(SalesOrder).filter_by(id=order_id).first()
            
            if not sales_order:
                raise ValueError("销售订单不存在")
            
            if sales_order.status in ['completed', 'cancelled']:
                raise ValueError("已完成或已取消的订单无法取消")
            
            sales_order.status = 'cancelled'
            sales_order.updated_by = user_id
            sales_order.updated_at = datetime.utcnow()
            
            # 可以在这里记录取消原因到备注或日志表
            if reason:
                sales_order.order_requirements = f"{sales_order.order_requirements or ''}\n取消原因: {reason}"
            
            db.session.commit()
            
            return self.get_sales_order_detail(order_id)
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"取消销售订单失败: {str(e)}")
    
    def calculate_order_total(self, order_id: str) -> Dict[str, Any]:
        """计算订单总额"""
        self._set_schema()
        
        # 获取订单明细
        details = db.session.query(SalesOrderDetail).filter_by(sales_order_id=order_id).all()
        
        # 获取其他费用
        other_fees = db.session.query(SalesOrderOtherFee).filter_by(sales_order_id=order_id).all()
        
        # 获取材料费用
        material_fees = db.session.query(SalesOrderMaterial).filter_by(sales_order_id=order_id).all()
        
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
        self._set_schema()
        
        base_query = db.session.query(SalesOrder)
        
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