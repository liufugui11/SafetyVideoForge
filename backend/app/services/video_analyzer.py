"""
视频解析服务
对现有视频进行多维度分析
"""
import os
import json
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import cv2
import numpy as np
from pydub import AudioSegment
from loguru import logger


@dataclass
class VideoAnalysisReport:
    """视频解析报告"""
    # 语言风格
    language_style: Dict[str, Any]
    # 画面风格
    visual_style: Dict[str, Any]
    # 呈现效果
    presentation: Dict[str, Any]
    # 标准评级
    quality_rating: Dict[str, Any]
    # 传播效果预测
    viral_potential: Dict[str, Any]
    # 综合评分
    overall_score: float
    # 改进建议
    suggestions: List[str]


class VideoAnalyzer:
    """视频解析器"""
    
    def __init__(self):
        self.issues = []
        self.suggestions = []
    
    async def analyze(self, video_path: str) -> VideoAnalysisReport:
        """
        全面分析视频
        
        Args:
            video_path: 视频文件路径
        
        Returns:
            分析报告
        """
        self.issues = []
        self.suggestions = []
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        logger.info(f"🔍 开始分析视频: {video_path}")
        
        # 1. 基础信息提取
        basic_info = self._extract_basic_info(video_path)
        
        # 2. 画面分析
        visual_analysis = self._analyze_visuals(video_path, basic_info)
        
        # 3. 音频分析
        audio_analysis = self._analyze_audio(video_path)
        
        # 4. 综合评估
        quality_rating = self._rate_quality(basic_info, visual_analysis, audio_analysis)
        
        # 5. 传播潜力预测
        viral_potential = self._predict_viral_potential(
            basic_info, visual_analysis, audio_analysis
        )
        
        # 综合评分
        overall = (
            quality_rating.get("clarity_score", 0) * 0.3 +
            quality_rating.get("professional_score", 0) * 0.3 +
            viral_potential.get("engagement_score", 0) * 0.2 +
            visual_analysis.get("composition_score", 0) * 0.2
        )
        
        report = VideoAnalysisReport(
            language_style=self._analyze_language_style(audio_analysis),
            visual_style=visual_analysis,
            presentation=self._evaluate_presentation(basic_info, visual_analysis),
            quality_rating=quality_rating,
            viral_potential=viral_potential,
            overall_score=round(overall, 1),
            suggestions=self.suggestions
        )
        
        logger.info(f"✅ 视频分析完成: 综合评分 {report.overall_score}/100")
        return report
    
    def _extract_basic_info(self, path: str) -> Dict[str, Any]:
        """提取基础信息"""
        cap = cv2.VideoCapture(path)
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        file_size = os.path.getsize(path) / (1024 * 1024)  # MB
        
        info = {
            "width": width,
            "height": height,
            "fps": round(fps, 2),
            "frame_count": frame_count,
            "duration": round(duration, 2),
            "file_size_mb": round(file_size, 2),
            "aspect_ratio": round(width / height, 3) if height > 0 else 0,
            "bitrate_mbps": round(file_size * 8 / duration, 2) if duration > 0 else 0,
        }
        
        return info
    
    def _analyze_visuals(self, path: str, basic_info: Dict) -> Dict[str, Any]:
        """画面分析"""
        cap = cv2.VideoCapture(path)
        
        # 采样帧进行分析
        total_frames = basic_info["frame_count"]
        sample_indices = [int(i * total_frames / 10) for i in range(10)]
        
        brightness_values = []
        saturation_values = []
        contrast_values = []
        
        for idx in sample_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            
            # 转换到HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # 亮度
            brightness = np.mean(hsv[:, :, 2])
            brightness_values.append(brightness)
            
            # 饱和度
            saturation = np.mean(hsv[:, :, 1])
            saturation_values.append(saturation)
            
            # 对比度 (标准差)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            contrast = np.std(gray)
            contrast_values.append(contrast)
        
        cap.release()
        
        avg_brightness = np.mean(brightness_values) if brightness_values else 0
        avg_saturation = np.mean(saturation_values) if saturation_values else 0
        avg_contrast = np.mean(contrast_values) if contrast_values else 0
        
        # 色调判断
        tone = self._determine_tone(avg_brightness, avg_saturation, avg_contrast)
        
        # 构图评分 (简化)
        composition_score = min(100, avg_contrast / 2)
        
        # 清晰度评分
        clarity_score = min(100, basic_info.get("width", 0) / 10)
        
        analysis = {
            "tone": tone,
            "avg_brightness": round(avg_brightness, 1),
            "avg_saturation": round(avg_saturation, 1),
            "avg_contrast": round(avg_contrast, 1),
            "composition_score": round(composition_score, 1),
            "clarity_score": round(clarity_score, 1),
        }
        
        # 建议
        if avg_brightness < 50:
            self.suggestions.append("画面偏暗，建议提高亮度或增加照明")
        if avg_contrast < 30:
            self.suggestions.append("画面对比度较低，建议增强明暗层次")
        if basic_info["width"] < 1080:
            self.suggestions.append("分辨率偏低，建议升级到1080p以上")
        
        return analysis
    
    def _analyze_audio(self, path: str) -> Dict[str, Any]:
        """音频分析"""
        try:
            audio = AudioSegment.from_file(path)
            
            # 音量
            dbfs = audio.dBFS
            
            # 动态范围
            max_db = audio.max_dBFS
            
            # 时长
            duration_sec = len(audio) / 1000
            
            info = {
                "duration_sec": round(duration_sec, 2),
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "dbfs": round(dbfs, 1),
                "max_dbfs": round(max_db, 1),
                "dynamic_range": round(max_db - dbfs, 1),
            }
            
            # 语速估算 (简化)
            # 假设安全生产视频语速约200字/分钟
            estimated_words = int(duration_sec / 60 * 200)
            info["estimated_words"] = estimated_words
            info["speech_pace"] = "适中" if 150 <= estimated_words <= 250 else (
                "偏快" if estimated_words > 250 else "偏慢"
            )
            
            return info
            
        except Exception as e:
            logger.warning(f"音频分析失败: {e}")
            return {"error": str(e)}
    
    def _rate_quality(self, basic_info: Dict, visual: Dict, audio: Dict) -> Dict[str, Any]:
        """标准评级"""
        # 清晰度
        w = basic_info.get("width", 0)
        clarity = 100 if w >= 1080 else (80 if w >= 720 else 50)
        
        # 专业度 (基于多项指标)
        prof_factors = [
            1.0 if basic_info.get("fps", 0) >= 30 else 0.8,
            1.0 if basic_info.get("duration", 0) >= 30 else 0.7,
            1.0 if visual.get("composition_score", 0) >= 50 else 0.7,
            1.0 if audio.get("channels", 2) >= 2 else 0.8,
        ]
        professional = sum(prof_factors) / len(prof_factors) * 100
        
        rating = {
            "clarity_score": round(clarity, 1),
            "professional_score": round(professional, 1),
            "resolution_grade": "高清" if w >= 1080 else ("标清" if w >= 720 else "低清"),
            "professional_grade": "A" if professional >= 85 else ("B" if professional >= 70 else "C"),
        }
        
        return rating
    
    def _predict_viral_potential(self, basic_info: Dict, visual: Dict, 
                                  audio: Dict) -> Dict[str, Any]:
        """传播效果预测"""
        duration = basic_info.get("duration", 0)
        
        # 完播率预测 (简化模型)
        # 短视频完播率与时长呈反比
        if duration <= 30:
            completion_rate = 0.75
        elif duration <= 60:
            completion_rate = 0.55
        elif duration <= 120:
            completion_rate = 0.35
        else:
            completion_rate = 0.20
        
        # 互动潜力
        engagement = completion_rate * (visual.get("composition_score", 50) / 100)
        
        # 信息密度 (简化)
        info_density = min(1.0, audio.get("estimated_words", 100) / (duration * 3))
        
        return {
            "estimated_completion_rate": round(completion_rate, 2),
            "engagement_score": round(engagement * 100, 1),
            "info_density": round(info_density, 2),
            "duration_category": "短" if duration <= 30 else ("中" if duration <= 60 else "长"),
            "recommendation": "适合发布" if completion_rate >= 0.5 else "建议缩短时长以提升完播率",
        }
    
    def _analyze_language_style(self, audio_info: Dict) -> Dict[str, Any]:
        """语言风格分析"""
        pace = audio_info.get("speech_pace", "适中")
        
        pace_map = {
            "偏快": {"pace": "fast", "description": "语速偏快，信息密度高，适合紧凑的警示内容"},
            "适中": {"pace": "medium", "description": "语速适中，表达清晰，适合规范讲解"},
            "偏慢": {"pace": "slow", "description": "语速偏慢，沉稳有力，适合重要强调"},
        }
        
        pace_info = pace_map.get(pace, pace_map["适中"])
        
        return {
            "tone": "专业严肃" if audio_info.get("dbfs", -20) < -15 else "亲切自然",
            "pace": pace_info["pace"],
            "pace_description": pace_info["description"],
            "expression": "指令式" if pace == "偏快" else "叙述式",
        }
    
    def _evaluate_presentation(self, basic_info: Dict, visual: Dict) -> Dict[str, Any]:
        """呈现效果评估"""
        duration = basic_info.get("duration", 0)
        info_density = visual.get("avg_contrast", 0)
        
        return {
            "visual_impact": "强" if info_density > 50 else ("中" if info_density > 30 else "弱"),
            "info_density": "高" if duration < 60 else "适中",
            "pacing": "紧凑" if duration < 30 else "舒缓",
            "attention_score": round(min(100, 100 - duration * 0.5 + info_density), 1),
        }
    
    def _determine_tone(self, brightness: float, saturation: float, 
                        contrast: float) -> str:
        """判断画面色调"""
        if brightness < 80:
            return "暗调/严肃"
        elif brightness > 180 and saturation < 80:
            return "亮调/明快"
        elif saturation > 120:
            return "高饱和/醒目"
        else:
            return "自然/平衡"
