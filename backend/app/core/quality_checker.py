"""
质检模块 - 视频质量检查与评分
"""
import os
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import cv2
import numpy as np
from pydub import AudioSegment
from loguru import logger


@dataclass
class QualityReport:
    """质检报告"""
    overall_score: float           # 总分 0-100
    video_score: float             # 视频质量分
    audio_score: float             # 音频质量分
    content_score: float           # 内容质量分
    
    # 详细指标
    resolution_ok: bool
    fps_ok: bool
    duration_ok: bool
    audio_level_ok: bool
    audio_sync_ok: bool
    
    # 问题列表
    issues: List[Dict[str, Any]]
    suggestions: List[str]


class QualityChecker:
    """质量检查器"""
    
    # 质量标准
    MIN_RESOLUTION = (720, 1280)   # 最低分辨率 720p竖屏
    TARGET_RESOLUTION = (1080, 1920)  # 目标分辨率
    MIN_FPS = 24
    TARGET_FPS = 30
    MIN_DURATION = 15
    MAX_DURATION = 300
    TARGET_AUDIO_DB = -14          # 目标音量 LUFS
    
    def __init__(self):
        self.issues = []
        self.suggestions = []
    
    async def check_video(self, video_path: str, 
                         script_text: str = "") -> QualityReport:
        """
        检查视频质量
        
        Args:
            video_path: 视频文件路径
            script_text: 原始文案(用于内容检查)
        
        Returns:
            质检报告
        """
        self.issues = []
        self.suggestions = []
        
        if not os.path.exists(video_path):
            return self._create_error_report(f"视频文件不存在: {video_path}")
        
        # 视频基本参数检查
        video_info = self._analyze_video_stream(video_path)
        
        # 音频检查
        audio_info = self._analyze_audio_stream(video_path)
        
        # 评分
        video_score = self._score_video(video_info)
        audio_score = self._score_audio(audio_info)
        content_score = self._score_content(script_text)
        
        overall = (video_score * 0.4 + audio_score * 0.3 + content_score * 0.3)
        
        report = QualityReport(
            overall_score=round(overall, 1),
            video_score=round(video_score, 1),
            audio_score=round(audio_score, 1),
            content_score=round(content_score, 1),
            resolution_ok=video_info.get("width", 0) >= self.MIN_RESOLUTION[0],
            fps_ok=video_info.get("fps", 0) >= self.MIN_FPS,
            duration_ok=self.MIN_DURATION <= video_info.get("duration", 0) <= self.MAX_DURATION,
            audio_level_ok=audio_info.get("volume_ok", False),
            audio_sync_ok=True,  # 简化处理
            issues=self.issues,
            suggestions=self.suggestions
        )
        
        logger.info(f"🔍 质检完成: 总分 {report.overall_score}/100")
        return report
    
    def _analyze_video_stream(self, path: str) -> Dict[str, Any]:
        """分析视频流"""
        cap = cv2.VideoCapture(path)
        
        if not cap.isOpened():
            return {"error": "无法打开视频文件"}
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        info = {
            "width": width,
            "height": height,
            "fps": fps,
            "frame_count": frame_count,
            "duration": duration,
            "aspect_ratio": width / height if height > 0 else 0,
        }
        
        # 分辨率检查
        if width < self.MIN_RESOLUTION[0] or height < self.MIN_RESOLUTION[1]:
            self.issues.append({
                "type": "resolution",
                "severity": "warning",
                "message": f"分辨率偏低: {width}x{height}, 建议不低于 {self.TARGET_RESOLUTION[0]}x{self.TARGET_RESOLUTION[1]}"
            })
            self.suggestions.append("使用更高分辨率素材重新生成")
        
        # FPS检查
        if fps < self.MIN_FPS:
            self.issues.append({
                "type": "fps",
                "severity": "warning",
                "message": f"帧率偏低: {fps:.1f}fps, 建议 {self.TARGET_FPS}fps"
            })
        
        # 时长检查
        if duration < self.MIN_DURATION:
            self.issues.append({
                "type": "duration",
                "severity": "warning",
                "message": f"视频过短: {duration:.1f}秒"
            })
        elif duration > self.MAX_DURATION:
            self.issues.append({
                "type": "duration",
                "severity": "info",
                "message": f"视频较长: {duration:.1f}秒, 短视频平台建议控制在3分钟内"
            })
        
        # 比例检查 (9:16竖屏)
        expected_ratio = 9 / 16
        actual_ratio = width / height if height > 0 else 0
        if abs(actual_ratio - expected_ratio) > 0.1:
            self.issues.append({
                "type": "aspect_ratio",
                "severity": "warning",
                "message": f"画面比例非标准竖屏(9:16): 当前 {width}:{height}"
            })
            self.suggestions.append("调整为9:16竖屏比例以适配视频号")
        
        return info
    
    def _analyze_audio_stream(self, path: str) -> Dict[str, Any]:
        """分析音频流"""
        try:
            audio = AudioSegment.from_file(path)
            
            # 计算音量(dBFS)
            dbfs = audio.dBFS
            
            # 判断音量是否合适
            volume_ok = -20 <= dbfs <= -10
            
            info = {
                "duration_ms": len(audio),
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "dbfs": dbfs,
                "volume_ok": volume_ok,
            }
            
            if not volume_ok:
                severity = "warning" if dbfs < -20 else "info"
                self.issues.append({
                    "type": "audio_level",
                    "severity": severity,
                    "message": f"音量{'过低' if dbfs < -20 else '偏高'}: {dbfs:.1f}dBFS"
                })
                self.suggestions.append(f"调整音频音量至目标范围(-20 ~ -10 dBFS)")
            
            return info
            
        except Exception as e:
            logger.warning(f"音频分析失败: {e}")
            return {"error": str(e), "volume_ok": False}
    
    def _score_video(self, info: Dict[str, Any]) -> float:
        """视频质量评分"""
        score = 100.0
        
        # 分辨率扣分
        w, h = info.get("width", 0), info.get("height", 0)
        if w >= 1080 and h >= 1920:
            pass  # 满分
        elif w >= 720 and h >= 1280:
            score -= 10
        else:
            score -= 25
        
        # FPS扣分
        fps = info.get("fps", 30)
        if fps < 24:
            score -= 15
        elif fps < 30:
            score -= 5
        
        return max(0, score)
    
    def _score_audio(self, info: Dict[str, Any]) -> float:
        """音频质量评分"""
        score = 100.0
        
        if not info.get("volume_ok", True):
            score -= 15
        
        # 声道检查
        if info.get("channels", 2) < 2:
            score -= 5
            self.suggestions.append("建议输出立体声以提升观感")
        
        return max(0, score)
    
    def _score_content(self, script_text: str) -> float:
        """内容质量评分(简化版)"""
        score = 100.0
        
        if not script_text:
            return score
        
        # 字数检查
        char_count = len(script_text)
        if char_count < 50:
            score -= 20
            self.suggestions.append("文案内容偏少，建议补充更多安全知识点")
        
        # 关键词检查
        safety_keywords = ["安全", "规范", "注意", "必须", "禁止", "防护", "风险", "事故"]
        keyword_count = sum(1 for kw in safety_keywords if kw in script_text)
        if keyword_count < 2:
            score -= 10
            self.suggestions.append("建议增加安全警示关键词")
        
        return max(0, score)
    
    def _create_error_report(self, error_msg: str) -> QualityReport:
        """创建错误报告"""
        return QualityReport(
            overall_score=0,
            video_score=0,
            audio_score=0,
            content_score=0,
            resolution_ok=False,
            fps_ok=False,
            duration_ok=False,
            audio_level_ok=False,
            audio_sync_ok=False,
            issues=[{"type": "error", "severity": "critical", "message": error_msg}],
            suggestions=["请检查视频文件路径和格式"]
        )
