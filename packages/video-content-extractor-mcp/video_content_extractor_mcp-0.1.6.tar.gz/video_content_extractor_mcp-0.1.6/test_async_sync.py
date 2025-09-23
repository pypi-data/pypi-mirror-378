#!/usr/bin/env python3
"""
测试同步和异步处理模式的功能
"""

import os
import sys
import json
import time
import tempfile
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from video_content_extractor_mcp.main import (
    extract_audio_from_video,
    trim_video,
    extract_video_frames,
    extract_scene_change_frames,
    query_task_progress,
    get_file_size_mb
)


def create_test_video(size_mb=1):
    """创建一个指定大小的测试视频文件"""
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, f"test_video_{size_mb}mb.mp4")
    
    # 使用 ffmpeg 创建一个测试视频
    import subprocess
    
    # 计算视频时长，使其达到指定大小（大概估算）
    duration = max(1, size_mb * 2)  # 简单估算
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"testsrc=duration={duration}:size=320x240:rate=1",
        "-f", "lavfi",
        "-i", f"sine=frequency=1000:duration={duration}",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        video_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"创建测试视频: {video_path} (目标大小: {size_mb}MB, 实际大小: {get_file_size_mb(video_path):.2f}MB)")
        return video_path
    except subprocess.CalledProcessError as e:
        print(f"创建测试视频失败: {e}")
        return None


def test_sync_mode():
    """测试同步模式（小文件）"""
    print("\n=== 测试同步模式 (小文件 < 50MB) ===")
    
    # 创建小文件
    small_video = create_test_video(size_mb=1)
    if not small_video:
        print("无法创建小测试视频，跳过同步模式测试")
        return
    
    try:
        # 测试音频提取
        print("测试音频提取...")
        result = extract_audio_from_video(small_video, "/tmp/test_audio.wav")
        print(f"音频提取结果: {result}")
        
        # 测试视频裁剪
        print("测试视频裁剪...")
        result = trim_video(small_video, "/tmp/test_trimmed.mp4", "00:00:00", "00:00:05")
        print(f"视频裁剪结果: {result}")
        
        # 测试场景关键帧提取
        print("测试场景关键帧提取...")
        os.makedirs("/tmp/test_scenes", exist_ok=True)
        result = extract_scene_change_frames(small_video, "/tmp/test_scenes", scene_threshold=0.3)
        print(f"场景关键帧提取结果: {result}")
        
    except Exception as e:
        print(f"同步模式测试失败: {e}")
    finally:
        # 清理
        if os.path.exists(small_video):
            os.remove(small_video)


def test_async_mode():
    """测试异步模式（大文件）"""
    print("\n=== 测试异步模式 (大文件 >= 50MB) ===")
    
    # 创建大文件
    large_video = create_test_video(size_mb=60)
    if not large_video:
        print("无法创建大测试视频，跳过异步模式测试")
        return
    
    try:
        # 测试音频提取（异步）
        print("测试异步音频提取...")
        result = extract_audio_from_video(large_video, "/tmp/test_audio_async.wav")
        print(f"异步音频提取结果: {result}")
        
        # 解析任务ID
        if result.startswith("{"):
            task_info = json.loads(result)
            task_id = task_info.get("task_id")
            
            if task_id:
                print(f"任务ID: {task_id}")
                
                # 查询任务进度
                for i in range(10):  # 最多查询10次
                    time.sleep(2)
                    progress_result = query_task_progress(task_id)
                    progress_info = json.loads(progress_result)
                    
                    print(f"进度查询 {i+1}: {progress_info}")
                    
                    if progress_info.get("status") in ["completed", "failed"]:
                        break
        
        # 测试视频裁剪（异步）
        print("\n测试异步视频裁剪...")
        result = trim_video(large_video, "/tmp/test_trimmed_async.mp4", "00:00:00", "00:00:10")
        print(f"异步视频裁剪结果: {result}")
        
        # 测试场景关键帧提取（异步）
        print("\n测试异步场景关键帧提取...")
        os.makedirs("/tmp/test_scenes_async", exist_ok=True)
        result = extract_scene_change_frames(large_video, "/tmp/test_scenes_async", scene_threshold=0.3)
        print(f"异步场景关键帧提取结果: {result}")
        
    except Exception as e:
        print(f"异步模式测试失败: {e}")
    finally:
        # 清理
        if os.path.exists(large_video):
            os.remove(large_video)


def main():
    """主测试函数"""
    print("开始测试同步和异步处理模式...")
    
    # 检查 ffmpeg 是否可用
    try:
        import subprocess
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到 ffmpeg，请先安装 ffmpeg")
        return
    
    # 测试同步模式
    test_sync_mode()
    
    # 测试异步模式
    test_async_mode()
    
    print("\n测试完成！")


if __name__ == "__main__":
    main()