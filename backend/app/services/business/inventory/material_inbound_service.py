# -*- coding: utf-8 -*-
# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
材料入库服务
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID
from app.models.business.inventory import MaterialInboundOrder, MaterialInboundOrderDetail, Inventory, InventoryTransaction
from app.extensions import db
from flask import g, current_app
import logging
import uuid
from app.services.base_service import TenantAwareService

logger = logging.getLogger(__name__)


class MaterialInboundService(TenantAwareService):
    """
    材料入库服务类
    提供材料入库单相关的业务逻辑操作
    """
    
    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        super().__init__(tenant_id, schema_name, strict_tenant_check=True)

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
            warehouses = self.get_session().query(Warehouse).filter(Warehouse.id.in_(warehouse_ids)).all()
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

    def _fill_department_info(self, orders):
        """批量填充订单的部门名称信息"""
        if not orders:
            return
        
        # 获取所有部门字段值（可能是UUID或者已经是名称）
        department_values = list(set([order.department for order in orders if order.department]))
        
        if not department_values:
            return
        
        try:
            # 尝试将部门值当作UUID查询
            from app.models.organization import Department
            import uuid
            
            department_uuids = []
            for dept_val in department_values:
                try:
                    dept_uuid = uuid.UUID(dept_val)
                    department_uuids.append(dept_uuid)
                except (TypeError):
                    # 不是UUID，跳过
                    continue
            
            if department_uuids:
                # 查询部门信息
                departments = self.get_session().query(Department).filter(Department.id.in_(department_uuids)).all()
                department_dict = {str(d.id): d.department_name for d in departments}
                
                # 填充部门名称
                for order in orders:
                    if order.department and order.department in department_dict:
                        order.department = department_dict[order.department]
        except Exception as e:
            current_app.logger.warning(f"填充部门信息失败: {e}")
            # 失败时保持原值
            pass

    def get_material_inbound_order_list(
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
        """获取材料入库单列表"""
        from sqlalchemy.orm import joinedload
        query = self.get_session().query(MaterialInboundOrder).options(
            joinedload(MaterialInboundOrder.inbound_person),
            joinedload(MaterialInboundOrder.department)
        )
        
        if warehouse_id:
            query = query.filter(MaterialInboundOrder.warehouse_id == warehouse_id)
        
        if order_type:
            query = query.filter(MaterialInboundOrder.order_type == order_type)
        
        if status:
            query = query.filter(MaterialInboundOrder.status == status)
        
        if approval_status:
            query = query.filter(MaterialInboundOrder.approval_status == approval_status)
        
        if start_date:
            query = query.filter(MaterialInboundOrder.order_date >= start_date)
        
        if end_date:
            query = query.filter(MaterialInboundOrder.order_date <= end_date)
        
        if search:
            search_filter = or_(
                MaterialInboundOrder.order_number.ilike(f'%{search}%'),
                MaterialInboundOrder.supplier_name.ilike(f'%{search}%'),
                MaterialInboundOrder.notes.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        total = query.count()
        
        orders = query.order_by(MaterialInboundOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 填充仓库信息
        self._fill_warehouse_info(orders)
        
        # 填充部门信息
        self._fill_department_info(orders)
        
        return {
            'items': [order.to_dict() for order in orders],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }

    def get_material_inbound_order_by_id(self, order_id: str) -> Optional[MaterialInboundOrder]:
        """根据ID获取材料入库单详情"""
        from sqlalchemy.orm import joinedload
        order = self.get_session().query(MaterialInboundOrder).options(
            joinedload(MaterialInboundOrder.inbound_person),
            joinedload(MaterialInboundOrder.department)
        ).filter(MaterialInboundOrder.id == order_id).first()
        
        if order:
            # 填充仓库信息
            self._fill_warehouse_info([order])
            # 填充部门信息
            self._fill_department_info([order])
        
        return order

    def get_material_inbound_order_details(self, order_id: str) -> List[Dict[str, Any]]:
        """获取材料入库单明细"""
        details = self.get_session().query(MaterialInboundOrderDetail).filter(
            MaterialInboundOrderDetail.material_inbound_order_id == order_id
        ).all()
        
        return [detail.to_dict() for detail in details]

    def create_material_inbound_order(
        self,
        data: dict,
        created_by: str
    ) -> MaterialInboundOrder:
        """创建材料入库单"""
        
        # 转换created_by为UUID
        try:
            created_by_uuid = uuid.UUID(created_by)
        except (TypeError):
            created_by_uuid = created_by
        
        # 提取明细数据和一些特殊字段，避免重复参数
        details_data = data.pop('details', [])
        warehouse_id = data.pop('warehouse_id')
        order_type = data.pop('order_type', 'material')
        
        # 转换日期字段
        if 'order_date' in data and isinstance(data['order_date'], str):
            data['order_date'] = datetime.fromisoformat(data['order_date'].replace('Z', '+00:00'))
        
        # 处理UUID字段
        if 'inbound_person_id' in data and data['inbound_person_id']:
            data['inbound_person_id'] = uuid.UUID(data['inbound_person_id'])
        if 'department_id' in data and data['department_id']:
            data['department_id'] = uuid.UUID(data['department_id'])
        if 'supplier_id' in data and data['supplier_id']:
            data['supplier_id'] = uuid.UUID(data['supplier_id'])
        
        order = MaterialInboundOrder(
            warehouse_id=uuid.UUID(warehouse_id),
            order_type=order_type,
            created_by=created_by_uuid,
            **data
        )
        
        self.get_session().add(order)
        self.get_session().flush()  # 获取order.id
        
        # 创建明细
        if details_data:
            for detail_data in details_data:
                detail = MaterialInboundOrderDetail(
                    material_inbound_order_id=order.id,
                    inbound_quantity=Decimal(detail_data['inbound_quantity']),
                    unit=detail_data['unit'],
                    created_by=created_by_uuid,
                    **{k: v for k, v in detail_data.items() if k not in ['inbound_quantity', 'unit']}
                )
                self.get_session().add(detail)
        
        self.commit()
        
        # 填充仓库信息
        self._fill_warehouse_info([order])
        # 填充部门信息
        self._fill_department_info([order])
        
        return order

    def update_material_inbound_order(
        self,
        order_id: str,
        updated_by: str,
        **update_data
    ) -> Optional[MaterialInboundOrder]:
        """更新材料入库单"""
        order = self.get_session().query(MaterialInboundOrder).filter(MaterialInboundOrder.id == order_id).first()
        
        if not order:
            return None
        
        # 提取明细数据
        details_data = update_data.pop('details', None)
        
        # 过滤掉SQLAlchemy内部属性和不允许更新的字段
        forbidden_fields = ['id', 'created_at', 'created_by', '_sa_instance_state', '_state']
        allowed_data = {k: v for k, v in update_data.items() 
                       if k not in forbidden_fields and hasattr(order, k)}
        
        # 处理特殊字段
        if 'warehouse_id' in allowed_data:
            allowed_data['warehouse_id'] = uuid.UUID(allowed_data['warehouse_id']) if isinstance(allowed_data['warehouse_id'], str) else allowed_data['warehouse_id']
        
        if 'order_date' in allowed_data and isinstance(allowed_data['order_date'], str):
            try:
                allowed_data['order_date'] = datetime.fromisoformat(allowed_data['order_date'].replace('Z', '+00:00')).date()
            except:
                # 如果转换失败，保持原值
                pass
        
        # 更新字段
        for key, value in allowed_data.items():
            setattr(order, key, value)
        
        order.updated_by = uuid.UUID(updated_by) if isinstance(updated_by, str) else updated_by
        # 删除显式设置updated_at，让数据库自动处理
        
        # 处理明细数据更新
        if details_data is not None:
            # 删除现有明细
            self.get_session().query(MaterialInboundOrderDetail).filter(
                MaterialInboundOrderDetail.material_inbound_order_id == order.id
            ).delete()
            
            # 添加新明细
            for detail_data in details_data:
                if detail_data.get('material_id') and detail_data.get('inbound_quantity'):
                    detail = MaterialInboundOrderDetail(
                        material_inbound_order_id=order.id,
                        material_id=uuid.UUID(detail_data['material_id']),
                        material_name=detail_data.get('material_name'),
                        material_code=detail_data.get('material_code'),
                        material_spec=detail_data.get('specification'),
                        inbound_quantity=Decimal(str(detail_data['inbound_quantity'])),
                        inbound_weight=Decimal(str(detail_data['inbound_weight'])) if detail_data.get('inbound_weight') else None,
                        inbound_length=Decimal(str(detail_data['inbound_length'])) if detail_data.get('inbound_length') else None,
                        inbound_rolls=int(detail_data['inbound_rolls']) if detail_data.get('inbound_rolls') else None,
                        unit=detail_data.get('unit', '个'),
                        batch_number=detail_data.get('batch_number'),
                        unit_price=Decimal(str(detail_data['unit_price'])) if detail_data.get('unit_price') else None,
                        notes=detail_data.get('notes'),
                        created_by=uuid.UUID(updated_by) if isinstance(updated_by, str) else updated_by
                    )
                    self.get_session().add(detail)
        
        self.commit()
        
        return order

    def add_material_inbound_order_detail(
        self,
        order_id: str,
        inbound_quantity: Decimal,
        unit: str,
        created_by: str,
        material_id: str = None,
        material_name: str = None,
        **kwargs
    ) -> MaterialInboundOrderDetail:
        """添加材料入库单明细"""
        
        detail = MaterialInboundOrderDetail(
            material_inbound_order_id=uuid.UUID(order_id),
            material_id=uuid.UUID(material_id) if material_id else None,
            material_name=material_name,
            inbound_quantity=inbound_quantity,
            unit=unit,
            created_by=uuid.UUID(created_by) if isinstance(created_by, str) else created_by,
            **kwargs
        )
        
        self.get_session().add(detail)
        self.commit()
        
        return detail

    def update_material_inbound_order_detail(
        self,
        detail_id: str,
        updated_by: str,
        **update_data
    ) -> Optional[MaterialInboundOrderDetail]:
        """更新材料入库单明细"""
        detail = self.get_session().query(MaterialInboundOrderDetail).filter(
            MaterialInboundOrderDetail.id == detail_id
        ).first()
        
        if not detail:
            return None
        
        # 更新字段
        for key, value in update_data.items():
            if hasattr(detail, key) and key not in ['id', 'created_at', 'created_by']:
                if key == 'inbound_quantity' and value is not None:
                    value = Decimal(value)
                setattr(detail, key, value)
        
        detail.updated_by = uuid.UUID(updated_by) if isinstance(updated_by, str) else updated_by
        # 删除显式设置updated_at，让数据库自动处理
        
        self.commit()
        
        return detail

    def delete_material_inbound_order_detail(self, detail_id: str) -> bool:
        """删除材料入库单明细"""
        detail = self.get_session().query(MaterialInboundOrderDetail).filter(
            MaterialInboundOrderDetail.id == detail_id
        ).first()
        
        if not detail:
            return False
        
        self.get_session().delete(detail)
        self.commit()
        
        return True

    def approve_material_inbound_order(
        self,
        order_id: str,
        approved_by: str,
        approval_status: str = 'approved'
    ) -> MaterialInboundOrder:
        """审核材料入库单"""
        order = self.get_session().query(MaterialInboundOrder).filter(MaterialInboundOrder.id == order_id).first()
        
        if not order:
            raise ValueError("材料入库单不存在")
        
        if order.approval_status != 'pending':
            raise ValueError("材料入库单已经审核过")
        
        order.approval_status = approval_status
        order.approved_by = uuid.UUID(approved_by) if isinstance(approved_by, str) else approved_by
        order.approved_at = datetime.now()
        
        if approval_status == 'approved':
            order.status = 'confirmed'
        
        self.commit()
        
        return order

    def execute_material_inbound_order(
        self,
        order_id: str,
        executed_by: str,
        auto_create_inventory: bool = True
    ) -> List[InventoryTransaction]:
        """执行材料入库单"""
        order = self.get_session().query(MaterialInboundOrder).filter(MaterialInboundOrder.id == order_id).first()
        
        if not order:
            raise ValueError("材料入库单不存在")
        
        if order.approval_status != 'approved':
            raise ValueError("材料入库单未审核，不能执行")
        
        if order.status == 'completed':
            raise ValueError("材料入库单已经执行")
        
        transactions = []
        
        # 处理每个明细行
        for detail in order.details:
            if not detail.material_id:
                continue
            
            # 查找或创建库存记录
            inventory = self.get_session().query(Inventory).filter(
                and_(
                    Inventory.warehouse_id == order.warehouse_id,
                    Inventory.material_id == detail.material_id,
                    Inventory.batch_number == detail.batch_number,
                    Inventory.is_active == True
                )
            ).first()
            
            if not inventory and auto_create_inventory:
                # 创建新的库存记录
                inventory = Inventory(
                    warehouse_id=order.warehouse_id,
                    material_id=detail.material_id,
                    unit=detail.unit,
                    batch_number=detail.batch_number,
                    production_date=detail.production_date,
                    expiry_date=detail.expiry_date,
                    location_code=detail.actual_location_code or detail.location_code,
                    created_by=uuid.UUID(executed_by) if isinstance(executed_by, str) else executed_by
                )
                self.get_session().add(inventory)
                self.get_session().flush()
            
            if inventory:
                # 记录变动前数量
                quantity_before = inventory.current_quantity
                
                # 更新库存数量
                inventory.current_quantity += detail.inbound_quantity
                inventory.available_quantity += detail.inbound_quantity
                
                # 更新成本信息
                if detail.unit_price:
                    total_cost = inventory.total_cost or Decimal('0')
                    total_quantity = inventory.current_quantity
                    new_cost = detail.inbound_quantity * detail.unit_price
                    
                    inventory.total_cost = total_cost + new_cost
                    if total_quantity > 0:
                        inventory.unit_cost = inventory.total_cost / total_quantity
                
                inventory.updated_by = uuid.UUID(executed_by) if isinstance(executed_by, str) else executed_by
                # 删除显式设置updated_at，让数据库自动处理
                
                # 创建库存流水记录
                transaction = InventoryTransaction(
                    inventory_id=inventory.id,
                    warehouse_id=order.warehouse_id,
                    material_id=detail.material_id,
                    transaction_type='in',
                    quantity_change=detail.inbound_quantity,
                    quantity_before=quantity_before,
                    quantity_after=inventory.current_quantity,
                    unit=detail.unit,
                    unit_price=detail.unit_price,
                    source_document_type='material_inbound_order',
                    source_document_id=order.id,
                    source_document_number=order.order_number,
                    batch_number=detail.batch_number,
                    to_location=detail.actual_location_code or detail.location_code,
                    supplier_id=order.supplier_id,
                    created_by=uuid.UUID(executed_by) if isinstance(executed_by, str) else executed_by
                )
                
                self.get_session().add(transaction)
                transactions.append(transaction)
        
        # 更新入库单状态
        order.status = 'completed'
        order.updated_by = uuid.UUID(executed_by) if isinstance(executed_by, str) else executed_by
        # 删除显式设置updated_at，让数据库自动处理
        
        self.commit()
        
        return transactions

    def submit_material_inbound_order(
        self,
        order_id: str,
        submitted_by: str
    ) -> MaterialInboundOrder:
        """提交材料入库单"""
        order = self.get_session().query(MaterialInboundOrder).filter(MaterialInboundOrder.id == order_id).first()
        
        if not order:
            raise ValueError("材料入库单不存在")
        
        if order.status != 'draft':
            raise ValueError("只能提交草稿状态的入库单")
        
        # 简化流程：提交后自动审核通过
        order.status = 'confirmed'
        order.approval_status = 'approved'
        order.approved_by = uuid.UUID(submitted_by) if isinstance(submitted_by, str) else submitted_by
        order.approved_at = datetime.now()
        order.updated_by = uuid.UUID(submitted_by) if isinstance(submitted_by, str) else submitted_by
        # 删除显式设置updated_at，让数据库自动处理
        
        self.commit()
        
        return order

    def cancel_material_inbound_order(
        self,
        order_id: str,
        cancelled_by: str,
        cancel_reason: str = None
    ) -> MaterialInboundOrder:
        """取消材料入库单"""
        order = self.get_session().query(MaterialInboundOrder).filter(MaterialInboundOrder.id == order_id).first()
        
        if not order:
            raise ValueError("材料入库单不存在")
        
        if order.status == 'completed':
            raise ValueError("已执行的材料入库单不能取消")
        
        order.status = 'cancelled'
        order.approval_status = 'rejected'
        order.notes = f"{order.notes or ''}\n取消原因: {cancel_reason or '用户取消'}"
        order.updated_by = uuid.UUID(cancelled_by) if isinstance(cancelled_by, str) else cancelled_by
        # 删除显式设置updated_at，让数据库自动处理
        
        self.commit()
        
        return order


def get_material_inbound_service(tenant_id: Optional[str] = None, schema_name: Optional[str] = None) -> MaterialInboundService:
    """获取材料入库服务实例"""
    return MaterialInboundService(tenant_id, schema_name) 