import request from '../../utils/request';

// 付款方式管理API
export const paymentMethodApi = {
  // 获取付款方式列表
  getPaymentMethods: (params = {}) => {
    return request({
      url: '/tenant/basic-data/payment-methods',
      method: 'get',
      params
    });
  },

  // 获取启用的付款方式列表
  getEnabledPaymentMethods: () => {
    return request({
      url: '/tenant/basic-data/payment-methods/enabled',
      method: 'get'
    });
  },

  // 获取付款方式详情
  getPaymentMethod: (id) => {
    return request({
      url: `/tenant/basic-data/payment-methods/${id}`,
      method: 'get'
    });
  },

  // 创建付款方式
  createPaymentMethod: (data) => {
    return request({
      url: '/tenant/basic-data/payment-methods',
      method: 'post',
      data
    });
  },

  // 更新付款方式
  updatePaymentMethod: (id, data) => {
    return request({
      url: `/tenant/basic-data/payment-methods/${id}`,
      method: 'put',
      data
    });
  },

  // 删除付款方式
  deletePaymentMethod: (id) => {
    return request({
      url: `/tenant/basic-data/payment-methods/${id}`,
      method: 'delete'
    });
  },

  // 批量更新付款方式
  batchUpdatePaymentMethods: (data) => {
    return request({
      url: '/tenant/basic-data/payment-methods/batch',
      method: 'put',
      data
    });
  }
}; 