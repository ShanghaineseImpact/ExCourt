from flask import Blueprint, request, jsonify
from datetime import datetime
from execute_for_sql import select, insert, update  # 导入封装的SQL函数
import os

bp = Blueprint('chat', __name__, url_prefix='/chat')

# 发送消息
@bp.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()

    # 获取发送者和接收者信息
    sender_id = data.get('Sender_id')
    receiver_id = data.get('Receiver_id')
    message_sent = data.get('Message_sent', '')
    message_type = data.get('Message_type', 'text')
    pic_url = data.get('Pic_url', None)
    message_time = datetime.now()

    if not sender_id or not receiver_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # 插入消息记录
        message_data = {
            'Sender_id': sender_id,
            'Receiver_id': receiver_id,
            'Message_sent': message_sent,
            'Message_type': message_type,
            'Pic_url': pic_url,
            'Message_time': message_time,
            'Is_read': 0,
            'Is_deleted': 0
        }
        insert('ConversationInfo', message_data)

        # 实时通知接收者
        socketio.emit('new_message', {
            "Sender_id": sender_id,
            "Receiver_id": receiver_id,
            "Message_sent": message_sent,
            "Message_type": message_type,
            "Pic_url": pic_url,
            "Message_time": message_time.strftime('%Y-%m-%d %H:%M:%S')
        }, room=f"user_{receiver_id}")

        return jsonify({'message': 'Message sent successfully', "status": 'success'}), 201
    except Exception as e:
        return jsonify({'message': 'Error occurred while sending message', 'error': str(e)}), 500

QR_path = 'QR'
QR_folder = os.path.join(os.getcwd(), QR_path)

# 发送图片消息
@bp.route('/sendphoto', methods=['POST'])
def send_photo():
    file = request.files['photo'].stream.read()
    sender_id = request.form['Sender_id']
    receiver_id = request.form['Receiver_id']
    message_sent = ''
    message_type = 'image'
    message_time = datetime.now()

    if not sender_id or not receiver_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # 插入消息记录
        message_data = {
            'Sender_id': sender_id,
            'Receiver_id': receiver_id,
            'Message_sent': message_sent,
            'Message_type': message_type,
            'Pic_url': '',
            'Message_time': message_time,
            'Is_read': 0,
            'Is_deleted': 0
        }
        insert('ConversationInfo', message_data)

        # 获取最新消息ID
        latest_message = select(
            table="ConversationInfo",
            fields="*",
            conditions={
                "OR": [
                    {"Sender_id": sender_id, "Receiver_id": receiver_id},
                    {"Sender_id": receiver_id, "Receiver_id": sender_id}
                ]
            },
            order_by="Message_time DESC",
            limit=1,
            fetchone=True
        )

        Conversation_id = latest_message['Conversation_id']
        file_path = os.path.join(QR_folder, f"{Conversation_id}.jpg")
        with open(file_path, 'wb') as f:
            f.write(file)

        # 更新图片URL
        update(
            table="ConversationInfo",
            data={"Pic_url": file_path},
            conditions={"Conversation_id": Conversation_id}
        )

        return jsonify({'profileurl': file_path, 'message': 'Message sent successfully', "status": 'success'}), 201
    except Exception as e:
        return jsonify({'message': 'Error occurred while sending message', 'error': str(e)}), 500

@bp.route('/history', methods=['POST'])
def get_chat_history():
    data = request.get_json()
    user_id = data.get('user_id')
    contact_id = data.get('contact_id')
    page = int(data.get('page', 1))
    limit = int(data.get('limit', 20))
    offset = (page - 1) * limit

    if not user_id or not contact_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # 获取聊天记录
        messages = select(
            table="ConversationInfo",
            fields="*",
            conditions={
                "OR": [
                    {"Sender_id": user_id, "Receiver_id": contact_id},
                    {"Sender_id": contact_id, "Receiver_id": user_id}
                ]
            },
            order_by="Message_time ASC",
            limit=limit,
            offset=offset
        )

        return jsonify({
            "status": "success",
            "message": "Chat history fetched successfully",
            "data": messages
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching chat history', 'error': str(e)}), 500

# 标记消息为已读
@bp.route('/mark_as_read', methods=['POST'])
def mark_as_read():
    data = request.get_json()
    user_id = data.get('user_id')
    contact_id = data.get('contact_id')

    if not user_id or not contact_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # 更新未读消息为已读
        updated = update(
            table="ConversationInfo",
            data={"Is_read": 1},
            conditions={
                "Sender_id": contact_id,
                "Receiver_id": user_id,
                "Is_read": 0
            }
        )

        return jsonify({'message': 'Messages marked as read successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while marking messages as read', 'error': str(e)}), 500

# 获取未读消息数量
@bp.route('/unread_count', methods=['GET'])
def get_unread_count():
    data = request.get_json()
    user_id = data.get('student_id')

    if not user_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # 查询未读消息数量
        unread_counts = select(
            table="ConversationInfo",
            fields=["Sender_id", "COUNT(*) as unread_count"],
            conditions={"Receiver_id": user_id, "Is_read": 0},
            group_by="Sender_id"
        )

        return jsonify(unread_counts), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching unread counts', 'error': str(e)}), 500

# 获取所有有过聊天记录的学生信息
@bp.route('/contacts', methods=['POST'])
def get_chat_contacts():
    data = request.get_json()
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'message': '缺少必要的参数: student_id'}), 400

    try:
        # 查询与当前学生有聊天记录的所有学生的基本信息
        contacts = select(
            table="ConversationInfo c JOIN Student s ON (c.Sender_id = s.Student_id AND c.Receiver_id = %s) OR (c.Receiver_id = s.Student_id AND c.Sender_id = %s)",
            fields=[
                "DISTINCT s.Student_id",
                "s.Student_name",
                "s.Student_nickname",
                "s.Student_profileurl"
            ],
            params=(student_id, student_id)
        )

        # 格式化结果
        contact_list = [
            {
                "student_id": contact["Student_id"],
                "name": contact["Student_name"],
                "nickname": contact["Student_nickname"],
                "profile_url": contact["Student_profileurl"]
            }
            for contact in contacts
        ]

        return jsonify({
            "status": "success",
            "message": "获取聊天联系人成功",
            "data": contact_list
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching chat contacts', 'error': str(e)}), 500

# WebSocket 事件
@socketio.on('connect')
def handle_connect():
    print("A user connected.")

@socketio.on('join')
def handle_join(data):
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        join_room(room)
        print(f"User {user_id} joined room {room}")