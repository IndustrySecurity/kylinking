#!/usr/bin/env python3
import psycopg2
import uuid
import sys

def fix_tenants():
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='saas_platform',
            user='postgres',
            password='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("🔧 检查和修复租户数据...")
        
        # 检查tenants表中是否有数据
        cursor.execute("SELECT count(*) FROM public.tenants;")
        tenant_count_result = cursor.fetchone()
        tenant_count = tenant_count_result[0] if tenant_count_result else 0
        print(f"📋 当前租户数量: {tenant_count}")
        
        if tenant_count == 0:
            print("📋 创建万乐租户...")
            tenant_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO public.tenants (id, name, slug, schema_name, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (tenant_id, '万乐包装', 'wanle', 'wanle', True))
            print(f"✅ 租户创建成功: {tenant_id}")
        else:
            # 获取现有租户
            cursor.execute("SELECT id, name, slug FROM public.tenants LIMIT 1;")
            tenant = cursor.fetchone()
            if tenant:
                tenant_id = tenant[0]
                print(f"✅ 使用现有租户: {tenant[1]} ({tenant[2]})")
            else:
                raise Exception("无法获取租户信息")
        
        # 检查users表是否有tenant_id字段
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'tenant_id' AND table_schema = 'public';
        """)
        
        if not cursor.fetchone():
            print("📋 添加tenant_id字段到users表...")
            cursor.execute("ALTER TABLE public.users ADD COLUMN tenant_id UUID;")
            cursor.execute("ALTER TABLE public.users ADD FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);")
        
        # 将管理员用户关联到租户
        cursor.execute("""
            UPDATE public.users SET tenant_id = %s 
            WHERE email = 'admin@kylinking.com' OR username = 'admin';
        """, (tenant_id,))
        
        cursor.execute("SELECT count(*) FROM public.users WHERE tenant_id = %s;", (tenant_id,))
        associated_users_result = cursor.fetchone()
        associated_users = associated_users_result[0] if associated_users_result else 0
        print(f"✅ 已关联 {associated_users} 个用户到租户")
        
        conn.close()
        print("🎉 租户修复完成！")
        return True
        
    except Exception as e:
        print(f"❌ 租户修复失败: {e}")
        return False

if __name__ == "__main__":
    success = fix_tenants()
    sys.exit(0 if success else 1) 