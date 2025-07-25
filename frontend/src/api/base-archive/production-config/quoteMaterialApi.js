import request from '../../../utils/request';

// 获取报价材料列表
export const getQuoteMaterials = (params) => {
  return request({
    url: '/tenant/base-archive/production-config/quote-materials/',
    method: 'get',
    params
  });
};

// 获取单个报价材料
export const getQuoteMaterial = (id) => {
  return request({
    url: `/tenant/base-archive/production-config/quote-materials/${id}`,
    method: 'get'
  });
};

// 创建报价材料
export const createQuoteMaterial = (data) => {
  return request({
    url: '/tenant/base-archive/production-config/quote-materials/',
    method: 'post',
    data
  });
};

// 更新报价材料
export const updateQuoteMaterial = (id, data) => {
  return request({
    url: `/tenant/base-archive/production-config/quote-materials/${id}`,
    method: 'put',
    data
  });
};

// 删除报价材料
export const deleteQuoteMaterial = (id) => {
  return request({
    url: `/tenant/base-archive/production-config/quote-materials/${id}`,
    method: 'delete'
  });
};

// 批量更新报价材料
export const batchUpdateQuoteMaterials = (data) => {
  return request({
    url: '/tenant/base-archive/production-config/quote-materials/batch',
    method: 'put',
    data
  });
};

// 获取启用的报价材料列表
export const getEnabledQuoteMaterials = () => {
  return request({
    url: '/tenant/base-archive/production-config/quote-materials/enabled',
    method: 'get'
  });
};

// 统一导出API对象
const quoteMaterialApi = {
  getQuoteMaterials,
  getQuoteMaterial,
  createQuoteMaterial,
  updateQuoteMaterial,
  deleteQuoteMaterial,
  batchUpdateQuoteMaterials,
  getEnabledQuoteMaterials
};

export default quoteMaterialApi; 