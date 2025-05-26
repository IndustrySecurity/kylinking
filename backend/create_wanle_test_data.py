from app import create_app
from app.extensions import db
from app.models.basic_data import Specification
from app.models.user import User
from sqlalchemy import text
import uuid

app = create_app()
with app.app_context():
    # 设置租户schema为wanle
    db.session.execute(text('SET search_path TO wanle, public'))
    
    # 获取一个用户ID作为创建者
    user = User.query.first()
    if user:
        # 创建测试规格数据
        specs = [
            {
                'spec_name': '薄膜规格-小型',
                'length': 8.0,
                'width': 400.0,
                'roll': 2.5,
                'description': '小型薄膜产品规格',
                'sort_order': 1,
                'created_by': user.id
            },
            {
                'spec_name': '薄膜规格-中型',
                'length': 12.0,
                'width': 600.0,
                'roll': 2.0,
                'description': '中型薄膜产品规格',
                'sort_order': 2,
                'created_by': user.id
            },
            {
                'spec_name': '薄膜规格-大型',
                'length': 18.0,
                'width': 900.0,
                'roll': 1.5,
                'description': '大型薄膜产品规格',
                'sort_order': 3,
                'created_by': user.id
            },
            {
                'spec_name': '特殊规格-超宽',
                'length': 25.0,
                'width': 1500.0,
                'roll': 1.0,
                'description': '超宽薄膜特殊规格',
                'sort_order': 4,
                'created_by': user.id
            }
        ]
        
        for spec_data in specs:
            spec = Specification(**spec_data)
            spec.calculate_area_and_format()
            db.session.add(spec)
        
        db.session.commit()
        print('wanle schema 测试规格数据创建成功')
    else:
        print('未找到用户') 