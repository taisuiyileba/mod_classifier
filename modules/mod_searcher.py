import urllib.request
import urllib.error
import re
from .name_normalizer import NameNormalizer
from .config import get_moddata_path

class ModSearcher:
    def __init__(self):
        self.normalizer = NameNormalizer()
    
    def search_mod_via_mcmod_api(self, displayName):
        """
        通过MC百科搜索API查找mod信息
        """
        try:
            # 构建搜索URL
            search_url = f"https://search.mcmod.cn/s?key={urllib.parse.quote(displayName)}&filter=1&mold=1"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(search_url, headers=headers)
            response = urllib.request.urlopen(req, timeout=10)
            content = response.read().decode('utf-8')
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找搜索结果中的链接
            links = soup.find_all('a', href=re.compile(r'/class/\d+\.html'))
            
            # 也查找class="head"中的a标签
            head_divs = soup.find_all('div', class_='head')
            for head_div in head_divs:
                head_links = head_div.find_all('a', href=re.compile(r'/class/\d+\.html'))
                links.extend(head_links)
            
            # 去重，保持顺序
            unique_links = []
            seen_hrefs = set()
            for link in links:
                href = link.get('href')
                if href and href not in seen_hrefs:
                    unique_links.append(link)
                    seen_hrefs.add(href)
            
            links = unique_links
            
            # 提取displayName的字母部分用于比较
            normalized_display_name = self.normalizer.extract_letters_only(displayName)
            
            # 检查至多3条搜索结果
            for i, link in enumerate(links[:3]):
                # 获取链接文本
                link_text = link.get_text().strip()
                
                # 查找括号中的内容
                bracket_match = re.search(r'\((.*?)\)', link_text)
                if bracket_match:
                    # 如果有括号，使用括号中的内容进行比较
                    bracket_content = bracket_match.group(1)
                    
                    # 处理嵌套括号，只保留第一级括号内容，去除第二级括号
                    # 例如："落叶 (FallingLeaves (Fabric))" -> "FallingLeaves"
                    # 使用正则表达式匹配第一级括号内容，并去除内部的括号
                    bracket_content = re.sub(r'\(.*?\)', '', bracket_content).strip()
                    
                    # 提取括号内容的字母部分
                    normalized_bracket = self.normalizer.extract_letters_only(bracket_content)
                    
                    # 比较字母部分是否相似度达到90%及以上
                    similarity = self.normalizer.calculate_similarity(normalized_display_name, normalized_bracket)
                    if similarity >= 90:
                        # 提取WikiId
                        href = link.get('href')
                        wiki_id_match = re.search(r'/class/(\d+)\.html', href)
                        if wiki_id_match:
                            wiki_id = wiki_id_match.group(1)
                            print(f"  通过MC百科搜索API找到匹配项: {link_text} (相似度: {similarity:.2f}%)")
                            return int(wiki_id)
                else:
                    # 如果没有括号，去除方括号及其中内容后进行比较
                    # 移除方括号及其内容，例如 [MTR] Moog's TemplesReimagined -> Moog's TemplesReimagined
                    text_without_brackets = re.sub(r'\[.*?\]', '', link_text).strip()
                    if text_without_brackets:
                        # 如果去除方括号后包含'-'，则提取左边的字符串
                        # 例如："Brutal Bosses - Custom Bosses" -> "Brutal Bosses"
                        if ' - ' in text_without_brackets:
                            text_without_brackets = text_without_brackets.split(' - ')[0]
                        
                        # 提取去除方括号后文本的字母部分
                        normalized_text = self.normalizer.extract_letters_only(text_without_brackets)
                        
                        # 比较字母部分是否相似度达到90%及以上
                        similarity = self.normalizer.calculate_similarity(normalized_display_name, normalized_text)
                        if similarity >= 90:
                            # 提取WikiId
                            href = link.get('href')
                            wiki_id_match = re.search(r'/class/(\d+)\.html', href)
                            if wiki_id_match:
                                wiki_id = wiki_id_match.group(1)
                                print(f"  通过MC百科搜索API找到匹配项: {link_text} (相似度: {similarity:.2f}%)")
                                return int(wiki_id)
            
            return None
        except Exception as e:
            print(f"  MC百科搜索API调用失败: {e}")
            return None
    
    def search_wiki_id(self, mod_file_path, displayName):
        """
        在ModData.txt中搜索mod信息
        """
        # 确保使用正确的ModData.txt路径
        moddata_path = get_moddata_path()
            
        try:
            with open(moddata_path, 'r', encoding='utf-8') as f:
                # 首先使用文件名规范化搜索
                filename = mod_file_path
                normalized_name = self.normalizer.normalize_mod_name(filename)
                # print(f"  规范化后的文件名: {normalized_name}")
                for line_num, line in enumerate(f, 1):
                    # 检查规范化后的名称是否在行中
                    if normalized_name.lower() in line.lower():
                        # 行号即为WikiId
                        wiki_id = line_num
                        return wiki_id, "filename"
                
                # 如果文件名搜索失败，尝试使用displayName搜索
                if displayName:
                    normalized_displayName = self.normalizer.normalize_displayName(displayName)
                    # print(f"  规范化后的displayName: {normalized_displayName}")
                    
                    # 重置文件指针到开头进行第二次搜索
                    f.seek(0)
                    for line_num, line in enumerate(f, 1):
                        # 检查规范化后的displayName是否在行中
                        if normalized_displayName.lower() in line.lower():
                            # 行号即为WikiId
                            wiki_id = line_num
                            return wiki_id, "displayName"
                
                # 如果displayName搜索失败，尝试使用MC百科搜索API
                if displayName:
                    normalized_displayName = self.normalizer.normalize_displayName(displayName)
                    normalized_displayName = normalized_displayName.replace("-", "")
                    wiki_id = self.search_mod_via_mcmod_api(normalized_displayName)
                    if wiki_id:
                        return wiki_id, "mcmod_api"
            
        except Exception as e:
            print(f"读取 {moddata_path} 时出错: {e}")
        return None, None