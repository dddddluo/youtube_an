"""
音频转录模块

使用 OpenAI Whisper 模型将音频转换为文字
"""

import os
import logging
from typing import Optional, Dict
from pathlib import Path
import whisper
from tqdm import tqdm


class AudioTranscriber:
    """音频转录器"""
    
    def __init__(self, config: Dict):
        """
        初始化音频转录器
        
        参数:
            config: 配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Whisper 配置
        whisper_config = config.get("whisper", {})
        self.model_name = whisper_config.get("model", "base")
        self.language = whisper_config.get("language", "zh")
        self.device = whisper_config.get("device", "cpu")
        
        # 加载 Whisper 模型
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """
        加载 Whisper 模型
        
        模型大小说明:
        - tiny: 最快,但准确度较低 (~1GB RAM)
        - base: 速度快,准确度中等 (~1GB RAM) [推荐]
        - small: 速度中等,准确度好 (~2GB RAM)
        - medium: 速度较慢,准确度高 (~5GB RAM)
        - large: 最慢,准确度最高 (~10GB RAM)
        """
        self.logger.info(f"正在加载 Whisper 模型: {self.model_name}")
        
        try:
            self.model = whisper.load_model(self.model_name, device=self.device)
            self.logger.info(f"Whisper 模型加载成功 (设备: {self.device})")
        except Exception as e:
            self.logger.error(f"加载 Whisper 模型失败: {str(e)}")
            raise
    
    def transcribe(self, audio_file: str, language: Optional[str] = None) -> Dict:
        """
        转录单个音频文件
        
        参数:
            audio_file: 音频文件路径
            language: 语言代码 (None 表示自动检测)
            
        返回:
            转录结果字典,包含 text 和 segments
        """
        if not os.path.exists(audio_file):
            self.logger.error(f"音频文件不存在: {audio_file}")
            return {"text": "", "segments": []}
        
        self.logger.info(f"正在转录音频: {audio_file}")
        
        # 使用指定语言或默认语言
        lang = language if language else self.language
        
        try:
            # 转录音频
            # verbose=False: 不显示详细输出
            # language: 指定语言可以提高准确度
            result = self.model.transcribe(
                audio_file,
                language=lang if lang != "auto" else None,
                verbose=False
            )
            
            # 提取文本
            text = result.get("text", "").strip()
            segments = result.get("segments", [])
            
            self.logger.info(f"转录完成,文本长度: {len(text)} 字符")
            
            return {
                "text": text,
                "segments": segments,
                "language": result.get("language", lang)
            }
            
        except Exception as e:
            self.logger.error(f"转录音频失败: {str(e)}")
            return {"text": "", "segments": [], "error": str(e)}
    
    def transcribe_batch(self, audio_files: list, language: Optional[str] = None) -> Dict[str, Dict]:
        """
        批量转录多个音频文件
        
        参数:
            audio_files: 音频文件路径列表
            language: 语言代码 (None 表示自动检测)
            
        返回:
            字典,键为音频文件路径,值为转录结果
        """
        self.logger.info(f"开始批量转录 {len(audio_files)} 个音频文件")
        
        results = {}
        
        for audio_file in tqdm(audio_files, desc="转录音频"):
            try:
                result = self.transcribe(audio_file, language)
                results[audio_file] = result
            except Exception as e:
                self.logger.error(f"转录 {audio_file} 时出错: {str(e)}")
                results[audio_file] = {"text": "", "segments": [], "error": str(e)}
        
        self.logger.info(f"批量转录完成,成功 {len([r for r in results.values() if r.get('text')])} 个")
        
        return results
    
    def format_segments(self, segments: list) -> str:
        """
        格式化转录片段为带时间戳的文本
        
        参数:
            segments: Whisper 转录的片段列表
            
        返回:
            格式化后的文本
        """
        formatted_lines = []
        
        for segment in segments:
            start = segment.get('start', 0)
            end = segment.get('end', 0)
            text = segment.get('text', '').strip()
            
            # 格式化时间 (秒转为 MM:SS)
            start_time = f"{int(start // 60):02d}:{int(start % 60):02d}"
            end_time = f"{int(end // 60):02d}:{int(end % 60):02d}"
            
            formatted_lines.append(f"[{start_time} - {end_time}] {text}")
        
        return '\n'.join(formatted_lines)
    
    def save_transcription(self, audio_file: str, transcription: Dict, output_dir: str = "data/processed"):
        """
        保存转录结果到文本文件
        
        参数:
            audio_file: 原始音频文件路径
            transcription: 转录结果字典
            output_dir: 输出目录
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 生成输出文件名
        audio_name = Path(audio_file).stem
        text_file = output_path / f"{audio_name}_transcript.txt"
        
        try:
            with open(text_file, 'w', encoding='utf-8') as f:
                # 写入纯文本
                f.write(transcription.get('text', ''))
                f.write('\n\n')
                f.write('='*50)
                f.write('\n带时间戳的完整转录:\n')
                f.write('='*50)
                f.write('\n\n')
                # 写入带时间戳的文本
                segments = transcription.get('segments', [])
                if segments:
                    f.write(self.format_segments(segments))
            
            self.logger.info(f"转录结果已保存: {text_file}")
            return str(text_file)
            
        except Exception as e:
            self.logger.error(f"保存转录结果失败: {str(e)}")
            return None

