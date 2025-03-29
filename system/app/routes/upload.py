from flask import Blueprint, request, jsonify, send_from_directory
from app import mysql
from flask_cors import CORS
import os
import random
import string
from datetime import datetime
from execute_for_sql import select, insert, update, delete  # 导入你封装的SQL函数

def generate_random_string(length=10):
    # 选择包含的字符（字母和数字）
    characters = string.ascii_letters + string.digits
    # 使用 random.choices 生成指定长度的随机字符串
    return ''.join(random.choices(characters, k=length))

pf_path = 'profiles'
pf_folder = os.path.join(os.getcwd(), pf_path)

QR_path = 'QR'
QR_folder = os.path.join(os.getcwd(), QR_path)

lf_path = 'lostfind'
lf_folder = os.path.join(os.getcwd(), lf_path)

bp = Blueprint('upload', __name__, url_prefix='/upload')

@bp.route('/profile', methods=['POST'])
def upload_profile():
    file = request.files['photo'].stream.read()
    name = request.form['filename']
    folder = pf_path
    file_path = os.path.join(folder, name)
    if not file_exists(name,2):
        with open(file_path, 'wb') as f:
            f.write(file)
        return jsonify({'profileurl': file_path}), 201
    else:
        os.remove(file_path)
        with open(file_path, 'wb') as f:
            f.write(file)
        return jsonify({'profileurl': file_path,'message': 'Profile already updated'}), 201
    
@bp.route('/lostfind', methods=['POST'])
def upload_lostfind():
    file = request.files['photo'].stream.read()
    name = generate_random_string(10) + '.jpg'
    while file_exists_lf(name,2):
        name = generate_random_string(10) + '.jpg'
    folder = lf_path
    file_path = os.path.join(folder, name)
    if not file_exists(name,2):
        with open(file_path, 'wb') as f:
            f.write(file)
        return jsonify({'profilename': name}), 201

def file_exists_lf(name,flag):
    if flag == 1:
        folder = lf_path
        path = os.path.join(folder, name)
        return os.path.isfile(path)
    else:
        folder = lf_path
        path = os.path.join(folder, name)
        return os.path.isfile(path)

def file_exists(name,flag):
    if flag == 1:
        folder = pf_path
        path = os.path.join(folder, name)
        return os.path.isfile(path)
    else:
        folder = pf_path
        path = os.path.join(folder, name)
        return os.path.isfile(path)

@bp.route('/find_profile', methods=['POST'])
def find_profile():
    data = request.get_json()
    stu_id = data.get('student_id')
    if not stu_id:
        return jsonify({'error': 'Missing keyword'}), 400
    # 遍历文件夹寻找匹配的图片
    for filename in os.listdir(pf_folder):
        if stu_id in filename:  # 根据关键字匹配文件名
            image_url = f"http://123.60.86.239:8000/upload/profiles/{filename}"
            return jsonify({'imageUrl': image_url}),200

    # 如果没有找到图片
    return jsonify({'error': 'Image not found'}), 404

@bp.route('/find_code', methods=['POST'])
def find_code():
    data = request.get_json()
    con_id = data.get('con_id')
    if not con_id:
        return jsonify({'error': 'Missing keyword'}), 400
    # 遍历文件夹寻找匹配的图片
    for filename in os.listdir(QR_folder):
        if con_id in filename:  # 根据关键字匹配文件名
            image_url = f"http://123.60.86.239:8000/upload/code/{filename}"
            return jsonify({'imageUrl': image_url}),200

    # 如果没有找到图片
    return jsonify({'error': 'Image not found'}), 404

@bp.route('/find_lost', methods=['POST'])
def get_lost():
    data = request.get_json()

    # 从请求中获取数据
    lost_id = data.get('Lost_id')

    try:
        # 使用封装的select函数替换原始SQL
        result = select(
            table="MyLost",
            fields=["Lost_item_pic_url"],
            conditions={"Lost_id": lost_id},
            fetchone=True
        )
        
        if result and 'Lost_item_pic_url' in result:
            url = result['Lost_item_pic_url']
            
            # 遍历文件夹寻找匹配的图片
            for filename in os.listdir(lf_folder):
                if url in filename:  # 根据关键字匹配文件名
                    image_url = f"http://123.60.86.239:8000/upload/lost/{filename}"
                    return jsonify({'imageUrl': image_url}), 200

            # 如果没有找到图片
            return jsonify({'error': 'Image not found'}), 404
        else:
            return jsonify({'error': 'Record not found'}), 404
            
    except Exception as e:
        return jsonify({"message": "Error occurred while fetching lost items", "error": str(e)}), 500


@bp.route('/profiles/<path:filename>', methods=['GET'])
def get_profile(filename):
    print(filename)
    print(pf_folder)
    return send_from_directory(pf_folder, filename)

@bp.route('/code/<path:filename>', methods=['GET'])
def get_code(filename):
    print(filename)
    print(QR_folder)
    return send_from_directory(QR_folder, filename)

@bp.route('/lost/<path:filename>', methods=['GET'])
def get_lost_pic(filename):
    print(filename)
    print(lf_folder)
    return send_from_directory(lf_folder, filename)