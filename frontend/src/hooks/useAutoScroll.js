import { useState, useEffect, useRef } from 'react';

export const useAutoScroll = () => {
  const [isDragging, setIsDragging] = useState(false);
  const scrollContainerRef = useRef(null);

  // 强制设置拖拽效果
  const setDropEffect = (e) => {
    try {
      e.dataTransfer.dropEffect = 'move';
      e.dataTransfer.effectAllowed = 'move';
      
      if (e.dataTransfer.setData) {
        e.dataTransfer.setData('text/plain', '');
      }
      
      if (e.dataTransfer.setDragImage) {
        const dragImage = document.createElement('div');
        dragImage.style.width = '1px';
        dragImage.style.height = '1px';
        dragImage.style.opacity = '0';
        document.body.appendChild(dragImage);
        e.dataTransfer.setDragImage(dragImage, 0, 0);
        setTimeout(() => document.body.removeChild(dragImage), 0);
      }
    } catch (error) {
      console.log('设置拖拽效果时出错:', error);
    }
  };

  // 增强的拖拽事件处理
  const handleDragStart = (e, field) => {
    console.log('拖拽开始:', field);
    
    e.stopPropagation();
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.dropEffect = 'move';
    e.dataTransfer.setData('text/plain', field);
    
    e.currentTarget.style.opacity = '0.5';
    e.currentTarget.style.transform = 'rotate(2deg)';
    
    setIsDragging(true);
    
    const cleanup = startAutoScroll(e, scrollContainerRef);
    e.currentTarget._cleanupAutoScroll = cleanup;
  };

  const handleDragEnd = (e, isVisible) => {
    e.stopPropagation();
    
    e.currentTarget.style.opacity = isVisible ? 1 : 0.7;
    e.currentTarget.style.transform = '';
    
    setIsDragging(false);
    
    // 确保清理函数被调用
    if (e.currentTarget._cleanupAutoScroll) {
      e.currentTarget._cleanupAutoScroll();
      delete e.currentTarget._cleanupAutoScroll;
    }
    
    // 额外确保停止滚动
    stopAutoScroll();
  };

  // 自动滚动功能
  const startAutoScroll = (e, containerRef) => {
    if (!containerRef.current) return;
    
    const container = containerRef.current;
    
    const handleDragOver = (dragEvent) => {
      const rect = container.getBoundingClientRect();
      const mouseY = dragEvent.clientY;
      const containerTop = rect.top;
      const containerBottom = rect.bottom;
      
      const containerHeight = containerBottom - containerTop;
      const topTriggerZone = containerTop + containerHeight * 0.3;
      const bottomTriggerZone = containerBottom - containerHeight * 0.3;
      
      // 直接滚动，不使用定时器
      if (mouseY < topTriggerZone) {
        const distance = topTriggerZone - mouseY;
        const speed = Math.max(1, Math.min(10, Math.floor(distance / 20)));
        
        if (container.scrollTop > 0) {
          container.scrollTop = Math.max(0, container.scrollTop - speed);
        }
      } else if (mouseY > bottomTriggerZone) {
        const distance = mouseY - bottomTriggerZone;
        const speed = Math.max(1, Math.min(10, Math.floor(distance / 20)));
        
        const maxScrollTop = container.scrollHeight - container.clientHeight;
        if (container.scrollTop < maxScrollTop) {
          container.scrollTop = Math.min(maxScrollTop, container.scrollTop + speed);
        }
      }
    };
    
    const handleWheel = (wheelEvent) => {
      wheelEvent.preventDefault();
      wheelEvent.stopPropagation();
      
      const deltaY = wheelEvent.deltaY;
      const scrollSpeed = Math.abs(deltaY) > 100 ? 50 : 30;
      
      if (deltaY > 0) {
        const maxScrollTop = container.scrollHeight - container.clientHeight;
        if (container.scrollTop < maxScrollTop) {
          container.scrollTop = Math.min(maxScrollTop, container.scrollTop + scrollSpeed);
        }
      } else {
        if (container.scrollTop > 0) {
          container.scrollTop = Math.max(0, container.scrollTop - scrollSpeed);
        }
      }
    };
    
    document.addEventListener('dragover', handleDragOver, { passive: false });
    container.addEventListener('wheel', handleWheel, { passive: false });
    
    return () => {
      document.removeEventListener('dragover', handleDragOver);
      container.removeEventListener('wheel', handleWheel);
    };
  };

  const stopAutoScroll = () => {
    // 不再需要定时器清理
  };

  // 全局拖拽事件处理
  useEffect(() => {
    const handleGlobalDragOver = (e) => {
      console.log('全局拖拽悬停事件');
      e.preventDefault();
      try {
        e.dataTransfer.dropEffect = 'move';
        e.dataTransfer.effectAllowed = 'move';
      } catch (error) {
        // 忽略错误
      }
    };

    const handleGlobalDrop = (e) => {
      e.preventDefault();
    };

    const handleGlobalDragEnter = (e) => {
      e.preventDefault();
    };

    const handleGlobalDragLeave = (e) => {
      e.preventDefault();
    };

    const handleGlobalDragStart = (e) => {
      if (e.target.closest('[data-draggable="true"]')) {
        e.stopPropagation();
      }
    };

    const handleGlobalWheel = (e) => {
      if (isDragging) {
        e.preventDefault();
        e.stopPropagation();
        
        const container = scrollContainerRef.current;
        if (container) {
          const deltaY = e.deltaY;
          const scrollSpeed = Math.abs(deltaY) > 100 ? 50 : 30;
          
          if (deltaY > 0) {
            const maxScrollTop = container.scrollHeight - container.clientHeight;
            if (container.scrollTop < maxScrollTop) {
              container.scrollTop = Math.min(maxScrollTop, container.scrollTop + scrollSpeed);
            }
          } else {
            if (container.scrollTop > 0) {
              container.scrollTop = Math.max(0, container.scrollTop - scrollSpeed);
            }
          }
        }
      }
    };

    document.addEventListener('dragover', handleGlobalDragOver, { passive: false });
    document.addEventListener('drop', handleGlobalDrop, { passive: false });
    document.addEventListener('dragenter', handleGlobalDragEnter, { passive: false });
    document.addEventListener('dragleave', handleGlobalDragLeave, { passive: false });
    document.addEventListener('dragstart', handleGlobalDragStart, { passive: false });
    document.addEventListener('wheel', handleGlobalWheel, { passive: false });

    return () => {
      document.removeEventListener('dragover', handleGlobalDragOver);
      document.removeEventListener('drop', handleGlobalDrop);
      document.removeEventListener('dragenter', handleGlobalDragEnter);
      document.removeEventListener('dragleave', handleGlobalDragLeave);
      document.removeEventListener('dragstart', handleGlobalDragStart);
      document.removeEventListener('wheel', handleGlobalWheel);
    };
  }, [isDragging]);

  return {
    isDragging,
    scrollContainerRef,
    setDropEffect,
    handleDragStart,
    handleDragEnd,
    startAutoScroll,
    stopAutoScroll
  };
}; 