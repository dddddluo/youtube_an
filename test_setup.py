"""
测试脚本 - 检查环境配置是否正确
"""

import sys
import os


def test_python_version():
    """测试 Python 版本"""
    print("1. 检查 Python 版本...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ❌ Python 版本过低,需要 3.8 或更高")
        return False
    else:
        print("   ✓ Python 版本符合要求")
        return True


def test_imports():
    """测试模块导入"""
    print("\n2. 检查依赖包...")
    
    packages = [
        ('yt_dlp', 'yt-dlp'),
        ('whisper', 'openai-whisper'),
        ('yaml', 'pyyaml'),
        ('tqdm', 'tqdm'),
        ('colorama', 'colorama'),
    ]
    
    all_ok = True
    for module_name, package_name in packages:
        try:
            __import__(module_name)
            print(f"   ✓ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} 未安装")
            all_ok = False
    
    return all_ok


def test_optional_imports():
    """测试可选依赖"""
    print("\n3. 检查可选依赖...")
    
    optional_packages = [
        ('openai', 'openai (用于 GPT 分析)'),
        ('anthropic', 'anthropic (用于 Claude 分析)'),
        ('jieba', 'jieba (用于中文分词)'),
        ('wordcloud', 'wordcloud (用于生成词云)'),
    ]
    
    for module_name, description in optional_packages:
        try:
            __import__(module_name)
            print(f"   ✓ {description}")
        except ImportError:
            print(f"   ⚠️  {description} 未安装 (可选)")


def test_ffmpeg():
    """测试 ffmpeg"""
    print("\n4. 检查 ffmpeg...")
    
    import subprocess
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✓ {version_line}")
            return True
        else:
            print("   ❌ ffmpeg 未正确安装")
            return False
    except FileNotFoundError:
        print("   ❌ ffmpeg 未安装")
        print("   安装方法:")
        print("   - macOS: brew install ffmpeg")
        print("   - Ubuntu: sudo apt-get install ffmpeg")
        print("   - Windows: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"   ⚠️  无法检查 ffmpeg: {str(e)}")
        return False


def test_modules():
    """测试项目模块"""
    print("\n5. 检查项目模块...")
    
    try:
        from modules import YouTubeFetcher
        print("   ✓ YouTubeFetcher")
    except ImportError as e:
        print(f"   ❌ YouTubeFetcher: {str(e)}")
        return False
    
    try:
        from modules import AudioTranscriber
        print("   ✓ AudioTranscriber")
    except ImportError as e:
        print(f"   ❌ AudioTranscriber: {str(e)}")
        return False
    
    try:
        from modules import ContentAnalyzer
        print("   ✓ ContentAnalyzer")
    except ImportError as e:
        print(f"   ❌ ContentAnalyzer: {str(e)}")
        return False
    
    try:
        from modules import StyleSummarizer
        print("   ✓ StyleSummarizer")
    except ImportError as e:
        print(f"   ❌ StyleSummarizer: {str(e)}")
        return False
    
    try:
        from modules import KnowledgeBaseGenerator
        print("   ✓ KnowledgeBaseGenerator")
    except ImportError as e:
        print(f"   ❌ KnowledgeBaseGenerator: {str(e)}")
        return False
    
    return True


def test_config():
    """测试配置文件"""
    print("\n6. 检查配置文件...")
    
    if not os.path.exists('config.yaml'):
        print("   ❌ config.yaml 不存在")
        return False
    
    print("   ✓ config.yaml 存在")
    
    try:
        import yaml
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print("   ✓ config.yaml 格式正确")
        
        # 检查 API 密钥
        openai_key = config.get('api', {}).get('openai', {}).get('api_key', '')
        if openai_key and openai_key != '':
            print("   ✓ OpenAI API 密钥已配置")
        else:
            print("   ⚠️  OpenAI API 密钥未配置(将使用关键词分析)")
        
        return True
    except Exception as e:
        print(f"   ❌ 配置文件错误: {str(e)}")
        return False


def test_env():
    """测试环境变量"""
    print("\n7. 检查环境变量...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"   ✓ OPENAI_API_KEY 已设置 (长度: {len(openai_key)})")
    else:
        print("   ⚠️  OPENAI_API_KEY 未设置")
    
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        print(f"   ✓ ANTHROPIC_API_KEY 已设置 (长度: {len(anthropic_key)})")
    else:
        print("   ℹ️  ANTHROPIC_API_KEY 未设置 (可选)")


def test_directories():
    """测试目录结构"""
    print("\n8. 检查目录结构...")
    
    required_dirs = [
        'modules',
        'data',
        'output',
        'logs',
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"   ✓ {dir_name}/")
        else:
            print(f"   ⚠️  {dir_name}/ 不存在,将自动创建")
            os.makedirs(dir_name, exist_ok=True)
    
    return all_ok


def main():
    """主函数"""
    print("="*60)
    print("YouTube 视频分析系统 - 环境检查")
    print("="*60)
    
    results = []
    
    results.append(("Python 版本", test_python_version()))
    results.append(("依赖包", test_imports()))
    test_optional_imports()
    results.append(("ffmpeg", test_ffmpeg()))
    results.append(("项目模块", test_modules()))
    results.append(("配置文件", test_config()))
    test_env()
    results.append(("目录结构", test_directories()))
    
    # 总结
    print("\n" + "="*60)
    print("检查结果:")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✓" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✨ 所有检查通过!系统已准备就绪!")
        print("\n下一步:")
        print("  python main.py -c \"https://www.youtube.com/@channel_name\"")
    else:
        print("\n⚠️  部分检查未通过,请根据上述提示解决问题")
        print("\n常见解决方法:")
        print("  1. 安装依赖: pip install -r requirements.txt")
        print("  2. 安装 ffmpeg: brew install ffmpeg (macOS)")
        print("  3. 配置 API 密钥: 编辑 .env 文件")
    
    print()


if __name__ == "__main__":
    main()

