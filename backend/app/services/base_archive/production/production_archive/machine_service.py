# -*- coding: utf-8 -*-
"""
Machine管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import Machine
from app.models.user import User


class MachineService(TenantAwareService):
    """机台服务类"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化Machine服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_machines(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取机台列表"""
        try:
            from app.models.basic_data import Machine
            from sqlalchemy import or_
            
            query = self.session.query(Machine)
            
            # 搜索过滤
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    or_(
                        Machine.machine_name.ilike(search_pattern),
                        Machine.machine_code.ilike(search_pattern),
                        Machine.model.ilike(search_pattern)
                    )
                )
            
            # 启用状态过滤
            if enabled_only:
                query = query.filter(Machine.is_enabled == True)
            
            # 排序
            query = query.order_by(Machine.sort_order, Machine.machine_name)
            
            # 总数
            total = query.count()
            
            # 分页
            machines = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 转换为字典
            machine_list = [machine.to_dict() for machine in machines]
            
            return {
                'items': machine_list,
                'total': total,
                'pages': (total + per_page - 1) // per_page,
                'current_page': page,
                'per_page': per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            }
            
        except Exception as e:
            print(f"获取机台列表失败: {str(e)}")
            raise e
    def get_machine(self, machine_id):
        """获取单个机台"""
        try:
            from app.models.basic_data import Machine
            import uuid
            
            machine = self.session.query(Machine).get(uuid.UUID(machine_id))
            if not machine:
                return None
            
            # 获取用户信息
            from app.models.user import User
            user_ids = []
            if machine.created_by:
                user_ids.append(machine.created_by)
            if machine.updated_by:
                user_ids.append(machine.updated_by)
            
            users = {}
            if user_ids:
                user_list = self.session.query(User).filter(User.id.in_(user_ids)).all()
                users = {str(user.id): user.get_full_name() for user in user_list}
            
            machine_dict = machine.to_dict()
            machine_dict['created_by_name'] = users.get(str(machine.created_by), '')
            machine_dict['updated_by_name'] = users.get(str(machine.updated_by), '')
            
            return machine_dict
            
        except Exception as e:
            print(f"获取机台失败: {str(e)}")
            raise e
    def create_machine(self, data, created_by):
        """创建机台"""
        try:
            from app.models.basic_data import Machine
            import uuid
            
            # 生成机台编号
            machine_code = Machine.generate_machine_code()
            
            # 创建机台
            machine = Machine(
                machine_code=machine_code,
                machine_name=data.get('machine_name'),
                model=data.get('model'),
                min_width=data.get('min_width'),
                max_width=data.get('max_width'),
                production_speed=data.get('production_speed'),
                preparation_time=data.get('preparation_time'),
                difficulty_factor=data.get('difficulty_factor'),
                circulation_card_id=data.get('circulation_card_id'),
                max_colors=data.get('max_colors'),
                kanban_display=data.get('kanban_display'),
                capacity_formula=data.get('capacity_formula'),
                gas_unit_price=data.get('gas_unit_price'),
                power_consumption=data.get('power_consumption'),
                electricity_cost_per_hour=data.get('electricity_cost_per_hour'),
                output_conversion_factor=data.get('output_conversion_factor'),
                plate_change_time=data.get('plate_change_time'),
                mes_barcode_prefix=data.get('mes_barcode_prefix'),
                is_curing_room=data.get('is_curing_room', False),
                material_name=data.get('material_name'),
                remarks=data.get('remarks'),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.session.add(machine)
            self.commit()
            
            return machine.to_dict()
            
        except Exception as e:
            self.rollback()
            print(f"创建机台失败: {str(e)}")
            raise e
    def update_machine(self, machine_id, data, updated_by):
        """更新机台"""
        try:
            from app.models.basic_data import Machine
            import uuid
            
            machine = self.session.query(Machine).get(uuid.UUID(machine_id))
            if not machine:
                raise ValueError("机台不存在")
            
            # 更新字段
            if 'machine_name' in data:
                machine.machine_name = data['machine_name']
            if 'model' in data:
                machine.model = data['model']
            if 'min_width' in data:
                machine.min_width = data['min_width']
            if 'max_width' in data:
                machine.max_width = data['max_width']
            if 'production_speed' in data:
                machine.production_speed = data['production_speed']
            if 'preparation_time' in data:
                machine.preparation_time = data['preparation_time']
            if 'difficulty_factor' in data:
                machine.difficulty_factor = data['difficulty_factor']
            if 'circulation_card_id' in data:
                machine.circulation_card_id = data['circulation_card_id']
            if 'max_colors' in data:
                machine.max_colors = data['max_colors']
            if 'kanban_display' in data:
                machine.kanban_display = data['kanban_display']
            if 'capacity_formula' in data:
                machine.capacity_formula = data['capacity_formula']
            if 'gas_unit_price' in data:
                machine.gas_unit_price = data['gas_unit_price']
            if 'power_consumption' in data:
                machine.power_consumption = data['power_consumption']
            if 'electricity_cost_per_hour' in data:
                machine.electricity_cost_per_hour = data['electricity_cost_per_hour']
            if 'output_conversion_factor' in data:
                machine.output_conversion_factor = data['output_conversion_factor']
            if 'plate_change_time' in data:
                machine.plate_change_time = data['plate_change_time']
            if 'mes_barcode_prefix' in data:
                machine.mes_barcode_prefix = data['mes_barcode_prefix']
            if 'is_curing_room' in data:
                machine.is_curing_room = data['is_curing_room']
            if 'material_name' in data:
                machine.material_name = data['material_name']
            if 'remarks' in data:
                machine.remarks = data['remarks']
            if 'sort_order' in data:
                machine.sort_order = data['sort_order']
            if 'is_enabled' in data:
                machine.is_enabled = data['is_enabled']
            
            machine.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            
            return machine.to_dict()
            
        except Exception as e:
            self.rollback()
            print(f"更新机台失败: {str(e)}")
            raise e
    def delete_machine(self, machine_id):
        """删除机台"""
        try:
            from app.models.basic_data import Machine
            import uuid
            
            machine = self.session.query(Machine).get(uuid.UUID(machine_id))
            if not machine:
                raise ValueError("机台不存在")
            
            self.session.delete(machine)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            print(f"删除机台失败: {str(e)}")
            raise e
    def batch_update_machines(self, data_list, updated_by):
        """批量更新机台"""
        try:
            from app.models.basic_data import Machine
            import uuid
            
            updated_machines = []
            
            for item in data_list:
                machine_id = item.get('id')
                if not machine_id:
                    continue
                
                machine = self.session.query(Machine).get(uuid.UUID(machine_id))
                if not machine:
                    continue
                
                # 更新字段
                for field in ['machine_name', 'model', 'min_width', 'max_width', 'production_speed',
                             'preparation_time', 'difficulty_factor', 'circulation_card_id', 'max_colors',
                             'kanban_display', 'capacity_formula', 'gas_unit_price', 'power_consumption',
                             'electricity_cost_per_hour', 'output_conversion_factor', 'plate_change_time',
                             'mes_barcode_prefix', 'is_curing_room', 'material_name', 'remarks',
                             'sort_order', 'is_enabled']:
                    if field in item:
                        setattr(machine, field, item[field])
                
                machine.updated_by = uuid.UUID(updated_by)
                updated_machines.append(machine.to_dict())
            
            self.commit()
            
            return updated_machines
            
        except Exception as e:
            self.rollback()
            print(f"批量更新机台失败: {str(e)}")
            raise e
    def get_enabled_machines(self):
        """获取启用的机台列表"""
        try:
            from app.models.basic_data import Machine
            
            machines = self.session.query(Machine).filter_by(is_enabled=True).order_by(Machine.sort_order, Machine.machine_name).all()
            return [machine.to_dict() for machine in machines]
            
        except Exception as e:
            print(f"获取启用机台列表失败: {str(e)}")
            raise e

