import re

class NameNormalizer:
    def __init__(self):
        pass
    
    def normalize_mod_name(self, filename):
        """
        规范化mod名称
        """
        # 移除文件扩展名
        name = filename.rsplit('.', 1)[0]
        
        # 1. 移除方括号及其内容（包括中英文方括号）
        name = re.sub(r'[【】\[\]].*?[】\]]', '', name)
        
        # 2. 替换&为and
        name = name.replace('&', 'and')
        
        # 3. 处理所有格形式（Tomtaru's -> Tomtarus）
        name = re.sub(r"'s\b", "s", name)
        
        # 4. 移除所有单引号
        name = name.replace("'", "")
        
        # 5. 分割字符串为单词（允许连字符作为单词的一部分）
        words = re.split(r'[_\s-]+', name)
        # 6. 过滤单词：移除包含数字的单词和特定关键词
        valid_words = []
        for word in words:
            # 跳过空单词
            if not word:
                continue
                
            # 跳过同时包含数字和.的单词（版本号）
            if re.search(r'\d', word) and '.' in word:
                continue
                
            # 跳过特定关键词（不区分大小写）
            if word.lower() in ['neoforge', 'forge', 'fabric', 'mc', 'mod']:
                continue
            
            # 如果单词以mod结尾，则删除mod字符
            if word.lower().endswith('mod') and len(word) > 3:
                word = word[:-3]
                
            # 将单词转换为小写并添加到有效单词列表
            valid_words.append(word.lower())
        
        # 7. 用连字符连接有效单词
        return '-'.join(valid_words) if valid_words else 'unknown'

    def normalize_displayName(self, displayName):
        """
        规范化displayName
        """
        # 处理所有格形式（Tomtaru's -> Tomtarus）
        displayName = re.sub(r"'s\b", "s", displayName)
        
        # 移除所有单引号
        displayName = displayName.replace("'", "")
        
        # 分割字符串为单词
        words = re.split(r'[_\s-]+', displayName)
        
        # 过滤单词：移除特定关键词
        valid_words = []
        for word in words:
            # 跳过空单词
            if not word:
                continue
                
            # 跳过特定关键词（不区分大小写）
            if word.lower() in ['neoforge', 'forge', 'fabric', 'mc', 'mod']:
                continue
            
            # 如果单词以mod结尾，则删除mod字符
            if word.lower().endswith('mod') and len(word) > 3:
                word = word[:-3]
                
            # 将单词转换为小写并添加到有效单词列表
            valid_words.append(word.lower())
        
        # 用连字符连接有效单词
        return '-'.join(valid_words) if valid_words else 'unknown'
    
    def extract_letters_only(self, text):
        """
        只提取文本中的字母字符
        """
        return re.sub(r'[^a-zA-Z]', '', text).lower()
    
    def calculate_similarity(self, str1, str2):
        """
        计算两个字符串的相似度（基于较长字符串的长度）
        """
        if not str1 or not str2:
            return 0
        
        # 计算相同字符的数量
        common_chars = sum(1 for c in str1 if c in str2)
        
        # 返回相似度百分比（基于较长字符串的长度）
        max_len = max(len(str1), len(str2))
        similarity = (common_chars / max_len) * 100
        return similarity