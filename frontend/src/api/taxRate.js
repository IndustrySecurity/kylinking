import request from '../utils/request';

// 税率管理API
export const taxRateApi = {
  // 获取税率列表
  getTaxRates: (params = {}) => {
    return request({
      url: '/tenant/basic-data/tax-rates',
      method: 'get',
      params
    });
  },

  // 获取税率详情
  getTaxRate: (id) => {
    return request({
      url: `/tenant/basic-data/tax-rates/${id}`,
      method: 'get'
    });
  },

  // 创建税率
  createTaxRate: (data) => {
    return request({
      url: '/tenant/basic-data/tax-rates',
      method: 'post',
      data
    });
  },

  // 更新税率
  updateTaxRate: (id, data) => {
    return request({
      url: `/tenant/basic-data/tax-rates/${id}`,
      method: 'put',
      data
    });
  },

  // 删除税率
  deleteTaxRate: (id) => {
    return request({
      url: `/tenant/basic-data/tax-rates/${id}`,
      method: 'delete'
    });
  },

  // 设置为默认税率
  setDefaultTaxRate: (id) => {
    return request({
      url: `/tenant/basic-data/tax-rates/${id}/set-default`,
      method: 'post'
    });
  },

  // 获取启用的税率列表（用于下拉选择）
  getEnabledTaxRates: () => {
    return request({
      url: '/tenant/basic-data/tax-rates/enabled',
      method: 'get'
    });
  }
}; 