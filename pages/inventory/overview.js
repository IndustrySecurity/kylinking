// pages/inventory/overview.js
const app = getApp()

Page({
  data: {
    // 顶部统计卡片数据
    summaryCards: {
      totalItems: 0,        // 库存物料总数
      totalValue: 0,        // 库存总价值
      lowStockAlert: 0,     // 低库存预警
      expiredItems: 0       // 过期物料
    },
    
    // 库存明细列表
    inventoryList: [],
    
    // 分页参数
    page: 1,
    pageSize: 20,
    total: 0,
    hasMore: true,
    loading: false,
    refreshing: false,
    
    // 基础数据
    warehouseList: [],      // 仓库列表
    materialList: [],       // 物料列表
    productList: [],        // 产品列表
    
    // 搜索相关
    searchKeyword: '',
    isSearching: false,
    searchResults: [],
    showSearchResults: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 检查登录状态
    if (!app.globalData.isLoggedIn) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
      return
    }
    
    // 先加载基础数据，然后加载库存数据
    this.loadBasicData().then(() => {
      this.loadStatistics()
      this.loadInventoryList(true)
    }).catch((error) => {
      console.error('基础数据加载失败:', error)
      // 即使基础数据加载失败，也尝试加载库存数据
      this.loadStatistics()
      this.loadInventoryList(true)
    })
  },

  /**
   * 加载基础数据（仓库、物料、产品）
   */
  loadBasicData() {
    return new Promise((resolve, reject) => {
      const promises = []
      
      // 获取仓库列表 - 使用正确的API路径
      const warehousePromise = app.request({
        url: '/api/tenant/base-archive/production-archive/warehouses/options',
        method: 'GET',
        data: {
          page: 1,
          page_size: 1000  // 获取所有仓库
        }
      }).then(res => {
        if (res.statusCode === 200 && res.data.success) {
          const warehouses = res.data.data || []
          this.setData({
            warehouseList: warehouses
          })
          return warehouses
        }
        return []
      }).catch(error => {
        console.error('加载仓库列表失败:', error)
        return []
      })
      
      promises.push(warehousePromise)

      // 获取物料列表 - 使用正确的API路径
      const materialPromise = app.request({
        url: '/api/tenant/base-archive/base-data/material-management/',
        method: 'GET',
        data: {
          page: 1,
          page_size: 1000  // 获取所有物料
        }
      }).then(res => {
        if (res.statusCode === 200 && res.data.success) {
          const materials = res.data.data.items || res.data.data || []
          this.setData({
            materialList: materials
          })
          return materials
        }
        return []
      }).catch(error => {
        console.error('加载物料列表失败:', error)
        return []
      })
      
      promises.push(materialPromise)

      // 获取产品列表 - 使用正确的API路径
      const productPromise = app.request({
        url: '/api/tenant/base-archive/base-data/product-management/',
        method: 'GET',
        data: {
          page: 1,
          page_size: 1000  // 获取所有产品
        }
      }).then(res => {
        if (res.statusCode === 200 && res.data.success) {
          const products = res.data.data.products || res.data.data.items || res.data.data || []
          this.setData({
            productList: products
          })
          return products
        }
        return []
      }).catch(error => {
        console.error('加载产品列表失败:', error)
        return []
      })
      
      promises.push(productPromise)

      // 等待所有基础数据加载完成
      Promise.all(promises).then(() => {
        resolve()
      }).catch(reject)
    })
  },

  /**
   * 加载统计数据
   */
  loadStatistics() {
    // 统计数据通过库存列表计算得出，不单独调用API
    this.setData({
      summaryCards: {
        totalItems: 0,
        totalValue: 0,
        lowStockAlert: 0,
        expiredItems: 0
      }
    })
  },

    /**
   * 加载库存明细列表
   */
  loadInventoryList(isRefresh = false) {
    if (this.data.loading) return

    this.setData({
      loading: true,
      refreshing: isRefresh
    })

    const page = isRefresh ? 1 : this.data.page
    const params = {
      page: page,
      page_size: this.data.pageSize
    }

    app.request({
      url: '/api/tenant/business/inventory/inventories',
      method: 'GET',
      data: params
    }).then(res => {
      if (res.statusCode === 200 && res.data.success) {
        let newData = res.data.data
        
        // 如果返回的是分页数据格式
        if (newData.items) {
          newData = newData.items
        } else if (Array.isArray(newData)) {
          // 直接是数组格式
          newData = newData
        } else {
          // 其他格式，尝试转换
          newData = []
        }
        
        // 格式化数据并解析名称
        const mapped = newData.map(item => {
          
          // 解析仓库名称
          if (item.warehouse_id && this.data.warehouseList.length > 0) {
            const warehouse = this.data.warehouseList.find(w => w.value === item.warehouse_id || w.id === item.warehouse_id)
            item.warehouse_name = warehouse ? warehouse.label || warehouse.warehouse_name : '未知仓库'
          } else {
            item.warehouse_name = item.warehouse_name || item.warehouse || '未知仓库'
          }
          
          // 解析物料/产品名称 - 改进逻辑
          if (item.material_id && this.data.materialList.length > 0) {
            const material = this.data.materialList.find(m => m.id === item.material_id)
            if (material) {
              item.material_name = material.material_name
              item.material_code = material.material_code
              item.item_type = 'material' // 标记为物料
            } else {
              item.material_name = '未知物料'
              item.material_code = 'N/A'
              item.item_type = 'material'
            }
          } else if (item.product_id && this.data.productList.length > 0) {
            const product = this.data.productList.find(p => p.id === item.product_id)
            if (product) {
              item.material_name = product.product_name
              item.material_code = product.product_code
              item.item_type = 'product' // 标记为产品
            } else {
              item.material_name = '未知产品'
              item.material_code = 'N/A'
              item.item_type = 'product'
            }
          } else {
            // 如果都没有ID，尝试从现有字段获取
            item.material_name = item.material_name || item.product_name || item.material || item.name || '未知物料'
            item.material_code = item.material_code || item.product_code || item.code || 'N/A'
            item.item_type = item.product_id ? 'product' : 'material'
          }
          
          // 格式化数量显示 - 支持多种字段名称
          const currentStock = item.current_quantity || item.current_stock || item.quantity || 0
          const availableStock = item.available_quantity || item.available_stock || item.available || currentStock
          const reservedStock = item.reserved_quantity || item.reserved_stock || item.reserved || 0
          const inTransitStock = item.in_transit_quantity || item.in_transit_stock || item.in_transit || 0
          
          item.formatted_current_stock = this.formatQuantity(currentStock, item.unit || item.unit_name)
          item.formatted_available_stock = this.formatQuantity(availableStock, item.unit || item.unit_name)
          item.formatted_reserved_stock = this.formatQuantity(reservedStock, item.unit || item.unit_name)
          item.formatted_in_transit_stock = this.formatQuantity(inTransitStock, item.unit || item.unit_name)
          
          // 格式化状态显示
          item.status_text = this.formatStatus(item.inventory_status || item.status || 'normal')
          item.quality_status_text = this.formatQualityStatus(item.quality_status || 'qualified')
          
          // 判断是否为零库存
          item.isZeroStock = currentStock <= 0
          
          // 确保其他关键字段存在
          item.batch_number = item.batch_number || item.batch || item.lot_number || '-'
          item.location = item.location || item.storage_location || item.warehouse_location || '-'
          
          return item
        })

        // 计算统计数据
        const totalValue = mapped.reduce((sum, item) => {
          const cost = parseFloat(item.total_cost) || parseFloat(item.cost) || parseFloat(item.value) || 0
          return sum + cost
        }, 0)
        
        const lowStockItems = mapped.filter(item => {
          const currentStock = parseFloat(item.current_quantity || item.current_stock || item.quantity || 0)
          const safetyStock = parseFloat(item.safety_stock || item.min_stock || 0)
          return currentStock <= safetyStock && currentStock > 0
        }).length
        
        const expiredItems = mapped.filter(item => {
          const expiryDate = item.expiry_date || item.expiration_date || item.expire_date
          if (!expiryDate) return false
          return new Date(expiryDate) < new Date()
        }).length

        this.setData({
          inventoryList: isRefresh ? mapped : this.data.inventoryList.concat(mapped),
          page: isRefresh ? 2 : this.data.page + 1,
          hasMore: mapped.length === this.data.pageSize,
          loading: false,
          refreshing: false,
          // 更新统计数据
          summaryCards: {
            totalItems: mapped.length,
            totalValue: totalValue,
            lowStockAlert: lowStockItems,
            expiredItems: expiredItems
          }
        })
      } else {
        console.error('API错误:', res.data)
        wx.showToast({
          title: res.data.error || res.data.message || '加载失败',
          icon: 'none'
        })
        this.setData({
          loading: false,
          refreshing: false
        })
      }
    }).catch(error => {
      console.error('加载库存明细失败:', error)
      // API未准备好时，显示空列表
      this.setData({
        inventoryList: [],
        loading: false,
        refreshing: false,
        hasMore: false
      })
      wx.showToast({
        title: '暂无库存数据',
        icon: 'none'
      })
    })
  },



  /**
   * 搜索输入处理
   */
  onSearchInput: function(e) {
    const keyword = e.detail.value.trim()
    this.setData({
      searchKeyword: keyword,
      showSearchResults: keyword.length > 0
    })
    
    // 实时搜索
    if (keyword.length > 0) {
      this.performSearch(keyword)
    } else {
      this.clearSearch()
    }
  },

  /**
   * 搜索确认
   */
  onSearchConfirm: function(e) {
    const keyword = e.detail.value.trim()
    if (keyword.length > 0) {
      this.performSearch(keyword)
    }
  },

  /**
   * 执行搜索
   */
  performSearch: function(keyword) {
    if (!keyword) return
    
    this.setData({
      isSearching: true
    })

    // 在现有数据中搜索
    const allInventory = this.data.inventoryList
    const results = allInventory.filter(item => {
      const searchText = keyword.toLowerCase()
      
      // 搜索仓库名称
      if (item.warehouse_name && item.warehouse_name.toLowerCase().includes(searchText)) {
        return true
      }
      
      // 搜索物料名称
      if (item.material_name && item.material_name.toLowerCase().includes(searchText)) {
        return true
      }
      
      // 搜索物料编码
      if (item.material_code && item.material_code.toLowerCase().includes(searchText)) {
        return true
      }
      
      // 搜索批次号
      if (item.batch_number && item.batch_number.toLowerCase().includes(searchText)) {
        return true
      }
      
      return false
    })

    this.setData({
      searchResults: results,
      isSearching: false,
      showSearchResults: true
    })
  },

  /**
   * 清除搜索
   */
  clearSearch: function() {
    this.setData({
      searchKeyword: '',
      searchResults: [],
      showSearchResults: false,
      isSearching: false
    })
  },



  /**
   * 格式化状态显示
   */
  formatStatus: function(status) {
    const statusMap = {
      'normal': '正常',
      'low_stock': '低库存',
      'expired': '过期',
      'reserved': '预留',
      'in_transit': '在途'
    }
    return statusMap[status] || status
  },

  /**
   * 格式化质量状态显示
   */
  formatQualityStatus: function(qualityStatus) {
    const statusMap = {
      'qualified': '合格',
      'unqualified': '不合格',
      'pending': '待检',
      'quarantine': '隔离'
    }
    return statusMap[qualityStatus] || qualityStatus
  },

  /**
   * 获取状态样式类名
   */
  getStatusClass: function(status) {
    const classMap = {
      'normal': 'status-normal',
      'low_stock': 'status-low-stock',
      'expired': 'status-expired',
      'reserved': 'status-reserved',
      'in_transit': 'status-in-transit'
    }
    return classMap[status] || 'status-default'
  },

  /**
   * 获取质量状态样式类名
   */
  getQualityStatusClass: function(qualityStatus) {
    const classMap = {
      'qualified': 'quality-qualified',
      'unqualified': 'quality-unqualified',
      'pending': 'quality-pending',
      'quarantine': 'quality-quarantine'
    }
    return classMap[qualityStatus] || 'quality-default'
  },

  /**
   * 格式化数量显示
   */
  formatQuantity: function(quantity, unit) {
    if (quantity === null || quantity === undefined) return '0'
    return `${quantity} ${unit || ''}`
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh: function() {
    this.loadStatistics()
    this.loadInventoryList(true)
    setTimeout(() => {
      wx.stopPullDownRefresh()
    }, 1000)
  },

  /**
   * 上拉加载更多
   */
  onReachBottom: function() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadInventoryList()
    }
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    return {
      title: 'MES库存总览',
      path: '/pages/inventory/overview'
    }
  }
}) 