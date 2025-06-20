import request from '../../utils/request';

/**
 * 材料调拨API
 */

// 获取调拨单列表
export const getMaterialTransferOrders = (params) => {
  return request.get('/tenant/inventory/material-transfer-orders', { params });
};

// 创建调拨单
export const createMaterialTransferOrder = (data) => {
  return request.post('/tenant/inventory/material-transfer-orders', data);
};

// 获取调拨单详情
export const getMaterialTransferOrder = (orderId) => {
  return request.get(`/tenant/inventory/material-transfer-orders/${orderId}`);
};

// 更新调拨单
export const updateMaterialTransferOrder = (orderId, data) => {
  return request.put(`/tenant/inventory/material-transfer-orders/${orderId}`, data);
};

// 获取调拨单明细
export const getMaterialTransferOrderDetails = (orderId) => {
  return request.get(`/tenant/inventory/material-transfer-orders/${orderId}/details`);
};

// 添加调拨明细
export const addMaterialTransferOrderDetail = (orderId, data) => {
  return request.post(`/tenant/inventory/material-transfer-orders/${orderId}/details`, data);
};

// 更新调拨明细
export const updateMaterialTransferOrderDetail = (orderId, detailId, data) => {
  return request.put(`/tenant/inventory/material-transfer-orders/${orderId}/details/${detailId}`, data);
};

// 删除调拨明细
export const deleteMaterialTransferOrderDetail = (orderId, detailId) => {
  return request.delete(`/tenant/inventory/material-transfer-orders/${orderId}/details/${detailId}`);
};

// 确认调拨单
export const confirmMaterialTransferOrder = (orderId) => {
  return request.post(`/tenant/inventory/material-transfer-orders/${orderId}/confirm`);
};

// 执行调拨单（出库）
export const executeMaterialTransferOrder = (orderId) => {
  return request.post(`/tenant/inventory/material-transfer-orders/${orderId}/execute`);
};

// 接收调拨单（入库）
export const receiveMaterialTransferOrder = (orderId) => {
  return request.post(`/tenant/inventory/material-transfer-orders/${orderId}/receive`);
};

// 取消调拨单
export const cancelMaterialTransferOrder = (orderId, data = {}) => {
  return request.post(`/tenant/inventory/material-transfer-orders/${orderId}/cancel`, data);
};

// 获取仓库可调拨材料
export const getWarehouseTransferMaterials = (warehouseId) => {
  return request.get(`/tenant/inventory/warehouses/${warehouseId}/transfer-materials`);
}; 