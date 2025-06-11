import request from '../../utils/request';

// 币别管理API
export const currencyApi = {
  // 获取币别列表
  getCurrencies: (params = {}) => {
    return request({
      url: '/tenant/basic-data/currencies',
      method: 'get',
      params
    });
  },

  // 获取币别详情
  getCurrency: (id) => {
    return request({
      url: `/tenant/basic-data/currencies/${id}`,
      method: 'get'
    });
  },

  // 创建币别
  createCurrency: (data) => {
    return request({
      url: '/tenant/basic-data/currencies',
      method: 'post',
      data
    });
  },

  // 更新币别
  updateCurrency: (id, data) => {
    return request({
      url: `/tenant/basic-data/currencies/${id}`,
      method: 'put',
      data
    });
  },

  // 删除币别
  deleteCurrency: (id) => {
    return request({
      url: `/tenant/basic-data/currencies/${id}`,
      method: 'delete'
    });
  },

  // 设置为本位币
  setBaseCurrency: (id) => {
    return request({
      url: `/tenant/basic-data/currencies/${id}/set-base`,
      method: 'post'
    });
  },

  // 获取启用的币别列表（用于下拉选择）
  getEnabledCurrencies: () => {
    return request({
      url: '/tenant/basic-data/currencies/enabled',
      method: 'get'
    });
  }
}; 