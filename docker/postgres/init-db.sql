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
    ('employee:delete', 'Delete employee data')
ON CONFLICT (name) DO NOTHING;

-- Create schema for public access
CREATE SCHEMA IF NOT EXISTS public;

-- Create schema for tenant isolation
CREATE SCHEMA IF NOT EXISTS tenant_management;

-- Set search path
SET search_path TO public, tenant_management;

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