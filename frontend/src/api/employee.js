import request from '@/utils/request'

const API_BASE = '/tenant/basic-data'

// 获取员工列表
export const getEmployees = (params) => {
  return request({
    url: `${API_BASE}/employees`,
    method: 'get',
    params
  })
}

// 获取员工详情
export const getEmployee = (id) => {
  return request({
    url: `${API_BASE}/employees/${id}`,
    method: 'get'
  })
}

// 创建员工
export const createEmployee = (data) => {
  return request({
    url: `${API_BASE}/employees`,
    method: 'post',
    data
  })
}

// 更新员工
export const updateEmployee = (id, data) => {
  return request({
    url: `${API_BASE}/employees/${id}`,
    method: 'put',
    data
  })
}

// 删除员工
export const deleteEmployee = (id) => {
  return request({
    url: `${API_BASE}/employees/${id}`,
    method: 'delete'
  })
}

// 批量更新员工
export const batchUpdateEmployees = (data) => {
  return request({
    url: `${API_BASE}/employees/batch`,
    method: 'put',
    data
  })
}

// 获取员工选项
export const getEmployeeOptions = () => {
  return request({
    url: `${API_BASE}/employees/options`,
    method: 'get'
  })
}

// 获取在职状态选项
export const getEmploymentStatusOptions = () => {
  return request({
    url: `${API_BASE}/employees/employment-status-options`,
    method: 'get'
  })
}

// 获取业务类型选项
export const getBusinessTypeOptions = () => {
  return request({
    url: `${API_BASE}/employees/business-type-options`,
    method: 'get'
  })
}

// 获取性别选项
export const getGenderOptions = () => {
  return request({
    url: `${API_BASE}/employees/gender-options`,
    method: 'get'
  })
}

// 获取评量流程级别选项
export const getEvaluationLevelOptions = () => {
  return request({
    url: `${API_BASE}/employees/evaluation-level-options`,
    method: 'get'
  })
}

// 获取下一个员工工号
export const getNextEmployeeId = () => {
  return request({
    url: `${API_BASE}/employees/next-employee-id`,
    method: 'get'
  })
} 