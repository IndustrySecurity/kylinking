"""
成品盘点服务
提供成品盘点的业务逻辑处理
"""

from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime
import uuid

from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import joinedload
from app.models.business.inventory import ProductCountPlan, ProductCountRecord, Inventory, InventoryTransaction
from app.models.basic_data import Product, Warehouse, Employee, Department
from app.utils.tenant_context import TenantContext
from app.extensions import db


class ProductCountService:
    """成品盘点服务"""
    
    @staticmethod
    def create_count_plan(data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """
        创建成品盘点计划
        
        Args:
            data: 盘点计划数据
            created_by: 创建人ID
            
        Returns:
            创建的盘点计划信息
        """
        try:
            tenant_context = TenantContext()
            
            # 转换UUID字段
            warehouse_id = uuid.UUID(data['warehouse_id'])
            count_person_id = uuid.UUID(data['count_person_id'])
            created_by_uuid = uuid.UUID(created_by)
            department_id = uuid.UUID(data['department_id']) if data.get('department_id') else None
            
            # 获取仓库信息
            warehouse = db.session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                raise ValueError("仓库不存在")
            
            # 获取盘点人信息
            count_person = db.session.query(Employee).filter(Employee.id == count_person_id).first()
            if not count_person:
                raise ValueError("盘点人不存在")
            
            # 准备盘点计划数据
            count_data = {
                'warehouse_id': warehouse_id,
                'warehouse_name': warehouse.warehouse_name,
                'warehouse_code': warehouse.warehouse_code,
                'count_person_id': count_person_id,
                'count_date': datetime.fromisoformat(data['count_date'].replace('Z', '+00:00')),
                'created_by': created_by_uuid
            }
            
            # 添加可选字段
            if department_id:
                count_data['department_id'] = department_id
            if data.get('notes'):
                count_data['notes'] = data['notes']
            
            # 创建盘点计划
            count_plan = ProductCountPlan(**count_data)
            
            db.session.add(count_plan)
            db.session.flush()
            
            # 自动获取该仓库的成品库存并生成盘点记录
            ProductCountService._generate_count_records(count_plan.id, warehouse_id, created_by_uuid)
            
            db.session.commit()
            
            return count_plan.to_dict()
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"创建盘点计划失败: {str(e)}")
    
    @staticmethod
    def _generate_count_records(count_plan_id: uuid.UUID, warehouse_id: uuid.UUID, created_by: uuid.UUID):
        """
        为盘点计划生成盘点记录
        
        Args:
            count_plan_id: 盘点计划ID
            warehouse_id: 仓库ID
            created_by: 创建人ID
        """
        # 查询该仓库的所有成品库存
        inventories = db.session.query(Inventory).filter(
            and_(
                Inventory.warehouse_id == warehouse_id,
                Inventory.product_id.isnot(None),  # 只查询成品库存
                Inventory.current_quantity > 0  # 只查询有库存的
            )
        ).all()
        
        for inventory in inventories:
            # 获取产品信息
            product = db.session.query(Product).filter(Product.id == inventory.product_id).first()
            if not product:
                continue
            
            # 创建盘点记录
            record_data = {
                'count_plan_id': count_plan_id,
                'inventory_id': inventory.id,
                'product_id': inventory.product_id,
                'product_code': product.product_code,
                'product_name': product.product_name,
                'product_spec': product.specification or '',
                'base_unit': inventory.unit or product.base_unit,
                'book_quantity': inventory.current_quantity,
                'batch_number': inventory.batch_number,
                'production_date': inventory.production_date,
                'expiry_date': inventory.expiry_date,
                'location_code': inventory.location_code,
                'created_by': created_by
            }
            
            # 添加产品特有字段
            if hasattr(product, 'customer_id') and product.customer_id:
                record_data['customer_id'] = product.customer_id
                record_data['customer_name'] = getattr(product.customer, 'customer_name', '') if hasattr(product, 'customer') and product.customer else ''
            
            if hasattr(product, 'bag_type_id') and product.bag_type_id:
                record_data['bag_type_id'] = product.bag_type_id
                record_data['bag_type_name'] = getattr(product.bag_type, 'bag_type_name', '') if hasattr(product, 'bag_type') and product.bag_type else ''
            
            # 包装信息
            if hasattr(product, 'package_unit'):
                record_data['package_unit'] = product.package_unit
            if hasattr(product, 'net_weight'):
                record_data['net_weight'] = product.net_weight
            if hasattr(product, 'gross_weight'):
                record_data['gross_weight'] = product.gross_weight
            
            count_record = ProductCountRecord(**record_data)
            db.session.add(count_record)
    
    @staticmethod
    def get_count_plans(page: int = 1, page_size: int = 20, **filters) -> Dict[str, Any]:
        """
        获取盘点计划列表
        
        Args:
            page: 页码
            page_size: 每页数量
            **filters: 筛选条件
            
        Returns:
            盘点计划列表和分页信息
        """
        try:
            tenant_context = TenantContext()
            
            query = db.session.query(ProductCountPlan)
            
            # 应用筛选条件
            if filters.get('warehouse_id'):
                query = query.filter(ProductCountPlan.warehouse_id == uuid.UUID(filters['warehouse_id']))
            
            if filters.get('status'):
                query = query.filter(ProductCountPlan.status == filters['status'])
            
            if filters.get('count_person_id'):
                query = query.filter(ProductCountPlan.count_person_id == uuid.UUID(filters['count_person_id']))
            
            if filters.get('start_date') and filters.get('end_date'):
                start_date = datetime.fromisoformat(filters['start_date'].replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(filters['end_date'].replace('Z', '+00:00'))
                query = query.filter(ProductCountPlan.count_date.between(start_date, end_date))
            
            # 搜索条件
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        ProductCountPlan.count_number.ilike(search_term),
                        ProductCountPlan.warehouse_name.ilike(search_term),
                        ProductCountPlan.notes.ilike(search_term)
                    )
                )
            
            # 总数统计
            total = query.count()
            
            # 排序和分页
            query = query.order_by(ProductCountPlan.created_at.desc())
            plans = query.offset((page - 1) * page_size).limit(page_size).all()
            
            return {
                'items': [plan.to_dict() for plan in plans],
                'total': total,
                'page': page,
                'page_size': page_size,
                'pages': (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            raise Exception(f"获取盘点计划列表失败: {str(e)}")
    
    @staticmethod
    def get_count_plan(plan_id: str) -> Dict[str, Any]:
        """
        获取盘点计划详情
        
        Args:
            plan_id: 盘点计划ID
            
        Returns:
            盘点计划详情
        """
        try:
            tenant_context = TenantContext()
            
            plan = db.session.query(ProductCountPlan).options(
                joinedload(ProductCountPlan.count_person),
                joinedload(ProductCountPlan.department)
            ).filter(ProductCountPlan.id == uuid.UUID(plan_id)).first()
            
            if not plan:
                raise ValueError("盘点计划不存在")
            
            return plan.to_dict()
            
        except Exception as e:
            raise Exception(f"获取盘点计划详情失败: {str(e)}")
    
    @staticmethod
    def get_count_records(plan_id: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """
        获取盘点记录列表
        
        Args:
            plan_id: 盘点计划ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            盘点记录列表和分页信息
        """
        try:
            tenant_context = TenantContext()
            
            query = db.session.query(ProductCountRecord).filter(
                ProductCountRecord.count_plan_id == uuid.UUID(plan_id)
            )
            
            total = query.count()
            
            records = query.order_by(ProductCountRecord.product_code, ProductCountRecord.product_name)\
                           .offset((page - 1) * page_size).limit(page_size).all()
            
            return {
                'items': [record.to_dict() for record in records],
                'total': total,
                'page': page,
                'page_size': page_size,
                'pages': (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            raise Exception(f"获取盘点记录失败: {str(e)}")
    
    @staticmethod
    def update_count_record(plan_id: str, record_id: str, data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """
        更新盘点记录
        
        Args:
            plan_id: 盘点计划ID
            record_id: 盘点记录ID
            data: 更新数据
            updated_by: 更新人ID
            
        Returns:
            更新后的盘点记录
        """
        try:
            tenant_context = TenantContext()
            
            record = db.session.query(ProductCountRecord).filter(
                and_(
                    ProductCountRecord.id == uuid.UUID(record_id),
                    ProductCountRecord.count_plan_id == uuid.UUID(plan_id)
                )
            ).first()
            
            if not record:
                raise ValueError("盘点记录不存在")
            
            # 更新实盘数量
            if 'actual_quantity' in data:
                record.actual_quantity = Decimal(str(data['actual_quantity']))
                record.calculate_variance()
            
            # 更新其他字段
            if 'variance_reason' in data:
                record.variance_reason = data['variance_reason']
            
            if 'notes' in data:
                record.notes = data['notes']
            
            if 'status' in data:
                record.status = data['status']
            
            record.updated_by = uuid.UUID(updated_by)
            
            db.session.commit()
            
            return record.to_dict()
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"更新盘点记录失败: {str(e)}")
    
    @staticmethod
    def start_count_plan(plan_id: str, updated_by: str) -> Dict[str, Any]:
        """
        开始盘点计划
        
        Args:
            plan_id: 盘点计划ID
            updated_by: 更新人ID
            
        Returns:
            更新后的盘点计划
        """
        try:
            tenant_context = TenantContext()
            
            plan = db.session.query(ProductCountPlan).filter(ProductCountPlan.id == uuid.UUID(plan_id)).first()
            
            if not plan:
                raise ValueError("盘点计划不存在")
            
            if plan.status != 'draft':
                raise ValueError("只有草稿状态的盘点计划才能开始")
            
            # 检查是否已有盘点记录，如果没有则生成
            existing_records = db.session.query(ProductCountRecord).filter(
                ProductCountRecord.count_plan_id == uuid.UUID(plan_id)
            ).count()
            
            if existing_records == 0:
                # 生成盘点记录
                ProductCountService._generate_count_records(
                    count_plan_id=uuid.UUID(plan_id),
                    warehouse_id=plan.warehouse_id,
                    created_by=uuid.UUID(updated_by)
                )
            
            plan.status = 'in_progress'
            plan.updated_by = uuid.UUID(updated_by)
            
            db.session.commit()
            
            return plan.to_dict()
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"开始盘点计划失败: {str(e)}")
    
    @staticmethod
    def complete_count_plan(plan_id: str, updated_by: str) -> Dict[str, Any]:
        """
        完成盘点计划
        
        Args:
            plan_id: 盘点计划ID
            updated_by: 更新人ID
            
        Returns:
            更新后的盘点计划
        """
        try:
            tenant_context = TenantContext()
            
            plan = db.session.query(ProductCountPlan).filter(ProductCountPlan.id == uuid.UUID(plan_id)).first()
            
            if not plan:
                raise ValueError("盘点计划不存在")
            
            if plan.status != 'in_progress':
                raise ValueError("只有进行中的盘点计划才能完成")
            
            # 检查是否所有记录都已盘点
            pending_count = db.session.query(ProductCountRecord).filter(
                and_(
                    ProductCountRecord.count_plan_id == uuid.UUID(plan_id),
                    ProductCountRecord.status == 'pending'
                )
            ).count()
            
            if pending_count > 0:
                raise ValueError(f"还有 {pending_count} 条记录未盘点完成")
            
            plan.status = 'completed'
            plan.updated_by = uuid.UUID(updated_by)
            
            db.session.commit()
            
            return plan.to_dict()
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"完成盘点计划失败: {str(e)}")
    
    @staticmethod
    def adjust_inventory(plan_id: str, record_ids: List[str], updated_by: str) -> Dict[str, Any]:
        """
        根据盘点结果调整库存
        
        Args:
            plan_id: 盘点计划ID
            record_ids: 需要调整的记录ID列表
            updated_by: 操作人ID
            
        Returns:
            调整结果
        """
        try:
            tenant_context = TenantContext()
            
            plan = db.session.query(ProductCountPlan).filter(ProductCountPlan.id == uuid.UUID(plan_id)).first()
            
            if not plan:
                raise ValueError("盘点计划不存在")
            
            if plan.status != 'completed':
                raise ValueError("只有已完成的盘点计划才能调整库存")
            
            adjustment_count = 0
            
            # 如果没有指定record_ids，则处理所有有差异且未调整的记录
            if not record_ids:
                records_to_adjust = db.session.query(ProductCountRecord).filter(
                    and_(
                        ProductCountRecord.count_plan_id == uuid.UUID(plan_id),
                        ProductCountRecord.variance_quantity != 0,
                        ProductCountRecord.variance_quantity.isnot(None),
                        ProductCountRecord.is_adjusted == False
                    )
                ).all()
                record_ids = [str(record.id) for record in records_to_adjust]
            
            for record_id in record_ids:
                record = db.session.query(ProductCountRecord).filter(
                    and_(
                        ProductCountRecord.id == uuid.UUID(record_id),
                        ProductCountRecord.count_plan_id == uuid.UUID(plan_id)
                    )
                ).first()
                
                if not record or record.is_adjusted:
                    continue
                
                if record.variance_quantity is None or record.variance_quantity == 0:
                    continue
                
                # 获取库存记录
                inventory = db.session.query(Inventory).filter(Inventory.id == record.inventory_id).first()
                
                if not inventory:
                    continue
                
                # 调整库存
                old_quantity = inventory.current_quantity
                inventory.current_quantity = record.actual_quantity
                inventory.available_quantity = record.actual_quantity - inventory.reserved_quantity
                inventory.updated_by = uuid.UUID(updated_by)
                
                # 创建库存流水记录
                transaction_type = 'adjustment_in' if record.variance_quantity > 0 else 'adjustment_out'
                transaction = InventoryTransaction(
                    inventory_id=inventory.id,
                    warehouse_id=inventory.warehouse_id,
                    product_id=inventory.product_id,
                    transaction_type=transaction_type,
                    quantity_change=record.variance_quantity,
                    quantity_before=old_quantity,
                    quantity_after=record.actual_quantity,
                    unit=inventory.unit,
                    source_document_type='count_order',
                    source_document_id=plan.id,
                    source_document_number=plan.count_number,
                    reason=f"成品盘点调整: {record.variance_reason or '盘点差异'}",
                    created_by=uuid.UUID(updated_by)
                )
                
                db.session.add(transaction)
                
                # 标记记录为已调整
                record.is_adjusted = True
                record.status = 'adjusted'
                record.updated_by = uuid.UUID(updated_by)
                
                adjustment_count += 1
            
            # 更新盘点计划状态
            plan.status = 'adjusted'
            plan.updated_by = uuid.UUID(updated_by)
            
            db.session.commit()
            
            return {
                'message': f'成功调整 {adjustment_count} 条记录的库存',
                'adjustment_count': adjustment_count
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"调整库存失败: {str(e)}")
    
    @staticmethod
    def get_warehouse_product_inventory(warehouse_id: str) -> List[Dict[str, Any]]:
        """
        获取仓库成品库存
        
        Args:
            warehouse_id: 仓库ID
            
        Returns:
            成品库存列表
        """
        try:
            tenant_context = TenantContext()
            
            # 查询该仓库的所有成品库存
            inventories = db.session.query(Inventory).filter(
                and_(
                    Inventory.warehouse_id == uuid.UUID(warehouse_id),
                    Inventory.product_id.isnot(None),  # 只查询成品库存
                    Inventory.current_quantity > 0  # 只查询有库存的
                )
            ).all()
            
            inventory_data = []
            for inventory in inventories:
                # 获取产品信息
                product = db.session.query(Product).filter(Product.id == inventory.product_id).first()
                
                inventory_dict = inventory.to_dict()
                if product:
                    inventory_dict.update({
                        'product_code': product.product_code,
                        'product_name': product.product_name,
                        'product_spec': product.specification or '',
                        'base_unit': product.base_unit,
                        'customer_name': getattr(product, 'customer_name', ''),
                        'bag_type_name': getattr(product, 'bag_type_name', ''),
                        'net_weight': float(getattr(product, 'net_weight', 0)) if getattr(product, 'net_weight', None) else None,
                        'gross_weight': float(getattr(product, 'gross_weight', 0)) if getattr(product, 'gross_weight', None) else None
                    })
                
                inventory_data.append(inventory_dict)
            
            return inventory_data
            
        except Exception as e:
            raise Exception(f"获取仓库成品库存失败: {str(e)}")
    
    @staticmethod
    def delete_count_plan(plan_id: str, deleted_by: str) -> bool:
        """
        删除盘点计划
        
        Args:
            plan_id: 盘点计划ID
            deleted_by: 删除人ID
            
        Returns:
            是否删除成功
        """
        try:
            tenant_context = TenantContext()
            
            plan = db.session.query(ProductCountPlan).filter(ProductCountPlan.id == uuid.UUID(plan_id)).first()
            
            if not plan:
                raise ValueError("盘点计划不存在")
            
            if plan.status not in ['draft', 'in_progress']:
                raise ValueError("只有草稿或进行中的盘点计划才能删除")
            
            # 删除相关的盘点记录会通过级联删除自动处理
            db.session.delete(plan)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"删除盘点计划失败: {str(e)}")
    
    @staticmethod
    def get_count_statistics(plan_id: str) -> Dict[str, Any]:
        """
        获取盘点统计信息
        
        Args:
            plan_id: 盘点计划ID
            
        Returns:
            盘点统计信息
        """
        try:
            tenant_context = TenantContext()
            
            # 基础统计
            total_records = db.session.query(ProductCountRecord).filter(
                ProductCountRecord.count_plan_id == uuid.UUID(plan_id)
            ).count()
            
            counted_records = db.session.query(ProductCountRecord).filter(
                and_(
                    ProductCountRecord.count_plan_id == uuid.UUID(plan_id),
                    ProductCountRecord.actual_quantity.isnot(None)
                )
            ).count()
            
            variance_records = db.session.query(ProductCountRecord).filter(
                and_(
                    ProductCountRecord.count_plan_id == uuid.UUID(plan_id),
                    ProductCountRecord.variance_quantity != 0,
                    ProductCountRecord.variance_quantity.isnot(None)
                )
            ).count()
            
            adjusted_records = db.session.query(ProductCountRecord).filter(
                and_(
                    ProductCountRecord.count_plan_id == uuid.UUID(plan_id),
                    ProductCountRecord.is_adjusted == True
                )
            ).count()
            
            # 差异统计
            variance_stats = db.session.query(
                func.sum(ProductCountRecord.variance_quantity).label('total_variance'),
                func.sum(func.abs(ProductCountRecord.variance_quantity)).label('abs_variance')
            ).filter(
                and_(
                    ProductCountRecord.count_plan_id == uuid.UUID(plan_id),
                    ProductCountRecord.variance_quantity.isnot(None)
                )
            ).first()
            
            return {
                'total_records': total_records,
                'counted_records': counted_records,
                'pending_records': total_records - counted_records,
                'variance_records': variance_records,
                'adjusted_records': adjusted_records,
                'count_progress': round((counted_records / total_records * 100) if total_records > 0 else 0, 2),
                'total_variance': float(variance_stats.total_variance) if variance_stats.total_variance else 0,
                'abs_variance': float(variance_stats.abs_variance) if variance_stats.abs_variance else 0
            }
            
        except Exception as e:
            raise Exception(f"获取盘点统计信息失败: {str(e)}") 