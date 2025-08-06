# -*- coding: utf-8 -*-
# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
材料出库服务
"""

from typing import Dict, List, Optional, Any, Union
from sqlalchemy import func, and_, or_, desc, text
from sqlalchemy.orm import Query
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID
from app.models.business.inventory import MaterialOutboundOrder, MaterialOutboundOrderDetail, Inventory, InventoryTransaction
from app.models.basic_data import Unit
from app.services.base_service import TenantAwareService
from flask import g, current_app
import logging
import uuid

logger = logging.getLogger(__name__)


class MaterialOutboundService(TenantAwareService):
    """
    材料出库服务类
    提供材料出库单相关的业务逻辑操作
    """
    
    def _fill_warehouse_info(self, orders: List[MaterialOutboundOrder]) -> None:
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
                elif not hasattr(order, 'warehouse_name') or not order.warehouse_name:
                    order.warehouse_name = '未知仓库'
        except Exception as e:
            current_app.logger.warning(f"填充仓库信息失败: {e}")
            # 失败时使用默认值
            for order in orders:
                if not hasattr(order, 'warehouse_name') or not order.warehouse_name:
                    order.warehouse_name = '未知仓库'

    def get_material_outbound_order_list(
        self,
        warehouse_id: Optional[str] = None,
        order_type: Optional[str] = None,
        status: Optional[str] = None,
        approval_status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取材料出库单列表"""
        from sqlalchemy.orm import joinedload
        query: Query = self.session.query(MaterialOutboundOrder).options(
            joinedload(MaterialOutboundOrder.outbound_person),
            joinedload(MaterialOutboundOrder.department),
            joinedload(MaterialOutboundOrder.requisition_department),
            joinedload(MaterialOutboundOrder.requisition_person)
        )
        
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
                MaterialOutboundOrder.requisition_purpose.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        total: int = query.count()
        
        orders: List[MaterialOutboundOrder] = query.order_by(MaterialOutboundOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
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
        from sqlalchemy.orm import joinedload
        order: Optional[MaterialOutboundOrder] = self.session.query(MaterialOutboundOrder).options(
            joinedload(MaterialOutboundOrder.outbound_person),
            joinedload(MaterialOutboundOrder.department),
            joinedload(MaterialOutboundOrder.requisition_department),
            joinedload(MaterialOutboundOrder.requisition_person)
        ).filter(MaterialOutboundOrder.id == order_id).first()
        
        if order:
            # 填充仓库信息
            self._fill_warehouse_info([order])
        
        return order

    def get_material_outbound_order_details(self, order_id: str) -> List[Dict[str, Any]]:
        """获取材料出库单明细"""
        details: List[MaterialOutboundOrderDetail] = self.session.query(MaterialOutboundOrderDetail).filter(
            MaterialOutboundOrderDetail.material_outbound_order_id == order_id
        ).all()
        
        return [detail.to_dict() for detail in details]

    def create_material_outbound_order(
        self,
        data: Dict[str, Any],
        created_by: str
    ) -> MaterialOutboundOrder:
        """创建材料出库单"""
        try:
            # 转换created_by为UUID
            created_by_uuid: Union[UUID, str]
            try:
                created_by_uuid = uuid.UUID(created_by)
            except (TypeError, ValueError):
                created_by_uuid = created_by
            
            # 提取明细数据
            details_data: List[Dict[str, Any]] = data.pop('details', [])
            
            # 复制数据并处理warehouse_id
            order_data = data.copy()
            order_data['warehouse_id'] = uuid.UUID(order_data['warehouse_id'])
            order_data['created_by'] = created_by_uuid
            
            # 设置默认值
            if 'order_type' not in order_data:
                order_data['order_type'] = 'material'
            
            # 使用继承的create_with_tenant方法
            order: MaterialOutboundOrder = self.create_with_tenant(MaterialOutboundOrder, **order_data)
            
            self.session.flush()  # 获取order.id
            
            # 创建明细
            if details_data:
                for detail_data in details_data:
                    # 处理unit_id字段
                    unit_id = detail_data.get('unit_id')
                    if not unit_id and detail_data.get('unit'):
                        # 如果没有unit_id但有unit字段，尝试从units表中查找对应的unit_id
                        unit = self.session.query(Unit).filter(Unit.unit_name == detail_data['unit']).first()
                        if unit:
                            unit_id = unit.id
                        else:
                            # 如果找不到对应的单位，抛出错误
                            raise ValueError(f"明细缺少必需的unit_id参数")
                    
                    if not unit_id:
                        raise ValueError(f"明细缺少必需的unit_id参数")
                    
                    # 提取必需的位置参数
                    outbound_quantity = Decimal(detail_data.get('outbound_quantity', 0))
                    
                    # 创建明细
                    material_id = detail_data.get('material_id')
                    if material_id:
                        material_id = uuid.UUID(material_id)
                    
                    detail = MaterialOutboundOrderDetail(
                        material_outbound_order_id=order.id,
                        outbound_quantity=outbound_quantity,
                        unit_id=unit_id,
                        created_by=created_by_uuid,
                        material_id=material_id,
                        material_name=detail_data.get('material_name'),
                        material_code=detail_data.get('material_code'),
                        material_spec=detail_data.get('specification'),
                        batch_number=detail_data.get('batch_number'),
                        location_code=detail_data.get('location_code'),
                        notes=detail_data.get('remarks')
                    )
                    self.session.add(detail)
            
            self.session.commit()
            return order
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"创建材料出库单失败: {e}")
            raise e

    def update_material_outbound_order(
        self,
        order_id: str,
        updated_by: str,
        **update_data
    ) -> Optional[MaterialOutboundOrder]:
        """更新材料出库单"""
        order = self.session.query(MaterialOutboundOrder).filter(MaterialOutboundOrder.id == order_id).first()
        
        if not order:
            return None
        
        # 更新字段
        for key, value in update_data.items():
            if hasattr(order, key) and key not in ['id', 'created_at', 'created_by']:
                setattr(order, key, value)
        
        order.updated_by = uuid.UUID(updated_by) if isinstance(updated_by, str) else updated_by
        order.updated_at = datetime.now()
        
        self.commit()
        self.session.refresh(order)
        
        return order

    def create_material_outbound_order_detail(self, order_id: str, data: Dict[str, Any], created_by: str) -> MaterialOutboundOrderDetail:
        """创建材料出库单明细"""
        # 清理数据，移除SQLAlchemy内部属性
        detail_data = {}
        for key, value in data.items():
            if not key.startswith('_') and key not in ['_sa_instance_state']:
                detail_data[key] = value
        
        # 处理unit_id字段
        unit_id = detail_data.get('unit_id')
        if not unit_id and detail_data.get('unit'):
            # 如果没有unit_id但有unit字段，尝试从units表中查找对应的unit_id
            unit = self.session.query(Unit).filter(Unit.unit_name == detail_data['unit']).first()
            if unit:
                unit_id = unit.id
            else:
                # 如果找不到对应的单位，抛出错误
                raise ValueError(f"明细缺少必需单位的数据")
        
        if not unit_id:
            raise ValueError(f"明细缺少必需的unit_id参数")
        
        # 处理外键字段的UUID转换
        for key in ['material_id']:
            if key in detail_data and detail_data[key]:
                detail_data[key] = uuid.UUID(detail_data[key])
        
        # 明确设置必需字段
        detail = MaterialOutboundOrderDetail(
            material_outbound_order_id=uuid.UUID(order_id),
            created_by=uuid.UUID(created_by) if isinstance(created_by, str) else created_by,
            outbound_quantity=Decimal(detail_data.get('outbound_quantity', 0)),
            unit_id=unit_id,
            material_id=detail_data.get('material_id'),
            material_name=detail_data.get('material_name'),
            material_code=detail_data.get('material_code'),
            material_spec=detail_data.get('material_spec'),
            batch_number=detail_data.get('batch_number'),
            location_code=detail_data.get('location_code'),
            notes=detail_data.get('notes')
        )   
        self.session.add(detail)
        self.commit()
        self.session.refresh(detail)
        return detail

    def update_material_outbound_order_detail(self, detail_id: str, data: Dict[str, Any], updated_by: str) -> bool:
        """更新材料出库单明细"""
        detail = self.session.query(MaterialOutboundOrderDetail).filter(
            MaterialOutboundOrderDetail.id == detail_id
        ).first()
        
        if not detail:
            return False

        # 清理数据，移除SQLAlchemy内部属性
        clean_data = {}
        for key, value in data.items():
            if not key.startswith('_') and key not in ['_sa_instance_state', 'id', 'created_at', 'created_by']:
                clean_data[key] = value

        # 处理unit_id字段
        if 'unit_id' in clean_data or 'unit' in clean_data:
            unit_id = clean_data.get('unit_id')
            if not unit_id and clean_data.get('unit'):
                # 如果没有unit_id但有unit字段，尝试从units表中查找对应的unit_id
                unit = self.session.query(Unit).filter(Unit.unit_name == clean_data['unit']).first()
                if unit:
                    unit_id = unit.id
                else:
                    # 如果找不到对应的单位，抛出错误
                    raise ValueError(f"明细缺少必需单位的数据")
            
            if unit_id:
                detail.unit_id = unit_id

        for key, value in clean_data.items():
            if hasattr(detail, key) and key not in ['unit_id', 'unit']:  # unit_id已经单独处理
                # 处理外键字段的UUID转换
                if key in ['material_id', 'outbound_order_id'] and value:
                    setattr(detail, key, uuid.UUID(value))
                elif key == 'outbound_quantity':
                    setattr(detail, key, Decimal(value))
                else:
                    setattr(detail, key, value)

        detail.updated_by = uuid.UUID(updated_by) if isinstance(updated_by, str) else updated_by
        detail.updated_at = datetime.now()

        self.commit()

        return True


    def delete_material_outbound_order_detail(self, detail_id: str) -> bool:
        """删除材料出库单明细"""
        detail = self.session.query(MaterialOutboundOrderDetail).filter(
            MaterialOutboundOrderDetail.id == detail_id
        ).first()
        
        if not detail:
            return False
        
        self.session.delete(detail)
        self.commit()
        
        return True


    def approve_material_outbound_order(
        self,
        order_id: str,
        approved_by: str,
        approval_status: str = 'approved'
    ) -> MaterialOutboundOrder:
        """审核材料出库单"""
        order = self.session.query(MaterialOutboundOrder).filter(MaterialOutboundOrder.id == order_id).first()
        
        if not order:
            raise ValueError("材料出库单不存在")
        
        if order.approval_status != 'pending':
            raise ValueError("材料出库单已经审核过")
        
        # 检查是否有明细
        details = self.session.query(MaterialOutboundOrderDetail).filter(
            MaterialOutboundOrderDetail.material_outbound_order_id == order_id
        ).all()
        
        if not details:
            raise ValueError("材料出库单没有明细，无法审核")
        
        order.approval_status = approval_status
        order.approved_by = uuid.UUID(approved_by) if isinstance(approved_by, str) else approved_by
        order.approved_at = datetime.now()
        
        if approval_status == 'approved':
            order.status = 'confirmed'
        
        self.commit()
        self.session.refresh(order)
        
        return order

    def execute_material_outbound_order(
        self,
        order_id: str,
        executed_by: str
    ) -> List[InventoryTransaction]:
        """执行材料出库单"""
        order = self.session.query(MaterialOutboundOrder).filter(MaterialOutboundOrder.id == order_id).first()
        
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
            inventory = self.session.query(Inventory).filter(
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
                unit_id=detail.unit_id,
                unit_price=detail.unit_price,
                source_document_type='material_outbound_order',
                source_document_id=order.id,
                source_document_number=order.order_number,
                batch_number=detail.batch_number,
                from_location=detail.location_code,
                reason=f"材料出库单执行: {order.order_number}",
                created_by=executed_by
            )
            
            self.session.add(transaction)
            transactions.append(transaction)
        
        # 更新出库单状态
        order.status = 'completed'
        order.updated_by = executed_by
        order.updated_at = datetime.now()
        
        self.commit()
        
        return transactions

    def cancel_material_outbound_order(
        self,
        order_id: str,
        cancelled_by: str,
        cancel_reason: str = None
    ) -> MaterialOutboundOrder:
        """取消材料出库单"""
        order = self.session.query(MaterialOutboundOrder).filter(MaterialOutboundOrder.id == order_id).first()
        
        if not order:
            raise ValueError("材料出库单不存在")
        
        if order.status == 'completed':
            raise ValueError("已执行的材料出库单不能取消")
        
        order.status = 'cancelled'
        order.approval_status = 'rejected'
        order.remark = f"{order.remark or ''}\n取消原因: {cancel_reason or '用户取消'}"
        order.updated_by = uuid.UUID(cancelled_by) if isinstance(cancelled_by, str) else cancelled_by
        order.updated_at = datetime.now()
        
        self.commit()
        self.session.refresh(order)
        
        return order


def get_material_outbound_service(tenant_id: str = None, schema_name: str = None) -> MaterialOutboundService:
    """获取材料出库服务实例"""
    return MaterialOutboundService(tenant_id=tenant_id, schema_name=schema_name) 