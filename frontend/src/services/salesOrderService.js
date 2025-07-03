/**
 * 销售订单服务
 */
import request from '../utils/request';

class SalesOrderService {
  // 基础API路径
  baseURL = '/tenant/business/sales';

  /**
   * 获取销售订单列表
   */
  getSalesOrders = async (params = {}) => {
    return request.get(`${this.baseURL}/sales-orders`, { params });
  };

  /**
   * 获取销售订单详情
   */
  getSalesOrderById = async (id) => {
    return request.get(`${this.baseURL}/sales-orders/${id}`);
  };

  /**
   * 创建销售订单
   */
  createSalesOrder = async (data) => {
    return request.post(`${this.baseURL}/sales-orders`, data);
  };

  /**
   * 更新销售订单
   */
  updateSalesOrder = async (id, data) => {
    return request.put(`${this.baseURL}/sales-orders/${id}`, data);
  };

  /**
   * 删除销售订单
   */
  deleteSalesOrder = async (id) => {
    return request.delete(`${this.baseURL}/sales-orders/${id}`);
  };

  /**
   * 审批销售订单
   */
  approveSalesOrder = async (id) => {
    return request.post(`${this.baseURL}/sales-orders/${id}/approve`);
  };

  /**
   * 取消销售订单
   */
  cancelSalesOrder = async (id) => {
    return request.post(`${this.baseURL}/sales-orders/${id}/cancel`);
  };

  /**
   * 批量删除销售订单
   */
  batchDeleteSalesOrders = async (ids) => {
    return request.post(`${this.baseURL}/sales-orders/batch-delete`, { ids });
  };

  /**
   * 批量审批销售订单
   */
  batchApproveSalesOrders = async (ids) => {
    return request.post(`${this.baseURL}/sales-orders/batch-approve`, { ids });
  };

  /**
   * 获取客户选项
   */
  getCustomerOptions = async () => {
    return request.get(`${this.baseURL}/customers/options`);
  };

  /**
   * 获取产品选项
   */
  getProductOptions = async () => {
    return request.get(`${this.baseURL}/products/options`);
  };

  /**
   * 获取材料选项
   */
  getMaterialOptions = async () => {
    return request.get(`${this.baseURL}/materials/options`);
  };

  /**
   * 获取单位选项
   */
  getUnitOptions = async () => {
    return request.get(`${this.baseURL}/units/options`);
  };

  /**
   * 获取税收选项
   */
  getTaxOptions = async () => {
    return request.get(`${this.baseURL}/taxes/options`);
  };

  /**
   * 获取币种选项
   */
  getCurrencyOptions = async () => {
    return request.get(`${this.baseURL}/currencies/options`);
  };

  /**
   * 获取仓库选项
   */
  getWarehouseOptions = async () => {
    return request.get(`${this.baseURL}/warehouses/options`);
  };

  /**
   * 获取员工选项
   */
  getEmployeeOptions = async () => {
    return request.get(`${this.baseURL}/employees/options`);
  };

  /**
   * 获取联系人选项
   */
  getContactOptions = async (customerId) => {
    return request.get(`${this.baseURL}/contacts/options`, { 
      params: { customer_id: customerId } 
    });
  };

  /**
   * 导出销售订单
   */
  exportSalesOrders = async (params = {}) => {
    return request.get(`${this.baseURL}/sales-orders/export`, { 
      params,
      responseType: 'blob'
    });
  };

  /**
   * 获取销售订单统计
   */
  getSalesOrderStats = async (params = {}) => {
    return request.get(`${this.baseURL}/sales-orders/stats`, { params });
  };

  /**
   * 获取销售订单报表
   */
  getSalesOrderReport = async (params = {}) => {
    return request.get(`${this.baseURL}/sales-orders/report`, { params });
  };

  /**
   * 获取产品库存信息
   */
  getProductInventory = async (productId) => {
    return request.get(`${this.baseURL}/products/${productId}/inventory`);
  };

  /**
   * 获取客户详细信息用于自动填充表单
   */
  getCustomerDetails = async (customerId) => {
    return request.get(`${this.baseURL}/customers/${customerId}/details`);
  };

  /**
   * 获取客户联系人选项
   */
  getCustomerContacts = async (customerId) => {
    return request.get(`${this.baseURL}/customers/${customerId}/contacts`);
  };

  /**
   * 获取产品详细信息用于自动填充订单明细
   */
  getProductDetails = async (productId) => {
    return request.get(`${this.baseURL}/products/${productId}/details`);
  };

  /**
   * 获取客户税率信息
   */
  getCustomerTaxRate = async (customerId) => {
    return request.get(`${this.baseURL}/customers/${customerId}/tax-rate`);
  };

  /**
   * 获取销售订单状态选项
   */
  getOrderStatusOptions = async () => {
    return request.get(`${this.baseURL}/sales-orders/status-options`);
  };

  /**
   * 获取付款方式选项
   */
  getPaymentMethodOptions = async () => {
    return request.get(`${this.baseURL}/payment-methods/options`);
  };

  /**
   * 获取配送方式选项
   */
  getDeliveryMethodOptions = async () => {
    return request.get(`${this.baseURL}/delivery-methods/options`);
  };
}

// 发货通知服务
export class DeliveryNoticeService {
  baseURL = '/tenant/business/sales/delivery';

  /**
   * 获取发货通知列表
   */
  getDeliveryNotices = async (params = {}) => {
    return request.get(`${this.baseURL}/delivery-notices`, { params });
  };

  /**
   * 获取发货通知详情
   */
  getDeliveryNoticeById = async (id) => {
    return request.get(`${this.baseURL}/delivery-notices/${id}`);
  };

  /**
   * 创建发货通知
   */
  createDeliveryNotice = async (data) => {
    return request.post(`${this.baseURL}/delivery-notices`, data);
  };

  /**
   * 更新发货通知
   */
  updateDeliveryNotice = async (id, data) => {
    return request.put(`${this.baseURL}/delivery-notices/${id}`, data);
  };

  /**
   * 删除发货通知
   */
  deleteDeliveryNotice = async (id) => {
    return request.delete(`${this.baseURL}/delivery-notices/${id}`);
  };

  /**
   * 确认发货
   */
  confirmDelivery = async (id) => {
    return request.post(`${this.baseURL}/delivery-notices/${id}/confirm`);
  };
}

// 创建单例实例
const salesOrderService = new SalesOrderService();
const deliveryNoticeService = new DeliveryNoticeService();

export { deliveryNoticeService };
export default salesOrderService; 