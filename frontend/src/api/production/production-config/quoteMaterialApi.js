import request from '../../../utils/request';

// 获取报价材料列表
export const getQuoteMaterials = (params) => {
  return request({
    url: '/tenant/basic-data/quote-materials',
    method: 'get',
    params
  });
};

// 获取单个报价材料
export const getQuoteMaterial = (id) => {
  return request({
    url: `/tenant/basic-data/quote-materials/${id}`,
    method: 'get'
  });
};

// 创建报价材料
export const createQuoteMaterial = (data) => {
  return request({
    url: '/tenant/basic-data/quote-materials',
    method: 'post',
    data
  });
};

// 更新报价材料
export const updateQuoteMaterial = (id, data) => {
  return request({
    url: `/tenant/basic-data/quote-materials/${id}`,
    method: 'put',
    data
  });
};

// 删除报价材料
export const deleteQuoteMaterial = (id) => {
  return request({
    url: `/tenant/basic-data/quote-materials/${id}`,
    method: 'delete'
  });
};

// 批量更新报价材料
export const batchUpdateQuoteMaterials = (data) => {
  return request({
    url: '/tenant/basic-data/quote-materials/batch',
    method: 'put',
    data
  });
};

// 获取启用的报价材料列表
export const getEnabledQuoteMaterials = () => {
  return request({
    url: '/tenant/basic-data/quote-materials/enabled',
    method: 'get'
  });
};

export default {
  getQuoteMaterials,
  getQuoteMaterial,
  createQuoteMaterial,
  updateQuoteMaterial,
  deleteQuoteMaterial,
  batchUpdateQuoteMaterials,
  getEnabledQuoteMaterials
}; 