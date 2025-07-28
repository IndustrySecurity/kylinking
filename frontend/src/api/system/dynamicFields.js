import request from '../../utils/request';

const dynamicFieldsApi = {
  // 获取模型字段定义
  getModelFields: (modelName, pageName) => {
    const params = pageName ? { page_name: pageName } : {};
    return request.get(`/system/dynamic-fields/${modelName}/fields`, {
      params
    });
  },

  // 获取指定页面字段定义
  getPageFields: (modelName, pageName) => {
    return request.get(`/system/dynamic-fields/${modelName}/${pageName}/fields`);
  },

  // 创建字段定义
  createField: (modelName, fieldData) => {
    return request.post(`/system/dynamic-fields/${modelName}/fields`, fieldData);
  },

  // 更新字段定义
  updateField: (fieldId, fieldData) => {
    return request.put(`/system/dynamic-fields/fields/${fieldId}`, fieldData);
  },

  // 删除字段定义
  deleteField: (fieldId) => {
    return request.delete(`/system/dynamic-fields/fields/${fieldId}`);
  },

  // 获取记录动态字段值
  getRecordDynamicValues: (modelName, recordId, pageName = 'default') => {
    return request.get(`/system/dynamic-fields/${modelName}/${recordId}/values`, {
      params: { page_name: pageName }
    });
  },

  // 获取记录指定页面动态字段值
  getRecordPageValues: (modelName, pageName, recordId) => {
    return request.get(`/system/dynamic-fields/${modelName}/page/${pageName}/${recordId}/values`);
  },

  // 保存记录动态字段值
  saveRecordDynamicValues: (modelName, recordId, values, pageName = 'default') => {
    return request.post(`/system/dynamic-fields/${modelName}/${recordId}/values`, values, {
      params: { page_name: pageName }
    });
  },

  // 保存记录指定页面动态字段值
  saveRecordPageValues: (modelName, pageName, recordId, values) => {
    return request.post(`/system/dynamic-fields/${modelName}/page/${pageName}/${recordId}/values`, values);
  },

  // 删除记录指定页面的所有动态字段值
  deleteRecordPageValues: (modelName, pageName, recordId) => {
    return request.delete(`/system/dynamic-fields/${modelName}/page/${pageName}/${recordId}/values`);
  },

  // 清理记录中重复的动态字段值
  cleanupDuplicateValues: (modelName, recordId) => {
    return request.post(`/system/dynamic-fields/${modelName}/${recordId}/cleanup-duplicates`);
  },

  // 获取字段类型
  getFieldTypes: () => {
    return request.get('/system/dynamic-fields/field-types');
  },
};

export default dynamicFieldsApi; 