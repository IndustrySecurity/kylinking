from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

from app.models.business.inventory import (
    Inventory, 
    InventoryTransaction, 
    InventoryCountPlan, 
    InventoryCountRecord,
    InboundOrder,
    InboundOrderDetail
)
from flask import g, current_app


class InventoryService:
    """
    库存管理服务类
    提供库存相关的业务逻辑操作
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        schema_name = getattr(g, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in InventoryService")
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
    
    # ================ 库存查询方法 ================
    
    def get_inventory_by_id(self, inventory_id: str) -> Optional[Inventory]:
        """根据ID获取库存记录"""
        self._set_schema()
        return self.db.query(Inventory).filter(Inventory.id == inventory_id).first()
    
    def get_inventory_by_warehouse_and_item(
        self, 
        warehouse_id: str, 
        product_id: str = None, 
        material_id: str = None,
        batch_number: str = None,
        location_code: str = None
    ) -> Optional[Inventory]:
        """根据仓库和物品获取库存记录"""
        self._set_schema()
        query = self.db.query(Inventory).filter(Inventory.warehouse_id == warehouse_id)
        
        if product_id:
            query = query.filter(Inventory.product_id == product_id)
        elif material_id:
            query = query.filter(Inventory.material_id == material_id)
        
        if batch_number:
            query = query.filter(Inventory.batch_number == batch_number)
        
        if location_code:
            query = query.filter(Inventory.location_code == location_code)
        
        return query.filter(Inventory.is_active == True).first()
    
    def get_inventory_list(
        self,
        warehouse_id: str = None,
        inventory_status: str = None,
        quality_status: str = None,
        below_safety_stock: bool = False,
        expired_only: bool = False,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取库存列表"""
        self._set_schema()
        query = self.db.query(Inventory).filter(Inventory.is_active == True)
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        if inventory_status:
            query = query.filter(Inventory.inventory_status == inventory_status)
        
        if quality_status:
            query = query.filter(Inventory.quality_status == quality_status)
        
        if below_safety_stock:
            query = query.filter(Inventory.current_quantity <= Inventory.safety_stock)
        
        if expired_only:
            query = query.filter(
                and_(
                    Inventory.expiry_date.isnot(None),
                    Inventory.expiry_date <= datetime.now()
                )
            )
        
        total = query.count()
        
        inventories = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            'items': [inventory.to_dict() for inventory in inventories],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }
    
    def get_inventory_summary_by_warehouse(self, warehouse_id: str) -> Dict[str, Any]:
        """获取仓库库存汇总"""
        self._set_schema()
        result = self.db.query(
            func.count(Inventory.id).label('total_items'),
            func.sum(Inventory.current_quantity).label('total_quantity'),
            func.sum(Inventory.total_cost).label('total_value'),
            func.count().filter(Inventory.current_quantity <= Inventory.safety_stock).label('below_safety_stock_items')
        ).filter(
            and_(
                Inventory.warehouse_id == warehouse_id,
                Inventory.is_active == True
            )
        ).first()
        
        return {
            'total_items': result.total_items or 0,
            'total_quantity': float(result.total_quantity or 0),
            'total_value': float(result.total_value or 0),
            'below_safety_stock_items': result.below_safety_stock_items or 0
        }
    
    # ================ 库存操作方法 ================
    
    def create_inventory(
        self,
        warehouse_id: str,
        unit: str,
        created_by: str,
        product_id: str = None,
        material_id: str = None,
        **kwargs
    ) -> Inventory:
        """创建库存记录"""
        self._set_schema()
        inventory = Inventory(
            warehouse_id=warehouse_id,
            product_id=product_id,
            material_id=material_id,
            unit=unit,
            created_by=created_by,
            **kwargs
        )
        
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)
        
        return inventory
    
    def update_inventory_quantity(
        self,
        inventory_id: str,
        quantity_change: Decimal,
        transaction_type: str,
        updated_by: str,
        source_document_type: str = None,
        source_document_id: str = None,
        source_document_number: str = None,
        reason: str = None,
        notes: str = None,
        unit_price: Decimal = None,
        **kwargs
    ) -> InventoryTransaction:
        """更新库存数量并创建流水记录"""
        self._set_schema()
        
        inventory = self.get_inventory_by_id(inventory_id)
        if not inventory:
            raise ValueError(f"库存记录不存在: {inventory_id}")
        
        # 检查库存是否足够（出库操作）
        if quantity_change < 0 and inventory.available_quantity < abs(quantity_change):
            raise ValueError("可用库存不足")
        
        # 记录变动前数量
        quantity_before = inventory.current_quantity
        
        # 更新库存数量
        inventory.update_quantity(quantity_change, transaction_type, updated_by)
        
        # 重新计算总成本
        inventory.calculate_total_cost()
        
        # 创建库存流水记录
        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            warehouse_id=inventory.warehouse_id,
            product_id=inventory.product_id,
            material_id=inventory.material_id,
            transaction_type=transaction_type,
            quantity_change=quantity_change,
            quantity_before=quantity_before,
            quantity_after=inventory.current_quantity,
            unit=inventory.unit,
            unit_price=unit_price,
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            source_document_number=source_document_number,
            reason=reason,
            notes=notes,
            created_by=updated_by,
            **kwargs
        )
        
        # 计算总金额
        transaction.calculate_total_amount()
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def reserve_inventory(
        self,
        inventory_id: str,
        quantity: Decimal,
        updated_by: str,
        reason: str = None
    ) -> bool:
        """预留库存"""
        self._set_schema()
        
        inventory = self.get_inventory_by_id(inventory_id)
        if not inventory:
            raise ValueError(f"库存记录不存在: {inventory_id}")
        
        if inventory.reserve_quantity(quantity, updated_by):
            # 创建预留流水记录
            transaction = InventoryTransaction(
                inventory_id=inventory.id,
                warehouse_id=inventory.warehouse_id,
                product_id=inventory.product_id,
                material_id=inventory.material_id,
                transaction_type='reserve',
                quantity_change=-quantity,  # 预留减少可用数量
                quantity_before=inventory.available_quantity + quantity,
                quantity_after=inventory.available_quantity,
                unit=inventory.unit,
                reason=reason or '库存预留',
                created_by=updated_by
            )
            
            self.db.add(transaction)
            self.db.commit()
            return True
        
        return False
    
    def unreserve_inventory(
        self,
        inventory_id: str,
        quantity: Decimal,
        updated_by: str,
        reason: str = None
    ) -> bool:
        """取消预留库存"""
        self._set_schema()
        
        inventory = self.get_inventory_by_id(inventory_id)
        if not inventory:
            raise ValueError(f"库存记录不存在: {inventory_id}")
        
        if inventory.unreserve_quantity(quantity, updated_by):
            # 创建取消预留流水记录
            transaction = InventoryTransaction(
                inventory_id=inventory.id,
                warehouse_id=inventory.warehouse_id,
                product_id=inventory.product_id,
                material_id=inventory.material_id,
                transaction_type='unreserve',
                quantity_change=quantity,  # 取消预留增加可用数量
                quantity_before=inventory.available_quantity - quantity,
                quantity_after=inventory.available_quantity,
                unit=inventory.unit,
                reason=reason or '取消预留',
                created_by=updated_by
            )
            
            self.db.add(transaction)
            self.db.commit()
            return True
        
        return False
    
    # ================ 库存调拨方法 ================
    
    def transfer_inventory(
        self,
        from_inventory_id: str,
        to_warehouse_id: str,
        quantity: Decimal,
        transferred_by: str,
        to_location_code: str = None,
        reason: str = None,
        notes: str = None
    ) -> tuple[InventoryTransaction, InventoryTransaction]:
        """库存调拨"""
        from_inventory = self.get_inventory_by_id(from_inventory_id)
        if not from_inventory:
            raise ValueError(f"源库存记录不存在: {from_inventory_id}")
        
        if from_inventory.available_quantity < quantity:
            raise ValueError("源库存数量不足")
        
        # 查找或创建目标库存记录
        to_inventory = self.get_inventory_by_warehouse_and_item(
            warehouse_id=to_warehouse_id,
            product_id=from_inventory.product_id,
            material_id=from_inventory.material_id,
            batch_number=from_inventory.batch_number,
            location_code=to_location_code
        )
        
        if not to_inventory:
            # 创建新的库存记录
            to_inventory = self.create_inventory(
                warehouse_id=to_warehouse_id,
                product_id=from_inventory.product_id,
                material_id=from_inventory.material_id,
                unit=from_inventory.unit,
                batch_number=from_inventory.batch_number,
                location_code=to_location_code,
                unit_cost=from_inventory.unit_cost,
                inventory_status=from_inventory.inventory_status,
                quality_status=from_inventory.quality_status,
                created_by=transferred_by,
                current_quantity=0,
                available_quantity=0
            )
        
        # 生成调拨单号
        transfer_number = f"TF{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建出库流水
        out_transaction = self.update_inventory_quantity(
            inventory_id=from_inventory.id,
            quantity_change=-quantity,
            transaction_type='transfer_out',
            updated_by=transferred_by,
            source_document_type='transfer_order',
            source_document_number=transfer_number,
            reason=reason or '库存调拨出库',
            notes=notes,
            to_location=to_location_code
        )
        
        # 创建入库流水
        in_transaction = self.update_inventory_quantity(
            inventory_id=to_inventory.id,
            quantity_change=quantity,
            transaction_type='transfer_in',
            updated_by=transferred_by,
            source_document_type='transfer_order',
            source_document_number=transfer_number,
            reason=reason or '库存调拨入库',
            notes=notes,
            from_location=from_inventory.location_code
        )
        
        return out_transaction, in_transaction
    
    # ================ 盘点管理方法 ================
    
    def create_count_plan(
        self,
        plan_name: str,
        count_type: str,
        plan_start_date: datetime,
        plan_end_date: datetime,
        created_by: str,
        **kwargs
    ) -> InventoryCountPlan:
        """创建盘点计划"""
        count_plan = InventoryCountPlan(
            plan_name=plan_name,
            count_type=count_type,
            plan_start_date=plan_start_date,
            plan_end_date=plan_end_date,
            created_by=created_by,
            **kwargs
        )
        
        self.db.add(count_plan)
        self.db.commit()
        self.db.refresh(count_plan)
        
        return count_plan
    
    def generate_count_records(
        self,
        count_plan_id: str,
        created_by: str,
        warehouse_ids: List[str] = None
    ) -> List[InventoryCountRecord]:
        """为盘点计划生成盘点记录"""
        count_plan = self.db.query(InventoryCountPlan).filter(
            InventoryCountPlan.id == count_plan_id
        ).first()
        
        if not count_plan:
            raise ValueError(f"盘点计划不存在: {count_plan_id}")
        
        # 构建查询条件
        query = self.db.query(Inventory).filter(Inventory.is_active == True)
        
        # 根据盘点范围筛选库存
        if warehouse_ids or count_plan.warehouse_ids:
            target_warehouses = warehouse_ids or count_plan.warehouse_ids
            query = query.filter(Inventory.warehouse_id.in_(target_warehouses))
        
        if count_plan.location_codes:
            query = query.filter(Inventory.location_code.in_(count_plan.location_codes))
        
        inventories = query.all()
        
        count_records = []
        for inventory in inventories:
            count_record = InventoryCountRecord(
                count_plan_id=count_plan.id,
                inventory_id=inventory.id,
                warehouse_id=inventory.warehouse_id,
                product_id=inventory.product_id,
                material_id=inventory.material_id,
                book_quantity=inventory.current_quantity,
                batch_number=inventory.batch_number,
                location_code=inventory.location_code,
                unit=inventory.unit,
                created_by=created_by
            )
            count_records.append(count_record)
        
        self.db.add_all(count_records)
        self.db.commit()
        
        for record in count_records:
            self.db.refresh(record)
        
        return count_records
    
    def record_count_result(
        self,
        count_record_id: str,
        actual_quantity: Decimal,
        count_by: str,
        variance_reason: str = None,
        notes: str = None
    ) -> InventoryCountRecord:
        """记录盘点结果"""
        count_record = self.db.query(InventoryCountRecord).filter(
            InventoryCountRecord.id == count_record_id
        ).first()
        
        if not count_record:
            raise ValueError(f"盘点记录不存在: {count_record_id}")
        
        count_record.actual_quantity = actual_quantity
        count_record.count_by = count_by
        count_record.count_date = datetime.now()
        count_record.variance_reason = variance_reason
        count_record.notes = notes
        count_record.status = 'counted'
        
        # 计算差异
        count_record.calculate_variance()
        
        self.db.commit()
        self.db.refresh(count_record)
        
        return count_record
    
    def adjust_inventory_by_count(
        self,
        count_record_id: str,
        adjusted_by: str,
        reason: str = None
    ) -> Optional[InventoryTransaction]:
        """根据盘点结果调整库存"""
        count_record = self.db.query(InventoryCountRecord).filter(
            InventoryCountRecord.id == count_record_id
        ).first()
        
        if not count_record:
            raise ValueError(f"盘点记录不存在: {count_record_id}")
        
        if count_record.variance_quantity == 0:
            return None  # 无需调整
        
        if count_record.is_adjusted:
            raise ValueError("该盘点记录已经调整过库存")
        
        # 创建库存调整流水
        transaction_type = 'adjustment_in' if count_record.variance_quantity > 0 else 'adjustment_out'
        
        transaction = self.update_inventory_quantity(
            inventory_id=count_record.inventory_id,
            quantity_change=count_record.variance_quantity,
            transaction_type=transaction_type,
            updated_by=adjusted_by,
            source_document_type='count_order',
            source_document_id=count_record.count_plan_id,
            source_document_number=count_record.count_plan.plan_number,
            reason=reason or f'盘点调整: {count_record.variance_reason}',
            notes=f'盘点差异调整，差异数量: {count_record.variance_quantity}'
        )
        
        # 更新盘点记录状态
        count_record.is_adjusted = True
        count_record.adjustment_transaction_id = transaction.id
        count_record.status = 'adjusted'
        
        self.db.commit()
        
        return transaction
    
    # ================ 报表统计方法 ================
    
    def get_inventory_aging_report(
        self,
        warehouse_id: str = None,
        days_threshold: int = 90
    ) -> List[Dict[str, Any]]:
        """获取库存账龄报表"""
        query = self.db.query(Inventory).filter(
            and_(
                Inventory.is_active == True,
                Inventory.current_quantity > 0
            )
        )
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        inventories = query.all()
        
        aging_data = []
        current_date = datetime.now()
        
        for inventory in inventories:
            # 获取最早的入库记录
            earliest_transaction = self.db.query(InventoryTransaction).filter(
                and_(
                    InventoryTransaction.inventory_id == inventory.id,
                    InventoryTransaction.transaction_type.in_(['in', 'purchase_in', 'production_in']),
                    InventoryTransaction.is_cancelled == False
                )
            ).order_by(InventoryTransaction.transaction_date.asc()).first()
            
            if earliest_transaction:
                days_in_stock = (current_date - earliest_transaction.transaction_date).days
                
                aging_data.append({
                    'inventory_id': str(inventory.id),
                    'warehouse_id': str(inventory.warehouse_id),
                    'product_id': str(inventory.product_id) if inventory.product_id else None,
                    'material_id': str(inventory.material_id) if inventory.material_id else None,
                    'current_quantity': float(inventory.current_quantity),
                    'unit': inventory.unit,
                    'total_cost': float(inventory.total_cost) if inventory.total_cost else 0,
                    'earliest_in_date': earliest_transaction.transaction_date.isoformat(),
                    'days_in_stock': days_in_stock,
                    'is_slow_moving': days_in_stock >= days_threshold
                })
        
        return aging_data
    
    def get_inventory_turnover_report(
        self,
        warehouse_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Dict[str, Any]]:
        """获取库存周转率报表"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()
        
        # 查询期间内的出库记录
        query = self.db.query(
            InventoryTransaction.inventory_id,
            func.sum(func.abs(InventoryTransaction.quantity_change)).label('total_out_quantity'),
            func.sum(InventoryTransaction.total_amount).label('total_out_amount')
        ).filter(
            and_(
                InventoryTransaction.transaction_type.in_(['out', 'sales_out', 'production_out']),
                InventoryTransaction.transaction_date.between(start_date, end_date),
                InventoryTransaction.is_cancelled == False
            )
        )
        
        if warehouse_id:
            query = query.filter(InventoryTransaction.warehouse_id == warehouse_id)
        
        out_data = query.group_by(InventoryTransaction.inventory_id).all()
        
        turnover_data = []
        for data in out_data:
            inventory = self.get_inventory_by_id(str(data.inventory_id))
            if inventory and inventory.current_quantity > 0:
                # 计算平均库存（简化为当前库存）
                avg_inventory = inventory.current_quantity
                turnover_rate = float(data.total_out_quantity) / float(avg_inventory) if avg_inventory > 0 else 0
                
                turnover_data.append({
                    'inventory_id': str(inventory.id),
                    'warehouse_id': str(inventory.warehouse_id),
                    'product_id': str(inventory.product_id) if inventory.product_id else None,
                    'material_id': str(inventory.material_id) if inventory.material_id else None,
                    'current_quantity': float(inventory.current_quantity),
                    'total_out_quantity': float(data.total_out_quantity),
                    'total_out_amount': float(data.total_out_amount) if data.total_out_amount else 0,
                    'turnover_rate': round(turnover_rate, 2),
                    'period_days': (end_date - start_date).days
                })
        
        return turnover_data
    
    # ================ 库存预警方法 ================
    
    def get_low_stock_alerts(self, warehouse_id: str = None) -> List[Dict[str, Any]]:
        """获取低库存预警"""
        query = self.db.query(Inventory).filter(
            and_(
                Inventory.is_active == True,
                Inventory.current_quantity <= Inventory.safety_stock
            )
        )
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        low_stock_items = query.all()
        
        alerts = []
        for item in low_stock_items:
            alerts.append({
                'inventory_id': str(item.id),
                'warehouse_id': str(item.warehouse_id),
                'product_id': str(item.product_id) if item.product_id else None,
                'material_id': str(item.material_id) if item.material_id else None,
                'current_quantity': float(item.current_quantity),
                'safety_stock': float(item.safety_stock),
                'shortage': float(item.safety_stock - item.current_quantity),
                'unit': item.unit,
                'alert_level': 'critical' if item.current_quantity <= 0 else 'warning'
            })
        
        return alerts
    
    def get_expiring_inventory_alerts(
        self, 
        warehouse_id: str = None, 
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """获取即将过期库存预警"""
        expiry_threshold = datetime.now() + timedelta(days=days_ahead)
        
        query = self.db.query(Inventory).filter(
            and_(
                Inventory.is_active == True,
                Inventory.expiry_date.isnot(None),
                Inventory.expiry_date <= expiry_threshold,
                Inventory.current_quantity > 0
            )
        )
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        expiring_items = query.all()
        
        alerts = []
        current_date = datetime.now()
        
        for item in expiring_items:
            days_to_expiry = (item.expiry_date - current_date).days
            
            alerts.append({
                'inventory_id': str(item.id),
                'warehouse_id': str(item.warehouse_id),
                'product_id': str(item.product_id) if item.product_id else None,
                'material_id': str(item.material_id) if item.material_id else None,
                'current_quantity': float(item.current_quantity),
                'expiry_date': item.expiry_date.isoformat(),
                'days_to_expiry': days_to_expiry,
                'unit': item.unit,
                'batch_number': item.batch_number,
                'alert_level': 'critical' if days_to_expiry <= 0 else ('warning' if days_to_expiry <= 7 else 'info')
            })
        
        return alerts
    
    # ================ 入库单管理方法 ================
    
    def get_inbound_order_list(
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
        """获取入库单列表"""
        self._set_schema()
        query = self.db.query(InboundOrder)
        
        if warehouse_id:
            query = query.filter(InboundOrder.warehouse_id == warehouse_id)
        
        if order_type:
            query = query.filter(InboundOrder.order_type == order_type)
        
        if status:
            query = query.filter(InboundOrder.status == status)
        
        if approval_status:
            query = query.filter(InboundOrder.approval_status == approval_status)
        
        if start_date:
            query = query.filter(InboundOrder.order_date >= start_date)
        
        if end_date:
            query = query.filter(InboundOrder.order_date <= end_date)
        
        if search:
            query = query.filter(
                or_(
                    InboundOrder.order_number.ilike(f'%{search}%'),
                    InboundOrder.warehouse_name.ilike(f'%{search}%'),
                    InboundOrder.inbound_person.ilike(f'%{search}%'),
                    InboundOrder.department.ilike(f'%{search}%')
                )
            )
        
        total = query.count()
        orders = query.order_by(InboundOrder.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        # 批量获取仓库信息并填充仓库名称
        self._fill_warehouse_info(orders)
        
        return {
            'items': [order.to_dict() for order in orders],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }
    
    def get_inbound_order_by_id(self, order_id: str) -> Optional[InboundOrder]:
        """根据ID获取入库单"""
        self._set_schema()
        order = self.db.query(InboundOrder).filter(InboundOrder.id == order_id).first()
        if order:
            # 填充仓库信息
            self._fill_warehouse_info([order])
        return order
    
    def get_inbound_order_details(self, order_id: str) -> List[Dict[str, Any]]:
        """获取入库单详情列表"""
        self._set_schema()
        details = self.db.query(InboundOrderDetail).filter(
            InboundOrderDetail.inbound_order_id == order_id
        ).all()
        
        return [detail.to_dict() for detail in details]
    
    def create_inbound_order(
        self,
        data: dict,
        created_by: str
    ) -> InboundOrder:
        """创建入库单"""
        self._set_schema()
        
        # 从用户ID获取用户信息
        from app.models.user import User
        user = self.db.query(User).get(uuid.UUID(created_by))
        created_by_name = user.get_full_name() if user else '未知用户'
        
        inbound_order = InboundOrder(
            warehouse_id=data.get('warehouse_id'),
            order_type=data.get('order_type', 'finished_goods'),
            warehouse_name=data.get('warehouse_name'),
            inbound_person=data.get('inbound_person'),
            department=data.get('department'),
            order_date=data.get('order_date'),
            pallet_barcode=data.get('pallet_barcode'),
            pallet_count=data.get('pallet_count'),
            notes=data.get('notes'),
            created_by=uuid.UUID(created_by)
        )
        
        self.db.add(inbound_order)
        self.db.commit()
        self.db.refresh(inbound_order)
        
        # 填充仓库信息
        self._fill_warehouse_info([inbound_order])
        
        return inbound_order
    
    def update_inbound_order(
        self,
        order_id: str,
        updated_by: str,
        **update_data
    ) -> Optional[InboundOrder]:
        """更新入库单"""
        self._set_schema()
        inbound_order = self.get_inbound_order_by_id(order_id)
        if not inbound_order:
            raise ValueError(f"入库单不存在: {order_id}")
        
        # 检查状态是否允许修改
        if inbound_order.status in ['completed', 'cancelled']:
            raise ValueError("已完成或已取消的入库单不能修改")
        
        # 更新字段
        for field, value in update_data.items():
            if hasattr(inbound_order, field) and field not in ['id', 'order_number', 'created_at', 'created_by']:
                setattr(inbound_order, field, value)
        
        inbound_order.updated_by = updated_by
        inbound_order.updated_at = func.now()
        
        self.db.commit()
        self.db.refresh(inbound_order)
        
        return inbound_order
    
    def add_inbound_order_detail(
        self,
        order_id: str,
        inbound_quantity: Decimal,
        unit: str,
        created_by: str,
        product_id: str = None,
        product_name: str = None,
        **kwargs
    ) -> InboundOrderDetail:
        """添加入库单明细"""
        self._set_schema()
        
        # 验证入库单是否存在
        inbound_order = self.get_inbound_order_by_id(order_id)
        if not inbound_order:
            raise ValueError(f"入库单不存在: {order_id}")
        
        # 检查状态是否允许添加明细
        if inbound_order.status in ['completed', 'cancelled']:
            raise ValueError("已完成或已取消的入库单不能添加明细")
        
        detail = InboundOrderDetail(
            inbound_order_id=order_id,
            inbound_quantity=inbound_quantity,
            unit=unit,
            created_by=created_by,
            product_id=product_id,
            product_name=product_name,
            **kwargs
        )
        
        # 计算总成本
        detail.calculate_total_cost()
        
        self.db.add(detail)
        self.db.commit()
        self.db.refresh(detail)
        
        return detail
    
    def update_inbound_order_detail(
        self,
        detail_id: str,
        updated_by: str,
        **update_data
    ) -> Optional[InboundOrderDetail]:
        """更新入库单明细"""
        self._set_schema()
        detail = self.db.query(InboundOrderDetail).filter(
            InboundOrderDetail.id == detail_id
        ).first()
        
        if not detail:
            raise ValueError(f"入库单明细不存在: {detail_id}")
        
        # 检查主单状态
        inbound_order = detail.inbound_order
        if inbound_order.status in ['completed', 'cancelled']:
            raise ValueError("已完成或已取消的入库单明细不能修改")
        
        # 更新字段
        for field, value in update_data.items():
            if hasattr(detail, field) and field not in ['id', 'inbound_order_id', 'created_at', 'created_by']:
                setattr(detail, field, value)
        
        # 重新计算总成本
        detail.calculate_total_cost()
        detail.updated_by = updated_by
        detail.updated_at = func.now()
        
        self.db.commit()
        self.db.refresh(detail)
        
        return detail
    
    def delete_inbound_order_detail(self, detail_id: str) -> bool:
        """删除入库单明细"""
        self._set_schema()
        detail = self.db.query(InboundOrderDetail).filter(
            InboundOrderDetail.id == detail_id
        ).first()
        
        if not detail:
            return False
        
        # 检查主单状态
        inbound_order = detail.inbound_order
        if inbound_order.status in ['completed', 'cancelled']:
            raise ValueError("已完成或已取消的入库单明细不能删除")
        
        self.db.delete(detail)
        self.db.commit()
        
        return True
    
    def approve_inbound_order(
        self,
        order_id: str,
        approved_by: str,
        approval_status: str = 'approved'
    ) -> InboundOrder:
        """审核入库单"""
        self._set_schema()
        inbound_order = self.get_inbound_order_by_id(order_id)
        if not inbound_order:
            raise ValueError(f"入库单不存在: {order_id}")
        
        if inbound_order.approval_status != 'pending':
            raise ValueError("只能审核待审核状态的入库单")
        
        inbound_order.approval_status = approval_status
        # 修复UUID转换错误
        try:
            inbound_order.approved_by = uuid.UUID(approved_by) if isinstance(approved_by, str) else approved_by
        except (ValueError, TypeError):
            inbound_order.approved_by = approved_by
        inbound_order.approved_at = func.now()
        
        # 如果审核通过，更新状态为已确认
        if approval_status == 'approved':
            inbound_order.status = 'confirmed'
        
        self.db.commit()
        self.db.refresh(inbound_order)
        
        return inbound_order
    
    def execute_inbound_order(
        self,
        order_id: str,
        executed_by: str,
        auto_create_inventory: bool = True
    ) -> List[InventoryTransaction]:
        """执行入库单 - 创建库存流水并更新库存"""
        self._set_schema()
        inbound_order = self.get_inbound_order_by_id(order_id)
        if not inbound_order:
            raise ValueError(f"入库单不存在: {order_id}")
        
        if inbound_order.approval_status != 'approved':
            raise ValueError("只能执行已审核通过的入库单")
        
        if inbound_order.status != 'confirmed':
            raise ValueError("只能执行已确认状态的入库单")
        
        if not inbound_order.details:
            raise ValueError("入库单没有明细，无法执行")
        
        transactions = []
        
        try:
            # 更新入库单状态
            inbound_order.status = 'in_progress'
            self.db.commit()
            
            for detail in inbound_order.details:
                # 查找或创建库存记录
                inventory = self.get_inventory_by_warehouse_and_item(
                    warehouse_id=inbound_order.warehouse_id,
                    product_id=detail.product_id,
                    batch_number=detail.batch_number,
                    location_code=detail.actual_location_code or detail.location_code
                )
                
                if not inventory and auto_create_inventory:
                    # 创建新的库存记录
                    inventory = self.create_inventory(
                        warehouse_id=inbound_order.warehouse_id,
                        product_id=detail.product_id,
                        unit=detail.unit,
                        batch_number=detail.batch_number,
                        location_code=detail.actual_location_code or detail.location_code,
                        unit_cost=detail.unit_cost,
                        created_by=executed_by,
                        current_quantity=0,
                        available_quantity=0
                    )
                
                if not inventory:
                    raise ValueError(f"找不到对应的库存记录: 产品{detail.product_name}")
                
                # 创建入库流水
                transaction = self.update_inventory_quantity(
                    inventory_id=inventory.id,
                    quantity_change=detail.inbound_quantity,
                    transaction_type='in',
                    updated_by=executed_by,
                    source_document_type='inbound_order',
                    source_document_id=inbound_order.id,
                    source_document_number=inbound_order.order_number,
                    unit_price=detail.unit_cost,
                    reason=f'入库单入库: {inbound_order.order_number}',
                    batch_number=detail.batch_number,
                    to_location=detail.actual_location_code or detail.location_code
                )
                
                transactions.append(transaction)
            
            # 更新入库单状态为已完成
            inbound_order.status = 'completed'
            self.db.commit()
            
            return transactions
            
        except Exception as e:
            # 回滚状态
            inbound_order.status = 'confirmed'
            self.db.rollback()
            raise e
    
    def cancel_inbound_order(
        self,
        order_id: str,
        cancelled_by: str,
        cancel_reason: str = None
    ) -> InboundOrder:
        """取消入库单"""
        self._set_schema()
        inbound_order = self.get_inbound_order_by_id(order_id)
        if not inbound_order:
            raise ValueError(f"入库单不存在: {order_id}")
        
        if inbound_order.status == 'completed':
            raise ValueError("已完成的入库单不能取消")
        
        if inbound_order.status == 'cancelled':
            raise ValueError("入库单已经被取消")
        
        inbound_order.status = 'cancelled'
        # 修复UUID转换错误
        try:
            inbound_order.updated_by = uuid.UUID(cancelled_by) if isinstance(cancelled_by, str) else cancelled_by
        except (ValueError, TypeError):
            inbound_order.updated_by = cancelled_by
        inbound_order.updated_at = func.now()
        
        if cancel_reason:
            inbound_order.notes = f"{inbound_order.notes or ''}\n取消原因: {cancel_reason}".strip()
        
        self.db.commit()
        self.db.refresh(inbound_order)
        
        return inbound_order


# ================ 工厂函数 ================

def get_inventory_service(db: Session = None) -> InventoryService:
    """获取库存服务实例"""
    if db is None:
        from app.core.database import SessionLocal
        db = SessionLocal()
    
    return InventoryService(db) 