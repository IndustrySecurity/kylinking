# -*- coding: utf-8 -*-
"""
送货通知单服务
"""
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import desc
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import Dict, Any, Optional
from flask import current_app

from app.services.base_service import TenantAwareService
from app.models.business.sales import DeliveryNotice, DeliveryNoticeDetail
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

            # 处理明细
            if 'details' in notice_data and notice_data['details']:
                for detail_data in notice_data['details']:
                    detail_data['created_by'] = user_id
                    detail_data['delivery_notice_id'] = notice.id
                    new_detail = self.create_with_tenant(DeliveryNoticeDetail, **detail_data)
                    
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
        query = session.query(DeliveryNotice).options(joinedload(DeliveryNotice.customer))
        
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
            'items': [item.to_dict() for item in pagination.items],
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
            joinedload(DeliveryNotice.details).joinedload(DeliveryNoticeDetail.product)
        ).get(notice_id)
        
        if notice and self.validate_tenant_access(getattr(notice, 'tenant_id', self.tenant_id)):
            return notice.to_dict()
        
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

        self.log_operation('update_delivery_notice', {
            'notice_id': notice_id, 
            'data_keys': list(data.keys())
        })

        # 更新主表字段
        for key, value in data.items():
            if hasattr(notice, key) and key not in ['id', 'details', 'tenant_id']:
                setattr(notice, key, value)
        
        notice.updated_by = user_id

        # 更新或创建或删除明细
        if 'details' in data:
            incoming_detail_ids = {str(d.get('id')) for d in data['details'] if d.get('id')}

            # 删除不在新数据中的明细
            for detail in notice.details[:]:
                if str(detail.id) not in incoming_detail_ids:
                    session.delete(detail)
            
            # 新增或更新明细
            for detail_data in data['details']:
                detail_id = detail_data.get('id')
                if detail_id:  # 更新现有明细
                    detail = session.query(DeliveryNoticeDetail).get(detail_id)
                    if detail and self.validate_tenant_access(getattr(detail, 'tenant_id', self.tenant_id)):
                        for k, v in detail_data.items():
                            if hasattr(detail, k) and k not in ['id', 'tenant_id']:
                                setattr(detail, k, v)
                        detail.updated_by = user_id
                else:  # 新增明细
                    if 'id' in detail_data:
                        del detail_data['id']
                    detail_data['created_by'] = user_id
                    detail_data['delivery_notice_id'] = notice.id
                    new_detail = self.create_with_tenant(DeliveryNoticeDetail, **detail_data)

        self.commit()
        return self.get_delivery_notice_by_id(notice_id)

    def delete_delivery_notice(self, notice_id: str) -> bool:
        """
        删除送货通知单
        
        Args:
            notice_id: 送货通知单ID
            
        Returns:
            bool: 是否删除成功
        """
        session = self.get_session()
        notice = session.query(DeliveryNotice).get(notice_id)
        
        if not notice:
            raise ValueError("送货通知单未找到")
        
        if not self.validate_tenant_access(getattr(notice, 'tenant_id', self.tenant_id)):
            raise ValueError("无权限删除该送货通知单")
        
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