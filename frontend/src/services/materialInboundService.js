import request from '../utils/request';

const API_BASE = '/tenant/inventory';

// 物料入库单相关API
export const materialInboundService = {
  // 获取入库单列表
  getInboundOrderList: (params = {}) => {
    return request.get(`${API_BASE}/material-inbound-orders`, { params });
  },

  // 获取入库单详情
  getInboundOrderById: (id) => {
    return request.get(`${API_BASE}/material-inbound-orders/${id}`);
  },

  // 创建入库单
  createInboundOrder: (data) => {
    return request.post(`${API_BASE}/material-inbound-orders`, data);
  },

  // 更新入库单
  updateInboundOrder: (id, data) => {
    return request.put(`${API_BASE}/material-inbound-orders/${id}`, data);
  },

  // 删除入库单
  deleteInboundOrder: (id) => {
    return request.delete(`${API_BASE}/material-inbound-orders/${id}`);
  },

  // 审核入库单
  approveInboundOrder: (id, data) => {
    return request.post(`${API_BASE}/material-inbound-orders/${id}/approve`, data);
  },

  // 执行入库单
  executeInboundOrder: (id) => {
    return request.post(`${API_BASE}/material-inbound-orders/${id}/execute`);
  },

  // 取消入库单
  cancelInboundOrder: (id, data) => {
    return request.post(`${API_BASE}/material-inbound-orders/${id}/cancel`, data);
  },

  // 获取入库单明细列表
  getInboundOrderDetails: (orderId) => {
    return request.get(`${API_BASE}/material-inbound-orders/${orderId}/details`);
  },

  // 创建入库单明细
  createInboundOrderDetail: (orderId, data) => {
    return request.post(`${API_BASE}/material-inbound-orders/${orderId}/details`, data);
  },

  // 更新入库单明细
  updateInboundOrderDetail: (orderId, detailId, data) => {
    return request.put(`${API_BASE}/material-inbound-orders/${orderId}/details/${detailId}`, data);
  },

  // 删除入库单明细
  deleteInboundOrderDetail: (orderId, detailId) => {
    return request.delete(`${API_BASE}/material-inbound-orders/${orderId}/details/${detailId}`);
  },

  // 批量创建入库单明细
  batchCreateInboundOrderDetails: (orderId, data) => {
    return request.post(`${API_BASE}/material-inbound-orders/${orderId}/details/batch`, data);
  },

  // 批量更新入库单明细
  batchUpdateInboundOrderDetails: (orderId, data) => {
    return request.put(`${API_BASE}/material-inbound-orders/${orderId}/details/batch`, data);
  },

  // 批量删除入库单明细
  batchDeleteInboundOrderDetails: (orderId, detailIds) => {
    return request.delete(`${API_BASE}/material-inbound-orders/${orderId}/details/batch`, {
      data: { detail_ids: detailIds }
    });
  }
};

// 基础数据相关API
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
  },

  // 获取供应商列表
  getSuppliers: (params = {}) => {
    return request.get('/tenant/basic-data/supplier-management', { params });
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
  // 获取入库统计报表
  getInboundStatistics: (params = {}) => {
    return request.get(`${API_BASE}/reports/material-inbound-statistics`, { params });
  },

  // 获取库存统计报表
  getInventoryStatistics: (params = {}) => {
    return request.get(`${API_BASE}/reports/material-inventory-statistics`, { params });
  },

  // 导出入库单
  exportInboundOrder: (id) => {
    return request.get(`${API_BASE}/material-inbound-orders/${id}/export`, {
      responseType: 'blob'
    });
  },

  // 导出入库单列表
  exportInboundOrderList: (params = {}) => {
    return request.get(`${API_BASE}/material-inbound-orders/export`, {
      params,
      responseType: 'blob'
    });
  }
}; 