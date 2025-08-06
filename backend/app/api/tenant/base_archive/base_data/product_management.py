"""
产品管理API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

from app.api.tenant.routes import tenant_required
from app.services.base_archive.base_data.product_management_service import get_product_management_service

# 创建蓝图
product_management_bp = Blueprint('product_management', __name__)

# 设置别名以便注册路由时使用
bp = product_management_bp

# 配置上传目录
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_tenant_upload_folder(tenant_id):
    """获取租户特定的上传目录"""
    return f'uploads/products/{tenant_id}'

def ensure_upload_dir(tenant_id):
    """确保租户上传目录存在"""
    upload_folder = get_tenant_upload_folder(tenant_id)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

@bp.route('/upload-image', methods=['POST'])
@jwt_required()
@tenant_required
def upload_image():
    """上传产品图片"""
    try:
        # 获取当前租户ID
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return jsonify({
                'success': False,
                'message': '租户ID缺失'
            }), 400
        
        # 确保租户上传目录存在
        upload_folder = ensure_upload_dir(tenant_id)
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
            
        if file and allowed_file(file.filename):
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            # 添加时间戳和UUID避免文件名冲突
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            file_extension = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{timestamp}_{unique_id}.{file_extension}"
            
            # 保存文件到租户特定目录
            file_path = os.path.join(upload_folder, new_filename)
            print(f"准备保存文件到: {file_path}")
            print(f"当前工作目录: {os.getcwd()}")
            print(f"租户上传目录: {upload_folder}")
            file.save(file_path)
            print(f"文件保存成功: {file_path}")
            print(f"文件是否存在: {os.path.exists(file_path)}")
            print(f"文件大小: {os.path.getsize(file_path)}")
            
            # 返回文件URL - 使用租户特定的路径
            file_url = f"/uploads/products/{tenant_id}/{new_filename}"
            
            return jsonify({
                'success': True,
                'data': {
                    'url': file_url,
                    'filename': new_filename,
                    'original_name': filename,
                    'size': os.path.getsize(file_path)
                },
                'message': '图片上传成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '不支持的文件格式，只支持 PNG, JPG, JPEG, GIF'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'图片上传失败: {str(e)}'
        }), 500

@bp.route('/delete-image', methods=['POST'])
@jwt_required()
@tenant_required
def delete_image():
    """删除产品图片"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        print(f"删除图片请求 - 文件名: {filename}")
        
        if not filename:
            return jsonify({
                'success': False,
                'message': '缺少文件名参数'
            }), 400
        
        # 获取当前租户ID
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return jsonify({
                'success': False,
                'message': '租户ID缺失'
            }), 400
        
        # 构建租户特定的文件路径
        upload_folder = get_tenant_upload_folder(tenant_id)
        file_path = os.path.join(upload_folder, filename)
        print(f"文件路径: {file_path}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"租户上传目录: {upload_folder}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404
        
        print(f"文件存在，准备删除: {file_path}")
        
        # 删除文件
        os.remove(file_path)
        
        print(f"文件删除成功: {file_path}")
        
        return jsonify({
            'success': True,
            'message': '图片删除成功'
        })
        
    except Exception as e:
        print(f"删除图片异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'图片删除失败: {str(e)}'
        }), 500

@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_products():
    """获取产品列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        customer_id = request.args.get('customer_id')
        bag_type_id = request.args.get('bag_type_id')
        status = request.args.get('status')
        
        # 调用服务层
        service = get_product_management_service()
        result = service.get_products(
            page=page,
            per_page=per_page,
            search=search,
            customer_id=customer_id,
            bag_type_id=bag_type_id,
            status=status
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<product_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_product(product_id):
    """获取产品详情"""
    try:
        service = get_product_management_service()
        product = service.get_product_detail(product_id)
        
        return jsonify({
            'success': True,
            'data': product
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_product():
    """创建产品"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
            
        service = get_product_management_service()
        result = service.create_product(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '产品创建成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_product(product_id):
    """更新产品"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
            
        service = get_product_management_service()
        result = service.update_product(product_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '产品更新成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_product(product_id):
    """删除产品"""
    try:
        service = get_product_management_service()
        result = service.delete_product(product_id)
        
        if not result:
            return jsonify({
                'success': False,
                'message': '产品不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'message': '产品删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/form-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_form_options():
    """获取产品表单选项"""
    try:
        service = get_product_management_service()
        options = service.get_form_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 

@bp.route('/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_options():
    """获取产品选项"""
    try:
        service = get_product_management_service()
        
        # 获取产品列表
        products = service.get_products(page=1, per_page=1000)  # 获取所有产品
        
        # 转换为选项格式
        options = []
        if products and 'products' in products:
            for product in products['products']:
                options.append({
                    'value': str(product['id']),
                    'label': product['product_name'],
                    'code': product.get('product_code', ''),
                    'specification': product.get('specification', ''),
                    'unit_id': str(product.get('unit_id')) if product.get('unit_id') else None,
                    'unit_name': product.get('unit_name', ''),
                    'price': product.get('price', 0),
                    'bag_type': product.get('bag_type', ''),
                    'material': product.get('material', ''),
                    'color': product.get('color', ''),
                    'width': product.get('width', 0),
                    'length': product.get('length', 0),
                    'thickness': product.get('thickness', 0)
                })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<product_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_details(product_id):
    """获取产品详细信息"""
    try:
        service = get_product_management_service()
        
        # 获取产品详情
        product = service.get_product_detail(product_id)
        
        if not product:
            return jsonify({'error': '产品不存在'}), 404
        
        # 转换为前端需要的格式
        product_details = {
            'id': str(product['id']),
            'product_code': product.get('product_code', ''),
            'product_name': product['product_name'],
            'specification': product.get('specification', ''),
            'unit_id': product.get('unit_id', ''),
            'price': product.get('price', 0),
            'bag_type': product.get('bag_type', ''),
            'material': product.get('material', ''),
            'color': product.get('color', ''),
            'width': product.get('width', 0),
            'length': product.get('length', 0),
            'thickness': product.get('thickness', 0),
            'customer_id': product.get('customer_id'),
            'customer_name': product.get('customer_name', ''),
            'category_id': product.get('category_id'),
            'category_name': product.get('category_name', '')
        }
        
        return jsonify({
            'success': True,
            'data': product_details
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

