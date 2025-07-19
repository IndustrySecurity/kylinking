import request from '../../../utils/request';

const BASE_URL = '/tenant/base-archive/production-config/calculation-schemes';

// 计算方案管理API
export const calculationSchemeApi = {
  // 获取计算方案列表
  getCalculationSchemes: (params = {}) => {
    return request.get(`${BASE_URL}/`, { params });
  },

  // 获取计算方案详情
  getCalculationSchemeById: (id) => {
    return request.get(`${BASE_URL}/${id}`);
  },

  // 创建计算方案
  createCalculationScheme: (data) => {
    return request.post(`${BASE_URL}/`, data);
  },

  // 更新计算方案
  updateCalculationScheme: (id, data) => {
    return request.put(`${BASE_URL}/${id}`, data);
  },

  // 删除计算方案
  deleteCalculationScheme: (id) => {
    return request.delete(`${BASE_URL}/${id}`);
  },

  // 获取方案分类选项
  getSchemeCategories: () => {
    return request.get(`${BASE_URL}/categories`);
  },

  // 验证计算公式
  validateFormula: (formula) => {
    return request.post(`${BASE_URL}/validate-formula`, { formula });
  },

  // 获取计算方案选项数据
  getCalculationSchemeOptions: () => {
    return request.get(`${BASE_URL}/options`);
  }
};

export default calculationSchemeApi; 