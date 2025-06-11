import request from '../../../utils/request';

// 机台相关API
export const machineApi = {
  // 获取机台列表
  getMachines: (params) => {
    return request({
      url: '/tenant/basic-data/machines',
      method: 'get',
      params
    });
  },

  // 获取启用的机台列表
  getEnabledMachines: () => {
    return request({
      url: '/tenant/basic-data/machines/enabled',
      method: 'get'
    });
  },

  // 获取单个机台
  getMachine: (id) => {
    return request({
      url: `/tenant/basic-data/machines/${id}`,
      method: 'get'
    });
  },

  // 创建机台
  createMachine: (data) => {
    return request({
      url: '/tenant/basic-data/machines',
      method: 'post',
      data
    });
  },

  // 更新机台
  updateMachine: (id, data) => {
    return request({
      url: `/tenant/basic-data/machines/${id}`,
      method: 'put',
      data
    });
  },

  // 删除机台
  deleteMachine: (id) => {
    return request({
      url: `/tenant/basic-data/machines/${id}`,
      method: 'delete'
    });
  },

  // 批量更新机台
  batchUpdateMachines: (data) => {
    return request({
      url: '/tenant/basic-data/machines/batch',
      method: 'put',
      data
    });
  }
};

export default machineApi; 