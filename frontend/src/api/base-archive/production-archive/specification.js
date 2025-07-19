import request from '../../../utils/request';

// 规格管理API
export const specificationApi = {
  // 获取规格列表
  getSpecifications: (params = {}) => {
    return request({
      url: '/tenant/base-archive/production-archive/specifications/',
      method: 'get',
      params
    });
  },

  // 获取规格详情
  getSpecification: (id) => {
    return request({
      url: `/tenant/base-archive/production-archive/specifications/${id}`,
      method: 'get'
    });
  },

  // 创建规格
  createSpecification: (data) => {
    return request({
      url: '/tenant/base-archive/production-archive/specifications/',
      method: 'post',
      data
    });
  },

  // 更新规格
  updateSpecification: (id, data) => {
    return request({
      url: `/tenant/base-archive/production-archive/specifications/${id}`,
      method: 'put',
      data
    });
  },

  // 删除规格
  deleteSpecification: (id) => {
    return request({
      url: `/tenant/base-archive/production-archive/specifications/${id}`,
      method: 'delete'
    });
  },

  // 批量更新规格
  batchUpdateSpecifications: (data) => {
    return request({
      url: '/tenant/base-archive/production-archive/specifications/batch',
      method: 'put',
      data
    });
  },

  // 获取启用的规格列表（用于下拉选择）
  getEnabledSpecifications: () => {
    return request({
      url: '/tenant/base-archive/production-archive/specifications',
      method: 'get',
      params: { enabled_only: true, per_page: 1000 }
    });
  }
}; 