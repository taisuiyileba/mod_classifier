from .mod_processor import ModProcessor
from .mod_searcher import ModSearcher
import json
import os
import sys
from .config import get_moddata_path
from .server_communicator import update_temp_mod_environments_json

def get_exe_dir():
    """获取exe文件所在目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包的exe，使用exe所在目录
        return os.path.dirname(sys.executable)
    else:
        # 如果是脚本运行，使用当前文件所在目录
        return os.path.dirname(os.path.abspath(__file__))

def save_mod_environment(modid, environment):
    """将mod的运行环境信息保存到JSON文件中"""
    # 将环境值标准化为三种值之一: required, optional, unsupported
    if environment in ["server_required", "required"]:
        environment = "required"
    elif environment in ["server_optional", "optional"]:
        environment = "optional"
    elif environment in ["server_unsupported", "unsupported"]:
        environment = "unsupported"
    # JSON文件路径
    json_file_path = os.path.join(get_exe_dir(), "mod_environments.json")
    
    # 读取现有的数据
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
    else:
        data = {}
    
    # 更新数据
    data[modid] = environment
    
    # 保存数据
    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存mod环境信息到JSON文件时出错: {e}")

def get_mod_environment(modid):
    """从JSON文件中获取mod的运行环境信息"""
    # JSON文件路径
    json_file_path = os.path.join(get_exe_dir(), "mod_environments.json")
    
    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        return None
    
    # 读取数据
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 查找modid对应的环境信息
        if modid in data:
            return data[modid]
    except Exception as e:
        print(f"读取mod环境信息时出错: {e}")
    
    return None

class ModClassifier:
    def __init__(self):
        self.processor = ModProcessor()
        self.searcher = ModSearcher()
    
    def classify_mod(self, mod_file_path):
        """
        对mod进行分类，优先从JSON文件获取环境信息
        """
        # 首先获取modid
        result = self.processor.get_mod_info(mod_file_path)
        if isinstance(result, tuple) and len(result) == 2:
            modid, displayName = result
        else:
            modid = result
            displayName = modid
        
        # 首先尝试从JSON文件获取环境信息
        environment = get_mod_environment(modid)
        if environment:
            return environment
        
        # 如果JSON文件中没有环境信息，则尝试使用Modrinth方法分类
        classification = self.classify_mod_by_modrinth(mod_file_path , modid)
        if classification:
            if classification in ["required", "optional", "unsupported"]:
                save_mod_environment(modid, classification)
                update_temp_mod_environments_json(modid , classification)
            return classification
        
        # 如果Modrinth方法无法分类，则使用MC百科方法
        classification = self.classify_mod_by_mcmod(mod_file_path , modid , displayName)
        if classification:
            if classification in ["required", "optional", "unsupported"]:
                save_mod_environment(modid, classification)
                update_temp_mod_environments_json(modid , classification)
            return classification
        
        # 如果仍然无法分类，则归为"无法识别"
        return 'unknown'
    
    def classify_mod_by_mcmod(self, mod_file_path , modid , displayName):
        """
        使用MC百科方法分类mod
        """
        
        # 在ModData.txt中搜索
        wiki_id, search_type = self.searcher.search_wiki_id(mod_file_path, displayName)
        
        if wiki_id:
            # print(f"  通过{search_type}找到匹配项")
            print(f"  WikiId: {wiki_id}")
            
            # 获取服务端支持环境
            server_support = self.processor.get_mcmod_server_support(wiki_id)
            # print(f"  服务端支持环境: {server_support}")
            
            # 将中文环境描述转换为英文
            if '服务端需装' in server_support:
                return "required"
            elif '服务端可选' in server_support:
                return "optional"
            elif '服务端无效' in server_support:
                return "unsupported"
            else:
                return 'unknown'  # 无法识别
        return None

    def classify_mod_by_modrinth(self, mod_file_path , modid):
        """
        使用Modrinth方法分类mod
        """
        result = self.processor.lookup_modrinth_server_support(mod_file_path)
        
        if result:
            return result['server_side']

            # # 保存mod环境信息到JSON文件
            # save_mod_environment(modid, server_side)
            # update_temp_mod_environments_json(modid , server_side)
            # if server_side == 'required':
            #     return 'SERVER_REQUIRED'  # 服务端需装
            # elif server_side == 'optional':
            #     return 'SERVER_OPTIONAL'  # 服务端可选
            # elif server_side == 'unsupported':
            #     return 'SERVER_UNSUPPORTED'  # 服务端无效
            # else:
            #     return 'UNKNOWN'  # 无法识别
        return None