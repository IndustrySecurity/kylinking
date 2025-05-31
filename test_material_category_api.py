#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试材料分类API
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:5000"
TENANT_ID = "wanle"

def test_material_category_api():
    """测试材料分类API"""
    print("=== 测试材料分类API ===")
    
    # 1. 测试获取选项数据
    print("\n1. 测试获取选项数据:")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tenant/basic-data/material-categories/options",
            headers={"X-Tenant-ID": TENANT_ID}
        )
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"  错误: {response.text}")
    except Exception as e:
        print(f"  异常: {e}")
    
    # 2. 测试获取材料分类列表
    print("\n2. 测试获取材料分类列表:")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tenant/basic-data/material-categories",
            headers={"X-Tenant-ID": TENANT_ID},
            params={"page": 1, "per_page": 10}
        )
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  总数: {data.get('data', {}).get('total', 0)}")
            categories = data.get('data', {}).get('material_categories', [])
            print(f"  返回数量: {len(categories)}")
            if categories:
                print(f"  第一个分类: {categories[0].get('material_name', 'N/A')}")
        else:
            print(f"  错误: {response.text}")
    except Exception as e:
        print(f"  异常: {e}")

if __name__ == "__main__":
    test_material_category_api() 