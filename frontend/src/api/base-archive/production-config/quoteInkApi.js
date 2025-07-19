import request from '../../../utils/request';

// 获取报价油墨列表
export const getQuoteInks = (params) => {
  return request({
    url: '/tenant/base-archive/production-config/quote-inks/',
    method: 'get',
    params
  });
};

// 获取单个报价油墨
export const getQuoteInk = (id) => {
  return request({
    url: `/tenant/base-archive/production-config/quote-inks/${id}`,
    method: 'get'
  });
};

// 创建报价油墨
export const createQuoteInk = (data) => {
  return request({
    url: '/tenant/base-archive/production-config/quote-inks/',
    method: 'post',
    data
  });
};

// 更新报价油墨
export const updateQuoteInk = (id, data) => {
  return request({
    url: `/tenant/base-archive/production-config/quote-inks/${id}`,
    method: 'put',
    data
  });
};

// 删除报价油墨
export const deleteQuoteInk = (id) => {
  return request({
    url: `/tenant/base-archive/production-config/quote-inks/${id}`,
    method: 'delete'
  });
};

// 批量更新报价油墨
export const batchUpdateQuoteInks = (data) => {
  return request({
    url: '/tenant/base-archive/production-config/quote-inks/batch',
    method: 'put',
    data
  });
};

// 获取启用的报价油墨列表
export const getEnabledQuoteInks = () => {
  return request({
    url: '/tenant/base-archive/production-config/quote-inks/enabled',
    method: 'get'
  });
};

// 统一导出API对象
export const quoteInkApi = {
  getQuoteInks,
  getQuoteInk,
  createQuoteInk,
  updateQuoteInk,
  deleteQuoteInk,
  batchUpdateQuoteInks,
  getEnabledQuoteInks
}; 