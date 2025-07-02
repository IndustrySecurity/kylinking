import request from '../../../utils/request';

// 获取油墨选项列表
export const getInkOptions = (params) => {
  return request({
    url: '/tenant/base-archive/production/production-config/ink-options',
    method: 'get',
    params
  });
};

// 创建油墨选项
export const createInkOption = (data) => {
  return request({
    url: '/tenant/base-archive/production/production-config/ink-options',
    method: 'post',
    data
  });
};

// 更新油墨选项
export const updateInkOption = (id, data) => {
  return request({
    url: `/tenant/base-archive/production/production-config/ink-options/${id}`,
    method: 'put',
    data
  });
};

// 删除油墨选项
export const deleteInkOption = (id) => {
  return request({
    url: `/tenant/base-archive/production/production-config/ink-options/${id}`,
    method: 'delete'
  });
};

// 获取油墨选项详情
export const getInkOptionById = (id) => {
  return request({
    url: `/tenant/base-archive/production/production-config/ink-options/${id}`,
    method: 'get'
  });
};

// 获取启用的油墨选项
export const getEnabledInkOptions = () => {
  return request({
    url: '/tenant/base-archive/production/production-config/ink-options/enabled',
    method: 'get'
  });
};

// 批量更新油墨选项
export const batchUpdateInkOptions = (data) => {
  return request({
    url: '/tenant/base-archive/production/production-config/ink-options/batch-update',
    method: 'post',
    data
  });
};

// 获取油墨选项下拉列表
export const getInkOptionsList = () => {
  return request({
    url: '/tenant/base-archive/production/production-config/ink-options/options',
    method: 'get'
  });
};

// 油墨选项管理API（保持向后兼容）
export const inkOptionApi = {
  getInkOptions,
  getInkOption: getInkOptionById,
  createInkOption,
  updateInkOption,
  deleteInkOption,
  batchUpdateInkOptions,
  getEnabledInkOptions
}; 