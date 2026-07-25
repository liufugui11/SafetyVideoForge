"""
背景音乐服务
支持：本地音乐库 / AI音乐生成 / 免版权音乐
"""
import os
import random
from typing import Optional, List, Dict
from pathlib import Path

from pydub import AudioSegment
from loguru import logger

from app.config import settings


class MusicService:
    """背景音乐服务"""
    
    # 安全生产视频推荐音乐风格
    SAFETY_MOODS = {
        "serious": ["严肃", "警示", "正式"],       # 规范讲解
        "urgent": ["紧张", "紧迫", "警示"],        # 事故案例
        "hopeful": ["希望", "积极", "温暖"],       # 安全承诺
        "educational": ["轻快", "清晰", "平和"],   # 知识科普
    }
    
    def __init__(self, music_library_dir: str = None):
        self.library_dir = Path(music_library_dir or settings.DATA_DIR / "music_library")
        self.library_dir.mkdir(parents=True, exist_ok=True)
        
        # 扫描音乐库
        self.tracks = self._scan_library()
    
    def _scan_library(self) -> List[Dict]:
        """扫描音乐库"""
        tracks = []
        
        if not self.library_dir.exists():
            return tracks
        
        for ext in ["*.mp3", "*.wav", "*.m4a"]:
            for path in self.library_dir.glob(ext):
                tracks.append({
                    "path": str(path),
                    "name": path.stem,
                    "format": path.suffix.lstrip("."),
                })
        
        logger.info(f"🎵 音乐库扫描完成: {len(tracks)} 首")
        return tracks
    
    def get_track(self, mood: str = "educational", duration: int = 60) -> Optional[str]:
        """
        根据情绪选择合适背景音乐
        
        Args:
            mood: 情绪标签
            duration: 目标时长(秒)
        
        Returns:
            音乐文件路径
        """
        if not self.tracks:
            logger.warning("音乐库为空")
            return None
        
        # 简单随机选择（实际应按标签匹配）
        track = random.choice(self.tracks)
        return track["path"]
    
    def generate_silence(self, duration: int, output_path: str) -> str:
        """生成静音文件"""
        silent = AudioSegment.silent(duration=duration * 1000)
        silent.export(output_path, format="mp3")
        return output_path
    
    def loop_to_duration(self, track_path: str, target_duration: int, 
                         output_path: str, fade_in: int = 2000, 
                         fade_out: int = 3000) -> str:
        """
        循环音乐到指定时长
        
        Args:
            track_path: 原音乐路径
            target_duration: 目标时长(秒)
            output_path: 输出路径
            fade_in: 淡入时长(ms)
            fade_out: 淡出时长(ms)
        
        Returns:
            输出路径
        """
        track = AudioSegment.from_file(track_path)
        target_ms = target_duration * 1000
        
        # 循环
        looped = AudioSegment.silent(duration=0)
        while len(looped) < target_ms:
            looped += track
        
        # 裁剪到目标长度
        looped = looped[:target_ms]
        
        # 淡入淡出
        looped = looped.fade_in(fade_in).fade_out(fade_out)
        
        # 调整音量 (BGM应比旁白低)
        looped = looped - 18  # 降低18dB
        
        looped.export(output_path, format="mp3", bitrate="192k")
        logger.info(f"🎵 BGM生成完成: {output_path}")
        
        return output_path
    
    def get_library_info(self) -> Dict:
        """获取音乐库信息"""
        return {
            "total_tracks": len(self.tracks),
            "library_dir": str(self.library_dir),
            "tracks": [{"name": t["name"], "format": t["format"]} for t in self.tracks]
        }
