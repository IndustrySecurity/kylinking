-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create public schema for system-wide tables
CREATE SCHEMA IF NOT EXISTS public;

-- Create a schema for the system
CREATE SCHEMA IF NOT EXISTS system;

-- Create a tenant management table in the system schema
CREATE TABLE IF NOT EXISTS system.tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    schema_name VARCHAR(63) NOT NULL UNIQUE,
    domain VARCHAR(255) UNIQUE,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create users table in the system schema
CREATE TABLE IF NOT EXISTS system.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_superadmin BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (tenant_id) REFERENCES system.tenants(id)
);

-- Create roles table in the system schema
CREATE TABLE IF NOT EXISTS system.roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (tenant_id) REFERENCES system.tenants(id),
    UNIQUE(tenant_id, name)
);

-- Create permissions table in the system schema
CREATE TABLE IF NOT EXISTS system.permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create user_roles table in the system schema
CREATE TABLE IF NOT EXISTS system.user_roles (
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES system.users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES system.roles(id) ON DELETE CASCADE
);

-- Create role_permissions table in the system schema
CREATE TABLE IF NOT EXISTS system.role_permissions (
    role_id UUID NOT NULL,
    permission_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES system.roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES system.permissions(id) ON DELETE CASCADE
);

-- Create a function to create a new tenant schema
CREATE OR REPLACE FUNCTION system.create_tenant_schema(tenant_schema VARCHAR(63))
RETURNS VOID AS $$
BEGIN
    -- Create the tenant schema
    EXECUTE 'CREATE SCHEMA IF NOT EXISTS ' || quote_ident(tenant_schema);
    
    -- Create production_plans table
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.production_plans (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        description TEXT,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        status VARCHAR(50) NOT NULL,
        created_by UUID NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    )';
    
    -- Create production_records table
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.production_records (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        plan_id UUID NOT NULL,
        equipment_id UUID NOT NULL,
        start_time TIMESTAMP WITH TIME ZONE NOT NULL,
        end_time TIMESTAMP WITH TIME ZONE,
        quantity NUMERIC(10, 2) NOT NULL,
        status VARCHAR(50) NOT NULL,
        notes TEXT,
        created_by UUID NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    )';
    
    -- Create equipments table
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.equipments (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        code VARCHAR(100) NOT NULL,
        type VARCHAR(100) NOT NULL,
        status VARCHAR(50) NOT NULL,
        purchase_date DATE,
        warranty_expiry_date DATE,
        location VARCHAR(255),
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    )';
    
    -- Create equipment_maintenance table
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.equipment_maintenance (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        equipment_id UUID NOT NULL,
        maintenance_date DATE NOT NULL,
        description TEXT NOT NULL,
        performed_by UUID NOT NULL,
        status VARCHAR(50) NOT NULL,
        cost NUMERIC(10, 2),
        notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    )';
    
    -- Create quality_inspections table
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.quality_inspections (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        production_record_id UUID,
        inspection_date DATE NOT NULL,
        inspector_id UUID NOT NULL,
        result VARCHAR(50) NOT NULL,
        defect_rate NUMERIC(5, 2),
        notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    )';
    
    -- Create inventory_materials table
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.inventory_materials (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        code VARCHAR(100) NOT NULL,
        category VARCHAR(100) NOT NULL,
        unit VARCHAR(50) NOT NULL,
        quantity NUMERIC(10, 2) NOT NULL DEFAULT 0,
        min_quantity NUMERIC(10, 2) NOT NULL DEFAULT 0,
        location VARCHAR(255),
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    )';
    
    -- Create inventory_products table
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.inventory_products (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        code VARCHAR(100) NOT NULL,
        category VARCHAR(100) NOT NULL,
        unit VARCHAR(50) NOT NULL,
        quantity NUMERIC(10, 2) NOT NULL DEFAULT 0,
        min_quantity NUMERIC(10, 2) NOT NULL DEFAULT 0,
        location VARCHAR(255),
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    )';
    
    -- Create departments table
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.departments (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        code VARCHAR(100) NOT NULL,
        manager_id UUID,
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    )';
    
    -- Create employees table
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.employees (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID,
        department_id UUID NOT NULL,
        employee_code VARCHAR(100) NOT NULL,
        position VARCHAR(100),
        hire_date DATE NOT NULL,
        contact_phone VARCHAR(50),
        emergency_contact VARCHAR(255),
        notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    )';
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to automatically create a schema when a new tenant is added
CREATE OR REPLACE FUNCTION system.create_tenant_schema_trigger()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM system.create_tenant_schema(NEW.schema_name);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic schema creation
DROP TRIGGER IF EXISTS create_tenant_schema_trigger ON system.tenants;
CREATE TRIGGER create_tenant_schema_trigger
AFTER INSERT ON system.tenants
FOR EACH ROW
EXECUTE FUNCTION system.create_tenant_schema_trigger();

-- Insert default superadmin user (password: admin123)
-- In a real application, you would generate a secure password hash
INSERT INTO system.users (email, password_hash, first_name, last_name, is_active, is_admin, is_superadmin)
VALUES ('admin@kylinking.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'System', 'Admin', TRUE, TRUE, TRUE)
ON CONFLICT (email) DO NOTHING;

-- Insert some default permissions
INSERT INTO system.permissions (name, description)
VALUES 
    ('tenant:create', 'Create a new tenant'),
    ('tenant:read', 'View tenant details'),
    ('tenant:update', 'Update tenant details'),
    ('tenant:delete', 'Delete/deactivate a tenant'),
    ('user:create', 'Create a new user'),
    ('user:read', 'View user details'),
    ('user:update', 'Update user details'),
    ('user:delete', 'Delete/deactivate a user'),
    ('production:create', 'Create production plans and records'),
    ('production:read', 'View production data'),
    ('production:update', 'Update production data'),
    ('production:delete', 'Delete production data'),
    ('equipment:create', 'Create equipment records'),
    ('equipment:read', 'View equipment data'),
    ('equipment:update', 'Update equipment data'),
    ('equipment:delete', 'Delete equipment data'),
    ('quality:create', 'Create quality inspection records'),
    ('quality:read', 'View quality data'),
    ('quality:update', 'Update quality data'),
    ('quality:delete', 'Delete quality data'),
    ('inventory:create', 'Create inventory records'),
    ('inventory:read', 'View inventory data'),
    ('inventory:update', 'Update inventory data'),
    ('inventory:delete', 'Delete inventory data'),
    ('employee:create', 'Create employee records'),
    ('employee:read', 'View employee data'),
    ('employee:update', 'Update employee data'),
    ('employee:delete', 'Delete employee data'),
    ('module:manage', 'Manage system modules'),
    ('module:configure', 'Configure tenant modules')
ON CONFLICT (name) DO NOTHING;

-- Create schema for public access
CREATE SCHEMA IF NOT EXISTS public;

-- Create schema for tenant isolation
CREATE SCHEMA IF NOT EXISTS tenant_management;

-- Set search path
SET search_path TO public, tenant_management;

-- Create the same tables in public schema to ensure foreign key relationships work
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_superadmin BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.user_roles (
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.role_permissions (
    role_id UUID NOT NULL,
    permission_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE
);

-- Create triggers to sync data from system to public schema
CREATE OR REPLACE FUNCTION sync_system_to_public()
RETURNS TRIGGER AS $$
BEGIN
    -- For users
    IF TG_TABLE_NAME = 'users' THEN
        INSERT INTO public.users (id, tenant_id, email, password_hash, first_name, last_name, 
                                is_active, is_admin, is_superadmin, last_login_at, created_at, updated_at)
        VALUES (NEW.id, NEW.tenant_id, NEW.email, NEW.password_hash, NEW.first_name, NEW.last_name, 
               NEW.is_active, NEW.is_admin, NEW.is_superadmin, NEW.last_login_at, NEW.created_at, NEW.updated_at)
        ON CONFLICT (id) DO UPDATE SET
            tenant_id = NEW.tenant_id,
            email = NEW.email,
            password_hash = NEW.password_hash,
            first_name = NEW.first_name,
            last_name = NEW.last_name,
            is_active = NEW.is_active,
            is_admin = NEW.is_admin,
            is_superadmin = NEW.is_superadmin,
            last_login_at = NEW.last_login_at,
            updated_at = NEW.updated_at;
    
    -- For roles
    ELSIF TG_TABLE_NAME = 'roles' THEN
        INSERT INTO public.roles (id, tenant_id, name, description, created_at, updated_at)
        VALUES (NEW.id, NEW.tenant_id, NEW.name, NEW.description, NEW.created_at, NEW.updated_at)
        ON CONFLICT (id) DO UPDATE SET
            tenant_id = NEW.tenant_id,
            name = NEW.name,
            description = NEW.description,
            updated_at = NEW.updated_at;
    
    -- For permissions
    ELSIF TG_TABLE_NAME = 'permissions' THEN
        INSERT INTO public.permissions (id, name, description, created_at, updated_at)
        VALUES (NEW.id, NEW.name, NEW.description, NEW.created_at, NEW.updated_at)
        ON CONFLICT (id) DO UPDATE SET
            name = NEW.name,
            description = NEW.description,
            updated_at = NEW.updated_at;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for syncing data
CREATE TRIGGER sync_users_to_public
AFTER INSERT OR UPDATE ON system.users
FOR EACH ROW
EXECUTE FUNCTION sync_system_to_public();

CREATE TRIGGER sync_roles_to_public
AFTER INSERT OR UPDATE ON system.roles
FOR EACH ROW
EXECUTE FUNCTION sync_system_to_public();

CREATE TRIGGER sync_permissions_to_public
AFTER INSERT OR UPDATE ON system.permissions
FOR EACH ROW
EXECUTE FUNCTION sync_system_to_public();

-- Initialize public tables with existing data from system schema
INSERT INTO public.users (id, tenant_id, email, password_hash, first_name, last_name, 
                        is_active, is_admin, is_superadmin, last_login_at, created_at, updated_at)
SELECT id, tenant_id, email, password_hash, first_name, last_name, 
       is_active, is_admin, is_superadmin, last_login_at, created_at, updated_at
FROM system.users
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.roles (id, tenant_id, name, description, created_at, updated_at)
SELECT id, tenant_id, name, description, created_at, updated_at
FROM system.roles
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.permissions (id, name, description, created_at, updated_at)
SELECT id, name, description, created_at, updated_at
FROM system.permissions
ON CONFLICT (id) DO NOTHING;

-- Create tenant management tables
CREATE TABLE IF NOT EXISTS tenant_management.tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    schema_name VARCHAR(100) NOT NULL UNIQUE,
    domain VARCHAR(255) UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    max_users INTEGER NOT NULL DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE TABLE IF NOT EXISTS tenant_management.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant_management.tenants(id),
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_role CHECK (role IN ('admin', 'manager', 'user')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE TABLE IF NOT EXISTS tenant_management.roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant_management.tenants(id),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, name)
);

CREATE TABLE IF NOT EXISTS tenant_management.user_roles (
    user_id UUID NOT NULL REFERENCES tenant_management.users(id),
    role_id UUID NOT NULL REFERENCES tenant_management.roles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tenants_schema_name ON tenant_management.tenants(schema_name);
CREATE INDEX IF NOT EXISTS idx_tenants_domain ON tenant_management.tenants(domain);
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON tenant_management.users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON tenant_management.users(email);
CREATE INDEX IF NOT EXISTS idx_roles_tenant_id ON tenant_management.roles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON tenant_management.user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON tenant_management.user_roles(role_id);

-- Create functions
CREATE OR REPLACE FUNCTION tenant_management.create_tenant_schema(schema_name VARCHAR)
RETURNS VOID AS $$
BEGIN
    EXECUTE 'CREATE SCHEMA IF NOT EXISTS ' || quote_ident(schema_name);
    
    -- Create tenant-specific tables
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(schema_name) || '.users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        username VARCHAR(50) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100),
        role VARCHAR(20) NOT NULL DEFAULT ''user'',
        status VARCHAR(20) NOT NULL DEFAULT ''active'',
        last_login TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT valid_role CHECK (role IN (''admin'', ''manager'', ''user'')),
        CONSTRAINT valid_status CHECK (status IN (''active'', ''inactive'', ''suspended''))
    )';
    
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(schema_name) || '.roles (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(50) NOT NULL,
        description TEXT,
        permissions JSONB NOT NULL DEFAULT ''{}'',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(name)
    )';
    
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(schema_name) || '.user_roles (
        user_id UUID NOT NULL REFERENCES ' || quote_ident(schema_name) || '.users(id),
        role_id UUID NOT NULL REFERENCES ' || quote_ident(schema_name) || '.roles(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, role_id)
    )';
    
    -- Create indexes
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_users_email ON ' || quote_ident(schema_name) || '.users(email)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_roles_name ON ' || quote_ident(schema_name) || '.roles(name)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON ' || quote_ident(schema_name) || '.user_roles(user_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON ' || quote_ident(schema_name) || '.user_roles(role_id)';
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE OR REPLACE FUNCTION tenant_management.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenant_management.tenants
    FOR EACH ROW
    EXECUTE FUNCTION tenant_management.update_updated_at();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON tenant_management.users
    FOR EACH ROW
    EXECUTE FUNCTION tenant_management.update_updated_at();

CREATE TRIGGER update_roles_updated_at
    BEFORE UPDATE ON tenant_management.roles
    FOR EACH ROW
    EXECUTE FUNCTION tenant_management.update_updated_at();

-- Create default admin user
INSERT INTO tenant_management.tenants (name, schema_name, domain, status, max_users)
VALUES ('System', 'public', 'www.kylinking.com', 'active', 1000)
ON CONFLICT (schema_name) DO NOTHING;

DO $$
DECLARE
    system_tenant_id UUID;
BEGIN
    SELECT id INTO system_tenant_id FROM tenant_management.tenants WHERE schema_name = 'public';
    
    INSERT INTO tenant_management.users (tenant_id, username, email, password_hash, full_name, role, status)
    VALUES (
        system_tenant_id,
        'admin',
        'admin@kylinking.com',
        crypt('admin123', gen_salt('bf')),
        'System Administrator',
        'admin',
        'active'
    )
    ON CONFLICT (email) DO NOTHING;
END;
$$; 

-- Create tenant module management tables
-- 系统模块表
CREATE TABLE IF NOT EXISTS system.system_modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    version VARCHAR(20) DEFAULT '1.0.0',
    icon VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    is_core BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    dependencies JSONB DEFAULT '[]',
    default_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 模块字段表
CREATE TABLE IF NOT EXISTS system.module_fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID NOT NULL REFERENCES system.system_modules(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    description TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    is_system_field BOOLEAN DEFAULT FALSE,
    is_configurable BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    validation_rules JSONB DEFAULT '{}',
    field_options JSONB DEFAULT '{}',
    default_value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(module_id, field_name)
);

-- 租户模块配置表
CREATE TABLE IF NOT EXISTS system.tenant_modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES system.tenants(id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES system.system_modules(id) ON DELETE CASCADE,
    is_enabled BOOLEAN DEFAULT TRUE,
    is_visible BOOLEAN DEFAULT TRUE,
    custom_config JSONB DEFAULT '{}',
    custom_permissions JSONB DEFAULT '{}',
    configured_by UUID REFERENCES system.users(id),
    configured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, module_id)
);

-- 租户字段配置表
CREATE TABLE IF NOT EXISTS system.tenant_field_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES system.tenants(id) ON DELETE CASCADE,
    field_id UUID NOT NULL REFERENCES system.module_fields(id) ON DELETE CASCADE,
    is_enabled BOOLEAN DEFAULT TRUE,
    is_visible BOOLEAN DEFAULT TRUE,
    is_required BOOLEAN DEFAULT FALSE,
    is_readonly BOOLEAN DEFAULT FALSE,
    custom_label VARCHAR(255),
    custom_placeholder VARCHAR(255),
    custom_help_text TEXT,
    custom_validation_rules JSONB DEFAULT '{}',
    custom_options JSONB DEFAULT '{}',
    custom_default_value JSONB,
    display_order INTEGER DEFAULT 0,
    column_width INTEGER,
    field_group VARCHAR(100),
    configured_by UUID REFERENCES system.users(id),
    configured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, field_id)
);

-- 租户扩展表
CREATE TABLE IF NOT EXISTS system.tenant_extensions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES system.tenants(id) ON DELETE CASCADE,
    extension_type VARCHAR(100) NOT NULL,
    extension_name VARCHAR(255) NOT NULL,
    extension_key VARCHAR(100) NOT NULL,
    extension_config JSONB DEFAULT '{}',
    extension_schema JSONB DEFAULT '{}',
    extension_metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    module_id UUID REFERENCES system.system_modules(id),
    created_by UUID REFERENCES system.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, extension_key)
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_system_modules_category ON system.system_modules(category);
CREATE INDEX IF NOT EXISTS idx_system_modules_is_active ON system.system_modules(is_active);
CREATE INDEX IF NOT EXISTS idx_module_fields_module_id ON system.module_fields(module_id);
CREATE INDEX IF NOT EXISTS idx_tenant_modules_tenant_id ON system.tenant_modules(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_modules_module_id ON system.tenant_modules(module_id);
CREATE INDEX IF NOT EXISTS idx_tenant_field_configs_tenant_id ON system.tenant_field_configs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_field_configs_field_id ON system.tenant_field_configs(field_id);
CREATE INDEX IF NOT EXISTS idx_tenant_extensions_tenant_id ON system.tenant_extensions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_extensions_module_id ON system.tenant_extensions(module_id);

-- 创建触发器自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_system_modules_updated_at BEFORE UPDATE ON system.system_modules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_module_fields_updated_at BEFORE UPDATE ON system.module_fields FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tenant_modules_updated_at BEFORE UPDATE ON system.tenant_modules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tenant_field_configs_updated_at BEFORE UPDATE ON system.tenant_field_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tenant_extensions_updated_at BEFORE UPDATE ON system.tenant_extensions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 基础档案管理表结构 (在租户schema中创建)
-- 这些表将在每个租户的schema中创建

-- Function to create basic data tables in tenant schema
CREATE OR REPLACE FUNCTION system.create_basic_data_tables(tenant_schema VARCHAR(63))
RETURNS VOID AS $$
BEGIN
    -- 客户分类表
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.customer_categories (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        category_code VARCHAR(50) NOT NULL UNIQUE,
        category_name VARCHAR(100) NOT NULL,
        parent_id UUID REFERENCES ' || quote_ident(tenant_schema) || '.customer_categories(id),
        level INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )';

    -- 客户档案表
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.customers (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        customer_code VARCHAR(50) NOT NULL UNIQUE,
        customer_name VARCHAR(200) NOT NULL,
        customer_type VARCHAR(20) DEFAULT ''enterprise'',
        category_id UUID REFERENCES ' || quote_ident(tenant_schema) || '.customer_categories(id),
        
        -- 基本信息
        legal_name VARCHAR(200),
        unified_credit_code VARCHAR(50),
        tax_number VARCHAR(50),
        industry VARCHAR(100),
        scale VARCHAR(20),
        
        -- 联系信息
        contact_person VARCHAR(100),
        contact_phone VARCHAR(50),
        contact_email VARCHAR(100),
        contact_address TEXT,
        postal_code VARCHAR(20),
        
        -- 业务信息
        credit_limit DECIMAL(15,2) DEFAULT 0,
        payment_terms INTEGER DEFAULT 30,
        currency VARCHAR(10) DEFAULT ''CNY'',
        price_level VARCHAR(20) DEFAULT ''standard'',
        sales_person_id UUID,
        
        -- 系统字段
        status VARCHAR(20) DEFAULT ''active'',
        is_approved BOOLEAN DEFAULT FALSE,
        approved_by UUID,
        approved_at TIMESTAMP WITH TIME ZONE,
        
        -- 租户模块配置支持
        custom_fields JSONB DEFAULT ''{}'',
        
        -- 审计字段
        created_by UUID NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_by UUID,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT customers_status_check CHECK (status IN (''active'', ''inactive'', ''pending'')),
        CONSTRAINT customers_type_check CHECK (customer_type IN (''enterprise'', ''individual''))
    )';

    -- 供应商分类表
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.supplier_categories (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        category_code VARCHAR(50) NOT NULL UNIQUE,
        category_name VARCHAR(100) NOT NULL,
        parent_id UUID REFERENCES ' || quote_ident(tenant_schema) || '.supplier_categories(id),
        level INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )';

    -- 供应商档案表
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.suppliers (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        supplier_code VARCHAR(50) NOT NULL UNIQUE,
        supplier_name VARCHAR(200) NOT NULL,
        supplier_type VARCHAR(20) DEFAULT ''material'',
        category_id UUID REFERENCES ' || quote_ident(tenant_schema) || '.supplier_categories(id),
        
        -- 基本信息
        legal_name VARCHAR(200),
        unified_credit_code VARCHAR(50),
        business_license VARCHAR(50),
        industry VARCHAR(100),
        established_date DATE,
        
        -- 联系信息
        contact_person VARCHAR(100),
        contact_phone VARCHAR(50),
        contact_email VARCHAR(100),
        office_address TEXT,
        factory_address TEXT,
        
        -- 业务信息
        payment_terms INTEGER DEFAULT 30,
        currency VARCHAR(10) DEFAULT ''CNY'',
        quality_level VARCHAR(20) DEFAULT ''qualified'',
        cooperation_level VARCHAR(20) DEFAULT ''ordinary'',
        
        -- 评估信息
        quality_score DECIMAL(3,1) DEFAULT 0,
        delivery_score DECIMAL(3,1) DEFAULT 0,
        service_score DECIMAL(3,1) DEFAULT 0,
        price_score DECIMAL(3,1) DEFAULT 0,
        overall_score DECIMAL(3,1) DEFAULT 0,
        
        -- 系统字段
        status VARCHAR(20) DEFAULT ''active'',
        is_approved BOOLEAN DEFAULT FALSE,
        approved_by UUID,
        approved_at TIMESTAMP WITH TIME ZONE,
        
        custom_fields JSONB DEFAULT ''{}'',
        
        created_by UUID NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_by UUID,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT suppliers_status_check CHECK (status IN (''active'', ''inactive'', ''pending'')),
        CONSTRAINT suppliers_type_check CHECK (supplier_type IN (''material'', ''service'', ''both'')),
        CONSTRAINT suppliers_quality_check CHECK (quality_level IN (''excellent'', ''good'', ''qualified'', ''poor'')),
        CONSTRAINT suppliers_cooperation_check CHECK (cooperation_level IN (''strategic'', ''important'', ''ordinary''))
    )';

    -- 产品分类表
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.product_categories (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        category_code VARCHAR(50) NOT NULL UNIQUE,
        category_name VARCHAR(100) NOT NULL,
        parent_id UUID REFERENCES ' || quote_ident(tenant_schema) || '.product_categories(id),
        level INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )';

    -- 产品档案表
    EXECUTE 'CREATE TABLE IF NOT EXISTS ' || quote_ident(tenant_schema) || '.products (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        product_code VARCHAR(50) NOT NULL UNIQUE,
        product_name VARCHAR(200) NOT NULL,
        product_type VARCHAR(20) DEFAULT ''finished'',
        category_id UUID REFERENCES ' || quote_ident(tenant_schema) || '.product_categories(id),
        
        -- 基本信息
        short_name VARCHAR(100),
        english_name VARCHAR(200),
        brand VARCHAR(100),
        model VARCHAR(100),
        specification TEXT,
        
        -- 技术参数 (薄膜产品特有)
        thickness DECIMAL(8,3),
        width DECIMAL(8,2),
        length DECIMAL(10,2),
        material_type VARCHAR(100),
        transparency DECIMAL(5,2),
        tensile_strength DECIMAL(8,2),
        
        -- 包装信息
        base_unit VARCHAR(20) DEFAULT ''m²'',
        package_unit VARCHAR(20),
        conversion_rate DECIMAL(10,4) DEFAULT 1,
        net_weight DECIMAL(10,3),
        gross_weight DECIMAL(10,3),
        
        -- 价格信息
        standard_cost DECIMAL(15,4),
        standard_price DECIMAL(15,4),
        currency VARCHAR(10) DEFAULT ''CNY'',
        
        -- 库存信息
        safety_stock DECIMAL(15,3) DEFAULT 0,
        min_order_qty DECIMAL(15,3) DEFAULT 1,
        max_order_qty DECIMAL(15,3),
        
        -- 生产信息
        lead_time INTEGER DEFAULT 0,
        shelf_life INTEGER,
        storage_condition VARCHAR(200),
        
        -- 质量标准
        quality_standard VARCHAR(200),
        inspection_method VARCHAR(200),
        
        -- 系统字段
        status VARCHAR(20) DEFAULT ''active'',
        is_sellable BOOLEAN DEFAULT TRUE,
        is_purchasable BOOLEAN DEFAULT TRUE,
        is_producible BOOLEAN DEFAULT TRUE,
        
        custom_fields JSONB DEFAULT ''{}'',
        
        created_by UUID NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_by UUID,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT products_status_check CHECK (status IN (''active'', ''inactive'', ''pending'')),
        CONSTRAINT products_type_check CHECK (product_type IN (''finished'', ''semi'', ''material''))
    )';

    -- 创建索引
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_customer_categories_parent ON ' || quote_ident(tenant_schema) || '.customer_categories(parent_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_customers_category ON ' || quote_ident(tenant_schema) || '.customers(category_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_customers_status ON ' || quote_ident(tenant_schema) || '.customers(status)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_customers_code ON ' || quote_ident(tenant_schema) || '.customers(customer_code)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_customers_name ON ' || quote_ident(tenant_schema) || '.customers(customer_name)';
    
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_supplier_categories_parent ON ' || quote_ident(tenant_schema) || '.supplier_categories(parent_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_suppliers_category ON ' || quote_ident(tenant_schema) || '.suppliers(category_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_suppliers_status ON ' || quote_ident(tenant_schema) || '.suppliers(status)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_suppliers_code ON ' || quote_ident(tenant_schema) || '.suppliers(supplier_code)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_suppliers_name ON ' || quote_ident(tenant_schema) || '.suppliers(supplier_name)';
    
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_product_categories_parent ON ' || quote_ident(tenant_schema) || '.product_categories(parent_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_products_category ON ' || quote_ident(tenant_schema) || '.products(category_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_products_status ON ' || quote_ident(tenant_schema) || '.products(status)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_products_code ON ' || quote_ident(tenant_schema) || '.products(product_code)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_products_name ON ' || quote_ident(tenant_schema) || '.products(product_name)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_products_type ON ' || quote_ident(tenant_schema) || '.products(product_type)';

END;
$$ LANGUAGE plpgsql;

-- 索引创建
CREATE INDEX IF NOT EXISTS idx_system_modules_name ON system.system_modules(name);
CREATE INDEX IF NOT EXISTS idx_system_modules_category ON system.system_modules(category);
CREATE INDEX IF NOT EXISTS idx_module_fields_module_id ON system.module_fields(module_id);
CREATE INDEX IF NOT EXISTS idx_tenant_modules_tenant_id ON system.tenant_modules(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_modules_module_id ON system.tenant_modules(module_id);
CREATE INDEX IF NOT EXISTS idx_tenant_field_configs_tenant_id ON system.tenant_field_configs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_field_configs_field_id ON system.tenant_field_configs(field_id);
CREATE INDEX IF NOT EXISTS idx_tenant_extensions_tenant_id ON system.tenant_extensions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_extensions_module_id ON system.tenant_extensions(module_id);

-- 为现有租户创建基础档案表
SELECT system.create_basic_data_tables('wanle'); 