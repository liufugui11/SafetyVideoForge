"""
合成与质检技能
"""
from app.skills.base import BaseSkill, SkillContext, SkillResult
from app.core.quality_checker import QualityChecker
from app.core.distributor import Distributor
from app.config import settings


class VideoAssemblerSkill(BaseSkill):
    """视频合成技能"""
    
    name = "video-assembler"
    category = "synthesis"
    version = "1.0.0"
    description = "将素材合成为最终视频"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "scenes", "type": "list", "description": "场景列表", "required": True},
        {"name": "video_paths", "type": "list", "description": "视频片段路径", "required": True},
        {"name": "audio_paths", "type": "list", "description": "音频路径", "required": True},
        {"name": "bgm_path", "type": "str", "description": "背景音乐路径", "required": False},
    ]
    outputs = [
        {"name": "output_video", "type": "str", "description": "合成后的视频路径"},
    ]
    
    def __init__(self, config=None):
        super().__init__(config)
    
    async def execute(self, context: SkillContext) -> SkillResult:
        # 简化版：实际应使用 MoviePy + FFmpeg 合成
        # 这里返回模拟结果，完整实现在 utils/ffmpeg_utils.py
        
        import tempfile
        output_path = tempfile.mktemp(suffix=".mp4")
        
        return SkillResult(
            success=True,
            data={
                "output_video": output_path,
                "note": "此为技能框架，完整合成需调用ffmpeg_utils"
            }
        )


class QualityInspectorSkill(BaseSkill):
    """质量检查技能"""
    
    name = "quality-inspector"
    category = "synthesis"
    version = "1.0.0"
    description = "检查视频质量并生成报告"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "video_path", "type": "str", "description": "视频路径", "required": True},
        {"name": "script_text", "type": "str", "description": "原始文案", "required": False},
    ]
    outputs = [
        {"name": "report", "type": "dict", "description": "质检报告"},
    ]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.checker = QualityChecker()
    
    async def execute(self, context: SkillContext) -> SkillResult:
        video_path = context.data.get("video_path", "")
        script_text = context.data.get("script_text", "")
        
        try:
            report = await self.checker.check_video(video_path, script_text)
            
            return SkillResult(
                success=True,
                data={
                    "overall_score": report.overall_score,
                    "video_score": report.video_score,
                    "audio_score": report.audio_score,
                    "content_score": report.content_score,
                    "issues": report.issues,
                    "suggestions": report.suggestions,
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


class DistributorSkill(BaseSkill):
    """分发技能"""
    
    name = "distributor"
    category = "synthesis"
    version = "1.0.0"
    description = "导出视频到指定平台格式"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "video_path", "type": "str", "description": "视频路径", "required": True},
        {"name": "project_name", "type": "str", "description": "项目名称", "required": True},
        {"name": "platform", "type": "str", "description": "目标平台", "required": False, "default": "视频号"},
    ]
    outputs = [
        {"name": "export_result", "type": "dict", "description": "导出结果"},
    ]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.distributor = Distributor(settings.OUTPUT_DIR)
    
    async def execute(self, context: SkillContext) -> SkillResult:
        video_path = context.data.get("video_path", "")
        project_name = context.data.get("project_name", "untitled")
        platform = context.data.get("platform", "视频号")
        
        try:
            result = await self.distributor.export_video(
                video_path=video_path,
                project_name=project_name,
                platform=platform
            )
            
            return SkillResult(success=True, data=result)
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))
