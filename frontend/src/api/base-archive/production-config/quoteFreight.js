import request from '../../../utils/request';

// 报价运费管理API
export const quoteFreightApi = {
  // 获取报价运费列表
  getQuoteFreights: (params = {}) => {
    return request({
      url: '/tenant/basic-data/quote-freights/',
      method: 'get',
      params
    });
  },

  // 获取报价运费详情
  getQuoteFreight: (id) => {
    return request({
      url: `/tenant/basic-data/quote-freights/${id}`,
      method: 'get'
    });
  },

  // 创建报价运费
  createQuoteFreight: (data) => {
    return request({
      url: '/tenant/basic-data/quote-freights/',
      method: 'post',
      data
    });
  },

  // 更新报价运费
  updateQuoteFreight: (id, data) => {
    return request({
      url: `/tenant/basic-data/quote-freights/${id}`,
      method: 'put',
      data
    });
  },

  // 删除报价运费
  deleteQuoteFreight: (id) => {
    return request({
      url: `/tenant/basic-data/quote-freights/${id}`,
      method: 'delete'
    });
  },

  // 批量更新报价运费
  batchUpdateQuoteFreights: (data) => {
    return request({
      url: '/tenant/basic-data/quote-freights/batch',
      method: 'put',
      data
    });
  },

  // 获取启用的报价运费列表（用于下拉选择）
  getEnabledQuoteFreights: () => {
    return request({
      url: '/tenant/basic-data/quote-freights',
      method: 'get',
      params: { enabled_only: true, per_page: 1000 }
    });
  }
}; 