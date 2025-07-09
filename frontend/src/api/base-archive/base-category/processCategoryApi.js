import request from '../../../utils/request';

// 工序分类相关API
export const processCategoryApi = {
  // 获取工序分类列表
  getProcessCategories: (params) => {
    return request({
      url: '/tenant/base-archive/base-category/process-categories',
      method: 'get',
      params
    });
  },

  // 获取单个工序分类
  getProcessCategory: (id) => {
    return request({
      url: `/tenant/base-archive/base-category/process-categories/${id}`,
      method: 'get'
    });
  },

  // 创建工序分类
  createProcessCategory: (data) => {
    return request({
      url: '/tenant/base-archive/base-category/process-categories',
      method: 'post',
      data
    });
  },

  // 更新工序分类
  updateProcessCategory: (id, data) => {
    return request({
      url: `/tenant/base-archive/base-category/process-categories/${id}`,
      method: 'put',
      data
    });
  },

  // 删除工序分类
  deleteProcessCategory: (id) => {
    return request({
      url: `/tenant/base-archive/base-category/process-categories/${id}`,
      method: 'delete'
    });
  },

  // 批量更新工序分类
  batchUpdateProcessCategories: (data) => {
    return request({
      url: '/tenant/base-archive/base-category/process-categories/batch-update',
      method: 'post',
      data
    });
  },

  // 获取启用的工序分类列表
  getEnabledProcessCategories: () => {
    return request({
      url: '/tenant/base-archive/base-category/process-categories/enabled',
      method: 'get'
    });
  },

  // 获取类型选项
  getProcessCategoryTypeOptions: () => {
    return request.get('/tenant/base-archive/base-category/process-categories/category-type-options');
  },

  // 获取数据采集模式选项
  getDataCollectionModeOptions: () => {
    return request.get('/tenant/base-archive/base-category/process-categories/data-collection-mode-options');
  },

  // 获取工序分类选项（用于下拉框）
  getProcessCategoryOptions: () => {
    return request({
      url: '/tenant/base-archive/base-category/process-categories/options',
      method: 'get'
    });
  },
};

export default processCategoryApi;