# 使用示例

本文档提供 YouTube 视频分析系统的详细使用示例。

## 基础示例

### 1. 分析单个频道

最简单的用法,分析一个 YouTube 频道:

```bash
python main.py -c "https://www.youtube.com/@channel_name"
```

### 2. 限制分析视频数量

只分析最新的 10 个视频(节省时间和费用):

```bash
# 修改 config.yaml 中的 max_videos 为 10
python main.py -c "https://www.youtube.com/@channel_name"
```

或者创建自定义配置文件:

```yaml
# custom_config.yaml
youtube:
  max_videos: 10
```

然后运行:

```bash
python main.py -c "频道URL" --config custom_config.yaml
```

### 3. 不使用 AI 分析(免费模式)

如果没有 API 密钥或想节省费用,可以使用关键词分析模式:

```yaml
# 在 config.yaml 中设置
analysis:
  use_ai: false
```

### 4. 启用详细日志

调试或查看详细运行信息:

```bash
python main.py -c "频道URL" --log-level DEBUG
```

### 5. 强制重新获取数据

不使用缓存,重新下载所有数据:

```bash
python main.py -c "频道URL" --no-cache
```

## 高级示例

### 1. 使用 GPU 加速 Whisper

如果你有 NVIDIA GPU,可以大幅提升转录速度:

```yaml
# config.yaml
whisper:
  model: "small"  # 可以使用更大的模型
  device: "cuda"  # 使用 GPU
```

### 2. 使用更精确的 Whisper 模型

对于重要的分析项目:

```yaml
# config.yaml
whisper:
  model: "medium"  # 或 "large"
  language: "zh"
```

### 3. 分析英文频道

```yaml
# config.yaml
whisper:
  language: "en"

youtube:
  subtitle_languages: ["en", "en-US"]
```

### 4. 使用 Claude 进行分析

```yaml
# config.yaml
api:
  anthropic:
    api_key: "your_claude_api_key"
    model: "claude-3-haiku-20240307"

analysis:
  ai_provider: "anthropic"
```

## 完整工作流示例

### 场景: 分析一个美食频道

```bash
# 1. 首先配置(修改 config.yaml)
cat > config.yaml << EOF
youtube:
  max_videos: 30  # 分析最新 30 个视频
  subtitle_languages: ["zh-Hans", "zh", "en"]

whisper:
  model: "base"
  language: "zh"
  device: "cpu"

analysis:
  use_ai: true
  ai_provider: "openai"

knowledge_base:
  generate_wordcloud: true
  include_video_details: true
EOF

# 2. 设置 API 密钥
echo "OPENAI_API_KEY=your_key_here" > .env

# 3. 运行分析
python main.py -c "https://www.youtube.com/@food_channel"

# 4. 查看结果
cd output/food_channel/
ls -la
# 会看到:
# - summary.md
# - statistics.md  
# - learning_guide.md
# - videos/
# - wordcloud.png
```

## 批量分析多个频道

创建一个脚本来分析多个频道:

```bash
#!/bin/bash
# analyze_multiple.sh

channels=(
  "https://www.youtube.com/@channel1"
  "https://www.youtube.com/@channel2"
  "https://www.youtube.com/@channel3"
)

for channel in "${channels[@]}"
do
  echo "正在分析: $channel"
  python main.py -c "$channel"
  echo "完成: $channel"
  echo "------------------------"
done

echo "所有频道分析完成!"
```

运行:

```bash
chmod +x analyze_multiple.sh
./analyze_multiple.sh
```

## Python 脚本集成

如果要在自己的 Python 脚本中使用:

```python
import yaml
from modules import (
    YouTubeFetcher,
    AudioTranscriber,
    ContentAnalyzer,
    StyleSummarizer,
    KnowledgeBaseGenerator
)

# 加载配置
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 获取视频数据
fetcher = YouTubeFetcher(config)
videos = fetcher.fetch_all("https://www.youtube.com/@channel_name")

# 转录音频(如需要)
transcriber = AudioTranscriber(config)
for video in videos:
    if video.get('needs_transcription'):
        audio_file = video.get('audio_file')
        result = transcriber.transcribe(audio_file)
        video['subtitle_text'] = result['text']

# 分析内容
analyzer = ContentAnalyzer(config)
analyses = analyzer.analyze_batch(videos)

# 总结风格
summarizer = StyleSummarizer(config)
summary = summarizer.summarize(analyses)

# 生成知识库
generator = KnowledgeBaseGenerator(config)
output_dir = generator.generate(
    "channel_name",
    summary,
    analyses,
    videos
)

print(f"知识库已生成: {output_dir}")
```

## 输出示例

运行成功后,你会看到类似这样的输出:

```
============================================================
   YouTube 视频分析系统
   Video Content Analyzer & Knowledge Base Generator
============================================================

[步骤 1/6] 获取频道视频数据...
✓ 成功获取 25 个视频数据

[步骤 2/6] 处理音频转录...
✓ 所有视频都有字幕,无需转录

[步骤 3/6] 分析视频内容...
✓ 成功分析 25/25 个视频

[步骤 4/6] 总结频道风格...
✓ 风格总结完成

【频道风格简报】
  主要类型: 美食
  主要受众: 美食爱好者
  高频主题: 烹饪技巧, 食材选择, 菜谱分享

[步骤 5/6] 生成知识库...
✓ 知识库已生成

[步骤 6/6] 完成!

============================================================
✨ 分析完成! 知识库已生成
============================================================

📂 输出目录: output/美食频道/

生成的文件:
  - summary.md           (频道风格总结)
  - statistics.md        (详细统计数据)
  - learning_guide.md    (学习与模仿指南)
  - videos/              (各视频详细分析)
  - wordcloud.png        (关键词词云图)

可以查看这些文件来了解频道的风格特点!
```

## 故障排除

### 问题 1: 无法下载视频

```bash
# 确保 yt-dlp 是最新版本
pip install --upgrade yt-dlp

# 检查网络连接
curl -I https://www.youtube.com
```

### 问题 2: Whisper 转录失败

```bash
# 检查是否安装了 ffmpeg
ffmpeg -version

# 如果没有,安装 ffmpeg
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Windows:
# 从 https://ffmpeg.org/download.html 下载
```

### 问题 3: API 调用失败

```bash
# 检查 API 密钥是否正确
echo $OPENAI_API_KEY

# 测试 API 连接
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 问题 4: 内存不足

如果遇到内存错误:

```yaml
# config.yaml
whisper:
  model: "tiny"  # 使用最小模型

youtube:
  max_videos: 10  # 减少视频数量

system:
  max_workers: 1  # 减少并发数
```

## 最佳实践

1. **首次测试**: 先用 `max_videos: 5` 测试,确保一切正常
2. **API 费用控制**: 使用 `gpt-3.5-turbo` 而不是 `gpt-4`
3. **定期清理**: 定期清理 `data/` 目录下的缓存文件
4. **备份输出**: 重要的分析结果记得备份
5. **查看日志**: 遇到问题先查看 `logs/youtube_analyzer.log`

## 技巧和窍门

### 快速分析(只看概览)

```yaml
knowledge_base:
  include_video_details: false  # 不生成详细视频分析
  generate_wordcloud: false      # 不生成词云
```

### 只下载数据不分析

修改代码或创建自己的脚本:

```python
from modules import YouTubeFetcher
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

fetcher = YouTubeFetcher(config)
videos = fetcher.fetch_all("频道URL")

# 数据已保存在 data/cache/ 中
print(f"下载了 {len(videos)} 个视频的数据")
```

### 导出为 JSON

如果需要 JSON 格式的结果:

```python
import json

# 在生成知识库后
with open('output/channel_name/data.json', 'w', encoding='utf-8') as f:
    json.dump({
        'summary': summary,
        'analyses': analyses,
        'videos': videos
    }, f, ensure_ascii=False, indent=2)
```

---

更多问题和建议,请查看主 README.md 或提交 Issue。

