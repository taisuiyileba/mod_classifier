from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# 确保保存数据的目录存在
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 确保备份目录存在
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def backup_data():
    """
    备份当前的mod_environments.json文件
    """
    try:
        # 源文件路径
        source_file = os.path.join(DATA_DIR, 'mod_environments.json')
        
        # 检查源文件是否存在
        if not os.path.exists(source_file):
            return
        
        # 创建备份文件名，格式为 mod_environments_YYYYMMDD.json
        today = datetime.now().strftime('%Y%m%d')
        backup_file = os.path.join(BACKUP_DIR, f'mod_environments_{today}.json')
        
        # 复制文件
        with open(source_file, 'r', encoding='utf-8') as src:
            data = json.load(src)
            
        with open(backup_file, 'w', encoding='utf-8') as dst:
            json.dump(data, dst, ensure_ascii=False, indent=2)
        
        # 清理超过30天的备份文件
        cleanup_old_backups()
        
    except Exception as e:
        print(f"备份数据时出错: {e}")

def cleanup_old_backups():
    """
    清理超过30天的备份文件
    """
    try:
        # 计算30天前的日期
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # 遍历备份目录中的所有文件
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith('mod_environments_') and filename.endswith('.json'):
                # 从文件名中提取日期
                try:
                    date_str = filename[18:26]  # 提取 YYYYMMDD 部分
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                    
                    # 如果文件日期早于截止日期，则删除文件
                    if file_date < cutoff_date:
                        file_path = os.path.join(BACKUP_DIR, filename)
                        os.remove(file_path)
                except ValueError:
                    # 如果无法解析日期，则跳过该文件
                    continue
                    
    except Exception as e:
        print(f"清理旧备份时出错: {e}")

def should_backup_today():
    """
    检查今天是否需要备份（根据是否存在今天的备份文件）
    """
    today = datetime.now().strftime('%Y%m%d')
    backup_file = os.path.join(BACKUP_DIR, f'mod_environments_{today}.json')
    return not os.path.exists(backup_file)

@app.route('/upload', methods=['POST'])
def upload_mod_environments():
    """
    接收客户端上传的mod_environments.json数据
    """
    try:
        # 获取上传的JSON数据
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 保存数据到文件
        file_path = os.path.join(DATA_DIR, 'mod_environments.json')
        
        # 如果文件已存在，则合并数据
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # 合并数据，新数据覆盖旧数据
            existing_data.update(data)
            combined_data = existing_data
            today = datetime.now().strftime('%Y%m%d')
            combined_data['update_time'] = today
        else:
            combined_data = data
        
        # 保存合并后的数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
            
        
        # 检查是否需要备份，如果需要则执行备份
        if should_backup_today():
            backup_data()
        
        return jsonify({'message': 'Data uploaded successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mod_environments', methods=['GET'])
def get_mod_environments():
    """
    返回所有mod环境信息
    """
    try:
        file_path = os.path.join(DATA_DIR, 'mod_environments.json')
        
        if not os.path.exists(file_path):
            return jsonify({}), 200
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mod_environment/<modid>', methods=['GET'])
def get_mod_environment(modid):
    """
    根据modid返回特定mod的环境信息
    """
    try:
        file_path = os.path.join(DATA_DIR, 'mod_environments.json')
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'No data available'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if modid in data:
            return jsonify({modid: data[modid]}), 200
        else:
            return jsonify({'error': f'Mod {modid} not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/backup', methods=['POST'])
def manual_backup():
    """
    手动触发备份
    """
    try:
        backup_data()
        return jsonify({'message': 'Backup completed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)