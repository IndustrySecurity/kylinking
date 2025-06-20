#!/usr/bin/env python3
"""
创建材料盘点功能测试数据
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.extensions import db
from app.models.business.inventory import Inventory, InventoryCountPlan, InventoryCountRecord
from app.models.basic_data import Warehouse, Material


def create_test_data():
    """创建测试数据"""
    app = create_app()
    
    with app.app_context():
        # 设置测试租户schema
        test_schema = 'wanle_test'
        db.session.execute(f'SET search_path TO {test_schema}, public')
        
        try:
            # 创建测试仓库
            test_warehouses = []
            warehouses_data = [
                {'warehouse_name': '原材料一库', 'warehouse_code': 'CL001', 'warehouse_type': '材料仓库'},
                {'warehouse_name': '原材料二库', 'warehouse_code': 'CL002', 'warehouse_type': '材料仓库'},
                {'warehouse_name': '辅料仓库', 'warehouse_code': 'CL003', 'warehouse_type': '材料仓库'}
            ]
            
            for warehouse_data in warehouses_data:
                warehouse = Warehouse.query.filter_by(warehouse_code=warehouse_data['warehouse_code']).first()
                if not warehouse:
                    warehouse = Warehouse(
                        id=uuid.uuid4(),
                        **warehouse_data,
                        storage_capacity=10000,
                        is_active=True,
                        created_by=uuid.uuid4(),
                        created_at=datetime.now()
                    )
                    db.session.add(warehouse)
                test_warehouses.append(warehouse)
            
            # 创建测试材料
            test_materials = []
            materials_data = [
                {'material_name': 'PE塑料颗粒', 'material_code': 'MAT001', 'specification': '规格A', 'unit': '吨'},
                {'material_name': 'PP塑料颗粒', 'material_code': 'MAT002', 'specification': '规格B', 'unit': '吨'},
                {'material_name': '聚乙烯薄膜', 'material_code': 'MAT003', 'specification': '0.05mm', 'unit': '米'},
                {'material_name': '包装袋', 'material_code': 'MAT004', 'specification': '50kg装', 'unit': '个'},
                {'material_name': '胶水', 'material_code': 'MAT005', 'specification': '环保型', 'unit': '桶'},
                {'material_name': '印刷墨水', 'material_code': 'MAT006', 'specification': '黑色', 'unit': '升'}
            ]
            
            for material_data in materials_data:
                material = Material.query.filter_by(material_code=material_data['material_code']).first()
                if not material:
                    material = Material(
                        id=uuid.uuid4(),
                        **material_data,
                        is_active=True,
                        created_by=uuid.uuid4(),
                        created_at=datetime.now()
                    )
                    db.session.add(material)
                test_materials.append(material)
            
            db.session.commit()
            
            # 创建测试库存记录
            test_user_id = uuid.uuid4()
            for warehouse in test_warehouses:
                for i, material in enumerate(test_materials):
                    # 为每个仓库创建部分材料的库存记录
                    if warehouse.warehouse_code == 'CL001' or i < 3:  # 第一个仓库有所有材料，其他仓库只有前3种
                        inventory = Inventory(
                            warehouse_id=warehouse.id,
                            material_id=material.id,
                            current_quantity=Decimal(str(100 + i * 50)),  # 100, 150, 200, 250...
                            available_quantity=Decimal(str(100 + i * 50)),
                            unit=material.unit,
                            unit_cost=Decimal(str(10 + i)),
                            batch_number=f'B{datetime.now().strftime("%Y%m%d")}{i+1:03d}',
                            location_code=f'A01-{i+1:02d}-01',
                            inventory_status='normal',
                            quality_status='qualified',
                            safety_stock=Decimal('10'),
                            min_stock=Decimal('5'),
                            max_stock=Decimal('1000'),
                            created_by=test_user_id
                        )
                        inventory.calculate_total_cost()
                        db.session.add(inventory)
            
            db.session.commit()
            print("✓ 测试库存数据创建成功")
            
            # 创建测试盘点计划
            count_plan = InventoryCountPlan(
                plan_name='2024年末材料盘点',
                count_type='full',
                warehouse_ids=[str(warehouse.id) for warehouse in test_warehouses[:2]],  # 前两个仓库
                plan_start_date=datetime.now(),
                plan_end_date=datetime.now() + timedelta(days=3),
                status='confirmed',
                supervisor_id=test_user_id,
                count_team=['张三', '李四', '王五'],
                description='年末全面盘点所有材料库存',
                created_by=test_user_id
            )
            db.session.add(count_plan)
            db.session.commit()
            print(f"✓ 测试盘点计划创建成功: {count_plan.plan_number}")
            
            # 为盘点计划生成盘点记录
            inventories = Inventory.query.filter(
                Inventory.warehouse_id.in_([warehouse.id for warehouse in test_warehouses[:2]]),
                Inventory.material_id.isnot(None),
                Inventory.is_active == True
            ).all()
            
            for inventory in inventories:
                count_record = InventoryCountRecord(
                    count_plan_id=count_plan.id,
                    inventory_id=inventory.id,
                    warehouse_id=inventory.warehouse_id,
                    material_id=inventory.material_id,
                    book_quantity=inventory.current_quantity,
                    batch_number=inventory.batch_number,
                    location_code=inventory.location_code,
                    unit=inventory.unit,
                    status='pending',
                    created_by=test_user_id
                )
                db.session.add(count_record)
            
            db.session.commit()
            
            # 为部分记录设置实盘数据
            records = InventoryCountRecord.query.filter_by(count_plan_id=count_plan.id).limit(3).all()
            for i, record in enumerate(records):
                # 模拟不同的盘点结果
                if i == 0:  # 盘盈
                    record.actual_quantity = record.book_quantity + Decimal('5')
                elif i == 1:  # 盘亏
                    record.actual_quantity = record.book_quantity - Decimal('3')
                else:  # 账实相符
                    record.actual_quantity = record.book_quantity
                
                record.count_by = test_user_id
                record.count_date = datetime.now()
                record.status = 'counted'
                record.calculate_variance()
                
                if record.variance_quantity != 0:
                    record.variance_reason = '正常损耗' if record.variance_quantity < 0 else '发现遗漏库存'
            
            db.session.commit()
            print(f"✓ 测试盘点记录创建成功: {len(inventories)} 条记录")
            
            print("\n📊 测试数据创建完成!")
            print(f"   - 仓库数量: {len(test_warehouses)}")
            print(f"   - 材料数量: {len(test_materials)}")
            print(f"   - 库存记录: {len(inventories)}")
            print(f"   - 盘点计划: 1")
            print(f"   - 盘点记录: {len(inventories)}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建测试数据失败: {str(e)}")
            raise


if __name__ == '__main__':
    create_test_data() 