from flask import Blueprint, request, jsonify
from .execute_for_sql import select, insert, delete  # 导入封装的SQL函数

bp = Blueprint('friend', __name__, url_prefix='/friend')

@bp.route('/add', methods=['POST'])
def add_friend():
    data = request.json
    my_id = data.get('my_id')
    search_id = data.get('search_id')

    if not my_id or not search_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        # 检查是否已经是好友
        existing_friend = select(
            table="Friend",
            fields=["COUNT(*)"],
            conditions={
                "OR": [
                    {"Friend_a_id": my_id, "Friend_b_id": search_id},
                    {"Friend_a_id": search_id, "Friend_b_id": my_id}
                ]
            },
            fetchone=True
        )

        if existing_friend['COUNT(*)'] > 0:
            return jsonify({"status": "error", "message": "已经是好友"}), 400

        # 添加好友
        insert(
            table="Friend",
            data={
                "Friend_a_id": my_id,
                "Friend_b_id": search_id
            }
        )

        return jsonify({"status": "success", "message": "好友添加成功"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/delete', methods=['POST'])
def delete_friend():
    data = request.json
    my_id = data.get('my_id')
    search_id = data.get('search_id')

    if not my_id or not search_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        # 删除好友
        deleted = delete(
            table="Friend",
            conditions={
                "OR": [
                    {"Friend_a_id": my_id, "Friend_b_id": search_id},
                    {"Friend_a_id": search_id, "Friend_b_id": my_id}
                ]
            }
        )

        if deleted:
            return jsonify({"status": "success", "message": "好友删除成功"}), 200
        else:
            return jsonify({"status": "error", "message": "好友关系不存在"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/getall', methods=['POST'])
def get_all_friends():
    data = request.json
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        # 查询好友的详细信息
        friends = select(
            table="Friend f JOIN Student s ON (f.Friend_a_id = s.Student_id AND f.Friend_b_id = %s) OR (f.Friend_b_id = s.Student_id AND f.Friend_a_id = %s)",
            fields=[
                "s.Student_id", 
                "s.Student_name", 
                "s.Student_profileurl", 
                "s.Student_nickname"
            ],
            params=(student_id, student_id)
        )

        # 格式化结果
        friend_list = [
            {
                "student_id": friend['Student_id'],
                "name": friend['Student_name'],
                "profile_url": friend['Student_profileurl'],
                "nickname": friend['Student_nickname']
            }
            for friend in friends
        ]

        return jsonify({
            "status": "success",
            "message": "获取好友列表成功",
            "data": friend_list
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500