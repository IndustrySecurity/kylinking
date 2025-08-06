# -*- coding: utf-8 -*-
"""
送货通知单服务
"""
import uuid
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import desc
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import Dict, Any, Optional
from flask import current_app
from decimal import Decimal

from app.services.base_service import TenantAwareService
from app.models.business.sales import DeliveryNotice, DeliveryNoticeDetail, SalesOrder, SalesOrderDetail
from app.models.basic_data import CustomerManagement


class DeliveryNoticeService(TenantAwareService):
    """送货通知单服务类 - 支持多租户"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """
        初始化送货通知单服务
        
        Args:
            tenant_id: 租户ID
            schema_name: Schema名称
        """
        super().__init__(tenant_id, schema_name)

    def _is_uuid(self, value: str) -> bool:
        """检查字符串是否为有效的UUID格式"""
        try:
            uuid.UUID(str(value))
            return True
        except (ValueError, TypeError):
            return False

    def _generate_notice_number(self) -> str:
        """生成送货通知单号 (DN前缀)"""
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        
        # 查询当天最大通知单号
        session = self.get_session()
        max_notice = session.query(DeliveryNotice).filter(
            DeliveryNotice.notice_number.like(f'DN{date_str}%')
        ).order_by(desc(DeliveryNotice.notice_number)).first()
        
        if max_notice:
            last_seq = int(max_notice.notice_number[-4:])
            new_seq = last_seq + 1
        else:
            new_seq = 1
            
        return f'DN{date_str}{new_seq:04d}'

    def create_delivery_notice(self, notice_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        创建送货通知单
        
        Args:
            notice_data: 送货通知单数据
            user_id: 用户ID
            
        Returns:
            创建的送货通知单数据
        """
        try:
            self.log_operation('create_delivery_notice', {'data_keys': list(notice_data.keys())})
            
            # 创建主通知单对象
            notice = self.create_with_tenant(
                DeliveryNotice,
                notice_number=self._generate_notice_number(),
                customer_id=notice_data.get('customer_id'),
                sales_order_id=notice_data.get('sales_order_id'),
                delivery_address=notice_data.get('delivery_address'),
                delivery_date=notice_data.get('delivery_date'),
                delivery_method=notice_data.get('delivery_method'),
                logistics_info=notice_data.get('logistics_info'),
                remark=notice_data.get('remark'),
                status=notice_data.get('status', 'draft'),
                created_by=user_id
            )

            # 立即 flush，确保 notice.id 可用
            self.get_session().flush()

            # 处理明细：如果前端直接传入，则以传入为准；否则尝试根据销售订单自动生成
            details_from_frontend = notice_data.get('details') or []

            if not details_from_frontend and notice.sales_order_id:
                # 自动根据销售订单导入明细
                details_from_frontend = self._generate_details_from_sales_order(notice.sales_order_id)

            for detail_data in details_from_frontend:
                detail_data['created_by'] = user_id
                detail_data['delivery_notice_id'] = notice.id
                detail_data['already_outbound_quantity'] = 0
                detail_data['pending_outbound_quantity'] = detail_data.get('notice_quantity') or 0
                valid_fields = {c.name for c in DeliveryNoticeDetail.__table__.columns}
                clean_data = {k: v for k, v in detail_data.items() if k in valid_fields}
                clean_data['delivery_notice_id'] = notice.id
                self.create_with_tenant(DeliveryNoticeDetail, **clean_data)

                # 如果送货通知关联了销售订单，更新销售订单明细的已安排送货数
                if notice.sales_order_id and detail_data.get('product_id'):
                    sod = self.get_session().query(SalesOrderDetail).filter(
                        SalesOrderDetail.sales_order_id == notice.sales_order_id,
                        SalesOrderDetail.product_id == detail_data['product_id']
                    ).first()
                    if sod is not None and hasattr(sod, 'scheduled_delivery_quantity'):
                        from decimal import Decimal
                        qty_raw = detail_data.get('notice_quantity') or 0
                        try:
                            qty_decimal = Decimal(str(qty_raw))
                        except Exception:
                            qty_decimal = Decimal(0)

                        current_qty = sod.scheduled_delivery_quantity or Decimal(0)
                        try:
                            current_qty = Decimal(str(current_qty))
                        except Exception:
                            current_qty = Decimal(0)

                        sod.scheduled_delivery_quantity = current_qty + qty_decimal
            
            # 更新销售订单状态
            if notice.sales_order_id:
                sales_order = self.get_session().query(SalesOrder).get(notice.sales_order_id)
                if sales_order:
                    sales_order.status = 'partial_shipped'
            
            # 检查是否需要关闭销售订单
            if notice.sales_order_id:
                self._check_and_close_sales_order(notice.sales_order_id, user_id)
            
            self.commit()
            
            # 重新查询以获取完整数据
            return self.get_delivery_notice_by_id(str(notice.id))
            
        except SQLAlchemyError as e:
            self.rollback()
            raise e

    def get_delivery_notices(self, page: int, per_page: int, search_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        获取送货通知单列表（分页）
        
        Args:
            page: 页码
            per_page: 每页数量
            search_params: 搜索参数
            
        Returns:
            分页的送货通知单列表
        """
        session = self.get_session()
        query = session.query(DeliveryNotice).options(joinedload(DeliveryNotice.customer), joinedload(DeliveryNotice.sales_order))
        
        # 确保租户隔离
        query = self.ensure_tenant_isolation(query)

        if search_params:
            if 'notice_number' in search_params and search_params['notice_number']:
                query = query.filter(DeliveryNotice.notice_number.ilike(f"%{search_params['notice_number']}%"))
            if 'customer_id' in search_params and search_params['customer_id']:
                query = query.filter(DeliveryNotice.customer_id == search_params['customer_id'])
            if 'status' in search_params and search_params['status']:
                query = query.filter(DeliveryNotice.status == search_params['status'])
        
        pagination = query.order_by(DeliveryNotice.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'items': [self._notice_to_dict(item) for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }

    def get_delivery_notice_by_id(self, notice_id: str) -> Optional[Dict[str, Any]]:
        """
        通过ID获取单个送货通知单
        
        Args:
            notice_id: 送货通知单ID
            
        Returns:
            送货通知单数据或None
        """
        session = self.get_session()
        notice = session.query(DeliveryNotice).options(
            joinedload(DeliveryNotice.details).joinedload(DeliveryNoticeDetail.product),
            joinedload(DeliveryNotice.customer),
            joinedload(DeliveryNotice.sales_order)
        ).get(notice_id)
        
        if notice and self.validate_tenant_access(getattr(notice, 'tenant_id', self.tenant_id)):
            return self._notice_to_dict(notice)
        
        return None

    def update_delivery_notice(self, notice_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        更新送货通知单
        
        Args:
            notice_id: 送货通知单ID
            data: 更新数据
            user_id: 用户ID
            
        Returns:
            更新后的送货通知单数据
        """
        session = self.get_session()
        notice = session.query(DeliveryNotice).get(notice_id)
        
        if not notice:
            raise ValueError("送货通知单未找到")
        
        if not self.validate_tenant_access(getattr(notice, 'tenant_id', self.tenant_id)):
            raise ValueError("无权限访问该送货通知单")

        # 当状态已确认或之后，不允许再编辑
        if notice.status in ['confirmed', 'shipped', 'completed', 'cancelled']:
            raise ValueError("送货通知单已进入不可编辑状态，无法修改")

        self.log_operation('update_delivery_notice', {
            'notice_id': notice_id, 
            'data_keys': list(data.keys())
        })

        # 更新主表字段
        for key, value in data.items():
            if hasattr(notice, key) and key not in ['id', 'details', 'tenant_id']:
                # 特殊处理 sales_order_id 字段
                if key == 'sales_order_id' and value:
                    # 如果传入的是订单号而不是UUID，需要查找对应的UUID
                    if not self._is_uuid(value):
                        # 通过订单号查找销售订单的UUID
                        sales_order = session.query(SalesOrder).filter(
                            SalesOrder.order_number == value
                        ).first()
                        if sales_order:
                            setattr(notice, key, sales_order.id)
                        else:
                            # 如果找不到对应的销售订单，跳过这个字段
                            continue
                    else:
                        setattr(notice, key, value)
                else:
                    setattr(notice, key, value)
        
        notice.updated_by = user_id

        # 更新或创建或删除明细
        if 'details' in data:
            incoming_detail_ids = {str(d.get('id')) for d in data['details'] if d.get('id')}

            # 删除不在新数据中的明细
            for detail in notice.details[:]:
                if str(detail.id) not in incoming_detail_ids:
                    # 如果送货通知关联了销售订单，需要减少销售订单明细的已安排送货数
                    if notice.sales_order_id and detail.product_id:
                        sod = session.query(SalesOrderDetail).filter(
                            SalesOrderDetail.sales_order_id == notice.sales_order_id,
                            SalesOrderDetail.product_id == detail.product_id
                        ).first()
                        if sod is not None and hasattr(sod, 'scheduled_delivery_quantity'):
                            from decimal import Decimal
                            current_qty = sod.scheduled_delivery_quantity or Decimal(0)
                            detail_qty = detail.notice_quantity or Decimal(0)
                            sod.scheduled_delivery_quantity = current_qty - detail_qty
                    
                    session.delete(detail)
            
            # 新增或更新明细
            for detail_data in data['details']:
                detail_id = detail_data.get('id')
                if detail_id:  # 更新现有明细
                    detail = session.query(DeliveryNoticeDetail).get(detail_id)
                    if detail and self.validate_tenant_access(getattr(detail, 'tenant_id', self.tenant_id)):
                        # 记录原始数量，用于计算差值
                        old_notice_quantity = detail.notice_quantity or 0
                        
                        for k, v in detail_data.items():
                            if hasattr(detail, k) and k not in ['id', 'tenant_id']:
                                # 过滤掉字典类型的字段
                                if isinstance(v, dict):
                                    continue
                                setattr(detail, k, v)
                        detail.updated_by = user_id
                        
                        # 如果送货通知关联了销售订单，更新销售订单明细的已安排送货数
                        if notice.sales_order_id and detail.product_id:
                            sod = session.query(SalesOrderDetail).filter(
                                SalesOrderDetail.sales_order_id == notice.sales_order_id,
                                SalesOrderDetail.product_id == detail.product_id
                            ).first()
                            if sod is not None and hasattr(sod, 'scheduled_delivery_quantity'):
                                from decimal import Decimal
                                current_qty = sod.scheduled_delivery_quantity or Decimal(0)
                                new_qty = detail.notice_quantity or Decimal(0)
                                old_qty = Decimal(str(old_notice_quantity))
                                # 计算差值：新数量 - 旧数量
                                qty_diff = new_qty - old_qty
                                sod.scheduled_delivery_quantity = current_qty + qty_diff
                else:  # 新增明细
                    if 'id' in detail_data:
                        del detail_data['id']
                    
                    # 过滤掉字典类型的字段
                    clean_detail_data = {}
                    for k, v in detail_data.items():
                        if not isinstance(v, dict):
                            clean_detail_data[k] = v
                    
                    clean_detail_data['created_by'] = user_id
                    clean_detail_data['delivery_notice_id'] = notice.id
                    valid_fields = {c.name for c in DeliveryNoticeDetail.__table__.columns}
                    clean_data = {k: v for k, v in clean_detail_data.items() if k in valid_fields}
                    clean_data['delivery_notice_id'] = notice.id
                    self.create_with_tenant(DeliveryNoticeDetail, **clean_data)

                    # 如果送货通知关联了销售订单，更新销售订单明细的已安排送货数
                    if notice.sales_order_id and detail_data.get('product_id'):
                        sod = session.query(SalesOrderDetail).filter(
                            SalesOrderDetail.sales_order_id == notice.sales_order_id,
                            SalesOrderDetail.product_id == detail_data['product_id']
                        ).first()
                        if sod is not None and hasattr(sod, 'scheduled_delivery_quantity'):
                            from decimal import Decimal
                            qty_raw = detail_data.get('notice_quantity') or 0
                            try:
                                qty_decimal = Decimal(str(qty_raw))
                            except Exception:
                                qty_decimal = Decimal(0)

                            current_qty = sod.scheduled_delivery_quantity or Decimal(0)
                            try:
                                current_qty = Decimal(str(current_qty))
                            except Exception:
                                current_qty = Decimal(0)

                            sod.scheduled_delivery_quantity = current_qty + qty_decimal

        self.commit()
        return self.get_delivery_notice_by_id(notice_id)

    def delete_delivery_notice(self, notice_id: str, user_id: str) -> bool:
        """
        删除送货通知单
        
        Args:
            notice_id: 送货通知单ID
            user_id: 用户ID
            
        Returns:
            bool: 是否删除成功
        """
        session = self.get_session()
        notice = session.query(DeliveryNotice).get(notice_id)
        
        if not notice:
            raise ValueError("送货通知单未找到")
        
        if not self.validate_tenant_access(getattr(notice, 'tenant_id', self.tenant_id)):
            raise ValueError("无权限删除该送货通知单")
        
        # 在删除前，恢复销售订单明细的已安排数量
        if notice.sales_order_id:
            for detail in notice.details:
                if detail.product_id:
                    sod = session.query(SalesOrderDetail).filter(
                        SalesOrderDetail.sales_order_id == notice.sales_order_id,
                        SalesOrderDetail.product_id == detail.product_id
                    ).first()
                    if sod is not None and hasattr(sod, 'scheduled_delivery_quantity'):
                        from decimal import Decimal
                        current_qty = sod.scheduled_delivery_quantity or Decimal(0)
                        detail_qty = detail.notice_quantity or Decimal(0)
                        sod.scheduled_delivery_quantity = current_qty - detail_qty
            
            # 更新销售订单状态
            self._update_sales_order_status_after_delete(notice.sales_order_id, user_id)
        
        self.log_operation('delete_delivery_notice', {'notice_id': notice_id})
        
        session.delete(notice)
        self.commit()
        return True

    def update_notice_status(self, notice_id: str, new_status: str, user_id: str) -> Dict[str, Any]:
        """
        更新送货通知单状态
        
        Args:
            notice_id: 送货通知单ID
            new_status: 新状态
            user_id: 用户ID
            
        Returns:
            更新后的送货通知单数据
        """
        valid_statuses = ['draft', 'confirmed', 'shipped', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"无效的状态值: {new_status}")
        
        session = self.get_session()
        notice = session.query(DeliveryNotice).get(notice_id)
        
        if not notice:
            raise ValueError("送货通知单未找到")
        
        if not self.validate_tenant_access(getattr(notice, 'tenant_id', self.tenant_id)):
            raise ValueError("无权限访问该送货通知单")
        
        self.log_operation('update_notice_status', {
            'notice_id': notice_id,
            'old_status': notice.status,
            'new_status': new_status
        })
        
        notice.status = new_status
        notice.updated_by = user_id
        
        self.commit()
        return self.get_delivery_notice_by_id(notice_id) 

    def get_delivery_notice_list(self, page: int, per_page: int, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        获取送货通知单列表（别名方法，兼容前端调用）
        
        Args:
            page: 页码
            per_page: 每页数量
            filters: 搜索参数
            
        Returns:
            分页的送货通知单列表
        """
        return self.get_delivery_notices(page, per_page, filters)

    def get_delivery_notice_detail(self, notice_id: str) -> Optional[Dict[str, Any]]:
        """
        获取送货通知单详情（别名方法，兼容前端调用）
        
        Args:
            notice_id: 送货通知单ID
            
        Returns:
            送货通知单数据或None
        """
        return self.get_delivery_notice_by_id(notice_id)

    def confirm_delivery_notice(self, notice_id: str, user_id: str) -> Dict[str, Any]:
        """
        确认送货通知单
        
        Args:
            notice_id: 送货通知单ID
            user_id: 用户ID
            
        Returns:
            更新后的送货通知单数据
        """
        return self.update_notice_status(notice_id, 'confirmed', user_id)

    def ship_delivery_notice(self, notice_id: str, user_id: str) -> Dict[str, Any]:
        """
        发货送货通知单
        
        Args:
            notice_id: 送货通知单ID
            user_id: 用户ID
            
        Returns:
            更新后的送货通知单数据
        """
        return self.update_notice_status(notice_id, 'shipped', user_id)

    def complete_delivery_notice(self, notice_id: str, user_id: str) -> Dict[str, Any]:
        """
        完成送货通知单
        
        Args:
            notice_id: 送货通知单ID
            user_id: 用户ID
            
        Returns:
            更新后的送货通知单数据
        """
        return self.update_notice_status(notice_id, 'completed', user_id)

    # ---------------------------------------------------------------------
    # 辅助方法
    # ---------------------------------------------------------------------

    def _generate_details_from_sales_order(self, sales_order_id: str):
        """根据销售订单明细生成送货通知明细列表"""
        session = self.get_session()
        order: SalesOrder = session.query(SalesOrder).options(
            joinedload(SalesOrder.order_details)
        ).get(sales_order_id)

        if not order:
            return []

        details = []
        for od in order.order_details:
            # 计算剩余未安排数量
            remaining_qty = (od.order_quantity or 0) - (od.scheduled_delivery_quantity or 0)
            if remaining_qty <= 0:
                continue  # 已全部安排跳过

            details.append({
                'work_order_number': None,
                'product_id': od.product_id,
                'product_name': od.product_name,
                'product_code': od.product_code,
                'specification': od.product_specification,
                'order_quantity': od.order_quantity,
                'remaining_quantity': remaining_qty,  # 添加未安排数量
                'notice_quantity': remaining_qty,  # 默认剩余全部安排，可前端修改
                'already_outbound_quantity': 0,
                'pending_outbound_quantity': remaining_qty,
                'unit_id': od.unit_id,
                'sales_unit_id': od.sales_unit_id,
                'negative_deviation_percentage': od.negative_deviation_percentage,
                'positive_deviation_percentage': od.positive_deviation_percentage,
                'production_min_quantity': od.production_small_quantity,
                'production_max_quantity': od.production_large_quantity,
                'order_delivery_date': od.delivery_date,
                'internal_delivery_date': od.internal_delivery_date,
                'sales_order_number': order.order_number,
                'customer_order_number': order.customer_order_number,
                'product_category': None,
                'customer_code': None,
                'material_structure': od.material_structure,
                'price': od.unit_price,
                'amount': od.amount
            })

        return details 

    def _notice_to_dict(self, notice: DeliveryNotice) -> Dict[str, Any]:
        """将DeliveryNotice对象转换为字典并附加销售订单信息"""
        data = notice.to_dict() if hasattr(notice, 'to_dict') else {c.name: getattr(notice, c.name) for c in notice.__table__.columns}
        
        # 客户信息已在 joinedload(customer) 中，可通过notice.customer
        if notice.customer:
            data['customer'] = {
                'id': str(notice.customer.id),
                'customer_name': notice.customer.customer_name,
                'customer_abbreviation': notice.customer.customer_abbreviation,
                'remarks': notice.customer.remarks
            }
        
        # 销售订单信息
        if notice.sales_order:
            data['sales_order'] = {
                'id': str(notice.sales_order.id),
                'order_number': notice.sales_order.order_number
            }
            # 同时设置 sales_order_id 为订单号，方便前端显示
            data['sales_order_id'] = notice.sales_order.order_number
        
        # 处理明细，添加 remaining_quantity 字段
        if 'details' in data and data['details']:
            # 如果有销售订单，从销售订单明细中获取 remaining_quantity
            if notice.sales_order:
                session = self.get_session()
                for detail in data['details']:
                    if detail.get('product_id'):
                        # 查找对应的销售订单明细
                        sod = session.query(SalesOrderDetail).filter(
                            SalesOrderDetail.sales_order_id == notice.sales_order.id,
                            SalesOrderDetail.product_id == detail['product_id']
                        ).first()
                        if sod:
                            # 计算未安排数量 = 订单数量 - 已安排数量 + 当前通知数量
                            order_qty = float(sod.order_quantity or 0)
                            scheduled_qty = float(sod.scheduled_delivery_quantity or 0)
                            current_notice_qty = float(detail.get('notice_quantity', 0))
                            # 编辑时：未安排数量 = 订单数量 - 已安排数量 + 当前通知数量
                            detail['remaining_quantity'] = max(0, order_qty - scheduled_qty + current_notice_qty)
                        else:
                            detail['remaining_quantity'] = 0
                    else:
                        detail['remaining_quantity'] = 0
            else:
                # 如果没有销售订单，使用默认值
                for detail in data['details']:
                    detail['remaining_quantity'] = detail.get('order_quantity', 0)
        
        return data

    def _check_and_close_sales_order(self, sales_order_id: str, user_id: str) -> None:
        """
        检查销售订单的所有明细是否都已安排完毕，如果是则关闭订单
        
        Args:
            sales_order_id: 销售订单ID
            user_id: 用户ID
        """
        session = self.get_session()
        
        # 获取销售订单及其所有明细
        sales_order = session.query(SalesOrder).options(
            joinedload(SalesOrder.order_details)
        ).get(sales_order_id)
        
        if not sales_order:
            return
        
        # 检查是否所有明细的已安排数量都大于等于订单数量
        all_details_fully_scheduled = True
        
        for detail in sales_order.order_details:
            order_qty = Decimal(str(detail.order_quantity or 0))
            scheduled_qty = Decimal(str(detail.scheduled_delivery_quantity or 0))
            
            # 如果任何一个明细的已安排数量小于订单数量，则不能关闭
            if scheduled_qty < order_qty:
                all_details_fully_scheduled = False
                break
        
        # 如果所有明细都已安排完毕，则关闭销售订单
        if all_details_fully_scheduled and sales_order.status not in ['shipped', 'completed', 'cancelled']:
            sales_order.status = 'shipped'
            sales_order.updated_by = user_id
            self.log_operation('auto_close_sales_order', {
                'sales_order_id': sales_order_id,
                'reason': '所有明细已安排完毕'
            })

    def _update_sales_order_status_after_delete(self, sales_order_id: str, user_id: str) -> None:
        """
        删除送货通知单后更新销售订单状态
        
        Args:
            sales_order_id: 销售订单ID
            user_id: 用户ID
        """
        session = self.get_session()
        
        # 获取销售订单及其所有明细
        sales_order = session.query(SalesOrder).options(
            joinedload(SalesOrder.order_details)
        ).get(sales_order_id)
        
        if not sales_order:
            return
        
        # 检查所有明细的已安排数量
        all_details_no_scheduled = True
        any_detail_has_scheduled = False
        
        for detail in sales_order.order_details:
            scheduled_qty = Decimal(str(detail.scheduled_delivery_quantity or 0))
            
            if scheduled_qty > 0:
                any_detail_has_scheduled = True
                all_details_no_scheduled = False
        
        # 根据已安排数量更新销售订单状态
        if all_details_no_scheduled:
            # 如果所有明细的已安排数量都是0，则变为已确认
            if sales_order.status in ['shipped', 'partial_shipped']:
                old_status = sales_order.status
                sales_order.status = 'confirmed'
                sales_order.updated_by = user_id
                self.log_operation('update_sales_order_status_after_delete', {
                    'sales_order_id': sales_order_id,
                    'old_status': old_status,
                    'new_status': 'confirmed',
                    'reason': '删除送货通知单后，所有明细已安排数量为0'
                })
        elif any_detail_has_scheduled:
            # 如果有明细的已安排数量大于0，则变为部分安排送货
            if sales_order.status in ['confirmed', 'shipped']:
                old_status = sales_order.status
                sales_order.status = 'partial_shipped'
                sales_order.updated_by = user_id
                self.log_operation('update_sales_order_status_after_delete', {
                    'sales_order_id': sales_order_id,
                    'old_status': old_status,
                    'new_status': 'partial_shipped',
                    'reason': '删除送货通知单后，部分明细仍有已安排数量'
                }) 