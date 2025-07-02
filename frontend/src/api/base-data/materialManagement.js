import request from '../../utils/request';

// 获取原料列表
export const getMaterials = (params) => {
  return request({
    url: '/tenant/base-archive/base-data/materials',
    method: 'get',
    params
  });
};

// 创建原料
export const createMaterial = (data) => {
  return request({
    url: '/tenant/base-archive/base-data/materials',
    method: 'post',
    data
  });
};

// 更新原料
export const updateMaterial = (id, data) => {
  return request({
    url: `/tenant/base-archive/base-data/materials/${id}`,
    method: 'put',
    data
  });
};

// 删除原料
export const deleteMaterial = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/materials/${id}`,
    method: 'delete'
  });
};

// 获取原料详情
export const getMaterialById = (id) => {
  return request({
    url: `/tenant/base-archive/base-data/materials/${id}`,
    method: 'get'
  });
};

// 获取启用的原料选项
export const getEnabledMaterials = () => {
  return request({
    url: '/tenant/base-archive/base-data/materials/enabled',
    method: 'get'
  });
};

// 获取原料选项（用于下拉框）
export const getMaterialOptions = () => {
  return request({
    url: '/tenant/base-archive/base-data/materials/options',
    method: 'get'
  });
};

// 导入原料数据
export const importMaterials = (formData) => {
  return request({
    url: '/tenant/base-archive/base-data/materials/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

// 导出原料数据
export const exportMaterials = (params) => {
  return request({
    url: '/tenant/base-archive/base-data/materials/export',
    method: 'get',
    params,
    responseType: 'blob'
  });
};

// 搜索原料
export const searchMaterials = (keyword) => {
  return request({
    url: '/tenant/base-archive/base-data/materials/search',
    method: 'get',
    params: { keyword }
  });
};

// 获取表单选项
export const getFormOptions = () => {
  return request.get('/tenant/base-archive/base-data/materials/form-options');
};

// 获取材料分类详情（用于自动填入）
export const getMaterialCategoryDetails = (categoryId) => {
  return request.get('/tenant/base-archive/base-data/materials/category-details/' + categoryId);
};

// 批量更新材料
export const batchUpdateMaterials = (data) => {
  return request.put('/tenant/base-archive/base-data/materials/batch', data);
};

// 统一导出API对象
export const materialManagementApi = {
  getMaterials,
  createMaterial,
  updateMaterial,
  deleteMaterial,
  getMaterialById,
  getEnabledMaterials,
  getMaterialOptions,
  importMaterials,
  exportMaterials,
  searchMaterials,
  getFormOptions,
  getMaterialCategoryDetails,
  batchUpdateMaterials
}; 