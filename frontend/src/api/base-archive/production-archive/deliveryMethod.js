import request from '../../../utils/request';

const BASE_URL = '/tenant/base-archive/production-archive/delivery-methods/';

export const deliveryMethodApi = {
  // 获取送货方式列表
  getDeliveryMethods: (params) => {
    return request.get(BASE_URL, { params });
  },

  // 获取送货方式详情
  getDeliveryMethod: (id) => {
    return request.get(`${BASE_URL}/${id}`);
  },

  // 创建送货方式
  createDeliveryMethod: (data) => {
    return request.post(BASE_URL, data);
  },

  // 更新送货方式
  updateDeliveryMethod: (id, data) => {
    return request.put(`${BASE_URL}/${id}`, data);
  },

  // 删除送货方式
  deleteDeliveryMethod: (id) => {
    return request.delete(`${BASE_URL}/${id}`);
  },

  // 批量更新送货方式（用于可编辑表格）
  batchUpdateDeliveryMethods: (data) => {
    return request.put(`${BASE_URL}/batch`, data);
  },

  // 获取启用的送货方式列表（用于下拉选择）
  getEnabledDeliveryMethods: () => {
    return request.get(BASE_URL, { 
      params: { 
        enabled_only: true,
        per_page: 1000 
      } 
    });
  }
}; 