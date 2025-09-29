import requests
import json
import os
import sys
from datetime import datetime
temp_mod_environments_json={}
def temp_mod_environments_json_inti():
    global temp_mod_environments_json
    temp_mod_environments_json={}
def update_temp_mod_environments_json(key , value):
    global temp_mod_environments_json
    temp_mod_environments_json[key] = value
def get_exe_dir():
    """获取exe文件所在目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包的exe，使用exe所在目录
        return os.path.dirname(sys.executable)
    else:
        # 如果是脚本运行，使用当前文件所在目录
        return os.path.dirname(os.path.abspath(__file__))

def get_last_download_file():
    """获取记录最后下载时间的文件路径"""
    return os.path.join(get_exe_dir(), "last_download.txt")

def should_download_from_server():
    """
    检查是否应该从服务器下载数据
    如果本地没有mod_environments.json文件或者距离上次下载已超过一天，则应该下载
    """
    json_file_path = os.path.join(get_exe_dir(), "mod_environments.json")
    
    # 如果本地文件不存在，则需要下载
    if not os.path.exists(json_file_path):
        return True
    
    
    try:
        # 读取最后下载时间
        with open(json_file_path, 'r') as f:
            json_data = json.load(f)
            if  'update_time' in json_data:
                update_time = json_data['update_time']
                today = datetime.now().strftime('%Y%m%d')
                if update_time == today:
                    return False
                else:
                    return True
            else:
                return True
        
    except Exception:
        # 如果读取或解析日期出错，则需要下载
        return True

def download_mod_environments_from_server(server_url):
    """
    从服务器下载mod_environments.json文件
    """
    # 检查是否需要下载
    if not should_download_from_server():
        return True  # 不需要下载，视为成功
    
    try:
        # 从服务器获取数据
        response = requests.get(f"{server_url}/mod_environments")
        
        if response.status_code == 200:
            data = response.json()
            
            # 保存数据到本地文件
            json_file_path = os.path.join(get_exe_dir(), "mod_environments.json")
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print("成功从服务器下载mod环境信息")
            return True
        else:
            print(f"从服务器下载失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"从服务器下载mod环境信息时出错: {e}")
        return False

def sync_mod_environments_with_server(server_url , temp_mod_environments_json):
    """
    将temp_mod_environments_json同步到服务器
    """
    response = requests.post(f"{server_url}/upload", json=temp_mod_environments_json)
        
    if response.status_code == 200:
        print("成功同步mod环境信息到服务器")
        return True
    else:
        print(f"同步失败: {response.json()}")
        return False