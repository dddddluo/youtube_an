"""
知识库生成模块

根据分析结果生成 Markdown 格式的知识库文档
"""

import os
import logging
from typing import Dict, List
from pathlib import Path
from datetime import datetime


class KnowledgeBaseGenerator:
    """知识库生成器"""
    
    def __init__(self, config: Dict, output_dir: str = "output"):
        """
        初始化知识库生成器
        
        参数:
            config: 配置字典
            output_dir: 输出目录
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # 知识库配置
        kb_config = config.get("knowledge_base", {})
        self.include_video_details = kb_config.get("include_video_details", True)
        self.generate_wordcloud = kb_config.get("generate_wordcloud", True)
    
    def generate(self, channel_name: str, summary: Dict, analysis_results: List[Dict], videos_data: List[Dict]) -> str:
        """
        生成完整的知识库
        
        参数:
            channel_name: 频道名称
            summary: 风格总结
            analysis_results: 视频分析结果列表
            videos_data: 原始视频数据列表
            
        返回:
            输出目录路径
        """
        self.logger.info(f"开始生成知识库: {channel_name}")
        
        # 创建频道输出目录
        channel_dir = self.output_dir / self._sanitize_filename(channel_name)
        channel_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成总结文档
        summary_file = self._generate_summary_doc(channel_dir, channel_name, summary)
        self.logger.info(f"已生成总结文档: {summary_file}")
        
        # 生成统计数据文档
        stats_file = self._generate_statistics_doc(channel_dir, channel_name, summary, analysis_results)
        self.logger.info(f"已生成统计文档: {stats_file}")
        
        # 生成视频详情文档
        if self.include_video_details:
            videos_dir = channel_dir / "videos"
            videos_dir.mkdir(exist_ok=True)
            self._generate_video_details(videos_dir, analysis_results, videos_data)
            self.logger.info(f"已生成视频详情文档: {videos_dir}")
        
        # 生成学习指南
        guide_file = self._generate_learning_guide(channel_dir, channel_name, summary)
        self.logger.info(f"已生成学习指南: {guide_file}")
        
        # 生成词云(如果配置启用)
        if self.generate_wordcloud:
            try:
                wordcloud_file = self._generate_wordcloud_image(channel_dir, summary)
                if wordcloud_file:
                    self.logger.info(f"已生成词云图: {wordcloud_file}")
            except Exception as e:
                self.logger.warning(f"生成词云失败: {str(e)}")
        
        self.logger.info(f"知识库生成完成: {channel_dir}")
        return str(channel_dir)
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名,移除不合法字符
        
        参数:
            filename: 原始文件名
            
        返回:
            清理后的文件名
        """
        import re
        # 移除不合法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return filename
    
    def _generate_summary_doc(self, output_dir: Path, channel_name: str, summary: Dict) -> str:
        """
        生成总结文档
        
        参数:
            output_dir: 输出目录
            channel_name: 频道名称
            summary: 风格总结
            
        返回:
            文档文件路径
        """
        summary_file = output_dir / "summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            # 标题
            f.write(f"# {channel_name} - 频道风格分析总结\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 基本信息
            f.write("## 📊 基本信息\n\n")
            f.write(f"- **分析视频总数**: {summary.get('total_videos', 0)}\n")
            f.write(f"- **成功分析数量**: {summary.get('analyzed_videos', 0)}\n")
            f.write(f"- **主要内容类型**: {summary.get('primary_type', '未知')}\n")
            f.write(f"- **主要目标受众**: {summary.get('primary_audience', '大众')}\n\n")
            
            # 视频类型分布
            f.write("## 🎬 视频类型分布\n\n")
            video_types = summary.get('video_types', {})
            if video_types:
                for vtype, count in video_types.items():
                    percentage = (count / summary.get('analyzed_videos', 1)) * 100
                    f.write(f"- **{vtype}**: {count} 个 ({percentage:.1f}%)\n")
            f.write("\n")
            
            # 风格特点
            f.write("## 🎨 风格特点\n\n")
            style_features = summary.get('style_features', {})
            if style_features:
                for style, count in list(style_features.items())[:5]:
                    f.write(f"- **{style}**: 出现 {count} 次\n")
            f.write("\n")
            
            # 高频主题
            f.write("## 📌 高频主题\n\n")
            topics = summary.get('topics', {})
            if topics:
                for i, (topic, count) in enumerate(list(topics.items())[:10], 1):
                    f.write(f"{i}. **{topic}** ({count} 次)\n")
            f.write("\n")
            
            # 高频关键词
            f.write("## 🔑 高频关键词\n\n")
            keywords = summary.get('top_keywords', [])
            if keywords:
                # 每行显示 5 个关键词
                for i in range(0, len(keywords), 5):
                    kw_line = keywords[i:i+5]
                    f.write(f"- {' · '.join(kw_line)}\n")
            f.write("\n")
            
            # 标题特征
            f.write("## 📝 标题特征\n\n")
            title_patterns = summary.get('title_patterns', {})
            if title_patterns:
                avg_length = title_patterns.get('average_length', 0)
                f.write(f"- **平均标题长度**: {avg_length} 字符\n\n")
                
                common_starts = title_patterns.get('common_starts', {})
                if common_starts:
                    f.write("**常见标题开头**:\n\n")
                    for word, count in list(common_starts.items())[:5]:
                        f.write(f"- `{word}` (使用 {count} 次)\n")
                f.write("\n")
                
                punctuation = title_patterns.get('punctuation_usage', {})
                if punctuation:
                    f.write("**标点符号使用**:\n\n")
                    for punc, count in punctuation.items():
                        if count > 0:
                            f.write(f"- {punc}: {count} 次\n")
                f.write("\n")
            
            # 吸引观众技巧
            f.write("## 💡 吸引观众技巧\n\n")
            engagement = summary.get('engagement_techniques', {})
            if engagement:
                for i, (technique, count) in enumerate(list(engagement.items())[:10], 1):
                    f.write(f"{i}. **{technique}** (使用 {count} 次)\n")
            f.write("\n")
            
            # 内容结构模式
            f.write("## 📋 内容结构模式\n\n")
            content_patterns = summary.get('content_patterns', {})
            if content_patterns:
                for pattern, count in content_patterns.items():
                    f.write(f"- **{pattern}**: {count} 个视频\n")
            f.write("\n")
        
        return str(summary_file)
    
    def _generate_statistics_doc(self, output_dir: Path, channel_name: str, summary: Dict, analysis_results: List[Dict]) -> str:
        """
        生成统计数据文档
        
        参数:
            output_dir: 输出目录
            channel_name: 频道名称
            summary: 风格总结
            analysis_results: 分析结果列表
            
        返回:
            文档文件路径
        """
        stats_file = output_dir / "statistics.md"
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write(f"# {channel_name} - 详细统计数据\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 视频分析状态统计
            f.write("## 📈 分析状态统计\n\n")
            successful = len([r for r in analysis_results if r.get('analysis_status') == 'success'])
            failed = len([r for r in analysis_results if r.get('analysis_status') == 'failed'])
            skipped = len([r for r in analysis_results if r.get('analysis_status') == 'skipped'])
            
            f.write(f"- ✅ 成功分析: {successful}\n")
            f.write(f"- ❌ 分析失败: {failed}\n")
            f.write(f"- ⏭️ 跳过分析: {skipped}\n\n")
            
            # 视频类型详细统计
            f.write("## 🎬 视频类型详细统计\n\n")
            video_types = summary.get('video_types', {})
            total = sum(video_types.values())
            
            f.write("| 视频类型 | 数量 | 占比 |\n")
            f.write("|---------|------|------|\n")
            for vtype, count in video_types.items():
                percentage = (count / total * 100) if total > 0 else 0
                f.write(f"| {vtype} | {count} | {percentage:.1f}% |\n")
            f.write("\n")
            
            # 主题统计
            f.write("## 📌 主题统计 (Top 20)\n\n")
            topics = summary.get('topics', {})
            f.write("| 排名 | 主题 | 出现次数 |\n")
            f.write("|------|------|----------|\n")
            for i, (topic, count) in enumerate(list(topics.items())[:20], 1):
                f.write(f"| {i} | {topic} | {count} |\n")
            f.write("\n")
            
            # 风格特点统计
            f.write("## 🎨 风格特点统计\n\n")
            styles = summary.get('style_features', {})
            f.write("| 风格特点 | 出现次数 |\n")
            f.write("|----------|----------|\n")
            for style, count in styles.items():
                f.write(f"| {style} | {count} |\n")
            f.write("\n")
            
            # 关键词统计
            f.write("## 🔑 关键词统计\n\n")
            keywords = summary.get('top_keywords', [])
            f.write("| 排名 | 关键词 |\n")
            f.write("|------|--------|\n")
            for i, kw in enumerate(keywords, 1):
                f.write(f"| {i} | {kw} |\n")
            f.write("\n")
        
        return str(stats_file)
    
    def _generate_video_details(self, videos_dir: Path, analysis_results: List[Dict], videos_data: List[Dict]):
        """
        生成每个视频的详细分析文档
        
        参数:
            videos_dir: 视频详情目录
            analysis_results: 分析结果列表
            videos_data: 原始视频数据列表
        """
        # 创建视频数据映射
        video_data_map = {v.get('video_id'): v for v in videos_data}
        
        for analysis in analysis_results:
            if analysis.get('analysis_status') != 'success':
                continue
            
            video_id = analysis.get('video_id', 'unknown')
            title = analysis.get('title', 'Untitled')
            
            # 清理标题作为文件名
            safe_title = self._sanitize_filename(title)[:50]  # 限制长度
            video_file = videos_dir / f"{video_id}_{safe_title}.md"
            
            with open(video_file, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                
                # 基本信息
                video_data = video_data_map.get(video_id, {})
                f.write("## 📺 基本信息\n\n")
                f.write(f"- **视频 ID**: {video_id}\n")
                f.write(f"- **视频链接**: {video_data.get('url', 'N/A')}\n")
                f.write(f"- **上传时间**: {video_data.get('upload_date', 'N/A')}\n")
                f.write(f"- **时长**: {video_data.get('duration', 0)} 秒\n")
                f.write(f"- **观看数**: {video_data.get('view_count', 0):,}\n")
                f.write(f"- **点赞数**: {video_data.get('like_count', 0):,}\n\n")
                
                # 内容分析
                f.write("## 🔍 内容分析\n\n")
                f.write(f"- **视频类型**: {analysis.get('video_type', 'N/A')}\n")
                f.write(f"- **语言风格**: {analysis.get('style', 'N/A')}\n")
                f.write(f"- **语气**: {analysis.get('tone', 'N/A')}\n")
                f.write(f"- **目标受众**: {analysis.get('target_audience', 'N/A')}\n\n")
                
                # 主题和关键词
                f.write("### 主要主题\n\n")
                topics = analysis.get('topics', [])
                if topics:
                    for topic in topics:
                        f.write(f"- {topic}\n")
                f.write("\n")
                
                f.write("### 关键词\n\n")
                keywords = analysis.get('keywords', [])
                if keywords:
                    f.write(f"{' · '.join(keywords[:10])}\n\n")
                
                # 内容结构
                f.write("### 内容结构\n\n")
                f.write(f"{analysis.get('content_structure', 'N/A')}\n\n")
                
                # 核心要点
                f.write("### 核心要点\n\n")
                key_points = analysis.get('key_points', [])
                if key_points:
                    for i, point in enumerate(key_points, 1):
                        f.write(f"{i}. {point}\n")
                f.write("\n")
                
                # 吸引技巧
                f.write("### 吸引观众技巧\n\n")
                techniques = analysis.get('engagement_techniques', [])
                if techniques:
                    for tech in techniques:
                        f.write(f"- {tech}\n")
                f.write("\n")
                
                # 字幕内容(节选)
                subtitle_text = video_data.get('subtitle_text', '')
                if subtitle_text:
                    f.write("## 📝 字幕内容节选\n\n")
                    f.write("```\n")
                    # 只显示前 500 字符
                    preview = subtitle_text[:500]
                    if len(subtitle_text) > 500:
                        preview += "..."
                    f.write(preview)
                    f.write("\n```\n\n")
    
    def _generate_learning_guide(self, output_dir: Path, channel_name: str, summary: Dict) -> str:
        """
        生成学习指南
        
        参数:
            output_dir: 输出目录
            channel_name: 频道名称
            summary: 风格总结
            
        返回:
            文档文件路径
        """
        guide_file = output_dir / "learning_guide.md"
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(f"# {channel_name} - 学习与模仿指南\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 🎯 核心特征总结\n\n")
            
            # 内容定位
            f.write("### 1. 内容定位\n\n")
            primary_type = summary.get('primary_type', '未知')
            f.write(f"该频道主要制作【{primary_type}】类型的视频,")
            primary_audience = summary.get('primary_audience', '大众')
            f.write(f"目标受众为【{primary_audience}】。\n\n")
            
            # 风格特点
            f.write("### 2. 风格特点\n\n")
            style_features = summary.get('style_features', {})
            if style_features:
                top_styles = list(style_features.keys())[:3]
                f.write("该频道的语言风格特点:\n\n")
                for style in top_styles:
                    f.write(f"- {style}\n")
            f.write("\n")
            
            # 内容主题
            f.write("### 3. 内容主题\n\n")
            topics = summary.get('topics', {})
            if topics:
                f.write("频道经常涉及的主题:\n\n")
                for topic in list(topics.keys())[:10]:
                    f.write(f"- {topic}\n")
            f.write("\n")
            
            # 标题技巧
            f.write("### 4. 标题技巧\n\n")
            title_patterns = summary.get('title_patterns', {})
            if title_patterns:
                avg_length = title_patterns.get('average_length', 0)
                f.write(f"- 标题平均长度: {avg_length} 字符\n")
                
                common_starts = title_patterns.get('common_starts', {})
                if common_starts:
                    f.write("- 常用开头词: ")
                    f.write(", ".join(list(common_starts.keys())[:5]))
                    f.write("\n")
                
                punctuation = title_patterns.get('punctuation_usage', {})
                high_usage_punct = [p for p, c in punctuation.items() if c > 3]
                if high_usage_punct:
                    f.write(f"- 常用标点: {', '.join(high_usage_punct)}\n")
            f.write("\n")
            
            # 吸引技巧
            f.write("### 5. 吸引观众技巧\n\n")
            engagement = summary.get('engagement_techniques', {})
            if engagement:
                f.write("该频道常用的吸引观众技巧:\n\n")
                for i, technique in enumerate(list(engagement.keys())[:8], 1):
                    f.write(f"{i}. {technique}\n")
            f.write("\n")
            
            # 模仿建议
            f.write("## 💡 模仿建议\n\n")
            
            f.write("### 内容创作方向\n\n")
            f.write(f"1. **定位明确**: 聚焦于【{primary_type}】类型内容\n")
            f.write(f"2. **受众定位**: 针对【{primary_audience}】创作内容\n")
            if topics:
                top_topics = list(topics.keys())[:5]
                f.write(f"3. **主题选择**: 围绕 {', '.join(top_topics)} 等主题展开\n")
            f.write("\n")
            
            f.write("### 风格塑造\n\n")
            if style_features:
                for i, style in enumerate(list(style_features.keys())[:3], 1):
                    f.write(f"{i}. 保持【{style}】的表达方式\n")
            f.write("\n")
            
            f.write("### 标题撰写\n\n")
            if title_patterns:
                avg_length = title_patterns.get('average_length', 0)
                f.write(f"1. 标题长度控制在 {int(avg_length * 0.8)}-{int(avg_length * 1.2)} 字符左右\n")
                
                common_starts = title_patterns.get('common_starts', {})
                if common_starts:
                    f.write(f"2. 可以尝试使用「{list(common_starts.keys())[0]}」等开头\n")
                
                f.write("3. 善用标点符号增强吸引力\n")
            f.write("\n")
            
            f.write("### 内容技巧\n\n")
            if engagement:
                techniques = list(engagement.keys())[:5]
                for i, tech in enumerate(techniques, 1):
                    f.write(f"{i}. {tech}\n")
            f.write("\n")
            
            # 关键成功因素
            f.write("## 🔑 关键成功因素\n\n")
            f.write("基于分析,该频道的成功关键因素可能包括:\n\n")
            f.write("1. **一致的风格定位**: 保持统一的内容类型和风格\n")
            f.write("2. **明确的受众群体**: 了解并服务好目标受众\n")
            f.write("3. **持续的主题深耕**: 在特定领域建立专业度\n")
            if engagement:
                f.write("4. **多样的互动技巧**: 运用多种方式吸引和留住观众\n")
            f.write("\n")
            
            f.write("---\n\n")
            f.write("**注**: 以上分析基于视频内容的客观数据,模仿时请结合自身特点,形成独特风格。\n")
        
        return str(guide_file)
    
    def _generate_wordcloud_image(self, output_dir: Path, summary: Dict) -> str:
        """
        生成词云图
        
        参数:
            output_dir: 输出目录
            summary: 风格总结
            
        返回:
            词云图文件路径
        """
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            
            # 获取关键词
            keywords = summary.get('top_keywords', [])
            if not keywords:
                return None
            
            # 构建词频字典
            topics = summary.get('topics', {})
            word_freq = {word: freq for word, freq in topics.items()}
            
            # 如果词频为空,使用关键词列表
            if not word_freq:
                word_freq = {kw: len(keywords) - i for i, kw in enumerate(keywords)}
            
            # 生成词云
            wordcloud = WordCloud(
                width=1200,
                height=600,
                background_color='white',
                font_path=None,  # 自动选择字体
                max_words=100,
                relative_scaling=0.5,
                colormap='viridis'
            ).generate_from_frequencies(word_freq)
            
            # 保存图片
            wordcloud_file = output_dir / "wordcloud.png"
            plt.figure(figsize=(12, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(wordcloud_file, dpi=150, bbox_inches='tight')
            plt.close()
            
            return str(wordcloud_file)
            
        except Exception as e:
            self.logger.warning(f"生成词云图失败: {str(e)}")
            return None

