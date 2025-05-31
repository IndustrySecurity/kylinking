import request from '../utils/request';

// 获取机台列表
export const getMachines = (params) => {
  return request({
    url: '/tenant/basic-data/machines',
    method: 'get',
    params
  });
};

// 获取启用的机台列表
export const getEnabledMachines = () => {
  return request({
    url: '/tenant/basic-data/machines/enabled',
    method: 'get'
  });
};

// 获取单个机台
export const getMachine = (id) => {
  return request({
    url: `/tenant/basic-data/machines/${id}`,
    method: 'get'
  });
};

// 创建机台
export const createMachine = (data) => {
  return request({
    url: '/tenant/basic-data/machines',
    method: 'post',
    data
  });
};

// 更新机台
export const updateMachine = (id, data) => {
  return request({
    url: `/tenant/basic-data/machines/${id}`,
    method: 'put',
    data
  });
};

// 删除机台
export const deleteMachine = (id) => {
  return request({
    url: `/tenant/basic-data/machines/${id}`,
    method: 'delete'
  });
};

// 批量更新机台
export const batchUpdateMachines = (data) => {
  return request({
    url: '/tenant/basic-data/machines/batch',
    method: 'put',
    data
  });
}; 