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
    pageSize: 10,
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
  const [deletedImages, setDeletedImages] = useState([]); // 跟踪被删除的图片
  const [originalImages, setOriginalImages] = useState([]); // 记录编辑开始时的原始图片
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
        
        // 立即上传图片到服务器
        const response = await productManagementApi.uploadImage(file);
        
  
        
        onProgress({ percent: 100 });
        
        // 确保返回正确的数据结构
        const result = {
          url: response.data.data.url,
          filename: response.data.data.filename,
          original_name: response.data.data.original_name,
          size: response.data.data.size
        };
        
        // 重要：需要将结果包装在 data 字段中
        
        // 直接调用onSuccess，让Ant Design处理数据
        onSuccess(result);
        
      } catch (error) {
        console.error('图片上传失败:', error);
        onError(error);
        
        // 显示具体的错误信息
        let errorMessage = '图片上传失败';
        if (error.response && error.response.data && error.response.data.message) {
          errorMessage = error.response.data.message;
        } else if (error.message) {
          errorMessage = error.message;
        }
        message.error(errorMessage);
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
        // 处理上传成功的文件
        if (file.response) {
          // 直接使用response中的数据
          file.url = file.response.url;
          file.name = file.response.filename;
          file.status = 'done';
          file.thumbUrl = file.response.url;
        }
        
        return file;
      });
      
      setProductImages(fileList);
    }
  };

  // 删除图片处理
  const handleDeleteImage = async (image) => {
    try {
  
      
      // 记录被删除的图片，用于保存时删除服务器文件
      setDeletedImages(prev => [...prev, image]);
      
      // 从本地图片列表中移除
      const newImageList = productImages.filter(img => img.uid !== image.uid);
      setProductImages(newImageList);
      
      message.success('图片已从表单中移除');
      
    } catch (error) {
      console.error('删除图片失败:', error);
      message.error('删除图片失败');
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
    setOriginalImages([]); // 新建时清空原始图片
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
        
        // 处理产品结构数据
        const formData = { ...productDetail };
        // 初始化产品结构数据，不设置默认值
        formData.product_structures = {};
        
        if (productDetail.structures && productDetail.structures.length > 0) {
          // 将第一个结构数据展开到product_structures字段
          const structure = productDetail.structures[0];
          formData.product_structures = {
            length: structure.length,
            width: structure.width,
            height: structure.height,
            side_width: structure.side_width,
            bottom_width: structure.bottom_width,
            thickness: structure.thickness,
            total_thickness: structure.total_thickness,
            volume: structure.volume,
            weight: structure.weight,
            expand_length: structure.expand_length,
            expand_width: structure.expand_width,
            expand_height: structure.expand_height,
            material_length: structure.material_length,
            material_width: structure.material_width,
            material_height: structure.material_height,
            single_length: structure.single_length,
            single_width: structure.single_width,
            single_height: structure.single_height,
            blue_color: structure.blue_color,
            red_color: structure.red_color,
            other_color: structure.other_color,
            // 新增字段
            cut_length: structure.cut_length,
            cut_width: structure.cut_width,
            cut_thickness: structure.cut_thickness,
            cut_area: structure.cut_area,
            light_eye_length: structure.light_eye_length,
            light_eye_width: structure.light_eye_width,
            light_eye_distance: structure.light_eye_distance,
            edge_sealing_width: structure.edge_sealing_width,
            bag_making_fee: structure.bag_making_fee,
            container_fee: structure.container_fee,
            cuff_fee: structure.cuff_fee,
            pallet_length: structure.pallet_length,
            pallet_width: structure.pallet_width,
            pallet_height: structure.pallet_height,
            pallet_1: structure.pallet_1,
            pallet_2: structure.pallet_2,
            pallet_3: structure.pallet_3,
            winding_diameter: structure.winding_diameter,
            density: structure.density,
            seal_top: structure.seal_top,
            seal_left: structure.seal_left,
            seal_right: structure.seal_right,
            seal_middle: structure.seal_middle,
            sealing_temperature: structure.sealing_temperature,
            sealing_width: structure.sealing_width,
            sealing_strength: structure.sealing_strength,
            sealing_method: structure.sealing_method,
            power: structure.power
          };
        }
        
        // 处理客户需求数据
        if (productDetail.customer_requirements && productDetail.customer_requirements.length > 0) {
          // 将第一个客户需求数据展开到product_customer_requirements字段
          const customerRequirement = productDetail.customer_requirements[0];
          formData.product_customer_requirements = {
            appearance_requirements: customerRequirement.appearance_requirements,
            surface_treatment: customerRequirement.surface_treatment,
            printing_requirements: customerRequirement.printing_requirements,
            color_requirements: customerRequirement.color_requirements,
            pattern_requirements: customerRequirement.pattern_requirements,
            cutting_method: customerRequirement.cutting_method,
            cutting_width: customerRequirement.cutting_width,
            cutting_length: customerRequirement.cutting_length,
            cutting_thickness: customerRequirement.cutting_thickness,
            optical_distance: customerRequirement.optical_distance,
            optical_width: customerRequirement.optical_width,
            bag_sealing_up: customerRequirement.bag_sealing_up,
            bag_sealing_down: customerRequirement.bag_sealing_down,
            bag_sealing_left: customerRequirement.bag_sealing_left,
            bag_sealing_right: customerRequirement.bag_sealing_right,
            bag_sealing_middle: customerRequirement.bag_sealing_middle,
            bag_sealing_inner: customerRequirement.bag_sealing_inner,
            bag_length_tolerance: customerRequirement.bag_length_tolerance,
            bag_width_tolerance: customerRequirement.bag_width_tolerance,
            packaging_method: customerRequirement.packaging_method,
            packaging_requirements: customerRequirement.packaging_requirements,
            packaging_material: customerRequirement.packaging_material,
            packaging_quantity: customerRequirement.packaging_quantity,
            packaging_specifications: customerRequirement.packaging_specifications,
            req_tensile_strength: customerRequirement.tensile_strength,
            thermal_shrinkage: customerRequirement.thermal_shrinkage,
            impact_strength: customerRequirement.impact_strength,
            thermal_tensile_strength: customerRequirement.thermal_tensile_strength,
            water_vapor_permeability: customerRequirement.water_vapor_permeability,
            heat_shrinkage_curve: customerRequirement.heat_shrinkage_curve,
            melt_index: customerRequirement.melt_index,
            gas_permeability: customerRequirement.gas_permeability,
            custom_1: customerRequirement.custom_1,
            custom_2: customerRequirement.custom_2,
            custom_3: customerRequirement.custom_3,
            custom_4: customerRequirement.custom_4,
            custom_5: customerRequirement.custom_5,
            custom_6: customerRequirement.custom_6,
            custom_7: customerRequirement.custom_7
          };
        }

        // 处理理化指标数据
        if (productDetail.quality_indicators && productDetail.quality_indicators.length > 0) {
          // 将第一个理化指标数据展开到product_quality_indicators字段
          const qualityIndicator = productDetail.quality_indicators[0];
          formData.product_quality_indicators = {
            tensile_strength_longitudinal: qualityIndicator.tensile_strength_longitudinal,
            tensile_strength_transverse: qualityIndicator.tensile_strength_transverse,
            thermal_shrinkage_longitudinal: qualityIndicator.thermal_shrinkage_longitudinal,
            thermal_shrinkage_transverse: qualityIndicator.thermal_shrinkage_transverse,
            puncture_strength: qualityIndicator.puncture_strength,
            optical_properties: qualityIndicator.optical_properties,
            heat_seal_temperature: qualityIndicator.heat_seal_temperature,
            heat_seal_tensile_strength: qualityIndicator.heat_seal_tensile_strength,
            quality_water_vapor_permeability: qualityIndicator.water_vapor_permeability,
            oxygen_permeability: qualityIndicator.oxygen_permeability,
            friction_coefficient: qualityIndicator.friction_coefficient,
            peel_strength: qualityIndicator.peel_strength,
            test_standard: qualityIndicator.test_standard,
            test_basis: qualityIndicator.test_basis,
            indicator_1: qualityIndicator.indicator_1,
            indicator_2: qualityIndicator.indicator_2,
            indicator_3: qualityIndicator.indicator_3,
            indicator_4: qualityIndicator.indicator_4,
            indicator_5: qualityIndicator.indicator_5,
            indicator_6: qualityIndicator.indicator_6,
            indicator_7: qualityIndicator.indicator_7,
            indicator_8: qualityIndicator.indicator_8,
            indicator_9: qualityIndicator.indicator_9,
            indicator_10: qualityIndicator.indicator_10
          };
        }
        
        form.setFieldsValue(formData);
        
        // 加载产品图片
        if (productDetail.product_images && productDetail.product_images.length > 0) {
          const images = productDetail.product_images.map(img => ({
            uid: img.id,
            name: img.image_name,
            url: img.image_url,
            status: 'done'
          }));
          setProductImages(images);
          // 记录编辑开始时的原始图片（用于取消时判断哪些是新添加的）
          setOriginalImages([...images]);
        } else {
          setProductImages([]);
          setOriginalImages([]);
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
            id: material.id || Date.now() + Math.random(),
            material_name: material.material_name || '',
            material_code: material.material_code || '',
            material_category_name: material.material_category_name || '',
            material_attribute: material.material_attribute || '',
            process_id: material.process_id || '',
            process_name: material.process_name || '',
            supplier_id: material.supplier_id || '',
            supplier_name: material.supplier_name || '',
            layer_number: material.layer_number || '',
            material_process: material.material_process || '',
            remarks: material.remarks || '',
            hot_stamping_film_length: material.hot_stamping_film_length || null,
            hot_stamping_film_width: material.hot_stamping_film_width || null,
            material_file_remarks: material.material_file_remarks || '',
            sort_order: material.sort_order || 0
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
            length: structure.length,
            width: structure.width,
            height: structure.height,
            side_width: structure.side_width,
            bottom_width: structure.bottom_width,
            thickness: structure.thickness,
            total_thickness: structure.total_thickness,
            volume: structure.volume,
            weight: structure.weight,
            expand_length: structure.expand_length,
            expand_width: structure.expand_width,
            expand_height: structure.expand_height,
            material_length: structure.material_length,
            material_width: structure.material_width,
            material_height: structure.material_height,
            single_length: structure.single_length,
            single_width: structure.single_width,
            single_height: structure.single_height,
            blue_color: structure.blue_color,
            red_color: structure.red_color,
            other_color: structure.other_color,
            // 新增字段
            cut_length: structure.cut_length,
            cut_width: structure.cut_width,
            cut_thickness: structure.cut_thickness,
            cut_area: structure.cut_area,
            light_eye_length: structure.light_eye_length,
            light_eye_width: structure.light_eye_width,
            light_eye_distance: structure.light_eye_distance,
            edge_sealing_width: structure.edge_sealing_width,
            bag_making_fee: structure.bag_making_fee,
            container_fee: structure.container_fee,
            cuff_fee: structure.cuff_fee,
            pallet_length: structure.pallet_length,
            pallet_width: structure.pallet_width,
            pallet_height: structure.pallet_height,
            pallet_1: structure.pallet_1,
            pallet_2: structure.pallet_2,
            pallet_3: structure.pallet_3,
            winding_diameter: structure.winding_diameter,
            density: structure.density,
            seal_top: structure.seal_top,
            seal_left: structure.seal_left,
            seal_right: structure.seal_right,
            seal_middle: structure.seal_middle,
            sealing_temperature: structure.sealing_temperature,
            sealing_width: structure.sealing_width,
            sealing_strength: structure.sealing_strength,
            sealing_method: structure.sealing_method,
            power: structure.power
          };
        }
        
        // 处理客户需求数据
        if (productDetail.customer_requirements && productDetail.customer_requirements.length > 0) {
          // 将第一个客户需求数据展开到product_customer_requirements字段
          const customerRequirement = productDetail.customer_requirements[0];
          formData.product_customer_requirements = {
            appearance_requirements: customerRequirement.appearance_requirements,
            surface_treatment: customerRequirement.surface_treatment,
            printing_requirements: customerRequirement.printing_requirements,
            color_requirements: customerRequirement.color_requirements,
            pattern_requirements: customerRequirement.pattern_requirements,
            cutting_method: customerRequirement.cutting_method,
            cutting_width: customerRequirement.cutting_width,
            cutting_length: customerRequirement.cutting_length,
            cutting_thickness: customerRequirement.cutting_thickness,
            optical_distance: customerRequirement.optical_distance,
            optical_width: customerRequirement.optical_width,
            bag_sealing_up: customerRequirement.bag_sealing_up,
            bag_sealing_down: customerRequirement.bag_sealing_down,
            bag_sealing_left: customerRequirement.bag_sealing_left,
            bag_sealing_right: customerRequirement.bag_sealing_right,
            bag_sealing_middle: customerRequirement.bag_sealing_middle,
            bag_sealing_inner: customerRequirement.bag_sealing_inner,
            bag_length_tolerance: customerRequirement.bag_length_tolerance,
            bag_width_tolerance: customerRequirement.bag_width_tolerance,
            packaging_method: customerRequirement.packaging_method,
            packaging_requirements: customerRequirement.packaging_requirements,
            packaging_material: customerRequirement.packaging_material,
            packaging_quantity: customerRequirement.packaging_quantity,
            packaging_specifications: customerRequirement.packaging_specifications,
            req_tensile_strength: customerRequirement.tensile_strength,
            thermal_shrinkage: customerRequirement.thermal_shrinkage,
            impact_strength: customerRequirement.impact_strength,
            thermal_tensile_strength: customerRequirement.thermal_tensile_strength,
            water_vapor_permeability: customerRequirement.water_vapor_permeability,
            heat_shrinkage_curve: customerRequirement.heat_shrinkage_curve,
            melt_index: customerRequirement.melt_index,
            gas_permeability: customerRequirement.gas_permeability,
            custom_1: customerRequirement.custom_1,
            custom_2: customerRequirement.custom_2,
            custom_3: customerRequirement.custom_3,
            custom_4: customerRequirement.custom_4,
            custom_5: customerRequirement.custom_5,
            custom_6: customerRequirement.custom_6,
            custom_7: customerRequirement.custom_7
          };
        }

        // 处理理化指标数据
        if (productDetail.quality_indicators && productDetail.quality_indicators.length > 0) {
          // 将第一个理化指标数据展开到product_quality_indicators字段
          const qualityIndicator = productDetail.quality_indicators[0];
          formData.product_quality_indicators = {
            tensile_strength_longitudinal: qualityIndicator.tensile_strength_longitudinal,
            tensile_strength_transverse: qualityIndicator.tensile_strength_transverse,
            thermal_shrinkage_longitudinal: qualityIndicator.thermal_shrinkage_longitudinal,
            thermal_shrinkage_transverse: qualityIndicator.thermal_shrinkage_transverse,
            puncture_strength: qualityIndicator.puncture_strength,
            optical_properties: qualityIndicator.optical_properties,
            heat_seal_temperature: qualityIndicator.heat_seal_temperature,
            heat_seal_tensile_strength: qualityIndicator.heat_seal_tensile_strength,
            quality_water_vapor_permeability: qualityIndicator.water_vapor_permeability,
            oxygen_permeability: qualityIndicator.oxygen_permeability,
            friction_coefficient: qualityIndicator.friction_coefficient,
            peel_strength: qualityIndicator.peel_strength,
            test_standard: qualityIndicator.test_standard,
            test_basis: qualityIndicator.test_basis,
            indicator_1: qualityIndicator.indicator_1,
            indicator_2: qualityIndicator.indicator_2,
            indicator_3: qualityIndicator.indicator_3,
            indicator_4: qualityIndicator.indicator_4,
            indicator_5: qualityIndicator.indicator_5,
            indicator_6: qualityIndicator.indicator_6,
            indicator_7: qualityIndicator.indicator_7,
            indicator_8: qualityIndicator.indicator_8,
            indicator_9: qualityIndicator.indicator_9,
            indicator_10: qualityIndicator.indicator_10
          };
        }
        
        form.setFieldsValue(formData);
        
        // 加载产品图片
        if (productDetail.product_images && productDetail.product_images.length > 0) {
          const images = productDetail.product_images.map(img => ({
            uid: img.id,
            name: img.image_name,
            url: img.image_url,
            status: 'done'
          }));
          setProductImages(images);
          // 记录编辑开始时的原始图片（用于取消时判断哪些是新添加的）
          setOriginalImages([...images]);
        } else {
          setProductImages([]);
          setOriginalImages([]);
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
            id: material.id || Date.now() + Math.random(),
            material_name: material.material_name || '',
            material_code: material.material_code || '',
            material_category_name: material.material_category_name || '',
            material_attribute: material.material_attribute || '',
            process_id: material.process_id || '',
            process_name: material.process_name || '',
            supplier_id: material.supplier_id || '',
            supplier_name: material.supplier_name || '',
            layer_number: material.layer_number || '',
            material_process: material.material_process || '',
            remarks: material.remarks || '',
            hot_stamping_film_length: material.hot_stamping_film_length || null,
            hot_stamping_film_width: material.hot_stamping_film_width || null,
            material_file_remarks: material.material_file_remarks || '',
            sort_order: material.sort_order || 0
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
        image_url: img.url || img.response?.data?.url || img.response?.url,
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

      // 验证材料数据
      const materialsWithProcess = productMaterials.filter(material => material.material_id);
      for (const material of materialsWithProcess) {
        const process_id = material.process_id;
        const materialDisplayName = material.material_name || material.material_code || `材料${material.id}`;
        if (!process_id || process_id === '' || process_id === 'null') {
          message.error(`材料 "${materialDisplayName}" 必须选择工序`);
          return;
        }
      }

      // 处理材料数据 - 只传送必要字段
      const materialData = materialsWithProcess.map(material => ({
        material_id: material.material_id,
        process_id: material.process_id,
        material_name: material.material_name,
        material_code: material.material_code,
        material_category_name: material.material_category_name,
        material_attribute: material.material_attribute,
        sort_order: material.sort_order || 0,
        layer_number: material.layer_number,
        supplier_id: material.supplier_id,
        material_process: material.material_process,
        remarks: material.remarks,
        hot_stamping_film_length: material.hot_stamping_film_length,
        hot_stamping_film_width: material.hot_stamping_film_width,
        material_file_remarks: material.material_file_remarks
      }));
      
      // 处理产品结构数据
      const structureData = values.product_structures || {};

      // 过滤掉undefined和null值，只保留有效数据
      const filteredStructureData = {};
      Object.keys(structureData).forEach(key => {
        if (structureData[key] !== undefined && structureData[key] !== null && structureData[key] !== '') {
          filteredStructureData[key] = structureData[key];
        }
      });

      // 处理客户需求数据
      const customerRequirementsData = values.product_customer_requirements || {};
      // 过滤掉undefined和null值，只保留有效数据
      const filteredCustomerRequirementsData = {};
      Object.keys(customerRequirementsData).forEach(key => {
        if (customerRequirementsData[key] !== undefined && customerRequirementsData[key] !== null && customerRequirementsData[key] !== '') {
          filteredCustomerRequirementsData[key] = customerRequirementsData[key];
        }
      });
      
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
        customer_requirements: filteredCustomerRequirementsData, // 将过滤后的客户需求数据作为customer_requirements字段传递
        quality_indicators: filteredQualityIndicatorsData, // 将过滤后的理化指标数据作为quality_indicators字段传递
        product_images: imageData,
        product_processes: processData,
        product_materials: materialData
      };
      
      // 删除嵌套的字段，避免重复
      delete productData.product_structures;
      delete productData.product_customer_requirements;
      delete productData.product_quality_indicators;

      if (modalType === 'create') {
        await productManagementApi.createProduct(productData);
        message.success('产品创建成功');
      } else if (modalType === 'edit') {
        await productManagementApi.updateProduct(editingRecord.id, productData);
        message.success('产品更新成功');
      }

      // 保存成功后，删除被删除的图片文件
      if (deletedImages.length > 0) {
  
        for (const image of deletedImages) {
          let filename = null;
          
          // 获取文件名
          if (image.response && image.response.data && image.response.data.filename) {
            filename = image.response.data.filename;
          } else if (image.response && image.response.filename) {
            filename = image.response.filename;
          } else if (image.name) {
            filename = image.name;
          } else if (image.url) {
            const urlParts = image.url.split('/');
            filename = urlParts[urlParts.length - 1];
          }
          
          if (filename) {
            try {
              await productManagementApi.deleteImage(filename);
  
            } catch (deleteError) {
              console.warn('删除图片文件失败:', filename, deleteError);
            }
          }
        }
      }

      setModalVisible(false);
      setDeletedImages([]); // 清空被删除的图片列表
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
  const closeModal = async () => {
    // 只清理新添加的图片（在编辑过程中上传但未保存到数据库的图片）
    if (productImages.length > 0) {
      try {
        // 🔒 安全检查：如果是编辑模式但originalImages为空，说明有问题，不删除任何图片
        if (modalType === 'edit' && originalImages.length === 0 && productImages.length > 0) {
          console.warn('⚠️ 编辑模式下originalImages为空，跳过图片清理以防误删');
          setModalVisible(false);
          setEditingRecord(null);
          setActiveTabKey('basic');
          setProductImages([]);
          setOriginalImages([]);
          setDeletedImages([]);
          setProductProcesses([]);
          setProductMaterials([]);
          form.resetFields();
          return;
        }
        
        // 找出新添加的图片（不在原始图片列表中的图片）
        const newImages = productImages.filter(currentImage => {
          // 如果有response字段，说明是新上传的
          if (currentImage.response) {
            return true;
          }
          
          // 如果不在原始图片列表中，也认为是新添加的
          const isOriginal = originalImages.some(originalImage => 
            originalImage.uid === currentImage.uid || 
            originalImage.name === currentImage.name ||
            originalImage.url === currentImage.url
          );
          
          return !isOriginal;
        });
        

        
        // 只删除新添加的图片
        for (const image of newImages) {
          let filename = null;
          
          // 获取文件名：优先从response获取，其次从name获取，最后从URL提取
          if (image.response && image.response.data && image.response.data.filename) {
            filename = image.response.data.filename;
          } else if (image.response && image.response.filename) {
            filename = image.response.filename;
          } else if (image.name) {
            filename = image.name;
          } else if (image.url) {
            // 从URL中提取文件名
            const urlParts = image.url.split('/');
            filename = urlParts[urlParts.length - 1];
          }
          
          if (filename) {
            try {
              await productManagementApi.deleteImage(filename);

            } catch (deleteError) {

            }
          }
        }
        
        if (newImages.length > 0) {
          message.info(`已清理 ${newImages.length} 张未保存的图片`);
        }
      } catch (error) {
        console.error('清理图片失败:', error);
      }
    }
    
    setModalVisible(false);
    setEditingRecord(null);
    setActiveTabKey('basic');
    setProductImages([]);
    setOriginalImages([]); // 清空原始图片列表
    setDeletedImages([]); // 清空被删除的图片列表
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
      unit_id: '',
      unit_name: '',
      sort_order: productProcesses.length + 1,
      curing: false,
      roll_out_direction: '',
      weight_gain: null,
      total_gram_weight: null,
      weight_gain_upper_limit: null,
      weight_gain_lower_limit: null,
      lamination_width: null,
      lamination_thickness: null,
      lamination_density: null,
      process_requirements: '',
      piece_rate_unit_price: null,
      difficulty_level: '',
      surface_print: null,
      reverse_print: null,
      inkjet_code: null,
      solvent: null,
      adhesive_amount: null,
      solid_content: null,
      no_material_needed: false,
      mes_semi_finished_usage: false,
      mes_multi_process_semi_finished: false,
      min_hourly_output: null,
      standard_hourly_output: null,
      semi_finished_coefficient: null
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
            unit_id: selectedProcess.unit_id || '',
            unit_name: selectedProcess.unit_name || ''
          };
        }
      } else {
        // 清空选择
        updatedProcesses[index] = {
          ...updatedProcesses[index],
          process_id: '',
          process_name: '',
          process_category_name: '',
          unit_id: '',
          unit_name: ''
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
      process_id: '',
      process_name: '',
      sort_order: productMaterials.length + 1,
      layer_number: '',
      supplier_id: '',
      supplier_name: '',
      material_process: '',
      remarks: '',
      hot_stamping_film_length: null,
      hot_stamping_film_width: null,
      material_file_remarks: ''
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
    } else if (field === 'process_id') {
      const updatedMaterials = [...productMaterials];
      if (value) {
        // 查找选中的工序信息
        const selectedProcess = (formOptions.processes || []).find(p => p.value === value);
        if (selectedProcess) {
          updatedMaterials[index] = {
            ...updatedMaterials[index],
            process_id: value,
            process_name: selectedProcess.label
          };
        }
      } else {
        // 清空选择
        updatedMaterials[index] = {
          ...updatedMaterials[index],
          process_id: '',
          process_name: ''
        };
      }
      setProductMaterials(updatedMaterials);
    } else if (field === 'supplier_id') {
      const updatedMaterials = [...productMaterials];
      if (value) {
        // 查找选中的供应商信息
        const selectedSupplier = (formOptions.suppliers || []).find(s => s.value === value);
        if (selectedSupplier) {
          updatedMaterials[index] = {
            ...updatedMaterials[index],
            supplier_id: value,
            supplier_name: selectedSupplier.label
          };
        }
      } else {
        // 清空选择
        updatedMaterials[index] = {
          ...updatedMaterials[index],
          supplier_id: '',
          supplier_name: ''
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
      title: '产品类别',
      dataIndex: 'category_name',
      key: 'category_name',
      width: 120
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
            <Input style={{ width: '100%' }} placeholder="宽(cm)*厚度(丝)" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="category_id" label="产品类别">
            <Select placeholder="请选择产品类别">
              {(formOptions.product_categories || []).map(category => (
                <Option key={category.value} value={category.value}>
                  {category.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="film_structure" label="理膜结构">
            <Input placeholder="根据选择袋型自动输入" disabled />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_structures', 'density']} label="密度">
            <InputNumber min={0} step={0.01} addonAfter="g/cm³" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="inner" label="内">
            <TextArea rows={3} placeholder="请输入内" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="middle" label="中">
            <TextArea rows={3} placeholder="请输入中" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="outer" label="外">
            <TextArea rows={3} placeholder="请输入外" />
          </Form.Item>
        </Col>
      </Row>
      
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="bag_body" label="袋体">
            <Select placeholder="请选择袋体">
              <Option value="single">单体</Option>
              <Option value="composite">复合</Option>
            </Select>
          </Form.Item>
        </Col>
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
      </Row>

      <Row gutter={16}>
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
    </div>
  );

  // 新增价格和其他信息分页
  const renderPriceAndOtherInfo = () => (
    <div>
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
            <InputNumber min={0} step={0.01} addonAfter="cm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'width']} label="宽">
            <InputNumber min={0} step={0.01} addonAfter="cm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'side_width']} label="侧宽">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'bottom_width']} label="底宽">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'thickness']} label="厚度">
            <InputNumber min={0} step={0.01} addonAfter="丝" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'total_thickness']} label="总厚度">
            <InputNumber min={0} step={0.01} addonAfter="丝" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'volume']} label="体积">
            <InputNumber min={0} step={0.01} addonAfter="L" style={{ width: '100%' }} />
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
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'cut_width']} label="分切宽">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'cut_thickness']} label="分切厚度">
            <InputNumber min={0} step={0.01} addonAfter="丝" style={{ width: '100%' }} />
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
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'light_eye_width']} label="光标宽">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'light_eye_distance']} label="光标距离">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'edge_sealing_width']} label="封边宽度">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
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
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_width']} label="托盘宽">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_height']} label="托盘高">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_1']} label="托盘1">
            <InputNumber min={0} step={0.01} addonAfter="个" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_2']} label="托盘2">
            <InputNumber min={0} step={0.01} addonAfter="个" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'pallet_3']} label="托盘3">
            <InputNumber min={0} step={0.01} addonAfter="个" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'winding_diameter']} label="收卷直径">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      {/* 封口信息 */}
      <Divider orientation="left">封口信息</Divider>
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name={['product_structures', 'seal_top']} label="封口上">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'seal_left']} label="封口左">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'seal_right']} label="封口右">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={['product_structures', 'seal_middle']} label="封口中">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_structures', 'sealing_temperature']} label="封合温度">
            <InputNumber min={0} step={0.01} addonAfter="℃" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_structures', 'sealing_width']} label="封合宽度">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_structures', 'sealing_strength']} label="封合强度">
            <InputNumber min={0} step={0.01} addonAfter="N" style={{ width: '100%' }} />
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
            <InputNumber min={0} step={0.01} addonAfter="kW" style={{ width: '100%' }} />
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
          {productImages.map((image, index) => {
            
            return (
              <div key={image.uid} style={{ position: 'relative' }}>
                <Image
                  width={200}
                  height={150}
                  src={(() => {
                    let url = image.url || image.thumbUrl || image.response?.data?.url;

                    if (url) {
                      // 如果是相对路径，添加域名
                      if (url.startsWith('/')) {
                        url = `https://www.kylinking.com${url}`;
                      }
                      // 如果包含 /api/ 前缀，移除它
                      if (url.includes('/api/uploads/')) {
                        url = url.replace('/api/uploads/', '/uploads/');
                      }
                    }

                    return url;
                  })()}
                  placeholder="图片加载中..."
                  style={{ objectFit: 'cover', borderRadius: 8 }}
                  onError={(e) => {
                    console.error('图片加载失败:', image.url, e);
                  }}
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
                <Button
                  type="text"
                  icon={<DeleteOutlined />}
                  size="small"
                  style={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    background: 'rgba(255,0,0,0.8)',
                    color: 'white',
                    border: 'none',
                    borderRadius: 4,
                    width: 32,
                    height: 32,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  onClick={() => handleDeleteImage(image)}
                />
              </div>
            );
          })}
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
            {/* 单行显示，支持左右滑动 */}
            <div style={{ overflowX: 'auto', whiteSpace: 'nowrap' }}>
              <div style={{ display: 'inline-flex', gap: '8px', minWidth: 'max-content', padding: '8px 0' }}>
                                {/* 工序名称 */}
                <div style={{ minWidth: '150px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>工序名称:</span>
                  <Select
                    placeholder="请选择工序"
                    value={process.process_id}
                    onChange={(value) => handleProcessChange(index, 'process_id', value)}
                    showSearch
                    size="small"
                    style={{ width: '120px' }}
                    filterOption={(input, option) =>
                      option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                    }
                  >
                    {(formOptions.processes || [])
                      .filter(p => {
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
                </div>

                                {/* 工序分类 */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>工序分类:</span>
                  <Input
                    value={process.process_category_name || ''}
                    readOnly
                    size="small"
                    style={{ width: '80px' }}
                    placeholder="自动填入"
                  />
                </div>

                {/* 单位 */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>单位:</span>
                  <Input
                    value={process.unit_name || ''}
                    readOnly
                    size="small"
                    style={{ width: '80px' }}
                    placeholder="自动填入"
                  />
                </div>

                {/* 熟化 */}
                <div style={{ minWidth: '80px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>熟化:</span>
                  <Checkbox
                    checked={process.curing}
                    onChange={(e) => updateProcess(process.id, 'curing', e.target.checked)}
                    size="small"
                  />
                </div>

                {/* 出卷方向 */}
                <div style={{ minWidth: '140px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>出卷方向:</span>
                  <Select
                    placeholder="请选择"
                    value={process.roll_out_direction}
                    onChange={(value) => updateProcess(process.id, 'roll_out_direction', value)}
                    size="small"
                    style={{ width: '100px' }}
                  >
                    <Option value="头出">头出</Option>
                    <Option value="尾出">尾出</Option>
                    <Option value="任意统一">任意统一</Option>
                  </Select>
                </div>

                {/* 增重g/m² */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>增重g/m²:</span>
                  <InputNumber
                    value={process.weight_gain}
                    onChange={(value) => updateProcess(process.id, 'weight_gain', value)}
                    size="small"
                    style={{ width: '80px' }}
                    precision={2}
                  />
                </div>

                {/* 总克重 */}
                <div style={{ minWidth: '100px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>总克重:</span>
                  <InputNumber
                    value={process.total_gram_weight}
                    onChange={(value) => updateProcess(process.id, 'total_gram_weight', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 增重上限 */}
                <div style={{ minWidth: '100px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>增重上限:</span>
                  <InputNumber
                    value={process.weight_gain_upper_limit}
                    onChange={(value) => updateProcess(process.id, 'weight_gain_upper_limit', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 增重下限 */}
                <div style={{ minWidth: '100px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>增重下限:</span>
                  <InputNumber
                    value={process.weight_gain_lower_limit}
                    onChange={(value) => updateProcess(process.id, 'weight_gain_lower_limit', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 计件单价 */}
                <div style={{ minWidth: '100px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>计件单价:</span>
                  <InputNumber
                    value={process.piece_rate_unit_price}
                    onChange={(value) => updateProcess(process.id, 'piece_rate_unit_price', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 难易等级 */}
                <div style={{ minWidth: '100px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>难易等级:</span>
                  <Input
                    value={process.difficulty_level}
                    onChange={(e) => updateProcess(process.id, 'difficulty_level', e.target.value)}
                    size="small"
                    style={{ width: '60px' }}
                  />
                </div>

                {/* 淋膜宽mm */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>淋膜宽mm:</span>
                  <InputNumber
                    value={process.lamination_width}
                    onChange={(value) => updateProcess(process.id, 'lamination_width', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 淋膜厚µm */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>淋膜厚µm:</span>
                  <InputNumber
                    value={process.lamination_thickness}
                    onChange={(value) => updateProcess(process.id, 'lamination_thickness', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 淋膜密度 */}
                <div style={{ minWidth: '100px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>淋膜密度:</span>
                  <InputNumber
                    value={process.lamination_density}
                    onChange={(value) => updateProcess(process.id, 'lamination_density', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 表印g/m² */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>表印g/m²:</span>
                  <InputNumber
                    value={process.surface_print}
                    onChange={(value) => updateProcess(process.id, 'surface_print', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 里印g/m² */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>里印g/m²:</span>
                  <InputNumber
                    value={process.reverse_print}
                    onChange={(value) => updateProcess(process.id, 'reverse_print', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 喷码(万个/kg) */}
                <div style={{ minWidth: '140px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>喷码(万个/kg):</span>
                  <InputNumber
                    value={process.inkjet_code}
                    onChange={(value) => updateProcess(process.id, 'inkjet_code', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 溶剂g/m² */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>溶剂g/m²:</span>
                  <InputNumber
                    value={process.solvent}
                    onChange={(value) => updateProcess(process.id, 'solvent', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 上胶量g/m² */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>上胶量g/m²:</span>
                  <InputNumber
                    value={process.adhesive_amount}
                    onChange={(value) => updateProcess(process.id, 'adhesive_amount', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 固含量g/m² */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>固含量g/m²:</span>
                  <InputNumber
                    value={process.solid_content}
                    onChange={(value) => updateProcess(process.id, 'solid_content', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 最低产量 */}
                <div style={{ minWidth: '100px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>最低产量:</span>
                  <InputNumber
                    value={process.min_hourly_output}
                    onChange={(value) => updateProcess(process.id, 'min_hourly_output', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 标准产量 */}
                <div style={{ minWidth: '100px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>标准产量:</span>
                  <InputNumber
                    value={process.standard_hourly_output}
                    onChange={(value) => updateProcess(process.id, 'standard_hourly_output', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 半成品系数 */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>半成品系数:</span>
                  <InputNumber
                    value={process.semi_finished_coefficient}
                    onChange={(value) => updateProcess(process.id, 'semi_finished_coefficient', value)}
                    size="small"
                    style={{ width: '60px' }}
                    precision={2}
                  />
                </div>

                {/* 无需材料 */}
                <div style={{ minWidth: '100px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>无需材料:</span>
                  <Checkbox
                    checked={process.no_material_needed}
                    onChange={(e) => updateProcess(process.id, 'no_material_needed', e.target.checked)}
                    size="small"
                  />
                </div>

                {/* MES半成品用量 */}
                <div style={{ minWidth: '140px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>MES半成品用量:</span>
                  <Checkbox
                    checked={process.mes_semi_finished_usage}
                    onChange={(e) => updateProcess(process.id, 'mes_semi_finished_usage', e.target.checked)}
                    size="small"
                  />
                </div>

                {/* MES多工序半成品 */}
                <div style={{ minWidth: '160px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>MES多工序半成品:</span>
                  <Checkbox
                    checked={process.mes_multi_process_semi_finished}
                    onChange={(e) => updateProcess(process.id, 'mes_multi_process_semi_finished', e.target.checked)}
                    size="small"
                  />
                </div>

                                {/* 工艺要求 */}
                <div style={{ minWidth: '200px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>工艺要求:</span>
                  <Input
                    value={process.process_requirements}
                    onChange={(e) => updateProcess(process.id, 'process_requirements', e.target.value)}
                    size="small"
                    style={{ width: '150px' }}
                    placeholder="请输入工艺要求"
                  />
                </div>

                {/* 排序 */}
                <div style={{ minWidth: '80px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>排序:</span>
                  <InputNumber
                    min={0}
                    value={process.sort_order}
                    onChange={(value) => updateProcess(process.id, 'sort_order', value)}
                    size="small"
                    style={{ width: '50px' }}
                  />
                </div>

                {/* 删除按钮 */}
                <div style={{ minWidth: '60px', textAlign: 'center' }}>
                  <Button 
                    type="text" 
                    danger 
                    icon={<DeleteOutlined />} 
                    onClick={() => removeProcess(process.id)}
                    size="small"
                  />
                </div>
              </div>
            </div>
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
            {/* 单行显示，支持左右滑动 */}
            <div style={{ overflowX: 'auto', whiteSpace: 'nowrap' }}>
              <div style={{ display: 'inline-flex', gap: '8px', minWidth: 'max-content', padding: '8px 0' }}>
                {/* 材料编号 */}
                <div style={{ minWidth: '180px', maxWidth: '260px', display: 'inline-block', verticalAlign: 'middle' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>材料编号:</span>
                  <Input
                    value={material.material_code}
                    readOnly
                    size="small"
                    style={{ width: '140px', fontSize: 14 }}
                  />
                </div>

                {/* 材料名称 */}
                <div style={{ minWidth: '150px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>材料名称:</span>
                  <Select
                    placeholder="请选择材料"
                    value={material.material_id}
                    onChange={(value) => handleMaterialChange(index, 'material_id', value)}
                    showSearch
                    size="small"
                    style={{ width: '120px', fontSize: 14 }}
                    filterOption={(input, option) =>
                      option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                    }
                  >
                    {(formOptions.materials || [])
                      .filter(m => {
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
                </div>

                {/* 材料类别 */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>材料类别:</span>
                  <Input
                    value={material.material_category_name || ''}
                    readOnly
                    size="small"
                    style={{ width: '80px' }}
                    placeholder="自动填入"
                  />
                </div>

                {/* 材料属性 */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>材料属性:</span>
                  <Input
                    value={material.material_attribute || ''}
                    readOnly
                    size="small"
                    style={{ width: '80px' }}
                    placeholder="自动填入"
                  />
                </div>

                {/* 工序 */}
                <div style={{ minWidth: '150px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>工序:</span>
                  <Select
                    placeholder="请选择工序"
                    value={material.process_id}
                    onChange={(value) => handleMaterialChange(index, 'process_id', value)}
                    showSearch
                    size="small"
                    style={{ width: '120px' }}
                    filterOption={(input, option) =>
                      option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                    }
                  >
                    {productProcesses
                      .filter(process => process.process_id)
                      .map(process => {
                        const processOption = (formOptions.processes || []).find(p => p.value === process.process_id);
                        return processOption ? (
                          <Option key={process.process_id} value={process.process_id}>
                            {processOption.label}
                          </Option>
                        ) : null;
                      })
                      .filter(Boolean)}
                  </Select>
                </div>

                {/* 层数 */}
                <div style={{ minWidth: '100px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>层数:</span>
                  <Input
                    placeholder="请输入层数"
                    value={material.layer_number}
                    onChange={(e) => updateMaterial(material.id, 'layer_number', e.target.value)}
                    size="small"
                    style={{ width: '80px' }}
                  />
                </div>

                {/* 供应商 */}
                <div style={{ minWidth: '150px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>供应商:</span>
                  <Select
                    placeholder="请选择供应商"
                    value={material.supplier_id}
                    onChange={(value) => handleMaterialChange(index, 'supplier_id', value)}
                    size="small"
                    style={{ width: '120px' }}
                  >
                    {(formOptions.suppliers || []).map(supplier => (
                      <Option key={supplier.value} value={supplier.value}>
                        {supplier.label}
                      </Option>
                    ))}
                  </Select>
                </div>

                {/* 材质工艺 */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>材质工艺:</span>
                  <Input
                    value={material.material_process}
                    onChange={(e) => updateMaterial(material.id, 'material_process', e.target.value)}
                    size="small"
                    style={{ width: '80px' }}
                    placeholder="请输入材质工艺"
                  />
                </div>

                {/* 烫金膜长 */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>烫金膜长:</span>
                  <InputNumber
                    value={material.hot_stamping_film_length}
                    onChange={(value) => updateMaterial(material.id, 'hot_stamping_film_length', value)}
                    size="small"
                    style={{ width: '80px' }}
                    precision={2}
                  />
                </div>

                {/* 烫金膜宽 */}
                <div style={{ minWidth: '120px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>烫金膜宽:</span>
                  <InputNumber
                    value={material.hot_stamping_film_width}
                    onChange={(value) => updateMaterial(material.id, 'hot_stamping_film_width', value)}
                    size="small"
                    style={{ width: '80px' }}
                    precision={2}
                  />
                </div>

                {/* 备注 */}
                <div style={{ minWidth: '150px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>备注:</span>
                  <Input
                    value={material.remarks}
                    onChange={(e) => updateMaterial(material.id, 'remarks', e.target.value)}
                    size="small"
                    style={{ width: '120px' }}
                    placeholder="请输入备注"
                  />
                </div>

                {/* 材料档案备注 */}
                <div style={{ minWidth: '150px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>材料档案备注:</span>
                  <Input
                    value={material.material_file_remarks}
                    onChange={(e) => updateMaterial(material.id, 'material_file_remarks', e.target.value)}
                    size="small"
                    style={{ width: '120px' }}
                    placeholder="请输入档案备注"
                  />
                </div>

                {/* 排序 */}
                <div style={{ minWidth: '80px' }}>
                  <span style={{ fontSize: 14, color: '#333', marginRight: 4 }}>排序:</span>
                  <InputNumber
                    min={0}
                    value={material.sort_order}
                    onChange={(value) => updateMaterial(material.id, 'sort_order', value)}
                    size="small"
                    style={{ width: '50px' }}
                  />
                </div>

                {/* 删除按钮 */}
                <div style={{ minWidth: '60px', textAlign: 'center' }}>
                  <Button 
                    type="text" 
                    danger 
                    icon={<DeleteOutlined />} 
                    onClick={() => removeMaterial(material.id)}
                    size="small"
                  />
                </div>
              </div>
            </div>
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
  // 客户需求标签页
  const renderCustomerRequirements = () => (
    <div>
      {/* 外观要求 */}
      <Divider orientation="left">外观要求</Divider>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'appearance_requirements']} label="外观要求">
            <TextArea rows={3} placeholder="请输入外观要求" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'surface_treatment']} label="表面处理">
            <TextArea rows={3} placeholder="请输入表面处理要求" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'printing_requirements']} label="印刷要求">
            <TextArea rows={3} placeholder="请输入印刷要求" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'color_requirements']} label="颜色要求">
            <TextArea rows={3} placeholder="请输入颜色要求" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'pattern_requirements']} label="图案要求">
            <TextArea rows={3} placeholder="请输入图案要求" />
          </Form.Item>
        </Col>
      </Row>

      {/* 切割要求 */}
      <Divider orientation="left">切割要求</Divider>
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'cutting_method']} label="切割方式">
            <Select placeholder="请选择切割方式">
              <Option value="laser">激光切割</Option>
              <Option value="mechanical">机械切割</Option>
              <Option value="water_jet">水刀切割</Option>
              <Option value="other">其他</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'cutting_width']} label="切割宽度">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'cutting_length']} label="切割长度">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'cutting_thickness']} label="切割厚度">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'optical_distance']} label="光标距离">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'optical_width']} label="光标宽度">
            <InputNumber min={0} step={0.01} addonAfter="mm" style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      {/* 制袋要求 */}
      <Divider orientation="left">制袋要求</Divider>
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'bag_sealing_up']} label="上封">
            <Input placeholder="请输入上封要求" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'bag_sealing_down']} label="下封">
            <Input placeholder="请输入下封要求" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'bag_sealing_left']} label="左封">
            <Input placeholder="请输入左封要求" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'bag_sealing_right']} label="右封">
            <Input placeholder="请输入右封要求" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'bag_sealing_middle']} label="中封">
            <Input placeholder="请输入中封要求" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'bag_sealing_inner']} label="内封">
            <Input placeholder="请输入内封要求" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'bag_length_tolerance']} label="袋长公差">
            <Input placeholder="请输入袋长公差" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'bag_width_tolerance']} label="袋宽公差">
            <Input placeholder="请输入袋宽公差" />
          </Form.Item>
        </Col>
      </Row>

      {/* 包装要求 */}
      <Divider orientation="left">包装要求</Divider>
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'packaging_method']} label="包装方式">
            <Input placeholder="请输入包装方式" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'packaging_requirements']} label="包装要求">
            <Input placeholder="请输入包装要求" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'packaging_material']} label="包装材料">
            <Input placeholder="请输入包装材料" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'packaging_quantity']} label="包装数量">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'packaging_specifications']} label="包装规格">
            <Input placeholder="请输入包装规格" />
          </Form.Item>
        </Col>
      </Row>

      {/* 性能要求 */}
      <Divider orientation="left">性能要求</Divider>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'req_tensile_strength']} label="拉伸强度要求">
            <Input placeholder="请输入拉伸强度要求" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'thermal_shrinkage']} label="热收缩率">
            <Input placeholder="请输入热收缩率要求" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'impact_strength']} label="冲击强度">
            <Input placeholder="请输入冲击强度要求" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'thermal_tensile_strength']} label="热拉伸强度">
            <Input placeholder="请输入热拉伸强度要求" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'water_vapor_permeability']} label="水蒸气透过率">
            <Input placeholder="请输入水蒸气透过率要求" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'heat_shrinkage_curve']} label="热缩曲线">
            <Input placeholder="请输入热缩曲线要求" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'melt_index']} label="熔指">
            <Input placeholder="请输入熔指要求" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name={['product_customer_requirements', 'gas_permeability']} label="气体透过率">
            <Input placeholder="请输入气体透过率要求" />
          </Form.Item>
        </Col>
      </Row>

      {/* 自定义字段 */}
      <Divider orientation="left">自定义字段</Divider>
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'custom_1']} label="自定义1">
            <Input placeholder="请输入自定义字段1" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'custom_2']} label="自定义2">
            <Input placeholder="请输入自定义字段2" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'custom_3']} label="自定义3">
            <Input placeholder="请输入自定义字段3" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'custom_4']} label="自定义4">
            <Input placeholder="请输入自定义字段4" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'custom_5']} label="自定义5">
            <Input placeholder="请输入自定义字段5" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'custom_6']} label="自定义6">
            <Input placeholder="请输入自定义字段6" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_customer_requirements', 'custom_7']} label="自定义7">
            <Input placeholder="请输入自定义字段7" />
          </Form.Item>
        </Col>

      </Row>
    </div>
  );

  const renderQualityIndicators = () => (
    <div>
      {/* 理化指标 */}
      <Divider orientation="left">理化指标</Divider>
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'tensile_strength_longitudinal']} label="拉伸强度纵向">
            <Input placeholder="请输入拉伸强度纵向" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'tensile_strength_transverse']} label="拉伸强度横向">
            <Input placeholder="请输入拉伸强度横向" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'thermal_shrinkage_longitudinal']} label="热缩率纵向">
            <Input placeholder="请输入热缩率纵向" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'thermal_shrinkage_transverse']} label="热缩率横向">
            <Input placeholder="请输入热缩率横向" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'puncture_strength']} label="穿刺强度">
            <Input placeholder="请输入穿刺强度" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'optical_properties']} label="光学性能">
            <Input placeholder="请输入光学性能" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'heat_seal_temperature']} label="热封温度">
            <Input placeholder="请输入热封温度" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'heat_seal_tensile_strength']} label="热封拉伸强度">
            <Input placeholder="请输入热封拉伸强度" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'quality_water_vapor_permeability']} label="水蒸气透过率">
            <Input placeholder="请输入水蒸气透过率" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'oxygen_permeability']} label="氧气透过率">
            <Input placeholder="请输入氧气透过率" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'friction_coefficient']} label="摩擦系数">
            <Input placeholder="请输入摩擦系数" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'peel_strength']} label="剥离强度">
            <Input placeholder="请输入剥离强度" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name={['product_quality_indicators', 'test_standard']} label="检验标准">
            <Input placeholder="请输入检验标准" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name={['product_quality_indicators', 'test_basis']} label="检验依据">
            <Input placeholder="请输入检验依据" />
          </Form.Item>
        </Col>
      </Row>

      {/* 指标1-10 */}
      <Divider orientation="left">其他指标</Divider>
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'indicator_1']} label="指标1">
            <Input placeholder="请输入指标1" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'indicator_2']} label="指标2">
            <Input placeholder="请输入指标2" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'indicator_3']} label="指标3">
            <Input placeholder="请输入指标3" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'indicator_4']} label="指标4">
            <Input placeholder="请输入指标4" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'indicator_5']} label="指标5">
            <Input placeholder="请输入指标5" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'indicator_6']} label="指标6">
            <Input placeholder="请输入指标6" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'indicator_7']} label="指标7">
            <Input placeholder="请输入指标7" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'indicator_8']} label="指标8">
            <Input placeholder="请输入指标8" />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'indicator_9']} label="指标9">
            <Input placeholder="请输入指标9" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name={['product_quality_indicators', 'indicator_10']} label="指标10">
            <Input placeholder="请输入指标10" />
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
                key: 'customer_requirements',
                label: '客户需求',
                children: renderCustomerRequirements()
              },
              {
                key: 'price_and_other',
                label: '价格及其他',
                children: renderPriceAndOtherInfo()
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