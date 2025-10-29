"""
YouTube 视频分析系统 - 核心模块包

本包包含以下核心模块:
- youtube_fetcher: 视频数据获取
- audio_transcriber: 音频转录
- content_analyzer: 内容分析
- style_summarizer: 风格总结
- knowledge_base_generator: 知识库生成
"""

__version__ = "1.0.0"
__author__ = "YouTube Analyzer"

from .youtube_fetcher import YouTubeFetcher
from .audio_transcriber import AudioTranscriber
from .content_analyzer import ContentAnalyzer
from .style_summarizer import StyleSummarizer
from .knowledge_base_generator import KnowledgeBaseGenerator

__all__ = [
    "YouTubeFetcher",
    "AudioTranscriber",
    "ContentAnalyzer",
    "StyleSummarizer",
    "KnowledgeBaseGenerator",
]

