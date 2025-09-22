

import pandas as pd
import pyodbc
import sqlite3
from typing import List, Dict, Any
from datetime import datetime

import time
# TABLES_TO_MIGRATE = None  # 设为 None 表示迁移全部表


def map_mssql_to_sqlite_type(mssql_type: str) -> str:
    mssql_type = mssql_type.upper()
    if 'INT' in mssql_type:
        if 'IDENTITY' in mssql_type or 'AUTO_INCREMENT' in mssql_type:
            return 'INTEGER PRIMARY KEY AUTOINCREMENT'  # SQLite 自增主键
        else:
            return 'INTEGER'
    elif 'VARCHAR' in mssql_type or 'NVARCHAR' in mssql_type or 'TEXT' in mssql_type or 'CHAR' in mssql_type:
        return 'TEXT'
    elif 'DATETIME' in mssql_type or 'DATE' in mssql_type or 'TIME' in mssql_type:
        return 'TEXT'  # SQLite 没有专门的日期类型，通常存为 ISO8601 字符串
    elif 'DECIMAL' in mssql_type or 'NUMERIC' in mssql_type or 'FLOAT' in mssql_type or 'REAL' in mssql_type:
        return 'REAL'
    elif 'BIT' in mssql_type:
        return 'INTEGER'  # SQLite 没有布尔类型，用 0/1 表示
    else:
        return 'TEXT'  # 默认转为 TEXT，可根据情况调整

# ======================
# 1. 连接到 MSSQL，获取表和列信息
# ======================

def get_mssql_tables_and_columns(conn_mssql,MSSQL_DATABASE,TABLES_TO_MIGRATE) -> Dict[str, List[Dict[str, str]]]:
    cursor = conn_mssql.cursor()

    # 获取所有用户表（排除系统表，根据 schema 过滤，如 'dbo'）
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' 
        AND TABLE_CATALOG = ?
    """, MSSQL_DATABASE)

    tables = [row.TABLE_NAME for row in cursor.fetchall()]

    if TABLES_TO_MIGRATE is not None:
        tables = [t for t in tables if t in TABLES_TO_MIGRATE]

    table_columns = {}

    for table in tables:
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') as IsIdentity
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table}'
            AND TABLE_CATALOG = '{MSSQL_DATABASE}'
            ORDER BY ORDINAL_POSITION
        """)
        # 注意：上面获取 ISIDENTITY 的方式可能因 SQL Server 版本不同而不同，更可靠的方式是通过 sys.columns 查询

        # 更通用的获取列信息方式（简化，不包含是否自增，你可以按需扩展）
        cursor.execute(f"""
            SELECT 
                COLUMN_NAME, 
                DATA_TYPE,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table}'
            ORDER BY ORDINAL_POSITION
        """)
        columns = []
        for col_name, data_type, is_nullable in cursor.fetchall():
            # 检查是否是自增列（简化处理，真实情况可能需要查询 sys.columns）
            is_identity = False
            col_type_mapped = map_mssql_to_sqlite_type(data_type)
            if 'IDENTITY' in data_type.upper() or 'AUTO_INCREMENT' in data_type.upper():
                is_identity = True
                col_type_mapped = col_type_mapped.replace('INTEGER', 'INTEGER PRIMARY KEY AUTOINCREMENT')

            columns.append({
                'name': col_name,
                'type': col_type_mapped,  # 已经映射为 SQLite 类型
                'nullable': is_nullable,
                'is_identity': is_identity
            })
        table_columns[table] = columns

    return tables, table_columns

# ======================
# 2. 连接到 SQLite 并创建表结构 + 导入数据
# ======================

def migrate_to_sqlite(mssql_conn, sqlite_path, tables, table_columns):
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()

    for table in tables:
        print(f"正在迁移表: {table}")
        columns_info = table_columns[table]
        # 构建 CREATE TABLE 语句
        columns_defs = []
        for col in columns_info:
            col_def = f"{col['name']} {col['type']}"
            columns_defs.append(col_def)
        columns_defs.append('id' + ' '+ 'INTEGER PRIMARY KEY AUTOINCREMENT')

        sqlite_cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"✅ 已删除表 '{table}'（如果它存在的话）")


        create_time = datetime.now()  # 或者用 datetime.utcnow() 获取 UTC 时间
        print(f"🔧 正在创建表 '{table}'，建表时间：{create_time}")
        start_time = time.time()
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns_defs)});"
        sqlite_cursor.execute(create_table_sql)

        # 从 MSSQL 获取所有数据
        # mssql_cursor = mssql_conn.cursor()
        # mssql_cursor.execute(f"SELECT * FROM {table}")
        # rows = mssql_cursor.fetchall()

        df = pd.read_sql(f"SELECT * FROM {table};", mssql_conn)

        if len(df)==0:
            print(f"表 {table} 无数据，跳过插入。")
            continue

        df.to_sql(table, sqlite_conn, if_exists='append', index=False, chunksize=5000)

        # 获取列名
        # col_names = [desc[0] for desc in mssql_cursor.description]
        # placeholders = ', '.join(['?'] * len(col_names))
        # insert_sql = f"INSERT INTO {table} ({', '.join(col_names)}) VALUES ({placeholders})"
        # 插入到 SQLite
        # sqlite_cursor.executemany(insert_sql, rows)
        print(f"表 {table}：已插入 {len(df)} 行数据。")
        end_time = time.time()
        # 计算耗时
        elapsed_seconds = end_time - start_time
        elapsed_minutes = elapsed_seconds / 60
        print(f"⏱️  建{table}表操作耗时：{elapsed_seconds:.2f} 秒，约 {elapsed_minutes:.4f} 分钟")


# ======================
# 主函数
# ======================

def main():
    MSSQL_SERVER = '192.168.10.200'  # 如 'localhost' 或 '127.0.0.1'，或 'DESKTOP-XXX\SQLEXPRESS'
    MSSQL_DATABASE = 'nWind'
    MSSQL_USERNAME = 'hcquant'  # 如果使用 Windows 认证，可以不填 username/password
    MSSQL_PASSWORD = 'Hcquant_hc_2022'
    MSSQL_DRIVER = '{ODBC Driver 17 for SQL Server}'  # 根据你安装的驱动版本调整，如 'SQL Server'
    # SQLite 文件路径
    SQLITE_DB_PATH = r"D:\factor\target.db"
    # 要迁移的表名列表（如果为 None，则迁移所有表）
    TABLES_TO_MIGRATE = ["ASHAREDESCRIPTION",
                         "ASHARECALENDAR","ASHAREEODPRICES"]

    mssql_conn_str = f'DRIVER={MSSQL_DRIVER};SERVER={MSSQL_SERVER};DATABASE={MSSQL_DATABASE};UID={MSSQL_USERNAME};PWD={MSSQL_PASSWORD}'

    print("正在连接 MSSQL...")
    mssql_conn = pyodbc.connect(mssql_conn_str)
    print("✅ MSSQL 连接成功！")
    # 2. 获取表和列信息
    tables, table_columns = get_mssql_tables_and_columns(mssql_conn,MSSQL_DATABASE,TABLES_TO_MIGRATE)
    print(f"📦 发现 {len(tables)} 个表准备迁移: {tables}")
    # 3. 连接 SQLite 并迁移
    print(f"🔁 开始迁移到 SQLite 数据库: {SQLITE_DB_PATH}")
    migrate_to_sqlite(mssql_conn, SQLITE_DB_PATH, tables, table_columns)
    # 4. 关闭 MSSQL 连接
    mssql_conn.close()
    print("✅ 迁移完成！SQLite 数据库已保存至：" + SQLITE_DB_PATH)

if __name__ == '__main__':
    main()