import request from '../utils/request';

// 获取账户列表
export const getAccounts = (params) => {
  return request({
    url: '/tenant/basic-data/account-management',
    method: 'get',
    params
  });
};

// 获取启用的账户列表
export const getEnabledAccounts = () => {
  return request({
    url: '/tenant/basic-data/account-management/enabled',
    method: 'get'
  });
};

// 获取账户详情
export const getAccount = (id) => {
  return request({
    url: `/tenant/basic-data/account-management/${id}`,
    method: 'get'
  });
};

// 创建账户
export const createAccount = (data) => {
  return request({
    url: '/tenant/basic-data/account-management',
    method: 'post',
    data
  });
};

// 更新账户
export const updateAccount = (id, data) => {
  return request({
    url: `/tenant/basic-data/account-management/${id}`,
    method: 'put',
    data
  });
};

// 删除账户
export const deleteAccount = (id) => {
  return request({
    url: `/tenant/basic-data/account-management/${id}`,
    method: 'delete'
  });
};

// 批量更新账户
export const batchUpdateAccounts = (data) => {
  return request({
    url: '/tenant/basic-data/account-management/batch',
    method: 'put',
    data
  });
};

export default {
  getAccounts,
  getEnabledAccounts,
  getAccount,
  createAccount,
  updateAccount,
  deleteAccount,
  batchUpdateAccounts
}; 