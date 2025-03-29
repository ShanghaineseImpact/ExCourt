from flask import Blueprint, request, jsonify
from datetime import datetime
from execute_for_sql import select, insert, update, delete  # 导入封装的SQL函数

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.route('/register', methods=['POST'])
def register_student():
    data = request.get_json()
    student_id = data.get('Student_id')
    student_name = data.get('Student_name')
    student_nickname = data.get('Student_nickname')
    student_phone = data.get('Student_phone')
    student_password = data.get('Student_password')

    if not student_id or not student_name or not student_password or not student_nickname:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # 使用封装的insert函数
        student_data = {
            'Student_id': student_id,
            'Student_name': student_name,
            'Student_nickname': student_nickname,
            'Student_phone': student_phone,
            'Student_password': student_password,
            'Student_credit': 100,
            'Student_level': 1,
            'Student_status': 1
        }
        insert(
            table="Student",
            data=student_data
        )
        return jsonify({'message': 'Student registered successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error occurred while registering student', 'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    student_id = data.get('Student_id')
    password = data.get('Student_password')

    if not student_id or not password:
        return jsonify({'message': 'Student_id and password are required'}), 400

    try:
        # 使用封装的select函数
        result = select(
            table="Student",
            fields=["Student_password"],
            conditions={"Student_id": student_id},
            fetchone=True
        )

        if not result:
            return jsonify({'message': 'Student_id not found'}), 404

        if result['Student_password'] != password:
            return jsonify({'message': 'Incorrect password'}), 401

        student = select(
            table="Student",
            fields=["Student_id", "Student_name"],
            conditions={"Student_id": student_id},
            fetchone=True
        )
        return jsonify({
            'message': 'Login successful',
            'Student_id': student['Student_id'],
            'Student_name': student['Student_name']
        })
    except Exception as e:
        return jsonify({'message': 'Error occurred while logging in', 'error': str(e)}), 500

@bp.route('/update', methods=['POST'])
def update_info():
    data = request.get_json()
    search_id = data.get('search_id')
    profileurl = data.get('profileurl')
    nickname = data.get('nickname')
    phone = data.get('phone')
    level = data.get('level')

    if not search_id or not profileurl or not nickname or not phone or not level:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        # 使用封装的update函数
        updated = update(
            table="Student",
            data={
                "Student_profileurl": profileurl,
                "Student_nickname": nickname,
                "Student_phone": phone,
                "Student_level": level
            },
            conditions={"Student_id": search_id}
        )
        
        if updated:
            return jsonify({"status": "success", "message": "用户信息已更新"}), 200
        else:
            return jsonify({"status": "error", "message": "用户不存在"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/owned-courts', methods=['POST'])
def get_owned_courts():
    data = request.get_json()
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({"message": "Missing required field: student_id"}), 400

    try:
        # 使用封装的select函数
        results = select(
            table="CourtInfo",
            fields=["Court_id", "Court_no", "Court_campus", "Court_date", "Court_time", "Court_owner"],
            conditions={
                "Court_owner": student_id,
                "Court_state": "owned"
            }
        )

        today = datetime.today().date()
        owned_courts = [
            {
                "dayId": (row['Court_date'] - today).days,
                "Court_owner": row['Court_owner'],
                "Court_no": row['Court_no'],
                "Court_time": row['Court_time'],
                "Court_id": row['Court_id']
            }
            for row in results
        ]

        return jsonify({"student_id": student_id, "owned_courts": owned_courts}), 200
    except Exception as e:
        return jsonify({"message": "Error occurred while fetching owned courts", "error": str(e)}), 500

@bp.route('/get_operation_records', methods=['GET'])
def get_operation_records():
    data = request.get_json()
    operator_id = data.get('student_id')

    if not operator_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # 使用封装的select函数
        operation_records = select(
            table="Operation_record",
            fields=["Operation_record_id", "Operation_type", "Operation_id", "Operation_status", "Operation_time"],
            conditions={"Operator_id": operator_id},
            order_by="Operation_time DESC"
        )

        operation_records_list = [{
            'operation_record_id': row['Operation_record_id'],
            'operation_type': row['Operation_type'],
            'operation_id': row['Operation_id'],
            'operation_status': row['Operation_status'],
            'operation_time': row['Operation_time'].strftime('%Y-%m-%d %H:%M:%S')
        } for row in operation_records]

        return jsonify(operation_records_list), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching operation records', 'error': str(e)}), 500

@bp.route('/find', methods=['POST'])
def query_friend():
    search_id = request.json.get('search_id')

    if not search_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        # 使用封装的select函数
        user_info = select(
            table="Student",
            fields=[
                "Student_id", "Student_name", "Student_profileurl", 
                "Student_nickname", "Student_credit", "Student_level", 
                "Student_status", "Student_phone"
            ],
            conditions={"Student_id": search_id},
            fetchone=True
        )

        if not user_info:
            return jsonify({"status": "error", "message": "用户不存在"}), 404

        return jsonify({
            "status": "success",
            "message": "获取用户信息成功",
            "data": user_info
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/get_exchangecourt', methods=['POST'])
def get_exchangecourt():
    data = request.get_json()
    my_id = data.get('my_id')
    
    if not my_id:
        return jsonify({'message': 'Missing required fields: my_id'}), 400

    try:
        # 使用封装的select函数
        court_ids = select(
            table="Exchangecourt_upload",
            fields=["Exchange_uploaded_court_id AS court_id"],
            conditions={"Exchange_uploader_id != %s": my_id}
        )

        court_ids_list = [{"court_id": row['court_id']} for row in court_ids]
        return jsonify({'court_ids_list': court_ids_list}), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching court ids', 'error': str(e)}), 500

@bp.route('/get_teamupcourt', methods=['POST'])
def get_teamupcourt():
    data = request.get_json()
    my_id = data.get('my_id')
    
    if not my_id:
        return jsonify({'message': 'Missing required fields: my_id'}), 400

    try:
        # 使用封装的select函数
        court_ids = select(
            table="Teamup_upload",
            fields=["Teamup_court_id AS court_id"],
            conditions={"Teamup_uploader_id != %s": my_id}
        )

        court_ids_list = [{"court_id": row['court_id']} for row in court_ids]
        return jsonify({'court_ids_list': court_ids_list}), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching court ids', 'error': str(e)}), 500

@bp.route('/get_offercourt', methods=['POST'])
def get_offercourt():
    data = request.get_json()
    my_id = data.get('my_id')
    
    if not my_id:
        return jsonify({'message': 'Missing required fields: my_id'}), 400

    try:
        # 使用封装的select函数
        court_ids = select(
            table="Offercourt_upload",
            fields=["Offer_uploaded_court_id AS court_id"],
            conditions={
                "Offer_uploader_id != %s": my_id,
                "offer_upload_state IN": ["not_responsed", "responsed"]
            }
        )

        court_ids_list = [{"court_id": row['court_id']} for row in court_ids]
        return jsonify({'court_ids_list': court_ids_list}), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching court ids', 'error': str(e)}), 500

@bp.route('/get_apply', methods=['POST'])
def get_user_apply():
    data = request.get_json()
    my_id = data.get('my_id')
    if not my_id:
        return jsonify({'message': 'Missing required fields: my_id'}), 400

    try:
        # 使用封装的select函数查询三个表
        exchangecourt_data = select(
            table="Exchangecourt_upload",
            fields=[
                "Exchange_uploaded_court_id AS court_id", 
                "Exchange_upload_state AS status", 
                "'Exchangecourt' AS source"
            ],
            conditions={"Exchange_uploader_id": my_id}
        )

        offercourt_data = select(
            table="Offercourt_upload",
            fields=[
                "Offer_uploaded_court_id AS court_id", 
                "Offer_upload_state AS status", 
                "'Offercourt' AS source"
            ],
            conditions={"Offer_uploader_id": my_id}
        )

        teamup_data = select(
            table="Teamup_upload",
            fields=[
                "Teamup_court_id AS court_id", 
                "Teamup_upload_state AS status", 
                "'Teamup' AS source"
            ],
            conditions={"Teamup_uploader_id": my_id}
        )

        result = [
            {"court_id": row['court_id'], "status": row['status'], "source": row['source']}
            for row in exchangecourt_data + offercourt_data + teamup_data
        ]

        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"message": "Error occurred while fetching court ids", "error": str(e)}), 500

@bp.route('/get_my_request', methods=['POST'])
def get_user_repond():
    data = request.get_json()
    my_id = data.get('my_id')
    
    if not my_id:
        return jsonify({'message': 'Missing required fields: my_id'}), 400

    try:
        # 使用封装的select函数查询三个表
        exchangecourt_data = select(
            table="Exchangecourt_record",
            fields=[
                "Exchange_responser_court_id AS court_id",
                "Exchange_state AS status", 
                "'Exchangecourt' AS source"
            ],
            conditions={"Exchange_responser_id": my_id}
        )

        offercourt_data = select(
            table="Offercourt_record",
            fields=[
                "Offer_uploader_court_id AS court_id",
                "Offer_state AS status", 
                "'Offercourt' AS source"
            ],
            conditions={"Offer_responser_id": my_id}
        )

        teamup_data = select(
            table="Teamup_request_record",
            fields=[
                "Teamup_court_id AS court_id",
                "Teamup_request_state AS status", 
                "'Teamup' AS source"
            ],
            conditions={"Teamup_requester_id": my_id}
        )

        result = [
            {"court_id": row['court_id'], "status": row['status'], "source": row['source']}
            for row in exchangecourt_data + offercourt_data + teamup_data
        ]

        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"message": "Error occurred while fetching court ids", "error": str(e)}), 500

@bp.route('/delete_apply', methods=['POST'])
def delete_apply():
    data = request.get_json()
    table_name = data.get('table_name')
    court_id = data.get('court_id')
    applier_id = data.get('applier_id')

    if not table_name or not court_id or not applier_id:
        return jsonify({'message': 'Missing required fields: table_name, court_id or uploader_id'}), 400

    table_deletes = {
        "Exchangecourt": {
            "table": "Exchangecourt_record",
            "conditions": {
                "Exchange_responser_court_id": court_id,
                "Exchange_responser_id": applier_id
            }
        },
        "Offercourt": {
            "table": "Offercourt_record",
            "conditions": {
                "Offer_uploader_court_id": court_id,
                "Offer_responser_id": applier_id
            }
        },
        "Teamup": {
            "table": "Teamup_request_record",
            "conditions": {
                "Teamup_court_id": court_id,
                "Teamup_requester_id": applier_id
            }
        },
    }

    if table_name not in table_deletes:
        return jsonify({'message': f'Invalid table name: {table_name}'}), 400

    try:
        # 使用封装的delete函数
        deleted = delete(
            table=table_deletes[table_name]["table"],
            conditions=table_deletes[table_name]["conditions"]
        )

        if deleted:
            return jsonify({"status": "success", "message": "Record deleted successfully"}), 200
        else:
            return jsonify({"status": "failure", "message": "No matching records found to delete"}), 404
    except Exception as e:
        return jsonify({"message": "Error occurred while deleting record", "error": str(e)}), 500

@bp.route('/delete_pub', methods=['POST'])
def delete_pub():
    data = request.get_json()
    table_name = data.get('table_name')
    court_id = data.get('court_id')
    puber_id = data.get('puber_id')

    if not table_name or not court_id or not puber_id:
        return jsonify({'message': 'Missing required fields: table_name, court_id or uploader_id'}), 400

    table_deletes = {
        "Exchangecourt": {
            "table": "Exchangecourt_upload",
            "conditions": {
                "Exchange_uploaded_court_id": court_id,
                "Exchange_uploader_id": puber_id
            }
        },
        "Offercourt": {
            "table": "Offercourt_upload",
            "conditions": {
                "Offer_uploaded_court_id": court_id,
                "Offer_uploader_id": puber_id
            }
        },
        "Teamup": {
            "table": "Teamup_upload",
            "conditions": {
                "Teamup_court_id": court_id,
                "Teamup_uploader_id": puber_id
            }
        },
    }

    if table_name not in table_deletes:
        return jsonify({'message': f'Invalid table name: {table_name}'}), 400

    try:
        # 使用封装的delete函数
        deleted = delete(
            table=table_deletes[table_name]["table"],
            conditions=table_deletes[table_name]["conditions"]
        )

        if deleted:
            return jsonify({"status": "success", "message": "Record deleted successfully"}), 200
        else:
            return jsonify({"status": "failure", "message": "No matching records found to delete"}), 404
    except Exception as e:
        return jsonify({"message": "Error occurred while deleting record", "error": str(e)}), 500

@bp.route('/update_req', methods=['POST'])
def update_status():
    data = request.get_json()
    table_name = data.get('table_name')
    court_id = data.get('court_id')
    owner_id = data.get('owner_id')
    status = data.get('status')

    if not table_name or not court_id or status is None:
        return jsonify({'message': 'Missing required fields: table_name, court_id or status'}), 400

    status_mapping = {
        "Exchangecourt": {0: 'retrieved', 1: 'exchanged'},
        "Offercourt": {0: 'retrieved', 1: 'offered'},
        "Teamup": {0: 'retrieved', 1: 'responsed'}
    }
    
    status_value = status_mapping.get(table_name, {}).get(status)
    if status_value is None:
        return jsonify({'message': 'Invalid status value. Must be 0 or 1'}), 400

    table_updates = {
        "Exchangecourt": {
            "table": "Exchangecourt_record",
            "data": {"Exchange_state": status_value},
            "conditions": {
                "Exchange_uploader_court_id": court_id,
                "Exchange_uploader_id": owner_id
            }
        },
        "Offercourt": {
            "table": "Offercourt_record",
            "data": {"Offer_state": status_value},
            "conditions": {
                "Offer_uploader_court_id": court_id,
                "Offer_uploader_id": owner_id
            }
        },
        "Teamup": {
            "table": "Teamup_request_record",
            "data": {"Teamup_request_state": status_value},
            "conditions": {
                "Teamup_court_id": court_id,
                "Teamup_uploader_id": owner_id
            }
        },
    }

    if table_name not in table_updates:
        return jsonify({'message': f'Invalid table name: {table_name}'}), 400

    try:
        # 使用封装的update函数
        updated = update(
            table=table_updates[table_name]["table"],
            data=table_updates[table_name]["data"],
            conditions=table_updates[table_name]["conditions"]
        )

        if updated:
            return jsonify({
                "status": "success",
                "message": f"Status updated to '{status_value}' successfully"
            }), 200
        else:
            return jsonify({
                "status": "failure",
                "message": "No matching records found to update"
            }), 404
    except Exception as e:
        return jsonify({"message": "Error occurred while updating record", "error": str(e)}), 500

@bp.route('/get_available_courts', methods=['POST'])
def get_available_courts():
    data = request.get_json()
    my_id = data.get('my_id')
    
    if not my_id:
        return jsonify({'message': 'Missing my_id parameter'}), 400

    try:
        # 使用封装的select函数
        result = select(
            table="CourtInfo",
            fields=["Court_id"],
            conditions={
                "Court_owner": my_id,
                "Court_id NOT IN": """
                    SELECT Offer_uploaded_court_id FROM Offercourt_upload WHERE Offer_uploaded_court_id IS NOT NULL
                    UNION
                    SELECT Teamup_court_id FROM Teamup_upload WHERE Teamup_court_id IS NOT NULL
                """
            }
        )

        court_ids = [row['Court_id'] for row in result]
        if court_ids:
            return jsonify({'available_courts': court_ids}), 200
        else:
            return jsonify({'message': 'No available courts found for the given owner'}), 404
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching data', 'error': str(e)}), 500