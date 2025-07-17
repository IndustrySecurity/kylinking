import request from '../../../utils/request';

// 获取币别列表
export const getCurrencies = (params) => {
  return request({
    url: '/tenant/base-archive/financial-management/currencies/',
    method: 'get',
    params
  });
};

// 创建币别
export const createCurrency = (data) => {
  return request({
    url: '/tenant/base-archive/financial-management/currencies/',
    method: 'post',
    data
  });
};

// 更新币别
export const updateCurrency = (id, data) => {
  return request({
    url: `/tenant/base-archive/financial-management/currencies/${id}`,
    method: 'put',
    data
  });
};

// 删除币别
export const deleteCurrency = (id) => {
  return request({
    url: `/tenant/base-archive/financial-management/currencies/${id}`,
    method: 'delete'
  });
};

// 获取币别详情
export const getCurrencyById = (id) => {
  return request({
    url: `/tenant/base-archive/financial-management/currencies/${id}`,
    method: 'get'
  });
};

// 获取启用的币别选项
export const getEnabledCurrencies = () => {
  return request({
    url: '/tenant/base-archive/financial-management/currencies/enabled',
    method: 'get'
  });
};

// 批量更新币别
export const batchUpdateCurrencies = (data) => {
  return request({
    url: '/tenant/base-archive/financial-management/currencies/batch-update',
    method: 'post',
    data
  });
};

// 获取币别选项（用于下拉框）
export const getCurrencyOptions = () => {
  return request({
    url: '/tenant/base-archive/financial-management/currencies/options',
    method: 'get'
  });
};

// 默认导出（向后兼容）
export default {
  getCurrencies,
  createCurrency,
  updateCurrency,
  deleteCurrency,
  getCurrencyById,
  getEnabledCurrencies,
  batchUpdateCurrencies,
  getCurrencyOptions
}; 