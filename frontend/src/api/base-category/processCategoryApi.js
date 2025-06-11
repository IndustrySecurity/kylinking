import request from '../../utils/request';

// 工序分类相关API
export const processCategoryApi = {
  // 获取工序分类列表
  getProcessCategories: (params) => {
    return request.get('/tenant/basic-data/process-categories', { params });
  },

  // 获取单个工序分类
  getProcessCategory: (id) => {
    return request.get(`/tenant/basic-data/process-categories/${id}`);
  },

  // 创建工序分类
  createProcessCategory: (data) => {
    return request.post('/tenant/basic-data/process-categories', data);
  },

  // 更新工序分类
  updateProcessCategory: (id, data) => {
    return request.put(`/tenant/basic-data/process-categories/${id}`, data);
  },

  // 删除工序分类
  deleteProcessCategory: (id) => {
    return request.delete(`/tenant/basic-data/process-categories/${id}`);
  },

  // 批量更新工序分类
  batchUpdateProcessCategories: (data) => {
    return request.post('/tenant/basic-data/process-categories/batch', data);
  },

  // 获取启用的工序分类列表
  getEnabledProcessCategories: () => {
    return request.get('/tenant/basic-data/process-categories/enabled');
  },

  // 获取类型选项
  getProcessCategoryTypeOptions: () => {
    return request.get('/tenant/basic-data/process-categories/category-type-options');
  },

  // 获取数据采集模式选项
  getDataCollectionModeOptions: () => {
    return request.get('/tenant/basic-data/process-categories/data-collection-mode-options');
  },
};

export default processCategoryApi;