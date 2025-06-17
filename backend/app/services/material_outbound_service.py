# -*- coding: utf-8 -*-
"""
材料出库服务
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID
from app.models.business.inventory import MaterialOutboundOrder, MaterialOutboundOrderDetail, Inventory, InventoryTransaction
from app.extensions import db
from flask import g, current_app
import logging
import uuid

logger = logging.getLogger(__name__)


class MaterialOutboundService:
    """
    材料出库服务类
    提供材料出库单相关的业务逻辑操作
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in MaterialOutboundService")
            from app.extensions import db
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))

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
            warehouses = self.db.query(Warehouse).filter(Warehouse.id.in_(warehouse_ids)).all()
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

    def get_material_outbound_order_list(
        self,
        warehouse_id: str = None,
        order_type: str = None,
        status: str = None,
        approval_status: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        search: str = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取材料出库单列表"""
        self._set_schema()
        query = self.db.query(MaterialOutboundOrder)
        
        if warehouse_id:
            query = query.filter(MaterialOutboundOrder.warehouse_id == warehouse_id)
        
        if order_type:
            query = query.filter(MaterialOutboundOrder.order_type == order_type)
        
        if status:
            query = query.filter(MaterialOutboundOrder.status == status)
        
        if approval_status:
            query = query.filter(MaterialOutboundOrder.approval_status == approval_status)
        
        if start_date:
            query = query.filter(MaterialOutboundOrder.order_date >= start_date)
        
        if end_date:
            query = query.filter(MaterialOutboundOrder.order_date <= end_date)
        
        if search:
            search_filter = or_(
                MaterialOutboundOrder.order_number.ilike(f'%{search}%'),
                MaterialOutboundOrder.requisition_department.ilike(f'%{search}%'),
                MaterialOutboundOrder.requisition_person.ilike(f'%{search}%'),
                MaterialOutboundOrder.outbound_person.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        total = query.count()
        
        orders = query.order_by(MaterialOutboundOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 填充仓库信息
        self._fill_warehouse_info(orders)
        
        return {
            'items': [order.to_dict() for order in orders],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }

    def get_material_outbound_order_by_id(self, order_id: str) -> Optional[MaterialOutboundOrder]:
        """根据ID获取材料出库单详情"""
        self._set_schema()
        order = self.db.query(MaterialOutboundOrder).filter(MaterialOutboundOrder.id == order_id).first()
        
        if order:
            # 填充仓库信息
            self._fill_warehouse_info([order])
        
        return order

    def get_material_outbound_order_details(self, order_id: str) -> List[Dict[str, Any]]:
        """获取材料出库单明细"""
        self._set_schema()
        details = self.db.query(MaterialOutboundOrderDetail).filter(
            MaterialOutboundOrderDetail.material_outbound_order_id == order_id
        ).all()
        
        return [detail.to_dict() for detail in details]

    def create_material_outbound_order(
        self,
        data: dict,
        created_by: str
    ) -> MaterialOutboundOrder:
        """创建材料出库单"""
        self._set_schema()
        
        # 转换created_by为UUID
        try:
            created_by_uuid = uuid.UUID(created_by)
        except (ValueError, TypeError):
            created_by_uuid = created_by
        
        # 提取明细数据
        details_data = data.pop('details', [])
        
        order = MaterialOutboundOrder(
            warehouse_id=uuid.UUID(data['warehouse_id']),
            order_type=data.get('order_type', 'material'),
            created_by=created_by_uuid,
            **data
        )
        
        self.db.add(order)
        self.db.flush()  # 获取order.id
        
        # 创建明细
        if details_data:
            for detail_data in details_data:
                detail = MaterialOutboundOrderDetail(
                    material_outbound_order_id=order.id,
                    outbound_quantity=Decimal(detail_data['outbound_quantity']),
                    unit=detail_data['unit'],
                    created_by=created_by_uuid,
                    **{k: v for k, v in detail_data.items() if k not in ['outbound_quantity', 'unit']}
                )
                self.db.add(detail)
        
        self.db.commit()
        self.db.refresh(order)
        
        return order

    def update_material_outbound_order(
        self,
        order_id: str,
        updated_by: str,
        **update_data
    ) -> Optional[MaterialOutboundOrder]:
        """更新材料出库单"""
        self._set_schema()
        order = self.db.query(MaterialOutboundOrder).filter(MaterialOutboundOrder.id == order_id).first()
        
        if not order:
            return None
        
        # 更新字段
        for key, value in update_data.items():
            if hasattr(order, key) and key not in ['id', 'created_at', 'created_by']:
                setattr(order, key, value)
        
        order.updated_by = uuid.UUID(updated_by) if isinstance(updated_by, str) else updated_by
        order.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(order)
        
        return order

    def add_material_outbound_order_detail(
        self,
        order_id: str,
        outbound_quantity: Decimal,
        unit: str,
        created_by: str,
        material_id: str = None,
        material_name: str = None,
        **kwargs
    ) -> MaterialOutboundOrderDetail:
        """添加材料出库单明细"""
        self._set_schema()
        
        detail = MaterialOutboundOrderDetail(
            material_outbound_order_id=uuid.UUID(order_id),
            material_id=uuid.UUID(material_id) if material_id else None,
            material_name=material_name,
            outbound_quantity=outbound_quantity,
            unit=unit,
            created_by=uuid.UUID(created_by) if isinstance(created_by, str) else created_by,
            **kwargs
        )
        
        self.db.add(detail)
        self.db.commit()
        self.db.refresh(detail)
        
        return detail

    def update_material_outbound_order_detail(
        self,
        detail_id: str,
        updated_by: str,
        **update_data
    ) -> Optional[MaterialOutboundOrderDetail]:
        """更新材料出库单明细"""
        self._set_schema()
        detail = self.db.query(MaterialOutboundOrderDetail).filter(
            MaterialOutboundOrderDetail.id == detail_id
        ).first()
        
        if not detail:
            return None
        
        # 更新字段
        for key, value in update_data.items():
            if hasattr(detail, key) and key not in ['id', 'created_at', 'created_by']:
                if key == 'outbound_quantity' and value is not None:
                    value = Decimal(value)
                setattr(detail, key, value)
        
        detail.updated_by = uuid.UUID(updated_by) if isinstance(updated_by, str) else updated_by
        detail.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(detail)
        
        return detail

    def delete_material_outbound_order_detail(self, detail_id: str) -> bool:
        """删除材料出库单明细"""
        self._set_schema()
        detail = self.db.query(MaterialOutboundOrderDetail).filter(
            MaterialOutboundOrderDetail.id == detail_id
        ).first()
        
        if not detail:
            return False
        
        self.db.delete(detail)
        self.db.commit()
        
        return True

    def approve_material_outbound_order(
        self,
        order_id: str,
        approved_by: str,
        approval_status: str = 'approved'
    ) -> MaterialOutboundOrder:
        """审核材料出库单"""
        self._set_schema()
        order = self.db.query(MaterialOutboundOrder).filter(MaterialOutboundOrder.id == order_id).first()
        
        if not order:
            raise ValueError("材料出库单不存在")
        
        if order.approval_status != 'pending':
            raise ValueError("材料出库单已经审核过")
        
        order.approval_status = approval_status
        order.approved_by = uuid.UUID(approved_by) if isinstance(approved_by, str) else approved_by
        order.approved_at = datetime.now()
        
        if approval_status == 'approved':
            order.status = 'confirmed'
        
        self.db.commit()
        self.db.refresh(order)
        
        return order

    def execute_material_outbound_order(
        self,
        order_id: str,
        executed_by: str
    ) -> List[InventoryTransaction]:
        """执行材料出库单"""
        self._set_schema()
        order = self.db.query(MaterialOutboundOrder).filter(MaterialOutboundOrder.id == order_id).first()
        
        if not order:
            raise ValueError("材料出库单不存在")
        
        if order.approval_status != 'approved':
            raise ValueError("材料出库单未审核，不能执行")
        
        if order.status == 'completed':
            raise ValueError("材料出库单已经执行")
        
        transactions = []
        
        # 处理每个明细行
        for detail in order.details:
            if not detail.material_id:
                continue
            
            # 查找库存记录
            inventory = self.db.query(Inventory).filter(
                and_(
                    Inventory.warehouse_id == order.warehouse_id,
                    Inventory.material_id == detail.material_id,
                    Inventory.batch_number == detail.batch_number,
                    Inventory.is_active == True
                )
            ).first()
            
            if not inventory:
                raise ValueError(f"材料 {detail.material_name or detail.material_id} 在仓库中没有库存")
            
            if inventory.available_quantity < detail.outbound_quantity:
                raise ValueError(f"材料 {detail.material_name or detail.material_id} 可用库存不足")
            
            # 记录变动前数量
            quantity_before = inventory.current_quantity
            
            # 更新库存数量
            inventory.current_quantity -= detail.outbound_quantity
            inventory.available_quantity -= detail.outbound_quantity
            
            # 更新成本信息
            if inventory.unit_cost and detail.outbound_quantity > 0:
                cost_reduction = detail.outbound_quantity * inventory.unit_cost
                inventory.total_cost = (inventory.total_cost or Decimal('0')) - cost_reduction
            
            inventory.updated_by = executed_by
            inventory.updated_at = datetime.now()
            
            # 创建库存流水记录
            transaction = InventoryTransaction(
                inventory_id=inventory.id,
                warehouse_id=order.warehouse_id,
                material_id=detail.material_id,
                transaction_type='out',
                quantity_change=-detail.outbound_quantity,
                quantity_before=quantity_before,
                quantity_after=inventory.current_quantity,
                unit=detail.unit,
                unit_price=detail.unit_price or inventory.unit_cost,
                source_document_type='material_outbound_order',
                source_document_id=order.id,
                source_document_number=order.order_number,
                batch_number=detail.batch_number,
                from_location=detail.actual_location_code or detail.location_code,
                reason=f"材料出库 - {order.requisition_purpose or ''}",
                created_by=executed_by
            )
            
            self.db.add(transaction)
            transactions.append(transaction)
        
        # 更新出库单状态
        order.status = 'completed'
        order.updated_by = executed_by
        order.updated_at = datetime.now()
        
        self.db.commit()
        
        return transactions

    def cancel_material_outbound_order(
        self,
        order_id: str,
        cancelled_by: str,
        cancel_reason: str = None
    ) -> MaterialOutboundOrder:
        """取消材料出库单"""
        self._set_schema()
        order = self.db.query(MaterialOutboundOrder).filter(MaterialOutboundOrder.id == order_id).first()
        
        if not order:
            raise ValueError("材料出库单不存在")
        
        if order.status == 'completed':
            raise ValueError("已执行的材料出库单不能取消")
        
        order.status = 'cancelled'
        order.approval_status = 'rejected'
        order.remark = f"{order.remark or ''}\n取消原因: {cancel_reason or '用户取消'}"
        order.updated_by = uuid.UUID(cancelled_by) if isinstance(cancelled_by, str) else cancelled_by
        order.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(order)
        
        return order


def get_material_outbound_service(db: Session = None) -> MaterialOutboundService:
    """获取材料出库服务实例"""
    if db is None:
        from app.extensions import db as default_db
        db = default_db.session
    return MaterialOutboundService(db) 