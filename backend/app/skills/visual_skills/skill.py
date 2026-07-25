"""
视觉生成技能
"""
from app.skills.base import BaseSkill, SkillContext, SkillResult
from app.services.llm_service import LLMService
from app.services.image_gen_service import ImageGenerationService
from app.services.video_gen_service import VideoGenerationService


class ImageGeneratorSkill(BaseSkill):
    """文生图技能"""
    
    name = "image-generator"
    category = "visual"
    version = "1.0.0"
    description = "根据提示词生成场景图片"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "prompts", "type": "list", "description": "提示词列表", "required": True},
        {"name": "provider", "type": "str", "description": "提供商", "required": False, "default": "qwen"},
    ]
    outputs = [
        {"name": "image_paths", "type": "list", "description": "生成图片路径列表"},
    ]
    required_models = ["qwen"]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.llm = LLMService()
        self.image_gen = ImageGenerationService(self.llm)
    
    async def execute(self, context: SkillContext) -> SkillResult:
        prompts = context.data.get("prompts", [])
        provider = context.data.get("provider", "qwen")
        
        try:
            paths = await self.image_gen.generate_batch(prompts, provider=provider)
            
            return SkillResult(
                success=True,
                data={
                    "image_paths": paths,
                    "successful": sum(1 for p in paths if p),
                    "failed": sum(1 for p in paths if not p),
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))
        finally:
            await self.image_gen.close()


class VideoGeneratorSkill(BaseSkill):
    """视频生成技能"""
    
    name = "video-generator"
    category = "visual"
    version = "1.0.0"
    description = "根据图片和提示词生成视频片段"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "items", "type": "list", "description": "生成项列表", "required": True},
        {"name": "provider", "type": "str", "description": "提供商", "required": False, "default": "wanx"},
    ]
    outputs = [
        {"name": "video_paths", "type": "list", "description": "生成视频路径列表"},
    ]
    required_models = ["wanx"]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.llm = LLMService()
        self.video_gen = VideoGenerationService(self.llm)
    
    async def execute(self, context: SkillContext) -> SkillResult:
        items = context.data.get("items", [])
        provider = context.data.get("provider", "wanx")
        
        try:
            paths = await self.video_gen.generate_batch(items, provider=provider)
            
            return SkillResult(
                success=True,
                data={
                    "video_paths": paths,
                    "successful": sum(1 for p in paths if p),
                    "failed": sum(1 for p in paths if not p),
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))
