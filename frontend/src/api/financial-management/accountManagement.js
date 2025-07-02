import request from '../../utils/request';

// 获取账户列表
export const getAccounts = (params) => {
  return request({
    url: '/tenant/base-archive/financial-management/account-management',
    method: 'get',
    params
  });
};

// 获取启用的账户列表
export const getEnabledAccounts = () => {
  return request({
    url: '/tenant/base-archive/financial-management/account-management/enabled',
    method: 'get'
  });
};

// 获取账户详情
export const getAccountById = (id) => {
  return request({
    url: `/tenant/base-archive/financial-management/account-management/${id}`,
    method: 'get'
  });
};

// 创建账户
export const createAccount = (data) => {
  return request({
    url: '/tenant/base-archive/financial-management/account-management',
    method: 'post',
    data
  });
};

// 更新账户
export const updateAccount = (id, data) => {
  return request({
    url: `/tenant/base-archive/financial-management/account-management/${id}`,
    method: 'put',
    data
  });
};

// 删除账户
export const deleteAccount = (id) => {
  return request({
    url: `/tenant/base-archive/financial-management/account-management/${id}`,
    method: 'delete'
  });
};

// 批量更新账户
export const batchUpdateAccounts = (data) => {
  return request({
    url: '/tenant/base-archive/financial-management/account-management/batch-update',
    method: 'post',
    data
  });
};

// 获取账户选项（用于下拉框）
export const getAccountOptions = () => {
  return request({
    url: '/tenant/base-archive/financial-management/account-management/options',
    method: 'get'
  });
};

// 获取账户余额
export const getAccountBalance = (id) => {
  return request({
    url: `/tenant/base-archive/financial-management/account-management/${id}/balance`,
    method: 'get'
  });
};

export default {
  getAccounts,
  getEnabledAccounts,
  getAccountById,
  createAccount,
  updateAccount,
  deleteAccount,
  batchUpdateAccounts,
  getAccountOptions,
  getAccountBalance
}; 