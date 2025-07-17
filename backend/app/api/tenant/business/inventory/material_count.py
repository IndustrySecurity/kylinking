# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
材料盘点管理 API

提供材料盘点的完整管理功能：
- 材料盘点列表查询和创建
- 材料盘点详情获取和更新
- 材料盘点删除和状态管理
- 材料盘点审核、执行、取消流程
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.tenant.routes import tenant_required
import logging

# 设置蓝图
bp = Blueprint('material_count', __name__)
logger = logging.getLogger(__name__)

# ==================== 材料盘点管理 ====================

@bp.route('/material-count-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_count_orders():
    """获取材料盘点列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        count_number = request.args.get('count_number')
        warehouse_id = request.args.get('warehouse_id')
        status = request.args.get('status')
        approval_status = request.args.get('approval_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        
        # 获取材料盘点列表
        from app.services.business.inventory.material_count_service import MaterialCountService
        service = MaterialCountService()
        result = service.get_material_count_list(
            warehouse_id=warehouse_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            search=count_number,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取材料盘点列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/material-count-orders/<count_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_count_order(count_id):
    """获取材料盘点详情"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.material_count_service import MaterialCountService
        service = MaterialCountService()
        count = service.get_material_count_by_id(count_id)
        
        if not count:
            return jsonify({'error': '材料盘点不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': count
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"获取材料盘点详情失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/material-count-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_material_count_order():
    """创建材料盘点"""
    try:
        current_user_id = get_jwt_identity()

        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('warehouse_id'):
            return jsonify({'error': '仓库ID不能为空'}), 400
        
        from app.services.business.inventory.material_count_service import MaterialCountService
        service = MaterialCountService()
        count = service.create_material_count(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': count,
            'message': '材料盘点创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建材料盘点失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/material-count-orders/<count_id>/start', methods=['POST'])
@jwt_required()
@tenant_required
def start_material_count_order(count_id):
    """开始材料盘点"""
    try:
        current_user_id = get_jwt_identity()
        
        from app.services.business.inventory.material_count_service import MaterialCountService
        service = MaterialCountService()
        result = service.start_material_count(count_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '盘点已开始'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"开始材料盘点失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/material-count-orders/<count_id>/complete', methods=['POST'])
@jwt_required()
@tenant_required
def complete_material_count_order(count_id):
    """完成材料盘点"""
    try:
        current_user_id = get_jwt_identity()
        
        from app.services.business.inventory.material_count_service import MaterialCountService
        service = MaterialCountService()
        result = service.complete_material_count(count_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '盘点已完成'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"完成材料盘点失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/material-count-orders/<order_id>/adjust', methods=['POST'])
@jwt_required()
@tenant_required
def adjust_material_count_inventory(order_id):
    """调整材料盘点库存"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        from app.services.business.inventory.material_count_service import MaterialCountService
        service = MaterialCountService()
        result = service.adjust_material_count_inventory(order_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '库存调整成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"调整材料盘点库存失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/material-count-orders/<count_id>/records', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_count_records(count_id):
    """获取材料盘点记录"""
    try:
        from app.services.business.inventory.material_count_service import MaterialCountService
        service = MaterialCountService()
        records = service.get_material_count_records(count_id)
        
        return jsonify({
            'success': True,
            'data': records
        })
        
    except Exception as e:
        logger.error(f"获取材料盘点记录失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/material-count-orders/<count_id>/records/<record_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_material_count_record(count_id, record_id):
    """更新材料盘点记录"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.business.inventory.material_count_service import MaterialCountService
        service = MaterialCountService()
        record = service.update_material_count_record(record_id, current_user_id, data)
        
        return jsonify({
            'success': True,
            'data': record,
            'message': '盘点记录更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"更新材料盘点记录失败: {str(e)}")
        return jsonify({'error': str(e)}), 500
