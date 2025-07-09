# -*- coding: utf-8 -*-
"""
CalculationScheme 服务
"""

from app.services.base_service import TenantAwareService
from app.extensions import db
from app.models.basic_data import CalculationScheme
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class CalculationSchemeService(TenantAwareService):
    """计算方案服务"""
    
    # 类级别的参数缓存，避免频繁查询数据库
    _parameter_cache = None
    _cache_timestamp = None
    _cache_timeout = 300  # 5分钟缓存时间

    def _get_cached_parameters(self):
        """获取缓存的参数列表"""
        import time
        current_time = time.time()
        
        # 检查缓存是否过期
        if (self._parameter_cache is None or 
            self._cache_timestamp is None or 
            current_time - self._cache_timestamp > self._cache_timeout):
            
            try:
                from app.models.basic_data import CalculationParameter
                existing_params = self.session.query(CalculationParameter.parameter_name).filter(
                    CalculationParameter.is_enabled == True
                ).all()
                self._parameter_cache = [p[0] for p in existing_params]
                self._cache_timestamp = current_time
            except Exception:
                # 如果查询失败，返回空列表，但不更新缓存时间，下次会重试
                return []
        
        return self._parameter_cache or []
    
    def _clear_parameter_cache(self):
        """清除参数缓存（在参数更新时调用）"""
        self._parameter_cache = None
        self._cache_timestamp = None

    def get_calculation_schemes(self, page=1, per_page=20, search=None, category=None):
        """获取计算方案列表"""
        query = self.session.query(CalculationScheme)
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                CalculationScheme.scheme_name.ilike(search_pattern),
                CalculationScheme.description.ilike(search_pattern)
            ))
        
        # 分类筛选
        if category:
            query = query.filter(CalculationScheme.scheme_category == category)
        
        # 只查询启用的记录
        query = query.filter(CalculationScheme.is_enabled == True)
        
        # 排序
        query = query.order_by(CalculationScheme.sort_order, CalculationScheme.created_at.desc())
        
        # 分页
        total = query.count()
        schemes = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'schemes': [scheme.to_dict() for scheme in schemes],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def get_calculation_scheme(self, scheme_id):
        """获取计算方案详情"""
        scheme = self.session.query(CalculationScheme).get(uuid.UUID(scheme_id))
        if not scheme:
            raise ValueError("计算方案不存在")
        return scheme.to_dict()
    
    def create_calculation_scheme(self, data, created_by):
        """创建计算方案"""
        try:
            # 验证公式
            if data.get('scheme_formula'):
                validation_result = self.validate_formula(data['scheme_formula'])
                if not validation_result['is_valid']:
                    raise ValueError(f"公式验证失败: {validation_result['error']}")
            
            # 创建计算方案对象
            scheme = self.create_with_tenant(CalculationScheme,
                scheme_name=data['scheme_name'],
                scheme_category=data['scheme_category'],
                scheme_formula=data.get('scheme_formula', ''),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.commit()
            return scheme.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            if 'scheme_name' in str(e):
                raise ValueError("方案名称已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建计算方案失败: {str(e)}")
    
    def update_calculation_scheme(self, scheme_id, data, updated_by):
        """更新计算方案"""
        try:
            scheme = self.session.query(CalculationScheme).get(uuid.UUID(scheme_id))
            if not scheme:
                raise ValueError("计算方案不存在")
            
            # 验证公式
            if 'scheme_formula' in data and data['scheme_formula']:
                validation_result = self.validate_formula(data['scheme_formula'])
                if not validation_result['is_valid']:
                    raise ValueError(f"公式验证失败: {validation_result['error']}")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(scheme, key):
                    setattr(scheme, key, value)
            
            scheme.updated_by = uuid.UUID(updated_by)
            
            try:
                self.commit()
                return scheme.to_dict()
            except Exception as e:
                self.rollback()
                raise ValueError(f'更新计算方案失败: {str(e)}')
            
        except IntegrityError as e:
            self.rollback()
            if 'scheme_name' in str(e):
                raise ValueError("方案名称已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新计算方案失败: {str(e)}")
    
    def delete_calculation_scheme(self, scheme_id):
        """删除计算方案"""
        try:
            scheme = self.session.query(CalculationScheme).get(uuid.UUID(scheme_id))
            if not scheme:
                raise ValueError("计算方案不存在")
            
            self.session.delete(scheme)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除计算方案失败: {str(e)}")
    
    def get_scheme_categories(self):
        """获取方案分类选项"""
        try:
            return CalculationScheme.get_scheme_categories()
        except Exception as e:
            raise ValueError(f"获取方案分类失败: {str(e)}")
    
    def validate_formula(self, formula):
        """验证公式语法"""
        try:
            if not formula or not formula.strip():
                return {'is_valid': True, 'error': None, 'warnings': []}
            
            # 统计信息
            param_count = len(re.findall(r'\[([^\]]+)\]', formula))
            string_count = len(re.findall(r"'([^']*)'", formula))
            line_count = formula.count('\n') + 1
            
            errors = []
            warnings = []
            
            # 1. 检查括号匹配
            round_brackets = formula.count('(') - formula.count(')')
            square_brackets = formula.count('[') - formula.count(']')
            single_quotes = formula.count("'")
            
            if round_brackets != 0:
                errors.append(f"圆括号不匹配，多了 {abs(round_brackets)} 个{'左' if round_brackets > 0 else '右'}括号")
            
            if square_brackets != 0:
                errors.append(f"方括号不匹配，多了 {abs(square_brackets)} 个{'左' if square_brackets > 0 else '右'}括号")
            
            if single_quotes % 2 != 0:
                errors.append("单引号不匹配，必须成对出现")
            
            # 2. 检查参数引用格式
            params = re.findall(r'\[([^\]]+)\]', formula)
            for param in params:
                if not param.strip():
                    errors.append("发现空的参数引用: []")
                elif not re.match(r'^[a-zA-Z\u4e00-\u9fa5][a-zA-Z0-9\u4e00-\u9fa5_]*$', param.strip()):
                    warnings.append(f"参数名称格式建议优化: [{param}]")
            
            # 3. 检查字符串格式
            strings = re.findall(r"'([^']*)'", formula)
            for string in strings:
                if not string.strip():
                    warnings.append("发现空字符串: ''")
            
            # 4. 改进的运算符检查
            # 先移除字符串和参数，再检查剩余部分
            temp_formula = formula
            # 移除字符串内容
            temp_formula = re.sub(r"'[^']*'", "STRING", temp_formula)
            # 移除参数内容
            temp_formula = re.sub(r"\[[^\]]+\]", "PARAM", temp_formula)
            
            # 检查是否包含无效字符（更精确的检查）
            # 允许的字符：数字、字母、中文、空格、标点符号、运算符
            valid_pattern = r'^[a-zA-Z0-9\u4e00-\u9fa5\s\(\).,><=+\-*/#%STRINGPARAM]*$'
            if not re.match(valid_pattern, temp_formula):
                # 找出具体的无效字符
                invalid_chars = re.findall(r'[^a-zA-Z0-9\u4e00-\u9fa5\s\(\).,><=+\-*/#%STRINGPARAM]', temp_formula)
                if invalid_chars:
                    unique_chars = list(set(invalid_chars))
                    warnings.append(f"发现特殊字符，请确认是否正确: {', '.join(unique_chars)}")
            
            # 5. 检查基本语法结构
            if '如果' in formula:
                if_count = formula.count('如果')
                then_count = formula.count('那么')
                end_count = formula.count('结束')
                
                if if_count != then_count:
                    errors.append(f"'如果'和'那么'数量不匹配: 如果({if_count}) vs 那么({then_count})")
                
                if if_count != end_count:
                    errors.append(f"'如果'和'结束'数量不匹配: 如果({if_count}) vs 结束({end_count})")
            
            # 6. 改进的数字格式检查
            # 更精确的数字匹配，支持整数、小数、科学记数法
            number_pattern = r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b'
            numbers = re.findall(number_pattern, formula)
            for num in numbers:
                try:
                    float(num)
                except ValueError:
                    errors.append(f"数字格式错误: {num}")
            
            # 7. 参数存在性检查（检查参数是否在系统中定义）
            try:
                # 使用缓存的参数列表
                existing_param_names = self._get_cached_parameters()
                
                for param in params:
                    param_name = param.strip()
                    # 检查精确匹配
                    if param_name not in existing_param_names:
                        # 检查大小写不一致的情况
                        similar_params = [p for p in existing_param_names if p.lower() == param_name.lower()]
                        if similar_params:
                            warnings.append(f"参数 '[{param_name}]' 大小写可能不正确，系统中存在: {similar_params}")
                        else:
                            errors.append(f"参数 '[{param_name}]' 在系统中不存在或未启用")
            except Exception as db_error:
                warnings.append(f"无法验证参数存在性: {str(db_error)}")
            
            # 8. 格式建议
            if formula and not re.search(r'\s', formula):
                warnings.append("建议在运算符前后添加空格以提高可读性")
            
            # 9. 检查连续运算符
            consecutive_operators = re.findall(r'[+\-*/>=<]{2,}', formula)
            if consecutive_operators:
                errors.append(f"发现连续的运算符: {', '.join(set(consecutive_operators))}")
            
            # 10. 检查运算符前后的空格（仅警告）
            operators_without_space = re.findall(r'\S[+\-*/>=<]\S', formula)
            if operators_without_space:
                warnings.append("建议在运算符前后添加空格以提高可读性")
            
            is_valid = len(errors) == 0
            
            result = {
                'is_valid': is_valid,
                'error': '; '.join(errors) if errors else None,
                'warnings': warnings,
                'statistics': {
                    'param_count': param_count,
                    'string_count': string_count,
                    'line_count': line_count,
                    'char_count': len(formula)
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': f"验证过程出错: {str(e)}",
                'warnings': [],
                'statistics': {
                    'param_count': 0,
                    'string_count': 0,
                    'line_count': 0,
                    'char_count': 0
                }
            }
    
    def get_calculation_scheme_options(self):
        """获取计算方案选项"""
        try:
            from app.models.basic_data import CalculationScheme
            
            # 使用ORM查询，自动应用租户上下文
            schemes = self.session.query(CalculationScheme).filter_by(is_enabled=True).order_by(
                CalculationScheme.sort_order, 
                CalculationScheme.scheme_name
            ).all()
            
            return [
                {
                    'value': str(scheme.id),
                    'label': scheme.scheme_name,
                    'category': scheme.scheme_category,
                    'description': scheme.description or '',
                    'formula': scheme.scheme_formula or ''
                }
                for scheme in schemes
            ]
        except Exception as e:
            raise ValueError(f"获取计算方案选项失败: {str(e)}")

    def get_calculation_schemes_by_category(self, category):
        """根据分类获取计算方案列表"""
        try:
            from app.models.basic_data import CalculationScheme
            
            # 使用ORM查询，自动应用租户上下文
            schemes = self.session.query(CalculationScheme).filter_by(
                scheme_category=category,
                is_enabled=True
            ).order_by(
                CalculationScheme.sort_order, 
                CalculationScheme.scheme_name
            ).all()
            
            return [
                {
                    'value': str(scheme.id),
                    'label': scheme.scheme_name,
                    'category': scheme.scheme_category,
                    'description': scheme.description or '',
                    'formula': scheme.scheme_formula or ''
                }
                for scheme in schemes
            ]
        except Exception as e:
            raise ValueError(f"获取{category}分类计算方案失败: {str(e)}")

    def get_calculation_scheme_options_by_category(self, request_category):
        """获取按类别分组的计算方案选项"""
        try:
            from app.models.basic_data import CalculationScheme
            
            # 使用ORM查询，自动应用租户上下文
            schemes = self.session.query(CalculationScheme).filter_by(is_enabled=True).order_by(
                CalculationScheme.sort_order, 
                CalculationScheme.scheme_name
            ).all()
                    
            # 按类别分组 - 支持工序相关分类
            categories = {
                'bag_spec': [],
                'bag_formula': [],
                'bag_quote': [],
                'material_usage': [],
                'material_quote': [],
                'process_quote': [],
                'process_loss': [],
                'process_bonus': [],
                'process_piece': [],
                'process_other': [],
                'multiple_formula': []
            }
            
            for scheme in schemes:
                # 转换为选项格式
                option = {
                    'value': str(scheme.id),
                    'label': scheme.scheme_name,
                    'category': scheme.scheme_category,
                    'formula': scheme.scheme_formula or '',
                    'description': scheme.description or ''
                }
                
                # 根据计算方案分类添加到对应类别
                category = scheme.scheme_category.lower() if scheme.scheme_category else ''
                if category in categories:
                    categories[category].append(option)
                else:
                    categories[category] = [option]
                    
            if request_category:
                return categories[request_category]
            else:
                return categories
            
        except Exception as e:
            raise ValueError(f"获取分类计算方案选项失败: {str(e)}")


# ==================== 工厂函数 ====================

def get_calculation_scheme_service(tenant_id: str = None, schema_name: str = None) -> CalculationSchemeService:
    """
    获取计算方案服务实例
    
    Args:
        tenant_id: 租户ID（可选）
        schema_name: Schema名称（可选）
    
    Returns:
        CalculationSchemeService: 计算方案服务实例
    """
    return CalculationSchemeService(tenant_id=tenant_id, schema_name=schema_name)


