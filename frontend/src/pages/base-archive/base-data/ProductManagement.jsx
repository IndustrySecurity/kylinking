import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  message,
  Modal,
  Form,
  Select,
  InputNumber,
  Switch,
  Tabs,
  Row,
  Col,
  Upload,
  Image,
  Checkbox,
  Typography,
  Popconfirm,
  Tag,
  Divider
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  ReloadOutlined,
  UploadOutlined,
  InboxOutlined
} from '@ant-design/icons';
import { productManagementApi } from '../../../api/base-archive/base-data/productManagement';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;
const { Dragger } = Upload;

const ProductManagement = () => {
  // 状态管理
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
  });
  const [searchText, setSearchText] = useState('');
  const [filters, setFilters] = useState({});
  
  // 弹窗状态
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState('create'); // create, edit, view
  const [editingRecord, setEditingRecord] = useState(null);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [activeTabKey, setActiveTabKey] = useState('basic');
  const [productImages, setProductImages] = useState([]);
  const [productProcesses, setProductProcesses] = useState([]);
  const [productMaterials, setProductMaterials] = useState([]);
  
  // 表单选项
  const [formOptions, setFormOptions] = useState({
    customers: [],
    bagTypes: [],
    processes: [],
    materials: [],
    employees: [],
    units: []
  });
  
  // 表单实例
  const [form] = Form.useForm();

  // 初始加载
  useEffect(() => {
    loadData();
    loadFormOptions();
  }, []);

  // 加载数据
  const loadData = async (params = {}) => {
    try {
      setLoading(true);
      const response = await productManagementApi.getProducts({
        page: pagination.current,
        per_page: pagination.pageSize,
        search: searchText,
        ...filters,
        ...params
      });

      if (response.data.success) {
        const { products, total, page, per_page } = response.data.data;
        
        // 为数据添加唯一key
        const dataWithKeys = (products || []).map((item, index) => ({
          ...item,
          key: item.id || `product-${index}`, // 使用id作为key，如果没有id则生成唯一key
        }));
        
        setData(dataWithKeys);
        setPagination(prev => ({
          ...prev,
          current: page || 1,
          pageSize: per_page || 20,
          total: total || 0
        }));
      }
    } catch (error) {
      console.error('获取产品列表失败:', error);
      message.error('获取产品列表失败');
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  // 加载表单选项
  const loadFormOptions = async () => {
    try {
      const response = await productManagementApi.getFormOptions();
      
      if (response.data.success) {
        const formData = response.data.data || {
          customers: [],
          bagTypes: [],
          processes: [],
          materials: [],
          employees: [],
          units: []
        };
        
        setFormOptions(formData);
      } else {
        message.error(response.data.error || '获取表单选项失败');
      }
    } catch (error) {
      console.error('获取表单选项失败:', error);
      message.error('获取表单选项失败: ' + (error.response?.data?.error || error.message));
    }
  };

  // 处理客户选择变化 - 自动填充功能
  const handleCustomerChange = async (customerId) => {
    try {
      if (!customerId) {
        // 如果没有选择客户，清空业务员字段
        form.setFieldsValue({
          salesperson_id: undefined,
        });
        return;
      }
      
      // 根据客户ID获取相关信息并自动填充
      const customer = formOptions.customers.find(c => c.value === customerId);
      if (customer && customer.sales_person_id) {
        form.setFieldsValue({
          salesperson_id: customer.sales_person_id, // 自动填充业务员
        });
      } else {
        // 如果客户没有关联的业务员，清空业务员字段
        form.setFieldsValue({
          salesperson_id: undefined,
        });
      }
    } catch (error) {
      console.error('自动填充客户信息失败:', error);
    }
  };

  // 处理袋型选择变化 - 自动填充功能
  const handleBagTypeChange = async (bagTypeId) => {
    if (!bagTypeId) return;
    
    try {
      // 根据袋型ID获取相关结构信息并自动填充
      const bagType = formOptions.bagTypes.find(b => b.value === bagTypeId);
      if (bagType) {
        // 只在新建产品时自动填充产品结构字段
        if (modalType === 'create') {
          form.setFieldsValue({
            film_structure: bagType.bag_type_name || '', // 理膜结构自动填入袋型名称
            specification: '', // 产品规格自动填入宽度
            bag_system: 'system1', // 袋型系统默认值
            width: bagType.width || 0,
            length: bagType.length || 0,
            thickness: bagType.thickness || 0,
            ['product_structures']: {
              width: bagType.width || 0,
              length: bagType.length || 0,
              thickness: bagType.thickness || 0
            }
          });
        } else {
          // 编辑时只填充基础信息，不覆盖产品结构数据
          form.setFieldsValue({
            film_structure: bagType.bag_type_name || '', // 理膜结构自动填入袋型名称
            specification: '', // 产品规格自动填入宽度
            bag_system: 'system1', // 袋型系统默认值
            width: bagType.width || 0,
            length: bagType.length || 0,
            thickness: bagType.thickness || 0
          });
        }
      }
    } catch (error) {
      console.error('自动填充袋型信息失败:', error);
    }
  };

  // 图片上传处理
  const handleImageUpload = {
    name: 'file',
    multiple: true,
    maxCount: 4,
    accept: 'image/*',
    customRequest: async (options) => {
      const { file, onSuccess, onError, onProgress } = options;
      
      try {
        onProgress({ percent: 10 });
        
        const response = await productManagementApi.uploadImage(file);
        
        onProgress({ percent: 100 });
        onSuccess(response.data.data);
        
      } catch (error) {
        console.error('图片上传失败:', error);
        onError(error);
        message.error('图片上传失败');
      }
    },
    beforeUpload: (file) => {
      const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
      if (!isJpgOrPng) {
        message.error('只能上传 JPG/PNG 格式的图片!');
        return false;
      }
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        message.error('图片大小不能超过 2MB!');
        return false;
      }
      return true;
    },
    onChange: (info) => {
      let fileList = [...info.fileList];
      
      // 限制文件数量
      fileList = fileList.slice(-4);
      
      // 设置上传状态
      fileList = fileList.map(file => {
        if (file.response) {
          file.url = file.response.url;
          file.status = 'done';
        }
        return file;
      });
      
      setProductImages(fileList);
    }
  };

  // 搜索处理
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1 });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchText('');
    setFilters({});
    setPagination(prev => ({ ...prev, current: 1 }));
    loadData({ page: 1, search: '', ...{} });
  };

  // 表格分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    loadData({
      page: newPagination.current,
      per_page: newPagination.pageSize
    });
  };

  // 新增产品
  const handleAdd = () => {
    setModalType('create');
    setEditingRecord(null);
    setActiveTabKey('basic');
    setProductImages([]);
    setProductProcesses([]);
    setProductMaterials([]);
    form.resetFields();
    
    // 获取当前用户信息
    const userInfo = localStorage.getItem('userInfo');
    let currentUserId = null;
    if (userInfo) {
      try {
        const user = JSON.parse(userInfo);
        currentUserId = user.id;
      } catch (error) {
        console.error('解析用户信息失败:', error);
      }
    }
    
    // 设置默认值
    form.setFieldsValue({
      customer_id: undefined,
      salesperson_id: undefined, 
      status: 'active',
      product_type: 'finished',
      unit_id: undefined,
      package_unit_id: undefined,
      currency: undefined,
      conversion_rate: undefined,
      safety_stock: undefined,
      min_order_qty: undefined,
      is_sellable: true,
      is_purchasable: true,
      is_producible: true
    });
    setModalVisible(true);
  };

  // 编辑产品
  const handleEdit = async (record) => {
    try {
      setModalType('edit');
      setEditingRecord(record);
      setActiveTabKey('basic');
      setModalVisible(true);
      
      // 获取产品详情
      const response = await productManagementApi.getProductDetail(record.id);
      if (response.data.success) {
        const productDetail = response.data.data;
        console.log('productDetail', productDetail);
        
        // 处理产品结构数据
        const formData = { ...productDetail };
        // 初始化产品结构数据，确保所有字段都有默认值
        formData.product_structures = {
          length: undefined,
          width: undefined,
          height: undefined,
          side_width: undefined,
          bottom_width: undefined,
          thickness: undefined,
          total_thickness: undefined,
          volume: undefined,
          weight: undefined,
          expand_length: undefined,
          expand_width: undefined,
          expand_height: undefined,
          material_length: undefined,
          material_width: undefined,
          material_height: undefined,
          single_length: undefined,
          single_width: undefined,
          single_height: undefined,
          blue_color: undefined,
          red_color: undefined,
          other_color: undefined,
          // 新增字段
          cut_length: undefined,
          cut_width: undefined,
          cut_thickness: undefined,
          cut_area: undefined,
          light_eye_length: undefined,
          light_eye_width: undefined,
          light_eye_distance: undefined,
          edge_sealing_width: undefined,
          bag_making_fee: undefined,
          container_fee: undefined,
          cuff_fee: undefined,
          pallet_length: undefined,
          pallet_width: undefined,
          pallet_height: undefined,
          pallet_1: undefined,
          pallet_2: undefined,
          pallet_3: undefined,
          winding_diameter: undefined,
          density: undefined,
          seal_top: undefined,
          seal_left: undefined,
          seal_right: undefined,
          seal_middle: undefined,
          sealing_temperature: undefined,
          sealing_width: undefined,
          sealing_strength: undefined,
          sealing_method: undefined,
          power: undefined
        };
        
        if (productDetail.structures && productDetail.structures.length > 0) {
          // 将第一个结构数据展开到product_structures字段
          const structure = productDetail.structures[0];
          formData.product_structures = {
            ...formData.product_structures, // 保持默认值
            length: structure.length || 0,
            width: structure.width || 0,
            height: structure.height || 0,
            side_width: structure.side_width || 0,
            bottom_width: structure.bottom_width || 0,
            thickness: structure.thickness || 0,
            total_thickness: structure.total_thickness || 0,
            volume: structure.volume || 0,
            weight: structure.weight || 0,
            expand_length: structure.expand_length || 0,
            expand_width: structure.expand_width || 0,
            expand_height: structure.expand_height || 0,
            material_length: structure.material_length || 0,
            material_width: structure.material_width || 0,
            material_height: structure.material_height || 0,
            single_length: structure.single_length || 0,
            single_width: structure.single_width || 0,
            single_height: structure.single_height || 0,
            blue_color: structure.blue_color || '',
            red_color: structure.red_color || '',
            other_color: structure.other_color || '',
            // 新增字段
            cut_length: structure.cut_length || 0,
            cut_width: structure.cut_width || 0,
            cut_thickness: structure.cut_thickness || 0,
            cut_area: structure.cut_area || 0,
            light_eye_length: structure.light_eye_length || 0,
            light_eye_width: structure.light_eye_width || 0,
            light_eye_distance: structure.light_eye_distance || 0,
            edge_sealing_width: structure.edge_sealing_width || 0,
            bag_making_fee: structure.bag_making_fee || 0,
            container_fee: structure.container_fee || 0,
            cuff_fee: structure.cuff_fee || 0,
            pallet_length: structure.pallet_length || 0,
            pallet_width: structure.pallet_width || 0,
            pallet_height: structure.pallet_height || 0,
            pallet_1: structure.pallet_1 || 0,
            pallet_2: structure.pallet_2 || 0,
            pallet_3: structure.pallet_3 || 0,
            winding_diameter: structure.winding_diameter || 0,
            density: structure.density || 0,
            seal_top: structure.seal_top || 0,
            seal_left: structure.seal_left || 0,
            seal_right: structure.seal_right || 0,
            seal_middle: structure.seal_middle || 0,
            sealing_temperature: structure.sealing_temperature || 0,
            sealing_width: structure.sealing_width || 0,
            sealing_strength: structure.sealing_strength || 0,
            sealing_method: structure.sealing_method || '',
            power: structure.power || 0
          };
        }
        
        // 处理理化指标数据
        if (productDetail.quality_indicators && productDetail.quality_indicators.length > 0) {
          // 将第一个理化指标数据展开到product_quality_indicators字段
          const qualityIndicator = productDetail.quality_indicators[0];
          formData.product_quality_indicators = {
            packaging_requirement: qualityIndicator.packaging_requirement,
            tensile_requirement: qualityIndicator.tensile_requirement,
            opening_requirement: qualityIndicator.opening_requirement,
            slip_requirement: qualityIndicator.slip_requirement,
            cut_requirement: qualityIndicator.cut_requirement,
            anti_static_requirement: qualityIndicator.anti_static_requirement,
            sterilization_requirement: qualityIndicator.sterilization_requirement,
            hygiene_requirement: qualityIndicator.hygiene_requirement,
            special_requirement: qualityIndicator.special_requirement,
            tensile_strength_md: qualityIndicator.tensile_strength_md,
            tensile_strength_td: qualityIndicator.tensile_strength_td,
            elongation_break_md: qualityIndicator.elongation_break_md,
            elongation_break_td: qualityIndicator.elongation_break_td,
            dart_drop_impact: qualityIndicator.dart_drop_impact,
            heat_shrinkage: qualityIndicator.heat_shrinkage,
            oxygen_transmission_rate: qualityIndicator.oxygen_transmission_rate,
            water_vapor_transmission_rate: qualityIndicator.water_vapor_transmission_rate,
            seal_strength: qualityIndicator.seal_strength
          };
        }
        
        form.setFieldsValue(formData);
        
        // 加载产品图片
        if (productDetail.product_images) {
          const images = productDetail.product_images.map(img => ({
            uid: img.id,
            name: img.image_name,
            url: img.image_url,
            status: 'done'
          }));
          setProductImages(images);
        }

        // 加载产品工序
        if (productDetail.product_processes) {
          setProductProcesses(productDetail.product_processes.map(process => ({
            ...process,
            id: process.id || Date.now() + Math.random()
          })));
        }

        // 加载产品材料
        if (productDetail.product_materials) {
          setProductMaterials(productDetail.product_materials.map(material => ({
            ...material,
            id: material.id || Date.now() + Math.random()
          })));
        }
      }
    } catch (error) {
      console.error('获取产品详情失败:', error);
      message.error('获取产品详情失败');
    }
  };

  // 查看产品
  const handleView = async (record) => {
    try {
      setModalType('view');
      setEditingRecord(record);
      setActiveTabKey('basic');
      setProductImages([]);
      setProductProcesses([]);
      setProductMaterials([]);
      
      // 获取产品详情
      const response = await productManagementApi.getProductDetail(record.id);
      if (response.data.success) {
        const productDetail = response.data.data;
        
        // 处理产品结构数据
        const formData = { ...productDetail };
        // 初始化产品结构数据，确保所有字段都有默认值
        formData.product_structures = {
          length: undefined,
          width: undefined,
          height: undefined,
          side_width: undefined,
          bottom_width: undefined,
          thickness: undefined,
          total_thickness: undefined,
          volume: undefined,
          weight: undefined,
          expand_length: undefined,
          expand_width: undefined,
          expand_height: undefined,
          material_length: undefined,
          material_width: undefined,
          material_height: undefined,
          single_length: undefined,
          single_width: undefined,
          single_height: undefined,
          blue_color: undefined,
          red_color: undefined,
          other_color: undefined,
          // 新增字段
          cut_length: undefined,
          cut_width: undefined,
          cut_thickness: undefined,
          cut_area: undefined,
          light_eye_length: undefined,
          light_eye_width: undefined,
          light_eye_distance: undefined,
          edge_sealing_width: undefined,
          bag_making_fee: undefined,
          container_fee: undefined,
          cuff_fee: undefined,
          pallet_length: undefined,
          pallet_width: undefined,
          pallet_height: undefined,
          pallet_1: undefined,
          pallet_2: undefined,
          pallet_3: undefined,
          winding_diameter: undefined,
          density: undefined,
          seal_top: undefined,
          seal_left: undefined,
          seal_right: undefined,
          seal_middle: undefined,
          sealing_temperature: undefined,
          sealing_width: undefined,
          sealing_strength: undefined,
          sealing_method: undefined,
          power: undefined
        };
        
        if (productDetail.structures && productDetail.structures.length > 0) {
          // 将第一个结构数据展开到product_structures字段
          const structure = productDetail.structures[0];
          formData.product_structures = {
            ...formData.product_structures, // 保持默认值
            length: structure.length || 0,
            width: structure.width || 0,
            height: structure.height || 0,
            side_width: structure.side_width || 0,
            bottom_width: structure.bottom_width || 0,
            thickness: structure.thickness || 0,
            total_thickness: structure.total_thickness || 0,
            volume: structure.volume || 0,
            weight: structure.weight || 0,
            expand_length: structure.expand_length || 0,
            expand_width: structure.expand_width || 0,
            expand_height: structure.expand_height || 0,
            material_length: structure.material_length || 0,
            material_width: structure.material_width || 0,
            material_height: structure.material_height || 0,
            single_length: structure.single_length || 0,
            single_width: structure.single_width || 0,
            single_height: structure.single_height || 0,
            blue_color: structure.blue_color || '',
            red_color: structure.red_color || '',
            other_color: structure.other_color || '',
            // 新增字段
            cut_length: structure.cut_length || 0,
            cut_width: structure.cut_width || 0,
            cut_thickness: structure.cut_thickness || 0,
            cut_area: structure.cut_area || 0,
            light_eye_length: structure.light_eye_length || 0,
            light_eye_width: structure.light_eye_width || 0,
            light_eye_distance: structure.light_eye_distance || 0,
            edge_sealing_width: structure.edge_sealing_width || 0,
            bag_making_fee: structure.bag_making_fee || 0,
            container_fee: structure.container_fee || 0,
            cuff_fee: structure.cuff_fee || 0,
            pallet_length: structure.pallet_length || 0,
            pallet_width: structure.pallet_width || 0,
            pallet_height: structure.pallet_height || 0,
            pallet_1: structure.pallet_1 || 0,
            pallet_2: structure.pallet_2 || 0,
            pallet_3: structure.pallet_3 || 0,
            winding_diameter: structure.winding_diameter || 0,
            density: structure.density || 0,
            seal_top: structure.seal_top || 0,
            seal_left: structure.seal_left || 0,
            seal_right: structure.seal_right || 0,
            seal_middle: structure.seal_middle || 0,
            sealing_temperature: structure.sealing_temperature || 0,
            sealing_width: structure.sealing_width || 0,
            sealing_strength: structure.sealing_strength || 0,
            sealing_method: structure.sealing_method || '',
            power: structure.power || 0
          };
        }
        
        // 处理理化指标数据
        if (productDetail.quality_indicators && productDetail.quality_indicators.length > 0) {
          // 将第一个理化指标数据展开到product_quality_indicators字段
          const qualityIndicator = productDetail.quality_indicators[0];
          formData.product_quality_indicators = {
            packaging_requirement: qualityIndicator.packaging_requirement,
            tensile_requirement: qualityIndicator.tensile_requirement,
            opening_requirement: qualityIndicator.opening_requirement,
            slip_requirement: qualityIndicator.slip_requirement,
            cut_requirement: qualityIndicator.cut_requirement,
            anti_static_requirement: qualityIndicator.anti_static_requirement,
            sterilization_requirement: qualityIndicator.sterilization_requirement,
            hygiene_requirement: qualityIndicator.hygiene_requirement,
            special_requirement: qualityIndicator.special_requirement,
            tensile_strength_md: qualityIndicator.tensile_strength_md,
            tensile_strength_td: qualityIndicator.tensile_strength_td,
            elongation_break_md: qualityIndicator.elongation_break_md,
            elongation_break_td: qualityIndicator.elongation_break_td,
            dart_drop_impact: qualityIndicator.dart_drop_impact,
            heat_shrinkage: qualityIndicator.heat_shrinkage,
            oxygen_transmission_rate: qualityIndicator.oxygen_transmission_rate,
            water_vapor_transmission_rate: qualityIndicator.water_vapor_transmission_rate,
            seal_strength: qualityIndicator.seal_strength
          };
        }
        
        form.setFieldsValue(formData);
        
        // 加载产品图片
        if (productDetail.product_images) {
          const images = productDetail.product_images.map(img => ({
            uid: img.id,
            name: img.image_name,
            url: img.image_url,
            status: 'done'
          }));
          setProductImages(images);
        }

        // 加载产品工序
        if (productDetail.product_processes) {
          setProductProcesses(productDetail.product_processes.map(process => ({
            ...process,
            id: process.id || Date.now() + Math.random()
          })));
        }

        // 加载产品材料
        if (productDetail.product_materials) {
          setProductMaterials(productDetail.product_materials.map(material => ({
            ...material,
            id: material.id || Date.now() + Math.random()
          })));
        }
      }
      
      setModalVisible(true);
    } catch (error) {
      console.error('获取产品详情失败:', error);
      message.error('获取产品详情失败');
    }
  };

  // 删除产品
  const handleDelete = async (id) => {
    try {
      await productManagementApi.deleteProduct(id);
      message.success('删除成功');
      loadData();
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  // 保存产品
  const handleSave = async () => {
    try {
      setConfirmLoading(true);
      const values = await form.validateFields();

      // 处理图片数据
      const imageData = productImages.map((img, index) => ({
        image_name: img.name,
        image_url: img.url || img.response?.url,
        image_type: `图片${index + 1}`,
        file_size: img.size,
        sort_order: index
      }));

      // 处理工序数据 - 只传送必要字段
      const processData = productProcesses
        .filter(process => process.process_id) // 只保存已选择工序的记录
        .map(process => ({
          process_id: process.process_id,
          sort_order: process.sort_order || 0
        }));

      // 处理材料数据 - 只传送必要字段
      const materialData = productMaterials
        .filter(material => material.material_id) // 只保存已选择材料的记录
        .map(material => ({
          material_id: material.material_id,
          sort_order: material.sort_order || 0
        }));
      
      // 处理产品结构数据
      const structureData = values.product_structures || {};
      console.log('原始产品结构数据:', structureData);
      // 过滤掉undefined和null值，只保留有效数据
      const filteredStructureData = {};
      Object.keys(structureData).forEach(key => {
        if (structureData[key] !== undefined && structureData[key] !== null && structureData[key] !== '') {
          filteredStructureData[key] = structureData[key];
        }
      });
      console.log('过滤后的产品结构数据:', filteredStructureData);
      
      // 处理理化指标数据
      const qualityIndicatorsData = values.product_quality_indicators || {};
      // 过滤掉undefined和null值，只保留有效数据
      const filteredQualityIndicatorsData = {};
      Object.keys(qualityIndicatorsData).forEach(key => {
        if (qualityIndicatorsData[key] !== undefined && qualityIndicatorsData[key] !== null && qualityIndicatorsData[key] !== '') {
          filteredQualityIndicatorsData[key] = qualityIndicatorsData[key];
        }
      });
      
      const productData = {
        ...values,
        structure: filteredStructureData, // 将过滤后的产品结构数据作为structure字段传递
        quality_indicators: filteredQualityIndicatorsData, // 将过滤后的理化指标数据作为quality_indicators字段传递
        product_images: imageData,
        product_processes: processData,
        product_materials: materialData
      };
      
      // 删除嵌套的字段，避免重复
      delete productData.product_structures;
      delete productData.product_quality_indicators;

      if (modalType === 'create') {
        await productManagementApi.createProduct(productData);
        message.success('产品创建成功');
      } else if (modalType === 'edit') {
        await productManagementApi.updateProduct(editingRecord.id, productData);
        message.success('产品更新成功');
      }

      setModalVisible(false);
      loadData();
    } catch (error) {
      if (error.errorFields) {
        message.error('请检查输入内容');
      } else {
        console.error('保存失败:', error);
        message.error(modalType === 'create' ? '创建失败' : '更新失败');
      }
    } finally {
      setConfirmLoading(false);
    }
  };

  // 关闭模态框
  const closeModal = () => {
    setModalVisible(false);
    setEditingRecord(null);
    setActiveTabKey('basic');
    setProductImages([]);
    setProductProcesses([]);
    setProductMaterials([]);
    form.resetFields();
  };

  // 工序管理功能
  const addProcess = () => {
    const newProcess = {
      id: Date.now(),
      process_id: '',
      process_name: '',
      process_category_name: '',
      scheduling_method: '',
      unit: '',
      sort_order: productProcesses.length + 1
    };
    setProductProcesses([...productProcesses, newProcess]);
  };

  const removeProcess = (id) => {
    setProductProcesses(productProcesses.filter(p => p.id !== id));
  };

  const updateProcess = (id, field, value) => {
    setProductProcesses(productProcesses.map(p => 
      p.id === id ? { ...p, [field]: value } : p
    ));
  };

  // 处理工序选择变化，自动填入相关信息
  const handleProcessChange = (index, field, value) => {
    if (field === 'process_id') {
      const updatedProcesses = [...productProcesses];
      if (value) {
        // 查找选中的工序信息
        const selectedProcess = (formOptions.processes || []).find(p => p.value === value);
        if (selectedProcess) {
          updatedProcesses[index] = {
            ...updatedProcesses[index],
            process_id: value,
            process_name: selectedProcess.process_name,
            process_category_name: selectedProcess.process_category_name || '',
            scheduling_method: selectedProcess.scheduling_method || '',
            unit: selectedProcess.unit || ''
          };
        }
      } else {
        // 清空选择
        updatedProcesses[index] = {
          ...updatedProcesses[index],
          process_id: '',
          process_name: '',
          process_category_name: '',
          scheduling_method: '',
          unit: ''
        };
      }
      setProductProcesses(updatedProcesses);
    } else {
      const processId = productProcesses[index].id;
      updateProcess(processId, field, value);
    }
  };

  // 材料管理功能
  const addMaterial = () => {
    const newMaterial = {
      id: Date.now(),
      material_id: '',
      material_name: '',
      material_code: '',
      material_category_name: '',
      material_attribute: '',
      sort_order: productMaterials.length + 1
    };
    setProductMaterials([...productMaterials, newMaterial]);
  };

  const removeMaterial = (id) => {
    setProductMaterials(productMaterials.filter(m => m.id !== id));
  };

  const updateMaterial = (id, field, value) => {
    setProductMaterials(productMaterials.map(m => 
      m.id === id ? { ...m, [field]: value } : m
    ));
  };

  // 处理材料选择变化，自动填入相关信息
  const handleMaterialChange = (index, field, value) => {
    if (field === 'material_id') {
      const updatedMaterials = [...productMaterials];
      if (value) {
        // 查找选中的材料信息
        const selectedMaterial = (formOptions.materials || []).find(m => m.value === value);
        if (selectedMaterial) {
          updatedMaterials[index] = {
            ...updatedMaterials[index],
            material_id: value,
            material_name: selectedMaterial.material_name,
            material_code: selectedMaterial.material_code || '',
            material_category_name: selectedMaterial.material_category_name || '',
            material_attribute: selectedMaterial.material_attribute || ''
          };
        }
      } else {
        // 清空选择
        updatedMaterials[index] = {
          ...updatedMaterials[index],
          material_id: '',
          material_name: '',
          material_code: '',
          material_category_name: '',
          material_attribute: ''
        };
      }
      setProductMaterials(updatedMaterials);
    } else {
      const materialId = productMaterials[index].id;
      updateMaterial(materialId, field, value);
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '产品编号',
      dataIndex: 'product_code',
      key: 'product_code',
      width: 120,
      fixed: 'left'
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 200,
      fixed: 'left'
    },
    {
      title: '客户名称',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 150
    },
    {
      title: '袋型',
      dataIndex: 'bag_type_name',
      key: 'bag_type_name',
      width: 120
    },
    {
      title: '产品类型',
      dataIndex: 'product_type',
      key: 'product_type',
      width: 100,
      render: (type) => {
        const typeMap = {
          finished: { color: 'green', text: '成品' },
          semi: { color: 'orange', text: '半成品' },
          material: { color: 'blue', text: '原料' }
        };
        const config = typeMap[type] || { color: 'default', text: type };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '规格',
      dataIndex: 'specification',
      key: 'specification',
      width: 200,
      ellipsis: true
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status) => {
        const statusMap = {
          active: { color: 'green', text: '启用' },
          inactive: { color: 'red', text: '停用' },
          pending: { color: 'orange', text: '待审核' }
        };
        const statusInfo = statusMap[status] || { color: 'default', text: status };
        return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
      }
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text) => text ? new Date(text).toLocaleString() : '-'
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个产品吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 基础信息标签页 - 根据用户字段整理重新设计
  const renderBasicInfo = () => (
    <div>
      {/* 第一部分：基本信息 */}
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="product_code" label="产品编号">
            <Input 
              disabled 
              placeholder={modalType === 'create' ? '系统自动生成' : ''} 
            />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="product_name" label="产品名称" rules={[{ required: true, message: '请输入产品名称' }]}>
            <Input placeholder="请输入产品名称" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="customer_id" label="客户">
            <Select
              placeholder="请选择客户"
              showSearch
              filterOption={(input, option) =>
                option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
              }
              onChange={handleCustomerChange}
            >
              {(formOptions.customers || []).map(customer => (
                <Option key={customer.value || customer.id} value={customer.value || customer.id}>
                  {customer.label || customer.customer_name}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="bag_type_id" label="袋型">
            <Select
              placeholder="请选择袋型"
              showSearch
              filterOption={(input, option) =>
                option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
              }
              onChange={handleBagTypeChange}
            >
              {(formOptions.bagTypes || []).map(bagType => (
                <Option key={bagType.value || bagType.id} value={bagType.value || bagType.id}>
                  {bagType.label || bagType.bag_name}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="unit_id" label="单位" rules={[{ required: true, message: '请选择单位' }]}>
            <Select placeholder="请选择单位">
              {(formOptions.units || []).map(unit => (
                <Option key={unit.value || unit.id} value={unit.value || unit.id}>
                  {unit.label || unit.unit_name}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="specification" label="产品规格">
            <Input style={{ width: '100%' }} placeholder="宽*厚度*密度" />
          </Form.Item>
        </Col>
        
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="product_category" label="产品类别">
            <Select placeholder="请选择产品类别">
              <Option value="plastic_bag">塑料袋</Option>
              <Option value="paper_bag">纸袋</Option>
              <Option value="cloth_bag">布袋</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="film_structure" label="理膜结构">
            <Input placeholder="根据选择袋型自动输入" disabled />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="bag_body" label="袋体">
            <Select placeholder="请选择袋体">
              <Option value="single">单体</Option>
              <Option value="composite">复合</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="bag_system" label="袋型系统">
            <Select placeholder="根据选择的袋型自动输入" disabled>
              <Option value="system1">系统1</Option>
              <Option value="system2">系统2</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="product_type" label="产品类型" initialValue="finished">
            <Select placeholder="成品" disabled>
              <Option value="finished">成品</Option>
              <Option value="semi">半成品</Option>
              <Option value="material">原料</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="salesperson_id" label="业务员">
            <Select 
              placeholder={'根据客户自动填入'} 
              disabled
              showSearch
              filterOption={(input, option) =>
                option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
              }
            >
              {(formOptions.employees || []).map(employee => (
                <Option key={employee.value || employee.id} value={employee.value || employee.id}>
                  {employee.label || employee.employee_name}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
      
      </Row>

      {/* 库存信息 */}
      <Divider orientation="left">库存信息</Divider>
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="min_inventory" label="最小库存">
            <InputNumber min={0} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="max_inventory" label="最大库存">
            <InputNumber min={0} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="safety_stock" label="安全库存">
            <InputNumber min={0} placeholder="根据单位库存提醒" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      {/* 价格信息 */}
      <Divider orientation="left">价格信息</Divider>
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name="print_plates" label="印刷版数">
            <InputNumber min={0} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="specification_size" label="规格">
            <InputNumber min={0} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="standard_price" label="单价">
            <InputNumber min={0} step={0.01} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="quote_price" label="报价">
            <InputNumber min={0} step={0.01} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="order_quantity" label="按订量">
            <InputNumber min={0} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="starting_quantity" label="起配">
            <InputNumber min={0} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="plate_fee_method" label="版费方式">
            <Select placeholder="客户付款/公司付款/滞工付款/付费/购买">
              <Option value="customer_pay">客户付款</Option>
              <Option value="company_pay">公司付款</Option>
              <Option value="delay_pay">滞工付款</Option>
              <Option value="fee_pay">付费</Option>
              <Option value="purchase">购买</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="charge_amount" label="收费金额">
            <InputNumber min={0} step={0.01} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="external_amount" label="外收金额">
            <InputNumber min={0} step={0.01} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="charge_regulation" label="收费规定">
            <InputNumber min={0} step={0.01} placeholder="0" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      {/* 材料信息 */}
      <Divider orientation="left">材料信息</Divider>
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="material_primary" label="材料">
            <Select placeholder="请选择材料">
              <Option value="pe">聚乙烯</Option>
              <Option value="pp">聚丙烯</Option>
              <Option value="pvc">聚氯乙烯</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="material_secondary" label="材料(自动)">
            <Input placeholder="根据主材料自动填入" disabled />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="cold_flat" label="冷平">
            <Select placeholder="请选择冷平">
              <Option value="yes">是</Option>
              <Option value="no">否</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="special_notes" label="备注信息">
            <TextArea rows={2} placeholder="请输入备注信息" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="special_remarks" label="特殊备注">
            <TextArea rows={2} placeholder="请输入特殊备注" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={24}>
          <Form.Item name="work_standard" label="作业基准">
            <TextArea rows={2} placeholder="请输入作业基准" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="moisture_content" label="含水率">
            <Select placeholder="请选择含水率">
              <Option value="low">低</Option>
              <Option value="medium">中</Option>
              <Option value="high">高</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>

      {/* 功能开关 */}
      <Divider orientation="left">功能开关</Divider>
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name="is_main_product" label="主产品" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="is_spare" label="备用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="is_revised" label="改版" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="no_audit_needed" label="无需审版" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name="charge_revision" label="收费改版" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="gov_manual" label="政府手册" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="no_revision_needed" label="无需改版" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="simple_revision" label="简易改版" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name="copy_foreign_trade" label="复制外贸" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Col>
      </Row>
    </div>
  );

  // 产品结构标签页 - 根据用户字段整理重新设计
  const renderProductStructure = () => (
    <div>
      {/* 基础尺寸 */}
      <Divider orientation="left">基础尺寸</Divider>
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'length']} label="长">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'width']} label="宽">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'side_width']} label="侧宽">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'bottom_width']} label="底宽">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'thickness']} label="厚度">
            <InputNumber min={0} step={0.1} addonAfter="μm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'total_thickness']} label="总厚度">
            <InputNumber min={0} step={0.1} addonAfter="μm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'density']} label="密度">
            <InputNumber min={0} step={0.01} addonAfter="g/cm³" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'volume']} label="体积">
            <InputNumber min={0} addonAfter="L" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'weight']} label="重量">
            <InputNumber min={0} step={0.01} addonAfter="g" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      {/* 分切信息 */}
      <Divider orientation="left">分切信息</Divider>
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'cut_length']} label="分切长">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'cut_width']} label="分切宽">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'cut_thickness']} label="分切厚度">
            <InputNumber min={0} step={0.1} addonAfter="μm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'cut_area']} label="分切面积">
            <InputNumber min={0} step={0.01} addonAfter="m²" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      {/* 光标尺寸 */}
      <Divider orientation="left">光标尺寸</Divider>
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'light_eye_length']} label="光标长">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'light_eye_width']} label="光标宽">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'light_eye_distance']} label="光标距离">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'edge_sealing_width']} label="封边宽度">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      {/* 收费信息 */}
      <Divider orientation="left">收费信息</Divider>
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'bag_making_fee']} label="制袋费">
            <InputNumber min={0} step={0.01} addonAfter="元" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'container_fee']} label="装袋费">
            <InputNumber min={0} step={0.01} addonAfter="元" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'cuff_fee']} label="打提手费">
            <InputNumber min={0} step={0.01} addonAfter="元" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_length']} label="托盘长">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_width']} label="托盘宽">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_height']} label="托盘高">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_1']} label="托盘1">
            <InputNumber min={0} addonAfter="个" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_2']} label="托盘2">
            <InputNumber min={0} addonAfter="个" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_3']} label="托盘3">
            <InputNumber min={0} addonAfter="个" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'winding_diameter']} label="收卷直径">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      {/* 封口信息 */}
      <Divider orientation="left">封口信息</Divider>
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'seal_top']} label="封口上">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'seal_left']} label="封口左">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'seal_right']} label="封口右">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'seal_middle']} label="封口中">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_structures', 'sealing_temperature']} label="封合温度">
            <InputNumber min={0} addonAfter="℃" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_structures', 'sealing_width']} label="封合宽度">
            <InputNumber min={0} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_structures', 'sealing_strength']} label="封合强度">
            <InputNumber min={0} step={0.1} addonAfter="N" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_structures', 'sealing_method']} label="封机方式">
            <Select placeholder="请选择封机方式">
              <Option value="heat_seal">热封</Option>
              <Option value="cold_seal">冷封</Option>
              <Option value="adhesive">胶粘</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_structures', 'power']} label="功率">
            <InputNumber min={0} step={0.1} addonAfter="kW" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>
         </div>
   );

  // 产品图片标签页
  const renderProductImages = () => (
    <Row gutter={16}>
      <Col span={24}>
        <Dragger {...handleImageUpload} fileList={productImages}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单次或批量上传，最多4张图片，每张不超过2MB
          </p>
        </Dragger>
      </Col>
      <Col span={24} style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
          {productImages.map((image, index) => (
            <div key={image.uid} style={{ position: 'relative' }}>
              <Image
                width={200}
                height={150}
                src={image.url || image.thumbUrl}
                placeholder="图片加载中..."
                style={{ objectFit: 'cover', borderRadius: 8 }}
              />
              <div style={{ 
                position: 'absolute', 
                top: 8, 
                left: 8, 
                background: 'rgba(0,0,0,0.7)', 
                color: 'white', 
                padding: '2px 6px', 
                borderRadius: 4, 
                fontSize: 12 
              }}>
                图片{index + 1}
              </div>
            </div>
          ))}
        </div>
      </Col>
    </Row>
  );

    // 渲染工序管理
  const renderProcesses = () => {
    return (
      <div>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={24}>
            <Button type="dashed" onClick={addProcess} icon={<PlusOutlined />} style={{ width: '100%' }}>
              添加工序
            </Button>
          </Col>
        </Row>
                
        {productProcesses.map((process, index) => (
          <Card 
            key={process.id} 
            size="small" 
            style={{ marginBottom: 8 }}
            title={`工序 ${index + 1}`}
            bodyStyle={{ padding: '8px 12px' }}
          >
            <Row gutter={8} align="middle">
              <Col span={5}>
                <span style={{ fontSize: 12, color: '#666', marginRight: 4 }}>工序名称:</span>
                                  <Select
                    placeholder="请选择工序"
                    value={process.process_id}
                    onChange={(value) => handleProcessChange(index, 'process_id', value)}
                    showSearch
                    size="small"
                    style={{ width: '70%' }}
                    filterOption={(input, option) =>
                      option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                    }
                  >
                    {(formOptions.processes || [])
                      .filter(p => {
                        // 过滤掉已经被其他工序选择的项目
                        const selectedProcessIds = productProcesses
                          .filter((proc, idx) => idx !== index && proc.process_id)
                          .map(proc => proc.process_id);
                        return !selectedProcessIds.includes(p.value);
                      })
                      .map(p => (
                        <Option key={p.value} value={p.value}>
                          {p.label}
                        </Option>
                      ))}
                  </Select>
              </Col>
              <Col span={4}>
                <span style={{ fontSize: 12, color: '#666', marginRight: 4 }}>工序分类:</span>
                <Input
                  value={process.process_category_name || ''}
                  readOnly
                  size="small"
                  style={{ width: '60%' }}
                  placeholder="自动填入"
                />
              </Col>
              <Col span={4}>
                <span style={{ fontSize: 12, color: '#666', marginRight: 4 }}>排程方式:</span>
                <Input
                  value={process.scheduling_method || ''}
                  readOnly
                  size="small"
                  style={{ width: '60%' }}
                  placeholder="自动填入"
                />
              </Col>
              <Col span={3}>
                <span style={{ fontSize: 12, color: '#666', marginRight: 4 }}>单位:</span>
                <Input
                  value={process.unit || ''}
                  readOnly
                  size="small"
                  style={{ width: '60%' }}
                  placeholder="自动填入"
                />
              </Col>
              <Col span={3}>
                <span style={{ fontSize: 12, color: '#666', marginRight: 4 }}>排序:</span>
                <InputNumber
                  min={0}
                  value={process.sort_order}
                  onChange={(value) => updateProcess(process.id, 'sort_order', value)}
                  size="small"
                  style={{ width: '60%' }}
                />
              </Col>
              <Col span={5} style={{ textAlign: 'right' }}>
                <Button 
                  type="text" 
                  danger 
                  icon={<DeleteOutlined />} 
                  onClick={() => removeProcess(process.id)}
                  size="small"
                >
                  删除
                </Button>
              </Col>
            </Row>
          </Card>
        ))}
        
        {productProcesses.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            暂无工序，点击上方按钮添加工序
          </div>
        )}
      </div>
    );
  };

    // 渲染材料管理
  const renderMaterials = () => {
    return (
      <div>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={24}>
            <Button type="dashed" onClick={addMaterial} icon={<PlusOutlined />} style={{ width: '100%' }}>
              添加材料
            </Button>
          </Col>
        </Row>
                
        {productMaterials.map((material, index) => (
          <Card 
            key={material.id} 
            size="small" 
            style={{ marginBottom: 8 }}
            title={`材料 ${index + 1}`}
            bodyStyle={{ padding: '8px 12px' }}
          >
            <Row gutter={8} align="middle">
              <Col span={4}>
                <span style={{ fontSize: 12, color: '#666', marginRight: 4 }}>材料编号:</span>
                <Input
                  value={material.material_code || ''}
                  readOnly
                  size="small"
                  style={{ width: '65%' }}
                  placeholder="自动填入"
                />
              </Col>
              <Col span={5}>
                <span style={{ fontSize: 12, color: '#666', marginRight: 4 }}>材料名称:</span>
                                  <Select
                    placeholder="请选择材料"
                    value={material.material_id}
                    onChange={(value) => handleMaterialChange(index, 'material_id', value)}
                    showSearch
                    size="small"
                    style={{ width: '70%' }}
                    filterOption={(input, option) =>
                      option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                    }
                  >
                    {(formOptions.materials || [])
                      .filter(m => {
                        // 过滤掉已经被其他材料选择的项目
                        const selectedMaterialIds = productMaterials
                          .filter((mat, idx) => idx !== index && mat.material_id)
                          .map(mat => mat.material_id);
                        return !selectedMaterialIds.includes(m.value);
                      })
                      .map(m => (
                        <Option key={m.value} value={m.value}>
                          {m.label}
                        </Option>
                      ))}
                  </Select>
              </Col>
              <Col span={4}>
                <span style={{ fontSize: 12, color: '#666', marginRight: 4 }}>材料分类:</span>
                <Input
                  value={material.material_category_name || ''}
                  readOnly
                  size="small"
                  style={{ width: '60%' }}
                  placeholder="自动填入"
                />
              </Col>
              <Col span={4}>
                <span style={{ fontSize: 12, color: '#666', marginRight: 4 }}>材料属性:</span>
                <Input
                  value={material.material_attribute || ''}
                  readOnly
                  size="small"
                  style={{ width: '60%' }}
                  placeholder="自动填入"
                />
              </Col>
              <Col span={3}>
                <span style={{ fontSize: 12, color: '#666', marginRight: 4 }}>排序:</span>
                <InputNumber
                  min={0}
                  value={material.sort_order}
                  onChange={(value) => updateMaterial(material.id, 'sort_order', value)}
                  size="small"
                  style={{ width: '60%' }}
                />
              </Col>
              <Col span={4} style={{ textAlign: 'right' }}>
                <Button 
                  type="text" 
                  danger 
                  icon={<DeleteOutlined />} 
                  onClick={() => removeMaterial(material.id)}
                  size="small"
                >
                  删除
                </Button>
              </Col>
            </Row>
          </Card>
        ))}
        
        {productMaterials.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            暂无材料，点击上方按钮添加材料
          </div>
        )}
      </div>
    );
  };

  // 理化指标标签页
  const renderQualityIndicators = () => (
    <div>
      {/* 工艺要求 */}
      <Divider orientation="left">工艺要求</Divider>
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'packaging_requirement']} label="包装要求">
            <Select placeholder="请选择包装要求">
              <Option value="vacuum">真空包装</Option>
              <Option value="standard">标准包装</Option>
              <Option value="special">特殊包装</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'tensile_requirement']} label="拉丝要求">
            <Select placeholder="请选择拉丝要求">
              <Option value="high">高要求</Option>
              <Option value="medium">中等要求</Option>
              <Option value="low">低要求</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'opening_requirement']} label="开口要求">
            <Select placeholder="请选择开口要求">
              <Option value="easy">易开口</Option>
              <Option value="normal">普通开口</Option>
              <Option value="difficult">难开口</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'slip_requirement']} label="爽滑要求">
            <Select placeholder="请选择爽滑要求">
              <Option value="high">高爽滑</Option>
              <Option value="medium">中等爽滑</Option>
              <Option value="low">低爽滑</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'cut_requirement']} label="切刀要求">
            <Select placeholder="请选择切刀要求">
              <Option value="sharp">锋利切割</Option>
              <Option value="smooth">平滑切割</Option>
              <Option value="special">特殊切割</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'anti_static_requirement']} label="抗静电要求">
            <Select placeholder="请选择抗静电要求">
              <Option value="high">高抗静电</Option>
              <Option value="medium">中等抗静电</Option>
              <Option value="low">低抗静电</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'sterilization_requirement']} label="灭菌要求">
            <Select placeholder="请选择灭菌要求">
              <Option value="required">需要灭菌</Option>
              <Option value="not_required">不需要灭菌</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'hygiene_requirement']} label="卫生要求">
            <Select placeholder="请选择卫生要求">
              <Option value="food_grade">食品级</Option>
              <Option value="medical_grade">医疗级</Option>
              <Option value="industrial_grade">工业级</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'special_requirement']} label="特殊要求">
            <TextArea rows={2} placeholder="请输入特殊要求" />
          </Form.Item>
        </Col>
      </Row>

      {/* 理化指标 */}
      <Divider orientation="left">理化指标</Divider>
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'tensile_strength_md']} label="拉伸强度≥(MD方向)">
            <InputNumber min={0} step={0.1} addonAfter="MPa" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'tensile_strength_td']} label="拉伸强度≥(TD方向)">
            <InputNumber min={0} step={0.1} addonAfter="MPa" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'elongation_break_md']} label="断裂伸长率≥(MD方向)">
            <InputNumber min={0} step={0.1} addonAfter="%" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'elongation_break_td']} label="断裂伸长率≥(TD方向)">
            <InputNumber min={0} step={0.1} addonAfter="%" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'dart_drop_impact']} label="抗冲击性能">
            <InputNumber min={0} step={0.1} addonAfter="J" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'heat_shrinkage']} label="热收缩率">
            <InputNumber min={0} step={0.1} addonAfter="%" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'oxygen_transmission_rate']} label="氧气透过率≤(O2/15μm)">
            <InputNumber min={0} step={0.1} addonAfter="cm³/m²·d" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'water_vapor_transmission_rate']} label="水蒸气透过率≤(MJ/m²)">
            <InputNumber min={0} step={0.1} addonAfter="g/m²·d" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'seal_strength']} label="热封强度≥(g/m²)">
            <InputNumber min={0} step={0.1} addonAfter="N/15mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'peel_strength_top']} label="剥离度(上层)">
            <InputNumber min={0} step={0.1} addonAfter="N/15mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'peel_strength_bottom']} label="剥离度(下层)">
            <InputNumber min={0} step={0.1} addonAfter="N/15mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'friction_coefficient']} label="摩擦力">
            <InputNumber min={0} step={0.001} style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={24}>
          <Form.Item name={['product_quality_indicators', 'test_standard']} label="检验依据">
            <Select placeholder="不可编辑" disabled>
              <Option value="national_standard">国家标准</Option>
              <Option value="industry_standard">行业标准</Option>
              <Option value="enterprise_standard">企业标准</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>
    </div>
  );

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        {/* 页面标题 */}
        <div style={{ marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>
            产品管理
          </Title>
        </div>

        {/* 搜索和操作栏 */}
        <div style={{ marginBottom: 16 }}>
          <Row gutter={16} justify="space-between">
            <Col>
              <Space>
                <Input
                  placeholder="搜索产品编号、名称或规格"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={handleSearch}
                  style={{ width: 250 }}
                  prefix={<SearchOutlined />}
                />
                <Select
                  placeholder="选择客户"
                  value={filters.customer_id}
                  onChange={(value) => setFilters(prev => ({ ...prev, customer_id: value }))}
                  style={{ width: 150 }}
                  allowClear
                >
                  {(formOptions.customers || []).map(customer => (
                    <Option key={customer.value || customer.id} value={customer.value || customer.id}>
                      {customer.label || customer.customer_name}
                    </Option>
                  ))}
                </Select>
                <Select
                  placeholder="选择袋型"
                  value={filters.bag_type_id}
                  onChange={(value) => setFilters(prev => ({ ...prev, bag_type_id: value }))}
                  style={{ width: 150 }}
                  allowClear
                >
                  {(formOptions.bagTypes || []).map(bagType => (
                    <Option key={bagType.value || bagType.id} value={bagType.value || bagType.id}>
                      {bagType.label || bagType.bag_name}
                    </Option>
                  ))}
                </Select>
                <Button onClick={handleSearch} type="primary">
                  搜索
                </Button>
                <Button onClick={handleReset}>
                  重置
                </Button>
              </Space>
            </Col>
            <Col>
              <Space>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleAdd}
                >
                  新增产品
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={() => loadData()}
                >
                  刷新
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        {/* 数据表格 */}
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
          size="middle"
        />
      </Card>

      {/* 产品编辑弹窗 */}
      <Modal
        title={
          modalType === 'create' ? '新增产品' :
          modalType === 'edit' ? '编辑产品' : '查看产品'
        }
        open={modalVisible}
        onCancel={closeModal}
        width={1200}
        style={{ top: 20 }}
        footer={modalType === 'view' ? [
          <Button key="close" onClick={closeModal}>
            关闭
          </Button>
        ] : [
          <Button key="cancel" onClick={closeModal}>
            取消
          </Button>,
          <Button
            key="save"
            type="primary"
            loading={confirmLoading}
            onClick={handleSave}
          >
            保存
          </Button>
        ]}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          disabled={modalType === 'view'}
          key={`${modalType}-${editingRecord?.id || 'new'}`}
        >
          <Tabs 
            activeKey={activeTabKey} 
            onChange={setActiveTabKey}
            items={[
              {
                key: 'basic',
                label: '基础信息',
                children: renderBasicInfo()
              },
              {
                key: 'structure',
                label: '产品结构',
                children: renderProductStructure()
              },
              {
                key: 'images',
                label: '产品图片',
                children: renderProductImages()
              },
              {
                key: 'quality',
                label: '理化指标',
                children: renderQualityIndicators()
              },
              {
                key: 'processes',
                label: '工序管理',
                children: renderProcesses()
              },
              {
                key: 'materials',
                label: '材料管理',
                children: renderMaterials()
              }
            ]}
          />
        </Form>
      </Modal>
    </div>
  );
};

export default ProductManagement;