import request from '../utils/request';

// 获取报损类型列表
export const getLossTypes = (params) => {
  return request({
    url: '/tenant/basic-data/loss-types',
    method: 'get',
    params
  });
};

// 获取启用的报损类型列表
export const getEnabledLossTypes = () => {
  return request({
    url: '/tenant/basic-data/loss-types/enabled',
    method: 'get'
  });
};

// 获取单个报损类型
export const getLossType = (id) => {
  return request({
    url: `/tenant/basic-data/loss-types/${id}`,
    method: 'get'
  });
};

// 创建报损类型
export const createLossType = (data) => {
  return request({
    url: '/tenant/basic-data/loss-types',
    method: 'post',
    data
  });
};

// 更新报损类型
export const updateLossType = (id, data) => {
  return request({
    url: `/tenant/basic-data/loss-types/${id}`,
    method: 'put',
    data
  });
};

// 删除报损类型
export const deleteLossType = (id) => {
  return request({
    url: `/tenant/basic-data/loss-types/${id}`,
    method: 'delete'
  });
};

// 批量更新报损类型
export const batchUpdateLossTypes = (data) => {
  return request({
    url: '/tenant/basic-data/loss-types/batch',
    method: 'put',
    data
  });
}; 