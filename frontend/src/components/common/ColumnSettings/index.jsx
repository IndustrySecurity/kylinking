import React from 'react';
import {
  Space,
  Checkbox,
  Badge,
  Button,
  Divider,
  message,
  Typography
} from 'antd';
import {
  MenuOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useAutoScroll } from '../../../hooks/useAutoScroll';

const { Text: AntText } = Typography;

const ColumnSettings = ({
  fieldConfig = {},
  dynamicFields = [],
  fieldGroups = {},
  columnConfig = {},
  columnSettingOrder = [],
  isAdmin = false,
  onConfigChange,
  onOrderChange,
  onSave,
  onReset,
  title = "列显示设置"
}) => {
  // 自动滚动功能
  const { scrollContainerRef, setDropEffect, handleDragStart, handleDragEnd } = useAutoScroll();

  // 移动列功能
  const moveColumn = (dragKey, targetIndex) => {
    console.log('移动列:', dragKey, '到位置:', targetIndex);
    
    // 使用 getDisplayFields 获取基础顺序，确保所有字段都在其中
    const baseOrder = getDisplayFields();
    const dragIndex = baseOrder.indexOf(dragKey);
    
    console.log('基础顺序:', baseOrder);
    console.log('拖拽项索引:', dragIndex);
    
    if (dragIndex === -1) {
      // 如果拖拽项不在基础顺序中，添加到末尾
      baseOrder.push(dragKey);
      console.log('拖拽项不在基础顺序中，添加到末尾:', baseOrder);
      onOrderChange(baseOrder);
      return;
    }
    
    if (dragIndex === targetIndex) {
      // 如果目标位置就是当前位置，不做任何操作
      console.log('目标位置就是当前位置，不做操作');
      return;
    }
    
    // 移除拖拽项
    baseOrder.splice(dragIndex, 1);
    
    // 计算插入位置
    let insertIndex = targetIndex;
    
    // 如果移除的项在目标位置之前，需要调整插入位置
    if (dragIndex < targetIndex) {
      insertIndex = targetIndex - 1;
    }
    
    // 确保插入位置在有效范围内
    insertIndex = Math.max(0, Math.min(insertIndex, baseOrder.length));
    
    console.log('插入位置:', insertIndex);
    
    // 插入到目标位置
    baseOrder.splice(insertIndex, 0, dragKey);
    
    console.log('新顺序:', baseOrder);
    onOrderChange(baseOrder);
  };

  // 获取所有字段列表
  const getAllFields = () => {
    const baseFields = Object.keys(fieldConfig || {}).filter(key => key !== 'action');
    const dynamicFieldNames = Array.isArray(dynamicFields) ? dynamicFields.map(field => field.field_name) : [];
    return [...baseFields, ...dynamicFieldNames];
  };

  // 获取显示字段列表
  const getDisplayFields = () => {
    const allFields = getAllFields();
    let displayFields = [];
    
    // 始终确保包含所有字段
    if (Array.isArray(columnSettingOrder) && columnSettingOrder.length > 0) {
      // 先添加 columnSettingOrder 中的字段
      columnSettingOrder.forEach(field => {
        if (allFields.includes(field) && !displayFields.includes(field)) {
          displayFields.push(field);
        }
      });
    } else {
      // 使用默认顺序
      const defaultOrder = [
        'category_name', 'category_code', 'description', 'sort_order', 'is_enabled',
        'created_by_name', 'created_at', 'updated_by_name', 'updated_at'
      ];
      defaultOrder.forEach(field => {
        if (allFields.includes(field) && !displayFields.includes(field)) {
          displayFields.push(field);
        }
      });
    }
    
    // 确保所有字段都在列表中
    allFields.forEach(field => {
      if (!displayFields.includes(field)) {
        displayFields.push(field);
      }
    });
    
    return displayFields;
  };

  // 获取可见字段列表
  const getVisibleFormFields = () => {
    if (!fieldConfig) return [];
    
    const baseFields = Object.keys(fieldConfig || {}).filter(key => key !== 'action');
    const dynamicFieldNames = Array.isArray(dynamicFields) ? dynamicFields.map(field => field.field_name) : [];
    const allFields = [...baseFields, ...dynamicFieldNames];
    
    if (Object.keys(columnConfig || {}).length === 0) {
      return allFields;
    }
    
    return allFields.filter(key => {
      if (dynamicFieldNames.includes(key)) {
        return !(key in (columnConfig || {})) || columnConfig[key] === true;
      }
      
      if (key === 'action') return false;
      
      const config = fieldConfig[key];
      if (config && config.required) {
        return true;
      }
      
      return !(key in (columnConfig || {})) || columnConfig[key] === true;
    });
  };

  // 渲染列设置界面
  const renderColumnSettings = () => {
    if (!fieldConfig || !Array.isArray(dynamicFields)) {
      return null;
    }

    const displayFields = getDisplayFields();
    
    return (
      <div>
        <div style={{ marginBottom: 16 }}>
          <AntText type="secondary">
            选择需要的字段，支持拖拽调整列顺序
          </AntText>
        </div>
        
        {/* 字段列表 */}
        <div 
          ref={scrollContainerRef}
          data-draggable="true"
          style={{ 
            maxHeight: '70vh',
            overflowY: 'auto',
            border: '1px solid #f0f0f0',
            borderRadius: '4px',
            padding: '8px',
            position: 'relative',
            background: 'linear-gradient(to bottom, rgba(24, 144, 255, 0.05) 0%, transparent 150px, transparent calc(100% - 150px), rgba(24, 144, 255, 0.05) 100%)'
          }}
          onDragOver={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setDropEffect(e);
          }}
          onDragEnter={(e) => {
            e.preventDefault();
            e.stopPropagation();
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            e.stopPropagation();
          }}
          onDrop={(e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const draggedField = e.dataTransfer.getData('text/plain');
            if (draggedField) {
              moveColumn(draggedField, displayFields.length);
            }
          }}
        >
          {displayFields.map((field) => {
            const dynamicField = Array.isArray(dynamicFields) ? dynamicFields.find(df => df.field_name === field) : null;
            const isDynamicField = !!dynamicField;
            
            let config = null;
            if (isDynamicField && dynamicField) {
              config = {
                title: dynamicField.field_label || dynamicField.field_Label,
                width: 120,
                required: dynamicField.is_required || false,
                readonly: dynamicField.is_readonly || false,
                type: dynamicField.field_type || 'text',
                options: dynamicField.field_options || null,
                help_text: dynamicField.help_text || null,
                default_value: dynamicField.default_value || null,
                display_order: dynamicField.display_order || 999
              };
            } else if (!isDynamicField) {
              config = (fieldConfig || {})[field];
            }
            
            if (isDynamicField && !config) {
              return null;
            }
            if (!isDynamicField && !config) return null;
            
            const finalConfig = config;
            
            let groupInfo = null;
            if (isDynamicField && dynamicField) {
              const pageName = (dynamicField.page_name || 'default').trim() || 'default';
              Object.entries(fieldGroups || {}).forEach(([groupKey, group]) => {
                if (group.title === pageName) {
                  groupInfo = { 
                    key: groupKey, 
                    title: `${group.title}(自定义)`, 
                    icon: group.icon,
                    fields: group.fields,
                    color: 'purple' 
                  };
                }
              });
              if (!groupInfo) {
                groupInfo = { key: 'dynamic', title: '自定义字段', color: 'purple' };
              }
            } else {
              Object.entries(fieldGroups || {}).forEach(([groupKey, group]) => {
                if (Array.isArray(group?.fields) && group.fields.includes(field)) {
                  groupInfo = { key: groupKey, ...group };
                }
              });
            }
            
            const isVisible = (columnConfig || {})[field] !== false;
            
            return (
              <div
                key={field}
                data-draggable="true"
                style={{
                  padding: '12px',
                  border: '1px solid #d9d9d9',
                  borderRadius: '6px',
                  marginBottom: '4px',
                  backgroundColor: isVisible ? '#fff' : '#f5f5f5',
                  cursor: 'grab',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  transition: 'all 0.2s',
                  opacity: isVisible ? 1 : 0.7,
                  position: 'relative',
                  userSelect: 'none'
                }}
                draggable={true}
                onDragStart={(e) => {
                  console.log('开始拖拽字段:', field);
                  handleDragStart(e, field);
                }}
                onDragEnd={(e) => {
                  console.log('结束拖拽字段:', field);
                  handleDragEnd(e, isVisible);
                }}
                onDragOver={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setDropEffect(e);
                  
                  const rect = e.currentTarget.getBoundingClientRect();
                  const mouseY = e.clientY;
                  const itemCenterY = rect.top + rect.height / 2;
                  
                  // 清除所有边框样式
                  e.currentTarget.style.borderTop = '1px solid #d9d9d9';
                  e.currentTarget.style.borderBottom = '1px solid #d9d9d9';
                  
                  if (mouseY < itemCenterY) {
                    e.currentTarget.style.borderTop = '3px solid #1890ff';
                  } else {
                    e.currentTarget.style.borderBottom = '3px solid #1890ff';
                  }
                }}
                onDragEnter={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                }}
                onDragLeave={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  e.currentTarget.style.borderTop = '1px solid #d9d9d9';
                  e.currentTarget.style.borderBottom = '1px solid #d9d9d9';
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  e.currentTarget.style.borderTop = '1px solid #d9d9d9';
                  e.currentTarget.style.borderBottom = '1px solid #d9d9d9';
                  
                  const draggedField = e.dataTransfer.getData('text/plain');
                  console.log('拖拽放置:', draggedField, '到字段:', field);
                  
                  if (draggedField && draggedField !== field) {
                    const rect = e.currentTarget.getBoundingClientRect();
                    const mouseY = e.clientY;
                    
                    let targetIndex = displayFields.indexOf(field);
                    
                    // 根据鼠标位置决定插入位置
                    const itemCenterY = rect.top + rect.height / 2;
                    if (mouseY > itemCenterY) {
                      targetIndex += 1;
                    }
                    
                    console.log('目标索引:', targetIndex, '显示字段:', displayFields);
                    if (targetIndex !== -1) {
                      moveColumn(draggedField, targetIndex);
                    }
                  }
                }}
              >

                
                {/* 字段信息 */}
                <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                  <MenuOutlined style={{ marginRight: 8, color: '#999', cursor: 'grab' }} />
                  <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
                    <div style={{ 
                      fontWeight: 'bold', 
                      color: isVisible ? '#000' : '#999',
                      display: 'flex',
                      alignItems: 'center'
                    }}>
                      {config ? config.title : field}
                      {config && config.required && (
                        <span style={{ color: '#ff4d4f', marginLeft: '4px' }}>*</span>
                      )}
                    </div>
                    {groupInfo && (
                      <div style={{ fontSize: '12px', color: '#666', marginLeft: '8px', display: 'flex', alignItems: 'center' }}>
                        <span>{groupInfo.icon} {groupInfo.title}</span>
                        <Badge 
                          count={Array.isArray(groupInfo.fields) ? groupInfo.fields.filter(f => getVisibleFormFields().includes(f)).length : 0} 
                          size="small" 
                          style={{ 
                            backgroundColor: '#52c41a', 
                            marginLeft: '4px',
                            fontSize: '10px'
                          }} 
                        />
                      </div>
                    )}
                  </div>
                </div>
                
                <Checkbox
                  checked={isVisible}
                  disabled={config && config.required}
                  onChange={(e) => {
                    const newConfig = {
                      ...(columnConfig || {}),
                      [field]: e.target.checked
                    };
                    onConfigChange(newConfig);
                  }}
                />
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div>
      <style>
        {`
          [draggable="true"] {
            cursor: grab !important;
            user-select: none;
          }
          [draggable="true"]:active {
            cursor: grabbing !important;
          }
          * {
            -webkit-user-drag: none;
            user-drag: none;
          }
          [data-draggable="true"][draggable="true"] {
            -webkit-user-drag: element;
            user-drag: element;
          }
          input, textarea {
            user-select: text;
          }
        `}
      </style>
      
      {renderColumnSettings()}
      
      <Divider />
      
      <Space style={{ width: '100%', justifyContent: 'center' }}>
        <Button 
          type="primary" 
          onClick={() => {
            if (!isAdmin) {
              message.error('只有管理员可以保存列配置');
              return;
            }
            onSave(columnConfig);
          }}
        >
          保存设置
        </Button>
        <Button 
          onClick={async () => {
            if (!isAdmin) {
              message.error('只有管理员可以重置列配置');
              return;
            }
            onReset();
          }}
        >
          重置默认
        </Button>
      </Space>
    </div>
  );
};

export default ColumnSettings; 