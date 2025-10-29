"""
风格总结模块

分析所有视频的分析结果,总结频道的整体风格特征
"""

import logging
from typing import Dict, List
from collections import Counter
import json


class StyleSummarizer:
    """风格总结器"""
    
    def __init__(self, config: Dict):
        """
        初始化风格总结器
        
        参数:
            config: 配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 知识库配置
        kb_config = config.get("knowledge_base", {})
        self.top_keywords = kb_config.get("top_keywords", 20)
    
    def summarize(self, analysis_results: List[Dict]) -> Dict:
        """
        总结所有视频的分析结果
        
        参数:
            analysis_results: 视频分析结果列表
            
        返回:
            总结结果字典
        """
        self.logger.info(f"开始总结 {len(analysis_results)} 个视频的风格特征")
        
        # 过滤成功分析的视频
        successful_analyses = [
            r for r in analysis_results 
            if r.get('analysis_status') == 'success'
        ]
        
        if not successful_analyses:
            self.logger.warning("没有成功分析的视频")
            return {
                'total_videos': len(analysis_results),
                'analyzed_videos': 0,
                'status': 'failed',
                'message': '没有成功分析的视频'
            }
        
        self.logger.info(f"成功分析了 {len(successful_analyses)} 个视频")
        
        # 统计视频类型分布
        video_types = self._analyze_video_types(successful_analyses)
        
        # 统计主题分布
        topics_distribution = self._analyze_topics(successful_analyses)
        
        # 统计风格特点
        style_features = self._analyze_styles(successful_analyses)
        
        # 提取高频关键词
        top_keywords = self._extract_top_keywords(successful_analyses)
        
        # 分析内容结构模式
        content_patterns = self._analyze_content_patterns(successful_analyses)
        
        # 分析目标受众
        target_audiences = self._analyze_target_audience(successful_analyses)
        
        # 提取吸引观众的技巧
        engagement_techniques = self._analyze_engagement_techniques(successful_analyses)
        
        # 分析标题特征
        title_patterns = self._analyze_title_patterns(successful_analyses)
        
        # 构建总结结果
        summary = {
            'total_videos': len(analysis_results),
            'analyzed_videos': len(successful_analyses),
            'status': 'success',
            
            # 视频类型分布
            'video_types': video_types,
            'primary_type': max(video_types.items(), key=lambda x: x[1])[0] if video_types else '未知',
            
            # 主题分布
            'topics': topics_distribution,
            
            # 风格特点
            'style_features': style_features,
            
            # 高频关键词
            'top_keywords': top_keywords,
            
            # 内容模式
            'content_patterns': content_patterns,
            
            # 目标受众
            'target_audiences': target_audiences,
            'primary_audience': max(target_audiences.items(), key=lambda x: x[1])[0] if target_audiences else '大众',
            
            # 吸引技巧
            'engagement_techniques': engagement_techniques,
            
            # 标题特征
            'title_patterns': title_patterns,
        }
        
        self.logger.info("风格总结完成")
        return summary
    
    def _analyze_video_types(self, analyses: List[Dict]) -> Dict[str, int]:
        """
        统计视频类型分布
        
        参数:
            analyses: 分析结果列表
            
        返回:
            类型分布字典
        """
        types = [a.get('video_type', '其他') for a in analyses]
        type_counts = Counter(types)
        return dict(type_counts.most_common())
    
    def _analyze_topics(self, analyses: List[Dict]) -> Dict[str, int]:
        """
        统计主题分布
        
        参数:
            analyses: 分析结果列表
            
        返回:
            主题分布字典
        """
        all_topics = []
        for a in analyses:
            topics = a.get('topics', [])
            if isinstance(topics, list):
                all_topics.extend(topics)
            elif isinstance(topics, str):
                all_topics.append(topics)
        
        topic_counts = Counter(all_topics)
        return dict(topic_counts.most_common(self.top_keywords))
    
    def _analyze_styles(self, analyses: List[Dict]) -> Dict[str, int]:
        """
        统计风格特点
        
        参数:
            analyses: 分析结果列表
            
        返回:
            风格分布字典
        """
        all_styles = []
        for a in analyses:
            style = a.get('style', '')
            if isinstance(style, list):
                all_styles.extend(style)
            elif isinstance(style, str):
                # 分割多个风格
                styles = [s.strip() for s in style.split(',')]
                all_styles.extend(styles)
        
        style_counts = Counter(all_styles)
        return dict(style_counts.most_common(10))
    
    def _extract_top_keywords(self, analyses: List[Dict]) -> List[str]:
        """
        提取高频关键词
        
        参数:
            analyses: 分析结果列表
            
        返回:
            关键词列表
        """
        all_keywords = []
        for a in analyses:
            keywords = a.get('keywords', [])
            if isinstance(keywords, list):
                all_keywords.extend(keywords)
        
        keyword_counts = Counter(all_keywords)
        top_kws = [kw for kw, _ in keyword_counts.most_common(self.top_keywords)]
        return top_kws
    
    def _analyze_content_patterns(self, analyses: List[Dict]) -> Dict[str, int]:
        """
        分析内容结构模式
        
        参数:
            analyses: 分析结果列表
            
        返回:
            内容模式分布字典
        """
        patterns = [a.get('content_structure', '标准结构') for a in analyses]
        pattern_counts = Counter(patterns)
        return dict(pattern_counts.most_common(10))
    
    def _analyze_target_audience(self, analyses: List[Dict]) -> Dict[str, int]:
        """
        分析目标受众
        
        参数:
            analyses: 分析结果列表
            
        返回:
            受众分布字典
        """
        audiences = [a.get('target_audience', '大众') for a in analyses]
        audience_counts = Counter(audiences)
        return dict(audience_counts.most_common())
    
    def _analyze_engagement_techniques(self, analyses: List[Dict]) -> Dict[str, int]:
        """
        分析吸引观众的技巧
        
        参数:
            analyses: 分析结果列表
            
        返回:
            技巧分布字典
        """
        all_techniques = []
        for a in analyses:
            techniques = a.get('engagement_techniques', [])
            if isinstance(techniques, list):
                all_techniques.extend(techniques)
            elif isinstance(techniques, str):
                all_techniques.append(techniques)
        
        technique_counts = Counter(all_techniques)
        return dict(technique_counts.most_common(10))
    
    def _analyze_title_patterns(self, analyses: List[Dict]) -> Dict:
        """
        分析标题特征
        
        参数:
            analyses: 分析结果列表
            
        返回:
            标题特征字典
        """
        titles = [a.get('title', '') for a in analyses]
        
        # 统计标题长度
        title_lengths = [len(t) for t in titles]
        avg_length = sum(title_lengths) / len(title_lengths) if title_lengths else 0
        
        # 统计常见的标题开头
        first_words = []
        for title in titles:
            words = title.split()
            if words:
                first_words.append(words[0])
        
        first_word_counts = Counter(first_words)
        common_starts = dict(first_word_counts.most_common(10))
        
        # 统计标题中的标点符号使用
        punctuation_usage = {
            '问号(?)': sum(1 for t in titles if '?' in t or '?' in t),
            '感叹号(!)': sum(1 for t in titles if '!' in t or '!' in t),
            '冒号(:)': sum(1 for t in titles if ':' in t or ':' in t),
            '括号()': sum(1 for t in titles if '(' in t or '(' in t),
        }
        
        return {
            'average_length': round(avg_length, 1),
            'common_starts': common_starts,
            'punctuation_usage': punctuation_usage,
            'sample_titles': titles[:5],  # 示例标题
        }
    
    def generate_style_description(self, summary: Dict) -> str:
        """
        根据总结生成风格描述文本
        
        参数:
            summary: 总结结果字典
            
        返回:
            风格描述文本
        """
        if summary.get('status') != 'success':
            return "无法生成风格描述"
        
        description_parts = []
        
        # 基本信息
        description_parts.append(
            f"该频道共分析了 {summary['analyzed_videos']} 个视频。"
        )
        
        # 视频类型
        primary_type = summary.get('primary_type', '未知')
        description_parts.append(
            f"主要内容类型为【{primary_type}】。"
        )
        
        # 风格特点
        style_features = summary.get('style_features', {})
        if style_features:
            top_styles = list(style_features.keys())[:3]
            description_parts.append(
                f"语言风格特点: {', '.join(top_styles)}。"
            )
        
        # 目标受众
        primary_audience = summary.get('primary_audience', '大众')
        description_parts.append(
            f"目标受众主要为【{primary_audience}】。"
        )
        
        # 高频主题
        topics = summary.get('topics', {})
        if topics:
            top_topics = list(topics.keys())[:5]
            description_parts.append(
                f"频繁讨论的主题包括: {', '.join(top_topics)}。"
            )
        
        # 吸引技巧
        engagement = summary.get('engagement_techniques', {})
        if engagement:
            top_techniques = list(engagement.keys())[:3]
            description_parts.append(
                f"常用的吸引观众技巧: {', '.join(top_techniques)}。"
            )
        
        return '\n'.join(description_parts)

