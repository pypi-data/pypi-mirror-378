#!/usr/bin/env python3
"""
测试集成版本的视频下载MCP服务器
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径到系统路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from video_download_mcp.server import VideoDownloadProcessor, get_video_info

def test_video_info():
    """测试获取视频信息功能"""
    print("=== 测试视频信息获取 ===")
    
    # 测试视频链接
    test_urls = [
        "https://www.bilibili.com/video/BV1xx411c7mu",
        # "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 需要翻墙
    ]
    
    for url in test_urls:
        print(f"\n测试URL: {url}")
        try:
            result = get_video_info(url)
            print("结果:")
            # 美化JSON输出
            result_dict = json.loads(result)
            print(json.dumps(result_dict, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

async def test_video_download():
    """测试视频下载功能"""
    print("\n=== 测试视频下载 ===")
    
    processor = VideoDownloadProcessor()
    
    # 测试下载一个视频（选择一个较小的视频）
    test_url = "https://www.bilibili.com/video/BV1xx411c7mu"
    print(f"测试下载URL: {test_url}")
    
    try:
        # 创建测试下载目录
        test_download_dir = Path("./test_downloads")
        test_download_dir.mkdir(exist_ok=True)
        
        result = await processor.download_video(test_url, output_dir=str(test_download_dir))
        print("下载结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"下载错误: {e}")
        import traceback
        traceback.print_exc()

def test_info_parsing():
    """测试信息解析功能"""
    print("\n=== 测试信息解析 ===")
    
    # 模拟输出
    sample_output = """Site:     Bilibili
Title:    测试视频标题
Type:     MPEG-4 video (video/mp4)
Size:     12.5 MiB (13107200 Bytes)
Real URL: https://example.com/video.mp4
"""
    
    processor = VideoDownloadProcessor()
    info = processor._parse_video_info(sample_output)
    
    print("解析结果:")
    print(json.dumps(info, ensure_ascii=False, indent=2))

def test_module_imports():
    """测试模块导入"""
    print("\n=== 测试模块导入 ===")
    
    try:
        from video_download_mcp.you_get import common
        from video_download_mcp.you_get.common import url_to_module
        from video_download_mcp.you_get.util import log
        print("✅ 核心模块导入成功")
        
        # 测试基本功能
        test_url = "https://www.bilibili.com/video/BV1xx411c7mu"
        module, processed_url = url_to_module(test_url)
        print(f"✅ URL模块解析成功: {module.__name__}")
        print(f"✅ 处理后的URL: {processed_url}")
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试集成版本的视频下载MCP服务器...")
    
    # 测试模块导入
    test_module_imports()
    
    # 测试信息解析
    test_info_parsing()
    
    # 测试视频信息获取
    test_video_info()
    
    # 测试视频下载（需要网络连接）
    print("\n注意: 视频下载测试需要网络连接，可能需要一些时间...")
    try:
        asyncio.run(test_video_download())
    except KeyboardInterrupt:
        print("\n用户中断测试")
    
    print("\n测试完成！")
