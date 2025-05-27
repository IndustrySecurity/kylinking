import request from '../utils/request';

// 结算方式管理API
export const settlementMethodApi = {
  // 获取结算方式列表
  getSettlementMethods: (params = {}) => {
    return request({
      url: '/tenant/basic-data/settlement-methods',
      method: 'get',
      params
    });
  },

  // 获取结算方式详情
  getSettlementMethod: (id) => {
    return request({
      url: `/tenant/basic-data/settlement-methods/${id}`,
      method: 'get'
    });
  },

  // 创建结算方式
  createSettlementMethod: (data) => {
    return request({
      url: '/tenant/basic-data/settlement-methods',
      method: 'post',
      data
    });
  },

  // 更新结算方式
  updateSettlementMethod: (id, data) => {
    return request({
      url: `/tenant/basic-data/settlement-methods/${id}`,
      method: 'put',
      data
    });
  },

  // 删除结算方式
  deleteSettlementMethod: (id) => {
    return request({
      url: `/tenant/basic-data/settlement-methods/${id}`,
      method: 'delete'
    });
  },

  // 批量更新结算方式
  batchUpdateSettlementMethods: (data) => {
    return request({
      url: '/tenant/basic-data/settlement-methods/batch',
      method: 'put',
      data
    });
  },

  // 获取启用的结算方式列表
  getEnabledSettlementMethods: () => {
    return request({
      url: '/tenant/basic-data/settlement-methods/enabled',
      method: 'get'
    });
  }
}; 