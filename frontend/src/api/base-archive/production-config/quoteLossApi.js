import request from '../../../utils/request';

const BASE_URL = '/tenant/base-archive/production-config/quote-losses';

export const quoteLossApi = {
  // 获取报价损耗列表
  getQuoteLosses: (params) => {
    return request.get(`${BASE_URL}/`, { params });
  },

  // 获取报价损耗详情
  getQuoteLoss: (id) => {
    return request.get(`${BASE_URL}/${id}`);
  },

  // 创建报价损耗
  createQuoteLoss: (data) => {
    return request.post(`${BASE_URL}/`, data);
  },

  // 更新报价损耗
  updateQuoteLoss: (id, data) => {
    return request.put(`${BASE_URL}/${id}`, data);
  },

  // 删除报价损耗
  deleteQuoteLoss: (id) => {
    return request.delete(`${BASE_URL}/${id}`);
  },

  // 批量更新报价损耗（用于可编辑表格）
  batchUpdateQuoteLosses: (data) => {
    return request.put(`${BASE_URL}/batch`, data);
  },

  // 获取启用的报价损耗列表（用于下拉选择）
  getEnabledQuoteLosses: () => {
    return request.get(`${BASE_URL}/enabled`);
  }
};

export default quoteLossApi; 