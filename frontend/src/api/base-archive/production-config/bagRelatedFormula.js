import request from '../../../utils/request';

/**
 * 袋型相关公式管理API
 */
export const bagRelatedFormulaApi = {
  // 获取袋型相关公式列表
  getBagRelatedFormulas: (params = {}) => {
    return request.get('/tenant/base-archive/production/production-config/bag-related-formulas/', { params });
  },

  // 获取袋型相关公式详情
  getBagRelatedFormula: (formulaId) => {
    return request.get(`/tenant/base-archive/production/production-config/bag-related-formulas/${formulaId}`);
  },

  // 创建袋型相关公式
  createBagRelatedFormula: (data) => {
    return request.post('/tenant/base-archive/production/production-config/bag-related-formulas/', data);
  },

  // 更新袋型相关公式
  updateBagRelatedFormula: (formulaId, data) => {
    return request.put(`/tenant/base-archive/production/production-config/bag-related-formulas/${formulaId}`, data);
  },

  // 删除袋型相关公式
  deleteBagRelatedFormula: (formulaId) => {
    return request.delete(`/tenant/base-archive/production/production-config/bag-related-formulas/${formulaId}`);
  },

  // 批量更新袋型相关公式
  batchUpdateBagRelatedFormulas: (updates) => {
    return request.put('/tenant/base-archive/production/production-config/bag-related-formulas/batch', { updates });
  },

  // 获取袋型相关公式选项数据
  getBagRelatedFormulaOptions: () => {
    return request.get('/tenant/base-archive/production/production-config/bag-related-formulas/options');
  }
}; 