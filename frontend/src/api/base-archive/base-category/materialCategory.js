import request from '../../../utils/request';

// 获取原料分类列表
export const getMaterialCategories = (params) => {
  return request({
    url: '/tenant/base-archive/base-category/material-categories/',
    method: 'get',
    params
  });
};

// 创建原料分类
export const createMaterialCategory = (data) => {
  return request({
    url: '/tenant/base-archive/base-category/material-categories/',
    method: 'post',
    data
  });
};

// 更新原料分类
export const updateMaterialCategory = (id, data) => {
  return request({
    url: `/tenant/base-archive/base-category/material-categories/${id}`,
    method: 'put',
    data
  });
};

// 删除原料分类
export const deleteMaterialCategory = (id) => {
  return request({
    url: `/tenant/base-archive/base-category/material-categories/${id}`,
    method: 'delete'
  });
};

// 获取原料分类详情
export const getMaterialCategoryById = (id) => {
  return request({
    url: `/tenant/base-archive/base-category/material-categories/${id}`,
    method: 'get'
  });
};

// 获取启用的原料分类选项
export const getEnabledMaterialCategories = () => {
  return request({
    url: '/tenant/base-archive/base-category/material-categories/enabled',
    method: 'get'
  });
};

// 获取原料分类选项（用于下拉框）
export const getMaterialCategoryOptions = () => {
  return request({
    url: '/tenant/base-archive/base-category/material-categories/options',
    method: 'get'
  });
};

// 获取材料分类表单选项（材料类型和单位）
export const getMaterialCategoryFormOptions = () => {
  return request({
    url: '/tenant/base-archive/base-category/material-categories/form-options',
    method: 'get'
  });
};

// 统一导出API对象
export const materialCategoryApi = {
  getMaterialCategories,
  createMaterialCategory,
  updateMaterialCategory,
  deleteMaterialCategory,
  getMaterialCategoryById,
  getEnabledMaterialCategories,
  getMaterialCategoryOptions,
  getMaterialCategoryFormOptions
}; 