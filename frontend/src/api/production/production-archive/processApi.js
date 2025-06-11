import request from '../../../utils/request';

// 工序相关API
export const processApi = {
  // 获取工序列表
  getProcesses: (params) => {
    return request.get('/tenant/basic-data/processes', { params });
  },

  // 获取单个工序
  getProcess: (id) => {
    return request.get(`/tenant/basic-data/processes/${id}`);
  },

  // 创建工序
  createProcess: (data) => {
    return request.post('/tenant/basic-data/processes', data);
  },

  // 更新工序
  updateProcess: (id, data) => {
    return request.put(`/tenant/basic-data/processes/${id}`, data);
  },

  // 删除工序
  deleteProcess: (id) => {
    return request.delete(`/tenant/basic-data/processes/${id}`);
  },

  // 批量更新工序
  batchUpdateProcesses: (data) => {
    return request.post('/tenant/basic-data/processes/batch', data);
  },

  // 获取启用的工序列表
  getEnabledProcesses: () => {
    return request.get('/tenant/basic-data/processes/enabled');
  },

  // 获取排程方式选项
  getSchedulingMethodOptions: () => {
    return request.get('/tenant/basic-data/processes/scheduling-method-options');
  },

  // 获取计算方案选项
  getCalculationSchemeOptions: () => {
    return request.get('/tenant/basic-data/processes/calculation-scheme-options');
  }
};


export default processApi; 