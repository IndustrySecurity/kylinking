import request from '../utils/request';

const BASE_URL = '/tenant/basic-data/calculation-parameters';

// 计算参数管理API
export const calculationParameterApi = {
  // 获取计算参数列表
  getCalculationParameters: (params = {}) => {
    return request.get(BASE_URL, { params });
  },

  // 获取计算参数详情
  getCalculationParameterById: (id) => {
    return request.get(`${BASE_URL}/${id}`);
  },

  // 创建计算参数
  createCalculationParameter: (data) => {
    return request.post(BASE_URL, data);
  },

  // 更新计算参数
  updateCalculationParameter: (id, data) => {
    return request.put(`${BASE_URL}/${id}`, data);
  },

  // 删除计算参数
  deleteCalculationParameter: (id) => {
    return request.delete(`${BASE_URL}/${id}`);
  },

  // 批量更新计算参数
  batchUpdateCalculationParameters: (data) => {
    return request.put(`${BASE_URL}/batch`, data);
  },

  // 获取计算参数选项数据
  getCalculationParameterOptions: () => {
    return request.get(`${BASE_URL}/options`);
  },

  // 获取启用的计算参数列表（用于下拉选择）
  getEnabledCalculationParameters: () => {
    return request.get(BASE_URL, { 
      params: { 
        enabled_only: true,
        per_page: 1000 
      } 
    });
  }
}; 