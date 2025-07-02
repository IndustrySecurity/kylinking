import request from '../../../utils/request';

const BASE_URL = '/tenant/base-archive/production/production-archive/color-cards';

export const colorCardApi = {
  // 获取色卡列表
  getColorCards: (params) => {
    return request.get(BASE_URL, { params });
  },

  // 获取色卡详情
  getColorCard: (id) => {
    return request.get(`${BASE_URL}/${id}`);
  },

  // 创建色卡
  createColorCard: (data) => {
    return request.post(BASE_URL, data);
  },

  // 更新色卡
  updateColorCard: (id, data) => {
    return request.put(`${BASE_URL}/${id}`, data);
  },

  // 删除色卡
  deleteColorCard: (id) => {
    return request.delete(`${BASE_URL}/${id}`);
  },

  // 批量更新色卡（用于可编辑表格）
  batchUpdateColorCards: (data) => {
    return request.put(`${BASE_URL}/batch`, data);
  },

  // 获取启用的色卡列表（用于下拉选择）
  getEnabledColorCards: () => {
    return request.get(BASE_URL, { 
      params: { 
        enabled_only: true,
        per_page: 1000 
      } 
    });
  }
}; 