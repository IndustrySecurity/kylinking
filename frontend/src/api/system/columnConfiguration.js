import request from '../../utils/request';

// 列配置API
export const columnConfigurationApi = {
  // 获取列配置
  getColumnConfig: (pageName, configType) => {
    return request({
      url: '/system/column-config/get',
      method: 'get',
      params: {
        page_name: pageName,
        config_type: configType
      }
    });
  },

  // 保存列配置
  saveColumnConfig: (pageName, configType, configData) => {
    return request({
      url: '/system/column-config/save',
      method: 'post',
      data: {
        page_name: pageName,
        config_type: configType,
        config_data: configData
      }
    });
  },

  // 删除列配置
  deleteColumnConfig: (pageName, configType) => {
    return request({
      url: '/system/column-config/delete',
      method: 'delete',
      params: {
        page_name: pageName,
        config_type: configType
      }
    });
  },

  // 获取所有配置
  getAllConfigs: (pageName) => {
    return request({
      url: '/system/column-config/list',
      method: 'get',
      params: {
        page_name: pageName
      }
    });
  }
}; 