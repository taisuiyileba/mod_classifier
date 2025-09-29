import hashlib
import requests
import json
import zipfile
import urllib.request
import urllib.error
import re
import os
from .name_normalizer import NameNormalizer
from bs4 import BeautifulSoup

class ModProcessor:
    def __init__(self):
        self.normalizer = NameNormalizer()
        pass
    
    def get_toml_value(self, key, content):
        """
        从toml文件中获取指定键的值
        """
        # 简单提取value
        if key in content:
            start = content.find(key) + len(key)
            # 找到等号后跳过空格和等号
            while start < len(content) and content[start] in [' ', '=']:
                start += 1
            
            # 确定值的开始和结束位置
            if start < len(content):
                # 如果是引号开头，则找到下一个引号
                if content[start] in ['"', "'"]:
                    quote_char = content[start]
                    start += 1
                    end = content.find(quote_char, start)
                else:
                    # 非引号值，找到下一个空格、换行或行结束符
                    end = start
                    while end < len(content) and content[end] not in [' ', '\n', '\r', '#', ',']:
                        end += 1
            
            if start < len(content) and end > start:
                value = content[start:end].strip()
                return value

    def get_mod_info(self, mod_file_path):
        """
        从mod文件中提取信息
        """
        try:
            with zipfile.ZipFile(mod_file_path, 'r') as zf:
                # 尝试读取mcmod.info文件
                if 'mcmod.info' in zf.namelist():
                    with zf.open('mcmod.info') as f:
                        content = f.read().decode('utf-8')
                        # 简单提取modid，实际应用中可能需要解析JSON
                        if '"modid"' in content:
                            start = content.find('"modid"') + 9
                            end = content.find('"', start)
                            modid = content[start:end]
                            print(f"modid: {modid}")
                            return modid, modid
                # 尝试读取fabric.mod.json文件
                elif 'fabric.mod.json' in zf.namelist():
                    with zf.open('fabric.mod.json') as f:
                        data = json.load(f)
                        modid = data.get('id')
                        name = data.get('name')
                        return modid, name
                # 尝试读取quilt.mod.json文件
                elif 'quilt.mod.json' in zf.namelist():
                    with zf.open('quilt.mod.json') as f:
                        data = json.load(f)
                        # Quilt mod的id在quilt_loader.id字段中
                        modid = data.get('quilt_loader', {}).get('id')
                        # Quilt mod的name在quilt_loader.metadata.name字段中
                        name = data.get('quilt_loader', {}).get('metadata', {}).get('name')
                        return modid, name
                # 尝试读取mods.toml文件 (Forge 1.13+)
                elif 'META-INF/mods.toml' in zf.namelist():
                    with zf.open('META-INF/mods.toml') as f:
                        content = f.read().decode('utf-8')
                        modid = self.get_toml_value('modId', content)
                        displayName = self.get_toml_value('displayName', content)
                        return modid, displayName
                # 尝试读取neoforge.mods文件
                elif 'META-INF/neoforge.mods.toml' in zf.namelist():
                    with zf.open('META-INF/neoforge.mods.toml') as f:
                        content = f.read().decode('utf-8')
                        modid = self.get_toml_value('modId', content)
                        displayName = self.get_toml_value('displayName', content)
                        return modid, displayName   
        except Exception as e:
            print(f"读取 {mod_file_path} 时出错: {e}")
        
        # 如果无法从文件中提取信息，使用文件名作为备选方案
        filename = os.path.basename(mod_file_path)
        modid = self.normalizer.normalize_mod_name(filename)
        return modid, modid

    def get_file_sha1(self, file_path):
        """
        计算文件的SHA1哈希值
        """
        sha1 = hashlib.sha1()
        try:
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(65536)
                    if not data:
                        break
                    sha1.update(data)
            return sha1.hexdigest()
        except Exception as e:
            print(f"计算文件SHA1时出错: {e}")
            return None

    def lookup_modrinth_server_support(self, file_path):
        """
        根据mod文件查找其在Modrinth上的服务端支持环境
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return None
            
        if not os.path.isfile(file_path):
            return None
        
        # 只处理.jar文件
        if not file_path.lower().endswith('.jar'):
            return None
        
        # 计算文件SHA1哈希值
        file_hash = self.get_file_sha1(file_path)
        if not file_hash:
            return None
        
        # 调用Modrinth API查找版本信息
        try:
            url = f"https://api.modrinth.com/v2/version_file/{file_hash}"
            headers = {
                'User-Agent': 'PCL2-Modrinth-Lookup/1.0 (Python)'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return None
                
            response.raise_for_status()
            
            version_info = response.json()
            project_id = version_info['project_id']
            
            # 获取项目详细信息
            project_url = f"https://api.modrinth.com/v2/project/{project_id}"
            project_response = requests.get(project_url, headers=headers)
            project_response.raise_for_status()
            
            project_info = project_response.json()
            
            # 返回服务端支持信息
            result = {
                'file_name': os.path.basename(file_path),
                'project_title': project_info['title'],
                'project_id': project_id,
                'client_side': project_info.get('client_side', 'unknown'),
                'server_side': project_info.get('server_side', 'unknown'),
                'loaders': project_info.get('loaders', []),
                'game_versions': project_info.get('game_versions', [])
            }
            
            return result
            
        except Exception:
            return None

    def get_mcmod_server_support(self, wiki_id):
        """
        获取MC百科中模组的服务端支持环境
        """
        try:
            url = f"https://www.mcmod.cn/class/{wiki_id}.html"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req, timeout=10)
            content = response.read().decode('utf-8')
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找包含运行环境信息的元素
            # 根据用户提供的信息查找<li class="col-lg-4" style="user-select: auto;">运行环境: 客户端需装, 服务端需装</li>
            elements = soup.find_all('li', class_='col-lg-4')
            
            for element in elements:
                if '运行环境:' in element.get_text():
                    env_text = element.get_text().strip()
                    return env_text
                    
            return "未找到运行环境信息"
        except urllib.error.URLError as e:
            return f"网络错误: {e}"
        except Exception as e:
            return f"解析错误: {e}"