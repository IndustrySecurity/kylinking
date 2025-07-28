import { useRef, useCallback } from 'react';

export const useAutoScroll = () => {
  const scrollContainerRef = useRef(null);
  const scrollIntervalRef = useRef(null);
  const scrollSpeedRef = useRef(0);

  const setDropEffect = useCallback((e) => {
    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = 'move';
    }
  }, []);

  const handleDragStart = useCallback((e, fieldName) => {
    e.dataTransfer.setData('text/plain', fieldName);
    e.dataTransfer.effectAllowed = 'move';
    
    // 设置拖拽时的样式
    if (e.target) {
      e.target.style.opacity = '0.5';
      e.target.style.transform = 'rotate(5deg)';
    }
  }, []);

  const handleDragEnd = useCallback((e, isVisible) => {
    // 清除拖拽样式
    if (e.target) {
      e.target.style.opacity = isVisible ? '1' : '0.7';
      e.target.style.transform = 'none';
    }
    
    // 清除自动滚动
    if (scrollIntervalRef.current) {
      clearInterval(scrollIntervalRef.current);
      scrollIntervalRef.current = null;
    }
    scrollSpeedRef.current = 0;
  }, []);

  const startAutoScroll = useCallback((direction) => {
    if (scrollIntervalRef.current) {
      clearInterval(scrollIntervalRef.current);
        }
    
    scrollSpeedRef.current = direction === 'up' ? -10 : 10;
    
    scrollIntervalRef.current = setInterval(() => {
      if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollTop += scrollSpeedRef.current;
      }
    }, 16); // 约60fps
  }, []);

  const stopAutoScroll = useCallback(() => {
    if (scrollIntervalRef.current) {
      clearInterval(scrollIntervalRef.current);
      scrollIntervalRef.current = null;
    }
    scrollSpeedRef.current = 0;
  }, []);

  return {
    scrollContainerRef,
    setDropEffect,
    handleDragStart,
    handleDragEnd,
    startAutoScroll,
    stopAutoScroll
  };
}; 