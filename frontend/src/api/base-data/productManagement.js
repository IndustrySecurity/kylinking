import request from '../../utils/request';

const BASE_URL = '/tenant/basic-data/product-management';

export const productManagementApi = {
  // 获取产品管理列表
  getProducts: (params) => {
    return request.get(BASE_URL, { params });
  },

  // 获取产品管理详情
  getProductDetail: (id) => {
    return request.get(`${BASE_URL}/${id}`);
  },

  // 创建产品
  createProduct: (data) => {
    return request.post(BASE_URL, data);
  },

  // 更新产品
  updateProduct: (id, data) => {
    return request.put(`${BASE_URL}/${id}`, data);
  },

  // 删除产品
  deleteProduct: (id) => {
    return request.delete(`${BASE_URL}/${id}`);
  },

  // 获取表单选项数据
  getFormOptions: () => {
    return request.get(`${BASE_URL}/form-options`);
  },

  // 上传产品图片
  uploadImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return request.post('/product-management/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // 根据袋型获取产品结构模板
  getBagTypeStructure: (bagTypeId) => {
    return request.get(`${BASE_URL}/bag-type-structure/${bagTypeId}`);
  },

  // 根据客户获取相关信息
  getCustomerInfo: (customerId) => {
    return request.get(`${BASE_URL}/customer-info/${customerId}`);
  }
}; 