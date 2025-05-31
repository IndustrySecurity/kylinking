import request from '../utils/request';

const positionApi = {
  // 获取职位列表
  getPositions: (params) => {
    return request({
      url: '/tenant/basic-data/positions',
      method: 'get',
      params
    });
  },

  // 获取职位详情
  getPosition: (id) => {
    return request({
      url: `/tenant/basic-data/positions/${id}`,
      method: 'get'
    });
  },

  // 创建职位
  createPosition: (data) => {
    return request({
      url: '/tenant/basic-data/positions',
      method: 'post',
      data
    });
  },

  // 更新职位
  updatePosition: (id, data) => {
    return request({
      url: `/tenant/basic-data/positions/${id}`,
      method: 'put',
      data
    });
  },

  // 删除职位
  deletePosition: (id) => {
    return request({
      url: `/tenant/basic-data/positions/${id}`,
      method: 'delete'
    });
  },

  // 获取职位选项数据
  getPositionOptions: (params) => {
    return request({
      url: '/tenant/basic-data/positions/options',
      method: 'get',
      params
    });
  },

  // 获取部门选项数据
  getDepartmentOptions: () => {
    return request({
      url: '/tenant/basic-data/departments/options',
      method: 'get'
    });
  }
};

export default positionApi; 