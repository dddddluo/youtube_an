# YouTube 视频分析系统

一个强大的 YouTube 频道内容分析工具,可以自动分析频道的所有视频,提取标题、字幕(或通过 AI 转录音频),使用 AI 分析视频类型和风格特征,最终生成结构化的 Markdown 知识库,帮助你学习和模仿优秀频道的创作风格。

## ✨ 主要功能

- 🎬 **自动获取视频数据**: 使用 yt-dlp 获取频道所有视频的元数据、标题、描述、字幕等
- 🎤 **智能音频转录**: 对没有字幕的视频,使用 Whisper AI 自动将音频转为文字
- 🤖 **AI 内容分析**: 使用 GPT 等 AI 模型深度分析视频内容,识别类型、主题、风格特征
- 📊 **风格总结**: 汇总所有视频的分析结果,提取频道的整体风格特征
- 📚 **知识库生成**: 生成详细的 Markdown 文档,包括:
  - 频道风格总结
  - 详细统计数据
  - 学习与模仿指南
  - 每个视频的详细分析
  - 关键词词云图

## 🚀 快速开始

### 1. 环境要求

- Python 3.8 或更高版本
- (可选) GPU 加速 Whisper 转录

### 2. 安装依赖

```bash
# 克隆或下载项目
cd youtube_an

# 安装依赖包
pip install -r requirements.txt
```

### 3. 配置

#### 方式一: 使用环境变量(推荐)

复制环境变量示例文件:

```bash
cp env.example .env
```

编辑 `.env` 文件,填入你的 API 密钥:

```bash
# OpenAI API 密钥(用于 AI 内容分析)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API 密钥(可选,作为备选)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### 方式二: 修改配置文件

编辑 `config.yaml` 文件,在对应位置填入 API 密钥:

```yaml
api:
  openai:
    api_key: "your_openai_api_key_here"
```

#### 配置说明

`config.yaml` 文件包含所有可配置选项:

- **Whisper 模型**: 可选择 `tiny`, `base`, `small`, `medium`, `large`
  - `base`: 推荐,速度快且准确度中等
  - `small`: 更准确但稍慢
  
- **AI 分析**: 可以选择使用 OpenAI GPT 或 Anthropic Claude
  - 如果不配置 API 密钥,系统会自动降级为关键词分析
  
- **视频数量限制**: 可以限制分析的视频数量(节省时间和 API 费用)

### 4. 运行

```bash
# 基本用法
python main.py --channel "https://www.youtube.com/@channel_name"

# 或使用短选项
python main.py -c "https://www.youtube.com/@channel_name"

# 使用自定义配置文件
python main.py -c "频道URL" --config custom_config.yaml

# 启用调试日志
python main.py -c "频道URL" --log-level DEBUG

# 不使用缓存,重新获取所有数据
python main.py -c "频道URL" --no-cache
```

### 5. 查看结果

运行完成后,会在 `output/[频道名称]/` 目录下生成以下文件:

- `summary.md` - 频道风格总结
- `statistics.md` - 详细统计数据
- `learning_guide.md` - 学习与模仿指南
- `videos/` - 每个视频的详细分析
- `wordcloud.png` - 关键词词云图

## 📖 使用说明

### 支持的 YouTube URL 格式

- `https://www.youtube.com/@channel_name`
- `https://www.youtube.com/c/ChannelName`
- `https://www.youtube.com/channel/UCxxxxxxxxxxxxx`
- `https://www.youtube.com/user/username`

### 工作流程

1. **获取视频列表**: 从 YouTube 频道获取视频列表
2. **下载元数据和字幕**: 
   - 优先下载人工添加的字幕
   - 如果没有,下载自动生成的字幕
   - 如果都没有,下载音频准备转录
3. **音频转录**: 使用 Whisper 将音频转为文字
4. **内容分析**: 使用 AI 分析每个视频的内容和风格
5. **风格总结**: 汇总所有分析结果,提取整体特征
6. **生成知识库**: 生成 Markdown 格式的分析报告

### 缓存机制

系统会自动缓存已获取的视频数据,避免重复下载:

- 缓存位置: `data/cache/`
- 如需重新获取,使用 `--no-cache` 参数

### 性能优化建议

1. **限制视频数量**: 在 `config.yaml` 中设置 `youtube.max_videos`,例如只分析最新的 20 个视频
2. **使用较小的 Whisper 模型**: 如果只是短视频,`base` 模型已经足够
3. **使用 GPU**: 如果有 NVIDIA GPU,在 `config.yaml` 中设置 `whisper.device: "cuda"`

## 🎯 应用场景

### 1. 内容创作者

- 分析竞争对手或标杆频道的内容风格
- 学习成功频道的标题、主题、表达方式
- 了解目标受众喜欢什么样的内容

### 2. 市场研究

- 分析特定领域的内容趋势
- 了解某个细分市场的内容特点
- 发现内容创作的机会点

### 3. 学习模仿

- 系统化学习优秀频道的创作技巧
- 理解如何构建吸引人的内容
- 借鉴成功的标题和结构模式

## 🛠️ 技术架构

### 核心模块

```
youtube_an/
├── modules/
│   ├── youtube_fetcher.py       # 视频数据获取
│   ├── audio_transcriber.py     # 音频转录(Whisper)
│   ├── content_analyzer.py      # 内容分析(GPT/Claude)
│   ├── style_summarizer.py      # 风格总结
│   └── knowledge_base_generator.py  # 知识库生成
├── main.py                      # 主程序入口
├── config.yaml                  # 配置文件
└── requirements.txt             # 依赖包列表
```

### 技术栈

- **yt-dlp**: YouTube 视频下载和元数据提取
- **OpenAI Whisper**: 免费的音频转文字(本地运行)
- **OpenAI GPT / Anthropic Claude**: AI 内容分析
- **WordCloud**: 词云生成
- **jieba**: 中文分词

## ❓ 常见问题

> 💡 **遇到问题?** 查看详细的 [故障排除指南](TROUBLESHOOTING.md)

### Q: 需要付费吗?

A: 
- **完全免费**: yt-dlp 和 Whisper 都是开源免费的
- **可选付费**: 如果使用 OpenAI GPT 或 Claude 进行 AI 分析,需要 API 费用
- **免费替代**: 不配置 API 密钥时,系统会使用关键词分析(免费但分析深度有限)

### Q: 分析一个频道需要多长时间?

A:
- **获取数据**: 1-5 分钟(取决于视频数量)
- **音频转录**: 每个视频约 1-3 分钟(取决于时长和模型大小)
- **AI 分析**: 每个视频约 5-10 秒(使用 API)
- **总计**: 20 个视频约 10-30 分钟

### Q: 如何减少 API 费用?

A:
1. 限制分析的视频数量(`config.yaml` 中的 `max_videos`)
2. 使用更便宜的模型(如 `gpt-3.5-turbo` 而不是 `gpt-4`)
3. 使用关键词分析模式(不调用 API)

### Q: Whisper 转录准确吗?

A:
- **中文**: `base` 模型准确度约 80-90%,`small` 模型约 90-95%
- **英文**: 准确度更高,`base` 模型约 90-95%
- **建议**: 对于重要项目,可使用 `small` 或 `medium` 模型

### Q: 支持哪些语言?

A: 
- Whisper 支持 99 种语言
- 可在 `config.yaml` 中设置 `whisper.language`
- 设置为 `auto` 可自动检测语言

### Q: 遇到 HTTP 403 错误怎么办?

A: HTTP 403 是最常见的问题,通常是因为 YouTube 的反爬虫机制。

**快速解决**:
```bash
# 1. 更新 yt-dlp 到最新版(最重要!)
pip install --upgrade yt-dlp

# 2. 重新运行
python main.py -c "频道URL"
```

更多解决方案请查看 [故障排除指南](TROUBLESHOOTING.md#http-403-错误)

### Q: 遇到其他错误怎么办?

A:
1. 查看日志文件: `logs/youtube_analyzer.log`
2. 使用 `--log-level DEBUG` 获取详细日志
3. 查看 [故障排除指南](TROUBLESHOOTING.md)
4. 运行 `python test_setup.py` 检查环境
5. 确保 Python 版本 >= 3.8

## 📝 配置文件详解

### config.yaml 主要配置项

```yaml
# API 配置
api:
  openai:
    api_key: ""           # OpenAI API 密钥
    model: "gpt-3.5-turbo"  # 使用的模型

# Whisper 配置
whisper:
  model: "base"          # 模型大小: tiny/base/small/medium/large
  language: "zh"         # 语言: zh(中文)/en(英文)/auto(自动)
  device: "cpu"          # 设备: cpu 或 cuda

# YouTube 配置
youtube:
  max_videos: 50         # 最多分析视频数(0=不限制)
  subtitle_languages: ["zh-Hans", "zh", "en"]  # 字幕语言优先级

# 分析配置
analysis:
  use_ai: true          # 是否使用 AI(false 则用关键词)
  ai_provider: "openai"  # AI 提供商: openai/anthropic
  min_subtitle_length: 50  # 最少字幕长度

# 知识库配置
knowledge_base:
  generate_wordcloud: true  # 是否生成词云
  include_video_details: true  # 是否包含视频详情

# 系统配置
system:
  cache_enabled: true    # 是否启用缓存
  log_level: "INFO"      # 日志级别
  max_workers: 3         # 并发线程数
```

## 🔄 更新日志

### v1.0.0 (2025-10-29)

- ✅ 初始版本发布
- ✅ 支持 YouTube 频道视频获取
- ✅ 支持字幕下载和音频转录
- ✅ 支持 AI 内容分析
- ✅ 支持风格总结和知识库生成
- ✅ 完整的文档和配置

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

## 💡 提示

- 首次使用 Whisper 时会自动下载模型文件(约 100MB-3GB,取决于模型大小)
- 建议在稳定的网络环境下运行
- 分析大型频道时建议分批处理(设置 `max_videos`)
- 生成的知识库可以用任何 Markdown 阅读器查看

## 🎉 开始使用

```bash
# 快速开始
python main.py -c "https://www.youtube.com/@your_favorite_channel"
```

祝你使用愉快!如有问题,请查看日志文件或提交 Issue。

