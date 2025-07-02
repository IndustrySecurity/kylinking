import request from '../../utils/request';

/**
 * 材料调拨API
 */

// 获取原料调拨列表
export const getMaterialTransfers = (params) => {
  return request({
    url: '/tenant/business/inventory/material-transfer',
    method: 'get',
    params
  });
};

// 创建原料调拨
export const createMaterialTransfer = (data) => {
  return request({
    url: '/tenant/business/inventory/material-transfer',
    method: 'post',
    data
  });
};

// 更新原料调拨
export const updateMaterialTransfer = (id, data) => {
  return request({
    url: `/tenant/business/inventory/material-transfer/${id}`,
    method: 'put',
    data
  });
};

// 删除原料调拨
export const deleteMaterialTransfer = (id) => {
  return request({
    url: `/tenant/business/inventory/material-transfer/${id}`,
    method: 'delete'
  });
};

// 获取原料调拨详情
export const getMaterialTransferById = (id) => {
  return request({
    url: `/tenant/business/inventory/material-transfer/${id}`,
    method: 'get'
  });
};

// 确认原料调拨
export const confirmMaterialTransfer = (id) => {
  return request({
    url: `/tenant/business/inventory/material-transfer/${id}/confirm`,
    method: 'post'
  });
};

// 获取原料库存信息
export const getMaterialStock = (materialId, warehouseId) => {
  return request({
    url: `/tenant/business/inventory/material-stock/${materialId}/${warehouseId}`,
    method: 'get'
  });
};

// 导出原料调拨数据
export const exportMaterialTransfer = (params) => {
  return request({
    url: '/tenant/business/inventory/material-transfer/export',
    method: 'get',
    params,
    responseType: 'blob'
  });
};

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

// 确认调拨单
export const confirmMaterialTransferOrder = (orderId) => {
  return request.post(`/tenant/inventory/material-transfer-orders/${orderId}/confirm`);
};

// 统一导出API对象
export const materialTransferApi = {
  // 基础调拨API
  getMaterialTransfers,
  createMaterialTransfer,
  updateMaterialTransfer,
  deleteMaterialTransfer,
  getMaterialTransferById,
  confirmMaterialTransfer,
  getMaterialStock,
  exportMaterialTransfer,
  // 调拨单API
  getMaterialTransferOrders,
  createMaterialTransferOrder,
  getMaterialTransferOrder,
  updateMaterialTransferOrder,
  getMaterialTransferOrderDetails,
  addMaterialTransferOrderDetail,
  updateMaterialTransferOrderDetail,
  deleteMaterialTransferOrderDetail,
  confirmMaterialTransferOrder,
  executeMaterialTransferOrder,
  receiveMaterialTransferOrder,
  cancelMaterialTransferOrder,
  getWarehouseTransferMaterials
}; 