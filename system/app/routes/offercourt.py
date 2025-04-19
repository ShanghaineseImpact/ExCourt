from flask import Blueprint, request, jsonify
from datetime import datetime
from .execute_for_sql import select, insert, update  # 导入封装的SQL函数

bp = Blueprint('offercourt', __name__, url_prefix='/offercourt')

@bp.route('/upload', methods=['POST'])
def offer_court():
    data = request.json
    my_id = data.get('my_id')
    court_id = data.get('court_id')
    upload_time = data.get('upload_time', datetime.now())

    if not my_id or not court_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        # 1. 检查是否已存在相同的上传请求（使用UNION）
        existing_uploads = select(
            table="Exchangecourt_upload",
            fields=["1"],
            conditions={
                "Exchange_uploader_id": my_id,
                "Exchange_uploaded_court_id": court_id
            },
            unions=[
                {
                    "type": "UNION",
                    "table": "Offercourt_upload",
                    "conditions": {
                        "Offer_uploader_id": my_id,
                        "Offer_uploaded_court_id": court_id
                    }
                },
                {
                    "type": "UNION",
                    "table": "Teamup_upload",
                    "conditions": {
                        "Teamup_uploader_id": my_id,
                        "Teamup_court_id": court_id
                    }
                }
            ],
            fetchone=True
        )

        if existing_uploads:
            return jsonify({'status': 'error', 'message': 'This user has already uploaded a request for this court'}), 402

        # 2. 插入 Offercourt_upload 表
        offer_data = {
            'Offer_uploader_id': my_id,
            'Offer_uploaded_court_id': court_id,
            'Offer_upload_time': upload_time,
            'Offer_upload_state': 'not_responsed'
        }
        offer_upload_id = insert(
            table="Offercourt_upload",
            data=offer_data
        )

        # 3. 插入 Operation_record 表
        operation_data = {
            'Operator_id': my_id,
            'Operation_type': 'Offercourt_upload',
            'Operation_id': offer_upload_id,
            'Operation_status': 0,
            'Operation_time': upload_time
        }
        insert(
            table="Operation_record",
            data=operation_data
        )

        return jsonify({
            "status": "success", 
            "message": "送场发布成功", 
            "data": {"Offer_upload_id": offer_upload_id}
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/record', methods=['POST'])
def accept_court():
    data = request.json
    my_id = data.get('my_id')
    court_id = data.get('court_id')
    upload_time = data.get('upload_time', datetime.now())

    if not my_id or not court_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        # 查找匹配的送场记录
        offer_upload = select(
            table="Offercourt_upload",
            fields=["Offer_uploader_id"],
            conditions={
                "Offer_uploaded_court_id": court_id,
                "offer_upload_state IN": ["not_responsed", "responsed"]
            },
            fetchone=True
        )

        if not offer_upload:
            return jsonify({"status": "error", "message": "No pending offer found for this court"}), 404

        offer_uploader_id = offer_upload['Offer_uploader_id']

        # 检查是否已存在相同的记录
        existing_record = select(
            table="Offercourt_record",
            fields=["COUNT(*)"],
            conditions={
                "Offer_uploader_id": offer_uploader_id,
                "Offer_responser_id": my_id,
                "Offer_uploader_court_id": court_id,
                "Offer_state != ": "retrieved"
            },
            fetchone=True
        )

        if existing_record['COUNT(*)'] > 0:
            return jsonify({"status": "error", "message": "已经存在相同的送场记录"}), 409

        # 插入 Offercourt_record 记录
        record_data = {
            'Offer_uploader_id': offer_uploader_id,
            'Offer_responser_id': my_id,
            'Offer_state': 'not_responsed',
            'Offer_uploader_court_id': court_id
        }
        accept_record_id = insert(
            table="Offercourt_record",
            data=record_data
        )

        # 更新 Offercourt_upload 状态
        update(
            table="Offercourt_upload",
            data={"Offer_upload_state": "responsed"},
            conditions={
                "Offer_uploaded_court_id": court_id,
                "Offer_uploader_id": offer_uploader_id
            }
        )

        # 插入 Operation_record 记录
        operation_data = {
            'Operator_id': my_id,
            'Operation_type': 'Request_court',
            'Operation_id': accept_record_id,
            'Operation_status': 0,
            'Operation_time': upload_time
        }
        insert(
            table="Operation_record",
            data=operation_data
        )

        return jsonify({
            "status": "success", 
            "message": "送场接受成功", 
            "data": {"Accept_record_id": accept_record_id}
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/accept', methods=['POST'])
def accept_offer():
    data = request.json
    my_id = data.get('my_id')
    court_id = data.get('court_id')
    recorder_id = data.get('recorder_id')

    if not my_id or not court_id or not recorder_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        # 查找匹配的送场记录
        record = select(
            table="Offercourt_record",
            fields=["Offer_record_id"],
            conditions={
                "Offer_uploader_id": my_id,
                "Offer_responser_id": recorder_id,
                "Offer_uploader_court_id": court_id
            },
            fetchone=True
        )

        if not record:
            return jsonify({"status": "error", "message": "没有找到匹配的记录"}), 404

        offer_record_id = record['Offer_record_id']

        # 更新 Offercourt_record 表
        update(
            table="Offercourt_record",
            data={"Offer_state": "offered"},
            conditions={"Offer_record_id": offer_record_id}
        )

        # 更新 Operation_record 记录
        update(
            table="Operation_record",
            data={"Operation_status": 1},
            conditions={
                "Operation_id": offer_record_id,
                "Operation_type": "Request_court",
                "Operator_id": recorder_id
            }
        )

        return jsonify({"status": "success", "message": "送场接受成功"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/decline', methods=['POST'])
def decline_offer():
    data = request.json
    my_id = data.get('my_id')
    court_id = data.get('court_id')
    recorder_id = data.get('recorder_id')

    if not my_id or not court_id or not recorder_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        # 查找匹配的送场记录
        record = select(
            table="Offercourt_record",
            fields=["Offer_record_id"],
            conditions={
                "Offer_uploader_id": my_id,
                "Offer_responser_id": recorder_id,
                "Offer_uploader_court_id": court_id
            },
            fetchone=True
        )

        if not record:
            return jsonify({"status": "error", "message": "没有找到匹配的记录"}), 404

        offer_record_id = record['Offer_record_id']

        # 更新 Offercourt_record 表
        update(
            table="Offercourt_record",
            data={"Offer_state": "retrieved"},
            conditions={"Offer_record_id": offer_record_id}
        )

        # 更新 Operation_record 记录
        update(
            table="Operation_record",
            data={"Operation_status": 2},
            conditions={
                "Operation_id": offer_record_id,
                "Operation_type": "Request_court",
                "Operator_id": recorder_id
            }
        )

        return jsonify({"status": "success", "message": "送场请求已拒绝"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/get_offer_records', methods=['POST'])
def get_all_records():
    data = request.json
    my_id = data.get('my_id')

    if not my_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        # 查询 Offercourt_record 表
        records = select(
            table="Offercourt_record",
            fields=[
                "Offer_record_id", 
                "Offer_responser_id", 
                "Offer_state", 
                "Offer_uploader_court_id"
            ],
            conditions={"Offer_uploader_id": my_id}
        )

        if not records:
            return jsonify({"status": "success", "message": "没有找到记录", "data": []}), 200

        # 获取所有响应者ID
        responser_ids = [record['Offer_responser_id'] for record in records]

        # 查询学生信息
        students_info = select(
            table="Student",
            fields=[
                "Student_id", "Student_name", "Student_profileurl", 
                "Student_nickname", "Student_credit", "Student_level", 
                "Student_status"
            ],
            conditions={"Student_id IN": responser_ids}
        )

        # 构建学生信息字典
        students_dict = {student['Student_id']: student for student in students_info}
        
        # 丰富记录信息
        enriched_records = []
        for record in records:
            student_info = students_dict.get(record['Offer_responser_id'])
            if student_info:
                enriched_record = {
                    'Offer_record_id': record['Offer_record_id'],
                    'Offer_responser_id': record['Offer_responser_id'],
                    'Offer_state': record['Offer_state'],
                    'Offer_uploader_court_id': record['Offer_uploader_court_id'],
                    'Student_name': student_info['Student_name'],
                    'Student_profileurl': student_info['Student_profileurl'],
                    'Student_nickname': student_info['Student_nickname'],
                    'Student_credit': student_info['Student_credit'],
                    'Student_level': student_info['Student_level'],
                    'Student_status': student_info['Student_status']
                }
                enriched_records.append(enriched_record)

        return jsonify({
            "status": "success", 
            "message": "获取记录成功", 
            "data": enriched_records
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/get_uploader_id', methods=['POST'])
def get_uploader_id():
    data = request.json
    court_id = data.get('court_id')

    if not court_id:
        return jsonify({"status": "error", "message": "Missing court_id"}), 400

    try:
        result = select(
            table="Offercourt_upload",
            fields=["Offer_uploader_id"],
            conditions={"Offer_uploaded_court_id": court_id},
            fetchone=True
        )

        if result:
            return jsonify({
                "status": "success", 
                "data": {"uploader_id": result['Offer_uploader_id']}
            }), 200
        else:
            return jsonify({
                "status": "error", 
                "message": "No pending offer found for this court"
            }), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500