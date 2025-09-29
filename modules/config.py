import os
import sys

# 配置区域 - 可自定义修改
BASE_FOLDER_PATH = r""  # 基础目录路径将通过界面选择
MODS_FOLDER_PATH = ""   # mods文件夹路径

# 分类文件夹路径（与mods文件夹同级）
SERVER_REQUIRED_FOLDER = ""
SERVER_OPTIONAL_FOLDER = ""
SERVER_UNSUPPORTED_FOLDER = ""
UNKNOWN_FOLDER = ""

def get_resource_path(relative_path):
    """获取资源文件的路径，兼容打包后的exe"""
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        # 作为脚本运行时的路径
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_moddata_path():
    """获取正确的ModData.txt路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包的exe，使用exe所在目录的ModData.txt
        return os.path.join(os.path.dirname(sys.executable), "ModData.txt")
    else:
        # 如果是脚本运行，使用当前目录的ModData.txt
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ModData.txt")

MODDATA_FILE_PATH = get_moddata_path()  # ModData.txt文件路径