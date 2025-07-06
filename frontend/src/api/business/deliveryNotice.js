/**
 * 送货通知单服务
 */
import request from '../../utils/request';

class DeliveryNoticeService {
  baseURL = '/tenant/business/sales';

  /**
   * 获取送货通知单列表
   */
  getDeliveryNotices = async (params = {}) => {
    return request.get(`${this.baseURL}/delivery-notices`, { params });
  };

  /**
   * 获取送货通知单详情
   */
  getDeliveryNoticeById = async (id) => {
    return request.get(`${this.baseURL}/delivery-notices/${id}`);
  };

  /**
   * 创建送货通知单
   */
  createDeliveryNotice = async (data) => {
    return request.post(`${this.baseURL}/delivery-notices`, data);
  };

  /**
   * 更新送货通知单
   */
  updateDeliveryNotice = async (id, data) => {
    return request.put(`${this.baseURL}/delivery-notices/${id}`, data);
  };

  /**
   * 删除送货通知单
   */
  deleteDeliveryNotice = async (id) => {
    return request.delete(`${this.baseURL}/delivery-notices/${id}`);
  };

  /**
   * 确认送货通知
   */
  confirmDelivery = async (id) => {
    return request.post(`${this.baseURL}/delivery-notices/${id}/confirm`);
  };

  /**
   * 根据销售订单获取待安排发货明细
   */
  getDetailsFromSalesOrder = async (salesOrderId) => {
    return request.get(`${this.baseURL}/delivery-notices/sales-order/${salesOrderId}/details`);
  };

  /**
   * 发货
   */
  shipDelivery = async (id) => {
    return request.post(`${this.baseURL}/delivery-notices/${id}/ship`);
  };

  /**
   * 完成送货
   */
  completeDelivery = async (id) => {
    return request.post(`${this.baseURL}/delivery-notices/${id}/complete`);
  };
}

const deliveryNoticeService = new DeliveryNoticeService();

export default deliveryNoticeService; 