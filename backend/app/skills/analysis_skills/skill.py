"""
视频解析技能
"""
from app.skills.base import BaseSkill, SkillContext, SkillResult
from app.services.video_analyzer import VideoAnalyzer


class StyleAnalyzerSkill(BaseSkill):
    """风格分析技能"""
    
    name = "style-analyzer"
    category = "analysis"
    version = "1.0.0"
    description = "分析视频的语言风格和画面风格"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "video_path", "type": "str", "description": "视频路径", "required": True},
    ]
    outputs = [
        {"name": "language_style", "type": "dict", "description": "语言风格分析"},
        {"name": "visual_style", "type": "dict", "description": "画面风格分析"},
    ]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.analyzer = VideoAnalyzer()
    
    async def execute(self, context: SkillContext) -> SkillResult:
        video_path = context.data.get("video_path", "")
        
        try:
            report = await self.analyzer.analyze(video_path)
            
            return SkillResult(
                success=True,
                data={
                    "language_style": report.language_style,
                    "visual_style": report.visual_style,
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


class ImpactEvaluatorSkill(BaseSkill):
    """效果评估技能"""
    
    name = "impact-evaluator"
    category = "analysis"
    version = "1.0.0"
    description = "评估视频呈现效果和质量标准"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "video_path", "type": "str", "description": "视频路径", "required": True},
    ]
    outputs = [
        {"name": "presentation", "type": "dict", "description": "呈现效果"},
        {"name": "quality_rating", "type": "dict", "description": "标准评级"},
    ]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.analyzer = VideoAnalyzer()
    
    async def execute(self, context: SkillContext) -> SkillResult:
        video_path = context.data.get("video_path", "")
        
        try:
            report = await self.analyzer.analyze(video_path)
            
            return SkillResult(
                success=True,
                data={
                    "presentation": report.presentation,
                    "quality_rating": report.quality_rating,
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


class ViralPredictorSkill(BaseSkill):
    """传播预测技能"""
    
    name = "viral-predictor"
    category = "analysis"
    version = "1.0.0"
    description = "预测视频的传播效果和互动潜力"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "video_path", "type": "str", "description": "视频路径", "required": True},
    ]
    outputs = [
        {"name": "viral_potential", "type": "dict", "description": "传播潜力预测"},
    ]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.analyzer = VideoAnalyzer()
    
    async def execute(self, context: SkillContext) -> SkillResult:
        video_path = context.data.get("video_path", "")
        
        try:
            report = await self.analyzer.analyze(video_path)
            
            return SkillResult(
                success=True,
                data={
                    "viral_potential": report.viral_potential,
                    "overall_score": report.overall_score,
                    "suggestions": report.suggestions,
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))
