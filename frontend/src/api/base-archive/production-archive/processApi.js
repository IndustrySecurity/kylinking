import request from '../../../utils/request';

// 获取工序列表
export const getProcesses = (params) => {
  return request({
    url: '/tenant/base-archive/production/production-archive/processes/',
    method: 'get',
    params
  });
};

// 创建工序
export const createProcess = (data) => {
  return request({
    url: '/tenant/base-archive/production/production-archive/processes/',
    method: 'post',
    data
  });
};

// 更新工序
export const updateProcess = (id, data) => {
  return request({
    url: `/tenant/base-archive/production/production-archive/processes/${id}`,
    method: 'put',
    data
  });
};

// 删除工序
export const deleteProcess = (id) => {
  return request({
    url: `/tenant/base-archive/production/production-archive/processes/${id}`,
    method: 'delete'
  });
};

// 获取工序详情
export const getProcessById = (id) => {
  return request({
    url: `/tenant/base-archive/production/production-archive/processes/${id}`,
    method: 'get'
  });
};

// 获取启用的工序选项
export const getEnabledProcesses = () => {
  return request({
    url: '/tenant/base-archive/production/production-archive/processes/enabled',
    method: 'get'
  });
};

// 获取工序选项（用于下拉框）
export const getProcessOptions = () => {
  return request({
    url: '/tenant/base-archive/production/production-archive/processes/options',
    method: 'get'
  });
};

// 工序相关API（保持向后兼容）
export const processApi = {
  getProcesses,
  getProcess: getProcessById,
  createProcess,
  updateProcess,
  deleteProcess,
  getEnabledProcesses,
  
  // 批量更新工序
  batchUpdateProcesses: (data) => {
    return request.post('/tenant/base-archive/production/production-archive/processes/batch', data);
  },

  // 获取排程方式选项
  getSchedulingMethodOptions: () => {
    return request.get('/tenant/base-archive/production/production-archive/processes/scheduling-method-options');
  },

  // 获取计算方案选项
  getCalculationSchemeOptions: (category) => {
    if (category) {
      return request.get(`/tenant/base-archive/production/production-config/calculation-schemes/options/by-category?category=${category}`);
    }
    return request.get('/tenant/base-archive/production/production-config/calculation-schemes/options/by-category');
  }
};


export default processApi; 