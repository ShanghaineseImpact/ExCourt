from flask import Blueprint, request, jsonify
from execute_for_sql import select, insert  # 导入封装的SQL函数

bp = Blueprint('lost_and_found', __name__, url_prefix='/lost_and_found')

@bp.route('/lost/create', methods=['POST'])
def create_lost_item():
    data = request.get_json()

    # 从请求中获取数据
    lost_uploader_id = data.get('Lost_uploader_id')
    lost_item_name = data.get('Lost_item_name')
    lost_description = data.get('Lost_description')
    lost_position = data.get('Lost_position')
    lost_time = data.get('Lost_time')
    lost_contact = data.get('Lost_contact')
    lost_item_pic_url = data.get('Lost_item_pic_url')

    # 校验必要字段
    if not lost_uploader_id or not lost_item_name or not lost_description or not lost_position or not lost_time:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # 使用封装的insert函数插入数据
        lost_data = {
            'Lost_uploader_id': lost_uploader_id,
            'Lost_item_name': lost_item_name,
            'Lost_description': lost_description,
            'Lost_position': lost_position,
            'Lost_time': lost_time,
            'Lost_contact': lost_contact,
            'Lost_item_pic_url': lost_item_pic_url
        }
        insert(
            table="MyLost",
            data=lost_data
        )
        return jsonify({'message': 'Lost item record created successfully'}), 201

    except Exception as e:
        return jsonify({'message': 'Error occurred while creating lost item record', 'error': str(e)}), 500

@bp.route('/lost/getall', methods=['POST'])
def get_lost_items():
    try:
        # 使用封装的select函数查询所有失物记录
        results = select(
            table="MyLost",
            fields="*"
        )

        # 格式化返回数据
        lost_items = [
            {
                "Lost_id": row['Lost_id'],
                "Lost_uploader_id": row['Lost_uploader_id'],
                "Lost_item_name": row['Lost_item_name'],
                "Lost_description": row['Lost_description'],
                "Lost_position": row['Lost_position'],
                "Lost_time": row['Lost_time'].strftime('%Y-%m-%d %H:%M:%S'),
                "Lost_contact": row['Lost_contact'],
                "Lost_item_pic_url": row['Lost_item_pic_url']
            }
            for row in results
        ]

        return jsonify({"lost_items": lost_items}), 200

    except Exception as e:
        return jsonify({"message": "Error occurred while fetching lost items", "error": str(e)}), 500

@bp.route('/found/create', methods=['POST'])
def create_found_item():
    data = request.get_json()

    # 从请求中获取数据
    found_uploader_id = data.get('Found_uploader_id')
    found_item_name = data.get('Found_item_name')
    found_description = data.get('Found_description')
    found_position = data.get('Found_position')
    found_time = data.get('Found_time')
    found_contact = data.get('Found_contact')
    found_item_pic_url = data.get('Found_item_pic_url')

    # 校验必要字段
    if not found_uploader_id or not found_item_name or not found_description or not found_position or not found_time:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # 使用封装的insert函数插入数据
        found_data = {
            'Found_uploader_id': found_uploader_id,
            'Found_item_name': found_item_name,
            'Found_description': found_description,
            'Found_position': found_position,
            'Found_time': found_time,
            'Found_contact': found_contact,
            'Found_item_pic_url': found_item_pic_url
        }
        insert(
            table="MyFound",
            data=found_data
        )
        return jsonify({'message': 'Found item record created successfully'}), 201

    except Exception as e:
        return jsonify({'message': 'Error occurred while creating found item record', 'error': str(e)}), 500

@bp.route('/found/getall', methods=['GET'])
def get_found_items():
    try:
        # 使用封装的select函数查询所有招领记录
        results = select(
            table="MyFound",
            fields="*"
        )

        # 格式化返回数据
        found_items = [
            {
                "Found_id": row['Found_id'],
                "Found_uploader_id": row['Found_uploader_id'],
                "Found_item_name": row['Found_item_name'],
                "Found_description": row['Found_description'],
                "Found_position": row['Found_position'],
                "Found_time": row['Found_time'].strftime('%Y-%m-%d %H:%M:%S'),
                "Found_contact": row['Found_contact'],
                "Found_item_pic_url": row['Found_item_pic_url']
            }
            for row in results
        ]

        return jsonify({"found_items": found_items}), 200

    except Exception as e:
        return jsonify({"message": "Error occurred while fetching found items", "error": str(e)}), 500