# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
材料出库管理 API

提供材料出库单的完整管理功能：
- 出库单列表查询和创建
- 出库单详情获取和更新
- 出库单删除和状态管理
- 出库单提交、审核、执行流程
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.business.inventory.material_outbound_service import MaterialOutboundService
from app.models.business.inventory import (
    MaterialOutboundOrder, MaterialOutboundOrderDetail, Inventory, InventoryTransaction
)
from app.models.basic_data import Unit
from datetime import datetime
from decimal import Decimal
from app import db
import logging

# 设置蓝图
bp = Blueprint('material_outbound', __name__)
logger = logging.getLogger(__name__)

# ==================== 材料出库单管理 ====================

@bp.route('/outbound-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_outbound_orders():
    """获取材料出库单列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        approval_status = request.args.get('approval_status', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        warehouse_id = request.args.get('warehouse_id', '')

        # 日期转换
        start_date_obj = None
        end_date_obj = None
        if start_date:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # 使用MaterialOutboundService
        service = MaterialOutboundService()
        result = service.get_material_outbound_order_list(
            warehouse_id=warehouse_id,
            order_type=request.args.get('order_type'),
            status=status,
            approval_status=approval_status,
            start_date=start_date_obj,
            end_date=end_date_obj,
            search=search,
            page=page,
            page_size=page_size
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"获取材料出库单列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_material_outbound_order():
    """创建材料出库单"""
    try:
        data = request.get_json()
        
        # 验证必需字段 - 修复：使用新的外键字段名
        required_fields = ['warehouse_id', 'order_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'code': 400, 'message': f'缺少必需字段: {field}'}), 400

        current_user = get_jwt_identity()
        
        # 如果没有warehouse_name，根据warehouse_id获取
        if not data.get('warehouse_name') and data.get('warehouse_id'):
            try:
                # 从仓库服务获取仓库名称
                from app.services.base_archive.production.production_archive.warehouse_service import WarehouseService
                warehouse_service = WarehouseService()
                warehouses = warehouse_service.get_warehouses(page=1, per_page=1000)
                warehouse = next((w for w in warehouses.get('items', []) if str(w.get('id')) == str(data.get('warehouse_id'))), None)
                if warehouse:
                    data['warehouse_name'] = warehouse.get('warehouse_name', f"仓库{data.get('warehouse_id')}")
                else:
                    data['warehouse_name'] = f"仓库{data.get('warehouse_id')}"
            except Exception as e:
                logger.warning(f"获取仓库名称失败: {e}")
                data['warehouse_name'] = f"仓库{data.get('warehouse_id')}"
        
        # 处理字段名映射 - 前端可能使用旧字段名
        if 'outbound_person' in data and 'outbound_person_id' not in data:
            data['outbound_person_id'] = data.pop('outbound_person')
        
        if 'department' in data and 'department_id' not in data:
            data['department_id'] = data.pop('department')
            
        if 'requisition_department' in data and 'requisition_department_id' not in data:
            data['requisition_department_id'] = data.pop('requisition_department')
            
        if 'requisition_person' in data and 'requisition_person_id' not in data:
            data['requisition_person_id'] = data.pop('requisition_person')
        
        # 使用新的服务类创建出库单
        service = MaterialOutboundService()
        order = service.create_material_outbound_order(data, current_user)
        
        # 转换为前端期望的格式
        response_data = order.to_dict()
        response_data['audit_status'] = response_data.pop('approval_status', 'pending')
        response_data['remarks'] = response_data.pop('remark', '')

        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': response_data
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建材料出库单失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500


@bp.route('/outbound-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_outbound_order(order_id):
    """获取材料出库单详情"""
    try:
        # 使用原生模型查询，不依赖service
        order = MaterialOutboundOrder.query.get(order_id)
        
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404

        # 获取明细
        details = MaterialOutboundOrderDetail.query.filter_by(material_outbound_order_id=order_id).all()
        
        order_dict = order.to_dict()
        order_dict['details'] = [detail.to_dict() for detail in details]
        order_dict['audit_status'] = order_dict.pop('approval_status', 'pending')

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': order_dict
        })

    except Exception as e:
        logger.error(f"获取材料出库单详情失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@bp.route('/outbound-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_material_outbound_order(order_id):
    """更新材料出库单"""
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404

        if order.status != 'draft':
            return jsonify({'code': 400, 'message': '只能修改草稿状态的出库单'}), 400

        # 处理字段名映射
        if 'outbound_person' in data and 'outbound_person_id' not in data:
            data['outbound_person_id'] = data.pop('outbound_person')
        
        if 'department' in data and 'department_id' not in data:
            data['department_id'] = data.pop('department')
            
        if 'requisition_department' in data and 'requisition_department_id' not in data:
            data['requisition_department_id'] = data.pop('requisition_department')
            
        if 'requisition_person' in data and 'requisition_person_id' not in data:
            data['requisition_person_id'] = data.pop('requisition_person')

        # 更新主表字段
        updateable_fields = [
            'order_date', 'order_type', 'warehouse_id', 'warehouse_name',
            'outbound_person_id', 'department_id', 'requisition_department_id', 
            'requisition_person_id', 'requisition_purpose', 'remark'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(order, field, data[field])

        order.updated_by = current_user
        order.updated_at = datetime.now()
        
        # 处理明细数据
        if 'details' in data:
            details_data = data['details']
            
            # 删除现有明细
            MaterialOutboundOrderDetail.query.filter_by(material_outbound_order_id=order_id).delete()
            
            # 添加新明细
            for detail_data in details_data:
                if detail_data.get('material_id') and detail_data.get('outbound_quantity'):
                    # 处理unit_id字段
                    unit_id = detail_data.get('unit_id')
                    if not unit_id and detail_data.get('unit'):
                        # 如果没有unit_id但有unit字段，尝试从units表中查找对应的unit_id
                        unit = db.session.query(Unit).filter(Unit.unit_name == detail_data['unit']).first()
                        if unit:
                            unit_id = unit.id
                        else:
                            # 如果找不到对应的单位，抛出错误
                            raise ValueError(f"明细缺少必需的unit_id参数")
                    
                    if not unit_id:
                        raise ValueError(f"明细缺少必需的unit_id参数")
                    
                    # 创建明细
                    detail = MaterialOutboundOrderDetail(
                        material_outbound_order_id=order_id,
                        outbound_quantity=Decimal(detail_data.get('outbound_quantity', 0)),
                        unit_id=unit_id,
                        created_by=current_user,
                        material_id=detail_data.get('material_id'),
                        material_name=detail_data.get('material_name'),
                        material_code=detail_data.get('material_code'),
                        material_spec=detail_data.get('specification'),
                        batch_number=detail_data.get('batch_number'),
                        location_code=detail_data.get('location_code'),
                        notes=detail_data.get('remarks')
                    )
                    db.session.add(detail)
        
        db.session.commit()
        
        # 转换为前端期望的格式
        response_data = order.to_dict()
        response_data['audit_status'] = response_data.pop('approval_status', 'pending')

        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': response_data
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新材料出库单失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@bp.route('/outbound-orders/<order_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_material_outbound_order(order_id):
    """删除材料出库单"""
    try:
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404

        if order.status != 'draft':
            return jsonify({'code': 400, 'message': '只能删除草稿状态的出库单'}), 400

        # 删除明细
        MaterialOutboundOrderDetail.query.filter_by(material_outbound_order_id=order_id).delete()
        
        # 删除主单
        db.session.delete(order)
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '删除成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除材料出库单失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500


@bp.route('/outbound-orders/<order_id>/submit', methods=['POST'])
@jwt_required()
@tenant_required
def submit_material_outbound_order(order_id):
    """提交材料出库单"""
    try:
        current_user = get_jwt_identity()
        
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404

        if order.status != 'draft':
            return jsonify({'code': 400, 'message': '只能提交草稿状态的出库单'}), 400

        # 检查是否有明细
        details = MaterialOutboundOrderDetail.query.filter_by(
            material_outbound_order_id=order_id
        ).all()
        
        if not details:
            return jsonify({'code': 400, 'message': '出库单没有明细，无法提交'}), 400

        # 直接设置为已审核状态
        order.status = 'approved'
        order.approval_status = 'approved'
        order.submitted_by = current_user
        order.submitted_at = datetime.now()
        order.approved_by = current_user
        order.approved_at = datetime.now()
        
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '提交成功',
            'data': order.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"提交材料出库单失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'提交失败: {str(e)}'}), 500


@bp.route('/outbound-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
@tenant_required
def approve_material_outbound_order(order_id):
    """审核材料出库单"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        approval_status = data.get('approval_status', 'approved')
        approval_comments = data.get('approval_comments', '')
        
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404

        if order.status != 'submitted':
            return jsonify({'code': 400, 'message': '只能审核已提交的出库单'}), 400
        
        order.approval_status = approval_status
        order.approved_by = current_user
        order.approved_at = datetime.now()
        order.approval_comments = approval_comments
        
        if approval_status == 'approved':
            order.status = 'approved'
        elif approval_status == 'rejected':
            order.status = 'rejected'

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '审核成功',
            'data': order.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"审核材料出库单失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'审核失败: {str(e)}'}), 500


@bp.route('/outbound-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
@tenant_required
def execute_material_outbound_order(order_id):
    """执行材料出库单"""
    try:
        current_user = get_jwt_identity()
        
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404

        if order.status != 'approved':
            return jsonify({'code': 400, 'message': '只能执行已审核通过的出库单'}), 400
        
        # 获取出库单明细
        details = MaterialOutboundOrderDetail.query.filter_by(
            material_outbound_order_id=order_id
        ).all()
        
        if not details:
            return jsonify({'code': 400, 'message': '出库单没有明细数据'}), 400
        
        # 处理每个明细的库存更新
        for detail in details:
            if not detail.material_id:
                continue
                
            # 查找对应的库存记录
            inventory = Inventory.query.filter_by(
                warehouse_id=order.warehouse_id,
                material_id=detail.material_id,
                batch_number=detail.batch_number,
                is_active=True
            ).first()

            if not inventory:
                # 如果没有找到精确匹配的库存（包括批次），尝试找不指定批次的库存
                inventory = Inventory.query.filter_by(
                    warehouse_id=order.warehouse_id,
                    material_id=detail.material_id,
                    is_active=True
                ).first()
            
            if not inventory:
                return jsonify({
                    'code': 400, 
                    'message': f'材料 {detail.material_name} 在仓库中没有库存记录'
                }), 400
            
            outbound_qty = Decimal(str(detail.outbound_quantity))
            
            # 检查库存是否足够
            if inventory.available_quantity < outbound_qty:
                return jsonify({
                    'code': 400,
                    'message': f'材料 {detail.material_name} 库存不足，可用数量: {inventory.available_quantity}，需要出库: {outbound_qty}'
                }), 400
            
            # 记录出库前数量
            quantity_before = inventory.current_quantity
            
            # 更新库存数量
            inventory.current_quantity -= outbound_qty
            inventory.available_quantity -= outbound_qty
            inventory.updated_by = current_user
            inventory.updated_at = datetime.now()
            
            # 重新计算总成本
            inventory.calculate_total_cost()
            
            # 生成库存流水记录
            transaction = InventoryTransaction(
                inventory_id=inventory.id,
                warehouse_id=inventory.warehouse_id,
                material_id=inventory.material_id,
                transaction_type='out',
                quantity_change=-outbound_qty,
                quantity_before=quantity_before,
                quantity_after=inventory.current_quantity,
                unit_id=detail.unit_id,
                created_by=current_user,
                unit_price=detail.unit_price,
                total_amount=detail.total_amount,
                source_document_type='material_outbound_order',
                source_document_id=order.id,
                source_document_number=order.order_number,
                batch_number=detail.batch_number,
                from_location=detail.location_code,
                reason=f'材料出库单 {order.order_number} 执行',
                approval_status='approved',
                approved_by=current_user,
                approved_at=datetime.now()
            )
            
            # 计算流水总金额
            transaction.calculate_total_amount()
            
            db.session.add(transaction)

        # 更新出库单状态
        order.status = 'executed'
        order.executed_by = current_user
        order.executed_at = datetime.now()

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '执行成功，库存已更新',
            'data': order.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"执行材料出库单失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'执行失败: {str(e)}'}), 500


@bp.route('/outbound-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_material_outbound_order(order_id):
    """取消材料出库单"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        cancel_reason = data.get('cancel_reason', '')
        
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404

        if order.status in ['executed', 'cancelled']:
            return jsonify({'code': 400, 'message': '该订单不能取消'}), 400

        order.status = 'cancelled'
        order.cancelled_by = current_user
        order.cancelled_at = datetime.now()
        order.cancel_reason = cancel_reason

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '取消成功',
            'data': order.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"取消材料出库单失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'取消失败: {str(e)}'}), 500

@bp.route('/outbound-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_material_outbound_order_detail(order_id, detail_id):
    """删除材料出库单明细"""
    try:
        service = MaterialOutboundService()
        service.delete_material_outbound_order_detail(detail_id)

        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除材料出库单明细失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500

@bp.route('/outbound-orders/<order_id>/details/<detail_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_material_outbound_order_detail(order_id, detail_id):
    """更新材料出库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 清理数据，移除SQLAlchemy内部属性
        clean_data = {}
        for key, value in data.items():
            if not key.startswith('_') and key not in ['_sa_instance_state']:
                clean_data[key] = value
        
        service = MaterialOutboundService()
        service.update_material_outbound_order_detail(detail_id, clean_data, current_user_id)

        return jsonify({
            'code': 200,
            'message': '更新成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新材料出库单明细失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500

@bp.route('/outbound-orders/<order_id>/details', methods=['POST'])
@jwt_required()
@tenant_required
def create_material_outbound_order_detail(order_id):
    """创建材料出库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 清理数据，移除SQLAlchemy内部属性
        clean_data = {}
        for key, value in data.items():
            if not key.startswith('_') and key not in ['_sa_instance_state']:
                clean_data[key] = value
        
        service = MaterialOutboundService()
        service.create_material_outbound_order_detail(order_id, clean_data, current_user_id)

        return jsonify({
            'code': 200,
            'message': '创建成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建材料出库单明细失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500