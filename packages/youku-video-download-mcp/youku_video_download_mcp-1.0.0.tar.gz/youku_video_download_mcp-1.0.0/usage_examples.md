# 优酷视频下载使用示例

## Claude Desktop 配置

将以下配置添加到 Claude Desktop 的配置文件中：

```json
{
  "mcpServers": {
    "youku-video-download-mcp": {
      "name": "Youku Video Download MCP",
      "type": "stdio", 
      "description": "Youku video downloader for downloading videos from Youku platform",
      "isActive": true,
      "registryUrl": "",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/youku_video_download_mcp",
        "run",
        "python", 
        "-m",
        "youku_video_download_mcp.server"
      ]
    }
  }
}
```

## 对话示例

### 获取优酷视频信息

**用户**: 请帮我查看这个优酷视频的信息：https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html

**Claude**: 我来帮您获取这个优酷视频的信息。

*使用 get_video_info 工具*

根据获取的信息，这个优酷视频的详细信息如下：
- 标题: 测试视频标题
- 平台: 优酷
- 格式: MP4 视频
- 大小: 约 12.5 MB
- 类型: MPEG-4 视频
- 可用清晰度: hd3 (1080P), hd2 (超清), mp4hd (高清), mp4sd (标清)

### 下载优酷视频（基础）

**用户**: 请把这个优酷视频下载到我的下载文件夹：https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html

**Claude**: 我来帮您下载这个优酷视频。

*使用 download_video 工具*

视频已成功下载到您指定的目录！下载的文件信息：
- 下载状态: 成功
- 输出目录: /Users/username/Downloads
- 下载文件: video_title.mp4
- 文件大小: [具体大小]

### 下载优酷视频（指定清晰度与登录 cookies）

**用户**: 请以超清下载这个优酷视频到桌面，并使用我的 cookies：
https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html

**Claude**: 我来按超清下载，并使用 cookies 进行登录。

*使用 download_video 工具（带 format 与 cookies_path）*

请求参数示例：
```json
{
  "tool": "download_video",
  "params": {
    "url": "https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html",
    "output_dir": "/Users/username/Desktop",
    "format": "hd2",
    "cookies_path": "/Users/username/Desktop/cookies.txt"
  }
}
```

如果目标清晰度需要登录且 cookies 不可用，工具会抛出异常，外层返回 `isError=true`。

### 批量处理优酷视频

**用户**: 我有几个优酷视频链接，请先帮我查看信息，然后下载质量最好的版本：
1. https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html
2. https://player.youku.com/embed/XNDQ5OTUxMjQ4
3. https://list.youku.com/show/id_XXXXXX.html

**Claude**: 我来逐个处理这些优酷视频链接。

首先获取所有视频的信息：

*依次使用 get_video_info 工具获取每个视频的信息*

现在开始下载这些视频：

*依次使用 download_video 工具下载每个视频*

所有视频都已成功处理完成！

## 支持的优酷链接格式示例

### 视频页面链接
```
# 标准视频页面
https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html

# 带参数的视频页面
https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html?spm=a2h0c.8166622.PhoneSokuProgram_1.dselectbutton_1&showid=XXXXXX
```

### 播放器链接
```
# 播放器PHP链接
https://player.youku.com/player.php/sid/XNDQ5OTUxMjQ4/v.swf

# 嵌入播放器链接
https://player.youku.com/embed/XNDQ5OTUxMjQ4

# 加载器链接
https://loader.swf?VideoIDS=XNDQ5OTUxMjQ4
```

### 节目和专辑链接
```
# 节目列表
https://list.youku.com/show/id_XXXXXX.html

# 专辑列表
https://list.youku.com/albumlist/show/id_XXXXXX.html
```

## 常见问题

### Q: 如何处理需要登录的优酷视频？
A: 某些优酷视频可能需要登录才能访问高清版本。you-get 支持使用 cookies 文件，您可以：
1. 从浏览器导出优酷的 cookies
2. 在调用工具时指定 cookies 文件路径

### Q: 优酷视频下载失败怎么办？
A: 常见原因和解决方法：
1. 网络连接问题 - 检查网络连接
2. 视频被删除或私有 - 确认视频链接有效
3. 优酷平台限制 - 可能有地理或时间限制
4. 需要登录 - 某些高清视频需要登录优酷账号
5. you-get 版本过旧 - 更新 you-get 到最新版本

### Q: 如何选择优酷视频质量？
A: 优酷支持多种清晰度，可以：
1. 先使用 get_video_info 查看可用格式
2. 使用 format 参数指定清晰度：hd3 (1080P), hd2 (超清), mp4hd (高清), mp4sd (标清)

### Q: 支持批量下载优酷节目列表吗？
A: 是的，支持优酷节目列表和专辑列表的批量下载。对于包含多个视频的列表URL，工具会自动处理。

## 高级使用

### 自定义下载目录结构
您可以在对话中指定更复杂的下载需求：

**用户**: 请将这些优酷视频按清晰度分类下载到不同文件夹中

**Claude**: 我来为您按清晰度分类下载这些优酷视频...
- 1080P视频 → /Downloads/Youku/1080P/
- 超清视频 → /Downloads/Youku/超清/
- 高清视频 → /Downloads/Youku/高清/
- 标清视频 → /Downloads/Youku/标清/

### 优酷节目列表下载
**用户**: 请下载这个优酷节目的所有剧集

**Claude**: 我来下载优酷节目的所有剧集...
*使用相应的工具和参数进行处理*

## 注意事项

1. **版权合规**: 请确保您有权下载和使用相关优酷视频内容
2. **存储空间**: 下载前确保有足够的磁盘空间
3. **网络流量**: 注意下载大文件时的网络流量消耗
4. **优酷条款**: 遵守优酷平台的使用条款和限制
5. **登录要求**: 某些高清视频可能需要登录优酷账号
