from flask import Blueprint, request, jsonify
from app import mysql
from datetime import datetime

bp = Blueprint('exchangecourt', __name__, url_prefix='/exchangecourt')

@bp.route('/upload', methods=['POST'])
def add_exchange_upload_and_operation_record():
    data = request.get_json()
    # 从请求中获取数据
    exchange_uploader_id = data.get('Exchange_uploader_id')  # 发布者学号
    exchange_uploaded_court_id = data.get('Exchange_uploaded_court_id')  # 场地ID
    # 校验必要字段
    if not exchange_uploader_id or not exchange_uploaded_court_id:
        return jsonify({'message': 'Missing required fields'}), 400
    # 获取当前时间
    current_time = datetime.now()
    cur = mysql.connection.cursor()
    try:
        # 1. 检查是否已存在相同的上传请求（Exchange、Offer、Teamup）
        check_existing_upload_query = """
            SELECT COUNT(*) 
            FROM (
                SELECT 1 FROM Exchangecourt_upload WHERE Exchange_uploader_id = %s AND Exchange_uploaded_court_id = %s
                UNION
                SELECT 1 FROM Offercourt_upload WHERE Offer_uploader_id = %s AND Offer_uploaded_court_id = %s
                UNION
                SELECT 1 FROM Teamup_upload WHERE Teamup_uploader_id = %s AND Teamup_court_id = %s
            ) AS existing_uploads
        """
        cur.execute(check_existing_upload_query, (
            exchange_uploader_id, exchange_uploaded_court_id, 
            exchange_uploader_id, exchange_uploaded_court_id,
            exchange_uploader_id, exchange_uploaded_court_id
        ))
        result = cur.fetchone()
        if result[0] > 0:
            # 如果有重复的上传请求
            return jsonify({'message': 'This user has already uploaded a request for this court'}), 402
        # 2. 插入 Exchangecourt_upload 表
        insert_exchange_query = """
            INSERT INTO Exchangecourt_upload (
                Exchange_uploader_id, Exchange_upload_state,
                Exchange_uploaded_court_id, Exchange_upload_time
            )
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(insert_exchange_query, (
            exchange_uploader_id, 'not_responsed',
            exchange_uploaded_court_id, current_time
        ))
        
        # 获取生成的 Exchangecourt_upload_id
        exchangecourt_upload_id = cur.lastrowid
        # 3. 插入 Operation_record 表
        insert_operation_query = """
            INSERT INTO Operation_record (
                Operator_id, Operation_type, Operation_id,
                Operation_status, Operation_time
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        operation_type = 'Exchangecourt_upload'
        operation_status = 0  # 状态 'not_responsed' 对应的索引值
        cur.execute(insert_operation_query, (
            exchange_uploader_id, operation_type,
            exchangecourt_upload_id, operation_status, current_time
        ))
        # 提交事务
        mysql.connection.commit()
        
        return jsonify({'message': 'Exchange upload and operation record added successfully'}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while adding records', 'error': str(e)}), 500
    finally:
        cur.close()


# 响应者相应换场请求
@bp.route('/respond', methods=['POST'])
def respond_to_exchange():
    data = request.get_json()
    # 从请求中获取数据
    exchange_responser_id = data.get('Exchange_responser_id')  # 换场响应者学号
    exchange_uploader_court_id = data.get('Exchange_uploader_court_id')  # 发布者的场地ID
    exchange_responser_court_id = data.get('Exchange_responser_court_id')  # 响应者的场地ID

    # 校验必要字段
    if not all([exchange_responser_id, exchange_uploader_court_id, exchange_responser_court_id]):
        return jsonify({'message': 'Missing required fields'}), 400

    cur = mysql.connection.cursor()
    current_time = datetime.now()

    try:
        # 查询 Exchangecourt_upload 表，获取 Exchange_uploader_id
        check_uploader_query = """
            SELECT Exchange_uploader_id FROM Exchangecourt_upload 
            WHERE Exchange_uploaded_court_id = %s
        """
        cur.execute(check_uploader_query, (exchange_uploader_court_id,))
        uploader_record = cur.fetchone()

        # 如果没有找到对应记录，返回错误
        if not uploader_record:
            return jsonify({'message': 'No exchange uploader found for the given court.'}), 404

        exchange_uploader_id = uploader_record[0]  # 从查询结果中获取 Exchange_uploader_id

        # 检查 Offercourt_upload 和 Teamup_upload 表中是否已有相同的发布请求
        check_offer_query = """
            SELECT 1 FROM Offercourt_upload 
            WHERE Offer_uploader_id = %s 
            AND Offer_uploaded_court_id = %s
        """
        check_teamup_query = """
            SELECT 1 FROM Teamup_upload 
            WHERE Teamup_uploader_id = %s 
            AND Teamup_court_id = %s
        """
        # 检查是否已经发布过送场请求
        cur.execute(check_offer_query, (exchange_responser_id, exchange_responser_court_id))
        offer_record = cur.fetchone()
        # 检查是否已经发布过组队拼场请求
        cur.execute(check_teamup_query, (exchange_responser_id, exchange_responser_court_id))
        teamup_record = cur.fetchone()
        # 如果已经发布过上传请求，则返回错误码 402
        if offer_record or teamup_record:
            return jsonify({'message': 'Duplicate upload request found. Please do not submit multiple upload requests for the same court.'}), 402

        # 检查 Exchangecourt_upload 表中是否有对应的记录
        check_exchange_query = """
            SELECT * FROM Exchangecourt_upload 
            WHERE Exchange_uploader_id = %s 
            AND Exchange_uploaded_court_id = %s
        """
        cur.execute(check_exchange_query, (
            exchange_uploader_id, exchange_uploader_court_id
        ))
        upload_record = cur.fetchone()

        # 如果没有找到对应记录，则先插入 Exchangecourt_upload 记录
        if not upload_record:
            insert_upload_query = """
                INSERT INTO Exchangecourt_upload (
                    Exchange_uploader_id, Exchange_uploaded_court_id,
                    Exchange_upload_state, Exchange_upload_time
                ) VALUES (%s, %s, %s, %s)
            """
            current_time = datetime.now()
            cur.execute(insert_upload_query, (
                exchange_uploader_id, exchange_uploader_court_id,
                'not_responsed', current_time
            ))
            mysql.connection.commit()  # 提交事务
            print('新发布的换场请求已经创建')

        # 插入到 Exchangecourt_record 表
        insert_record_query = """
            INSERT INTO Exchangecourt_record (
                Exchange_uploader_id, Exchange_responser_id,
                Exchange_uploader_court_id, Exchange_responser_court_id,
                Exchange_state
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_record_query, (
            exchange_uploader_id, exchange_responser_id,
            exchange_uploader_court_id, exchange_responser_court_id,
            'not_responsed'  # 默认状态
        ))

        # 获取生成的 Exchangecourt_record_id
        exchangecourt_record_id = cur.lastrowid

        # 插入到 Operation_record 表
        insert_operation_query = """
            INSERT INTO Operation_record (
                Operator_id, Operation_type, Operation_id,
                Operation_status, Operation_time
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        operation_type = 'Exchangecourt_record'
        operation_status = 0  # 状态 'not_responsed' 对应的索引值
        cur.execute(insert_operation_query, (
            exchange_responser_id, operation_type,
            exchangecourt_record_id, operation_status, current_time
        ))

        # 提交事务
        mysql.connection.commit()
        return jsonify({'message': 'Exchange response recorded successfully'}), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while recording exchange response', 'error': str(e)}), 500

#获取所有换场响应记录
@bp.route('/get_response_records_by_student', methods=['POST'])
def get_response_records_by_student():
    data = request.get_json()
    student_id = data.get('student_id')  # 学生ID

    # 校验必要字段
    if not student_id:
        return jsonify({'message': 'Missing required fields'}), 400

    cur = mysql.connection.cursor()
    try:
        # 查询Exchangecourt_record中响应者的记录
        query = """
            SELECT er.Exchange_record_id, er.Exchange_state, er.Exchange_uploader_court_id, er.Exchange_responser_court_id,
                   er.Exchange_uploader_score, er.Exchange_responser_score,er.Exchange_responser_id,
                   s.Student_name, s.Student_profileurl, s.Student_nickname, s.Student_credit, s.Student_level
            FROM Exchangecourt_record er
            JOIN Student s ON er.Exchange_responser_id = s.Student_id
            WHERE er.Exchange_uploader_id = %s
        """
        cur.execute(query, (student_id,))
        response_records = cur.fetchall()

        # 将查询结果转换为字典列表
        response_records_list = [{
            'exchange_record_id': row[0],
            'exchange_state': row[1],
            'exchange_uploader_court_id': row[2],
            'exchange_responser_court_id': row[3],
            'exchange_uploader_score': row[4],
            'exchange_responser_score': row[5],
            'exchange_responser_id' : row[6],
            'responser_info': {
                'name': row[7],
                'profileurl': row[8],
                'nickname': row[9],
                'credit': row[10],
                'level': row[11]
            }
        } for row in response_records]

        return jsonify({'data':response_records_list,'status':'success'}), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while fetching response records', 'error': str(e)}), 500
    finally:
        cur.close()

@bp.route('/complete_exchange', methods=['POST'])
def complete_exchange():
    data = request.get_json()

    # 从前端获取参数
    uploader_court_id = data.get('Exchange_uploader_court_id')
    responser_court_id = data.get('Exchange_responser_court_id')
    uploader_id = data.get('Exchange_uploader_id')
    responser_id = data.get('Exchange_responser_id')

    if not uploader_court_id or not responser_court_id or not uploader_id or not responser_id:
        return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400

    try:
        with mysql.connection.cursor() as cursor:
            # 在 Exchangecourt_record 表中更新状态为 exchanged
            sql_update_record = """
                UPDATE Exchangecourt_record
                SET Exchange_state = 'exchanged'
                WHERE Exchange_uploader_court_id = %s 
                  AND Exchange_responser_court_id = %s
                  AND Exchange_uploader_id = %s
                  AND Exchange_responser_id = %s
            """
            cursor.execute(sql_update_record, (uploader_court_id, responser_court_id, uploader_id, responser_id))
            
            if cursor.rowcount == 0:
                return jsonify({'status': 'error', 'message': '未找到匹配的交换记录'}), 404

            # 在 Exchangecourt_upload 表中更新状态为 exchanged
            sql_update_upload = """
                UPDATE Exchangecourt_upload
                SET Exchange_upload_state = 'exchanged'
                WHERE Exchange_uploaded_court_id = %s
                  AND Exchange_uploader_id = %s
            """
            cursor.execute(sql_update_upload, (uploader_court_id, uploader_id))
            
            if cursor.rowcount == 0:
                return jsonify({'status': 'error', 'message': '未找到匹配的上传记录'}), 404

            # 提交事务
            mysql.connection.commit()

        return jsonify({'status': 'success', 'message': '交换完成成功'}), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

#拒绝换场
@bp.route('/refuse', methods=['POST'])
def refuse_exchange():
    data = request.get_json()

    # 从前端获取参数
    uploader_court_id = data.get('Exchange_uploader_court_id')
    responser_court_id = data.get('Exchange_responser_court_id')
    uploader_id = data.get('Exchange_uploader_id')
    responser_id = data.get('Exchange_responser_id')

    if not uploader_court_id or not responser_court_id or not uploader_id or not responser_id:
        return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400

    try:
        with mysql.connection.cursor() as cursor:
            # 在 Exchangecourt_record 表中更新状态为 retrieved
            sql_update_record = """
                UPDATE Exchangecourt_record
                SET Exchange_state = 'retrieved'
                WHERE Exchange_uploader_court_id = %s 
                  AND Exchange_responser_court_id = %s
                  AND Exchange_uploader_id = %s
                  AND Exchange_responser_id = %s
            """
            cursor.execute(sql_update_record, (uploader_court_id, responser_court_id, uploader_id, responser_id))
            
            if cursor.rowcount == 0:
                return jsonify({'status': 'error', 'message': '未找到匹配的记录'}), 404

            # 提交事务
            mysql.connection.commit()

        return jsonify({'status': 'success', 'message': '拒绝完成成功'}), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500