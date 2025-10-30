# 故障排除指南

本文档帮助你解决使用 YouTube 视频分析系统时遇到的常见问题。

## HTTP 403 错误

### 问题描述
```
ERROR: unable to download video data: HTTP Error 403: Forbidden
```

### 原因
YouTube 检测到自动化请求,拒绝访问。这是最常见的问题。

### 解决方案

#### 方案 1: 更新 yt-dlp (推荐)

```bash
# 升级到最新版本
pip install --upgrade yt-dlp

# 验证版本
yt-dlp --version
```

YouTube 经常更改其 API,保持 yt-dlp 最新版本很重要。

#### 方案 2: 使用代理

如果你的 IP 被限制,可以使用代理:

```yaml
# config.yaml 中添加
youtube:
  proxy: "http://your-proxy:port"
```

或使用环境变量:

```bash
export HTTP_PROXY="http://your-proxy:port"
export HTTPS_PROXY="http://your-proxy:port"
```

#### 方案 3: 减慢请求速度

```yaml
# config.yaml
youtube:
  max_videos: 10  # 减少视频数量
  sleep_interval: 2  # 每个请求之间暂停

system:
  max_workers: 1  # 减少并发数
```

#### 方案 4: 使用 Cookies

如果你有 YouTube 账号,可以使用 cookies 绕过限制:

1. 安装浏览器扩展导出 cookies
2. 保存 cookies.txt 到项目目录
3. 修改代码使用 cookies

```python
# 在 youtube_fetcher.py 的 ydl_opts 中添加:
'cookiefile': 'cookies.txt'
```

#### 方案 5: 只分析有字幕的视频

如果音频下载总是失败,可以跳过需要音频转录的视频:

```python
# 修改 main.py 中的逻辑
# 过滤掉需要转录的视频
videos_data = [v for v in videos_data if not v.get('needs_transcription', False)]
```

## 网络连接问题

### 问题: 连接超时

```
ERROR: Connection timeout
```

### 解决方案

1. **检查网络连接**:
```bash
ping youtube.com
curl -I https://www.youtube.com
```

2. **增加超时时间**:
```yaml
# config.yaml
system:
  timeout: 60  # 增加超时时间(秒)
```

3. **使用 VPN 或代理**:
某些地区可能需要 VPN 访问 YouTube。

## ffmpeg 相关问题

### 问题: ffmpeg not found

```
ERROR: ffmpeg not found
```

### 解决方案

#### macOS:
```bash
brew install ffmpeg
```

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### Windows:
1. 访问 https://ffmpeg.org/download.html
2. 下载 Windows 版本
3. 解压到某个目录
4. 添加到 PATH 环境变量

### 问题: 音频转换失败

```
ERROR: Postprocessing failed
```

### 解决方案

1. **确认 ffmpeg 版本**:
```bash
ffmpeg -version
```

2. **重新安装 ffmpeg**:
```bash
# macOS
brew reinstall ffmpeg

# Ubuntu
sudo apt-get install --reinstall ffmpeg
```

## Whisper 相关问题

### 问题: 内存不足

```
RuntimeError: CUDA out of memory
```

### 解决方案

1. **使用更小的模型**:
```yaml
# config.yaml
whisper:
  model: "tiny"  # 或 "base"
```

2. **使用 CPU**:
```yaml
whisper:
  device: "cpu"
```

3. **减少并发处理**:
```yaml
system:
  max_workers: 1
```

### 问题: Whisper 模型下载失败

```
ERROR: Failed to download model
```

### 解决方案

1. **手动下载模型**:
访问 https://github.com/openai/whisper 查看模型下载链接

2. **使用镜像**:
如果在中国大陆,可能需要使用镜像或 VPN

3. **使用更小的模型**:
```yaml
whisper:
  model: "tiny"  # 最小,下载最快
```

## API 相关问题

### 问题: OpenAI API 密钥无效

```
ERROR: Invalid API key
```

### 解决方案

1. **检查密钥格式**:
```bash
# .env 文件
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx
```

2. **验证密钥**:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

3. **使用关键词分析**:
如果不想使用 API:
```yaml
# config.yaml
analysis:
  use_ai: false
```

### 问题: API 配额超限

```
ERROR: Rate limit exceeded
```

### 解决方案

1. **减少请求频率**:
```yaml
youtube:
  max_videos: 10  # 减少分析的视频数量
```

2. **增加重试延迟**:
```yaml
system:
  retry_delay: 10  # 增加延迟
```

3. **检查账户余额**:
访问 https://platform.openai.com/account/usage

## 字幕相关问题

### 问题: 无法下载字幕

```
WARNING: 视频 xxx 没有可用的字幕
```

### 解决方案

这不是错误,只是说明视频没有字幕。系统会自动下载音频进行转录。

如果不想转录:
```yaml
youtube:
  max_videos: 50
  skip_no_subtitles: true  # 跳过无字幕视频
```

### 问题: 字幕编码错误

```
UnicodeDecodeError: 'utf-8' codec can't decode
```

### 解决方案

通常系统会自动处理。如果仍有问题,检查字幕文件:

```bash
file data/raw/subtitles/*.vtt
```

## Python 依赖问题

### 问题: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'xxx'
```

### 解决方案

1. **重新安装依赖**:
```bash
pip install -r requirements.txt
```

2. **检查虚拟环境**:
```bash
# 确保在虚拟环境中
which python
# 应该显示虚拟环境路径
```

3. **升级 pip**:
```bash
pip install --upgrade pip
```

### 问题: 版本冲突

```
ERROR: Cannot install xxx because these package versions have conflicting dependencies
```

### 解决方案

1. **创建新的虚拟环境**:
```bash
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements.txt
```

2. **使用 conda**(如果安装了):
```bash
conda create -n youtube_an python=3.9
conda activate youtube_an
pip install -r requirements.txt
```

## 性能问题

### 问题: 处理速度太慢

### 解决方案

1. **减少视频数量**:
```yaml
youtube:
  max_videos: 20
```

2. **使用 GPU** (如果有):
```yaml
whisper:
  device: "cuda"
```

3. **使用更小的 Whisper 模型**:
```yaml
whisper:
  model: "base"  # 而不是 medium/large
```

4. **跳过音频转录**:
只分析有字幕的视频

5. **使用缓存**:
```yaml
system:
  cache_enabled: true
```

### 问题: 磁盘空间不足

### 解决方案

1. **清理缓存**:
```bash
rm -rf data/cache/*
rm -rf data/raw/audio/*
```

2. **及时删除已处理的数据**:
```bash
# 分析完成后
rm -rf data/raw/audio/*
```

3. **配置自动清理**:
```yaml
system:
  auto_cleanup: true
  keep_audio: false
```

## 特定错误代码

### Error 429: Too Many Requests

**原因**: 请求过于频繁

**解决**:
- 减少并发数
- 增加请求间隔
- 使用代理

### Error 404: Not Found

**原因**: 视频不存在或已删除

**解决**:
- 系统会自动跳过
- 检查频道 URL 是否正确

### Error 500: Internal Server Error

**原因**: YouTube 服务器问题

**解决**:
- 稍后重试
- 系统会自动重试 3 次

## 获取帮助

如果以上方案都无法解决你的问题:

1. **查看日志**:
```bash
cat logs/youtube_analyzer.log
```

2. **运行诊断**:
```bash
python test_setup.py
```

3. **启用调试模式**:
```bash
python main.py -c "频道URL" --log-level DEBUG
```

4. **检查 yt-dlp**:
```bash
# 直接测试 yt-dlp
yt-dlp --list-formats "视频URL"
```

5. **提交 Issue**:
如果是 bug,请在 GitHub 提交 Issue,包含:
- 错误信息
- 日志文件
- Python 版本
- 操作系统

## 预防措施

为避免问题:

1. ✅ 定期更新 yt-dlp: `pip install --upgrade yt-dlp`
2. ✅ 保持 Python 版本 >= 3.8
3. ✅ 首次使用时从小数据集开始测试
4. ✅ 定期清理缓存和临时文件
5. ✅ 使用稳定的网络连接
6. ✅ 不要频繁请求同一个频道

## 常见配置优化

### 最稳定配置

```yaml
# config.yaml
youtube:
  max_videos: 20
  subtitle_languages: ["zh-Hans", "en"]

whisper:
  model: "base"
  device: "cpu"

analysis:
  use_ai: false  # 使用关键词分析

system:
  cache_enabled: true
  max_workers: 1
  retry_times: 3
  retry_delay: 5
```

### 最快速配置

```yaml
youtube:
  max_videos: 10

whisper:
  model: "tiny"
  device: "cuda"  # 如果有 GPU

analysis:
  use_ai: false

system:
  cache_enabled: true
  max_workers: 3
```

---

最后更新: 2025-10-29

