import request from '../utils/request';

// 油墨选项管理API
export const inkOptionApi = {
  // 获取油墨选项列表
  getInkOptions: (params = {}) => {
    return request({
      url: '/tenant/basic-data/ink-options',
      method: 'get',
      params
    });
  },

  // 获取油墨选项详情
  getInkOption: (id) => {
    return request({
      url: `/tenant/basic-data/ink-options/${id}`,
      method: 'get'
    });
  },

  // 创建油墨选项
  createInkOption: (data) => {
    return request({
      url: '/tenant/basic-data/ink-options',
      method: 'post',
      data
    });
  },

  // 更新油墨选项
  updateInkOption: (id, data) => {
    return request({
      url: `/tenant/basic-data/ink-options/${id}`,
      method: 'put',
      data
    });
  },

  // 删除油墨选项
  deleteInkOption: (id) => {
    return request({
      url: `/tenant/basic-data/ink-options/${id}`,
      method: 'delete'
    });
  },

  // 批量更新油墨选项
  batchUpdateInkOptions: (data) => {
    return request({
      url: '/tenant/basic-data/ink-options/batch',
      method: 'put',
      data
    });
  },

  // 获取启用的油墨选项列表（用于下拉选择）
  getEnabledInkOptions: () => {
    return request({
      url: '/tenant/basic-data/ink-options',
      method: 'get',
      params: { enabled_only: true, per_page: 1000 }
    });
  }
}; 