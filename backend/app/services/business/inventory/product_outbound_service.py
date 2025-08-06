# -*- coding: utf-8 -*-
# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
产品出库服务
"""

from typing import Dict, List, Optional, Any
from sqlalchemy import func, and_, or_, desc, text
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID
from app.models.business.inventory import OutboundOrder, OutboundOrderDetail, Inventory, InventoryTransaction
from app.models.basic_data import Unit
from app.services.base_service import TenantAwareService
from flask import g, current_app
import logging
import uuid

logger = logging.getLogger(__name__)


class ProductOutboundService(TenantAwareService):
    """
    产品出库管理服务类
    提供产品出库相关的业务逻辑操作
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

    def get_outbound_order_list(
        self,
        warehouse_id: str = None,
        status: str = None,
        approval_status: str = None,
        start_date: str = None,
        end_date: str = None,
        search: str = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取出库单列表"""
        from sqlalchemy.orm import joinedload
        query = self.session.query(OutboundOrder).options(
            joinedload(OutboundOrder.outbound_person),
            joinedload(OutboundOrder.department)
        )
        
        if warehouse_id:
            query = query.filter(OutboundOrder.warehouse_id == warehouse_id)
        
        if status:
            query = query.filter(OutboundOrder.status == status)
        
        if approval_status:
            query = query.filter(OutboundOrder.approval_status == approval_status)
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(OutboundOrder.order_date >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(OutboundOrder.order_date <= end_dt)
            except ValueError:
                pass
        
        if search:
            search_filter = or_(
                OutboundOrder.order_number.ilike(f'%{search}%'),
                OutboundOrder.warehouse_name.ilike(f'%{search}%'),
                OutboundOrder.customer_name.ilike(f'%{search}%'),
                OutboundOrder.remark.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        orders = query.order_by(OutboundOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 填充仓库信息
        self._fill_warehouse_info(orders)
        
        return {
            'items': [order.to_dict() for order in orders],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }

    def get_outbound_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取出库单详情"""
        from sqlalchemy.orm import joinedload
        order = self.session.query(OutboundOrder).options(
            joinedload(OutboundOrder.outbound_person),
            joinedload(OutboundOrder.department)
        ).filter(OutboundOrder.id == order_id).first()
        
        if not order:
            return None
        
        # 填充仓库信息
        self._fill_warehouse_info([order])
        
        return order.to_dict()

    def create_outbound_order(self, data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """创建出库单（支持同时创建明细）"""
        try:
            # 生成出库单号 - 使用顺序生成
            from app.models.business.inventory import OutboundOrder
            order_number = OutboundOrder.generate_order_number('finished_goods')
            
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
                'order_type': data.get('order_type', 'finished_goods'),
                'order_number': order_number,
                'order_date': datetime.strptime(data['order_date'], '%Y-%m-%d') if data.get('order_date') else datetime.now(),
                'status': 'draft',
                'approval_status': 'pending',
                'outbound_person_id': uuid.UUID(data['outbound_person_id']) if data.get('outbound_person_id') else None,
                'department_id': uuid.UUID(data['department_id']) if data.get('department_id') else None,
                'customer_name': data.get('customer_name', ''),
                'customer_id': uuid.UUID(data['customer_id']) if data.get('customer_id') else None,
                'pallet_count': data.get('pallet_count', 0),
                'remark': data.get('remark', '')
            }
            
            # 使用继承的create_with_tenant方法
            order = self.create_with_tenant(OutboundOrder, **order_data)
            self.session.flush()  # 获取order.id
            # 创建明细
            if details_data:
                for detail_data in details_data:
                    detail_params = {
                        'outbound_order_id': order.id,
                        'outbound_quantity': Decimal(str(detail_data.get('outbound_quantity', 0))),
                        'unit_id': uuid.UUID(detail_data.get('unit_id')) if detail_data.get('unit_id') else None,
                        'product_id': detail_data.get('product_id', None),
                        'product_name': detail_data.get('product_name', None),
                        'product_code': detail_data.get('product_code', None),
                        'product_spec': detail_data.get('product_spec', None),
                        'batch_number': detail_data.get('batch_number', None),
                        'notes': detail_data.get('notes', None)
                    }
                    
                    # 创建明细
                    detail = self.create_with_tenant(OutboundOrderDetail, **detail_params)
            
            self.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([order])
            
            return order.to_dict()
            
        except Exception as e:
            self.rollback()
            logger.error(f"创建出库单失败: {e}")
            raise e

    def update_outbound_order(self, order_id: str, data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """更新出库单（支持同时更新明细）"""
        try:
            order = self.session.query(OutboundOrder).filter(OutboundOrder.id == order_id).first()
            
            if not order:
                raise ValueError(f"出库单不存在: {order_id}")
            
            # 检查状态是否允许更新
            if order.status not in ['draft', 'confirmed']:
                raise ValueError("只有草稿和已确认状态的出库单可以更新")
            
            # 提取明细数据
            details_data = data.pop('details', None)
            
            # 更新主表字段
            for key, value in data.items():
                if hasattr(order, key) and key not in ['id', 'order_number', 'created_by', 'created_at']:
                    if key == 'order_date' and isinstance(value, str):
                        order.order_date = datetime.strptime(value, '%Y-%m-%d')
                    elif key == 'warehouse_id' and isinstance(value, str):
                        order.warehouse_id = uuid.UUID(value)
                    elif key == 'customer_id' and isinstance(value, str):
                        order.customer_id = uuid.UUID(value)
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
                self.session.query(OutboundOrderDetail).filter(
                    OutboundOrderDetail.outbound_order_id == order_id
                ).delete()
                
                # 创建新明细
                for detail_data in details_data:
                    # 处理单位字段：优先使用unit_id，如果没有则使用unit
                    unit_id = None
                    if detail_data.get('unit_id'):
                        unit_id = uuid.UUID(detail_data['unit_id'])
                    elif detail_data.get('unit'):
                        unit_id = uuid.UUID(detail_data['unit'])
                    
                    # 如果仍然没有单位，尝试获取默认单位
                    if not unit_id:
                        # 查询默认单位（kg或个）
                        default_unit = self.session.query(Unit).filter(
                            Unit.unit_name.in_(['kg', '个', 'm²'])
                        ).first()
                        if default_unit:
                            unit_id = default_unit.id
                        else:
                            # 如果连默认单位都没有，获取第一个可用单位
                            first_unit = self.session.query(Unit).first()
                            if first_unit:
                                unit_id = first_unit.id
                    
                    if not unit_id:
                        raise ValueError("无法确定单位，请检查单位配置")
                    
                    detail = OutboundOrderDetail(
                        outbound_order_id=order.id,
                        outbound_quantity=Decimal(str(detail_data.get('outbound_quantity', 0))),
                        unit_id=unit_id,
                        created_by=updated_by_uuid
                    )
                    
                    # 设置其他明细字段
                    if detail_data.get('product_id'):
                        detail.product_id = uuid.UUID(detail_data['product_id'])
                    detail.product_name = detail_data.get('product_name', '')
                    detail.product_code = detail_data.get('product_code', '')
                    detail.product_spec = detail_data.get('product_spec', '')
                    detail.batch_number = detail_data.get('batch_number', '')
                    detail.location_code = detail_data.get('location_code', '')
                    
                    if detail_data.get('outbound_kg_quantity'):
                        detail.outbound_kg_quantity = Decimal(str(detail_data['outbound_kg_quantity']))
                    if detail_data.get('outbound_m_quantity'):
                        detail.outbound_m_quantity = Decimal(str(detail_data['outbound_m_quantity']))
                    if detail_data.get('outbound_roll_quantity'):
                        detail.outbound_roll_quantity = Decimal(str(detail_data['outbound_roll_quantity']))
                    if detail_data.get('box_quantity'):
                        detail.box_quantity = Decimal(str(detail_data['box_quantity']))
                    if detail_data.get('unit_cost'):
                        detail.unit_cost = Decimal(str(detail_data['unit_cost']))
                    
                    self.session.add(detail)
            
            self.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([order])
            
            return order.to_dict()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"更新出库单失败: {str(e)}")
            raise ValueError(f"更新出库单失败: {str(e)}")

    def delete_outbound_order(self, order_id: str) -> bool:
        """删除出库单"""
        try:
            order = self.session.query(OutboundOrder).filter(OutboundOrder.id == order_id).first()
            
            if not order:
                raise ValueError(f"出库单不存在: {order_id}")
            
            # 检查状态是否允许删除
            if order.status not in ['draft']:
                raise ValueError("只有草稿状态的出库单可以删除")
            
            self.session.delete(order)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"删除出库单失败: {str(e)}")
            raise ValueError(f"删除出库单失败: {str(e)}")

    def approve_outbound_order(self, order_id: str, approval_data: Dict[str, Any], approved_by: str) -> Dict[str, Any]:
        """审核出库单"""
        try:
            order = self.session.query(OutboundOrder).filter(OutboundOrder.id == order_id).first()
            
            if not order:
                raise ValueError(f"出库单不存在: {order_id}")
            
            # 检查状态
            if order.status not in ['draft', 'confirmed']:
                raise ValueError("只有草稿和已确认状态的出库单可以审核")
            
            # 检查是否有明细
            details = self.session.query(OutboundOrderDetail).filter(
                OutboundOrderDetail.outbound_order_id == order_id
            ).all()
            
            if not details:
                raise ValueError("出库单没有明细，无法审核")
            
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
            current_app.logger.error(f"审核出库单失败: {str(e)}")
            raise ValueError(f"审核出库单失败: {str(e)}")

    def execute_outbound_order(self, order_id: str, executed_by: str) -> Dict[str, Any]:
        """执行出库单（扣减库存）"""
        try:
            order = self.session.query(OutboundOrder).filter(OutboundOrder.id == order_id).first()
            
            if not order:
                raise ValueError(f"出库单不存在: {order_id}")
            
            # 检查状态
            if order.status != 'confirmed' or order.approval_status != 'approved':
                raise ValueError("只有已确认且已审核的出库单可以执行")
            
            # 获取出库单明细
            details = self.session.query(OutboundOrderDetail).filter(
                OutboundOrderDetail.outbound_order_id == order_id
            ).all()
            
            if not details:
                raise ValueError("出库单没有明细，无法执行")
            
            executed_by_uuid = uuid.UUID(executed_by)
            transactions = []
            
            # 执行库存扣减
            for detail in details:
                if not detail.product_id:
                    continue
                    
                # 查找对应的库存记录
                inventory = self.session.query(Inventory).filter(
                    Inventory.warehouse_id == order.warehouse_id,
                    Inventory.product_id == detail.product_id,
                    Inventory.is_active == True
                ).first()
                
                if not inventory:
                    raise ValueError(f"产品 {detail.product_name} 在仓库中没有库存记录")
                
                outbound_quantity = detail.outbound_quantity
                
                # 检查可用库存是否充足
                if inventory.available_quantity < outbound_quantity:
                    raise ValueError(
                        f"产品 {detail.product_name} 可用库存不足: "
                        f"需要 {outbound_quantity} {detail.unit}, "
                        f"可用 {inventory.available_quantity} {detail.unit}"
                    )
                
                # 扣减库存
                quantity_before = inventory.current_quantity
                inventory.current_quantity -= outbound_quantity
                inventory.available_quantity -= outbound_quantity
                inventory.updated_by = executed_by_uuid
                inventory.updated_at = func.now()
                
                # 重新计算总成本
                inventory.calculate_total_cost()
                
                # 创建库存流水记录
                transaction = InventoryTransaction(
                    inventory_id=inventory.id,
                    warehouse_id=order.warehouse_id,
                    product_id=detail.product_id,
                    transaction_type='sales_out',
                    quantity_change=-outbound_quantity,
                    quantity_before=quantity_before,
                    quantity_after=inventory.current_quantity,
                    unit_id=detail.unit_id,
                    unit_price=detail.unit_cost or Decimal('0'),
                    source_document_type='outbound_order',
                    source_document_id=order.id,
                    source_document_number=order.order_number,
                    batch_number=detail.batch_number,
                    from_location=detail.location_code,
                    customer_id=order.customer_id,
                    reason=f"出库单 {order.order_number} 执行出库",
                    created_by=executed_by_uuid,
                    approval_status='approved'
                )
                
                # 计算总金额
                transaction.calculate_total_amount()
                
                self.session.add(transaction)
                transactions.append(transaction)
            
            # 更新出库单状态
            order.status = 'completed'
            order.updated_by = executed_by_uuid
            order.updated_at = func.now()
            
            self.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([order])
            
            current_app.logger.info(f"出库单 {order.order_number} 执行成功，创建了 {len(transactions)} 条库存流水")
            
            return {
                **order.to_dict(),
                'transactions_count': len(transactions)
            }
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"执行出库单失败: {str(e)}")
            raise ValueError(f"执行出库单失败: {str(e)}")

    def cancel_outbound_order(self, order_id: str, cancel_data: Dict[str, Any], cancelled_by: str) -> Dict[str, Any]:
        """取消出库单"""
        try:
            order = self.session.query(OutboundOrder).filter(OutboundOrder.id == order_id).first()
            
            if not order:
                raise ValueError(f"出库单不存在: {order_id}")
            
            # 检查状态
            if order.status in ['completed', 'cancelled']:
                raise ValueError("已完成或已取消的出库单不能再次取消")
            
            order.status = 'cancelled'
            order.updated_by = uuid.UUID(cancelled_by)
            order.updated_at = func.now()
            
            # 记录取消原因
            if cancel_data.get('cancel_reason'):
                order.remark = f"{order.remark or ''}\n取消原因: {cancel_data['cancel_reason']}".strip()
            
            self.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([order])
            
            return order.to_dict()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"取消出库单失败: {str(e)}")
            raise ValueError(f"取消出库单失败: {str(e)}")

    def get_outbound_order_details(self, order_id: str) -> List[Dict[str, Any]]:
        """获取出库单明细列表"""
        try:
            details = self.session.query(OutboundOrderDetail).filter(OutboundOrderDetail.outbound_order_id == order_id).all()
            
            return [detail.to_dict() for detail in details]
            
        except Exception as e:
            current_app.logger.error(f"获取出库单明细失败: {str(e)}")
            raise ValueError(f"获取出库单明细失败: {str(e)}")

    def create_outbound_order_detail(self, order_id: str, detail_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """创建出库单明细"""
        try:
            
            # 检查出库单是否存在
            order = self.session.query(OutboundOrder).filter(OutboundOrder.id == order_id).first()
            if not order:
                raise ValueError(f"出库单不存在: {order_id}")
            
            # 检查状态是否允许添加明细
            if order.status not in ['draft', 'confirmed']:
                raise ValueError("只有草稿和已确认状态的出库单可以添加明细")
            
            created_by_uuid = uuid.UUID(created_by)
            
            # 处理单位字段：优先使用unit_id，如果没有则使用unit
            unit_id = None
            if detail_data.get('unit_id'):
                unit_id = uuid.UUID(detail_data['unit_id'])
            elif detail_data.get('unit'):
                unit_id = uuid.UUID(detail_data['unit'])
            
            if not unit_id:
                raise ValueError("单位字段不能为空")
            
            detail = OutboundOrderDetail(
                outbound_order_id=uuid.UUID(order_id),
                outbound_quantity=Decimal(str(detail_data.get('outbound_quantity', 0))),
                unit_id=unit_id,
                created_by=created_by_uuid
            )
            
            # 设置其他明细字段
            if detail_data.get('product_id'):
                detail.product_id = uuid.UUID(detail_data['product_id'])
            detail.product_name = detail_data.get('product_name', '')
            detail.product_code = detail_data.get('product_code', '')
            detail.product_spec = detail_data.get('product_spec', '')   
            detail.batch_number = detail_data.get('batch_number', '')
            detail.location_code = detail_data.get('location_code', '')
            
            if detail_data.get('outbound_kg_quantity'):
                detail.outbound_kg_quantity = Decimal(str(detail_data['outbound_kg_quantity']))
            if detail_data.get('outbound_m_quantity'):
                detail.outbound_m_quantity = Decimal(str(detail_data['outbound_m_quantity']))
            if detail_data.get('outbound_roll_quantity'):
                detail.outbound_roll_quantity = Decimal(str(detail_data['outbound_roll_quantity']))
            if detail_data.get('box_quantity'):
                detail.box_quantity = Decimal(str(detail_data['box_quantity']))
            if detail_data.get('unit_cost'):
                detail.unit_cost = Decimal(str(detail_data['unit_cost']))
            
            self.session.add(detail)
            self.commit()
            self.session.refresh(detail)
            
            return detail.to_dict()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"创建出库单明细失败: {str(e)}")
            raise ValueError(f"创建出库单明细失败: {str(e)}")

    def update_outbound_order_detail(self, order_id: str, detail_id: str, detail_data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """更新出库单明细"""
        try:
            
            detail = self.session.query(OutboundOrderDetail).filter(
                OutboundOrderDetail.id == detail_id,
                OutboundOrderDetail.outbound_order_id == order_id
            ).first()
            
            if not detail:
                raise ValueError(f"出库单明细不存在: {detail_id}")
            
            # 检查出库单状态是否允许更新明细
            order = self.session.query(OutboundOrder).filter(OutboundOrder.id == order_id).first()
            if order and order.status not in ['draft', 'confirmed']:
                raise ValueError("只有草稿和已确认状态的出库单可以更新明细")
            
            updated_by_uuid = uuid.UUID(updated_by)
            
            # 更新明细字段
            for key, value in detail_data.items():
                if hasattr(detail, key) and key not in ['id', 'outbound_order_id', 'created_by', 'created_at']:
                    if key in ['outbound_quantity', 'outbound_kg_quantity', 'outbound_m_quantity', 
                              'outbound_roll_quantity', 'box_quantity', 'unit_cost'] and value is not None:
                        setattr(detail, key, Decimal(str(value)))
                    elif key == 'product_id' and value:
                        setattr(detail, key, uuid.UUID(value))
                    elif key == 'unit' and value:
                        # 处理单位字段：将unit值转换为unit_id
                        setattr(detail, 'unit_id', uuid.UUID(value))
                    else:
                        setattr(detail, key, value)
            
            detail.updated_by = updated_by_uuid
            detail.updated_at = func.now()
            
            self.commit()
            
            return detail.to_dict()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"更新出库单明细失败: {str(e)}")
            raise ValueError(f"更新出库单明细失败: {str(e)}")

    def delete_outbound_order_detail(self, order_id: str, detail_id: str) -> bool:
        """删除出库单明细"""
        try:
            
            detail = self.session.query(OutboundOrderDetail).filter(
                OutboundOrderDetail.id == detail_id,
                OutboundOrderDetail.outbound_order_id == order_id
            ).first()
            
            if not detail:
                raise ValueError(f"出库单明细不存在: {detail_id}")
            
            # 检查出库单状态是否允许删除明细
            order = self.session.query(OutboundOrder).filter(OutboundOrder.id == order_id).first()
            if order and order.status not in ['draft', 'confirmed']:
                raise ValueError("只有草稿和已确认状态的出库单可以删除明细")
            
            self.session.delete(detail)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"删除出库单明细失败: {str(e)}")
            raise ValueError(f"删除出库单明细失败: {str(e)}")


def get_product_outbound_service(tenant_id: str = None, schema_name: str = None) -> ProductOutboundService:
    """获取产品出库服务实例"""
    return ProductOutboundService(tenant_id=tenant_id, schema_name=schema_name) 