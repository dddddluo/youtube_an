"""
YouTube 视频分析系统 - 主程序

分析 YouTube 频道的视频内容,生成风格分析知识库
"""

import os
import sys
import logging
import argparse
import yaml
from pathlib import Path
from dotenv import load_dotenv
from colorama import init, Fore, Style

# 导入模块
from modules.youtube_fetcher import YouTubeFetcher
from modules.audio_transcriber import AudioTranscriber
from modules.content_analyzer import ContentAnalyzer
from modules.style_summarizer import StyleSummarizer
from modules.knowledge_base_generator import KnowledgeBaseGenerator


# 初始化 colorama
init(autoreset=True)


def setup_logging(log_level: str = "INFO"):
    """
    设置日志配置
    
    参数:
        log_level: 日志级别
    """
    # 创建 logs 目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            # 文件处理器
            logging.FileHandler(log_dir / "youtube_analyzer.log", encoding='utf-8'),
            # 控制台处理器
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_config(config_file: str = "config.yaml") -> dict:
    """
    加载配置文件
    
    参数:
        config_file: 配置文件路径
        
    返回:
        配置字典
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def print_banner():
    """打印程序横幅"""
    banner = f"""
{Fore.CYAN}{'='*60}
{Fore.CYAN}   YouTube 视频分析系统
{Fore.CYAN}   Video Content Analyzer & Knowledge Base Generator
{Fore.CYAN}{'='*60}{Style.RESET_ALL}
"""
    print(banner)


def print_step(step: int, total: int, message: str):
    """
    打印步骤信息
    
    参数:
        step: 当前步骤
        total: 总步骤数
        message: 步骤描述
    """
    print(f"\n{Fore.GREEN}[步骤 {step}/{total}]{Style.RESET_ALL} {message}")


def analyze_channel(channel_url: str, config: dict):
    """
    分析 YouTube 频道
    
    参数:
        channel_url: YouTube 频道 URL
        config: 配置字典
    """
    logger = logging.getLogger(__name__)
    
    print_step(1, 6, "获取频道视频数据...")
    
    # 1. 获取视频数据
    fetcher = YouTubeFetcher(config)
    videos_data = fetcher.fetch_all(channel_url, use_cache=config.get("system", {}).get("cache_enabled", True))
    
    if not videos_data:
        print(f"{Fore.RED}✗ 未获取到任何视频数据{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✓ 成功获取 {len(videos_data)} 个视频数据{Style.RESET_ALL}")
    
    # 获取频道名称
    channel_name = videos_data[0].get('channel', 'Unknown_Channel')
    
    print_step(2, 6, "处理音频转录...")
    
    # 2. 音频转录(针对没有字幕的视频)
    videos_need_transcription = [v for v in videos_data if v.get('needs_transcription', False)]
    
    if videos_need_transcription:
        print(f"需要转录 {len(videos_need_transcription)} 个视频的音频...")
        transcriber = AudioTranscriber(config)
        
        for video in videos_need_transcription:
            audio_file = video.get('audio_file')
            if audio_file and os.path.exists(audio_file):
                video_id = video.get('video_id')
                print(f"  正在转录: {video_id}...")
                
                try:
                    transcription = transcriber.transcribe(audio_file)
                    video['subtitle_text'] = transcription.get('text', '')
                    print(f"  {Fore.GREEN}✓ 转录完成{Style.RESET_ALL}")
                except Exception as e:
                    logger.error(f"转录失败: {str(e)}")
                    print(f"  {Fore.YELLOW}⚠ 转录失败,将跳过该视频{Style.RESET_ALL}")
                    video['subtitle_text'] = ''
    else:
        print(f"{Fore.GREEN}✓ 所有视频都有字幕,无需转录{Style.RESET_ALL}")
    
    print_step(3, 6, "分析视频内容...")
    
    # 3. 内容分析
    analyzer = ContentAnalyzer(config)
    analysis_results = analyzer.analyze_batch(videos_data)
    
    successful_count = len([r for r in analysis_results if r.get('analysis_status') == 'success'])
    print(f"{Fore.GREEN}✓ 成功分析 {successful_count}/{len(analysis_results)} 个视频{Style.RESET_ALL}")
    
    print_step(4, 6, "总结频道风格...")
    
    # 4. 风格总结
    summarizer = StyleSummarizer(config)
    summary = summarizer.summarize(analysis_results)
    
    if summary.get('status') == 'success':
        print(f"{Fore.GREEN}✓ 风格总结完成{Style.RESET_ALL}")
        
        # 打印简要总结
        print(f"\n{Fore.CYAN}【频道风格简报】{Style.RESET_ALL}")
        print(f"  主要类型: {summary.get('primary_type', 'N/A')}")
        print(f"  主要受众: {summary.get('primary_audience', 'N/A')}")
        
        top_topics = list(summary.get('topics', {}).keys())[:3]
        if top_topics:
            print(f"  高频主题: {', '.join(top_topics)}")
    else:
        print(f"{Fore.YELLOW}⚠ 风格总结失败{Style.RESET_ALL}")
    
    print_step(5, 6, "生成知识库...")
    
    # 5. 生成知识库
    generator = KnowledgeBaseGenerator(config)
    output_dir = generator.generate(channel_name, summary, analysis_results, videos_data)
    
    print(f"{Fore.GREEN}✓ 知识库已生成{Style.RESET_ALL}")
    
    print_step(6, 6, "完成!")
    
    # 打印输出路径
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"✨ 分析完成! 知识库已生成")
    print(f"{'='*60}{Style.RESET_ALL}")
    print(f"\n📂 输出目录: {Fore.YELLOW}{output_dir}{Style.RESET_ALL}")
    print(f"\n生成的文件:")
    print(f"  - summary.md           (频道风格总结)")
    print(f"  - statistics.md        (详细统计数据)")
    print(f"  - learning_guide.md    (学习与模仿指南)")
    print(f"  - videos/              (各视频详细分析)")
    
    if config.get("knowledge_base", {}).get("generate_wordcloud", True):
        wordcloud_path = Path(output_dir) / "wordcloud.png"
        if wordcloud_path.exists():
            print(f"  - wordcloud.png        (关键词词云图)")
    
    print(f"\n{Fore.GREEN}可以查看这些文件来了解频道的风格特点!{Style.RESET_ALL}\n")


def main():
    """主函数"""
    # 打印横幅
    print_banner()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="分析 YouTube 频道的视频内容,生成风格分析知识库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --channel "https://www.youtube.com/@channel_name"
  python main.py -c "https://www.youtube.com/@channel_name" --config custom_config.yaml
  python main.py -c "https://www.youtube.com/c/ChannelName" --log-level DEBUG
        """
    )
    
    parser.add_argument(
        '-c', '--channel',
        type=str,
        required=True,
        help='YouTube 频道 URL (例如: https://www.youtube.com/@channel_name)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='日志级别 (默认: INFO)'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='不使用缓存,重新获取所有数据'
    )
    
    args = parser.parse_args()
    
    # 加载环境变量
    load_dotenv()
    
    # 设置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # 加载配置
        logger.info(f"加载配置文件: {args.config}")
        config = load_config(args.config)
        
        # 如果指定了 --no-cache,覆盖配置
        if args.no_cache:
            config.setdefault('system', {})['cache_enabled'] = False
        
        # 开始分析
        logger.info(f"开始分析频道: {args.channel}")
        analyze_channel(args.channel, config)
        
    except FileNotFoundError as e:
        print(f"{Fore.RED}✗ 错误: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠ 用户中断操作{Style.RESET_ALL}")
        sys.exit(0)
    
    except Exception as e:
        logger.exception("程序运行出错")
        print(f"{Fore.RED}✗ 错误: {str(e)}{Style.RESET_ALL}")
        print(f"\n详细错误信息请查看日志文件: logs/youtube_analyzer.log")
        sys.exit(1)


if __name__ == "__main__":
    main()

