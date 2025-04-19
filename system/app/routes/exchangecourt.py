from flask import Blueprint, request, jsonify
from datetime import datetime
from .execute_for_sql import select, insert, update

bp = Blueprint('exchangecourt', __name__, url_prefix='/exchangecourt')

@bp.route('/upload', methods=['POST'])
def add_exchange_upload_and_operation_record():
    data = request.get_json()
    exchange_uploader_id = data.get('Exchange_uploader_id')
    exchange_uploaded_court_id = data.get('Exchange_uploaded_court_id')
    
    if not exchange_uploader_id or not exchange_uploaded_court_id:
        return jsonify({'message': 'Missing required fields'}), 400
    
    current_time = datetime.now()
    
    try:
        # 1. 检查重复上传请求
        check_result = select(
            table="Exchangecourt_upload",
            fields="1",
            conditions={
                "Exchange_uploader_id": exchange_uploader_id,
                "Exchange_uploaded_court_id": exchange_uploaded_court_id
            },
            unions=[
                {
                    "type": "UNION",
                    "table": "Offercourt_upload",
                    "conditions": {
                        "Offer_uploader_id": exchange_uploader_id,
                        "Offer_uploaded_court_id": exchange_uploaded_court_id
                    }
                },
                {
                    "type": "UNION",
                    "table": "Teamup_upload",
                    "conditions": {
                        "Teamup_uploader_id": exchange_uploader_id,
                        "Teamup_court_id": exchange_uploaded_court_id
                    }
                }
            ]
        )
        if check_result and len(check_result) > 0:
            return jsonify({'message': 'This user has already uploaded a request for this court'}), 402
        
        # 2. 插入Exchangecourt_upload
        upload_data = {
            'Exchange_uploader_id': exchange_uploader_id,
            'Exchange_upload_state': 'not_responsed',
            'Exchange_uploaded_court_id': exchange_uploaded_court_id,
            'Exchange_upload_time': current_time
        }
        upload_id = insert('Exchangecourt_upload', upload_data)
        
        # 3. 插入Operation_record
        operation_data = {
            'Operator_id': exchange_uploader_id,
            'Operation_type': 'Exchangecourt_upload',
            'Operation_id': upload_id,
            'Operation_status': 0,
            'Operation_time': current_time
        }
        insert('Operation_record', operation_data)
        
        return jsonify({'message': 'Exchange upload and operation record added successfully'}), 201
    
    except Exception as e:
        return jsonify({'message': 'Error occurred: ' + str(e)}), 500

@bp.route('/respond', methods=['POST'])
def respond_to_exchange():
    data = request.get_json()
    exchange_responser_id = data.get('Exchange_responser_id')
    exchange_uploader_court_id = data.get('Exchange_uploader_court_id')
    exchange_responser_court_id = data.get('Exchange_responser_court_id')
    
    if not all([exchange_responser_id, exchange_uploader_court_id, exchange_responser_court_id]):
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        # 获取发布者ID
        uploader_result = select(
            table="Exchangecourt_upload",
            fields=["Exchange_uploader_id"],
            conditions={"Exchange_uploaded_court_id": exchange_uploader_court_id},
            fetchone=True
        )
        if not uploader_result:
            return jsonify({'message': 'No exchange uploader found'}), 404
        exchange_uploader_id = uploader_result['Exchange_uploader_id']
        
        # 检查重复请求
        offer_exists = select(
            table="Offercourt_upload",
            fields="1",
            conditions={
                "Offer_uploader_id": exchange_responser_id,
                "Offer_uploaded_court_id": exchange_responser_court_id
            }
        )
        teamup_exists = select(
            table="Teamup_upload",
            fields="1",
            conditions={
                "Teamup_uploader_id": exchange_responser_id,
                "Teamup_court_id": exchange_responser_court_id
            }
        )
        if offer_exists or teamup_exists:
            return jsonify({'message': 'Duplicate upload request found'}), 402
        
        # 检查并插入Exchangecourt_upload
        exchange_exists = select(
            table="Exchangecourt_upload",
            conditions={
                "Exchange_uploader_id": exchange_uploader_id,
                "Exchange_uploaded_court_id": exchange_uploader_court_id
            }
        )
        if not exchange_exists:
            insert_data = {
                'Exchange_uploader_id': exchange_uploader_id,
                'Exchange_uploaded_court_id': exchange_uploader_court_id,
                'Exchange_upload_state': 'not_responsed',
                'Exchange_upload_time': datetime.now()
            }
            insert('Exchangecourt_upload', insert_data)
        
        # 插入Exchangecourt_record
        record_data = {
            'Exchange_uploader_id': exchange_uploader_id,
            'Exchange_responser_id': exchange_responser_id,
            'Exchange_uploader_court_id': exchange_uploader_court_id,
            'Exchange_responser_court_id': exchange_responser_court_id,
            'Exchange_state': 'not_responsed'
        }
        record_id = insert('Exchangecourt_record', record_data)
        
        # 插入Operation_record
        operation_data = {
            'Operator_id': exchange_responser_id,
            'Operation_type': 'Exchangecourt_record',
            'Operation_id': record_id,
            'Operation_status': 0,
            'Operation_time': datetime.now()
        }
        insert('Operation_record', operation_data)
        
        return jsonify({'message': 'Response recorded successfully'}), 201
    
    except Exception as e:
        return jsonify({'message': 'Error occurred: ' + str(e)}), 500

@bp.route('/get_response_records_by_student', methods=['POST'])
def get_response_records_by_student():
    data = request.get_json()
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        results = select(
            table="Exchangecourt_record er",
            fields=[
                "er.Exchange_record_id", "er.Exchange_state",
                "er.Exchange_uploader_court_id", "er.Exchange_responser_court_id",
                "er.Exchange_uploader_score", "er.Exchange_responser_score",
                "er.Exchange_responser_id",
                "s.Student_name", "s.Student_profileurl",
                "s.Student_nickname", "s.Student_credit", "s.Student_level"
            ],
            joins=[("JOIN Student s ON er.Exchange_responser_id = s.Student_id", None)],
            conditions={"er.Exchange_uploader_id": student_id}
        )
        
        records = [{
            'exchange_record_id': row['Exchange_record_id'],
            'exchange_state': row['Exchange_state'],
            'exchange_uploader_court_id': row['Exchange_uploader_court_id'],
            'exchange_responser_court_id': row['Exchange_responser_court_id'],
            'exchange_uploader_score': row['Exchange_uploader_score'],
            'exchange_responser_score': row['Exchange_responser_score'],
            'exchange_responser_id': row['Exchange_responser_id'],
            'responser_info': {
                'name': row['Student_name'],
                'profileurl': row['Student_profileurl'],
                'nickname': row['Student_nickname'],
                'credit': row['Student_credit'],
                'level': row['Student_level']
            }
        } for row in results]
        
        return jsonify({'data': records, 'status': 'success'}), 200
    
    except Exception as e:
        return jsonify({'message': 'Error occurred: ' + str(e)}), 500

@bp.route('/complete_exchange', methods=['POST'])
def complete_exchange():
    data = request.get_json()
    required_fields = [
        'Exchange_uploader_court_id',
        'Exchange_responser_court_id',
        'Exchange_uploader_id',
        'Exchange_responser_id'
    ]
    if not all(data.get(field) for field in required_fields):
        return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400
    
    try:
        # 更新Exchangecourt_record
        record_updated = update(
            table='Exchangecourt_record',
            data={'Exchange_state': 'exchanged'},
            conditions={
                'Exchange_uploader_court_id': data['Exchange_uploader_court_id'],
                'Exchange_responser_court_id': data['Exchange_responser_court_id'],
                'Exchange_uploader_id': data['Exchange_uploader_id'],
                'Exchange_responser_id': data['Exchange_responser_id']
            }
        )
        if not record_updated:
            return jsonify({'status': 'error', 'message': '未找到交换记录'}), 404
        
        # 更新Exchangecourt_upload
        upload_updated = update(
            table='Exchangecourt_upload',
            data={'Exchange_upload_state': 'exchanged'},
            conditions={
                'Exchange_uploaded_court_id': data['Exchange_uploader_court_id'],
                'Exchange_uploader_id': data['Exchange_uploader_id']
            }
        )
        if not upload_updated:
            return jsonify({'status': 'error', 'message': '未找到上传记录'}), 404
        
        return jsonify({'status': 'success', 'message': '操作成功'}), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/refuse', methods=['POST'])
def refuse_exchange():
    data = request.get_json()
    required_fields = [
        'Exchange_uploader_court_id',
        'Exchange_responser_court_id',
        'Exchange_uploader_id',
        'Exchange_responser_id'
    ]
    if not all(data.get(field) for field in required_fields):
        return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400
    
    try:
        updated = update(
            table='Exchangecourt_record',
            data={'Exchange_state': 'retrieved'},
            conditions={
                'Exchange_uploader_court_id': data['Exchange_uploader_court_id'],
                'Exchange_responser_court_id': data['Exchange_responser_court_id'],
                'Exchange_uploader_id': data['Exchange_uploader_id'],
                'Exchange_responser_id': data['Exchange_responser_id']
            }
        )
        if not updated:
            return jsonify({'status': 'error', 'message': '未找到记录'}), 404
        
        return jsonify({'status': 'success', 'message': '操作成功'}), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500