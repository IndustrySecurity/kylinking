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
            
            # 填充仓库名称
            for count in counts:
                if count.warehouse_id and str(count.warehouse_id) in warehouse_dict:
                    count.warehouse_name = warehouse_dict[str(count.warehouse_id)]
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
        page_size: int = 20
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
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(MaterialCountPlan.count_date >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
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
            # 生成盘点单号
            count_number = f"MC{datetime.now().strftime('%Y%m%d')}{datetime.now().microsecond:06d}"
            
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
                'warehouse_name': data.get('warehouse_name', ''),
                'count_number': count_number,
                'count_date': datetime.strptime(data['count_date'], '%Y-%m-%d') if data.get('count_date') else datetime.now(),
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
                        'unit': detail_data.get('unit', '个'),
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
            
            self.session.commit()
            
            # 填充仓库信息
            self._fill_warehouse_info([count])
            
            return count.to_dict()
            
        except Exception as e:
            self.session.rollback()
            current_app.logger.error(f"创建材料盘点失败: {str(e)}")
            raise ValueError(f"创建材料盘点失败: {str(e)}")

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
                count.count_date = datetime.strptime(data['count_date'], '%Y-%m-%d')
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
                            'unit': detail.unit,
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


def get_material_count_service(tenant_id: str = None, schema_name: str = None) -> MaterialCountService:
    """获取材料盘点服务实例"""
    return MaterialCountService(tenant_id=tenant_id, schema_name=schema_name) 