import mysql.connector
from mysql.connector import Error
from flask import current_app
from datetime import datetime
#写一个选择不同数据库的函数，再把连接函数写成以选择结果为参数的函数

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_query(query, params=None, fetchone=False, commit=False):
    """执行 SQL 查询"""
    connection = get_db_connection()
    if not connection:
        return None
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params or ())
            if commit:
                connection.commit()
            if fetchone:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            return result
    except Error as e:
        print(f"Error executing query: {e}")
        connection.rollback()
        return None
    finally:
        if connection.is_connected():
            connection.close()

def execute_insert_update_delete(query, params=None):
    """执行 INSERT、UPDATE、DELETE 操作"""
    connection = get_db_connection()
    if not connection:
        return False

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            connection.commit()
            return True
    except Error as e:
        print(f"Error executing insert/update/delete: {e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            connection.close()

def select(
    table,
    fields='*',
    joins=None,
    conditions=None,
    condition_operator='AND',
    group_by=None,
    having=None,
    order_by=None,
    limit=None,
    offset=None,
    distinct=False,
    aliases=None,
    params=None,
    unions=None
):
    """
    功能齐全的 SELECT 操作（支持 UNION）
    :param table: 主表名 (可带别名，如 "users u")
    :param fields: 查询字段 (支持逗号分隔的字符串或列表，支持字段别名)
    :param joins: JOIN 子句列表，格式示例：
        [
            ("INNER JOIN orders o ON o.user_id = u.id", None),
            ("LEFT JOIN payments p ON p.order_id = o.id", {"p.status": "paid"})
        ]
    :param conditions: WHERE 条件，支持字典或元组列表：
        字典格式：{"age >": 18, "name LIKE": "%John%"}
        列表格式：[("created_at BETWEEN", (start_date, end_date)), ("role IN", roles)]
    :param condition_operator: 条件逻辑运算符 (AND/OR)
    :param group_by: GROUP BY 子句
    :param having: HAVING 子句
    :param order_by: ORDER BY 子句
    :param limit: LIMIT 值
    :param offset: OFFSET 值
    :param distinct: 是否添加 DISTINCT 关键字
    :param aliases: 字段别名映射 (如 {"u.id": "user_id"})
    :param params: 额外参数列表 (用于复杂条件)
    :param unions: UNION 子句列表，格式示例：
        [
            {
                "type": "UNION",        # 可选值为 UNION 或 UNION ALL
                "table": "other_table",  # 子查询表名
                "fields": "id",         # 子查询字段（需与主查询字段一致）
                "conditions": {"status": 1},  # 子查询条件
                "joins": [...]          # 子查询 JOIN 子句（可选）
            }
        ]
    :return: 查询结果
    """
    # 处理字段别名和格式化
    if isinstance(fields, list):
        fields = ", ".join(fields)
    if aliases:
        for original, alias in aliases.items():
            fields = fields.replace(original, f"{original} AS {alias}")

    query = ["SELECT"]
    query.append("DISTINCT" if distinct else "")
    query.append(fields)
    query.append(f"FROM {table}")

    params = params or []  # 主查询参数

    # 处理 JOIN 子句
    if joins:
        for join_clause, join_conditions in joins:
            query.append(join_clause)
            if join_conditions:
                where_clause, join_params = _build_conditions(join_conditions)
                query.append(f"AND {where_clause}")
                params.extend(join_params)

    # 构建 WHERE 条件
    if conditions:
        where_clause, where_params = _build_conditions(conditions, condition_operator)
        query.append(f"WHERE {where_clause}")
        params.extend(where_params)

    # 处理 GROUP BY 和 HAVING
    if group_by:
        query.append(f"GROUP BY {group_by}")
        if having:
            having_clause, having_params = _build_conditions(having)
            query.append(f"HAVING {having_clause}")
            params.extend(having_params)

    # 构建主查询 SQL
    main_query = " ".join(query)

    # 处理 UNION 子查询
    union_queries = []
    union_params = []
    if unions:
        for union_config in unions:
            # 生成子查询 SQL 和参数
            sub_query = select(
                table=union_config["table"],
                fields=union_config.get("fields", fields),
                joins=union_config.get("joins"),
                conditions=union_config.get("conditions"),
                condition_operator=union_config.get("condition_operator", "AND"),
                group_by=union_config.get("group_by"),
                having=union_config.get("having"),
                order_by=union_config.get("order_by"),
                limit=union_config.get("limit"),
                offset=union_config.get("offset"),
                distinct=union_config.get("distinct", False),
                aliases=union_config.get("aliases"),
                params=union_config.get("params"),
                unions=None  # 禁止嵌套 UNION
            )
            # 提取子查询的 SQL 和参数（假设返回格式为 (sql, params)）
            sub_sql = sub_query[0] if isinstance(sub_query, tuple) else sub_query
            union_type = union_config.get("type", "UNION")
            union_queries.append(f"{union_type} ({sub_sql})")
            union_params.extend(sub_query[1] if isinstance(sub_query, tuple) else [])

    # 合并主查询和 UNION 子查询
    full_query = main_query
    if unions:
        full_query += " " + " ".join(union_queries)

    # 处理排序和分页（作用于整个 UNION 查询）
    if order_by:
        full_query += f" ORDER BY {order_by}"
    if limit:
        full_query += f" LIMIT {limit}"
    if offset:
        full_query += f" OFFSET {offset}"

    # 合并所有参数
    all_params = params + union_params

    # 执行查询
    return execute_query(full_query, all_params)

def _build_conditions(conditions, operator='AND'):
    """
    构建 WHERE 条件子句
    :param conditions: 条件字典或列表
    :param operator: 逻辑运算符
    :return: (条件子句, 参数列表)
    """
    clauses = []
    params = []
    
    if isinstance(conditions, dict):
        conditions = conditions.items()
    
    for key, value in conditions:
        if "__" in key:
            field, op = key.split("__", 1)
            op = op.upper()
        elif " " in key:
            field, op = key.rsplit(" ", 1)
            op = op.upper()
        else:
            field, op = key, "="
        
        # 处理特殊操作符
        if op == "IN":
            placeholders = ", ".join(["%s"] * len(value))
            clauses.append(f"{field} IN ({placeholders})")
            params.extend(value)
        elif op == "BETWEEN":
            clauses.append(f"{field} BETWEEN %s AND %s")
            params.extend(value)
        else:
            clauses.append(f"{field} {op} %s")
            params.append(value)
    
    return f" {operator} ".join(clauses), params

def insert(table, data):
    """INSERT 操作"""
    fields = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    query = f"INSERT INTO {table} ({fields}) VALUES ({placeholders})"
    return execute_insert_update_delete(query, list(data.values()))

def update(table, data, conditions):
    """UPDATE 操作"""
    set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
    where_clause = " AND ".join([f"{k} = %s" for k in conditions.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    params = list(data.values()) + list(conditions.values())
    return execute_insert_update_delete(query, params)

def delete(table, conditions):
    """DELETE 操作"""
    where_clause = " AND ".join([f"{k} = %s" for k in conditions.keys()])
    query = f"DELETE FROM {table} WHERE {where_clause}"
    return execute_insert_update_delete(query, list(conditions.values()))