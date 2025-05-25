import request from '../utils/request';

// 单位管理API
export const unitApi = {
  // 获取单位列表
  getUnits: (params = {}) => {
    return request({
      url: '/tenant/basic-data/units',
      method: 'get',
      params
    });
  },

  // 获取单位详情
  getUnit: (id) => {
    return request({
      url: `/tenant/basic-data/units/${id}`,
      method: 'get'
    });
  },

  // 创建单位
  createUnit: (data) => {
    return request({
      url: '/tenant/basic-data/units',
      method: 'post',
      data
    });
  },

  // 更新单位
  updateUnit: (id, data) => {
    return request({
      url: `/tenant/basic-data/units/${id}`,
      method: 'put',
      data
    });
  },

  // 删除单位
  deleteUnit: (id) => {
    return request({
      url: `/tenant/basic-data/units/${id}`,
      method: 'delete'
    });
  },

  // 批量更新单位
  batchUpdateUnits: (data) => {
    return request({
      url: '/tenant/basic-data/units/batch',
      method: 'put',
      data
    });
  },

  // 获取启用的单位列表（用于下拉选择）
  getEnabledUnits: () => {
    return request({
      url: '/tenant/basic-data/units',
      method: 'get',
      params: { enabled_only: true, per_page: 1000 }
    });
  }
}; 