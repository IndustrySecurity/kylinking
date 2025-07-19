import request from '../../../utils/request';

const API_BASE = '/tenant/business/inventory/product-inbound';

// 成品入库单相关API
export const finishedGoodsInboundService = {
  // 获取入库单列表
  getInboundOrderList: (params = {}) => {
    return request.get(`${API_BASE}/product-inbound-orders`, { params });
  },

  // 获取入库单详情
  getInboundOrderById: (id) => {
    return request.get(`${API_BASE}/product-inbound-orders/${id}`);
  },

  // 创建入库单
  createInboundOrder: (data) => {
    return request.post(`${API_BASE}/product-inbound-orders`, data);
  },

  // 更新入库单
  updateInboundOrder: (id, data) => {
    return request.put(`${API_BASE}/product-inbound-orders/${id}`, data);
  },

  // 删除入库单
  deleteInboundOrder: (id) => {
    return request.delete(`${API_BASE}/product-inbound-orders/${id}`);
  },

  // 审核入库单
  approveInboundOrder: (id, data) => {
    return request.post(`${API_BASE}/product-inbound-orders/${id}/approve`, data);
  },

  // 执行入库单
  executeInboundOrder: (id) => {
    return request.post(`${API_BASE}/product-inbound-orders/${id}/execute`);
  },

  // 取消入库单
  cancelInboundOrder: (id, data) => {
    return request.post(`${API_BASE}/product-inbound-orders/${id}/cancel`, data);
  },

  // 获取入库单明细列表
  getInboundOrderDetails: (orderId) => {
    return request.get(`${API_BASE}/product-inbound-orders/${orderId}/details`);
  },

  // 创建入库单明细
  createInboundOrderDetail: (orderId, data) => {
    return request.post(`${API_BASE}/product-inbound-orders/${orderId}/details`, data);
  },

  // 更新入库单明细
  updateInboundOrderDetail: (orderId, detailId, data) => {
    return request.put(`${API_BASE}/product-inbound-orders/${orderId}/details/${detailId}`, data);
  },

  // 删除入库单明细
  deleteInboundOrderDetail: (orderId, detailId) => {
    return request.delete(`${API_BASE}/product-inbound-orders/${orderId}/details/${detailId}`);
  },

  // 批量创建入库单明细
  batchCreateInboundOrderDetails: (orderId, data) => {
    return request.post(`${API_BASE}/product-inbound-orders/${orderId}/details/batch`, data);
  },

  // 批量更新入库单明细
  batchUpdateInboundOrderDetails: (orderId, data) => {
    return request.put(`${API_BASE}/product-inbound-orders/${orderId}/details/batch`, data);
  },

  // 批量删除入库单明细
  batchDeleteInboundOrderDetails: (orderId, detailIds) => {
    return request.delete(`${API_BASE}/product-inbound-orders/${orderId}/details/batch`, {
      data: { detail_ids: detailIds }
    });
  }
};

// 基础数据相关API
export const baseDataService = {
  // 获取仓库选项（只获取成品仓）
  getWarehouses: (params = {}) => {
    return request.get('/tenant/base-archive/production-archive/warehouses/options', { 
      params: { ...params, warehouse_type: 'finished_goods' }
    });
  },

  // 获取产品选项
  getProducts: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/product-management/', { params });
  },

  // 获取部门选项
  getDepartments: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/departments/options', { params });
  },

  // 获取员工选项
  getEmployees: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/employees/options', { params });
  },

  // 获取供应商列表
  getSuppliers: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/suppliers/', { params });
  },

  // 获取客户列表
  getCustomers: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/customers/', { params });
  },

  // 获取单位列表
  getUnits: () => {
    return request.get('/tenant/base-archive/production-archive/units/options');
  }
};

// 库存相关API
export const inventoryService = {
  // 获取库存列表
  getInventoryList: (params = {}) => {
    return request.get('/tenant/business/inventory/inventories/', { params });
  },

  // 获取库存详情
  getInventoryById: (id) => {
    return request.get(`/tenant/business/inventory/inventories/${id}`);
  },

  // 获取库存事务记录
  getInventoryTransactions: (params = {}) => {
    return request.get('/tenant/business/inventory/inventory-transactions/', { params });
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
  // 获取入库统计报表
  getInboundStatistics: (params = {}) => {
    return request.get(`${API_BASE}/reports/inbound-statistics`, { params });
  },

  // 获取库存统计报表
  getInventoryStatistics: (params = {}) => {
    return request.get('/tenant/business/inventory/reports/inventory-statistics', { params });
  },

  // 导出入库单
  exportInboundOrder: (id) => {
    return request.get(`${API_BASE}/${id}/export`, {
      responseType: 'blob'
    });
  },

  // 导出入库单列表
  exportInboundOrderList: (params = {}) => {
    return request.get(`${API_BASE}/export`, {
      params,
      responseType: 'blob'
    });
  }
};

export default {
  finishedGoodsInboundService,
  baseDataService,
  inventoryService,
  reportService
}; 