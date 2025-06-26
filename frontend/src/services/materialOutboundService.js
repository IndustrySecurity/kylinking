import request from '../utils/request';

const API_BASE = '/tenant/inventory';

// 物料出库单相关API
export const materialOutboundService = {
  // 获取出库单列表
  getOutboundOrderList: (params = {}) => {
    return request.get(`${API_BASE}/material-outbound-orders`, { params });
  },

  // 获取出库单详情
  getOutboundOrderById: (id) => {
    return request.get(`${API_BASE}/material-outbound-orders/${id}`);
  },

  // 创建出库单
  createOutboundOrder: (data) => {
    return request.post(`${API_BASE}/material-outbound-orders`, data);
  },

  // 更新出库单
  updateOutboundOrder: (id, data) => {
    return request.put(`${API_BASE}/material-outbound-orders/${id}`, data);
  },

  // 删除出库单
  deleteOutboundOrder: (id) => {
    return request.delete(`${API_BASE}/material-outbound-orders/${id}`);
  },

  // 审核出库单
  approveOutboundOrder: (id, data) => {
    return request.post(`${API_BASE}/material-outbound-orders/${id}/approve`, data);
  },

  // 执行出库单
  executeOutboundOrder: (id) => {
    return request.post(`${API_BASE}/material-outbound-orders/${id}/execute`);
  },

  // 取消出库单
  cancelOutboundOrder: (id, data) => {
    return request.post(`${API_BASE}/material-outbound-orders/${id}/cancel`, data);
  },

  // 获取出库单明细列表
  getOutboundOrderDetails: (orderId) => {
    return request.get(`${API_BASE}/material-outbound-orders/${orderId}/details`);
  },

  // 创建出库单明细
  createOutboundOrderDetail: (orderId, data) => {
    return request.post(`${API_BASE}/material-outbound-orders/${orderId}/details`, data);
  },

  // 更新出库单明细
  updateOutboundOrderDetail: (orderId, detailId, data) => {
    return request.put(`${API_BASE}/material-outbound-orders/${orderId}/details/${detailId}`, data);
  },

  // 删除出库单明细
  deleteOutboundOrderDetail: (orderId, detailId) => {
    return request.delete(`${API_BASE}/material-outbound-orders/${orderId}/details/${detailId}`);
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

// 基础数据相关API (重用物料入库的基础数据服务)
export const baseDataService = {
  // 获取仓库选项（只获取物料仓库）
  getWarehouses: (params = {}) => {
    return request.get(`${API_BASE}/warehouses`, { 
      params: { ...params, warehouse_type: 'material' }
    });
  },

  // 获取材料选项
  getMaterials: (params = {}) => {
    return request.get('/tenant/basic-data/material-management', { params });
  },

  // 获取部门选项
  getDepartments: (params = {}) => {
    return request.get(`${API_BASE}/departments/options`, { params });
  },

  // 获取员工选项
  getEmployees: (params = {}) => {
    return request.get('/tenant/basic-data/employees/options', { params });
  }
};

// 库存相关API
export const inventoryService = {
  // 获取库存列表
  getInventoryList: (params = {}) => {
    return request.get(`${API_BASE}/inventories`, { params });
  },

  // 获取库存详情
  getInventoryById: (id) => {
    return request.get(`${API_BASE}/inventories/${id}`);
  },

  // 获取可用库存（用于出库检查）
  getAvailableInventory: (params = {}) => {
    return request.get(`${API_BASE}/inventories/available`, { params });
  },

  // 获取库存事务记录
  getInventoryTransactions: (params = {}) => {
    return request.get(`${API_BASE}/inventory-transactions`, { params });
  },

  // 预留库存
  reserveInventory: (data) => {
    return request.post(`${API_BASE}/inventories/reserve`, data);
  },

  // 释放预留库存
  releaseReservedInventory: (data) => {
    return request.post(`${API_BASE}/inventories/release-reserved`, data);
  },

  // 调整库存
  adjustInventory: (data) => {
    return request.post(`${API_BASE}/inventories/adjust`, data);
  }
};

// 报表相关API
export const reportService = {
  // 获取出库统计报表
  getOutboundStatistics: (params = {}) => {
    return request.get(`${API_BASE}/reports/material-outbound-statistics`, { params });
  },

  // 获取库存统计报表
  getInventoryStatistics: (params = {}) => {
    return request.get(`${API_BASE}/reports/material-inventory-statistics`, { params });
  },

  // 导出出库单
  exportOutboundOrder: (id) => {
    return request.get(`${API_BASE}/material-outbound-orders/${id}/export`, {
      responseType: 'blob'
    });
  },

  // 导出出库单列表
  exportOutboundOrderList: (params = {}) => {
    return request.get(`${API_BASE}/material-outbound-orders/export`, {
      params,
      responseType: 'blob'
    });
  }
}; 