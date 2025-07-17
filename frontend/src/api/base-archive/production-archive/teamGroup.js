import request from '../../../utils/request'

// 获取班组列表
export function getTeamGroups(params) {
  return request({
    url: '/tenant/basic-data/team-groups/',
    method: 'get',
    params
  })
}

// 获取班组详情
export function getTeamGroup(id) {
  return request({
    url: `/tenant/basic-data/team-groups/${id}`,
    method: 'get'
  })
}

// 创建班组
export function createTeamGroup(data) {
  return request({
    url: '/tenant/basic-data/team-groups/',
    method: 'post',
    data
  })
}

// 更新班组
export function updateTeamGroup(id, data) {
  return request({
    url: `/tenant/basic-data/team-groups/${id}`,
    method: 'put',
    data
  })
}

// 删除班组
export function deleteTeamGroup(id) {
  return request({
    url: `/tenant/basic-data/team-groups/${id}`,
    method: 'delete'
  })
}

// 获取班组选项
export function getTeamGroupOptions() {
  return request({
    url: '/tenant/basic-data/team-groups/options',
    method: 'get'
  })
}

// 获取班组表单选项数据
export function getTeamGroupFormOptions() {
  return request({
    url: '/tenant/basic-data/team-groups/form-options',
    method: 'get'
  })
}

// 班组成员管理
export function addTeamMember(teamGroupId, data) {
  return request({
    url: `/tenant/basic-data/team-groups/${teamGroupId}/members`,
    method: 'post',
    data
  })
}

export function updateTeamMember(memberId, data) {
  return request({
    url: `/tenant/basic-data/team-members/${memberId}`,
    method: 'put',
    data
  })
}

export function deleteTeamMember(memberId) {
  return request({
    url: `/tenant/basic-data/team-members/${memberId}`,
    method: 'delete'
  })
}

// 班组机台管理
export function addTeamMachine(teamGroupId, data) {
  return request({
    url: `/tenant/basic-data/team-groups/${teamGroupId}/machines`,
    method: 'post',
    data
  })
}

export function deleteTeamMachine(machineId) {
  return request({
    url: `/tenant/basic-data/team-machines/${machineId}`,
    method: 'delete'
  })
}

// 班组工序分类管理
export function addTeamProcess(teamGroupId, data) {
  return request({
    url: `/tenant/basic-data/team-groups/${teamGroupId}/processes`,
    method: 'post',
    data
  })
}

export function deleteTeamProcess(processId) {
  return request({
    url: `/tenant/basic-data/team-processes/${processId}`,
    method: 'delete'
  })
} 