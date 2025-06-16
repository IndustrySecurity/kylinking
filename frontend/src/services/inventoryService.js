import request from '../utils/request';

const API_BASE = '/tenant/inventory';

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

// 基础数据相关API (适用于库存总览，支持所有仓库类型)
export const baseDataService = {
  // 获取仓库选项（支持所有仓库类型）
  getWarehouses: (params = {}) => {
    return request.get('/tenant/basic-data/warehouses/options', { params });
  },

  // 获取产品选项
  getProducts: (params = {}) => {
    return request.get('/tenant/basic-data/products', { params });
  },

  // 获取部门选项
  getDepartments: (params = {}) => {
    return request.get('/tenant/basic-data/departments/options', { params });
  },

  // 获取员工选项
  getEmployees: (params = {}) => {
    return request.get('/tenant/basic-data/employees/options', { params });
  },

  // 获取供应商列表
  getSuppliers: (params = {}) => {
    return request.get('/tenant/basic-data/suppliers', { params });
  },

  // 获取客户列表
  getCustomers: (params = {}) => {
    return request.get('/tenant/basic-data/customers', { params });
  },

  // 获取材料列表
  getMaterials: (params = {}) => {
    return request.get('/tenant/basic-data/material-management', { params });
  }
};

// 统计报表相关API
export const statisticsService = {
  // 获取库存统计数据
  getInventoryStatistics: (params = {}) => {
    return request.get(`${API_BASE}/statistics/inventory`, { params });
  },

  // 获取仓库统计数据
  getWarehouseStatistics: (params = {}) => {
    return request.get(`${API_BASE}/statistics/warehouse`, { params });
  },

  // 获取产品统计数据
  getProductStatistics: (params = {}) => {
    return request.get(`${API_BASE}/statistics/product`, { params });
  },

  // 获取库存周转统计
  getInventoryTurnoverStatistics: (params = {}) => {
    return request.get(`${API_BASE}/statistics/turnover`, { params });
  }
};

export default {
  inventoryService,
  baseDataService,
  statisticsService
}; 