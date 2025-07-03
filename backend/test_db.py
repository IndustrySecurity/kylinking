#!/usr/bin/env python3
import psycopg2
import sys

# 测试数据库连接
def test_db_connection():
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='saas_platform', 
            user='postgres',
            password='postgres'
        )
        
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        if version:
            print(f"✅ 数据库连接成功: {version[0][:50]}...")
        
        # 检查关键表
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('users', 'tenants');")
        tables = cursor.fetchall()
        print(f"✅ 找到表: {[t[0] for t in tables]}")
        
        # 检查用户数据
        cursor.execute("SELECT count(*) FROM public.users;")
        user_count_result = cursor.fetchone()
        if user_count_result:
            print(f"✅ 用户数量: {user_count_result[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1) 