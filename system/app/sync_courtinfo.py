import mysql.connector
import traceback

school_db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '557177Hou',
    'database': 'school'
}

local_db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '557177Hou',
    'database': 'system'
}

has_synced_once = False  # 是否已经执行过一次同步


def sync_court_info():
    global has_synced_once  # 🟡 访问全局变量
    try:
        # 数据库连接
        school_db = mysql.connector.connect(**school_db_config)
        local_db = mysql.connector.connect(**local_db_config)

        school_cursor = school_db.cursor(dictionary=True)
        local_cursor = local_db.cursor(dictionary=True)

        # 查询数据
        school_cursor.execute("SELECT * FROM CourtInfo")
        school_data = school_cursor.fetchall()

        local_cursor.execute("SELECT * FROM CourtInfo")
        local_data = local_cursor.fetchall()

        local_cursor.execute("SELECT Student_id FROM Student")
        local_students = {row['Student_id'] for row in local_cursor.fetchall()}

        school_mapping = {row['Court_id']: row for row in school_data}
        local_mapping = {row['Court_id']: row for row in local_data}

        missing_students = set()
        updated = False

        # 插入 / 更新
        for court_id, school_row in school_mapping.items():
            owner = school_row['Court_owner']
            if owner is not None and owner not in local_students:
                missing_students.add(owner)
                continue

            if court_id in local_mapping:
                local_row = local_mapping[court_id]
                if (school_row['Court_state'] != local_row['Court_state'] or
                        school_row['Court_owner'] != local_row['Court_owner']):
                    local_cursor.execute("""
                        UPDATE CourtInfo
                        SET Court_state = %s, Court_owner = %s
                        WHERE Court_id = %s
                    """, (school_row['Court_state'], school_row['Court_owner'], court_id))
                    updated = True
            else:
                local_cursor.execute("""
                    INSERT INTO CourtInfo (Court_id, Court_campus, Court_date, Court_time, Court_no, Court_state, Court_owner, Court_qrcodeurl)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    school_row['Court_id'], school_row['Court_campus'], school_row['Court_date'],
                    school_row['Court_time'], school_row['Court_no'], school_row['Court_state'],
                    school_row['Court_owner'], school_row['Court_qrcodeurl']
                ))
                updated = True

        # 删除
        for court_id in local_mapping:
            if court_id not in school_mapping:
                local_cursor.execute("DELETE FROM CourtInfo WHERE Court_id = %s", (court_id,))
                updated = True

        local_db.commit()

        # ✅ 打印：第一次同步 or 有更新时打印
        if not has_synced_once or updated:
            print("✅ CourtInfo 表同步成功。")
            if missing_students:
                print(f"⚠️ 以下 Student_id 不存在，相关场地未同步：{sorted(missing_students)}")
            has_synced_once = True

    except Exception as e:
        print(f"同步过程中出错：{e}")
        traceback.print_exc()

    finally:
        try:
            school_cursor.close()
            school_db.close()
            local_cursor.close()
            local_db.close()
        except:
            pass
