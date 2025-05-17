import { rest } from 'msw';
import { v4 as uuid } from 'uuid';

// Mock data
let tenants = [
  {
    id: uuid(),
    name: '苏州赛尔新材料科技',
    slug: 'suzhou-saier',
    schema_name: 't_suzhou_saier',
    contact_email: 'admin@saier.com',
    contact_phone: '0512-66889900',
    domain: 'saier.kylinking.com',
    is_active: true,
    created_at: '2023-05-15T08:30:00Z',
    updated_at: '2023-05-15T08:30:00Z'
  },
  {
    id: uuid(),
    name: '常州星光新材料',
    slug: 'changzhou-starlight',
    schema_name: 't_changzhou_starlight',
    contact_email: 'info@starlight.com',
    contact_phone: '0519-88776655',
    domain: 'starlight.kylinking.com',
    is_active: true,
    created_at: '2023-06-20T10:15:00Z',
    updated_at: '2023-07-05T14:20:00Z'
  },
  {
    id: uuid(),
    name: '杭州拓普膜业',
    slug: 'hangzhou-topfilm',
    schema_name: 't_hangzhou_topfilm',
    contact_email: 'support@topfilm.com',
    contact_phone: '0571-56784321',
    domain: 'topfilm.kylinking.com',
    is_active: false,
    created_at: '2023-04-10T09:45:00Z',
    updated_at: '2023-08-01T11:30:00Z'
  }
];

// Mock users for the first tenant
let users = [
  {
    id: uuid(),
    tenant_id: tenants[0].id,
    email: 'admin@saier.com',
    first_name: '张',
    last_name: '明',
    is_active: true,
    is_admin: true,
    last_login_at: '2023-08-15T08:30:00Z',
    created_at: '2023-05-15T08:30:00Z',
    updated_at: '2023-08-15T08:30:00Z',
    roles: [
      { id: uuid(), name: '管理员' }
    ]
  },
  {
    id: uuid(),
    tenant_id: tenants[0].id,
    email: 'production@saier.com',
    first_name: '李',
    last_name: '强',
    is_active: true,
    is_admin: false,
    last_login_at: '2023-08-14T10:15:00Z',
    created_at: '2023-05-20T09:00:00Z',
    updated_at: '2023-08-14T10:15:00Z',
    roles: [
      { id: uuid(), name: '生产主管' }
    ]
  },
  {
    id: uuid(),
    tenant_id: tenants[0].id,
    email: 'quality@saier.com',
    first_name: '王',
    last_name: '芳',
    is_active: true,
    is_admin: false,
    last_login_at: '2023-08-10T14:20:00Z',
    created_at: '2023-06-01T11:30:00Z',
    updated_at: '2023-08-10T14:20:00Z',
    roles: [
      { id: uuid(), name: '质检员' }
    ]
  }
];

// Mock roles
const roles = [
  { id: uuid(), tenant_id: tenants[0].id, name: '管理员', description: '系统管理员' },
  { id: uuid(), tenant_id: tenants[0].id, name: '生产主管', description: '生产部门主管' },
  { id: uuid(), tenant_id: tenants[0].id, name: '质检员', description: '质量控制人员' },
  { id: uuid(), tenant_id: tenants[0].id, name: '操作员', description: '设备操作人员' }
];

// Mock API handlers
export const handlers = [
  // 获取租户列表
  rest.get('/admin/tenants', (req, res, ctx) => {
    const page = parseInt(req.url.searchParams.get('page')) || 1;
    const per_page = parseInt(req.url.searchParams.get('per_page')) || 10;
    const name = req.url.searchParams.get('name');
    const active = req.url.searchParams.get('active');
    
    // Filter tenants
    let filteredTenants = [...tenants];
    
    if (name) {
      filteredTenants = filteredTenants.filter(tenant => 
        tenant.name.toLowerCase().includes(name.toLowerCase())
      );
    }
    
    if (active !== null && active !== undefined) {
      const isActive = active === 'true';
      filteredTenants = filteredTenants.filter(tenant => tenant.is_active === isActive);
    }
    
    // Pagination
    const start = (page - 1) * per_page;
    const end = start + per_page;
    const paginatedTenants = filteredTenants.slice(start, end);
    
    return res(
      ctx.status(200),
      ctx.json({
        tenants: paginatedTenants,
        total: filteredTenants.length,
        pages: Math.ceil(filteredTenants.length / per_page),
        page,
        per_page
      })
    );
  }),
  
  // 获取单个租户
  rest.get('/admin/tenants/:id', (req, res, ctx) => {
    const { id } = req.params;
    const tenant = tenants.find(t => t.id === id);
    
    if (!tenant) {
      return res(
        ctx.status(404),
        ctx.json({ message: 'Tenant not found' })
      );
    }
    
    // Count users for this tenant
    const usersCount = users.filter(u => u.tenant_id === id).length;
    const tenantData = { ...tenant, users_count: usersCount };
    
    return res(
      ctx.status(200),
      ctx.json({ tenant: tenantData })
    );
  }),
  
  // 创建租户
  rest.post('/admin/tenants', (req, res, ctx) => {
    const newTenant = {
      id: uuid(),
      ...req.body,
      schema_name: `t_${req.body.slug.replace(/[^a-z0-9_]/g, '_')}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    tenants.push(newTenant);
    
    return res(
      ctx.status(201),
      ctx.json({
        message: 'Tenant created successfully',
        tenant: newTenant
      })
    );
  }),
  
  // 更新租户
  rest.put('/admin/tenants/:id', (req, res, ctx) => {
    const { id } = req.params;
    const tenantIndex = tenants.findIndex(t => t.id === id);
    
    if (tenantIndex === -1) {
      return res(
        ctx.status(404),
        ctx.json({ message: 'Tenant not found' })
      );
    }
    
    tenants[tenantIndex] = {
      ...tenants[tenantIndex],
      ...req.body,
      updated_at: new Date().toISOString()
    };
    
    return res(
      ctx.status(200),
      ctx.json({
        message: 'Tenant updated successfully',
        tenant: tenants[tenantIndex]
      })
    );
  }),
  
  // 停用租户
  rest.delete('/admin/tenants/:id', (req, res, ctx) => {
    const { id } = req.params;
    const tenantIndex = tenants.findIndex(t => t.id === id);
    
    if (tenantIndex === -1) {
      return res(
        ctx.status(404),
        ctx.json({ message: 'Tenant not found' })
      );
    }
    
    tenants[tenantIndex].is_active = false;
    tenants[tenantIndex].updated_at = new Date().toISOString();
    
    return res(
      ctx.status(200),
      ctx.json({ message: 'Tenant deactivated successfully' })
    );
  }),
  
  // 系统统计数据
  rest.get('/admin/stats', (req, res, ctx) => {
    const activeTenants = tenants.filter(t => t.is_active).length;
    const totalUsers = users.length;
    const adminUsers = users.filter(u => u.is_admin).length;
    
    return res(
      ctx.status(200),
      ctx.json({
        stats: {
          tenants: {
            total: tenants.length,
            active: activeTenants
          },
          users: {
            total: totalUsers,
            admin: adminUsers
          }
        }
      })
    );
  }),
  
  // 获取租户用户列表
  rest.get('/admin/tenants/:tenantId/users', (req, res, ctx) => {
    const { tenantId } = req.params;
    const page = parseInt(req.url.searchParams.get('page')) || 1;
    const per_page = parseInt(req.url.searchParams.get('per_page')) || 10;
    const email = req.url.searchParams.get('email');
    const active = req.url.searchParams.get('active');
    
    // Filter users
    let filteredUsers = users.filter(user => user.tenant_id === tenantId);
    
    if (email) {
      filteredUsers = filteredUsers.filter(user => 
        user.email.toLowerCase().includes(email.toLowerCase())
      );
    }
    
    if (active !== null && active !== undefined) {
      const isActive = active === 'true';
      filteredUsers = filteredUsers.filter(user => user.is_active === isActive);
    }
    
    // Pagination
    const start = (page - 1) * per_page;
    const end = start + per_page;
    const paginatedUsers = filteredUsers.slice(start, end);
    
    return res(
      ctx.status(200),
      ctx.json({
        users: paginatedUsers,
        total: filteredUsers.length,
        pages: Math.ceil(filteredUsers.length / per_page),
        page,
        per_page
      })
    );
  }),
  
  // 获取租户角色列表
  rest.get('/admin/tenants/:tenantId/roles', (req, res, ctx) => {
    const { tenantId } = req.params;
    const tenantRoles = roles.filter(role => role.tenant_id === tenantId);
    
    return res(
      ctx.status(200),
      ctx.json({
        roles: tenantRoles
      })
    );
  }),
  
  // 更多API处理程序可以在这里添加...
]; 