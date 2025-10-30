"""
YouTube 视频数据获取模块

使用 yt-dlp 从 YouTube 获取视频信息、字幕和音频
"""

import os
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import yt_dlp
from tqdm import tqdm


class YouTubeFetcher:
    """YouTube 视频数据获取器"""
    
    def __init__(self, config: Dict, data_dir: str = "data"):
        """
        初始化 YouTube 数据获取器
        
        参数:
            config: 配置字典
            data_dir: 数据存储目录
        """
        self.config = config
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.cache_dir = self.data_dir / "cache"
        
        # 创建必要的目录
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # YouTube 配置
        self.max_videos = config.get("youtube", {}).get("max_videos", 50)
        self.subtitle_languages = config.get("youtube", {}).get("subtitle_languages", ["zh-Hans", "zh", "en"])
        self.audio_format = config.get("youtube", {}).get("download_audio_format", "mp3")
        self.audio_quality = config.get("youtube", {}).get("audio_quality", "128K")
        
    def fetch_channel_videos(self, channel_url: str) -> List[Dict]:
        """
        获取频道的所有视频列表
        
        参数:
            channel_url: YouTube 频道 URL
            
        返回:
            视频信息列表
        """
        self.logger.info(f"正在获取频道视频列表: {channel_url}")
        
        # 配置 yt-dlp 选项 - 只获取视频列表信息
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',  # 只提取播放列表信息,不下载
            'playlistend': self.max_videos if self.max_videos > 0 else None,  # 限制视频数量
        }
        
        videos = []
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 提取频道信息
                self.logger.info("正在提取频道信息...")
                playlist_info = ydl.extract_info(channel_url, download=False)
                
                if playlist_info is None:
                    self.logger.error("无法获取频道信息")
                    return []
                
                # 获取频道名称
                channel_name = playlist_info.get('channel', playlist_info.get('uploader', 'unknown'))
                self.logger.info(f"频道名称: {channel_name}")
                
                # 获取视频列表
                entries = playlist_info.get('entries', [])
                
                if not entries:
                    self.logger.warning("频道中没有找到视频")
                    return []
                
                self.logger.info(f"找到 {len(entries)} 个视频")
                
                # 提取每个视频的基本信息
                for entry in entries:
                    if entry is None:
                        continue
                        
                    video_info = {
                        'video_id': entry.get('id'),
                        'title': entry.get('title', ''),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'duration': entry.get('duration', 0),
                        'channel': channel_name,
                    }
                    videos.append(video_info)
                    
        except Exception as e:
            self.logger.error(f"获取频道视频列表失败: {str(e)}")
            raise
            
        self.logger.info(f"成功获取 {len(videos)} 个视频信息")
        return videos
    
    def fetch_video_details(self, video_url: str) -> Dict:
        """
        获取单个视频的详细信息
        
        参数:
            video_url: 视频 URL
            
        返回:
            视频详细信息字典
        """
        self.logger.info(f"正在获取视频详情: {video_url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': self.subtitle_languages,
            'skip_download': True,
            # 防止403错误的配置
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if info is None:
                    self.logger.error(f"无法获取视频信息: {video_url}")
                    return {}
                
                # 提取关键信息
                video_details = {
                    'video_id': info.get('id'),
                    'title': info.get('title', ''),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'uploader': info.get('uploader', ''),
                    'channel': info.get('channel', ''),
                    'channel_id': info.get('channel_id', ''),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', []),
                    'url': video_url,
                    'has_subtitles': bool(info.get('subtitles')),
                    'has_automatic_captions': bool(info.get('automatic_captions')),
                    'available_subtitles': list(info.get('subtitles', {}).keys()),
                    'available_automatic_captions': list(info.get('automatic_captions', {}).keys()),
                }
                
                return video_details
                
        except Exception as e:
            self.logger.error(f"获取视频详情失败: {str(e)}")
            return {}
    
    def download_subtitles(self, video_url: str, video_id: str) -> Optional[str]:
        """
        下载视频字幕
        
        参数:
            video_url: 视频 URL
            video_id: 视频 ID
            
        返回:
            字幕文件路径,如果没有字幕则返回 None
        """
        self.logger.info(f"正在下载字幕: {video_id}")
        
        # 字幕保存目录
        subtitle_dir = self.raw_dir / "subtitles"
        subtitle_dir.mkdir(exist_ok=True)
        
        # 配置 yt-dlp 选项(增强防403配置)
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': True,  # 下载手动添加的字幕
            'writeautomaticsub': True,  # 下载自动生成的字幕
            'subtitleslangs': self.subtitle_languages,  # 字幕语言优先级
            'subtitlesformat': 'vtt',  # 字幕格式
            'skip_download': True,  # 不下载视频
            'outtmpl': str(subtitle_dir / f"{video_id}.%(ext)s"),  # 输出模板
            # 防止403错误的配置
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                
            # 查找下载的字幕文件
            subtitle_files = list(subtitle_dir.glob(f"{video_id}*.vtt"))
            
            if subtitle_files:
                self.logger.info(f"成功下载字幕: {subtitle_files[0].name}")
                return str(subtitle_files[0])
            else:
                self.logger.warning(f"视频 {video_id} 没有可用的字幕")
                return None
                
        except Exception as e:
            self.logger.error(f"下载字幕失败: {str(e)}")
            return None
    
    def download_audio(self, video_url: str, video_id: str) -> Optional[str]:
        """
        下载视频音频
        
        参数:
            video_url: 视频 URL
            video_id: 视频 ID
            
        返回:
            音频文件路径
        """
        self.logger.info(f"正在下载音频: {video_id}")
        
        # 音频保存目录
        audio_dir = self.raw_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        audio_path = audio_dir / f"{video_id}.{self.audio_format}"
        
        # 如果音频已存在,直接返回
        if audio_path.exists():
            self.logger.info(f"音频文件已存在: {audio_path}")
            return str(audio_path)
        
        # 配置 yt-dlp 选项(增强防403配置)
        ydl_opts = {
            'format': 'bestaudio/best',  # 最佳音频质量
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',  # 提取音频
                'preferredcodec': self.audio_format,  # 音频格式
                'preferredquality': self.audio_quality,  # 音频质量
            }],
            'outtmpl': str(audio_dir / f"{video_id}.%(ext)s"),  # 输出模板
            'quiet': True,
            'no_warnings': True,
            # 防止403错误的配置
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'extractor_retries': 3,
            'fragment_retries': 3,
            'retry_sleep': 5,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                
            if audio_path.exists():
                self.logger.info(f"成功下载音频: {audio_path}")
                return str(audio_path)
            else:
                self.logger.error(f"音频文件未找到: {audio_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"下载音频失败: {str(e)}")
            self.logger.warning(f"视频 {video_id} 无法下载音频,将跳过此视频")
            return None
    
    def parse_vtt_subtitles(self, vtt_file: str) -> str:
        """
        解析 VTT 字幕文件,提取纯文本
        
        参数:
            vtt_file: VTT 字幕文件路径
            
        返回:
            字幕文本内容
        """
        try:
            with open(vtt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 过滤掉时间戳和空行,只保留文本
            text_lines = []
            for line in lines:
                line = line.strip()
                # 跳过 WEBVTT 头、时间戳行、空行
                if (line and 
                    not line.startswith('WEBVTT') and 
                    not '-->' in line and 
                    not line.isdigit()):
                    text_lines.append(line)
            
            return '\n'.join(text_lines)
            
        except Exception as e:
            self.logger.error(f"解析字幕文件失败: {str(e)}")
            return ""
    
    def save_cache(self, channel_name: str, videos_data: List[Dict]):
        """
        保存视频数据到缓存
        
        参数:
            channel_name: 频道名称
            videos_data: 视频数据列表
        """
        cache_file = self.cache_dir / f"{channel_name}_videos.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(videos_data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"缓存已保存: {cache_file}")
        except Exception as e:
            self.logger.error(f"保存缓存失败: {str(e)}")
    
    def load_cache(self, channel_name: str) -> Optional[List[Dict]]:
        """
        从缓存加载视频数据
        
        参数:
            channel_name: 频道名称
            
        返回:
            视频数据列表,如果缓存不存在则返回 None
        """
        cache_file = self.cache_dir / f"{channel_name}_videos.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                videos_data = json.load(f)
            self.logger.info(f"从缓存加载了 {len(videos_data)} 个视频")
            return videos_data
        except Exception as e:
            self.logger.error(f"加载缓存失败: {str(e)}")
            return None
    
    def fetch_all(self, channel_url: str, use_cache: bool = True) -> List[Dict]:
        """
        获取频道的所有视频数据(包括详细信息和字幕)
        
        参数:
            channel_url: YouTube 频道 URL
            use_cache: 是否使用缓存
            
        返回:
            完整的视频数据列表
        """
        self.logger.info("="*50)
        self.logger.info("开始获取 YouTube 频道数据")
        self.logger.info("="*50)
        
        # 首先获取视频列表
        videos = self.fetch_channel_videos(channel_url)
        
        if not videos:
            self.logger.error("未获取到任何视频")
            return []
        
        channel_name = videos[0]['channel']
        
        # 检查缓存
        if use_cache:
            cached_data = self.load_cache(channel_name)
            if cached_data:
                self.logger.info("使用缓存数据")
                return cached_data
        
        # 获取每个视频的详细信息
        all_videos_data = []
        
        self.logger.info(f"开始处理 {len(videos)} 个视频...")
        
        for video in tqdm(videos, desc="处理视频"):
            video_url = video['url']
            video_id = video['video_id']
            
            try:
                # 获取视频详情
                details = self.fetch_video_details(video_url)
                
                if not details:
                    continue
                
                # 尝试下载字幕
                subtitle_file = self.download_subtitles(video_url, video_id)
                
                if subtitle_file:
                    # 解析字幕文本
                    subtitle_text = self.parse_vtt_subtitles(subtitle_file)
                    details['subtitle_text'] = subtitle_text
                    details['subtitle_file'] = subtitle_file
                    details['needs_transcription'] = False
                else:
                    # 没有字幕,需要下载音频进行转录
                    audio_file = self.download_audio(video_url, video_id)
                    details['audio_file'] = audio_file
                    details['needs_transcription'] = True
                    details['subtitle_text'] = ""
                
                all_videos_data.append(details)
                
            except Exception as e:
                self.logger.error(f"处理视频 {video_id} 时出错: {str(e)}")
                continue
        
        self.logger.info(f"成功处理 {len(all_videos_data)} 个视频")
        
        # 保存到缓存
        if use_cache:
            self.save_cache(channel_name, all_videos_data)
        
        return all_videos_data

