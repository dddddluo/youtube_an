#!/bin/bash
# YouTube 视频分析系统 - 快速设置脚本

echo "================================"
echo "YouTube 视频分析系统 - 快速设置"
echo "================================"
echo ""

# 检查 Python 版本
echo "1. 检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python 版本: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "   ❌ 错误: 未找到 Python 3"
    echo "   请先安装 Python 3.8 或更高版本"
    exit 1
fi

# 创建虚拟环境(可选)
echo ""
echo "2. 是否创建虚拟环境? (推荐) [y/N]"
read -r create_venv

if [[ "$create_venv" =~ ^[Yy]$ ]]; then
    echo "   正在创建虚拟环境..."
    python3 -m venv venv
    
    echo "   激活虚拟环境..."
    source venv/bin/activate
    
    echo "   ✓ 虚拟环境已创建并激活"
else
    echo "   跳过虚拟环境创建"
fi

# 安装依赖
echo ""
echo "3. 安装 Python 依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "   ✓ 依赖包安装完成"
else
    echo "   ❌ 依赖包安装失败"
    exit 1
fi

# 检查 ffmpeg
echo ""
echo "4. 检查 ffmpeg (Whisper 需要)..."
if command -v ffmpeg &> /dev/null; then
    ffmpeg_version=$(ffmpeg -version 2>&1 | head -n1)
    echo "   ✓ ffmpeg 已安装: $ffmpeg_version"
else
    echo "   ⚠️  ffmpeg 未安装"
    echo "   Whisper 音频转录需要 ffmpeg"
    echo "   安装方法:"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu: sudo apt-get install ffmpeg"
fi

# 创建 .env 文件
echo ""
echo "5. 配置 API 密钥..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "   已创建 .env 文件"
    echo "   请编辑 .env 文件,填入你的 API 密钥"
else
    echo "   .env 文件已存在"
fi

# 创建必要目录
echo ""
echo "6. 创建必要目录..."
mkdir -p data/raw/subtitles data/raw/audio data/processed data/cache output logs
echo "   ✓ 目录创建完成"

# 测试导入
echo ""
echo "7. 测试模块导入..."
python3 -c "from modules import YouTubeFetcher, AudioTranscriber, ContentAnalyzer, StyleSummarizer, KnowledgeBaseGenerator; print('   ✓ 所有模块导入成功')" 2>&1

# 完成
echo ""
echo "================================"
echo "✨ 设置完成!"
echo "================================"
echo ""
echo "下一步:"
echo "1. 编辑 .env 文件,填入 OpenAI API 密钥"
echo "2. (可选) 修改 config.yaml 调整配置"
echo "3. 运行: python main.py -c \"频道URL\""
echo ""
echo "示例:"
echo "  python main.py -c \"https://www.youtube.com/@channel_name\""
echo ""
echo "查看帮助:"
echo "  python main.py --help"
echo ""

if [[ "$create_venv" =~ ^[Yy]$ ]]; then
    echo "注意: 虚拟环境已激活"
    echo "下次使用前需要激活: source venv/bin/activate"
    echo ""
fi

