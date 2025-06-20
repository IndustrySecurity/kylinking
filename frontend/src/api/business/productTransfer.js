import request from '../../utils/request';

// 成品调拨管理API

// 获取成品调拨单列表
export const getProductTransferOrders = (params) => {
  return request.get('/tenant/inventory/product-transfer-orders', { params });
};

// 创建成品调拨单
export const createProductTransferOrder = (data) => {
  return request.post('/tenant/inventory/product-transfer-orders', data);
};

// 获取成品调拨单详情
export const getProductTransferOrder = (orderId) => {
  return request.get(`/tenant/inventory/product-transfer-orders/${orderId}`);
};

// 更新成品调拨单
export const updateProductTransferOrder = (orderId, data) => {
  return request.put(`/tenant/inventory/product-transfer-orders/${orderId}`, data);
};

// 获取成品调拨单明细
export const getProductTransferOrderDetails = (orderId) => {
  return request.get(`/tenant/inventory/product-transfer-orders/${orderId}/details`);
};

// 添加成品调拨单明细
export const addProductTransferOrderDetail = (orderId, data) => {
  return request.post(`/tenant/inventory/product-transfer-orders/${orderId}/details`, data);
};

// 更新成品调拨单明细
export const updateProductTransferOrderDetail = (orderId, detailId, data) => {
  return request.put(`/tenant/inventory/product-transfer-orders/${orderId}/details/${detailId}`, data);
};

// 删除成品调拨单明细
export const deleteProductTransferOrderDetail = (orderId, detailId) => {
  return request.delete(`/tenant/inventory/product-transfer-orders/${orderId}/details/${detailId}`);
};

// 确认成品调拨单
export const confirmProductTransferOrder = (orderId) => {
  return request.post(`/tenant/inventory/product-transfer-orders/${orderId}/confirm`);
};

// 执行成品调拨单
export const executeProductTransferOrder = (orderId) => {
  return request.post(`/tenant/inventory/product-transfer-orders/${orderId}/execute`);
};

// 收货确认成品调拨单
export const receiveProductTransferOrder = (orderId) => {
  return request.post(`/tenant/inventory/product-transfer-orders/${orderId}/receive`);
};

// 取消成品调拨单
export const cancelProductTransferOrder = (orderId, data) => {
  return request.post(`/tenant/inventory/product-transfer-orders/${orderId}/cancel`, data);
};

// 获取仓库成品库存
export const getWarehouseProductInventory = (warehouseId) => {
  return request.get(`/tenant/inventory/warehouses/${warehouseId}/transfer-product-inventory`);
}; 