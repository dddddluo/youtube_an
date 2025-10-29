# 快速入门指南

本指南帮助你在 5 分钟内开始使用 YouTube 视频分析系统。

## 📋 准备工作

### 必需条件

- Python 3.8 或更高版本
- 稳定的网络连接

### 可选条件(推荐)

- OpenAI API 密钥(用于 AI 深度分析)
- ffmpeg(用于音频转录)

## 🚀 安装步骤

### 方法一: 自动安装(推荐)

```bash
# 1. 进入项目目录
cd youtube_an

# 2. 运行安装脚本
bash setup.sh

# 3. 按照提示完成配置
```

### 方法二: 手动安装

```bash
# 1. 进入项目目录
cd youtube_an

# 2. (推荐) 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖包
pip install -r requirements.txt

# 4. 安装 ffmpeg (可选,用于音频转录)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# 5. 配置 API 密钥(可选,用于 AI 分析)
cp env.example .env
# 编辑 .env 文件,填入你的 OpenAI API 密钥
```

## ✅ 验证安装

运行测试脚本:

```bash
python test_setup.py
```

如果看到 "✨ 所有检查通过!系统已准备就绪!",说明安装成功!

## 🎯 第一次使用

### 示例 1: 分析一个频道(使用关键词分析,免费)

```bash
# 不需要 API 密钥,使用关键词分析
python main.py -c "https://www.youtube.com/@channel_name"
```

### 示例 2: 分析一个频道(使用 AI 分析,更准确)

```bash
# 1. 配置 OpenAI API 密钥
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env

# 2. 运行分析
python main.py -c "https://www.youtube.com/@channel_name"
```

### 示例 3: 只分析最新的 10 个视频

```bash
# 修改 config.yaml 中的 max_videos
# youtube:
#   max_videos: 10

python main.py -c "https://www.youtube.com/@channel_name"
```

## 📊 查看结果

分析完成后,结果保存在 `output/[频道名称]/` 目录:

```bash
# 查看频道风格总结
cat output/频道名称/summary.md

# 查看学习指南
cat output/频道名称/learning_guide.md

# 查看统计数据
cat output/频道名称/statistics.md
```

或使用任何 Markdown 阅读器打开这些文件。

## 🎨 配置选项

### 最小配置(免费)

```yaml
# config.yaml
youtube:
  max_videos: 10  # 限制视频数量

whisper:
  model: "base"  # 使用基础模型

analysis:
  use_ai: false  # 使用关键词分析,不调用 API
```

### 推荐配置(准确)

```yaml
# config.yaml
youtube:
  max_videos: 30

whisper:
  model: "base"  # 或 "small"

analysis:
  use_ai: true
  ai_provider: "openai"

api:
  openai:
    model: "gpt-3.5-turbo"  # 便宜且效果好
```

### 高级配置(最准确)

```yaml
# config.yaml
youtube:
  max_videos: 0  # 不限制

whisper:
  model: "medium"
  device: "cuda"  # 需要 NVIDIA GPU

analysis:
  use_ai: true
  ai_provider: "openai"

api:
  openai:
    model: "gpt-4"  # 最好但贵
```

## 💰 费用估算

### 完全免费方案

- 不配置 API 密钥
- 使用关键词分析
- 费用: $0

### 推荐方案(使用 GPT-3.5)

- 每个视频约 $0.001 - $0.003
- 20 个视频约 $0.02 - $0.06
- 100 个视频约 $0.10 - $0.30

### 高级方案(使用 GPT-4)

- 每个视频约 $0.01 - $0.03
- 20 个视频约 $0.20 - $0.60
- 100 个视频约 $1.00 - $3.00

> 注: 实际费用取决于视频字幕长度和 API 定价

## ❓ 常见问题

### Q: 没有 API 密钥可以使用吗?

A: 可以!系统会自动使用关键词分析,虽然不如 AI 深入,但仍能提供有价值的洞察。

### Q: 需要安装 ffmpeg 吗?

A: 只有在视频没有字幕需要音频转录时才需要。大多数视频都有字幕,所以不是必须的。

### Q: 分析需要多长时间?

A: 
- 获取数据: 1-5 分钟
- 有字幕的视频: 几乎即时
- 需要转录的视频: 每个 1-3 分钟
- AI 分析: 每个视频 5-10 秒

### Q: 如何获取 OpenAI API 密钥?

A:
1. 访问 https://platform.openai.com
2. 注册账号
3. 进入 API Keys 页面
4. 创建新的 API 密钥
5. 复制密钥到 `.env` 文件

### Q: 可以分析多个频道吗?

A: 可以!多次运行程序,每次指定不同的频道 URL。

### Q: 结果可以导出为其他格式吗?

A: 当前支持 Markdown 格式。如需 JSON 或其他格式,可以修改代码或使用转换工具。

## 🆘 遇到问题?

### 1. 查看日志

```bash
cat logs/youtube_analyzer.log
```

### 2. 启用详细日志

```bash
python main.py -c "频道URL" --log-level DEBUG
```

### 3. 运行环境检查

```bash
python test_setup.py
```

### 4. 常见错误解决

#### 错误: No module named 'xxx'

```bash
# 重新安装依赖
pip install -r requirements.txt
```

#### 错误: ffmpeg not found

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg
```

#### 错误: API key not found

```bash
# 检查 .env 文件
cat .env

# 或在 config.yaml 中配置
```

## 📚 下一步

- 阅读完整的 [README.md](README.md)
- 查看 [example_usage.md](example_usage.md) 了解更多用法
- 修改 `config.yaml` 自定义配置
- 尝试分析不同类型的频道

## 💡 使用技巧

1. **首次使用**: 先用 `max_videos: 5` 测试
2. **节省费用**: 使用 `gpt-3.5-turbo` 而不是 `gpt-4`
3. **加速处理**: 减少 `max_videos` 数量
4. **提高准确度**: 使用更大的 Whisper 模型
5. **批量处理**: 创建脚本循环处理多个频道

## 🎉 开始体验

```bash
# 一键开始
python main.py -c "https://www.youtube.com/@your_favorite_channel"
```

享受分析过程!如有问题,请查看完整文档或提交 Issue。

