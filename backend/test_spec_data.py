from app import create_app
from app.extensions import db
from app.models.basic_data import Specification
from app.models.user import User
from sqlalchemy import text
import uuid

app = create_app()
with app.app_context():
    # 设置租户schema
    db.session.execute(text('SET search_path TO tenant_management, public'))
    
    # 获取一个用户ID作为创建者
    user = User.query.first()
    if user:
        # 创建测试规格数据
        specs = [
            {
                'spec_name': '标准规格A',
                'length': 10.0,
                'width': 500.0,
                'roll': 2.0,
                'description': '标准薄膜规格A',
                'sort_order': 1,
                'created_by': user.id
            },
            {
                'spec_name': '标准规格B',
                'length': 15.0,
                'width': 800.0,
                'roll': 1.5,
                'description': '标准薄膜规格B',
                'sort_order': 2,
                'created_by': user.id
            },
            {
                'spec_name': '大尺寸规格',
                'length': 20.0,
                'width': 1200.0,
                'roll': 1.0,
                'description': '大尺寸薄膜规格',
                'sort_order': 3,
                'created_by': user.id
            }
        ]
        
        for spec_data in specs:
            spec = Specification(**spec_data)
            spec.calculate_area_and_format()
            db.session.add(spec)
        
        db.session.commit()
        print('测试规格数据创建成功')
    else:
        print('未找到用户') 