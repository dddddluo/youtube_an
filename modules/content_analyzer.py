"""
内容分析模块

使用 AI (GPT/Claude) 或关键词分析视频内容,识别类型和风格特征
"""

import os
import logging
import json
from typing import Dict, List, Optional
import re
from collections import Counter


class ContentAnalyzer:
    """内容分析器"""
    
    def __init__(self, config: Dict):
        """
        初始化内容分析器
        
        参数:
            config: 配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 分析配置
        analysis_config = config.get("analysis", {})
        self.use_ai = analysis_config.get("use_ai", True)
        self.ai_provider = analysis_config.get("ai_provider", "openai")
        self.min_subtitle_length = analysis_config.get("min_subtitle_length", 50)
        
        # 初始化 AI 客户端
        self.ai_client = None
        if self.use_ai:
            self._init_ai_client()
    
    def _init_ai_client(self):
        """初始化 AI 客户端 (OpenAI 或 Anthropic)"""
        try:
            if self.ai_provider == "openai":
                import openai
                api_key = os.getenv("OPENAI_API_KEY") or self.config.get("api", {}).get("openai", {}).get("api_key")
                
                if not api_key:
                    self.logger.warning("未配置 OpenAI API 密钥,将使用关键词分析")
                    self.use_ai = False
                    return
                
                openai.api_key = api_key
                self.ai_client = openai
                self.ai_model = self.config.get("api", {}).get("openai", {}).get("model", "gpt-3.5-turbo")
                self.logger.info(f"已初始化 OpenAI 客户端 (模型: {self.ai_model})")
                
            elif self.ai_provider == "anthropic":
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY") or self.config.get("api", {}).get("anthropic", {}).get("api_key")
                
                if not api_key:
                    self.logger.warning("未配置 Anthropic API 密钥,将使用关键词分析")
                    self.use_ai = False
                    return
                
                self.ai_client = anthropic.Anthropic(api_key=api_key)
                self.ai_model = self.config.get("api", {}).get("anthropic", {}).get("model", "claude-3-haiku-20240307")
                self.logger.info(f"已初始化 Anthropic 客户端 (模型: {self.ai_model})")
                
        except ImportError as e:
            self.logger.warning(f"无法导入 AI 库: {str(e)},将使用关键词分析")
            self.use_ai = False
        except Exception as e:
            self.logger.error(f"初始化 AI 客户端失败: {str(e)}")
            self.use_ai = False
    
    def analyze_video(self, video_data: Dict) -> Dict:
        """
        分析单个视频
        
        参数:
            video_data: 视频数据字典
            
        返回:
            分析结果字典
        """
        video_id = video_data.get('video_id', 'unknown')
        title = video_data.get('title', '')
        subtitle_text = video_data.get('subtitle_text', '')
        
        self.logger.info(f"正在分析视频: {video_id} - {title}")
        
        # 检查字幕长度
        if len(subtitle_text) < self.min_subtitle_length:
            self.logger.warning(f"视频 {video_id} 字幕内容太短,跳过分析")
            return {
                'video_id': video_id,
                'title': title,
                'analysis_status': 'skipped',
                'reason': '字幕内容太短'
            }
        
        # 使用 AI 或关键词分析
        if self.use_ai and self.ai_client:
            return self._analyze_with_ai(video_data)
        else:
            return self._analyze_with_keywords(video_data)
    
    def _analyze_with_ai(self, video_data: Dict) -> Dict:
        """
        使用 AI 进行深度分析
        
        参数:
            video_data: 视频数据字典
            
        返回:
            分析结果字典
        """
        video_id = video_data.get('video_id', '')
        title = video_data.get('title', '')
        description = video_data.get('description', '')
        subtitle_text = video_data.get('subtitle_text', '')
        
        # 截取字幕(避免太长)
        max_subtitle_length = 3000
        if len(subtitle_text) > max_subtitle_length:
            subtitle_text = subtitle_text[:max_subtitle_length] + "..."
        
        # 构建提示词
        prompt = f"""请分析以下 YouTube 短视频的内容,并以 JSON 格式返回分析结果。

视频标题: {title}

视频描述: {description[:500] if description else "无"}

字幕内容:
{subtitle_text}

请提供以下分析(用中文回答,以 JSON 格式返回):
1. video_type: 视频类型(如: 教程、娱乐、评测、Vlog、知识分享、搞笑、美食、旅游等)
2. topics: 主要话题/主题(列表,3-5个关键词)
3. style: 语言风格特点(如: 幽默风趣、专业严肃、口语化、激情澎湃等)
4. tone: 语气特点(如: 轻松、正式、亲切、激励等)
5. target_audience: 目标受众(如: 年轻人、专业人士、学生、大众等)
6. content_structure: 内容结构特点(如: 开场引入、主体讲解、结尾总结)
7. key_points: 核心要点(列表,2-3个要点)
8. keywords: 高频关键词(列表,5-10个)
9. engagement_techniques: 吸引观众的技巧(列表,如: 设置悬念、互动提问、视觉效果等)

返回格式示例:
{{
  "video_type": "知识分享",
  "topics": ["人工智能", "机器学习", "技术趋势"],
  "style": "专业且通俗易懂",
  "tone": "正式但友好",
  "target_audience": "技术爱好者和初学者",
  "content_structure": "问题引入 -> 概念解释 -> 案例说明 -> 总结",
  "key_points": ["AI的基本原理", "实际应用场景", "未来发展方向"],
  "keywords": ["人工智能", "算法", "数据", "应用", "未来"],
  "engagement_techniques": ["使用生活化例子", "设置思考问题", "视觉化展示"]
}}

请直接返回 JSON,不要包含其他说明文字。"""

        try:
            if self.ai_provider == "openai":
                # 使用 OpenAI API
                response = self.ai_client.chat.completions.create(
                    model=self.ai_model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的视频内容分析专家,擅长分析 YouTube 视频的风格和特点。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                
                result_text = response.choices[0].message.content.strip()
                
            elif self.ai_provider == "anthropic":
                # 使用 Anthropic API
                response = self.ai_client.messages.create(
                    model=self.ai_model,
                    max_tokens=1000,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                result_text = response.content[0].text.strip()
            
            # 解析 JSON 结果
            # 尝试提取 JSON 部分(有时 AI 会添加额外说明)
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(0)
            
            analysis_result = json.loads(result_text)
            
            # 添加基本信息
            analysis_result['video_id'] = video_id
            analysis_result['title'] = title
            analysis_result['analysis_status'] = 'success'
            analysis_result['analysis_method'] = 'ai'
            
            self.logger.info(f"AI 分析完成: {video_id}")
            return analysis_result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"解析 AI 返回的 JSON 失败: {str(e)}")
            self.logger.debug(f"AI 返回内容: {result_text}")
            # 降级使用关键词分析
            return self._analyze_with_keywords(video_data)
            
        except Exception as e:
            self.logger.error(f"AI 分析失败: {str(e)}")
            # 降级使用关键词分析
            return self._analyze_with_keywords(video_data)
    
    def _analyze_with_keywords(self, video_data: Dict) -> Dict:
        """
        使用关键词规则进行简单分析
        
        参数:
            video_data: 视频数据字典
            
        返回:
            分析结果字典
        """
        video_id = video_data.get('video_id', '')
        title = video_data.get('title', '')
        subtitle_text = video_data.get('subtitle_text', '')
        
        # 合并标题和字幕进行分析
        full_text = f"{title} {subtitle_text}"
        
        # 视频类型关键词匹配
        type_keywords = {
            '教程': ['教程', '教学', '如何', '怎么', '方法', '技巧', '步骤'],
            '评测': ['评测', '测评', '开箱', '体验', '使用', '对比'],
            'Vlog': ['vlog', '日常', '生活', '分享', '记录'],
            '知识分享': ['知识', '科普', '讲解', '介绍', '原理', '概念'],
            '娱乐': ['搞笑', '有趣', '娱乐', '好玩', '趣味'],
            '美食': ['美食', '做菜', '料理', '食谱', '烹饪'],
            '旅游': ['旅游', '旅行', '游记', '景点', '风景'],
        }
        
        # 匹配视频类型
        video_type = '其他'
        max_matches = 0
        for vtype, keywords in type_keywords.items():
            matches = sum(1 for kw in keywords if kw in full_text)
            if matches > max_matches:
                max_matches = matches
                video_type = vtype
        
        # 提取关键词(简单的词频统计)
        # 这里使用简单的中文分词
        try:
            import jieba
            import jieba.analyse
            
            # 提取关键词
            keywords = jieba.analyse.extract_tags(full_text, topK=10, withWeight=False)
            topics = jieba.analyse.extract_tags(full_text, topK=5, withWeight=False)
            
        except ImportError:
            # 如果没有 jieba,使用简单的字符串分割
            words = re.findall(r'[\u4e00-\u9fff]+', full_text)
            word_counts = Counter(words)
            keywords = [word for word, _ in word_counts.most_common(10)]
            topics = [word for word, _ in word_counts.most_common(5)]
        
        # 风格分析(基于关键词)
        style_keywords = {
            '幽默风趣': ['哈哈', '笑', '搞笑', '有趣'],
            '专业严肃': ['专业', '技术', '研究', '分析'],
            '口语化': ['我觉得', '其实', '就是', '然后'],
            '激情澎湃': ['非常', '超级', '特别', '真的'],
        }
        
        style = []
        for s, kws in style_keywords.items():
            if any(kw in full_text for kw in kws):
                style.append(s)
        
        if not style:
            style = ['自然流畅']
        
        analysis_result = {
            'video_id': video_id,
            'title': title,
            'video_type': video_type,
            'topics': topics,
            'style': ', '.join(style),
            'tone': '友好亲切',
            'target_audience': '大众',
            'content_structure': '标准结构',
            'key_points': topics[:3] if len(topics) >= 3 else topics,
            'keywords': keywords,
            'engagement_techniques': ['内容吸引人'],
            'analysis_status': 'success',
            'analysis_method': 'keywords'
        }
        
        self.logger.info(f"关键词分析完成: {video_id}")
        return analysis_result
    
    def analyze_batch(self, videos_data: List[Dict]) -> List[Dict]:
        """
        批量分析多个视频
        
        参数:
            videos_data: 视频数据列表
            
        返回:
            分析结果列表
        """
        self.logger.info(f"开始批量分析 {len(videos_data)} 个视频")
        
        results = []
        from tqdm import tqdm
        
        for video_data in tqdm(videos_data, desc="分析视频内容"):
            try:
                result = self.analyze_video(video_data)
                results.append(result)
            except Exception as e:
                self.logger.error(f"分析视频 {video_data.get('video_id')} 时出错: {str(e)}")
                results.append({
                    'video_id': video_data.get('video_id', 'unknown'),
                    'title': video_data.get('title', ''),
                    'analysis_status': 'failed',
                    'error': str(e)
                })
        
        self.logger.info(f"批量分析完成,成功 {len([r for r in results if r.get('analysis_status') == 'success'])} 个")
        
        return results

