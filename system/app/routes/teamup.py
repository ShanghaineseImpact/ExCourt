from flask import Blueprint, request, jsonify
from app import mysql
from datetime import datetime
from execute_for_sql import select, insert, update  # 导入封装的SQL函数

bp = Blueprint('teamup', __name__, url_prefix='/teamup')

@bp.route('/upload', methods=['POST'])
def register_teamup():
    data = request.get_json()
    student_id = data.get('Student_id')
    court_id = data.get('Court_id')
    max_num = data.get('Max_num')
    if not student_id or not court_id or not max_num:
        return jsonify({'message': 'Missing required fields'}), 400
    try:
        # 1. 使用封装的select函数检查现有上传记录（使用UNION）
        existing_uploads = select(
            table="Exchangecourt_upload",
            fields=["1"],
            conditions={
                "Exchange_uploader_id": student_id,
                "Exchange_uploaded_court_id": court_id
            },
            unions=[
                {
                    "type": "UNION",
                    "table": "Offercourt_upload",
                    "conditions": {
                        "Offer_uploader_id": student_id,
                        "Offer_uploaded_court_id": court_id
                    }
                },
                {
                    "type": "UNION",
                    "table": "Teamup_upload",
                    "conditions": {
                        "Teamup_uploader_id": student_id,
                        "Teamup_court_id": court_id
                    }
                }
            ],
            fetchone=True
        )
        
        if existing_uploads:
            return jsonify({'message': 'This user has already uploaded a request for this court'}), 402
        
        # 2. 插入 Teamup_upload 表
        current_time = datetime.now()
        teamup_data = {
            'Teamup_uploader_id': student_id,
            'Teamup_court_id': court_id,
            'Teamup_max_num': max_num,
            'Teamup_upload_time': current_time,
            'Teamup_upload_state': 'not_responsed'
        }
        operation_id = insert(
            table="Teamup_upload",
            data=teamup_data
        )
        
        # 3. 插入 Operation_record 表
        operation_data = {
            'Operator_id': student_id,
            'Operation_type': 'Teamup_upload',
            'Operation_id': operation_id,
            'Operation_status': 0,
            'Operation_time': current_time
        }
        insert(
            table="Operation_record",
            data=operation_data
        )
        
        return jsonify({'message': 'Teamup registered successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error occurred while registering teamup', 'error': str(e)}), 500
    
@bp.route('/record', methods=['POST'])
def request_teamup():
    data = request.get_json()
    student_id = data.get('Student_id')
    court_id = data.get('Court_id')
    try:
        # 检查是否已存在请求
        existing_request = select(
            table="Teamup_request_record",
            conditions={
                "Teamup_requester_id": student_id,
                "Teamup_court_id": court_id
            },
            fetchone=True
        )
        
        if existing_request:
            return jsonify({'message': '重复发送请求'}), 400
        
        # 获取上传者ID
        teamup_upload = select(
            table="Teamup_upload",
            fields=["Teamup_uploader_id"],
            conditions={"Teamup_court_id": court_id},
            fetchone=True
        )
        
        if teamup_upload:
            uploader_id = teamup_upload['Teamup_uploader_id']
            # 插入请求记录
            request_data = {
                'Teamup_requester_id': student_id,
                'Teamup_court_id': court_id,
                'Teamup_uploader_id': uploader_id,
                'Teamup_request_state': 'not_responsed'
            }
            insert(
                table="Teamup_request_record",
                data=request_data
            )
            return jsonify({'message': 'Teamup request registered successfully', 'status':'success'}), 201
        else:
            return jsonify({'message': 'Court not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error occurred while processing teamup request', 'error': str(e)}), 500

@bp.route('/get_records', methods=['POST'])
def get_teamup_records():
    data = request.get_json()
    student_id = data.get('Student_id')
    try:
        # 获取用户上传的场地ID
        uploads = select(
            table="Teamup_upload",
            fields=["Teamup_court_id"],
            conditions={"Teamup_uploader_id": student_id}
        )
        
        matched_records = []
        if uploads:
            for upload in uploads:
                court_id = upload['Teamup_court_id']
                # 获取每个场地的请求记录
                request_records = select(
                    table="Teamup_request_record",
                    conditions={"Teamup_court_id": court_id}
                )
                if request_records:
                    matched_records.extend(request_records)
        
        if matched_records:
            return jsonify({'data': matched_records, 'status':'success'}), 200
        else:
            return jsonify({'message': 'No matched records found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching records', 'error': str(e)}), 500

@bp.route('/accept', methods=['POST'])
def update_teamup_state():
    data = request.get_json()
    court_id = data.get('Teamup_court_id')
    teamup_requester_id = data.get('Teamup_requester_id')
    if not court_id or not teamup_requester_id:
        return jsonify({'message': 'Court_id and Teamup_requester_id are required'}), 400
    try:
        # 更新请求状态
        updated = update(
            table="Teamup_request_record",
            data={"Teamup_request_state": "responsed"},
            conditions={
                "Teamup_court_id": court_id,
                "Teamup_requester_id": teamup_requester_id
            }
        )
        
        if updated:
            # 获取请求ID
            request_id = select(
                table="Teamup_request_record",
                fields=["Teamup_request_id"],
                conditions={
                    "Teamup_court_id": court_id,
                    "Teamup_requester_id": teamup_requester_id
                },
                fetchone=True
            )['Teamup_request_id']
            
            # 更新操作记录
            update(
                table="operation_record",
                data={"Operation_status": 1},
                conditions={
                    "Operation_id": request_id,
                    "Operator_id": teamup_requester_id,
                    "Operation_type": "Teamup_request"
                }
            )
            
            return jsonify({'message': 'Teamup request state updated successfully', 'status':'success'}), 200
        else:
            return jsonify({'message': 'Teamup request not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error occurred while updating teamup request state', 'error': str(e)}), 500

@bp.route('/refuse', methods=['POST'])
def refuse_teamup_record():
    data = request.get_json()
    court_id = data.get('Teamup_court_id')
    teamup_requester_id = data.get('Teamup_requester_id')
    if not court_id or not teamup_requester_id:
        return jsonify({'message': 'Court_id and Teamup_requester_id are required'}), 400
    try:
        # 更新请求状态
        updated = update(
            table="Teamup_request_record",
            data={"Teamup_request_state": "retrieved"},
            conditions={
                "Teamup_court_id": court_id,
                "Teamup_requester_id": teamup_requester_id
            }
        )
        
        if updated:
            # 获取请求ID
            request_id = select(
                table="Teamup_request_record",
                fields=["Teamup_request_id"],
                conditions={
                    "Teamup_court_id": court_id,
                    "Teamup_requester_id": teamup_requester_id
                },
                fetchone=True
            )['Teamup_request_id']
            
            # 更新操作记录
            update(
                table="operation_record",
                data={"Operation_status": 2},
                conditions={
                    "Operation_id": request_id,
                    "Operator_id": teamup_requester_id,
                    "Operation_type": "Teamup_request"
                }
            )
            
            return jsonify({'message': 'Teamup request state updated successfully', 'status':'success'}), 200
        else:
            return jsonify({'message': 'Teamup request not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error occurred while updating teamup request state', 'error': str(e)}), 500

@bp.route('/get_uploader_id', methods=['POST'])
def get_uploader_id():
    data = request.json
    court_id = data.get('court_id')
    if not court_id:
        return jsonify({"status": "error", "message": "Missing court_id"}), 400
    try:
        result = select(
            table="Teamup_upload",
            fields=["Teamup_uploader_id"],
            conditions={"Teamup_court_id": court_id},
            fetchone=True
        )

        if result:
            return jsonify({"status": "success", "data": {"uploader_id": result['Teamup_uploader_id']}}), 200
        else:
            return jsonify({"status": "error", "message": "No pending offer found for this court"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500