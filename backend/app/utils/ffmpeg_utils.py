"""
FFmpeg 工具函数
视频合成、转码、处理
"""
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from loguru import logger


def run_ffmpeg(args: List[str], check: bool = True) -> Tuple[int, str, str]:
    """
    执行FFmpeg命令
    
    Returns:
        (returncode, stdout, stderr)
    """
    cmd = ["ffmpeg", "-y"] + args
    
    logger.debug(f"FFmpeg命令: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    
    if check and result.returncode != 0:
        logger.error(f"FFmpeg错误: {result.stderr}")
        raise RuntimeError(f"FFmpeg执行失败: {result.stderr[:500]}")
    
    return result.returncode, result.stdout, result.stderr


def concat_videos(video_paths: List[str], output_path: str, 
                  transition: str = "fade") -> str:
    """
    拼接多个视频片段
    
    Args:
        video_paths: 视频路径列表
        output_path: 输出路径
        transition: 转场效果 (fade/dissolve/none)
    
    Returns:
        输出路径
    """
    if not video_paths:
        raise ValueError("视频列表为空")
    
    # 创建concat列表文件
    list_file = output_path + ".list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for path in video_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")
    
    # 使用concat demuxer
    args = [
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_path
    ]
    
    run_ffmpeg(args)
    
    # 清理临时文件
    os.remove(list_file)
    
    logger.info(f"🎬 视频拼接完成: {output_path}")
    return output_path


def add_audio_to_video(video_path: str, audio_path: str, 
                       output_path: str, audio_volume: float = 1.0) -> str:
    """
    为视频添加/替换音轨
    
    Args:
        video_path: 视频路径
        audio_path: 音频路径
        output_path: 输出路径
        audio_volume: 音量倍数
    
    Returns:
        输出路径
    """
    args = [
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]
    
    if audio_volume != 1.0:
        args = [
            "-i", video_path,
            "-i", audio_path,
            "-filter_complex", f"[1:a]volume={audio_volume}[a]",
            "-map", "0:v:0",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
    
    run_ffmpeg(args)
    logger.info(f"🎵 音轨添加完成: {output_path}")
    return output_path


def burn_subtitles(video_path: str, subtitle_path: str, 
                   output_path: str, font_size: int = 24) -> str:
    """
    烧录字幕到视频
    
    Args:
        video_path: 视频路径
        subtitle_path: 字幕文件路径(SRT/ASS)
        output_path: 输出路径
        font_size: 字体大小
    
    Returns:
        输出路径
    """
    # 使用ASS滤镜烧录字幕
    args = [
        "-i", video_path,
        "-vf", f"subtitles={subtitle_path}:force_style='FontSize={font_size},PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000'",
        "-c:a", "copy",
        output_path
    ]
    
    run_ffmpeg(args)
    logger.info(f"📝 字幕烧录完成: {output_path}")
    return output_path


def resize_video(video_path: str, output_path: str, 
                 width: int = 1080, height: int = 1920) -> str:
    """
    调整视频尺寸 (默认9:16竖屏)
    
    Args:
        video_path: 视频路径
        output_path: 输出路径
        width: 目标宽度
        height: 目标高度
    
    Returns:
        输出路径
    """
    args = [
        "-i", video_path,
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black",
        "-c:a", "copy",
        output_path
    ]
    
    run_ffmpeg(args)
    logger.info(f"📐 视频尺寸调整完成: {width}x{height}")
    return output_path


def get_video_info(video_path: str) -> dict:
    """
    获取视频信息
    
    Returns:
        视频信息字典
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration,bit_rate",
        "-show_entries", "format=duration,size,bit_rate",
        "-of", "json",
        video_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    import json
    info = json.loads(result.stdout)
    
    return info
