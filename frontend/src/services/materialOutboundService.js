import request from '../utils/request';

const API_BASE = '/tenant/business/inventory/material-outbound';

// 物料出库单相关API
export const materialOutboundService = {
  // 获取出库单列表
  getOutboundOrderList: (params = {}) => {
    return request.get(`${API_BASE}/outbound-orders`, { params });
  },

  // 获取出库单详情
  getOutboundOrderById: (id) => {
    return request.get(`${API_BASE}/outbound-orders/${id}`);
  },

  // 创建出库单
  createOutboundOrder: (data) => {
    return request.post(`${API_BASE}/outbound-orders`, data);
  },

  // 更新出库单
  updateOutboundOrder: (id, data) => {
    return request.put(`${API_BASE}/outbound-orders/${id}`, data);
  },

  // 删除出库单
  deleteOutboundOrder: (id) => {
    return request.delete(`${API_BASE}/outbound-orders/${id}`);
  },

  // 审核出库单
  approveOutboundOrder: (id, data) => {
    return request.post(`${API_BASE}/outbound-orders/${id}/approve`, data);
  },

  // 执行出库单
  executeOutboundOrder: (id) => {
    return request.post(`${API_BASE}/outbound-orders/${id}/execute`);
  },

  // 取消出库单
  cancelOutboundOrder: (id, data) => {
    return request.post(`${API_BASE}/outbound-orders/${id}/cancel`, data);
  },

  // 获取出库单明细列表
  getOutboundOrderDetails: (orderId) => {
    return request.get(`${API_BASE}/outbound-orders/${orderId}/details`);
  },

  // 创建出库单明细
  createOutboundOrderDetail: (orderId, data) => {
    return request.post(`${API_BASE}/outbound-orders/${orderId}/details`, data);
  },

  // 更新出库单明细
  updateOutboundOrderDetail: (orderId, detailId, data) => {
    return request.put(`${API_BASE}/outbound-orders/${orderId}/details/${detailId}`, data);
  },

  // 删除出库单明细
  deleteOutboundOrderDetail: (orderId, detailId) => {
    return request.delete(`${API_BASE}/outbound-orders/${orderId}/details/${detailId}`);
  },

  // 批量创建出库单明细
  batchCreateOutboundOrderDetails: (orderId, data) => {
    return request.post(`${API_BASE}/material-outbound-orders/${orderId}/details/batch`, data);
  },

  // 批量更新出库单明细
  batchUpdateOutboundOrderDetails: (orderId, data) => {
    return request.put(`${API_BASE}/material-outbound-orders/${orderId}/details/batch`, data);
  },

  // 批量删除出库单明细
  batchDeleteOutboundOrderDetails: (orderId, detailIds) => {
    return request.delete(`${API_BASE}/material-outbound-orders/${orderId}/details/batch`, {
      data: { detail_ids: detailIds }
    });
  }
};

// 基础数据相关API (修正路径)
export const baseDataService = {
  // 获取仓库选项（只获取物料仓库）
  getWarehouses: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/warehouses/options', { 
      params: { ...params, warehouse_type: 'material' }
    });
  },

  // 获取材料选项
  getMaterials: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/material-management', { params });
  },

  // 获取部门选项
  getDepartments: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/departments/options', { params });
  },

  // 获取员工选项
  getEmployees: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/employees/options', { params });
  }
};

// 库存相关API
export const inventoryService = {
  // 获取库存列表
  getInventoryList: (params = {}) => {
    return request.get('/tenant/business/inventory/inventories', { params });
  },

  // 获取库存详情
  getInventoryById: (id) => {
    return request.get(`/tenant/business/inventory/inventories/${id}`);
  },

  // 获取可用库存（用于出库检查）
  getAvailableInventory: (params = {}) => {
    return request.get('/tenant/business/inventory/inventories/available', { params });
  },

  // 获取库存事务记录
  getInventoryTransactions: (params = {}) => {
    return request.get('/tenant/business/inventory/inventory-transactions', { params });
  },

  // 预留库存
  reserveInventory: (data) => {
    return request.post('/tenant/business/inventory/inventories/reserve', data);
  },

  // 释放预留库存
  releaseReservedInventory: (data) => {
    return request.post('/tenant/business/inventory/inventories/release-reserved', data);
  },

  // 调整库存
  adjustInventory: (data) => {
    return request.post('/tenant/business/inventory/inventories/adjust', data);
  }
};

// 报表相关API
export const reportService = {
  // 获取出库统计报表
  getOutboundStatistics: (params = {}) => {
    return request.get(`${API_BASE}/reports/outbound-statistics`, { params });
  },

  // 获取库存统计报表
  getInventoryStatistics: (params = {}) => {
    return request.get('/tenant/business/inventory/reports/inventory-statistics', { params });
  },

  // 导出出库单
  exportOutboundOrder: (id) => {
    return request.get(`${API_BASE}/outbound-orders/${id}/export`, {
      responseType: 'blob'
    });
  },

  // 导出出库单列表
  exportOutboundOrderList: (params = {}) => {
    return request.get(`${API_BASE}/outbound-orders/export`, {
      params,
      responseType: 'blob'
    });
  }
};

export default {
  materialOutboundService,
  baseDataService,
  inventoryService,
  reportService
}; 