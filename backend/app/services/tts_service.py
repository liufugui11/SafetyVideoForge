"""
TTS 语音合成服务
支持：Edge TTS (免费本地) / 火山引擎TTS / 其他在线TTS
"""
import os
import asyncio
from typing import Optional, Dict, List
from pathlib import Path

import edge_tts
from pydub import AudioSegment
from loguru import logger

from app.config import settings


class TTSService:
    """TTS服务"""
    
    # Edge TTS 中文音色映射
    EDGE_VOICES = {
        "zh-CN-XiaoxiaoNeural": "晓晓 (女声, 通用)",
        "zh-CN-XiaoyiNeural": "晓伊 (女声, 活泼)",
        "zh-CN-YunjianNeural": "云健 (男声, 新闻)",
        "zh-CN-YunxiNeural": "云希 (男声, 年轻)",
        "zh-CN-YunxiaNeural": "云夏 (男声, 少年)",
        "zh-CN-YunyangNeural": "云扬 (男声, 专业)",
        "zh-CN-liaoning-XiaobeiNeural": "晓北 (东北话女声)",
        "zh-CN-shaanxi-XiaoniNeural": "晓妮 (陕西话女声)",
    }
    
    # 安全生产场景推荐音色
    SAFETY_RECOMMENDED_VOICES = [
        "zh-CN-YunyangNeural",   # 专业男声 - 首选
        "zh-CN-XiaoxiaoNeural",  # 通用女声 - 备选
        "zh-CN-YunjianNeural",   # 新闻男声 - 正式场景
    ]
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or settings.TEMP_DIR / "audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def synthesize(
        self,
        text: str,
        voice: str = "zh-CN-YunyangNeural",
        rate: str = "+0%",     # 语速
        volume: str = "+0%",   # 音量
        output_filename: Optional[str] = None
    ) -> str:
        """
        合成语音
        
        Args:
            text: 要合成的文本
            voice: 音色
            rate: 语速调整 (+10% / -10%)
            volume: 音量调整
            output_filename: 输出文件名
        
        Returns:
            输出音频文件路径
        """
        if not output_filename:
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            output_filename = f"tts_{voice.replace('-', '_')}_{text_hash}.mp3"
        
        output_path = self.output_dir / output_filename
        
        # 如果已存在则直接返回
        if output_path.exists():
            logger.debug(f"🎯 TTS缓存命中: {output_filename}")
            return str(output_path)
        
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume
            )
            await communicate.save(str(output_path))
            
            logger.info(f"🔊 TTS合成完成: {output_filename} ({len(text)}字)")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ TTS合成失败: {e}")
            raise
    
    async def synthesize_scenes(
        self,
        scenes: List[Dict[str, Any]],
        voice: str = "zh-CN-YunyangNeural",
        output_prefix: str = "scene"
    ) -> List[str]:
        """
        批量合成场景旁白
        
        Args:
            scenes: 场景列表，每个包含 narration 字段
            voice: 音色
            output_prefix: 输出文件名前缀
        
        Returns:
            音频文件路径列表
        """
        tasks = []
        for i, scene in enumerate(scenes):
            narration = scene.get("narration", "")
            if not narration.strip():
                continue
            
            filename = f"{output_prefix}_{i+1:03d}.mp3"
            task = self.synthesize(narration, voice=voice, output_filename=filename)
            tasks.append(task)
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        audio_paths = []
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"场景旁白合成失败: {r}")
                audio_paths.append(None)
            else:
                audio_paths.append(r)
        
        return audio_paths
    
    async def merge_narrations(
        self,
        audio_paths: List[str],
        scene_durations: List[float],
        output_path: str,
        bgm_path: Optional[str] = None,
        bgm_volume: float = -20  # dB
    ) -> str:
        """
        合并旁白音频，按场景时长对齐，可选添加背景音乐
        
        Args:
            audio_paths: 旁白音频路径列表
            scene_durations: 各场景目标时长(秒)
            output_path: 输出路径
            bgm_path: 背景音乐路径
            bgm_volume: 背景音乐音量(dB)
        
        Returns:
            合并后的音频路径
        """
        from pydub import AudioSegment
        
        final_audio = AudioSegment.silent(duration=0)
        
        for i, (audio_path, duration) in enumerate(zip(audio_paths, scene_durations)):
            if not audio_path or not os.path.exists(audio_path):
                # 缺失音频，用静音填充
                segment = AudioSegment.silent(duration=int(duration * 1000))
            else:
                segment = AudioSegment.from_file(audio_path)
                target_ms = int(duration * 1000)
                
                # 调整长度：长了截断，短了补静音
                if len(segment) > target_ms:
                    segment = segment[:target_ms]
                elif len(segment) < target_ms:
                    segment = segment + AudioSegment.silent(duration=target_ms - len(segment))
            
            final_audio += segment
        
        # 叠加背景音乐
        if bgm_path and os.path.exists(bgm_path):
            bgm = AudioSegment.from_file(bgm_path)
            # 循环BGM以匹配总时长
            while len(bgm) < len(final_audio):
                bgm += bgm
            bgm = bgm[:len(final_audio)]
            bgm = bgm + bgm_volume  # 调整音量
            
            final_audio = final_audio.overlay(bgm)
        
        final_audio.export(output_path, format="mp3", bitrate="192k")
        logger.info(f"🎵 音频合并完成: {output_path}")
        
        return output_path
    
    def get_available_voices(self) -> Dict[str, str]:
        """获取可用音色列表"""
        return self.EDGE_VOICES.copy()
    
    def get_recommended_voices(self) -> List[str]:
        """获取安全生产场景推荐音色"""
        return self.SAFETY_RECOMMENDED_VOICES.copy()
