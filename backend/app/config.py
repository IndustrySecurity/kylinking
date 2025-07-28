import os
from datetime import timedelta


class Config:
    """基础配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://postgres:postgres@localhost:5432/saas_platform')
    
    # Redis配置
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # 多租户配置
    DEFAULT_SCHEMA = 'public'
    SYSTEM_SCHEMA = 'system'
    TENANT_HEADER = 'X-Tenant-ID'
    TENANT_DOMAIN_SUFFIX = os.getenv('TENANT_DOMAIN_SUFFIX', '.saasplatform.com')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI', 'postgresql://postgres:postgres@localhost:5432/saas_platform_test')
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    # 通常在生产环境中设置更短的JWT过期时间
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


# 动态字段配置
class DynamicFieldsConfig:
    """动态字段配置类"""
    
    # 是否启用按模型分表（默认关闭）
    ENABLE_MODEL_PARTITIONING = os.getenv('ENABLE_DYNAMIC_FIELDS_PARTITIONING', 'false').lower() == 'true'
    
    # 分表阈值：当某个模型的数据量超过此值时，建议启用分表
    PARTITIONING_THRESHOLD = int(os.getenv('DYNAMIC_FIELDS_PARTITIONING_THRESHOLD', '100000'))
    
    # 最大字段数限制（每个模型每个页面）
    MAX_FIELDS_PER_PAGE = int(os.getenv('MAX_DYNAMIC_FIELDS_PER_PAGE', '50'))
    
    # 最大页面数限制（每个模型）
    MAX_PAGES_PER_MODEL = int(os.getenv('MAX_PAGES_PER_MODEL', '20'))
    
    # 数据清理配置
    ENABLE_AUTO_CLEANUP = os.getenv('ENABLE_DYNAMIC_FIELDS_AUTO_CLEANUP', 'true').lower() == 'true'
    
    # 清理间隔（天）
    CLEANUP_INTERVAL_DAYS = int(os.getenv('DYNAMIC_FIELDS_CLEANUP_INTERVAL_DAYS', '30'))
    
    @classmethod
    def should_partition_model(cls, model_name, record_count=None):
        """判断是否应该为指定模型启用分表"""
        if not cls.ENABLE_MODEL_PARTITIONING:
            return False
        
        # 如果提供了记录数，检查是否超过阈值
        if record_count and record_count > cls.PARTITIONING_THRESHOLD:
            return True
        
        # 可以根据模型名称规则判断
        high_volume_models = ['customer', 'order', 'product', 'inventory']
        return any(model in model_name.lower() for model in high_volume_models)
    
    @classmethod
    def get_table_name(cls, model_name, base_table='dynamic_field_values'):
        """获取表名，支持分表"""
        if cls.should_partition_model(model_name):
            return f"{base_table}_{model_name}"
        return base_table

# 配置字典，用于根据环境变量选择配置
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 