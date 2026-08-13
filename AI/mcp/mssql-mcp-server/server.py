#!/usr/bin/env python3
"""
MSSQL MCP Server - 基于 FastMCP 的 SQL Server 查询服务
兼容 MCP SDK 2.x，使用 pymssql 纯 Python 驱动（无需 ODBC）

环境变量:
    MSSQL_HOST: SQL Server 主机地址
    MSSQL_PORT: 端口号，默认 1433
    MSSQL_USER: 用户名
    MSSQL_PASSWORD: 密码
    MSSQL_DATABASE: 默认数据库
"""

import os
import json
from typing import Any
from contextlib import contextmanager

import pymssql
from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务器
mcp = FastMCP("mssql-server")

# 从环境变量读取配置
MSSQL_HOST = os.getenv("MSSQL_HOST", "localhost")
MSSQL_PORT = int(os.getenv("MSSQL_PORT", "1433"))
MSSQL_USER = os.getenv("MSSQL_USER", "sa")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "master")


@contextmanager
def get_connection(database: str = None):
    """获取数据库连接的上下文管理器"""
    conn = None
    try:
        conn = pymssql.connect(
            server=MSSQL_HOST,
            port=MSSQL_PORT,
            user=MSSQL_USER,
            password=MSSQL_PASSWORD,
            database=database or MSSQL_DATABASE,
            charset="utf8",
            as_dict=True,
        )
        yield conn
    finally:
        if conn:
            conn.close()


def format_results(rows: list[dict], max_rows: int = 1000) -> str:
    """格式化查询结果为易读的表格形式"""
    if not rows:
        return "查询成功，无返回数据"
    
    # 限制返回行数
    truncated = False
    if len(rows) > max_rows:
        rows = rows[:max_rows]
        truncated = True
    
    # 获取列名
    columns = list(rows[0].keys())
    
    # 计算每列宽度
    col_widths = {}
    for col in columns:
        col_widths[col] = max(
            len(str(col)),
            max(len(str(row.get(col, ""))) for row in rows)
        )
        # 限制最大宽度
        col_widths[col] = min(col_widths[col], 50)
    
    # 构建表格
    lines = []
    
    # 表头
    header = " | ".join(str(col).ljust(col_widths[col])[:col_widths[col]] for col in columns)
    lines.append(header)
    lines.append("-" * len(header))
    
    # 数据行
    for row in rows:
        line = " | ".join(
            str(row.get(col, "")).ljust(col_widths[col])[:col_widths[col]] 
            for col in columns
        )
        lines.append(line)
    
    result = "\n".join(lines)
    
    if truncated:
        result += f"\n\n... 结果已截断，共 {len(rows)} 行（限制 {max_rows} 行）"
    else:
        result += f"\n\n共 {len(rows)} 行"
    
    return result


@mcp.tool()
def execute_sql(query: str, database: str = None) -> str:
    """
    执行 SQL 查询语句
    
    Args:
        query: SQL 查询语句（SELECT/INSERT/UPDATE/DELETE 等）
        database: 可选，指定数据库名。不指定则使用默认数据库
    
    Returns:
        查询结果或执行状态
    """
    try:
        with get_connection(database) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            
            # 判断是否是查询语句
            if query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("WITH"):
                rows = cursor.fetchall()
                return format_results(rows)
            else:
                # DML 语句
                affected = cursor.rowcount
                conn.commit()
                return f"执行成功，影响 {affected} 行"
                
    except pymssql.Error as e:
        return f"SQL 执行错误: {str(e)}"
    except Exception as e:
        return f"错误: {str(e)}"


@mcp.tool()
def list_databases() -> str:
    """
    列出 SQL Server 实例上的所有数据库
    
    Returns:
        数据库列表
    """
    try:
        with get_connection("master") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, state_desc, create_date 
                FROM sys.databases 
                ORDER BY name
            """)
            rows = cursor.fetchall()
            return format_results(rows)
    except Exception as e:
        return f"错误: {str(e)}"


@mcp.tool()
def list_tables(database: str = None, schema: str = "dbo") -> str:
    """
    列出指定数据库中的所有表
    
    Args:
        database: 数据库名，不指定则使用默认数据库
        schema: Schema 名称，默认 dbo
    
    Returns:
        表列表
    """
    try:
        with get_connection(database) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    t.name AS table_name,
                    s.name AS schema_name,
                    p.rows AS row_count,
                    CAST(ROUND(SUM(a.total_pages) * 8 / 1024.0, 2) AS DECIMAL(18,2)) AS size_mb
                FROM sys.tables t
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                INNER JOIN sys.indexes i ON t.object_id = i.object_id
                INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
                INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
                WHERE s.name = %s
                GROUP BY t.name, s.name, p.rows
                ORDER BY t.name
            """, (schema,))
            rows = cursor.fetchall()
            return format_results(rows)
    except Exception as e:
        return f"错误: {str(e)}"


@mcp.tool()
def describe_table(table_name: str, database: str = None, schema: str = "dbo") -> str:
    """
    获取表的列信息和结构
    
    Args:
        table_name: 表名
        database: 数据库名，不指定则使用默认数据库
        schema: Schema 名称，默认 dbo
    
    Returns:
        表结构信息
    """
    try:
        with get_connection(database) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.name AS column_name,
                    t.name AS data_type,
                    c.max_length,
                    c.precision,
                    c.scale,
                    c.is_nullable,
                    c.is_identity,
                    ISNULL(dc.definition, '') AS default_value,
                    ISNULL(ep.value, '') AS description
                FROM sys.columns c
                INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
                INNER JOIN sys.tables tb ON c.object_id = tb.object_id
                INNER JOIN sys.schemas s ON tb.schema_id = s.schema_id
                LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
                LEFT JOIN sys.extended_properties ep ON ep.major_id = c.object_id 
                    AND ep.minor_id = c.column_id AND ep.name = 'MS_Description'
                WHERE tb.name = %s AND s.name = %s
                ORDER BY c.column_id
            """, (table_name, schema))
            rows = cursor.fetchall()
            
            if not rows:
                return f"未找到表 {schema}.{table_name}"
            
            return format_results(rows)
    except Exception as e:
        return f"错误: {str(e)}"


@mcp.tool()
def get_table_indexes(table_name: str, database: str = None, schema: str = "dbo") -> str:
    """
    获取表的索引信息
    
    Args:
        table_name: 表名
        database: 数据库名，不指定则使用默认数据库
        schema: Schema 名称，默认 dbo
    
    Returns:
        索引信息
    """
    try:
        with get_connection(database) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    i.name AS index_name,
                    i.type_desc AS index_type,
                    i.is_unique,
                    i.is_primary_key,
                    STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS columns
                FROM sys.indexes i
                INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
                INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
                INNER JOIN sys.tables t ON i.object_id = t.object_id
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                WHERE t.name = %s AND s.name = %s AND i.name IS NOT NULL
                GROUP BY i.name, i.type_desc, i.is_unique, i.is_primary_key
                ORDER BY i.is_primary_key DESC, i.name
            """, (table_name, schema))
            rows = cursor.fetchall()
            
            if not rows:
                return f"表 {schema}.{table_name} 没有索引"
            
            return format_results(rows)
    except Exception as e:
        return f"错误: {str(e)}"


@mcp.tool()
def get_table_sample(table_name: str, limit: int = 10, database: str = None, schema: str = "dbo") -> str:
    """
    获取表的示例数据
    
    Args:
        table_name: 表名
        limit: 返回行数，默认 10，最大 100
        database: 数据库名，不指定则使用默认数据库
        schema: Schema 名称，默认 dbo
    
    Returns:
        示例数据
    """
    limit = min(max(1, limit), 100)
    try:
        with get_connection(database) as conn:
            cursor = conn.cursor()
            # 使用参数化的 schema 和 table 名（注意：表名不能参数化，需要验证）
            # 简单验证表名，防止 SQL 注入
            if not table_name.replace("_", "").isalnum():
                return "无效的表名"
            if not schema.replace("_", "").isalnum():
                return "无效的 schema 名"
                
            cursor.execute(f"SELECT TOP {limit} * FROM [{schema}].[{table_name}]")
            rows = cursor.fetchall()
            return format_results(rows)
    except Exception as e:
        return f"错误: {str(e)}"


@mcp.tool()
def get_server_info() -> str:
    """
    获取 SQL Server 服务器信息
    
    Returns:
        服务器版本和配置信息
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    @@VERSION AS version,
                    @@SERVERNAME AS server_name,
                    DB_NAME() AS current_database,
                    SYSTEM_USER AS login_user,
                    USER_NAME() AS database_user
            """)
            row = cursor.fetchone()
            
            info = []
            info.append(f"服务器: {row['server_name']}")
            info.append(f"版本: {row['version']}")
            info.append(f"当前数据库: {row['current_database']}")
            info.append(f"登录用户: {row['login_user']}")
            info.append(f"数据库用户: {row['database_user']}")
            
            return "\n".join(info)
    except Exception as e:
        return f"错误: {str(e)}"


@mcp.tool()
def search_tables(keyword: str, database: str = None) -> str:
    """
    按关键字搜索表名
    
    Args:
        keyword: 搜索关键字
        database: 数据库名，不指定则使用默认数据库
    
    Returns:
        匹配的表列表
    """
    try:
        with get_connection(database) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.name AS schema_name,
                    t.name AS table_name,
                    p.rows AS row_count
                FROM sys.tables t
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                INNER JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0, 1)
                WHERE t.name LIKE %s
                ORDER BY s.name, t.name
            """, (f"%{keyword}%",))
            rows = cursor.fetchall()
            
            if not rows:
                return f"未找到包含 '{keyword}' 的表"
            
            return format_results(rows)
    except Exception as e:
        return f"错误: {str(e)}"


@mcp.tool()
def search_columns(keyword: str, database: str = None) -> str:
    """
    按关键字搜索列名
    
    Args:
        keyword: 搜索关键字
        database: 数据库名，不指定则使用默认数据库
    
    Returns:
        匹配的列信息
    """
    try:
        with get_connection(database) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.name AS schema_name,
                    t.name AS table_name,
                    c.name AS column_name,
                    ty.name AS data_type
                FROM sys.columns c
                INNER JOIN sys.tables t ON c.object_id = t.object_id
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                INNER JOIN sys.types ty ON c.user_type_id = ty.user_type_id
                WHERE c.name LIKE %s
                ORDER BY s.name, t.name, c.name
            """, (f"%{keyword}%",))
            rows = cursor.fetchall()
            
            if not rows:
                return f"未找到包含 '{keyword}' 的列"
            
            return format_results(rows)
    except Exception as e:
        return f"错误: {str(e)}"


if __name__ == "__main__":
    mcp.run()
