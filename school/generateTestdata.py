from datetime import datetime
import os

def generate_sql(target_date: str, output_file="testData.sql"):
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        print("日期格式应为 YYYY-MM-DD")
        return

    # Student 插入语句
    student_insert = """INSERT INTO Student (Student_id, Student_name, Student_phone, Student_password) VALUES
(2250681, '赵嘉禾', '18004855049', '2250681'),
(2254228, '朱雨欢', '14782034156', '2254228'),
(2251146, '吴天宇', '11111111111', '2251146'),
(2251181, '仇伟烨', '22222222222', '2251181'),
(2254296, '侯青山', '33333333333', '2254296'),
(2252403, '赵唯旭', '44444444444', '2252403');

"""

    court_insert_head = """INSERT INTO CourtInfo (
    Court_id,
    Court_campus,
    Court_date,
    Court_time,
    Court_no,
    Court_state
) VALUES 
"""

    court_values = []
    for t in range(13):  # 0~12 时段
        for c in range(6):  # 场地1~6
            court_id = f"JiaDing-{target_date}-{t}-{c}"
            court_values.append(f"('{court_id}', 'JiaDing', '{target_date}', {t}, '场地{c+1}', 'not_owned')")

    court_insert_body = ",\n".join(court_values) + ";\n\n"

    update_statements = [
        (0, 0, 2250681),
        (1, 1, 2254228),
        (2, 2, 2251146),
        (4, 3, 2251181),
        (3, 4, 2254296),
        (5, 5, 2252403),
        (6, 0, 2250681),
        (7, 1, 2254228),
        (8, 2, 2251146),
        (9, 3, 2251181),
        (10, 4, 2254296),
        (11, 5, 2252403)
    ]

    update_sql = ""
    for time, court_no, student_id in update_statements:
        court_id = f"JiaDing-{target_date}-{time}-{court_no}"
        update_sql += f"UPDATE CourtInfo SET Court_owner = {student_id}, Court_state = 'owned' WHERE Court_id = '{court_id}';\n"

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(student_insert)
        f.write(court_insert_head)
        f.write(court_insert_body)
        f.write(update_sql)

    print(f"✅ SQL 文件已成功生成: {output_file}")


if __name__ == "__main__":
    user_date = input("请输入目标日期 (格式 YYYY-MM-DD)：").strip()
    generate_sql(user_date)
