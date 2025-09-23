from mcp.server.fastmcp import FastMCP, Context
import ffmpeg
import os  # For checking file existence if needed, though ffmpeg handles it
import shutil  # For cleaning up temporary directories
import logging
from logging.handlers import RotatingFileHandler
import uuid
import glob
import re
import tempfile
import threading
import time
import subprocess
from pathlib import Path
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Any, Optional



# 配置日志输出到stderr，避免干扰MCP通信
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 防止 basicConfig 被早期初始化抵消

# 使用用户临时目录存放日志文件
log_dir = Path(tempfile.gettempdir()) / "video-content-extractor-mcp"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "debug.log"

file_handler = RotatingFileHandler(str(log_file), maxBytes=5_000_000, backupCount=3, encoding="utf-8")

file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.propagate = False

FFMPEG_BINARY = os.environ.get('FFMPEG_BINARY')
FFPROBE_BINARY = os.environ.get('FFPROBE_BINARY')

# 异步任务管理
task_manager = {}
task_lock = threading.Lock()
executor = ProcessPoolExecutor(max_workers=2)

def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def generate_task_id() -> str:
    """生成唯一任务ID"""
    return str(uuid.uuid4())

def update_task_status(task_id: str, status: str, progress: float = 0.0, result: Any = None, error: str = None):
    """更新任务状态"""
    with task_lock:
        if task_id in task_manager:
            task_manager[task_id].update({
                'status': status,
                'progress': progress,
                'updated_at': time.time(),
                'result': result,
                'error': error
            })

def create_task(task_id: str, operation: str, params: Dict[str, Any]):
    """创建新任务"""
    with task_lock:
        task_manager[task_id] = {
            'id': task_id,
            'operation': operation,
            'params': params,
            'status': 'pending',
            'progress': 0.0,
            'created_at': time.time(),
            'updated_at': time.time(),
            'result': None,
            'error': None
        }

def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """获取任务状态"""
    with task_lock:
        return task_manager.get(task_id)

def execute_ffmpeg_async(task_id: str, operation: str, stream_spec, operation_name: str = "Processing", **kwargs):
    """在子进程中异步执行ffmpeg操作"""
    try:
        update_task_status(task_id, 'running', 0.1)
        
        # 设置默认参数
        if 'overwrite_output' not in kwargs:
            kwargs['overwrite_output'] = True
        
        # 执行ffmpeg命令
        update_task_status(task_id, 'running', 0.5)
        result = ffmpeg.run(stream_spec, **kwargs)
        
        update_task_status(task_id, 'completed', 1.0, result=f"{operation_name}完成")
        return f"{operation_name}完成"
        
    except ffmpeg.Error as e:
        error_msg = f"{operation_name}失败: {str(e)}"
        update_task_status(task_id, 'failed', 0.0, error=error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"{operation_name}异常: {str(e)}"
        update_task_status(task_id, 'failed', 0.0, error=error_msg)
        return error_msg


# --- ffmpeg/ffprobe helpers that always use resolved binaries ---
def _ffmpeg_run(stream_spec, **kwargs):
    """Run ffmpeg with an explicit binary path to avoid env propagation issues."""
    if 'overwrite_output' not in kwargs:
        kwargs['overwrite_output'] = True
    return ffmpeg.run(stream_spec, cmd=FFMPEG_BINARY, **kwargs)


def _ffmpeg_run_async(stream_spec, **kwargs):
    """Run ffmpeg asynchronously with explicit binary path."""
    return ffmpeg.run_async(stream_spec, cmd=FFMPEG_BINARY, **kwargs)


def _ffprobe_probe(path: str, **kwargs):
    """Probe media with explicit ffprobe binary."""
    return ffmpeg.probe(path, cmd=FFPROBE_BINARY, **kwargs)


def _ffmpeg_run_with_progress(stream_spec, operation_name: str = "Processing", ctx: Context = None, **kwargs):
    """Run ffmpeg with progress notifications to prevent timeout."""
    if 'overwrite_output' not in kwargs:
        kwargs['overwrite_output'] = True
    
    # Start ffmpeg process asynchronously
    process = _ffmpeg_run_async(stream_spec, pipe_stderr=True, **kwargs)
    
    # Progress monitoring thread
    def monitor_progress():
        if ctx:
            progress = 0
            while process.poll() is None:
                ctx.report_progress(progress, f"{operation_name}... {progress}%")
                time.sleep(2)  # Report progress every 2 seconds
                progress = min(progress + 10, 90)  # Increment progress up to 90%
            
            # Final progress report
            if process.returncode == 0:
                ctx.report_progress(100, f"{operation_name} completed successfully")
            else:
                ctx.report_progress(100, f"{operation_name} failed")
    
    # Start monitoring thread if context is provided
    if ctx:
        monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
        monitor_thread.start()
    
    # Wait for process to complete
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        error_message = stderr.decode('utf8') if stderr else "Unknown error"
        raise ffmpeg.Error('ffmpeg', stdout, stderr)
    
    return process


def _prepare_path(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        raise RuntimeError(f"Error: Input file not found at {input_path}")
    try:
        parent_dir = os.path.dirname(output_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Error creating output directory for {output_path}: {str(e)}")
    if os.path.exists(output_path):
        raise RuntimeError(
            f"Error: Output file already exists at {output_path}. Please choose a different path or delete the existing file.")


# Create an MCP server instance
mcp = FastMCP("VideoMaterialExtraction")


@mcp.tool()
def extract_audio_from_video(video_path: str, output_audio_path: str, audio_codec: str = 'mp3', ctx: Context = None) -> str:
    """从视频文件中提取音频。

    Args:
        video_path: 输入视频文件路径。
        output_audio_path: 输出音频文件路径。
        audio_codec: 音频编码格式（如 'mp3'、'aac'、'wav'、'flac'）。

    Returns:
        对于小文件（<50MB）：直接返回成功消息
        对于大文件（>=50MB）：返回包含任务ID的JSON字符串，可用于查询进度
    """
    _prepare_path(video_path, output_audio_path)
    # 校验音频编码格式
    valid_codecs = {'mp3', 'aac', 'wav', 'flac', 'm4a', 'ogg', 'wma'}
    if audio_codec not in valid_codecs:
        raise RuntimeError(f"Error: Invalid audio_codec '{audio_codec}'. Supported: {', '.join(sorted(valid_codecs))}")

    # 检查输入文件
    if not os.path.exists(video_path):
        raise RuntimeError(f"Error: Input video file not found at {video_path}")
    
    # 检查文件大小，决定同步还是异步处理
    file_size_mb = get_file_size_mb(video_path)
    
    if file_size_mb < 50.0:
        # 小文件，同步处理
        try:
            logger.info(f"抽取视频 {video_path} 中的音频到 {output_audio_path} ，音频格式 {audio_codec} (同步处理，文件大小: {file_size_mb:.1f}MB)")
            try:
                exists = os.path.exists(video_path)
                readable = os.access(video_path, os.R_OK)
                size = os.path.getsize(video_path) if exists else 'N/A'
                logger.info(f"输入文件检查: exists={exists} readable={readable} size={size}")
            except Exception as _e:
                logger.info(f"输入文件检查失败: {str(_e)}")
            
            if ctx:
                ctx.report_progress(0, "开始提取音频...")
            
            input_stream = ffmpeg.input(video_path)
            output_stream = input_stream.output(output_audio_path, acodec=audio_codec)
            _ffmpeg_run_with_progress(output_stream, ctx=ctx, operation_name="音频提取")
            return f"Audio extracted successfully to {output_audio_path}"
        except ffmpeg.Error as e:
            error_message = e.stderr.decode('utf8') if e.stderr else str(e)
            raise RuntimeError(f"Error extracting audio: {error_message}")
        except FileNotFoundError as e:
            # 可能是 ffmpeg 可执行文件未找到，也可能是输入文件不存在
            msg = str(e)
            logger.info(f"FileNotFoundError: {msg}")
            logger.info(f"os.path.basename(FFMPEG_BINARY): {os.path.basename(FFMPEG_BINARY)}")
            if isinstance(FFMPEG_BINARY, str) and (FFMPEG_BINARY in msg or os.path.basename(FFMPEG_BINARY) in msg):
                raise RuntimeError(f"Error: ffmpeg 可执行文件未找到或不可执行。当前设置 FFMPEG_BINARY={FFMPEG_BINARY}")
            raise RuntimeError(f"Error: Input video file not found at {video_path}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {str(e)}")
    else:
        # 大文件，异步处理
        task_id = generate_task_id()
        params = {
            'video_path': video_path,
            'output_audio_path': output_audio_path,
            'audio_codec': audio_codec,
            'file_size_mb': file_size_mb
        }
        
        create_task(task_id, 'extract_audio_from_video', params)
        
        logger.info(f"启动异步音频提取任务 {task_id}，文件大小: {file_size_mb:.1f}MB")
        
        # 提交异步任务
        input_stream = ffmpeg.input(video_path)
        output_stream = input_stream.output(output_audio_path, acodec=audio_codec)
        
        future = executor.submit(execute_ffmpeg_async, task_id, 'extract_audio_from_video', output_stream, "音频提取")
        
        return json.dumps({
            "message": "大文件异步处理已启动",
            "task_id": task_id,
            "file_size_mb": f"{file_size_mb:.1f}",
            "status": "pending",
            "note": "请使用 query_task_progress 工具查询处理进度"
        }, ensure_ascii=False, indent=2)


@mcp.tool()
def trim_video(video_path: str, output_video_path: str, start_time: str, end_time: str, ctx: Context = None) -> str:
    """按指定时间范围裁剪视频片段。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        start_time: 开始时间（支持 'HH:MM:SS' 或秒数）。
        end_time: 结束时间（支持 'HH:MM:SS' 或秒数）。

    Returns:
        对于小文件（<50MB）：直接返回成功消息
        对于大文件（>=50MB）：返回包含任务ID的JSON字符串，可用于查询进度
    """
    _prepare_path(video_path, output_video_path)
    # 简单时间格式校验
    import re
    for time_val, name in [(start_time, 'start_time'), (end_time, 'end_time')]:
        if not re.match(r'^\d+(\.\d+)?$|^\d{1,2}:\d{2}:\d{2}(\.\d+)?$', str(time_val)):
            raise RuntimeError(f"Error: Invalid {name} format '{time_val}'. Expected 'HH:MM:SS' or seconds.")
    
    # 检查文件大小，决定同步还是异步处理
    file_size_mb = get_file_size_mb(video_path)
    
    if file_size_mb < 50.0:
        # 小文件，同步处理
        try:
            if ctx:
                ctx.report_progress(0, "开始裁剪视频...")
            
            input_stream = ffmpeg.input(video_path, ss=start_time, to=end_time)
            # Attempt to copy codecs to avoid re-encoding if possible
            output_stream = input_stream.output(output_video_path, c='copy')
            _ffmpeg_run_with_progress(output_stream, ctx=ctx, operation_name="视频裁剪")
            return f"Video trimmed successfully (codec copy) to {output_video_path}"
        except ffmpeg.Error as e:
            error_message_copy = e.stderr.decode('utf8') if e.stderr else str(e)
            try:
                # Fallback to re-encoding if codec copy fails
                input_stream_recode = ffmpeg.input(video_path, ss=start_time, to=end_time)
                output_stream_recode = input_stream_recode.output(output_video_path)
                _ffmpeg_run_with_progress(output_stream_recode, ctx=ctx, operation_name="视频裁剪")
                return f"Video trimmed successfully (re-encoded) to {output_video_path}"
            except ffmpeg.Error as e_recode:
                error_message_recode = e_recode.stderr.decode('utf8') if e_recode.stderr else str(e_recode)
                raise RuntimeError(
                    f"Error trimming video. Copy attempt: {error_message_copy}. Re-encode attempt: {error_message_recode}")
        except FileNotFoundError:
            raise RuntimeError(f"Error: Input video file not found at {video_path}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {str(e)}")
    else:
        # 大文件，异步处理
        task_id = generate_task_id()
        params = {
            'video_path': video_path,
            'output_video_path': output_video_path,
            'start_time': start_time,
            'end_time': end_time,
            'file_size_mb': file_size_mb
        }
        
        create_task(task_id, 'trim_video', params)
        
        logger.info(f"启动异步视频裁剪任务 {task_id}，文件大小: {file_size_mb:.1f}MB")
        
        # 提交异步任务 - 先尝试codec copy
        input_stream = ffmpeg.input(video_path, ss=start_time, to=end_time)
        output_stream = input_stream.output(output_video_path, c='copy')
        
        future = executor.submit(execute_ffmpeg_async, task_id, 'trim_video', output_stream, "视频裁剪")
        
        return json.dumps({
            "message": "大文件异步处理已启动",
            "task_id": task_id,
            "file_size_mb": f"{file_size_mb:.1f}",
            "status": "pending",
            "note": "请使用 query_task_progress 工具查询处理进度"
        }, ensure_ascii=False, indent=2)


@mcp.tool()
def extract_video_frames(
        video_path: str,
        output_dir: str,
        image_format: str = "png",
        interval_seconds: float | None = None,
        extract_first: bool = False,
        extract_last: bool = False,
        width: int | None = None,
        height: int | None = None,
        ctx: Context = None,
) -> str:
    """从视频中按间隔或特定位置提取帧为图片。

    Args:
        video_path: 输入视频路径。
        output_dir: 输出目录（会自动创建）。
        image_format: 输出图片格式，如 'png'|'jpg'|'webp'。默认 'png'。
        interval_seconds: 间隔秒数；大于 0 时启用按间隔提取。
        extract_first: 是否额外导出首帧。
        extract_last: 是否额外导出末帧。
        width: 可选，缩放输出宽度。
        height: 可选，缩放输出高度。

    Returns:
        对于小文件（<50MB）：直接返回成功消息
        对于大文件（>=50MB）：返回包含任务ID的JSON字符串，可用于查询进度
    """
    _prepare_path(video_path, output_dir)
    # 校验图片格式
    valid_formats = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}
    if image_format not in valid_formats:
        raise RuntimeError(
            f"Error: Invalid image_format '{image_format}'. Supported: {', '.join(sorted(valid_formats))}")

    # 校验间隔参数
    if interval_seconds is not None and interval_seconds <= 0:
        raise RuntimeError("Error: interval_seconds must be positive.")

    # 校验尺寸参数
    if width is not None and width <= 0:
        raise RuntimeError("Error: width must be positive.")
    if height is not None and height <= 0:
        raise RuntimeError("Error: height must be positive.")
    
    # 检查文件大小，决定同步还是异步处理
    file_size_mb = get_file_size_mb(video_path)
    
    if file_size_mb < 50.0:
        # 小文件，同步处理
        return _extract_video_frames_sync(video_path, output_dir, image_format, interval_seconds, 
                                        extract_first, extract_last, width, height, ctx, file_size_mb)
    else:
        # 大文件，异步处理
        task_id = generate_task_id()
        params = {
            'video_path': video_path,
            'output_dir': output_dir,
            'image_format': image_format,
            'interval_seconds': interval_seconds,
            'extract_first': extract_first,
            'extract_last': extract_last,
            'width': width,
            'height': height,
            'file_size_mb': file_size_mb
        }
        
        create_task(task_id, 'extract_video_frames', params)
        
        logger.info(f"启动异步视频帧提取任务 {task_id}，文件大小: {file_size_mb:.1f}MB")
        
        # 异步执行帧提取
        future = executor.submit(_extract_video_frames_async, task_id, video_path, output_dir, image_format, 
                               interval_seconds, extract_first, extract_last, width, height)
        
        return json.dumps({
            "message": "大文件异步处理已启动",
            "task_id": task_id,
            "file_size_mb": f"{file_size_mb:.1f}",
            "status": "pending",
            "note": "请使用 query_task_progress 工具查询处理进度"
        }, ensure_ascii=False, indent=2)


def _extract_video_frames_sync(video_path: str, output_dir: str, image_format: str, interval_seconds: float | None,
                              extract_first: bool, extract_last: bool, width: int | None, height: int | None, 
                              ctx: Context, file_size_mb: float) -> str:
    """同步执行视频帧提取"""
    try:
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")

        if not (interval_seconds and interval_seconds > 0) and not extract_first and not extract_last:
            raise RuntimeError("Error: 需至少指定一种提取方式（interval_seconds>0 或 extract_first/extract_last 任一）。")

        os.makedirs(output_dir, exist_ok=True)

        # 统一的文件前缀，避免与既有文件冲突
        prefix = f"frames_{uuid.uuid4().hex[:8]}"
        created_files: list[str] = []

        # 可选获取视频时长（末帧提取需要）
        video_duration_sec = None
        if extract_last:
            try:
                probe = _ffprobe_probe(video_path)
                video_duration_sec = float(probe["format"]["duration"]) if "format" in probe and "duration" in probe[
                    "format"] else None
            except Exception:
                video_duration_sec = None

        # 1) 按固定时间间隔导出
        if interval_seconds and interval_seconds > 0:
            if ctx:
                ctx.report_progress(10, "开始按间隔提取帧...")
            fps_val = 1.0 / float(interval_seconds)
            input_stream = ffmpeg.input(video_path)
            v = input_stream.video.filter("fps", fps=fps_val)
            if width or height:
                scale_w = width if width else -1
                scale_h = height if height else -1
                v = v.filter("scale", scale_w, scale_h)
            pattern = os.path.join(output_dir, f"{prefix}_%06d.{image_format}")
            _ffmpeg_run_with_progress(ffmpeg.output(v, pattern, vsync="vfr"), ctx=ctx, operation_name="间隔帧提取")
            created_files.extend(sorted(glob.glob(os.path.join(output_dir, f"{prefix}_*.{image_format}"))))

        # 2) 首帧导出
        if extract_first:
            if ctx:
                ctx.report_progress(50, "提取首帧...")
            first_path = os.path.join(output_dir, f"{prefix}_first.{image_format}")
            v1 = ffmpeg.input(video_path, ss=0)
            vf = v1.video
            if width or height:
                scale_w = width if width else -1
                scale_h = height if height else -1
                vf = vf.filter("scale", scale_w, scale_h)
            _ffmpeg_run(ffmpeg.output(vf, first_path, vframes=1), capture_stdout=True, capture_stderr=True)
            created_files.append(first_path)

        # 3) 末帧导出（取接近末尾的一帧，避免 EOF 边界）
        if extract_last:
            if ctx:
                ctx.report_progress(80, "提取末帧...")
            if video_duration_sec is None or video_duration_sec <= 0:
                raise RuntimeError("Error: Failed to resolve video duration for last-frame extraction.")
            # 留出 10ms 作为缓冲，确保命中末尾有效帧
            last_ts = max(video_duration_sec - 0.01, 0)
            last_path = os.path.join(output_dir, f"{prefix}_last.{image_format}")
            v2 = ffmpeg.input(video_path, ss=last_ts)
            vf2 = v2.video
            if width or height:
                scale_w = width if width else -1
                scale_h = height if height else -1
                vf2 = vf2.filter("scale", scale_w, scale_h)
            _ffmpeg_run(ffmpeg.output(vf2, last_path, vframes=1), capture_stdout=True, capture_stderr=True)
            created_files.append(last_path)

        if not created_files:
            raise RuntimeError("Error: No frames were produced. Please check parameters.")

        if ctx:
            ctx.report_progress(100, "帧提取完成")

        return (
            f"Frames extracted successfully (同步处理，文件大小: {file_size_mb:.1f}MB). Count={len(created_files)}. "
            f"Output dir='{output_dir}', prefix='{prefix}'."
        )
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error extracting frames: {error_message}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in extract_video_frames: {str(e)}")


def _extract_video_frames_async(task_id: str, video_path: str, output_dir: str, image_format: str, 
                               interval_seconds: float | None, extract_first: bool, extract_last: bool, 
                               width: int | None, height: int | None) -> str:
    """异步执行视频帧提取"""
    try:
        update_task_status(task_id, "running", 0.0)
        
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")

        if not (interval_seconds and interval_seconds > 0) and not extract_first and not extract_last:
            raise RuntimeError("Error: 需至少指定一种提取方式（interval_seconds>0 或 extract_first/extract_last 任一）。")

        os.makedirs(output_dir, exist_ok=True)

        # 统一的文件前缀，避免与既有文件冲突
        prefix = f"frames_{uuid.uuid4().hex[:8]}"
        created_files: list[str] = []

        # 可选获取视频时长（末帧提取需要）
        video_duration_sec = None
        if extract_last:
            try:
                probe = _ffprobe_probe(video_path)
                video_duration_sec = float(probe["format"]["duration"]) if "format" in probe and "duration" in probe[
                    "format"] else None
            except Exception:
                video_duration_sec = None

        # 1) 按固定时间间隔导出
        if interval_seconds and interval_seconds > 0:
            update_task_status(task_id, "running", 10.0)
            fps_val = 1.0 / float(interval_seconds)
            input_stream = ffmpeg.input(video_path)
            v = input_stream.video.filter("fps", fps=fps_val)
            if width or height:
                scale_w = width if width else -1
                scale_h = height if height else -1
                v = v.filter("scale", scale_w, scale_h)
            pattern = os.path.join(output_dir, f"{prefix}_%06d.{image_format}")
            _ffmpeg_run(ffmpeg.output(v, pattern, vsync="vfr"), capture_stdout=True, capture_stderr=True)
            created_files.extend(sorted(glob.glob(os.path.join(output_dir, f"{prefix}_*.{image_format}"))))

        # 2) 首帧导出
        if extract_first:
            update_task_status(task_id, "running", 50.0)
            first_path = os.path.join(output_dir, f"{prefix}_first.{image_format}")
            v1 = ffmpeg.input(video_path, ss=0)
            vf = v1.video
            if width or height:
                scale_w = width if width else -1
                scale_h = height if height else -1
                vf = vf.filter("scale", scale_w, scale_h)
            _ffmpeg_run(ffmpeg.output(vf, first_path, vframes=1), capture_stdout=True, capture_stderr=True)
            created_files.append(first_path)

        # 3) 末帧导出（取接近末尾的一帧，避免 EOF 边界）
        if extract_last:
            update_task_status(task_id, "running", 80.0)
            if video_duration_sec is None or video_duration_sec <= 0:
                raise RuntimeError("Error: Failed to resolve video duration for last-frame extraction.")
            # 留出 10ms 作为缓冲，确保命中末尾有效帧
            last_ts = max(video_duration_sec - 0.01, 0)
            last_path = os.path.join(output_dir, f"{prefix}_last.{image_format}")
            v2 = ffmpeg.input(video_path, ss=last_ts)
            vf2 = v2.video
            if width or height:
                scale_w = width if width else -1
                scale_h = height if height else -1
                vf2 = vf2.filter("scale", scale_w, scale_h)
            _ffmpeg_run(ffmpeg.output(vf2, last_path, vframes=1), capture_stdout=True, capture_stderr=True)
            created_files.append(last_path)

        if not created_files:
            raise RuntimeError("Error: No frames were produced. Please check parameters.")

        result = (
            f"Frames extracted successfully (异步处理). Count={len(created_files)}. "
            f"Output dir='{output_dir}', prefix='{prefix}'."
        )
        
        update_task_status(task_id, "completed", 100.0, result)
        return result
        
    except Exception as e:
        error_msg = str(e)
        update_task_status(task_id, "failed", 0.0, None, error_msg)
        raise RuntimeError(f"异步帧提取失败: {error_msg}")


@mcp.tool()
def extract_scene_change_frames(
        video_path: str,
        output_dir: str,
        image_format: str = "png",
        scene_threshold: float = 0.4,
        min_scene_gap_seconds: float | None = None,
        max_frames: int | None = None,
        width: int | None = None,
        height: int | None = None,
        ctx: Context = None,
) -> str:
    """基于画面变化检测提取场景切换关键帧。

    Args:
        video_path: 输入视频路径。
        output_dir: 输出目录（会自动创建）。
        image_format: 输出图片格式，如 'png'|'jpg'|'webp'。默认 'png'。
        scene_threshold: 场景变化阈值（0.0~1.0，典型值 0.3~0.5）。
        min_scene_gap_seconds: 连续关键帧之间的最小时间间隔。
        max_frames: 最多导出的关键帧数量。
        width: 可选，缩放输出宽度。
        height: 可选，缩放输出高度。

    Returns:
        小文件（<50MB）: 直接返回成功消息
        大文件（>=50MB）: 返回包含任务ID的JSON字符串，可用于查询进度
    """
    # 检查文件大小，决定同步还是异步处理
    file_size_mb = get_file_size_mb(video_path)
    
    if file_size_mb < 50:
        # 小文件，同步处理
        return _extract_scene_change_frames_sync(
            video_path, output_dir, image_format, scene_threshold,
            min_scene_gap_seconds, max_frames, width, height, ctx
        )
    else:
        # 大文件，异步处理
        task_id = generate_task_id()
        params = {
            'video_path': video_path,
            'output_dir': output_dir,
            'image_format': image_format,
            'scene_threshold': scene_threshold,
            'min_scene_gap_seconds': min_scene_gap_seconds,
            'max_frames': max_frames,
            'width': width,
            'height': height
        }
        
        create_task(task_id, "extract_scene_change_frames", params)
        
        # 提交异步任务
        future = executor.submit(
            _extract_scene_change_frames_async,
            task_id, video_path, output_dir, image_format, scene_threshold,
            min_scene_gap_seconds, max_frames, width, height
        )
        
        return json.dumps({
            "message": f"场景关键帧提取任务已创建（文件大小: {file_size_mb:.1f}MB）",
            "task_id": task_id,
            "status": "processing",
            "file_size_mb": file_size_mb
        }, ensure_ascii=False, indent=2)


def _extract_scene_change_frames_sync(
        video_path: str,
        output_dir: str,
        image_format: str = "png",
        scene_threshold: float = 0.4,
        min_scene_gap_seconds: float | None = None,
        max_frames: int | None = None,
        width: int | None = None,
        height: int | None = None,
        ctx: Context = None,
) -> str:
    """同步处理场景关键帧提取（小文件）"""
    _prepare_path(video_path, output_dir)
    # 校验参数
    valid_formats = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}
    if image_format not in valid_formats:
        raise RuntimeError(
            f"Error: Invalid image_format '{image_format}'. Supported: {', '.join(sorted(valid_formats))}")

    if not (0.0 <= scene_threshold <= 1.0):
        raise RuntimeError(f"Error: scene_threshold must be between 0.0 and 1.0, got {scene_threshold}")

    if min_scene_gap_seconds is not None and min_scene_gap_seconds <= 0:
        raise RuntimeError("Error: min_scene_gap_seconds must be positive.")

    if max_frames is not None and max_frames <= 0:
        raise RuntimeError("Error: max_frames must be positive.")

    if width is not None and width <= 0:
        raise RuntimeError("Error: width must be positive.")
    if height is not None and height <= 0:
        raise RuntimeError("Error: height must be positive.")
    try:
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")

        os.makedirs(output_dir, exist_ok=True)

        # 获取视频时长，末尾边界安全
        duration = None
        try:
            probe = _ffprobe_probe(video_path)
            duration = float(probe["format"].get("duration", 0.0)) if "format" in probe else None
        except Exception:
            duration = None

        if ctx:
            ctx.report_progress(10, "开始检测场景变化...")
        
        # 第一遍：用 select+showinfo 找到候选时间戳
        detect_spec = (
            ffmpeg
            .input(video_path)
            .video
            .filter("select", f"gt(scene,{scene_threshold})")
            .filter("showinfo")
            .output("-", format="null")
        )
        detect_proc = _ffmpeg_run_async(detect_spec, pipe_stderr=True)
        _, stderr_bytes = detect_proc.communicate()
        stderr_str = stderr_bytes.decode("utf8")

        # showinfo 行内形如 ... pts_time:12.345 ...
        times = [float(x) for x in re.findall(r"pts_time:(\d+(?:\.\d+)?)", stderr_str)]
        if not times:
            return "No scene-change frames detected."

        # 二次去重：最小间隔
        filtered_times: list[float] = []
        last_kept = None
        gap = float(min_scene_gap_seconds) if (min_scene_gap_seconds and min_scene_gap_seconds > 0) else None
        for t in sorted(times):
            if duration is not None:
                t = min(max(t, 0.0), max(duration - 0.01, 0.0))
            if last_kept is None:
                filtered_times.append(t)
                last_kept = t
                continue
            if gap is None or (t - last_kept) >= gap:
                filtered_times.append(t)
                last_kept = t

        # 限制最大数量
        if max_frames and max_frames > 0:
            filtered_times = filtered_times[:max_frames]

        if not filtered_times:
            return "No scene-change frames after gap/limit filtering."

        prefix = f"scenes_{uuid.uuid4().hex[:8]}"
        created_files: list[str] = []

        if ctx:
            ctx.report_progress(50, "开始提取场景关键帧...")
        
        # 第二遍：逐时间戳抽帧
        for idx, ts in enumerate(filtered_times, start=1):
            out_path = os.path.join(output_dir, f"{prefix}_{idx:06d}.{image_format}")
            inp = ffmpeg.input(video_path, ss=ts)
            vf = inp.video
            if width or height:
                scale_w = width if width else -1
                scale_h = height if height else -1
                vf = vf.filter("scale", scale_w, scale_h)
            _ffmpeg_run(ffmpeg.output(vf, out_path, vframes=1), capture_stdout=True, capture_stderr=True)
            created_files.append(out_path)
            
            if ctx:
                progress = 50 + int((idx / len(filtered_times)) * 40)
                ctx.report_progress(progress, f"已提取 {idx}/{len(filtered_times)} 帧...")

        if ctx:
            ctx.report_progress(100, "场景关键帧提取完成")
        
        return (
            f"Scene-change frames extracted. Count={len(created_files)}. "
            f"Output dir='{output_dir}', prefix='{prefix}'. "
            f"File size: {get_file_size_mb(video_path):.1f}MB (processed synchronously)"
        )
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error extracting scene-change frames: {error_message}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in extract_scene_change_frames: {str(e)}")


def _extract_scene_change_frames_async(
        task_id: str,
        video_path: str,
        output_dir: str,
        image_format: str = "png",
        scene_threshold: float = 0.4,
        min_scene_gap_seconds: float | None = None,
        max_frames: int | None = None,
        width: int | None = None,
        height: int | None = None,
) -> str:
    """异步处理场景关键帧提取（大文件）"""
    try:
        update_task_status(task_id, "processing", 0.0)
        
        _prepare_path(video_path, output_dir)
        # 校验参数
        valid_formats = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}
        if image_format not in valid_formats:
            raise RuntimeError(
                f"Error: Invalid image_format '{image_format}'. Supported: {', '.join(sorted(valid_formats))}")

        if not (0.0 <= scene_threshold <= 1.0):
            raise RuntimeError(f"Error: scene_threshold must be between 0.0 and 1.0, got {scene_threshold}")

        if min_scene_gap_seconds is not None and min_scene_gap_seconds <= 0:
            raise RuntimeError("Error: min_scene_gap_seconds must be positive.")

        if max_frames is not None and max_frames <= 0:
            raise RuntimeError("Error: max_frames must be positive.")

        if width is not None and width <= 0:
            raise RuntimeError("Error: width must be positive.")
        if height is not None and height <= 0:
            raise RuntimeError("Error: height must be positive.")
            
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")

        os.makedirs(output_dir, exist_ok=True)

        # 获取视频时长，末尾边界安全
        duration = None
        try:
            probe = _ffprobe_probe(video_path)
            duration = float(probe["format"].get("duration", 0.0)) if "format" in probe else None
        except Exception:
            duration = None

        update_task_status(task_id, "processing", 10.0)
        
        # 第一遍：用 select+showinfo 找到候选时间戳
        detect_spec = (
            ffmpeg
            .input(video_path)
            .video
            .filter("select", f"gt(scene,{scene_threshold})")
            .filter("showinfo")
            .output("-", format="null")
        )
        detect_proc = _ffmpeg_run_async(detect_spec, pipe_stderr=True)
        _, stderr_bytes = detect_proc.communicate()
        stderr_str = stderr_bytes.decode("utf8")

        # showinfo 行内形如 ... pts_time:12.345 ...
        times = [float(x) for x in re.findall(r"pts_time:(\d+(?:\.\d+)?)", stderr_str)]
        if not times:
            result = "No scene-change frames detected."
            update_task_status(task_id, "completed", 100.0, result)
            return result

        # 二次去重：最小间隔
        filtered_times: list[float] = []
        last_kept = None
        gap = float(min_scene_gap_seconds) if (min_scene_gap_seconds and min_scene_gap_seconds > 0) else None
        for t in sorted(times):
            if duration is not None:
                t = min(max(t, 0.0), max(duration - 0.01, 0.0))
            if last_kept is None:
                filtered_times.append(t)
                last_kept = t
                continue
            if gap is None or (t - last_kept) >= gap:
                filtered_times.append(t)
                last_kept = t

        # 限制最大数量
        if max_frames and max_frames > 0:
            filtered_times = filtered_times[:max_frames]

        if not filtered_times:
            result = "No scene-change frames after gap/limit filtering."
            update_task_status(task_id, "completed", 100.0, result)
            return result

        prefix = f"scenes_{uuid.uuid4().hex[:8]}"
        created_files: list[str] = []

        update_task_status(task_id, "processing", 50.0)
        
        # 第二遍：逐时间戳抽帧
        for idx, ts in enumerate(filtered_times, start=1):
            out_path = os.path.join(output_dir, f"{prefix}_{idx:06d}.{image_format}")
            inp = ffmpeg.input(video_path, ss=ts)
            vf = inp.video
            if width or height:
                scale_w = width if width else -1
                scale_h = height if height else -1
                vf = vf.filter("scale", scale_w, scale_h)
            _ffmpeg_run(ffmpeg.output(vf, out_path, vframes=1), capture_stdout=True, capture_stderr=True)
            created_files.append(out_path)
            
            # 更新进度
            progress = 50 + int((idx / len(filtered_times)) * 40)
            update_task_status(task_id, "processing", progress)

        result = (
            f"Scene-change frames extracted. Count={len(created_files)}. "
            f"Output dir='{output_dir}', prefix='{prefix}'. "
            f"File size: {get_file_size_mb(video_path):.1f}MB (processed asynchronously)"
        )
        update_task_status(task_id, "completed", 100.0, result)
        return result
        
    except Exception as e:
        error_msg = str(e)
        update_task_status(task_id, "failed", 0.0, None, error_msg)
        raise RuntimeError(f"异步场景关键帧提取失败: {error_msg}")


@mcp.tool()
def query_task_progress(task_id: str, ctx: Context = None) -> str:
    """查询异步任务的进度和状态
    
    Args:
        task_id: 任务ID
        ctx: MCP上下文对象
        
    Returns:
        包含任务状态信息的JSON字符串
    """
    task_info = get_task_status(task_id)
    
    if not task_info:
        return json.dumps({
            "error": "任务不存在",
            "task_id": task_id
        }, ensure_ascii=False, indent=2)
    
    # 格式化时间戳
    created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task_info['created_at']))
    updated_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task_info['updated_at']))
    
    result = {
        "task_id": task_info['id'],
        "operation": task_info['operation'],
        "status": task_info['status'],
        "progress": f"{task_info['progress']:.1%}",
        "created_at": created_time,
        "updated_at": updated_time
    }
    
    if task_info['result']:
        result["result"] = task_info['result']
    
    if task_info['error']:
        result["error"] = task_info['error']
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """Main entry point for the MCP server."""
    mcp.run()


# Main execution block to run the server
if __name__ == "__main__":
    main()