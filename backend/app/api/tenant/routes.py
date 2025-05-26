from flask import jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.tenant import tenant_bp
from app.models.business.production import ProductionPlan, ProductionRecord
from app.extensions import db
from app.utils.tenant_context import tenant_context_required
from datetime import datetime
import uuid
from functools import wraps


def tenant_required(fn):
    """
    装饰器，确保用户有对应的租户
    """
    @jwt_required()
    @wraps(fn)  # 添加functools.wraps保留原始函数名称
    def tenant_wrapper(*args, **kwargs):
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({"message": "No tenant associated with user"}), 403
        
        return fn(*args, **kwargs)
    
    return tenant_wrapper


@tenant_bp.route('/production/plans', methods=['GET'])
@tenant_required
@tenant_context_required
def get_production_plans():
    """
    获取租户的生产计划列表
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = ProductionPlan.query
    
    # 过滤条件
    if request.args.get('name'):
        query = query.filter(ProductionPlan.name.ilike(f"%{request.args.get('name')}%"))
    
    if request.args.get('status'):
        query = query.filter(ProductionPlan.status == request.args.get('status'))
    
    # 时间范围过滤
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        query = query.filter(ProductionPlan.start_date >= start_date)
    
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        query = query.filter(ProductionPlan.end_date <= end_date)
    
    # 分页
    pagination = query.order_by(ProductionPlan.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # 序列化结果
    plans = []
    for plan in pagination.items:
        plans.append({
            "id": str(plan.id),
            "name": plan.name,
            "description": plan.description,
            "start_date": plan.start_date.isoformat() if plan.start_date else None,
            "end_date": plan.end_date.isoformat() if plan.end_date else None,
            "status": plan.status,
            "created_at": plan.created_at.isoformat(),
            "updated_at": plan.updated_at.isoformat()
        })
    
    return jsonify({
        "production_plans": plans,
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page,
        "per_page": per_page
    }), 200


@tenant_bp.route('/production/plans/<uuid:plan_id>', methods=['GET'])
@tenant_required
@tenant_context_required
def get_production_plan(plan_id):
    """
    获取单个生产计划详情
    """
    plan = ProductionPlan.query.get_or_404(plan_id)
    
    # 获取关联的生产记录
    records = []
    for record in plan.production_records:
        records.append({
            "id": str(record.id),
            "start_time": record.start_time.isoformat() if record.start_time else None,
            "end_time": record.end_time.isoformat() if record.end_time else None,
            "quantity": float(record.quantity),
            "status": record.status,
            "notes": record.notes,
            "created_at": record.created_at.isoformat()
        })
    
    # 序列化计划数据
    plan_data = {
        "id": str(plan.id),
        "name": plan.name,
        "description": plan.description,
        "start_date": plan.start_date.isoformat() if plan.start_date else None,
        "end_date": plan.end_date.isoformat() if plan.end_date else None,
        "status": plan.status,
        "created_at": plan.created_at.isoformat(),
        "updated_at": plan.updated_at.isoformat(),
        "production_records": records
    }
    
    return jsonify({"production_plan": plan_data}), 200


@tenant_bp.route('/production/plans', methods=['POST'])
@tenant_required
@tenant_context_required
def create_production_plan():
    """
    创建新的生产计划
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 验证请求数据
    data = request.json
    
    # 基本字段验证
    if not data.get('name'):
        return jsonify({"message": "Name is required"}), 400
    
    if not data.get('start_date'):
        return jsonify({"message": "Start date is required"}), 400
    
    if not data.get('end_date'):
        return jsonify({"message": "End date is required"}), 400
    
    if not data.get('status'):
        return jsonify({"message": "Status is required"}), 400
    
    # 解析日期
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # 验证日期范围
    if end_date < start_date:
        return jsonify({"message": "End date cannot be before start date"}), 400
    
    # 创建新的生产计划
    new_plan = ProductionPlan(
        name=data['name'],
        start_date=start_date,
        end_date=end_date,
        status=data['status'],
        created_by=current_user_id,
        description=data.get('description')
    )
    
    # 保存到数据库
    db.session.add(new_plan)
    db.session.commit()
    
    # 序列化返回数据
    plan_data = {
        "id": str(new_plan.id),
        "name": new_plan.name,
        "description": new_plan.description,
        "start_date": new_plan.start_date.isoformat(),
        "end_date": new_plan.end_date.isoformat(),
        "status": new_plan.status,
        "created_at": new_plan.created_at.isoformat(),
        "updated_at": new_plan.updated_at.isoformat()
    }
    
    return jsonify({"message": "Production plan created successfully", "production_plan": plan_data}), 201


@tenant_bp.route('/production/plans/<uuid:plan_id>', methods=['PUT'])
@tenant_required
@tenant_context_required
def update_production_plan(plan_id):
    """
    更新生产计划
    """
    # 获取计划
    plan = ProductionPlan.query.get_or_404(plan_id)
    
    # 验证请求数据
    data = request.json
    
    # 更新计划数据
    if data.get('name'):
        plan.name = data['name']
    
    if data.get('description') is not None:  # 允许将描述设置为空
        plan.description = data['description']
    
    if data.get('start_date'):
        try:
            plan.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"message": "Invalid start date format. Use YYYY-MM-DD"}), 400
    
    if data.get('end_date'):
        try:
            plan.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"message": "Invalid end date format. Use YYYY-MM-DD"}), 400
    
    # 验证日期范围
    if plan.end_date < plan.start_date:
        return jsonify({"message": "End date cannot be before start date"}), 400
    
    if data.get('status'):
        plan.status = data['status']
    
    # 保存更新
    db.session.commit()
    
    # 序列化返回数据
    plan_data = {
        "id": str(plan.id),
        "name": plan.name,
        "description": plan.description,
        "start_date": plan.start_date.isoformat(),
        "end_date": plan.end_date.isoformat(),
        "status": plan.status,
        "created_at": plan.created_at.isoformat(),
        "updated_at": plan.updated_at.isoformat()
    }
    
    return jsonify({"message": "Production plan updated successfully", "production_plan": plan_data}), 200


@tenant_bp.route('/production/plans/<uuid:plan_id>', methods=['DELETE'])
@tenant_required
@tenant_context_required
def delete_production_plan(plan_id):
    """
    删除生产计划
    """
    # 获取计划
    plan = ProductionPlan.query.get_or_404(plan_id)
    
    # 记录标识信息
    plan_name = plan.name
    
    # 删除计划（物理删除）
    db.session.delete(plan)
    db.session.commit()
    
    return jsonify({"message": f"Production plan '{plan_name}' deleted successfully"}), 200


@tenant_bp.route('/production/records', methods=['POST'])
@tenant_required
@tenant_context_required
def create_production_record():
    """
    创建新的生产记录
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 验证请求数据
    data = request.json
    
    # 基本字段验证
    if not data.get('plan_id'):
        return jsonify({"message": "Production plan ID is required"}), 400
    
    if not data.get('equipment_id'):
        return jsonify({"message": "Equipment ID is required"}), 400
    
    if not data.get('start_time'):
        return jsonify({"message": "Start time is required"}), 400
    
    if not data.get('quantity'):
        return jsonify({"message": "Quantity is required"}), 400
    
    if not data.get('status'):
        return jsonify({"message": "Status is required"}), 400
    
    # 解析时间
    try:
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = None
        if data.get('end_time'):
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({"message": "Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS.sssZ)"}), 400
    
    # 验证计划是否存在
    plan_id = uuid.UUID(data['plan_id']) if isinstance(data['plan_id'], str) else data['plan_id']
    if not ProductionPlan.query.get(plan_id):
        return jsonify({"message": "Production plan not found"}), 404
    
    # 创建新的生产记录
    new_record = ProductionRecord(
        plan_id=plan_id,
        equipment_id=uuid.UUID(data['equipment_id']) if isinstance(data['equipment_id'], str) else data['equipment_id'],
        start_time=start_time,
        end_time=end_time,
        quantity=data['quantity'],
        status=data['status'],
        created_by=current_user_id,
        notes=data.get('notes')
    )
    
    # 保存到数据库
    db.session.add(new_record)
    db.session.commit()
    
    # 序列化返回数据
    record_data = {
        "id": str(new_record.id),
        "plan_id": str(new_record.plan_id),
        "equipment_id": str(new_record.equipment_id),
        "start_time": new_record.start_time.isoformat(),
        "end_time": new_record.end_time.isoformat() if new_record.end_time else None,
        "quantity": float(new_record.quantity),
        "status": new_record.status,
        "notes": new_record.notes,
        "created_at": new_record.created_at.isoformat(),
        "updated_at": new_record.updated_at.isoformat()
    }
    
    return jsonify({"message": "Production record created successfully", "production_record": record_data}), 201 