import os
from app import create_app

# 从环境变量获取配置环境名称
env = os.environ.get('FLASK_ENV', 'development')

# 创建应用实例
app = create_app(env)

if __name__ == '__main__':
    # 获取端口
    port = int(os.environ.get('PORT', 5000))
    
    # 运行应用
    app.run(host='0.0.0.0', port=port) 