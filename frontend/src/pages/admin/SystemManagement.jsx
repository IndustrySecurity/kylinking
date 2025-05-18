import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Tabs, 
  Button, 
  Select, 
  Space, 
  message, 
  Typography, 
  Spin,
  Alert
} from 'antd';
import { PlusOutlined, ReloadOutlined, SettingOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../../hooks/useApi';

// Tab components
import UserManagement from './system/UserManagement';
import RoleManagement from './system/RoleManagement';
import PermissionManagement from './system/PermissionManagement';
import OrganizationManagement from './system/OrganizationManagement';

const { Title, Text } = Typography;
const { Option } = Select;

const SystemManagement = () => {
  const navigate = useNavigate();
  const api = useApi();
  const [activeKey, setActiveKey] = useState("users");
  const [tenants, setTenants] = useState([]);
  const [selectedTenant, setSelectedTenant] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userRole, setUserRole] = useState(null);
  
  // Direct state initialization from localStorage if available
  useEffect(() => {
    // Try to immediately initialize state from localStorage to avoid flicker
    const userFromStorage = api.getUser();
    if (userFromStorage) {
      setUserRole({
        isSuperAdmin: userFromStorage.is_superadmin,
        isAdmin: userFromStorage.is_admin,
        tenantId: userFromStorage.tenant_id
      });
      
      // If user is tenant admin, try to create tenant data directly 
      if (!userFromStorage.is_superadmin && userFromStorage.is_admin && userFromStorage.tenant_id) {
        // Try to get tenant from localStorage
        const storedTenant = localStorage.getItem('tenant');
        if (storedTenant) {
          try {
            const parsedTenant = JSON.parse(storedTenant);
            // Add the ID if not present
            if (!parsedTenant.id && userFromStorage.tenant_id) {
              parsedTenant.id = userFromStorage.tenant_id;
            }
            setSelectedTenant(parsedTenant);
          } catch (e) {
            console.error("Failed to parse tenant from localStorage:", e);
          }
        }
      }
    }
  }, [api]);

  // Fetch user role and tenants on component mount
  useEffect(() => {
    // Save a reference to determine if the component is still mounted when async operations complete
    let isMounted = true;
    let fetchAttempts = 0;
    const maxAttempts = 3;
    
    const fetchUserRoleAndTenants = async () => {
      if (loading) return; // Prevent concurrent fetches
      
      fetchAttempts++;
      setLoading(true);
      try {
        // Get user info from context or API call if needed
        let userInfo = api.getUser();
        
        // Log debugging info about user
        console.log("User from API context:", userInfo);
        
        // If user info isn't in context, try getting it from an API call
        if (!userInfo) {
          try {
            console.log("User not in context, trying API call");
            const userResponse = await api.get('/api/auth/me');
            userInfo = userResponse.data.user;
            console.log("User from API call:", userInfo);
          } catch (authError) {
            console.error("Failed to get user from API:", authError);
            throw new Error("User authentication failed");
          }
        }
        
        if (!userInfo) {
          throw new Error("User information not available");
        }
        
        if (isMounted) {
          // Log user role data being set
          console.log("Setting user role with data:", {
            isSuperAdmin: userInfo.is_superadmin,
            isAdmin: userInfo.is_admin,
            tenantId: userInfo.tenant_id
          });
          
          setUserRole({
            isSuperAdmin: userInfo.is_superadmin,
            isAdmin: userInfo.is_admin,
            tenantId: userInfo.tenant_id
          });
        }

        // If superadmin, fetch all tenants to allow selection
        if (userInfo.is_superadmin) {
          console.log("User is superadmin, fetching all tenants");
          const tenantResponse = await api.get('/api/admin/tenants');
          console.log("Tenants response:", tenantResponse.data);
          if (isMounted) {
            setTenants(tenantResponse.data.tenants || []);
          }
        } else if (userInfo.is_admin && userInfo.tenant_id) {
          // For tenant admin, only set their own tenant
          console.log("User is tenant admin, fetching tenant:", userInfo.tenant_id);
          try {
            const tenantResponse = await api.get(`/api/admin/tenants/${userInfo.tenant_id}`);
            console.log("Tenant response:", tenantResponse.data);
            
            // Check if the response has the expected structure
            if (tenantResponse.data && tenantResponse.data.tenant) {
              console.log("Setting selected tenant:", tenantResponse.data.tenant);
              if (isMounted) {
                setSelectedTenant(tenantResponse.data.tenant);
              }
            } else {
              // If the tenant data isn't in the expected format, try to use it directly
              console.log("Tenant data not in expected format, trying direct data");
              if (tenantResponse.data) {
                if (isMounted) {
                  setSelectedTenant(tenantResponse.data);
                }
              } else {
                throw new Error("No tenant data in response");
              }
            }
          } catch (tenantError) {
            console.error("Error fetching tenant:", tenantError);
            if (isMounted) {
              message.error("Failed to load tenant information");
            }
          }
        }
              } catch (error) {
          console.error("Error fetching user role or tenants:", error);
          
          // Check if we should retry
          if (fetchAttempts < maxAttempts && isMounted) {
            console.log(`Retry attempt ${fetchAttempts} of ${maxAttempts}`);
            setTimeout(() => {
              if (isMounted) {
                setLoading(false);
                fetchUserRoleAndTenants();
              }
            }, 1000); // Wait 1 second before retrying
            return;
          }
          
          if (isMounted) {
            message.error("Failed to load user information");
            // Only redirect if we have no user information at all
            if (!userRole) {
              navigate('/');
            }
          }
        } finally {
          if (isMounted) {
            setLoading(false);
          }
        }
      };

      fetchUserRoleAndTenants();
      
      // Add window event listener for online/offline status
      const handleOnline = () => {
        console.log("Connection restored, refreshing data");
        if (isMounted && !loading) {
          fetchUserRoleAndTenants();
        }
      };
      
      window.addEventListener('online', handleOnline);
      
      // Cleanup function to prevent state updates after unmount
      return () => {
        isMounted = false;
        window.removeEventListener('online', handleOnline);
      };
    }, [navigate, api, userRole]); // Include userRole to prevent unnecessary redirects

  // Handle tenant change for superadmin
  const handleTenantChange = (tenantId) => {
    if (!tenantId) {
      setSelectedTenant(null);
      return;
    }
    const tenant = tenants.find(t => t.id === tenantId);
    if (tenant) {
      setSelectedTenant(tenant);
    }
  };

  // Only show loading spinner on initial load when no data is available
  if (loading && !userRole && !selectedTenant) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
        <Spin size="large" />
      </div>
    );
  }

  // If not admin or superadmin, show access denied
  if (userRole && !userRole.isAdmin && !userRole.isSuperAdmin) {
    return (
      <Alert
        message="Access Denied"
        description="You do not have permission to access this page."
        type="error"
        showIcon
      />
    );
  }
  
  // Manual tenant loading option for admins if tenant failed to load
  const forceLoadTenant = () => {
    const tenantInfo = userRole?.tenantId ? {
      id: userRole.tenantId,
      name: '您的租户',  // Default name if we don't have it
      is_active: true,
      // Add other required properties that might be used by child components
      contact_email: userRole?.email || '',
      schema_name: `tenant_${userRole.tenantId.substring(0, 8)}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    } : null;
    
    if (tenantInfo) {
      console.log("Forcing tenant data:", tenantInfo);
      
      // Store in localStorage for future use
      localStorage.setItem('tenant', JSON.stringify(tenantInfo));
      
      // Update component state
      setSelectedTenant(tenantInfo);
      
      // Show success message
      message.success('租户信息已手动加载，系统管理功能已启用');
    }
  };

  // Debug information
  console.log("SystemManagement render state:", {
    userRole,
    selectedTenant,
    tenantsLoaded: tenants.length > 0
  });
  
  return (
    <div className="system-management">
      <Card>
        {/* Debug panel - only visible in development */}
        {process.env.NODE_ENV !== 'production' && (
          <div style={{ marginBottom: '20px', padding: '10px', background: '#fffbe6', border: '1px solid #ffe58f' }}>
            <Title level={5}>Debug Info</Title>
            <pre style={{ whiteSpace: 'pre-wrap' }}>
              {JSON.stringify({
                auth: {
                  token: localStorage.getItem('token') ? 'exists' : 'missing',
                  user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
                  tenant: localStorage.getItem('tenant') ? JSON.parse(localStorage.getItem('tenant')) : null
                },
                component: {
                  userRole,
                  selectedTenant,
                  tenantsLoaded: tenants.length > 0
                }
              }, null, 2)}
            </pre>
            <Button onClick={() => window.location.reload()} type="primary" size="small">
              刷新页面
            </Button>
          </div>
        )}
        
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
            <Title level={4}>
              系统管理
              {selectedTenant ? ` - ${selectedTenant.name}` : 
               userRole?.isAdmin && !userRole?.isSuperAdmin ? ' - 系统配置' : ''}
            </Title>
            <div>
              <Text type="secondary">租户专用管理模块，包含用户、角色、权限和组织管理</Text>
            </div>
            
            {/* Tenant selector for superadmin */}
            {userRole?.isSuperAdmin && (
              <Select
                showSearch
                style={{ width: 300 }}
                placeholder="选择租户"
                optionFilterProp="children"
                onChange={handleTenantChange}
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                }
              >
                {tenants.map(tenant => (
                  <Option key={tenant.id} value={tenant.id}>{tenant.name}</Option>
                ))}
              </Select>
            )}
          </div>

          {/* Status alerts */}
          {userRole === null && !loading && (
            <Alert
              message="用户权限加载失败"
              description="无法确定您的用户权限。请刷新页面或联系系统管理员。"
              type="error"
              showIcon
            />
          )}
          
          {/* Display message if no tenant is selected for superadmin */}
          {userRole?.isSuperAdmin && !selectedTenant && (
            <Alert
              message="请选择租户"
              description="系统管理模块用于管理租户内的用户、角色、权限和组织结构。请先选择一个租户，然后进行系统管理操作。"
              type="info"
              showIcon
            />
          )}
          
          {/* We've removed the manual loading UI since we're now showing tabs automatically */}

          {/* Tabs will be shown for tenant admins even if tenant data isn't fully loaded */}
          {(selectedTenant || (userRole?.isAdmin && !userRole?.isSuperAdmin)) && (
            <div>
              {/* Create a provisional tenant object if selectedTenant is null but we have a tenant ID */}
              {(() => {
                const useTenant = selectedTenant || (userRole?.tenantId ? {
                  id: userRole.tenantId,
                  name: '当前租户',
                  is_active: true,
                  contact_email: '',
                  schema_name: '',
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString()
                } : null);
                
                return (
                  <Tabs 
                    activeKey={activeKey} 
                    onChange={setActiveKey}
                    items={[
                      {
                        key: 'users',
                        label: '用户管理',
                        children: (
                          <div>
                            {/* 用户管理作为系统管理的一部分，取代了独立的用户管理页面 */}
                            <UserManagement tenant={useTenant} userRole={userRole} />
                          </div>
                        )
                      },
                      {
                        key: 'roles',
                        label: '角色管理',
                        children: <RoleManagement tenant={useTenant} userRole={userRole} />
                      },
                      {
                        key: 'permissions',
                        label: '权限管理',
                        children: <PermissionManagement tenant={useTenant} userRole={userRole} />
                      },
                      {
                        key: 'organizations',
                        label: '组织管理',
                        children: <OrganizationManagement tenant={useTenant} userRole={userRole} />
                      }
                    ]}
                  />
                );
              })()}
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default SystemManagement; 