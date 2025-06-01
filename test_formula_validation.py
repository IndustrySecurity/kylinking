#!/usr/bin/env python3
"""
计算方案公式验证逻辑测试脚本
用于验证修复后的公式验证逻辑是否正常工作
"""

import re
import sys
import os

# 添加backend目录到路径，以便导入模块
sys.path.append('backend')

def simulate_validate_formula(formula):
    """模拟公式验证逻辑（简化版，不依赖数据库）"""
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
        temp_formula = formula
        # 移除字符串内容
        temp_formula = re.sub(r"'[^']*'", "STRING", temp_formula)
        # 移除参数内容
        temp_formula = re.sub(r"\[[^\]]+\]", "PARAM", temp_formula)
        
        # 检查是否包含无效字符（更精确的检查）
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
        number_pattern = r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b'
        numbers = re.findall(number_pattern, formula)
        for num in numbers:
            try:
                float(num)
            except ValueError:
                errors.append(f"数字格式错误: {num}")
        
        # 7. 检查连续运算符
        consecutive_operators = re.findall(r'[+\-*/>=<]{2,}', formula)
        if consecutive_operators:
            errors.append(f"发现连续的运算符: {', '.join(set(consecutive_operators))}")
        
        # 8. 检查运算符前后的空格（仅警告）
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

def test_formulas():
    """测试各种公式场景"""
    test_cases = [
        # 正确的公式
        {
            'name': '基本算术运算',
            'formula': '[长度] * [宽度] * [厚度]',
            'expected': True
        },
        {
            'name': '条件判断',
            'formula': "如果 [长度] > 100 那么 [长度] * [宽度] * 1.2 否则 [长度] * [宽度] 结束",
            'expected': True
        },
        {
            'name': '字符串比较',
            'formula': "如果 [材料类型] = '塑料' 那么 [基础价格] * 1.1 否则 [基础价格] 结束",
            'expected': True
        },
        {
            'name': '科学记数法数字',
            'formula': '[基数] * 1.5e-3 + [系数]',
            'expected': True
        },
        {
            'name': '小数点开头的数字',
            'formula': '[长度] * .5 + [宽度]',
            'expected': True
        },
        
        # 错误的公式
        {
            'name': '括号不匹配',
            'formula': '([长度] + [宽度] * [厚度]',
            'expected': False
        },
        {
            'name': '方括号不匹配',
            'formula': '[长度 + [宽度] * [厚度]',
            'expected': False
        },
        {
            'name': '单引号不匹配',
            'formula': "如果 [材料类型] = '塑料 那么 [价格] * 1.1 结束",
            'expected': False
        },
        {
            'name': '如果结束不匹配',
            'formula': '如果 [长度] > 100 那么 [长度] * [宽度]',
            'expected': False
        },
        {
            'name': '连续运算符',
            'formula': '[长度] ++ [宽度]',
            'expected': False
        },
        {
            'name': '空参数引用',
            'formula': '[] + [宽度]',
            'expected': False
        },
        
        # 警告但不是错误的公式
        {
            'name': '没有空格的运算符',
            'formula': '[长度]*[宽度]+[厚度]',
            'expected': True  # 应该通过验证但有警告
        }
    ]
    
    print("=" * 80)
    print("计算方案公式验证逻辑测试")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"公式: {test_case['formula']}")
        
        result = simulate_validate_formula(test_case['formula'])
        actual_valid = result['is_valid']
        expected_valid = test_case['expected']
        
        if actual_valid == expected_valid:
            print(f"✅ 通过 - 验证结果: {'有效' if actual_valid else '无效'}")
            passed += 1
        else:
            print(f"❌ 失败 - 期望: {'有效' if expected_valid else '无效'}, 实际: {'有效' if actual_valid else '无效'}")
            failed += 1
        
        if result['error']:
            print(f"   错误: {result['error']}")
        
        if result['warnings']:
            print(f"   警告: {'; '.join(result['warnings'])}")
        
        stats = result['statistics']
        print(f"   统计: 参数{stats['param_count']}个, 字符串{stats['string_count']}个, 行数{stats['line_count']}, 字符数{stats['char_count']}")
    
    print("\n" + "=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败, 总计 {passed + failed}")
    print("=" * 80)
    
    return failed == 0

if __name__ == '__main__':
    success = test_formulas()
    sys.exit(0 if success else 1) 