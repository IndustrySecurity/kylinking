# 全局 Hooks

这个目录包含可以在整个应用中复用的自定义 React Hooks。

## useAutoScroll

拖拽自动滚动 Hook，用于在拖拽操作时提供平滑的自动滚动体验。

### 功能特性

- 🎯 **智能触发区域**: 当鼠标拖拽到容器边缘 30% 区域时自动触发滚动
- ⚡ **动态速度**: 根据鼠标距离边缘的距离动态调整滚动速度
- 🎮 **鼠标滚轮支持**: 拖拽时支持鼠标滚轮控制滚动
- 🧹 **自动清理**: 自动管理事件监听器的添加和移除
- 🎨 **拖拽效果**: 提供拖拽时的视觉反馈

### 使用方法

```jsx
import { useAutoScroll } from '../../../hooks/useAutoScroll';

const MyComponent = () => {
  const { 
    scrollContainerRef, 
    setDropEffect, 
    handleDragStart, 
    handleDragEnd 
  } = useAutoScroll();

  return (
    <div ref={scrollContainerRef} style={{ height: '400px', overflow: 'auto' }}>
      {items.map((item, index) => (
        <div
          key={item.id}
          draggable={true}
          onDragStart={(e) => handleDragStart(e, item.id)}
          onDragEnd={(e) => handleDragEnd(e, item.isVisible)}
          onDragOver={setDropEffect}
          style={{ padding: '8px', border: '1px solid #ddd' }}
        >
          {item.name}
        </div>
      ))}
    </div>
  );
};
```

### API

| 属性 | 类型 | 说明 |
|------|------|------|
| `scrollContainerRef` | `RefObject` | 滚动容器的 ref，需要绑定到可滚动的 DOM 元素 |
| `setDropEffect` | `Function` | 设置拖拽效果的函数，在 `onDragOver` 事件中调用 |
| `handleDragStart` | `Function` | 处理拖拽开始事件的函数 |
| `handleDragEnd` | `Function` | 处理拖拽结束事件的函数 |
| `isDragging` | `Boolean` | 当前是否正在拖拽的状态 |
| `startAutoScroll` | `Function` | 手动启动自动滚动的函数 |
| `stopAutoScroll` | `Function` | 手动停止自动滚动的函数 |

### 配置说明

- **触发区域**: 容器顶部和底部各 30% 的区域
- **滚动速度**: 1-10 像素/帧，根据距离动态调整
- **滚轮速度**: 30-50 像素/滚动，根据滚轮速度调整

## useApi

通用的 API 调用 Hook，提供统一的错误处理和加载状态管理。

### 使用方法

```jsx
import { useApi } from '../../../hooks/useApi';

const MyComponent = () => {
  const { loading, error, request } = useApi();

  const fetchData = async () => {
    const response = await request('/api/data');
    // 处理响应数据
  };

  return (
    <div>
      {loading && <div>加载中...</div>}
      {error && <div>错误: {error}</div>}
      <button onClick={fetchData}>获取数据</button>
    </div>
  );
};
```

### API

| 属性 | 类型 | 说明 |
|------|------|------|
| `loading` | `Boolean` | 请求加载状态 |
| `error` | `String` | 错误信息 |
| `request` | `Function` | 发送请求的函数 |

## 最佳实践

1. **导入路径**: 使用相对路径从页面组件导入全局 hooks
2. **性能优化**: 在组件卸载时自动清理事件监听器
3. **错误处理**: 使用 try-catch 包装可能出错的拖拽操作
4. **类型安全**: 建议使用 TypeScript 来获得更好的类型检查

## 扩展指南

如需添加新的全局 hooks：

1. 在 `frontend/src/hooks/` 目录下创建新文件
2. 遵循命名规范：`use[功能名].js`
3. 导出 hook 函数
4. 在此文档中添加使用说明
5. 确保 hook 具有良好的错误处理和清理机制 