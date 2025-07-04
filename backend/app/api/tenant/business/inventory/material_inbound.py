# -*- coding: utf-8 -*-
# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
材料入库管理API路由
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services import MaterialInboundService
from decimal import Decimal
from datetime import datetime

bp = Blueprint('material_inbound', __name__)


@bp.route('/inbound-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_inbound_orders():
    """获取材料入库单列表"""
    try:
        # 获取查询参数
        warehouse_id = request.args.get('warehouse_id')
        order_type = request.args.get('order_type')
        status = request.args.get('status')
        approval_status = request.args.get('approval_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        
        # 日期转换
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # 使用MaterialInboundService
        service = MaterialInboundService()
        result = service.get_material_inbound_order_list(
            warehouse_id=warehouse_id,
            order_type=order_type,
            status=status,
            approval_status=approval_status,
            start_date=start_date,
            end_date=end_date,
            search=search,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_material_inbound_order():
    """创建材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('warehouse_id'):
            return jsonify({'error': '仓库ID不能为空'}), 400
        
        service = MaterialInboundService()
        order = service.create_material_inbound_order(data, current_user_id)
        
        # 获取部门名称和员工名称
        try:
            department_name = order.department.dept_name if order.department else None
        except Exception as e:
            current_app.logger.warning(f"获取部门名称失败: {e}")
            department_name = None
            
        try:
            inbound_person_name = order.inbound_person.employee_name if order.inbound_person else None
        except Exception as e:
            current_app.logger.warning(f"获取员工名称失败: {e}")
            inbound_person_name = None
        
        # 为了避免SQLAlchemy懒加载问题，手动构建返回数据
        order_data = {
            'id': str(order.id),
            'order_number': order.order_number,
            'order_date': order.order_date.isoformat() if order.order_date else None,
            'order_type': order.order_type,
            'warehouse_id': str(order.warehouse_id) if order.warehouse_id else None,
            'warehouse_name': order.warehouse_name,
            'inbound_person_id': str(order.inbound_person_id) if order.inbound_person_id else None,
            'inbound_person': inbound_person_name,
            'department_id': str(order.department_id) if order.department_id else None,
            'department': department_name,
            'status': order.status,
            'approval_status': order.approval_status,
            'supplier_id': str(order.supplier_id) if order.supplier_id else None,
            'supplier_name': order.supplier_name,
            'notes': order.notes,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'data': order_data,
            'message': '入库单创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_inbound_order(order_id):
    """获取材料入库单详情"""
    try:
        service = MaterialInboundService()
        order = service.get_material_inbound_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': '入库单不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_material_inbound_order(order_id):
    """更新材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = MaterialInboundService()
        # 修复参数顺序：order_id, updated_by, **update_data
        order = service.update_material_inbound_order(order_id, current_user_id, **data)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_material_inbound_order(order_id):
    """删除材料入库单"""
    try:
        service = MaterialInboundService()
        success = service.delete_material_inbound_order(order_id)
        
        if not success:
            return jsonify({'error': '入库单不存在或无法删除'}), 404

        return jsonify({
            'success': True,
            'message': '入库单删除成功'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_inbound_order_details(order_id):
    """获取材料入库单明细列表"""
    try:
        service = MaterialInboundService()
        
        # 首先检查入库单是否存在
        order = service.get_material_inbound_order_by_id(order_id)
        if not order:
            return jsonify({
                'success': False,
                'error': f'入库单不存在: {order_id}',
                'data': []
            }), 404
        
        # 获取明细
        details = service.get_material_inbound_order_details(order_id)
        
        return jsonify({
            'success': True,
            'data': details,
            'message': f'成功获取 {len(details)} 条明细记录'
        })
        
    except Exception as e:
        current_app.logger.error(f"获取材料入库单明细失败 - order_id: {order_id}, error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取入库单明细失败: {str(e)}',
            'data': []
        }), 500


@bp.route('/inbound-orders/<order_id>/details', methods=['POST'])
@jwt_required()
@tenant_required
def add_material_inbound_order_detail(order_id):
    """添加材料入库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('inbound_quantity'):
            return jsonify({'error': '入库数量不能为空'}), 400
        
        service = MaterialInboundService()
        detail = service.add_material_inbound_order_detail(
            order_id=order_id,
            inbound_quantity=Decimal(str(data['inbound_quantity'])),
            unit=data.get('unit', '个'),
            created_by=current_user_id,
            material_id=data.get('material_id'),
            material_name=data.get('material_name'),
            **{k: v for k, v in data.items() if k not in ['inbound_quantity', 'unit', 'material_id', 'material_name']}
        )
        
        return jsonify({
            'success': True,
            'data': detail.to_dict() if hasattr(detail, 'to_dict') else detail,
            'message': '明细添加成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/details/<detail_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_material_inbound_order_detail(order_id, detail_id):
    """更新材料入库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = MaterialInboundService()
        detail = service.update_material_inbound_order_detail(
            detail_id=detail_id,
            updated_by=current_user_id,
            **data
        )
        
        if not detail:
            return jsonify({'error': '明细记录不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': detail.to_dict() if hasattr(detail, 'to_dict') else detail,
            'message': '明细更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_material_inbound_order_detail(order_id, detail_id):
    """删除材料入库单明细"""
    try:
        service = MaterialInboundService()
        success = service.delete_material_inbound_order_detail(detail_id)
        
        if not success:
            return jsonify({'error': '明细记录不存在'}), 404
        
        return jsonify({
            'success': True,
            'message': '明细删除成功'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/submit', methods=['POST'])
@jwt_required()
@tenant_required
def submit_material_inbound_order(order_id):
    """提交材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        
        service = MaterialInboundService()
        order = service.submit_material_inbound_order(order_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单提交成功'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
@tenant_required
def approve_material_inbound_order(order_id):
    """审核材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        approval_status = data.get('approval_status', 'approved')
        
        service = MaterialInboundService()
        order = service.approve_material_inbound_order(order_id, current_user_id, approval_status)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单审核成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
@tenant_required
def execute_material_inbound_order(order_id):
    """执行材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        current_app.logger.info(f"开始执行材料入库单: {order_id}, 操作人: {current_user_id}")
        
        service = MaterialInboundService()
        transactions = service.execute_material_inbound_order(order_id, current_user_id)
        
        current_app.logger.info(f"执行完成，创建了 {len(transactions)} 个库存事务")
        
        return jsonify({
            'success': True,
            'data': {
                'transaction_count': len(transactions),
                'transactions': [t.to_dict() for t in transactions]
            },
            'message': '入库单执行成功'
        })
        
    except ValueError as e:
        current_app.logger.error(f"执行材料入库单失败 - ValueError: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"执行材料入库单失败 - Exception: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_material_inbound_order(order_id):
    """取消材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        cancel_reason = data.get('cancel_reason', '') if data else ''
        
        service = MaterialInboundService()
        order = service.cancel_material_inbound_order(order_id, current_user_id, cancel_reason)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单取消成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 辅助数据API ====================

@bp.route('/warehouses', methods=['GET'])
@jwt_required()
@tenant_required
def get_warehouses():
    """获取仓库列表"""
    try:
        # 获取查询参数
        warehouse_type = request.args.get('warehouse_type', '')
        
        # 使用仓库服务获取真实的仓库数据
        try:
            # 这里应该调用仓库服务，但暂时使用模拟数据
            warehouses = [
                {'value': '1', 'label': '原材料一库', 'code': 'CL001', 'warehouse_type': '材料仓库'},
                {'value': '2', 'label': '原材料二库', 'code': 'CL002', 'warehouse_type': '材料仓库'},
                {'value': '3', 'label': '原材料三库', 'code': 'CL003', 'warehouse_type': '材料仓库'},
                {'value': '4', 'label': '材料仓', 'code': 'CL004', 'warehouse_type': '材料仓库'},
            ]
            
            # 过滤材料仓库
            if warehouse_type == 'material' or not warehouse_type:
                warehouses = [w for w in warehouses if w.get('warehouse_type') == '材料仓库' or '材料' in w.get('label', '')]
                
        except Exception as e:
            current_app.logger.warning(f"获取仓库数据失败，使用模拟数据: {e}")
            warehouses = [
                {'value': '1', 'label': '原材料一库', 'code': 'CL001', 'warehouse_type': '材料仓库'},
                {'value': '2', 'label': '原材料二库', 'code': 'CL002', 'warehouse_type': '材料仓库'},
            ]

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': warehouses
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@bp.route('/materials', methods=['GET'])
@jwt_required()
@tenant_required
def get_materials():
    """获取材料列表"""
    try:
        search = request.args.get('search', '')
        
        materials = [
            {
                'id': 1,
                'name': 'PE塑料颗粒',
                'code': 'MAT001',
                'specification': '规格A',
                'unit': '吨',
                'category': '塑料原料'
            },
            {
                'id': 2,
                'name': 'PP塑料颗粒',
                'code': 'MAT002',
                'specification': '规格B',
                'unit': '吨',
                'category': '塑料原料'
            },
            {
                'id': 3,
                'name': '聚乙烯薄膜',
                'code': 'MAT003',
                'specification': '0.05mm',
                'unit': '米',
                'category': '薄膜材料'
            },
            {
                'id': 4,
                'name': '包装袋',
                'code': 'MAT004',
                'specification': '50kg装',
                'unit': '个',
                'category': '包装材料'
            },
        ]

        # 简单的搜索过滤
        if search:
            materials = [m for m in materials if search.lower() in m['name'].lower() or search.lower() in m['code'].lower()]

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': materials
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@bp.route('/suppliers', methods=['GET'])
@jwt_required()
@tenant_required
def get_suppliers():
    """获取供应商列表"""
    try:
        suppliers = [
            {'id': 1, 'name': '供应商A', 'code': 'SUP001'},
            {'id': 2, 'name': '供应商B', 'code': 'SUP002'},
            {'id': 3, 'name': '供应商C', 'code': 'SUP003'},
        ]

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': suppliers
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@bp.route('/departments/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_department_options():
    """获取部门选项"""
    try:
        # 这里应该调用部门服务，但暂时使用模拟数据
        options = [
            {'value': '1', 'label': '生产部门', 'code': 'PROD'},
            {'value': '2', 'label': '采购部门', 'code': 'PURCH'},
            {'value': '3', 'label': '仓储部门', 'code': 'WARE'},
        ]
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 