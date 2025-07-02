import request from '../../utils/request';

// 获取税率列表
export const getTaxRates = (params) => {
  return request({
    url: '/tenant/base-archive/financial-management/tax-rates',
    method: 'get',
    params
  });
};

// 创建税率
export const createTaxRate = (data) => {
  return request({
    url: '/tenant/base-archive/financial-management/tax-rates',
    method: 'post',
    data
  });
};

// 更新税率
export const updateTaxRate = (id, data) => {
  return request({
    url: `/tenant/base-archive/financial-management/tax-rates/${id}`,
    method: 'put',
    data
  });
};

// 删除税率
export const deleteTaxRate = (id) => {
  return request({
    url: `/tenant/base-archive/financial-management/tax-rates/${id}`,
    method: 'delete'
  });
};

// 获取税率详情
export const getTaxRateById = (id) => {
  return request({
    url: `/tenant/base-archive/financial-management/tax-rates/${id}`,
    method: 'get'
  });
};

// 获取启用的税率选项
export const getEnabledTaxRates = () => {
  return request({
    url: '/tenant/base-archive/financial-management/tax-rates/enabled',
    method: 'get'
  });
};

// 批量更新税率
export const batchUpdateTaxRates = (data) => {
  return request({
    url: '/tenant/base-archive/financial-management/tax-rates/batch-update',
    method: 'post',
    data
  });
};

// 获取税率选项（用于下拉框）
export const getTaxRateOptions = () => {
  return request({
    url: '/tenant/base-archive/financial-management/tax-rates/options',
    method: 'get'
  });
};

// 默认导出（向后兼容）
export default {
  getTaxRates,
  createTaxRate,
  updateTaxRate,
  deleteTaxRate,
  getTaxRateById,
  getEnabledTaxRates,
  batchUpdateTaxRates,
  getTaxRateOptions
}; 