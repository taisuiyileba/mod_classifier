import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from modules.config import get_moddata_path
from modules.mod_classifier import ModClassifier
from modules.server_communicator import *
from modules.file_manager import FileManager
from modules.name_normalizer import NameNormalizer

class ModClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mod分类工具")
        self.root.geometry("600x550")
        self.root.minsize(600, 550)
        
        # 初始化模块
        self.classifier = ModClassifier()
        self.file_manager = FileManager()
        self.normalizer = NameNormalizer()
        
        # 创建界面元素
        self.create_widgets()
        
        # 初始化路径
        self.base_folder_path = ""
        self.mods_folder_path = ""
        self.server_required_folder = ""
        self.server_optional_folder = ""
        self.server_unsupported_folder = ""
        self.unknown_folder = ""
        
        # 分类控制标志
        self.classification_running = False
        
        # 服务端地址
        self.server_url = "http://47.115.171.66:5000"
        
    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="Mod分类工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # MC游戏版本路径选择框架
        base_frame = tk.Frame(self.root)
        base_frame.pack(fill=tk.X, padx=20, pady=5)
        
        base_label = tk.Label(base_frame, text="MC游戏版本路径(例如C:/Users/suiyi/AppData/Local/pcl/.minecraft/versions/1.20.1-Forge_47.4.0):")
        base_label.pack(anchor=tk.W)
        
        base_path_frame = tk.Frame(base_frame)
        base_path_frame.pack(fill=tk.X, pady=5)
        
        self.base_path_var = tk.StringVar()
        self.base_path_var.trace('w', self.on_path_change)  # 添加路径变化监听
        base_path_entry = tk.Entry(base_path_frame, textvariable=self.base_path_var)
        base_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = tk.Button(base_path_frame, text="浏览...", command=self.browse_base_folder)
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # ModData.txt框架
        moddata_frame = tk.Frame(self.root)
        moddata_frame.pack(fill=tk.X, padx=20, pady=5)
        
        moddata_label = tk.Label(moddata_frame, text="ModData.txt文件(首次使用需下载该文件):")
        moddata_label.pack(anchor=tk.W)
        
        moddata_path_frame = tk.Frame(moddata_frame)
        moddata_path_frame.pack(fill=tk.X, pady=5)
        
        self.moddata_path_var = tk.StringVar(value=get_moddata_path())
        moddata_path_entry = tk.Entry(moddata_path_frame, textvariable=self.moddata_path_var, state="readonly")
        moddata_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        download_button = tk.Button(moddata_path_frame, text="下载", command=self.download_moddata)
        download_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 日志显示区域
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        log_label = tk.Label(log_frame, text="运行日志:")
        log_label.pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 进度条
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.progress_label = tk.Label(self.progress_frame, text="进度:")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_text = tk.Label(self.progress_frame, text="等待开始...")
        self.progress_text.pack(anchor=tk.W)
        
        # 确保底部控件可见的占位框架
        bottom_spacer = tk.Frame(self.root, height=10)
        bottom_spacer.pack()
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10, fill=tk.X)
        
        # 创建一个内部框架用于居中按钮
        button_inner_frame = tk.Frame(button_frame)
        button_inner_frame.pack(expand=True)
        
        # 开始分类按钮
        self.start_button = tk.Button(button_inner_frame, text="开始分类", font=("Arial", 12, "bold"), 
                                     command=self.start_classification, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止按钮
        self.stop_button = tk.Button(button_inner_frame, text="停止", font=("Arial", 12, "bold"), 
                                    command=self.stop_classification, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
    def on_path_change(self, *args):
        """
        当路径文本发生变化时调用
        """
        folder_selected = self.base_path_var.get()
        if folder_selected:
            self.base_folder_path = folder_selected
            self.mods_folder_path = os.path.join(folder_selected, "mods")
            self.server_required_folder = os.path.join(folder_selected, "服务端需装")
            self.server_optional_folder = os.path.join(folder_selected, "服务端可选")
            self.server_unsupported_folder = os.path.join(folder_selected, "服务端无效")
            self.unknown_folder = os.path.join(folder_selected, "无法识别")
            
            # 检查mods文件夹是否存在
            if os.path.exists(self.mods_folder_path):
                self.start_button.config(state=tk.NORMAL)
            else:
                self.start_button.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.DISABLED)
    
    
    def browse_base_folder(self):
        folder_selected = filedialog.askdirectory(title="请选择MC游戏版本路径")
        if folder_selected:
            self.base_path_var.set(folder_selected)
            # on_path_change会自动处理后续逻辑
    
    def download_moddata(self):
        moddata_url = "https://raw.githubusercontent.com/Meloong-Git/PCL/refs/heads/main/Plain%20Craft%20Launcher%202/Resources/ModData.txt"
        try:
            self.log_message("正在下载 ModData.txt...")
            import urllib.request
            response = urllib.request.urlopen(moddata_url)
            # 确保MODDATA_FILE_PATH指向exe所在目录而不是临时目录
            moddata_path = os.path.join(os.path.dirname(sys.executable), "ModData.txt") if getattr(sys, 'frozen', False) else get_moddata_path()
            with open(moddata_path, "wb") as f:
                f.write(response.read())
            self.moddata_path_var.set(moddata_path)
            self.log_message(f"ModData.txt 下载完成: {moddata_path}")
            messagebox.showinfo("成功", "ModData.txt 下载完成!")
        except Exception as e:
            self.log_message(f"下载失败: {str(e)}")
            messagebox.showerror("错误", f"下载 ModData.txt 失败:\n{str(e)}")
    
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_classification(self):
        # 在新线程中运行分类，避免界面冻结
        import threading
        self.classification_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        thread = threading.Thread(target=self.run_classification)
        thread.daemon = True
        thread.start()
    
    def stop_classification(self):
        self.classification_running = False
        self.log_message("正在停止分类...")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def run_classification(self):
        try:
            self.log_message("开始分类...")
            
            # 检查配置
            if not self.base_folder_path:
                self.log_message("请先选择基础目录路径！")
                return
            
            if not os.path.exists(self.base_folder_path):
                self.log_message(f"基础文件夹路径不存在: {self.base_folder_path}")
                return
                
            if not os.path.exists(self.mods_folder_path):
                self.log_message(f"mods文件夹路径不存在: {self.mods_folder_path}")
                return
                
            # 使用正确的ModData.txt路径
            moddata_path = get_moddata_path()
            if not os.path.exists(moddata_path):
                self.log_message(f"ModData.txt文件路径不存在: {moddata_path}")
                self.log_message("请先下载ModData.txt文件")
                return
            
            # 从服务端下载最新的mod环境信息（每天最多下载一次，除非本地没有该文件）
            self.log_message("正在从服务端下载最新的mod环境信息...")
            download_mod_environments_from_server(self.server_url)
            temp_mod_environments_json_inti()
            # 清空分类文件夹
            folders = [
                self.server_required_folder,
                self.server_optional_folder,
                self.server_unsupported_folder,
                self.unknown_folder
            ]
            self.file_manager.clear_classification_folders(folders)
            
            # 处理mods文件夹
            self.process_mods_folder(self.mods_folder_path)
            
            if self.classification_running:
                sync_mod_environments_with_server(self.server_url)
                self.log_message("分类完成！")
        except Exception as e:
            self.log_message(f"分类过程中出现错误: {str(e)}")
        finally:
            self.classification_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def process_mods_folder(self, folder_path):
        """
        遍历mods文件夹中的每个mod，获取其服务端支持环境并分类
        """
        jar_files = self.file_manager.process_mods_folder(folder_path)
        
        if not jar_files:
            return
        
        total_files = len(jar_files)
        self.log_message(f"找到 {total_files} 个mod文件")
        self.log_message("-" * 80)
        
        # 处理每个mod文件
        for index, jar_file in enumerate(jar_files):
            # 检查是否需要停止
            if not self.classification_running:
                self.log_message("分类已停止")
                return
            
            # 更新进度条
            progress = (index + 1) / total_files * 100
            self.progress_var.set(progress)
            self.progress_text.config(text=f"进度: {index + 1}/{total_files} ({progress:.1f}%)")
            
            filename = os.path.basename(jar_file)
            self.log_message(f"处理: {filename}")
            
            # 使用新的分类方法，优先从JSON文件获取环境信息
            classification = self.classifier.classify_mod(jar_file)
            
            # 检查是否需要停止
            if not self.classification_running:
                self.log_message("分类已停止")
                return
            
            # 移动文件到对应文件夹
            if self.file_manager.move_mod_to_folder(
                jar_file, classification,
                self.server_required_folder,
                self.server_optional_folder,
                self.server_unsupported_folder,
                self.unknown_folder):
                # 显示分类结果
                classification_names = {
                    'required': '服务端需装',
                    'optional': '服务端可选',
                    'unsupported': '服务端无效',
                    'unknown': '无法识别'
                }
                
                self.log_message(f"  分类结果: {classification_names.get(classification, '未知')}")
            else:
                self.log_message(f"  文件复制失败")
            
            self.log_message("-" * 80)
        
        # 分类完成，设置进度为100%
        self.progress_var.set(100)
        self.progress_text.config(text=f"进度: {total_files}/{total_files} (100.0%)")

def main():
    """
    主函数
    """
    root = tk.Tk()
    app = ModClassifierApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()