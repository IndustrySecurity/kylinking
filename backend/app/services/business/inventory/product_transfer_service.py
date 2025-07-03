# -*- coding: utf-8 -*-
# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
成品调拨服务
"""
from flask import current_app, g
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import joinedload
from datetime import datetime
import uuid

from app.services.base_service import TenantAwareService
from app.models.business.inventory import (
    ProductTransferOrder, 
    ProductTransferOrderDetail,
    Inventory,
    InventoryTransaction
)
from app.models.basic_data import Product, Warehouse, Employee, Department


class ProductTransferService(TenantAwareService):
    """成品调拨服务类"""
    
    def create_transfer_order(self, data, created_by):
        """创建成品调拨单"""
        try:
            # 验证必填字段
            required_fields = ['from_warehouse_id', 'to_warehouse_id', 'transfer_type']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {'success': False, 'message': f'缺少必填字段: {field}'}
            
            # 验证调出和调入仓库不能相同
            if data['from_warehouse_id'] == data['to_warehouse_id']:
                return {'success': False, 'message': '调出仓库和调入仓库不能相同'}
            
            # 查询仓库信息
            from_warehouse = self.session.query(Warehouse).filter_by(
                id=data['from_warehouse_id']
            ).first()
            to_warehouse = self.session.query(Warehouse).filter_by(
                id=data['to_warehouse_id']
            ).first()
            
            if not from_warehouse:
                return {'success': False, 'message': '调出仓库不存在'}
            if not to_warehouse:
                return {'success': False, 'message': '调入仓库不存在'}
            
            # 验证仓库类型是否支持成品
            if from_warehouse.warehouse_type not in ['finished_goods', 'mixed']:
                return {'success': False, 'message': '调出仓库不支持成品存储'}
            if to_warehouse.warehouse_type not in ['finished_goods', 'mixed']:
                return {'success': False, 'message': '调入仓库不支持成品存储'}
            
            # 准备调拨单数据
            transfer_data = {
                'from_warehouse_id': data['from_warehouse_id'],
                'to_warehouse_id': data['to_warehouse_id'],
                'transfer_type': data['transfer_type'],
                'transfer_date': datetime.fromisoformat(data['transfer_date'].replace('Z', '+00:00')) if data.get('transfer_date') else datetime.now(),
                'from_warehouse_name': from_warehouse.warehouse_name,
                'from_warehouse_code': from_warehouse.warehouse_code,
                'to_warehouse_name': to_warehouse.warehouse_name,
                'to_warehouse_code': to_warehouse.warehouse_code,
                'transfer_person_id': data.get('transfer_person_id'),
                'department_id': data.get('department_id'),
                'transporter': data.get('transporter'),
                'transport_method': data.get('transport_method'),
                'expected_arrival_date': datetime.fromisoformat(data['expected_arrival_date'].replace('Z', '+00:00')) if data.get('expected_arrival_date') else None,
                'notes': data.get('notes', '')
            }
            
            # 使用继承的create_with_tenant方法
            transfer_order = self.create_with_tenant(ProductTransferOrder, **transfer_data)
            self.session.flush()  # 获取ID
            
            current_app.logger.info(f"成品调拨单创建成功: {transfer_order.transfer_number}")
            
            self.commit()
            
            return {
                'success': True,
                'message': '成品调拨单创建成功',
                'data': transfer_order.to_dict()
            }
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"创建成品调拨单失败: {str(e)}")
            return {'success': False, 'message': f'创建失败: {str(e)}'}
    
    def add_transfer_detail(self, transfer_order_id, product_data, created_by):
        """添加调拨明细"""
        try:
            # 验证调拨单存在
            transfer_order = self.session.query(ProductTransferOrder).filter_by(
                id=transfer_order_id
            ).first()
            
            if not transfer_order:
                return {'success': False, 'message': '调拨单不存在'}
            
            if transfer_order.status != 'draft':
                return {'success': False, 'message': '只能在草稿状态下添加明细'}
            
            # 验证必填字段
            required_fields = ['product_id', 'transfer_quantity']
            for field in required_fields:
                if field not in product_data or not product_data[field]:
                    return {'success': False, 'message': f'缺少必填字段: {field}'}
            
            # 查询产品信息
            product = self.session.query(Product).filter_by(
                id=product_data['product_id']
            ).first()
            
            if not product:
                return {'success': False, 'message': '产品不存在'}
            
            # 查询调出仓库的库存
            inventory = self.session.query(Inventory).filter_by(
                warehouse_id=transfer_order.from_warehouse_id,
                product_id=product_data['product_id']
            ).first()
            
            available_quantity = inventory.available_quantity if inventory else 0
            
            # 验证库存是否充足
            if float(product_data['transfer_quantity']) > available_quantity:
                return {'success': False, 'message': f'库存不足，可用数量: {available_quantity}'}
            
            # 准备调拨明细数据
            detail_data = {
                'transfer_order_id': transfer_order_id,
                'product_id': product_data['product_id'],
                'product_name': product.product_name,
                'product_code': product.product_code,
                'product_spec': getattr(product, 'specification', ''),
                'unit': product.base_unit,
                'transfer_quantity': product_data['transfer_quantity'],
                'from_inventory_id': inventory.id if inventory else None,
                'current_stock': inventory.current_quantity if inventory else 0,
                'available_quantity': available_quantity,
                'unit_cost': inventory.unit_cost if inventory else None,
                'batch_number': product_data.get('batch_number'),
                'from_location_code': inventory.location_code if inventory else None,
                'to_location_code': product_data.get('to_location_code'),
                'customer_id': getattr(product, 'customer_id', None),
                'customer_name': getattr(product.customer, 'customer_name', '') if hasattr(product, 'customer') and product.customer else '',
                'bag_type_id': getattr(product, 'bag_type_id', None),
                'bag_type_name': getattr(product.bag_type, 'bag_type_name', '') if hasattr(product, 'bag_type') and product.bag_type else '',
                'notes': product_data.get('notes', '')
            }
            
            # 使用继承的create_with_tenant方法
            detail = self.create_with_tenant(ProductTransferOrderDetail, **detail_data)
            
            # 计算金额
            detail.calculate_total_amount()
            
            # 更新调拨单统计信息
            transfer_order.calculate_totals()
            
            self.commit()
            
            return {
                'success': True,
                'message': '调拨明细添加成功',
                'data': detail.to_dict()
            }
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"添加调拨明细失败: {str(e)}")
            return {'success': False, 'message': f'添加失败: {str(e)}'}
    
    def confirm_transfer_order(self, transfer_order_id, confirmed_by):
        """确认调拨单"""
        try:
            transfer_order = self.session.query(ProductTransferOrder).filter_by(
                id=transfer_order_id
            ).first()
            
            if not transfer_order:
                return {'success': False, 'message': '调拨单不存在'}
            
            if transfer_order.status != 'draft':
                return {'success': False, 'message': '只能确认草稿状态的调拨单'}
            
            if not transfer_order.details:
                return {'success': False, 'message': '调拨单没有明细，无法确认'}
            
            # 再次验证所有明细的库存
            for detail in transfer_order.details:
                inventory = self.session.query(Inventory).filter_by(
                    id=detail.from_inventory_id
                ).first()
                
                if not inventory or inventory.available_quantity < detail.transfer_quantity:
                    return {'success': False, 'message': f'产品 {detail.product_name} 库存不足'}
            
            # 更新状态
            transfer_order.status = 'confirmed'
            transfer_order.confirmed_by = confirmed_by
            transfer_order.confirmed_at = datetime.now()
            
            self.commit()
            
            return {
                'success': True,
                'message': '调拨单确认成功',
                'data': transfer_order.to_dict()
            }
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"确认调拨单失败: {str(e)}")
            return {'success': False, 'message': f'确认失败: {str(e)}'}
    
    def execute_transfer_order(self, transfer_order_id, executed_by):
        """执行调拨单"""
        try:
            transfer_order = self.session.query(ProductTransferOrder).filter_by(
                id=transfer_order_id
            ).first()
            
            if not transfer_order:
                return {'success': False, 'message': '调拨单不存在'}
            
            if transfer_order.status != 'confirmed':
                return {'success': False, 'message': '只能执行已确认的调拨单'}
            
            # 执行库存调拨
            for detail in transfer_order.details:
                # 从调出仓库减库存
                from_inventory = self.session.query(Inventory).filter_by(
                    warehouse_id=transfer_order.from_warehouse_id,
                    product_id=detail.product_id
                ).first()
                
                if from_inventory:
                    from_inventory.current_quantity -= detail.transfer_quantity
                    from_inventory.available_quantity -= detail.transfer_quantity
                    from_inventory.updated_by = executed_by
                    
                    # 创建调出流水
                    out_transaction = InventoryTransaction(
                        inventory_id=from_inventory.id,
                        warehouse_id=transfer_order.from_warehouse_id,
                        product_id=detail.product_id,
                        transaction_type='transfer_out',
                        quantity_change=-detail.transfer_quantity,
                        quantity_before=from_inventory.current_quantity + detail.transfer_quantity,
                        quantity_after=from_inventory.current_quantity,
                        unit=detail.unit,
                        source_document_type='transfer_order',
                        source_document_id=transfer_order_id,
                        source_document_number=transfer_order.transfer_number,
                        batch_number=detail.batch_number,
                        from_location=detail.from_location_code,
                        reason=f'成品调拨出库: {transfer_order.transfer_number}',
                        created_by=executed_by
                    )
                    self.session.add(out_transaction)
                
                # 向调入仓库加库存
                to_inventory = self.session.query(Inventory).filter_by(
                    warehouse_id=transfer_order.to_warehouse_id,
                    product_id=detail.product_id
                ).first()
                
                if to_inventory:
                    to_inventory.current_quantity += detail.transfer_quantity
                    to_inventory.available_quantity += detail.transfer_quantity
                    to_inventory.updated_by = executed_by
                else:
                    # 创建新库存记录
                    to_inventory = Inventory(
                        warehouse_id=transfer_order.to_warehouse_id,
                        product_id=detail.product_id,
                        current_quantity=detail.transfer_quantity,
                        available_quantity=detail.transfer_quantity,
                        unit=detail.unit,
                        unit_cost=detail.unit_cost,
                        batch_number=detail.batch_number,
                        location_code=detail.to_location_code,
                        created_by=executed_by
                    )
                    self.session.add(to_inventory)
                    self.session.flush()
                
                # 创建调入流水
                in_transaction = InventoryTransaction(
                    inventory_id=to_inventory.id,
                    warehouse_id=transfer_order.to_warehouse_id,
                    product_id=detail.product_id,
                    transaction_type='transfer_in',
                    quantity_change=detail.transfer_quantity,
                    quantity_before=to_inventory.current_quantity - detail.transfer_quantity,
                    quantity_after=to_inventory.current_quantity,
                    unit=detail.unit,
                    source_document_type='transfer_order',
                    source_document_id=transfer_order_id,
                    source_document_number=transfer_order.transfer_number,
                    batch_number=detail.batch_number,
                    to_location=detail.to_location_code,
                    reason=f'成品调拨入库: {transfer_order.transfer_number}',
                    created_by=executed_by
                )
                self.session.add(in_transaction)
                
                # 更新明细状态
                detail.actual_transfer_quantity = detail.transfer_quantity
                detail.detail_status = 'in_transit'
                detail.updated_by = executed_by
            
            # 更新调拨单状态
            transfer_order.status = 'in_transit'
            transfer_order.executed_by = executed_by
            transfer_order.executed_at = datetime.now()
            transfer_order.updated_by = executed_by
            
            self.commit()
            
            return {
                'success': True,
                'message': '调拨单执行成功',
                'data': transfer_order.to_dict()
            }
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"执行调拨单失败: {str(e)}")
            return {'success': False, 'message': f'执行失败: {str(e)}'}
    
    def receive_transfer_order(self, transfer_order_id, received_by):
        """收货确认"""
        try:
            transfer_order = self.session.query(ProductTransferOrder).filter_by(
                id=transfer_order_id
            ).first()
            
            if not transfer_order:
                return {'success': False, 'message': '调拨单不存在'}
            
            if transfer_order.status != 'in_transit':
                return {'success': False, 'message': '只能收货运输中的调拨单'}
            
            # 更新明细状态
            for detail in transfer_order.details:
                detail.received_quantity = detail.actual_transfer_quantity
                detail.detail_status = 'received'
                detail.updated_by = received_by
            
            # 更新调拨单状态
            transfer_order.status = 'completed'
            transfer_order.actual_arrival_date = datetime.now()
            transfer_order.updated_by = received_by
            
            self.commit()
            
            return {
                'success': True,
                'message': '收货确认成功',
                'data': transfer_order.to_dict()
            }
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"收货确认失败: {str(e)}")
            return {'success': False, 'message': f'收货确认失败: {str(e)}'}
    
    def cancel_transfer_order(self, transfer_order_id, cancelled_by, reason=None):
        """取消调拨单"""
        try:
            transfer_order = self.session.query(ProductTransferOrder).filter_by(
                id=transfer_order_id
            ).first()
            
            if not transfer_order:
                return {'success': False, 'message': '调拨单不存在'}
            
            if transfer_order.status in ['completed', 'cancelled']:
                return {'success': False, 'message': '该状态下不能取消调拨单'}
            
            # 如果已执行，需要回滚库存
            if transfer_order.status == 'in_transit':
                for detail in transfer_order.details:
                    # 回滚调出仓库库存
                    from_inventory = self.session.query(Inventory).filter_by(
                        warehouse_id=transfer_order.from_warehouse_id,
                        product_id=detail.product_id
                    ).first()
                    
                    if from_inventory:
                        from_inventory.current_quantity += detail.actual_transfer_quantity or detail.transfer_quantity
                        from_inventory.available_quantity += detail.actual_transfer_quantity or detail.transfer_quantity
                        from_inventory.updated_by = cancelled_by
                    
                    # 回滚调入仓库库存
                    to_inventory = self.session.query(Inventory).filter_by(
                        warehouse_id=transfer_order.to_warehouse_id,
                        product_id=detail.product_id
                    ).first()
                    
                    if to_inventory:
                        to_inventory.current_quantity -= detail.actual_transfer_quantity or detail.transfer_quantity
                        to_inventory.available_quantity -= detail.actual_transfer_quantity or detail.transfer_quantity
                        to_inventory.updated_by = cancelled_by
                        
                        # 如果库存为0，删除记录
                        if to_inventory.current_quantity <= 0:
                            self.session.delete(to_inventory)
                    
                    # 更新明细状态
                    detail.detail_status = 'cancelled'
                    detail.updated_by = cancelled_by
            
            # 更新调拨单状态
            transfer_order.status = 'cancelled'
            transfer_order.notes = f"{transfer_order.notes or ''}\n取消原因: {reason or '用户取消'}"
            transfer_order.updated_by = cancelled_by
            
            self.commit()
            
            return {
                'success': True,
                'message': '调拨单取消成功',
                'data': transfer_order.to_dict()
            }
            
        except Exception as e:
            self.rollback()
            current_app.logger.error(f"取消调拨单失败: {str(e)}")
            return {'success': False, 'message': f'取消失败: {str(e)}'}
    
    def get_warehouse_product_inventory(self, warehouse_id):
        """获取仓库成品库存"""
        try:
            # 直接联合查询Inventory和Product表，避免使用inventory.product属性
            from app.models.basic_data import Product
            
            results = self.session.query(
                Inventory.id.label('inventory_id'),
                Inventory.product_id,
                Inventory.current_quantity,
                Inventory.available_quantity,
                Inventory.unit_cost,
                Product.product_code,
                Product.product_name,
                Product.specification,
                Product.base_unit
            ).join(
                Product, Inventory.product_id == Product.id
            ).filter(
                Inventory.warehouse_id == warehouse_id,
                Inventory.product_id.isnot(None),
                Inventory.current_quantity > 0
            ).all()
            
            result = []
            for item in results:
                result.append({
                    'inventory_id': str(item.inventory_id),
                    'product_id': str(item.product_id),
                    'product_code': item.product_code,
                    'product_name': item.product_name,
                    'product_spec': item.specification,
                    'current_quantity': float(item.current_quantity or 0),
                    'available_quantity': float(item.available_quantity or 0),
                    'unit': item.base_unit,
                    'unit_cost': float(item.unit_cost or 0)
                })
            
            return {
                'success': True,
                'data': result
            }
            
        except Exception as e:
            current_app.logger.error(f"获取仓库成品库存失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取仓库成品库存失败: {str(e)}'
            }


def get_product_transfer_service(tenant_id: str = None, schema_name: str = None) -> ProductTransferService:
    """获取成品调拨服务实例"""
    return ProductTransferService(tenant_id=tenant_id, schema_name=schema_name)