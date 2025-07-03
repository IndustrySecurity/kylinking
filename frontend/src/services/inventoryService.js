import request from '../utils/request';

const API_BASE = '/tenant/business/inventory';

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
  },

  // 创建库存记录
  createInventory: (data) => {
    return request.post(`${API_BASE}/inventories`, data);
  },

  // 更新库存记录
  updateInventory: (id, data) => {
    return request.put(`${API_BASE}/inventories/${id}`, data);
  },

  // 获取低库存预警
  getLowStockAlerts: (params = {}) => {
    return request.get(`${API_BASE}/reports/low-stock`, { params });
  },

  // 获取库存统计
  getInventoryStatistics: (params = {}) => {
    return request.get(`${API_BASE}/reports/inventory-statistics`, { params });
  }
};

// 基础数据相关API (修正路径)
export const baseDataService = {
  // 获取仓库选项（支持所有仓库类型）
  getWarehouses: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/warehouses/options', { params });
  },

  // 获取产品选项
  getProducts: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/product-management', { params });
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
    return request.get('/tenant/base-archive/base-data/suppliers', { params });
  },

  // 获取客户列表
  getCustomers: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/customers', { params });
  },

  // 获取材料列表
  getMaterials: (params = {}) => {
    return request.get('/tenant/base-archive/base-data/material-management', { params });
  }
};

// 材料入库相关API
export const materialInboundService = {
  // 获取材料入库列表
  getMaterialInboundList: (params = {}) => {
    return request.get(`${API_BASE}/material-inbound/material-inbound`, { params });
  },

  // 创建材料入库单
  createMaterialInbound: (data) => {
    return request.post(`${API_BASE}/material-inbound/material-inbound`, data);
  },

  // 更新材料入库单
  updateMaterialInbound: (id, data) => {
    return request.put(`${API_BASE}/material-inbound/material-inbound/${id}`, data);
  },

  // 删除材料入库单
  deleteMaterialInbound: (id) => {
    return request.delete(`${API_BASE}/material-inbound/material-inbound/${id}`);
  }
};

// 材料出库相关API
export const materialOutboundService = {
  // 获取材料出库列表
  getMaterialOutboundList: (params = {}) => {
    return request.get(`${API_BASE}/material-outbound/material-outbound`, { params });
  },

  // 创建材料出库单
  createMaterialOutbound: (data) => {
    return request.post(`${API_BASE}/material-outbound/material-outbound`, data);
  },

  // 更新材料出库单
  updateMaterialOutbound: (id, data) => {
    return request.put(`${API_BASE}/material-outbound/material-outbound/${id}`, data);
  },

  // 删除材料出库单
  deleteMaterialOutbound: (id) => {
    return request.delete(`${API_BASE}/material-outbound/material-outbound/${id}`);
  }
};

// 产品盘点相关API
export const productCountService = {
  // 获取盘点列表
  getProductCountList: (params = {}) => {
    return request.get(`${API_BASE}/product-count/product-count`, { params });
  },

  // 创建盘点单
  createProductCount: (data) => {
    return request.post(`${API_BASE}/product-count/product-count`, data);
  },

  // 更新盘点单
  updateProductCount: (id, data) => {
    return request.put(`${API_BASE}/product-count/product-count/${id}`, data);
  },

  // 完成盘点
  completeProductCount: (id) => {
    return request.post(`${API_BASE}/product-count/product-count/${id}/complete`);
  }
};

export default {
  inventoryService,
  baseDataService,
  materialInboundService,
  materialOutboundService,
  productCountService
}; 