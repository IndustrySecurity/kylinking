# -*- coding: utf-8 -*-
# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
材料调拨服务
"""

import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_, func
from flask import current_app

from app.services.base_service import TenantAwareService
from app.models.business.inventory import (
    MaterialTransferOrder, MaterialTransferOrderDetail, 
    Inventory, InventoryTransaction
)
from app.models.basic_data import Material, Warehouse, Employee, Department


class MaterialTransferService(TenantAwareService):
    """材料调拨服务"""
    
    def create_transfer_order(self, data, created_by):
        """
        创建材料调拨单
        
        Args:
            data: 调拨单数据
            created_by: 创建人ID
            
        Returns:
            MaterialTransferOrder: 创建的调拨单
        """
        try:
            # 转换UUID字段
            from_warehouse_id = uuid.UUID(data['from_warehouse_id'])
            to_warehouse_id = uuid.UUID(data['to_warehouse_id'])
            created_by_uuid = uuid.UUID(created_by)
            
            # 获取仓库信息
            from_warehouse = self.session.query(Warehouse).filter(Warehouse.id == from_warehouse_id).first()
            to_warehouse = self.session.query(Warehouse).filter(Warehouse.id == to_warehouse_id).first()
            
            if not from_warehouse or not to_warehouse:
                raise ValueError("仓库不存在")
            
            # 验证不能是同一个仓库
            if from_warehouse_id == to_warehouse_id:
                raise ValueError("调出仓库和调入仓库不能相同")
            
            # 转换日期字段
            if 'transfer_date' in data and isinstance(data['transfer_date'], str):
                data['transfer_date'] = datetime.fromisoformat(data['transfer_date'].replace('Z', '+00:00'))
            
            # 处理UUID字段
            if 'transfer_person_id' in data and data['transfer_person_id']:
                data['transfer_person_id'] = uuid.UUID(data['transfer_person_id'])
            if 'department_id' in data and data['department_id']:
                data['department_id'] = uuid.UUID(data['department_id'])
            
            # 准备调拨单数据
            transfer_data = {
                'from_warehouse_id': from_warehouse_id,
                'to_warehouse_id': to_warehouse_id,
                'transfer_type': data.get('transfer_type', 'warehouse'),
                'from_warehouse_name': from_warehouse.warehouse_name,
                'from_warehouse_code': from_warehouse.warehouse_code,
                'to_warehouse_name': to_warehouse.warehouse_name,
                'to_warehouse_code': to_warehouse.warehouse_code,
            }
            
            # 添加其他可选字段，避免重复
            for key, value in data.items():
                if key not in transfer_data and key not in ['from_warehouse_id', 'to_warehouse_id']:
                    transfer_data[key] = value
            
            # 使用继承的create_with_tenant方法
            transfer_order = self.create_with_tenant(MaterialTransferOrder, **transfer_data)
            self.session.flush()  # 获取ID
            
            self.commit()
            return transfer_order
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"创建材料调拨单失败: {str(e)}")
            raise
    
    def add_transfer_detail(self, transfer_order_id, material_data, created_by):
        """
        添加调拨明细
        
        Args:
            transfer_order_id: 调拨单ID
            material_data: 材料数据
            created_by: 创建人ID
            
        Returns:
            MaterialTransferOrderDetail: 创建的明细
        """
        try:
            # 获取调拨单
            transfer_order = self.session.query(MaterialTransferOrder).get(transfer_order_id)
            if not transfer_order:
                raise ValueError("调拨单不存在")
            
            if transfer_order.status not in ['draft', 'confirmed']:
                raise ValueError("只能修改草稿或已确认状态的调拨单")
            
            # 获取材料信息
            material_id = uuid.UUID(material_data['material_id'])
            material = self.session.query(Material).filter(Material.id == material_id).first()
            if not material:
                raise ValueError("材料不存在")
            
            # 检查调出仓库库存
            inventory = self.session.query(Inventory).filter(
                and_(
                    Inventory.warehouse_id == transfer_order.from_warehouse_id,
                    Inventory.material_id == material_id
                )
            ).first()
            
            if not inventory:
                raise ValueError(f"调出仓库中没有材料 {material.material_name} 的库存")
            
            transfer_quantity = Decimal(str(material_data['transfer_quantity']))
            if transfer_quantity <= 0:
                raise ValueError("调拨数量必须大于0")
            
            if inventory.available_quantity < transfer_quantity:
                raise ValueError(f"调出仓库可用库存不足，当前可用: {inventory.available_quantity}")
            
            # 准备调拨明细数据，避免参数重复
            detail_data = {
                'transfer_order_id': transfer_order_id,
                'material_id': material_id,
                'material_name': material.material_name,
                'unit': inventory.unit or '件',  # 使用库存记录中的单位
                'transfer_quantity': transfer_quantity,
                'material_code': material.material_code,
                'material_spec': material.specification_model,
                'from_inventory_id': inventory.id,
                'current_stock': inventory.current_quantity,
                'available_quantity': inventory.available_quantity,
                'unit_price': inventory.unit_cost,
            }
            
            # 添加额外的材料数据，但避免覆盖已设置的关键字段
            for key, value in material_data.items():
                if key not in detail_data:
                    detail_data[key] = value
            
            # 使用继承的create_with_tenant方法
            detail = self.create_with_tenant(MaterialTransferOrderDetail, **detail_data)
            
            # 计算总金额
            detail.calculate_total_amount()
            
            # 更新调拨单统计信息
            transfer_order.calculate_totals()
            
            self.commit()
            return detail
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"添加调拨明细失败: {str(e)}")
            raise
    
    def confirm_transfer_order(self, transfer_order_id, confirmed_by):
        """
        确认调拨单
        
        Args:
            transfer_order_id: 调拨单ID
            confirmed_by: 确认人ID
        """
        try:
            transfer_order = self.session.query(MaterialTransferOrder).get(transfer_order_id)
            if not transfer_order:
                raise ValueError("调拨单不存在")
            
            if transfer_order.status != 'draft':
                raise ValueError("只能确认草稿状态的调拨单")
            
            if not transfer_order.details:
                raise ValueError("调拨单没有明细，无法确认")
            
            # 再次检查所有明细的库存
            for detail in transfer_order.details:
                inventory = self.session.query(Inventory).get(detail.from_inventory_id)
                if not inventory or inventory.available_quantity < detail.transfer_quantity:
                    raise ValueError(f"材料 {detail.material_name} 可用库存不足")
            
            # 更新状态
            transfer_order.status = 'confirmed'
            transfer_order.confirmed_by = uuid.UUID(confirmed_by)
            transfer_order.confirmed_at = datetime.now()
            
            self.commit()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"确认调拨单失败: {str(e)}")
            raise
    
    def execute_transfer_order(self, transfer_order_id, executed_by):
        """
        执行调拨单（出库）
        
        Args:
            transfer_order_id: 调拨单ID
            executed_by: 执行人ID
        """
        try:
            transfer_order = self.session.query(MaterialTransferOrder).get(transfer_order_id)
            if not transfer_order:
                raise ValueError("调拨单不存在")
            
            if transfer_order.status != 'confirmed':
                raise ValueError("只能执行已确认的调拨单")
            
            executed_by_uuid = uuid.UUID(executed_by)
            
            for detail in transfer_order.details:
                # 出库操作
                inventory = self.session.query(Inventory).get(detail.from_inventory_id)
                if inventory:
                    # 取消预留并出库
                    inventory.unreserve_quantity(detail.transfer_quantity, executed_by)
                    inventory.update_quantity(-detail.transfer_quantity, 'transfer_out', executed_by)
                    
                    # 创建出库交易记录
                    out_transaction = InventoryTransaction(
                        inventory_id=inventory.id,
                        warehouse_id=inventory.warehouse_id,
                        material_id=inventory.material_id,
                        transaction_type='transfer_out',
                        quantity_change=-detail.transfer_quantity,
                        quantity_before=inventory.current_quantity + detail.transfer_quantity,
                        quantity_after=inventory.current_quantity,
                        unit=inventory.unit,
                        source_document_type='transfer_order',
                        source_document_number=transfer_order.transfer_number,
                        reason=f'调拨出库到 {transfer_order.to_warehouse_name}',
                        created_by=executed_by_uuid
                    )
                    self.session.add(out_transaction)
                
                detail.detail_status = 'in_transit'
                detail.actual_transfer_quantity = detail.transfer_quantity
            
            transfer_order.status = 'in_transit'
            transfer_order.executed_by = executed_by_uuid
            transfer_order.executed_at = datetime.now()
            transfer_order.updated_by = executed_by_uuid
            
            self.commit()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"执行调拨单失败: {str(e)}")
            raise
    
    def receive_transfer_order(self, transfer_order_id, received_by):
        """
        接收调拨单（入库）
        
        Args:
            transfer_order_id: 调拨单ID
            received_by: 接收人ID
        """
        try:
            transfer_order = self.session.query(MaterialTransferOrder).get(transfer_order_id)
            if not transfer_order:
                raise ValueError("调拨单不存在")
            
            if transfer_order.status != 'in_transit':
                raise ValueError("只能接收运输中的调拨单")
            
            received_by_uuid = uuid.UUID(received_by)
            
            for detail in transfer_order.details:
                # 检查调入仓库是否已有该材料库存
                to_inventory = self.session.query(Inventory).filter(
                    and_(
                        Inventory.warehouse_id == transfer_order.to_warehouse_id,
                        Inventory.material_id == detail.material_id
                    )
                ).first()
                
                if not to_inventory:
                    # 创建新库存记录
                    to_inventory = Inventory(
                        warehouse_id=transfer_order.to_warehouse_id,
                        material_id=detail.material_id,
                        unit=detail.unit,
                        created_by=received_by_uuid,
                        current_quantity=0,
                        available_quantity=0
                    )
                    self.session.add(to_inventory)
                    self.session.flush()
                
                # 入库操作
                old_quantity = to_inventory.current_quantity
                to_inventory.update_quantity(detail.transfer_quantity, 'transfer_in', received_by)
                
                # 创建入库交易记录
                in_transaction = InventoryTransaction(
                    inventory_id=to_inventory.id,
                    warehouse_id=to_inventory.warehouse_id,
                    material_id=to_inventory.material_id,
                    transaction_type='transfer_in',
                    quantity_change=detail.transfer_quantity,
                    quantity_before=old_quantity,
                    quantity_after=to_inventory.current_quantity,
                    unit=to_inventory.unit,
                    source_document_type='transfer_order',
                    source_document_number=transfer_order.transfer_number,
                    reason=f'调拨入库来自 {transfer_order.from_warehouse_name}',
                    created_by=received_by_uuid
                )
                self.session.add(in_transaction)
                
                detail.detail_status = 'received'
                detail.received_quantity = detail.transfer_quantity
            
            transfer_order.status = 'completed'
            transfer_order.actual_arrival_date = datetime.now()
            transfer_order.updated_by = received_by_uuid
            
            self.commit()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"接收调拨单失败: {str(e)}")
            raise
    
    def cancel_transfer_order(self, transfer_order_id, cancelled_by, reason=None):
        """
        取消调拨单
        
        Args:
            transfer_order_id: 调拨单ID
            cancelled_by: 取消人ID
            reason: 取消原因
        """
        try:
            transfer_order = self.session.query(MaterialTransferOrder).get(transfer_order_id)
            if not transfer_order:
                raise ValueError("调拨单不存在")
            
            if transfer_order.status not in ['draft', 'confirmed']:
                raise ValueError("只能取消草稿或已确认状态的调拨单")
            
            cancelled_by_uuid = uuid.UUID(cancelled_by)
            
            # 如果是已确认状态，需要释放预留库存
            if transfer_order.status == 'confirmed':
                for detail in transfer_order.details:
                    inventory = self.session.query(Inventory).get(detail.from_inventory_id)
                    if inventory:
                        inventory.unreserve_quantity(detail.transfer_quantity, cancelled_by)
                    detail.detail_status = 'cancelled'
            
            transfer_order.status = 'cancelled'
            transfer_order.updated_by = cancelled_by_uuid
            if reason:
                transfer_order.notes = f"{transfer_order.notes or ''}\n取消原因: {reason}".strip()
            
            self.commit()
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"取消调拨单失败: {str(e)}")
            raise
    
    def get_warehouse_material_inventory(self, warehouse_id):
        """
        获取仓库材料库存信息
        
        Args:
            warehouse_id: 仓库ID
            
        Returns:
            list: 库存信息列表
        """
        try:
            # 查询该仓库的所有材料库存
            inventories = self.session.query(Inventory).filter(
                and_(
                    Inventory.warehouse_id == warehouse_id,
                    Inventory.material_id.isnot(None),
                    Inventory.current_quantity > 0
                )
            ).all()
            
            inventory_data = []
            for inventory in inventories:
                # 获取材料信息
                material = self.session.query(Material).filter(Material.id == inventory.material_id).first()
                
                inventory_dict = inventory.to_dict()
                if material:
                    # 获取单位信息
                    unit_name = inventory.unit if inventory.unit else '个'  # 使用库存记录中的单位
                    
                    inventory_dict.update({
                        'material_code': material.material_code,
                        'material_name': material.material_name,
                        'material_spec': material.specification_model or '',
                        'unit': unit_name
                    })
                
                inventory_data.append(inventory_dict)
            
            return inventory_data
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"获取仓库材料库存失败: {str(e)}")
            raise 