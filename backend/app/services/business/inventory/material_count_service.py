# -*- coding: utf-8 -*-
# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
材料盘点服务
"""

from typing import Dict, List, Optional, Any
from sqlalchemy import func, and_, or_, desc, text
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID
from app.models.business.inventory import MaterialCountPlan, MaterialCountRecord, Inventory, InventoryTransaction
from app.services.base_service import TenantAwareService
from flask import g, current_app
import logging
import uuid

logger = logging.getLogger(__name__)


class MaterialCountService(TenantAwareService):
    """
    材料盘点管理服务类
    提供材料盘点相关的业务逻辑操作
    """
    
    def _parse_date(self, date_str):
        """解析日期字符串，支持多种格式"""
        if not date_str:
            return datetime.now()
        
        if isinstance(date_str, datetime):
            return date_str
        
        # 尝试解析ISO格式 (2025-07-13T10:55:19.958Z)
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # 尝试解析日期格式 (2025-07-13)
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            pass
        
        # 尝试解析带时间的格式 (2025-07-13 10:55:19)
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass
        
        # 如果都失败，返回当前时间
        current_app.logger.warning(f"无法解析日期格式: {date_str}，使用当前时间")
        return datetime.now()

    def _fill_warehouse_info(self, counts):
        """批量填充盘点的仓库名称信息"""
        if not counts:
            return
        
        # 获取所有唯一的仓库ID
        warehouse_ids = list(set([count.warehouse_id for count in counts if count.warehouse_id]))
        
        if not warehouse_ids:
            return
        
        try:
            # 查询仓库信息
            from app.models.basic_data import Warehouse
            warehouses = self.session.query(Warehouse).filter(Warehouse.id.in_(warehouse_ids)).all()
            warehouse_dict = {str(w.id): w.warehouse_name for w in warehouses}
            warehouse_code_dict = {str(w.id): w.code for w in warehouses}
            
            # 填充仓库名称
            for count in counts:
                if count.warehouse_id and str(count.warehouse_id) in warehouse_dict:
                    count.warehouse_name = warehouse_dict[str(count.warehouse_id)]
                    count.warehouse_code = warehouse_code_dict[str(count.warehouse_id)]
                elif not count.warehouse_name:
                    count.warehouse_name = '未知仓库'
        except Exception as e:
            current_app.logger.warning(f"填充仓库信息失败: {e}")
            # 失败时使用默认值
            for count in counts:
                if not count.warehouse_name:
                    count.warehouse_name = '未知仓库'

    def get_material_count_list(
        self,
        warehouse_id: str = None,
        status: str = None,
        start_date: str = None,
        end_date: str = None,
        search: str = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取材料盘点列表"""
        from sqlalchemy.orm import joinedload
        query = self.session.query(MaterialCountPlan).options(
            joinedload(MaterialCountPlan.count_person),
            joinedload(MaterialCountPlan.department)
        )
        
        if warehouse_id:
            query = query.filter(MaterialCountPlan.warehouse_id == warehouse_id)
        
        if status:
            query = query.filter(MaterialCountPlan.status == status)
        
        if start_date:
            try:
                start_dt = self._parse_date(start_date)
                query = query.filter(MaterialCountPlan.count_date >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = self._parse_date(end_date)
                query = query.filter(MaterialCountPlan.count_date <= end_dt)
            except ValueError:
                pass
        
        if search:
            search_filter = or_(
                MaterialCountPlan.count_number.ilike(f'%{search}%'),
                MaterialCountPlan.warehouse_name.ilike(f'%{search}%'),
                MaterialCountPlan.notes.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        counts = query.order_by(MaterialCountPlan.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 填充仓库信息
        self._fill_warehouse_info(counts)
        
        return {
            'items': [count.to_dict() for count in counts],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }

    def get_material_count_by_id(self, count_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取材料盘点详情"""
        from sqlalchemy.orm import joinedload
        count = self.session.query(MaterialCountPlan).options(
            joinedload(MaterialCountPlan.count_person),
            joinedload(MaterialCountPlan.department)
        ).filter(MaterialCountPlan.id == count_id).first()
        
        if not count:
            return None
        
        # 填充仓库信息
        self._fill_warehouse_info([count])
        
        return count.to_dict()

    def create_material_count(self, data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """创建材料盘点（支持同时创建明细）"""
        try:
            # 生成盘点单号 - 使用顺序生成
            from app.models.business.inventory import MaterialCountPlan
            count_number = MaterialCountPlan.generate_count_number()
            
            # 转换created_by为UUID
            try:
                created_by_uuid = uuid.UUID(created_by)
            except (TypeError):
                created_by_uuid = created_by
            
            # 提取明细数据
            details_data = data.pop('details', [])
            
            # 准备盘点数据
            count_data = {
                'warehouse_id': uuid.UUID(data['warehouse_id']),
                'warehouse_code': data.get('warehouse_code', ''),
                'warehouse_name': data.get('warehouse_name', ''),
                'count_number': count_number,
                'count_date': self._parse_date(data.get('count_date')) if data.get('count_date') else datetime.now(),
                'status': 'draft',
                'count_person_id': uuid.UUID(data['count_person_id']) if data.get('count_person_id') else None,
                'department_id': uuid.UUID(data['department_id']) if data.get('department_id') else None,
                'notes': data.get('notes', ''),
                'created_by': created_by_uuid
            }
            
            # 使用继承的create_with_tenant方法
            count = self.create_with_tenant(MaterialCountPlan, **count_data)
            self.session.flush()  # 获取count.id
            
            # 创建明细
            if details_data:
                for detail_data in details_data:
                    detail_params = {
                        'count_plan_id': count.id,
                        'book_quantity': Decimal(str(detail_data.get('book_quantity', 0))),
                        'actual_quantity': Decimal(str(detail_data.get('actual_quantity', 0))),
                        'unit': detail_data.get('unit'),
                        'created_by': created_by_uuid
                    }
                    
                    # 计算差异数量
                    detail_params['variance_quantity'] = detail_params['actual_quantity'] - detail_params['book_quantity']
                    
                    # 设置其他明细字段
                    if detail_data.get('material_id'):
                        detail_params['material_id'] = uuid.UUID(detail_data['material_id'])
                    if detail_data.get('material_name'):
                        detail_params['material_name'] = detail_data['material_name']
                    if detail_data.get('material_code'):
                        detail_params['material_code'] = detail_data['material_code']
                    if detail_data.get('batch_number'):
                        detail_params['batch_number'] = detail_data['batch_number']
                    if detail_data.get('location_code'):
                        detail_params['location_code'] = detail_data['location_code']
                    
                    # 创建明细记录
                    self.create_with_tenant(MaterialCountRecord, **detail_params)
            else:
                # 如果没有提供明细数据，自动从库存生成盘点记录
                self._generate_count_records_from_inventory(count.id, count.warehouse_id, created_by_uuid)
            
            self.session.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([count])
            
            return count.to_dict()
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"创建材料盘点失败: {str(e)}")
            raise ValueError(f"创建材料盘点失败: {str(e)}")

    def _generate_count_records_from_inventory(self, count_plan_id: uuid.UUID, warehouse_id: uuid.UUID, created_by: uuid.UUID):
        """
        根据仓库库存自动生成盘点记录
        
        Args:
            count_plan_id: 盘点计划ID
            warehouse_id: 仓库ID
            created_by: 创建人ID
        """
        try:
            # 查询该仓库的所有材料库存
            from app.models.business.inventory import Inventory
            from app.models.basic_data import Material, Unit
            
            inventories = self.session.query(Inventory).filter(
                and_(
                    Inventory.warehouse_id == warehouse_id,
                    Inventory.material_id.isnot(None),  # 只查询材料库存
                    Inventory.current_quantity > 0,  # 只查询有库存的
                    Inventory.is_active == True
                )
            ).all()
            
            for inventory in inventories:
                # 获取材料信息
                material = self.session.query(Material).filter(Material.id == inventory.material_id).first()
                if not material:
                    continue
                
                # 获取单位信息
                unit = self.session.query(Unit).filter(Unit.id == inventory.unit_id).first()
                
                # 创建盘点记录
                record_data = {
                    'count_plan_id': count_plan_id,
                    'inventory_id': inventory.id,
                    'material_id': inventory.material_id,
                    'material_code': material.material_code,
                    'material_name': material.material_name,
                    'material_spec': material.specification_model or '',
                    'unit_id': inventory.unit_id,
                    'book_quantity': inventory.current_quantity,
                    'actual_quantity': inventory.current_quantity,  # 初始时实盘数量等于账面数量
                    'variance_quantity': 0,
                    'variance_rate': 0,
                    'batch_number': inventory.batch_number,
                    'location_code': inventory.location_code,
                    'status': 'pending',
                    'created_by': created_by
                }
                
                # 创建盘点记录
                self.create_with_tenant(MaterialCountRecord, **record_data)
                
        except Exception as e:
            current_app.logger.error(f"生成盘点记录失败: {str(e)}")
            raise ValueError(f"生成盘点记录失败: {str(e)}")

    def update_material_count(self, count_id: str, data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """更新材料盘点"""
        try:
            count = self.session.query(MaterialCountPlan).filter(MaterialCountPlan.id == count_id).first()
            
            if not count:
                raise ValueError("盘点单不存在")
            
            # 检查状态是否可以更新
            if count.status not in ['draft', 'in_progress']:
                raise ValueError("只能更新草稿或进行中的盘点单")
            
            # 转换updated_by为UUID
            try:
                updated_by_uuid = uuid.UUID(updated_by)
            except (TypeError):
                updated_by_uuid = updated_by
            
            # 提取明细数据
            details_data = data.pop('details', [])
            
            # 更新主表数据
            if data.get('warehouse_id'):
                count.warehouse_id = uuid.UUID(data['warehouse_id'])
            if data.get('warehouse_name'):
                count.warehouse_name = data['warehouse_name']
            if data.get('count_date'):
                count.count_date = self._parse_date(data['count_date'])
            if data.get('count_person_id'):
                count.count_person_id = uuid.UUID(data['count_person_id'])
            if data.get('department_id'):
                count.department_id = uuid.UUID(data['department_id'])
            if data.get('notes'):
                count.notes = data['notes']
            if data.get('status'):
                count.status = data['status']
            
            count.updated_by = updated_by_uuid
            
            # 更新明细（如果提供了明细数据）
            if details_data:
                # 删除现有明细
                self.session.query(MaterialCountRecord).filter(
                    MaterialCountRecord.count_plan_id == count.id
                ).delete()
                
                # 创建新明细
                for detail_data in details_data:
                    detail_params = {
                        'count_plan_id': count.id,
                        'book_quantity': Decimal(str(detail_data.get('book_quantity', 0))),
                        'actual_quantity': Decimal(str(detail_data.get('actual_quantity', 0))),
                        'unit': detail_data.get('unit', '个'),
                        'created_by': updated_by_uuid
                    }
                    
                    # 计算差异数量
                    detail_params['variance_quantity'] = detail_params['actual_quantity'] - detail_params['book_quantity']
                    
                    # 设置其他明细字段
                    if detail_data.get('material_id'):
                        detail_params['material_id'] = uuid.UUID(detail_data['material_id'])
                    if detail_data.get('material_name'):
                        detail_params['material_name'] = detail_data['material_name']
                    if detail_data.get('material_code'):
                        detail_params['material_code'] = detail_data['material_code']
                    if detail_data.get('batch_number'):
                        detail_params['batch_number'] = detail_data['batch_number']
                    if detail_data.get('location_code'):
                        detail_params['location_code'] = detail_data['location_code']
                    
                    # 创建明细记录
                    self.create_with_tenant(MaterialCountRecord, **detail_params)
            
            self.session.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([count])
            
            return count.to_dict()
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"更新材料盘点失败: {str(e)}")
            raise ValueError(f"更新材料盘点失败: {str(e)}")

    def delete_material_count(self, count_id: str) -> bool:
        """删除材料盘点"""
        try:
            count = self.session.query(MaterialCountPlan).filter(MaterialCountPlan.id == count_id).first()
            
            if not count:
                raise ValueError("盘点单不存在")
            
            # 检查状态是否可以删除
            if count.status not in ['draft']:
                raise ValueError("只能删除草稿状态的盘点单")
            
            # 删除明细
            self.session.query(MaterialCountRecord).filter(
                MaterialCountRecord.count_plan_id == count.id
            ).delete()
            
            # 删除主表
            self.session.delete(count)
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"删除材料盘点失败: {str(e)}")
            raise ValueError(f"删除材料盘点失败: {str(e)}")

    def approve_material_count(self, count_id: str, approval_data: Dict[str, Any], approved_by: str) -> Dict[str, Any]:
        """审核材料盘点"""
        try:
            count = self.session.query(MaterialCountPlan).filter(MaterialCountPlan.id == count_id).first()
            
            if not count:
                raise ValueError("盘点单不存在")
            
            # 检查状态是否可以审核
            if count.status not in ['draft', 'in_progress']:
                raise ValueError("只能审核草稿或进行中的盘点单")
            
            # 转换approved_by为UUID
            try:
                approved_by_uuid = uuid.UUID(approved_by)
            except (TypeError):
                approved_by_uuid = approved_by
            
            # 更新审核状态
            approval_action = approval_data.get('action', 'approve')
            if approval_action == 'approve':
                count.status = 'completed'
            elif approval_action == 'reject':
                count.status = 'draft'
            
            count.updated_by = approved_by_uuid
            
            # 如果有审核意见，添加到备注中
            if approval_data.get('notes'):
                count.notes = (count.notes or '') + f"\n审核意见: {approval_data['notes']}"
            
            self.session.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([count])
            
            return count.to_dict()
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"审核材料盘点失败: {str(e)}")
            raise ValueError(f"审核材料盘点失败: {str(e)}")

    def execute_material_count(self, count_id: str, executed_by: str) -> Dict[str, Any]:
        """执行材料盘点（创建库存调整）"""
        try:
            count = self.session.query(MaterialCountPlan).filter(MaterialCountPlan.id == count_id).first()
            
            if not count:
                raise ValueError("盘点单不存在")
            
            # 检查状态是否可以执行
            if count.status != 'completed':
                raise ValueError("只能执行已完成的盘点单")
            
            # 转换executed_by为UUID
            try:
                executed_by_uuid = uuid.UUID(executed_by)
            except (TypeError):
                executed_by_uuid = executed_by
            
            # 获取盘点明细
            details = self.session.query(MaterialCountRecord).filter(
                MaterialCountRecord.count_plan_id == count.id
            ).all()
            
            # 处理每个明细的库存调整
            for detail in details:
                if detail.variance_quantity and detail.variance_quantity != 0:
                    # 查找对应的库存记录
                    inventory = self.session.query(Inventory).filter(
                        Inventory.warehouse_id == count.warehouse_id,
                        Inventory.material_id == detail.material_id,
                        Inventory.batch_number == detail.batch_number
                    ).first()
                    
                    if inventory:
                        # 更新库存数量
                        old_quantity = inventory.current_quantity
                        new_quantity = old_quantity + detail.variance_quantity
                        
                        inventory.current_quantity = new_quantity
                        inventory.available_quantity = new_quantity
                        inventory.last_count_date = datetime.now()
                        inventory.last_count_quantity = detail.actual_quantity
                        inventory.variance_quantity = detail.variance_quantity
                        inventory.updated_by = executed_by_uuid
                        
                        # 创建库存流水记录
                        transaction_data = {
                            'inventory_id': inventory.id,
                            'warehouse_id': count.warehouse_id,
                            'material_id': detail.material_id,
                            'transaction_type': 'adjustment_in' if detail.variance_quantity > 0 else 'adjustment_out',
                            'quantity_change': detail.variance_quantity,
                            'quantity_before': old_quantity,
                            'quantity_after': new_quantity,
                            'unit_id': detail.unit_id,
                            'source_document_type': 'count_order',
                            'source_document_id': count.id,
                            'source_document_number': count.count_number,
                            'reason': f'盘点调整 - {count.count_number}',
                            'created_by': executed_by_uuid
                        }
                        
                        self.create_with_tenant(InventoryTransaction, **transaction_data)
                        
                        # 更新明细状态
                        detail.is_adjusted = True
                        detail.status = 'adjusted'
                        detail.updated_by = executed_by_uuid
            
            # 更新盘点单状态
            count.status = 'adjusted'
            count.updated_by = executed_by_uuid
            
            self.session.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([count])
            
            return count.to_dict()
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"执行材料盘点失败: {str(e)}")
            raise ValueError(f"执行材料盘点失败: {str(e)}")

    def cancel_material_count(self, count_id: str, cancel_data: Dict[str, Any], cancelled_by: str) -> Dict[str, Any]:
        """取消材料盘点"""
        try:
            count = self.session.query(MaterialCountPlan).filter(MaterialCountPlan.id == count_id).first()
            
            if not count:
                raise ValueError("盘点单不存在")
            
            # 检查状态是否可以取消
            if count.status in ['adjusted']:
                raise ValueError("已调整的盘点单不能取消")
            
            # 转换cancelled_by为UUID
            try:
                cancelled_by_uuid = uuid.UUID(cancelled_by)
            except (TypeError):
                cancelled_by_uuid = cancelled_by
            
            # 更新状态
            count.status = 'draft'
            count.updated_by = cancelled_by_uuid
            
            # 如果有取消原因，添加到备注中
            if cancel_data.get('reason'):
                count.notes = (count.notes or '') + f"\n取消原因: {cancel_data['reason']}"
            
            self.session.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([count])
            
            return count.to_dict()
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"取消材料盘点失败: {str(e)}")
            raise ValueError(f"取消材料盘点失败: {str(e)}")

    def start_material_count(self, count_id: str, started_by: str) -> Dict[str, Any]:
        """开始材料盘点"""
        try:
            count = self.session.query(MaterialCountPlan).filter(MaterialCountPlan.id == count_id).first()
            
            if not count:
                raise ValueError("材料盘点不存在")
            
            if count.status != 'draft':
                raise ValueError("只能开始草稿状态的盘点")
            
            # 转换started_by为UUID
            try:
                started_by_uuid = uuid.UUID(started_by)
            except (TypeError):
                started_by_uuid = started_by
            
            # 更新状态
            count.status = 'in_progress'
            count.updated_by = started_by_uuid
            
            self.session.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([count])
            
            return count.to_dict()
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"开始材料盘点失败: {str(e)}")
            raise ValueError(f"开始材料盘点失败: {str(e)}")

    def complete_material_count(self, count_id: str, completed_by: str) -> Dict[str, Any]:
        """完成材料盘点"""
        try:
            count = self.session.query(MaterialCountPlan).filter(MaterialCountPlan.id == count_id).first()
            
            if not count:
                raise ValueError("材料盘点不存在")
            
            if count.status != 'in_progress':
                raise ValueError("只能完成进行中的盘点")
            
            # 转换completed_by为UUID
            try:
                completed_by_uuid = uuid.UUID(completed_by)
            except (TypeError):
                completed_by_uuid = completed_by
            
            # 更新状态
            count.status = 'completed'
            count.updated_by = completed_by_uuid
            
            self.session.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([count])
            
            return count.to_dict()
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"完成材料盘点失败: {str(e)}")
            raise ValueError(f"完成材料盘点失败: {str(e)}")

    def adjust_material_count_inventory(self, plan_id: str, adjusted_by: str) -> Dict[str, Any]:
        """调整材料盘点库存"""
        try:
            count = self.session.query(MaterialCountPlan).filter(MaterialCountPlan.id == plan_id).first()
            
            if not count:
                raise ValueError("材料盘点不存在")
            
            if count.status != 'completed':
                raise ValueError("只能调整已完成的材料盘点")
            
            # 转换adjusted_by为UUID
            try:
                adjusted_by_uuid = uuid.UUID(adjusted_by)
            except (TypeError):
                adjusted_by_uuid = adjusted_by
            
            # 获取盘点记录
            records = self.session.query(MaterialCountRecord).filter(MaterialCountRecord.count_plan_id == plan_id).all()
            
            transactions = []
            adjusted_records = []
            
            for record in records:
                if record.variance_quantity != 0 and record.material_id:
                    # 查找库存记录
                    inventory = self.session.query(Inventory).filter(
                        and_(
                            Inventory.warehouse_id == count.warehouse_id,
                            Inventory.material_id == record.material_id,
                            Inventory.batch_number == record.batch_number,
                            Inventory.is_active == True
                        )
                    ).first()
                    
                    if inventory:
                        # 记录变动前数量
                        quantity_before = inventory.current_quantity
                        
                        # 调整库存
                        inventory.current_quantity += record.variance_quantity
                        inventory.available_quantity += record.variance_quantity
                        
                        # 确保库存不为负数
                        if inventory.current_quantity < 0:
                            inventory.current_quantity = 0
                        if inventory.available_quantity < 0:
                            inventory.available_quantity = 0
                        
                        inventory.updated_by = adjusted_by_uuid
                        
                        # 创建库存流水记录
                        transaction_data = {
                            'inventory_id': inventory.id,
                            'warehouse_id': count.warehouse_id,
                            'material_id': record.material_id,
                            'transaction_type': 'adjustment',
                            'quantity_change': record.variance_quantity,
                            'quantity_before': quantity_before,
                            'quantity_after': inventory.current_quantity,
                            'unit_id': record.unit_id,
                            'source_document_type': 'material_count_plan',
                            'source_document_id': count.id,
                            'source_document_number': count.count_number,
                            'batch_number': record.batch_number,
                            'reason': f'材料盘点调整 - {count.count_number}',
                            'created_by': adjusted_by_uuid
                        }
                        
                        transaction = self.create_with_tenant(InventoryTransaction, **transaction_data)
                        transactions.append(transaction)
                        
                        # 标记盘点记录为已调整
                        record.is_adjusted = True
                        record.status = 'adjusted'
                        record.updated_by = adjusted_by_uuid
            
            # 更新盘点状态
            count.status = 'adjusted'
            count.updated_by = adjusted_by_uuid
            
            self.session.commit()
            
            return {
                'count': count.to_dict(),
                'transactions': [t.to_dict() for t in transactions],
                'transaction_count': len(transactions)
            }
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"调整材料盘点库存失败: {str(e)}")
            raise ValueError(f"调整材料盘点库存失败: {str(e)}")

    def get_material_count_records(self, count_id: str) -> List[Dict[str, Any]]:
        """获取材料盘点记录"""
        from sqlalchemy.orm import joinedload
        
        records = self.session.query(MaterialCountRecord).options(
            joinedload(MaterialCountRecord.unit)
        ).filter(
            MaterialCountRecord.count_plan_id == count_id
        ).all()
        
        return [record.to_dict() for record in records]

    def update_material_count_record(self, record_id: str, updated_by: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新材料盘点记录"""
        try:
            record = self.session.query(MaterialCountRecord).filter(MaterialCountRecord.id == record_id).first()
            
            if not record:
                raise ValueError("盘点记录不存在")
            
            # 转换updated_by为UUID
            try:
                updated_by_uuid = uuid.UUID(updated_by)
            except (TypeError):
                updated_by_uuid = updated_by
            
            # 更新实盘数量
            if 'actual_quantity' in data:
                record.actual_quantity = Decimal(str(data['actual_quantity']))
                # 重新计算差异数量
                record.variance_quantity = record.actual_quantity - record.book_quantity
            
            # 更新其他字段
            if 'notes' in data:
                record.notes = data['notes']
            
            record.updated_by = updated_by_uuid
            
            self.session.commit()
            
            return record.to_dict()
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"更新材料盘点记录失败: {str(e)}")
            raise ValueError(f"更新材料盘点记录失败: {str(e)}")


def get_material_count_service(tenant_id: str = None, schema_name: str = None) -> MaterialCountService:
    """获取材料盘点服务实例"""
    return MaterialCountService(tenant_id=tenant_id, schema_name=schema_name) 