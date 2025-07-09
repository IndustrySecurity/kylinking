import request from '../../../utils/request';

/**
 * 成品调拨API
 */

// 获取产品调拨列表
export const getProductTransfers = (params) => {
  return request({
    url: '/tenant/business/inventory/product-transfer/product-transfer-orders',
    method: 'get',
    params
  });
};

// 创建产品调拨
export const createProductTransfer = (data) => {
  return request({
    url: '/tenant/business/inventory/product-transfer/product-transfer-orders',
    method: 'post',
    data
  });
};

// 获取产品调拨详情
export const getProductTransferById = (id) => {
  return request({
    url: `/tenant/business/inventory/product-transfer/product-transfer-orders/${id}`,
    method: 'get'
  });
};

// 更新产品调拨
export const updateProductTransfer = (id, data) => {
  return request({
    url: `/tenant/business/inventory/product-transfer/product-transfer-orders/${id}`,
    method: 'put',
    data
  });
};

// 删除产品调拨
export const deleteProductTransfer = (id) => {
  return request({
    url: `/tenant/business/inventory/product-transfer/product-transfer-orders/${id}`,
    method: 'delete'
  });
};

// 确认产品调拨
export const confirmProductTransfer = (id) => {
  return request({
    url: `/tenant/business/inventory/product-transfer/product-transfer-orders/${id}/approve`,
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

// 导出产品调拨
export const exportProductTransfer = (params) => {
  return request({
    url: '/tenant/business/inventory/product-transfer/product-transfer-orders/export',
    method: 'get',
    params,
    responseType: 'blob'
  });
};

// ==================== 调拨单API ====================

// 获取产品调拨单列表
export const getProductTransferOrders = (params = {}) => {
  return request.get('/tenant/business/inventory/product-transfer/product-transfer-orders', { params });
};

// 创建产品调拨单
export const createProductTransferOrder = (data) => {
  return request.post('/tenant/business/inventory/product-transfer/product-transfer-orders', data);
};

// 获取产品调拨单详情
export const getProductTransferOrder = (orderId) => {
  return request.get(`/tenant/business/inventory/product-transfer/product-transfer-orders/${orderId}`);
};

// 更新产品调拨单
export const updateProductTransferOrder = (orderId, data) => {
  return request.put(`/tenant/business/inventory/product-transfer/product-transfer-orders/${orderId}`, data);
};

// 获取调拨单明细
export const getProductTransferOrderDetails = (orderId) => {
  return request.get(`/tenant/business/inventory/product-transfer/product-transfer-orders/${orderId}/details`);
};

// 添加调拨单明细
export const addProductTransferOrderDetail = (orderId, data) => {
  return request.post(`/tenant/business/inventory/product-transfer/product-transfer-orders/${orderId}/details`, data);
};

// 更新调拨单明细
export const updateProductTransferOrderDetail = (orderId, detailId, data) => {
  return request.put(`/tenant/business/inventory/product-transfer/product-transfer-orders/${orderId}/details/${detailId}`, data);
};

// 删除调拨单明细
export const deleteProductTransferOrderDetail = (orderId, detailId) => {
  return request.delete(`/tenant/business/inventory/product-transfer/product-transfer-orders/${orderId}/details/${detailId}`);
};

// 确认调拨单
export const confirmProductTransferOrder = (orderId) => {
  return request.post(`/tenant/business/inventory/product-transfer/product-transfer-orders/${orderId}/approve`);
};

// 执行调拨单（出库）
export const executeProductTransferOrder = (orderId) => {
  return request.post(`/tenant/business/inventory/product-transfer/product-transfer-orders/${orderId}/execute`);
};

// 接收调拨单（入库）
export const receiveProductTransferOrder = (orderId) => {
  return request.post(`/tenant/business/inventory/product-transfer/product-transfer-orders/${orderId}/receive`);
};

// 取消调拨单
export const cancelProductTransferOrder = (orderId, data) => {
  return request.post(`/tenant/business/inventory/product-transfer/product-transfer-orders/${orderId}/cancel`, data);
};

// 获取仓库产品库存
export const getWarehouseProductInventory = (warehouseId) => {
  return request.get(`/tenant/business/inventory/inventories?warehouse_id=${warehouseId}`);
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