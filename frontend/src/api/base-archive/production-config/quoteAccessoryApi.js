import request from '../../../utils/request';

// 获取报价辅材列表
export const getQuoteAccessories = (params) => {
  return request({
    url: '/tenant/base-archive/production-config/quote-accessories/',
    method: 'get',
    params
  });
};

// 获取单个报价辅材
export const getQuoteAccessory = (id) => {
  return request({
    url: `/tenant/base-archive/production-config/quote-accessories/${id}`,
    method: 'get'
  });
};

// 创建报价辅材
export const createQuoteAccessory = (data) => {
  return request({
    url: '/tenant/base-archive/production-config/quote-accessories/',
    method: 'post',
    data
  });
};

// 更新报价辅材
export const updateQuoteAccessory = (id, data) => {
  return request({
    url: `/tenant/base-archive/production-config/quote-accessories/${id}`,
    method: 'put',
    data
  });
};

// 删除报价辅材
export const deleteQuoteAccessory = (id) => {
  return request({
    url: `/tenant/base-archive/production-config/quote-accessories/${id}`,
    method: 'delete'
  });
};

// 批量更新报价辅材
export const batchUpdateQuoteAccessories = (data) => {
  return request({
    url: '/tenant/base-archive/production-config/quote-accessories/batch',
    method: 'put',
    data
  });
};

// 获取启用的报价辅材列表
export const getEnabledQuoteAccessories = () => {
  return request({
    url: '/tenant/base-archive/production-config/quote-accessories/enabled',
    method: 'get'
  });
};

// 获取材料报价分类的计算方案选项
export const getMaterialQuoteCalculationSchemes = () => {
  return request({
    url: '/tenant/base-archive/production-config/quote-accessories/calculation-schemes',
    method: 'get'
  });
};

// 统一导出API对象
const quoteAccessoryApi = {
  getQuoteAccessories,
  getQuoteAccessory,
  createQuoteAccessory,
  updateQuoteAccessory,
  deleteQuoteAccessory,
  batchUpdateQuoteAccessories,
  getEnabledQuoteAccessories,
  getMaterialQuoteCalculationSchemes
};

export default quoteAccessoryApi; 