import request from '../../utils/request';

/**
 * 产品调拨API
 */

// 获取产品调拨列表
export const getProductTransfers = (params) => {
  return request({
    url: '/tenant/business/inventory/product-transfer',
    method: 'get',
    params
  });
};

// 创建产品调拨
export const createProductTransfer = (data) => {
  return request({
    url: '/tenant/business/inventory/product-transfer',
    method: 'post',
    data
  });
};

// 更新产品调拨
export const updateProductTransfer = (id, data) => {
  return request({
    url: `/tenant/business/inventory/product-transfer/${id}`,
    method: 'put',
    data
  });
};

// 删除产品调拨
export const deleteProductTransfer = (id) => {
  return request({
    url: `/tenant/business/inventory/product-transfer/${id}`,
    method: 'delete'
  });
};

// 获取产品调拨详情
export const getProductTransferById = (id) => {
  return request({
    url: `/tenant/business/inventory/product-transfer/${id}`,
    method: 'get'
  });
};

// 确认产品调拨
export const confirmProductTransfer = (id) => {
  return request({
    url: `/tenant/business/inventory/product-transfer/${id}/confirm`,
    method: 'post'
  });
};

// 获取产品库存信息
export const getProductStock = (productId, warehouseId) => {
  return request({
    url: `/tenant/business/inventory/product-stock/${productId}/${warehouseId}`,
    method: 'get'
  });
};

// 导出产品调拨数据
export const exportProductTransfer = (params) => {
  return request({
    url: '/tenant/business/inventory/product-transfer/export',
    method: 'get',
    params,
    responseType: 'blob'
  });
};

// 获取调拨单列表
export const getProductTransferOrders = (params) => {
  return request.get('/tenant/inventory/product-transfer-orders', { params });
};

// 创建调拨单
export const createProductTransferOrder = (data) => {
  return request.post('/tenant/inventory/product-transfer-orders', data);
};

// 获取调拨单详情
export const getProductTransferOrder = (orderId) => {
  return request.get(`/tenant/inventory/product-transfer-orders/${orderId}`);
};

// 更新调拨单
export const updateProductTransferOrder = (orderId, data) => {
  return request.put(`/tenant/inventory/product-transfer-orders/${orderId}`, data);
};

// 获取调拨单明细
export const getProductTransferOrderDetails = (orderId) => {
  return request.get(`/tenant/inventory/product-transfer-orders/${orderId}/details`);
};

// 添加调拨明细
export const addProductTransferOrderDetail = (orderId, data) => {
  return request.post(`/tenant/inventory/product-transfer-orders/${orderId}/details`, data);
};

// 更新调拨明细
export const updateProductTransferOrderDetail = (orderId, detailId, data) => {
  return request.put(`/tenant/inventory/product-transfer-orders/${orderId}/details/${detailId}`, data);
};

// 删除调拨明细
export const deleteProductTransferOrderDetail = (orderId, detailId) => {
  return request.delete(`/tenant/inventory/product-transfer-orders/${orderId}/details/${detailId}`);
};

// 确认调拨单
export const confirmProductTransferOrder = (orderId) => {
  return request.post(`/tenant/inventory/product-transfer-orders/${orderId}/confirm`);
};

// 执行调拨单（出库）
export const executeProductTransferOrder = (orderId) => {
  return request.post(`/tenant/inventory/product-transfer-orders/${orderId}/execute`);
};

// 接收调拨单（入库）
export const receiveProductTransferOrder = (orderId) => {
  return request.post(`/tenant/inventory/product-transfer-orders/${orderId}/receive`);
};

// 取消调拨单
export const cancelProductTransferOrder = (orderId, data = {}) => {
  return request.post(`/tenant/inventory/product-transfer-orders/${orderId}/cancel`, data);
};

// 获取仓库产品库存
export const getWarehouseProductInventory = (warehouseId) => {
  return request.get(`/tenant/inventory/warehouses/${warehouseId}/product-inventory`);
};

// 统一导出API对象
export const productTransferApi = {
  // 基础调拨API
  getProductTransfers,
  createProductTransfer,
  updateProductTransfer,
  deleteProductTransfer,
  getProductTransferById,
  confirmProductTransfer,
  getProductStock,
  exportProductTransfer,
  // 调拨单API
  getProductTransferOrders,
  createProductTransferOrder,
  getProductTransferOrder,
  updateProductTransferOrder,
  getProductTransferOrderDetails,
  addProductTransferOrderDetail,
  updateProductTransferOrderDetail,
  deleteProductTransferOrderDetail,
  confirmProductTransferOrder,
  executeProductTransferOrder,
  receiveProductTransferOrder,
  cancelProductTransferOrder,
  getWarehouseProductInventory
}; 