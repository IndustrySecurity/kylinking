# -*- coding: utf-8 -*-
# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
产品入库服务
"""

from typing import Dict, List, Optional, Any
from sqlalchemy import func, and_, or_, desc, text
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID
from app.models.business.inventory import InboundOrder, InboundOrderDetail, Inventory, InventoryTransaction
from app.services.base_service import TenantAwareService
from flask import g, current_app
import logging
import uuid

logger = logging.getLogger(__name__)


class ProductInboundService(TenantAwareService):
    """
    产品入库管理服务类
    提供产品入库相关的业务逻辑操作
    """
    
    def _fill_warehouse_info(self, orders):
        """批量填充订单的仓库名称信息"""
        if not orders:
            return
        
        # 获取所有唯一的仓库ID
        warehouse_ids = list(set([order.warehouse_id for order in orders if order.warehouse_id]))
        
        if not warehouse_ids:
            return
        
        try:
            # 查询仓库信息
            from app.models.basic_data import Warehouse
            warehouses = self.session.query(Warehouse).filter(Warehouse.id.in_(warehouse_ids)).all()
            warehouse_dict = {str(w.id): w.warehouse_name for w in warehouses}
            
            # 填充仓库名称
            for order in orders:
                if order.warehouse_id and str(order.warehouse_id) in warehouse_dict:
                    order.warehouse_name = warehouse_dict[str(order.warehouse_id)]
                elif not order.warehouse_name:
                    order.warehouse_name = '未知仓库'
        except Exception as e:
            current_app.logger.warning(f"填充仓库信息失败: {e}")
            # 失败时使用默认值
            for order in orders:
                if not order.warehouse_name:
                    order.warehouse_name = '未知仓库'

    def get_product_inbound_order_list(
        self,
        warehouse_id: Optional[str] = None,
        status: Optional[str] = None,
        approval_status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取产品入库单列表"""
        from sqlalchemy.orm import joinedload
        query = self.session.query(InboundOrder).filter(
            InboundOrder.order_type == 'finished_goods'
        ).options(
            joinedload(InboundOrder.inbound_person),
            joinedload(InboundOrder.department)
        )
        
        if warehouse_id:
            query = query.filter(InboundOrder.warehouse_id == warehouse_id)
        
        if status:
            query = query.filter(InboundOrder.status == status)
        
        if approval_status:
            query = query.filter(InboundOrder.approval_status == approval_status)
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(InboundOrder.order_date >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(InboundOrder.order_date <= end_dt)
            except ValueError:
                pass
        
        if search:
            search_filter = or_(
                InboundOrder.order_number.ilike(f'%{search}%'),
                InboundOrder.warehouse_name.ilike(f'%{search}%'),
                InboundOrder.supplier_name.ilike(f'%{search}%'),
                InboundOrder.remark.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        orders = query.order_by(InboundOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 填充仓库信息
        self._fill_warehouse_info(orders)
        
        return {
            'items': [order.to_dict() for order in orders],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }

    def get_product_inbound_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取产品入库单详情"""
        from sqlalchemy.orm import joinedload
        order = self.session.query(InboundOrder).options(
            joinedload(InboundOrder.inbound_person),
            joinedload(InboundOrder.department)
        ).filter(
            InboundOrder.id == order_id,
            InboundOrder.order_type == 'finished_goods'
        ).first()
        
        if not order:
            return None
        
        # 填充仓库信息
        self._fill_warehouse_info([order])
        
        return order.to_dict()

    def create_product_inbound_order(self, data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """创建产品入库单（支持同时创建明细）"""
        try:
            # 生成入库单号
            order_number = f"PIN{datetime.now().strftime('%Y%m%d')}{datetime.now().microsecond:06d}"
            
            # 转换created_by为UUID
            try:
                created_by_uuid = uuid.UUID(created_by)
            except (TypeError):
                created_by_uuid = created_by
            
            # 提取明细数据
            details_data = data.pop('details', [])
            
            # 准备订单数据
            order_data = {
                'warehouse_id': uuid.UUID(data['warehouse_id']),
                'order_type': 'finished_goods',
                'order_number': order_number,
                'order_date': datetime.strptime(data['order_date'], '%Y-%m-%d') if data.get('order_date') else datetime.now(),
                'status': 'draft',
                'approval_status': 'pending',
                'inbound_person_id': uuid.UUID(data['inbound_person_id']) if data.get('inbound_person_id') else None,
                'department_id': uuid.UUID(data['department_id']) if data.get('department_id') else None,
                'supplier_name': data.get('supplier_name', ''),
                'supplier_id': uuid.UUID(data['supplier_id']) if data.get('supplier_id') else None,
                'pallet_count': data.get('pallet_count', 0),
                'remark': data.get('remark', '')
            }
            
            # 使用继承的create_with_tenant方法
            order = self.create_with_tenant(InboundOrder, **order_data)
            self.session.flush()  # 获取order.id
            
            # 创建明细
            if details_data:
                for detail_data in details_data:
                    detail_params = {
                        'inbound_order_id': order.id,
                        'inbound_quantity': Decimal(str(detail_data.get('inbound_quantity', 0))),
                        'unit': detail_data.get('unit', '个')
                    }
                    
                    # 设置其他明细字段
                    if detail_data.get('product_id'):
                        detail_params['product_id'] = uuid.UUID(detail_data['product_id'])
                    if detail_data.get('product_name'):
                        detail_params['product_name'] = detail_data['product_name']
                    if detail_data.get('product_code'):
                        detail_params['product_code'] = detail_data['product_code']
                    if detail_data.get('batch_number'):
                        detail_params['batch_number'] = detail_data['batch_number']
                    if detail_data.get('location_code'):
                        detail_params['location_code'] = detail_data['location_code']
                    if detail_data.get('unit_cost'):
                        detail_params['unit_cost'] = Decimal(str(detail_data['unit_cost']))
                    
                    # 创建明细
                    detail = self.create_with_tenant(InboundOrderDetail, **detail_params)
            
            self.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([order])
            
            return order.to_dict()
            
        except Exception as e:
            self.rollback()
            logger.error(f"创建产品入库单失败: {e}")
            raise e

    def update_product_inbound_order(self, order_id: str, data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """更新产品入库单（支持同时更新明细）"""
        try:
            order = self.session.query(InboundOrder).filter(
                InboundOrder.id == order_id,
                InboundOrder.order_type == 'finished_goods'
            ).first()
            
            if not order:
                raise ValueError(f"产品入库单不存在: {order_id}")
            
            # 检查状态是否允许更新
            if order.status not in ['draft', 'confirmed']:
                raise ValueError("只有草稿和已确认状态的产品入库单可以更新")
            
            # 提取明细数据
            details_data = data.pop('details', None)
            
            # 更新主表字段
            for key, value in data.items():
                if hasattr(order, key) and key not in ['id', 'order_number', 'created_by', 'created_at', 'order_type']:
                    if key == 'order_date' and isinstance(value, str):
                        order.order_date = datetime.strptime(value, '%Y-%m-%d')
                    elif key == 'warehouse_id' and isinstance(value, str):
                        order.warehouse_id = uuid.UUID(value)
                    elif key == 'supplier_id' and isinstance(value, str):
                        order.supplier_id = uuid.UUID(value)
                    else:
                        setattr(order, key, value)
            
            # 转换updated_by为UUID
            try:
                updated_by_uuid = uuid.UUID(updated_by)
            except (TypeError):
                updated_by_uuid = updated_by
            
            if hasattr(order, 'updated_by'):
                order.updated_by = updated_by_uuid
            if hasattr(order, 'updated_at'):
                order.updated_at = func.now()
            
            # 更新明细（如果提供了明细数据）
            if details_data is not None:
                # 删除现有明细
                self.session.query(InboundOrderDetail).filter(
                    InboundOrderDetail.inbound_order_id == order_id
                ).delete()
                
                # 创建新明细
                for detail_data in details_data:
                    detail_params = {
                        'inbound_order_id': order.id,
                        'inbound_quantity': Decimal(str(detail_data.get('inbound_quantity', 0))),
                        'unit': detail_data.get('unit', '个'),
                        'created_by': updated_by_uuid
                    }
                    
                    # 设置其他明细字段
                    if detail_data.get('product_id'):
                        detail_params['product_id'] = uuid.UUID(detail_data['product_id'])
                    if detail_data.get('product_name'):
                        detail_params['product_name'] = detail_data['product_name']
                    if detail_data.get('product_code'):
                        detail_params['product_code'] = detail_data['product_code']
                    if detail_data.get('batch_number'):
                        detail_params['batch_number'] = detail_data['batch_number']
                    if detail_data.get('location_code'):
                        detail_params['location_code'] = detail_data['location_code']
                    if detail_data.get('unit_cost'):
                        detail_params['unit_cost'] = Decimal(str(detail_data['unit_cost']))
                    
                    detail = self.create_with_tenant(InboundOrderDetail, **detail_params)
            
            self.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([order])
            
            return order.to_dict()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"更新产品入库单失败: {str(e)}")
            raise ValueError(f"更新产品入库单失败: {str(e)}")

    def delete_product_inbound_order(self, order_id: str) -> bool:
        """删除产品入库单"""
        try:
            order = self.session.query(InboundOrder).filter(
                InboundOrder.id == order_id,
                InboundOrder.order_type == 'finished_goods'
            ).first()
            
            if not order:
                raise ValueError(f"产品入库单不存在: {order_id}")
            
            # 检查状态是否允许删除
            if order.status not in ['draft']:
                raise ValueError("只有草稿状态的产品入库单可以删除")
            
            self.session.delete(order)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"删除产品入库单失败: {str(e)}")
            raise ValueError(f"删除产品入库单失败: {str(e)}")

    def approve_product_inbound_order(self, order_id: str, approval_data: Dict[str, Any], approved_by: str) -> Dict[str, Any]:
        """审核产品入库单"""
        try:
            order = self.session.query(InboundOrder).filter(
                InboundOrder.id == order_id,
                InboundOrder.order_type == 'finished_goods'
            ).first()
            
            if not order:
                raise ValueError(f"产品入库单不存在: {order_id}")
            
            # 检查状态
            if order.status not in ['draft', 'confirmed']:
                raise ValueError("只有草稿和已确认状态的产品入库单可以审核")
            
            approval_status = approval_data.get('approval_status', 'approved')
            
            order.approval_status = approval_status
            order.approved_by = uuid.UUID(approved_by)
            order.approved_at = func.now()
            order.updated_by = uuid.UUID(approved_by)
            order.updated_at = func.now()
            
            if approval_data.get('approval_comment'):
                order.remark = f"{order.remark or ''}\n审核意见: {approval_data['approval_comment']}".strip()
            
            # 如果审核通过，更新状态为已确认
            if approval_status == 'approved':
                order.status = 'confirmed'
            elif approval_status == 'rejected':
                order.status = 'cancelled'
            
            self.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([order])
            
            return order.to_dict()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"审核产品入库单失败: {str(e)}")
            raise ValueError(f"审核产品入库单失败: {str(e)}")

    def execute_product_inbound_order(self, order_id: str, executed_by: str) -> Dict[str, Any]:
        """执行产品入库单（增加库存）"""
        try:
            order = self.session.query(InboundOrder).filter(
                InboundOrder.id == order_id,
                InboundOrder.order_type == 'finished_goods'
            ).first()
            
            if not order:
                raise ValueError(f"产品入库单不存在: {order_id}")
            
            # 检查状态
            if order.status != 'confirmed' or order.approval_status != 'approved':
                raise ValueError("只有已确认且已审核的产品入库单可以执行")
            
            # 获取入库单明细
            details = self.session.query(InboundOrderDetail).filter(
                InboundOrderDetail.inbound_order_id == order_id
            ).all()
            
            if not details:
                raise ValueError("产品入库单没有明细，无法执行")
            
            executed_by_uuid = uuid.UUID(executed_by)
            transactions = []
            
            # 执行库存增加
            for detail in details:
                if not detail.product_id:
                    continue
                    
                # 查找对应的库存记录
                inventory = self.session.query(Inventory).filter(
                    Inventory.warehouse_id == order.warehouse_id,
                    Inventory.product_id == detail.product_id,
                    Inventory.is_active == True
                ).first()
                
                # 如果库存记录不存在，创建新的
                if not inventory:
                    inventory = Inventory(
                        warehouse_id=order.warehouse_id,
                        product_id=detail.product_id,
                        current_quantity=Decimal('0'),
                        available_quantity=Decimal('0'),
                        reserved_quantity=Decimal('0'),
                        unit=detail.unit,
                        unit_cost=detail.unit_cost or Decimal('0'),
                        total_cost=Decimal('0'),
                        last_inbound_date=datetime.now(),
                        created_by=executed_by_uuid,
                        is_active=True
                    )
                    self.session.add(inventory)
                    self.session.flush()  # 获取inventory.id
                
                inbound_quantity = detail.inbound_quantity
                quantity_before = inventory.current_quantity
                
                # 增加库存
                inventory.current_quantity += inbound_quantity
                inventory.available_quantity += inbound_quantity
                inventory.last_inbound_date = datetime.now()
                inventory.updated_by = executed_by_uuid
                inventory.updated_at = func.now()
                
                # 如果提供了单价，更新加权平均成本
                if detail.unit_cost:
                    total_cost_before = inventory.total_cost or Decimal('0')
                    new_cost = detail.unit_cost * inbound_quantity
                    inventory.total_cost = total_cost_before + new_cost
                    
                    # 计算新的加权平均单价
                    if inventory.current_quantity > 0:
                        inventory.unit_cost = inventory.total_cost / inventory.current_quantity
                
                # 重新计算总成本
                inventory.calculate_total_cost()
                
                # 创建库存流水记录
                transaction = InventoryTransaction(
                    inventory_id=inventory.id,
                    warehouse_id=order.warehouse_id,
                    product_id=detail.product_id,
                    transaction_type='production_in',
                    quantity_change=inbound_quantity,
                    quantity_before=quantity_before,
                    quantity_after=inventory.current_quantity,
                    unit=detail.unit,
                    unit_price=detail.unit_cost or Decimal('0'),
                    source_document_type='inbound_order',
                    source_document_id=order.id,
                    source_document_number=order.order_number,
                    batch_number=detail.batch_number,
                    to_location=detail.location_code,
                    supplier_id=order.supplier_id,
                    reason=f"产品入库单 {order.order_number} 执行入库",
                    created_by=executed_by_uuid,
                    approval_status='approved'
                )
                
                # 计算总金额
                transaction.calculate_total_amount()
                
                self.session.add(transaction)
                transactions.append(transaction)
            
            # 更新入库单状态
            order.status = 'completed'
            order.updated_by = executed_by_uuid
            order.updated_at = func.now()
            
            self.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([order])
            
            current_app.logger.info(f"产品入库单 {order.order_number} 执行成功，创建了 {len(transactions)} 条库存流水")
            
            return {
                **order.to_dict(),
                'transactions_count': len(transactions)
            }
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"执行产品入库单失败: {str(e)}")
            raise ValueError(f"执行产品入库单失败: {str(e)}")

    def cancel_product_inbound_order(self, order_id: str, cancel_data: Dict[str, Any], cancelled_by: str) -> Dict[str, Any]:
        """取消产品入库单"""
        try:
            order = self.session.query(InboundOrder).filter(
                InboundOrder.id == order_id,
                InboundOrder.order_type == 'finished_goods'
            ).first()
            
            if not order:
                raise ValueError(f"产品入库单不存在: {order_id}")
            
            # 检查状态
            if order.status in ['completed', 'cancelled']:
                raise ValueError("已完成或已取消的产品入库单不能再次取消")
            
            order.status = 'cancelled'
            order.updated_by = uuid.UUID(cancelled_by)
            order.updated_at = func.now()
            
            # 记录取消原因
            if cancel_data.get('cancel_reason'):
                order.remarks = f"{order.remarks or ''}\n取消原因: {cancel_data['cancel_reason']}".strip()
            
            self.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([order])
            
            return order.to_dict()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"取消产品入库单失败: {str(e)}")
            raise ValueError(f"取消产品入库单失败: {str(e)}")


def get_product_inbound_service(tenant_id: str = None, schema_name: str = None) -> ProductInboundService:
    """获取产品入库服务实例"""
    return ProductInboundService(tenant_id=tenant_id, schema_name=schema_name) 