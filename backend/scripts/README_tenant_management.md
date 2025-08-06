# 租户数据库管理工具

随着租户数量增加，手动管理每个schema变得越来越麻烦。本工具提供了自动化的租户数据库管理功能。

## 工具概览

### 1. 租户管理脚本 (`tenant_management.py`)
用于创建新租户、管理现有租户的数据库结构。

### 2. 批量更新脚本 (`batch_schema_update.py`)
用于对所有租户schema执行相同的数据库结构更新。

## 使用方法

### 创建新租户

```bash
# 进入后端目录
cd backend

# 创建新租户（使用yiboshuo作为模板）
python scripts/tenant_management.py create --tenant shuangxi

# 使用其他schema作为模板
python scripts/tenant_management.py create --tenant new_tenant --template wanle
```

### 查看所有租户

```bash
# 列出所有租户schema
python scripts/tenant_management.py list
```

### 批量更新所有租户

```bash
# 1. 首先预览要执行的SQL
python scripts/batch_schema_update.py preview --sql-file update_script.sql

# 2. 试运行（不实际执行）
python scripts/batch_schema_update.py update --sql-file update_script.sql --dry-run

# 3. 实际执行批量更新
python scripts/batch_schema_update.py update --sql-file update_script.sql

# 4. 查看所有租户schema
python scripts/batch_schema_update.py list
```

### 排除特定schema

```bash
# 排除public和test schema
python scripts/batch_schema_update.py update --sql-file update_script.sql --exclude public test
```

## 实际使用场景

### 场景1：新建租户
```bash
# 创建新租户"shuangxi"
python scripts/tenant_management.py create --tenant shuangxi
```

### 场景2：添加新字段到所有租户
```sql
-- 创建 update_add_new_column.sql
ALTER TABLE bag_types ADD COLUMN IF NOT EXISTS spec_expression TEXT;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employee_code VARCHAR(50);
```

```bash
# 批量更新所有租户
python scripts/batch_schema_update.py update --sql-file update_add_new_column.sql
```

### 场景3：修改表结构
```sql
-- 创建 update_table_structure.sql
ALTER TABLE customers RENAME TO customer_management;
ALTER TABLE suppliers RENAME TO supplier_management;
```

```bash
# 批量更新所有租户
python scripts/batch_schema_update.py update --sql-file update_table_structure.sql
```

### 场景4：添加索引
```sql
-- 创建 add_indexes.sql
CREATE INDEX IF NOT EXISTS idx_bag_types_name ON bag_types(bag_type_name);
CREATE INDEX IF NOT EXISTS idx_employees_code ON employees(employee_code);
```

```bash
# 批量更新所有租户
python scripts/batch_schema_update.py update --sql-file add_indexes.sql
```

## 最佳实践

### 1. 总是先预览和试运行
```bash
# 预览SQL内容
python scripts/batch_schema_update.py preview --sql-file your_update.sql

# 试运行
python scripts/batch_schema_update.py update --sql-file your_update.sql --dry-run
```

### 2. 备份重要数据
在执行批量更新前，建议备份重要的租户数据：
```bash
# 备份特定租户
docker exec saas_postgres_dev pg_dump -U postgres -d saas_platform -n yiboshuo > backup_yiboshuo.sql
```

### 3. 分步骤执行复杂更新
对于复杂的数据库变更，建议分步骤执行：
```bash
# 步骤1：添加新列
python scripts/batch_schema_update.py update --sql-file step1_add_columns.sql

# 步骤2：更新数据
python scripts/batch_schema_update.py update --sql-file step2_update_data.sql

# 步骤3：添加约束
python scripts/batch_schema_update.py update --sql-file step3_add_constraints.sql
```

### 4. 监控更新进度
脚本会显示详细的进度信息：
```
2024-01-01 10:00:00 - INFO - 找到 5 个租户schema: yiboshuo, wanle, shuangxi, test1, test2
2024-01-01 10:00:01 - INFO - Schema yiboshuo 更新成功
2024-01-01 10:00:02 - INFO - Schema wanle 更新成功
...
2024-01-01 10:00:05 - INFO - 批量更新完成: 成功: 5/5
```

## 错误处理

### 常见错误及解决方案

1. **连接数据库失败**
   - 检查数据库服务是否运行
   - 验证数据库连接配置

2. **权限不足**
   - 确保数据库用户有创建schema的权限
   - 检查是否有修改表的权限

3. **SQL语法错误**
   - 使用preview功能检查SQL语法
   - 在单个schema上测试SQL

4. **外键约束冲突**
   - 检查更新顺序，先更新被引用的表
   - 临时禁用外键约束

## 高级功能

### 自定义排除schema
```bash
# 排除多个系统schema
python scripts/batch_schema_update.py update --sql-file update.sql --exclude public information_schema pg_catalog
```

### 在Docker环境中使用
```bash
# 在Docker容器中执行
docker exec -it saas_backend_dev python scripts/tenant_management.py create --tenant new_tenant

docker exec -it saas_backend_dev python scripts/batch_schema_update.py update --sql-file /tmp/update.sql
```

## 注意事项

1. **数据安全**: 批量更新会影响所有租户，请谨慎操作
2. **备份**: 重要操作前请备份数据
3. **测试**: 建议在测试环境先验证SQL语句
4. **监控**: 关注更新过程中的错误信息
5. **回滚**: 准备回滚方案，以防更新失败

## 故障排除

如果遇到问题，可以：

1. 检查日志输出
2. 在单个schema上测试SQL
3. 使用`--dry-run`模式预览操作
4. 检查数据库连接和权限
5. 查看具体的错误信息

通过这些工具，你可以大大简化多租户数据库的管理工作，提高运维效率。 