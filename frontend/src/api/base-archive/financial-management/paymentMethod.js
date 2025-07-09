import request from '../../../utils/request';

// 获取支付方式列表
export const getPaymentMethods = (params) => {
  return request({
    url: '/tenant/base-archive/financial-management/payment-methods',
    method: 'get',
    params
  });
};

// 创建支付方式
export const createPaymentMethod = (data) => {
  return request({
    url: '/tenant/base-archive/financial-management/payment-methods',
    method: 'post',
    data
  });
};

// 更新支付方式
export const updatePaymentMethod = (id, data) => {
  return request({
    url: `/tenant/base-archive/financial-management/payment-methods/${id}`,
    method: 'put',
    data
  });
};

// 删除支付方式
export const deletePaymentMethod = (id) => {
  return request({
    url: `/tenant/base-archive/financial-management/payment-methods/${id}`,
    method: 'delete'
  });
};

// 获取支付方式详情
export const getPaymentMethodById = (id) => {
  return request({
    url: `/tenant/base-archive/financial-management/payment-methods/${id}`,
    method: 'get'
  });
};

// 获取启用的支付方式选项
export const getEnabledPaymentMethods = () => {
  return request({
    url: '/tenant/base-archive/financial-management/payment-methods/enabled',
    method: 'get'
  });
};

// 批量更新支付方式
export const batchUpdatePaymentMethods = (data) => {
  return request({
    url: '/tenant/base-archive/financial-management/payment-methods/batch-update',
    method: 'post',
    data
  });
};

// 获取支付方式选项（用于下拉框）
export const getPaymentMethodOptions = () => {
  return request({
    url: '/tenant/base-archive/financial-management/payment-methods/options',
    method: 'get'
  });
};

// 统一导出API对象
export const paymentMethodApi = {
  getPaymentMethods,
  createPaymentMethod,
  updatePaymentMethod,
  deletePaymentMethod,
  getPaymentMethodById,
  getEnabledPaymentMethods,
  batchUpdatePaymentMethods,
  getPaymentMethodOptions
}; 