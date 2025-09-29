import os
import shutil
import glob

class FileManager:
    def __init__(self):
        pass
    
    def clear_classification_folders(self, folders):
        """
        清空四个分类文件夹
        """
        for folder in folders:
            if os.path.exists(folder):
                try:
                    # 删除文件夹中的所有文件
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    print(f"已清空文件夹: {folder}")
                except Exception as e:
                    print(f"清空文件夹 {folder} 时出错: {e}")
            else:
                # 如果文件夹不存在，创建它
                os.makedirs(folder)
                print(f"创建文件夹: {folder}")
    
    def move_mod_to_folder(self, mod_file_path, classification, 
                          server_required_folder, server_optional_folder, 
                          server_unsupported_folder, unknown_folder):
        """
        将mod复制到对应的分类文件夹
        """
        if classification == 'required':
            target_folder = server_required_folder
        elif classification == 'optional':
            target_folder = server_optional_folder
        elif classification == 'unsupported':
            target_folder = server_unsupported_folder
        else:  # unknown
            target_folder = unknown_folder
        
        filename = os.path.basename(mod_file_path)
        target_path = os.path.join(target_folder, filename)
        
        # 如果目标文件已存在，添加序号
        counter = 1
        original_target_path = target_path
        while os.path.exists(target_path):
            name, ext = os.path.splitext(original_target_path)
            target_path = f"{name}_{counter}{ext}"
            counter += 1
        
        try:
            shutil.copy2(mod_file_path, target_path)
            print(f"已复制 {filename} 到 {target_folder}")
            return True
        except Exception as e:
            print(f"复制文件时出错: {e}")
            return False

    def process_mods_folder(self, folder_path):
        """
        遍历mods文件夹中的所有jar文件
        """
        if not os.path.exists(folder_path):
            print(f"文件夹不存在: {folder_path}")
            return []
        
        if not os.path.isdir(folder_path):
            print(f"路径不是文件夹: {folder_path}")
            return []
        
        # 查找所有.jar文件
        jar_files = glob.glob(os.path.join(folder_path, "*.jar"))
        
        if not jar_files:
            print(f"在 {folder_path} 中未找到任何.jar文件")
            return []
        
        print(f"找到 {len(jar_files)} 个mod文件")
        return jar_files