from werkzeug.wsgi import ClosingIterator
from flask import request, g, current_app
import re
from app.utils.tenant_context import TenantContext


class TenantMiddleware:
    """
    多租户中间件，负责在请求前识别租户并设置当前租户上下文
    """
    
    def __init__(self, wsgi_app, app):
        self.wsgi_app = wsgi_app
        self.app = app
        self.tenant_context = TenantContext()
    
    def __call__(self, environ, start_response):
        # 获取请求对象
        with self.app.request_context(environ):
            # 设置默认schema
            g.tenant_id = None
            g.schema_name = current_app.config['DEFAULT_SCHEMA']
            
            # 解析请求头中的租户ID
            tenant_id = request.headers.get(current_app.config['TENANT_HEADER'])
            if tenant_id:
                g.tenant_id = tenant_id
                # 查询数据库获取租户schema
                schema_name = self._get_schema_for_tenant(tenant_id)
                if schema_name:
                    g.schema_name = schema_name
            
            # 如果没有租户ID，尝试从域名解析
            elif not tenant_id and request.host:
                schema_name = self._get_schema_from_domain(request.host)
                if schema_name:
                    g.schema_name = schema_name
            
            # 设置租户上下文
            self.tenant_context.set_schema(g.schema_name)
            
            return self.wsgi_app(environ, start_response)
    
    def _get_schema_for_tenant(self, tenant_id):
        """
        根据租户ID获取schema名称
        :param tenant_id: 租户ID
        :return: schema名称
        """
        # 此处需要在数据库中查询租户信息，但为了避免循环导入，可以使用原生SQL
        # 在实际应用中，可以缓存租户信息以提高性能
        with self.app.app_context():
            from app.extensions import db
            from sqlalchemy import text
            
            try:
                schema_name = None
                sql = text(f"SELECT schema_name FROM {current_app.config['SYSTEM_SCHEMA']}.tenants WHERE id = :tenant_id AND is_active = TRUE")
                result = db.session.execute(sql, {"tenant_id": tenant_id})
                record = result.first()
                
                if record:
                    schema_name = record[0]
                
                return schema_name
            except Exception as e:
                current_app.logger.error(f"Error fetching schema for tenant {tenant_id}: {str(e)}")
                return None
    
    def _get_schema_from_domain(self, domain):
        """
        从域名解析租户schema
        :param domain: 请求域名
        :return: schema名称
        """
        # 检查域名是否符合租户子域名格式
        domain_suffix = current_app.config['TENANT_DOMAIN_SUFFIX']
        if domain.endswith(domain_suffix):
            subdomain = domain[:-len(domain_suffix)]
            # 查询数据库获取租户schema
            with self.app.app_context():
                from app.extensions import db
                from sqlalchemy import text
                
                try:
                    schema_name = None
                    sql = text(f"SELECT schema_name FROM {current_app.config['SYSTEM_SCHEMA']}.tenants WHERE slug = :slug AND is_active = TRUE")
                    result = db.session.execute(sql, {"slug": subdomain})
                    record = result.first()
                    
                    if record:
                        schema_name = record[0]
                    
                    return schema_name
                except Exception as e:
                    current_app.logger.error(f"Error fetching schema for domain {domain}: {str(e)}")
                    return None
        
        return None 