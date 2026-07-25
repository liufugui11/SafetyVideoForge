"""
安全生产文案生成技能
"""
from app.skills.base import BaseSkill, SkillContext, SkillResult
from app.services.llm_service import LLMService
from app.core.script_engine import ScriptEngine


class SafetyCopywriterSkill(BaseSkill):
    """安全生产文案生成技能"""
    
    name = "safety-copywriter"
    category = "content"
    version = "1.0.0"
    description = "根据主题自动生成安全生产类短视频文案"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "topic", "type": "str", "description": "主题/关键词", "required": True},
        {"name": "keywords", "type": "list", "description": "关键词列表", "required": False},
        {"name": "target_duration", "type": "int", "description": "目标时长(秒)", "required": False, "default": 60},
        {"name": "tone", "type": "str", "description": "语气风格", "required": False, "default": "professional"},
    ]
    outputs = [
        {"name": "copy_text", "type": "str", "description": "生成的文案"},
        {"name": "title", "type": "str", "description": "建议标题"},
    ]
    required_models = ["doubao"]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.llm = LLMService()
        self.engine = ScriptEngine(self.llm)
    
    async def execute(self, context: SkillContext) -> SkillResult:
        topic = context.data.get("topic", "")
        keywords = context.data.get("keywords", [])
        duration = context.data.get("target_duration", 60)
        
        try:
            copy_text = await self.engine.generate_copy(
                topic=topic,
                keywords=keywords,
                duration=duration
            )
            
            # 生成标题
            title_prompt = f"为以下安全生产短视频文案生成一个吸引人的标题（15字以内）：\n\n{copy_text[:200]}"
            title = await self.llm.chat(title_prompt, model_preference="doubao")
            
            return SkillResult(
                success=True,
                data={
                    "copy_text": copy_text,
                    "title": title.strip(),
                    "word_count": len(copy_text),
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


class ScriptSplitterSkill(BaseSkill):
    """脚本拆分技能"""
    
    name = "script-splitter"
    category = "content"
    version = "1.0.0"
    description = "将文案按场景拆分为结构化分镜脚本"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "copy_text", "type": "str", "description": "完整文案", "required": True},
        {"name": "style_preset", "type": "str", "description": "视觉风格", "required": False, "default": "industrial_3d"},
        {"name": "num_scenes", "type": "int", "description": "场景数", "required": False, "default": 8},
    ]
    outputs = [
        {"name": "scenes", "type": "list", "description": "分镜场景列表"},
        {"name": "total_duration", "type": "float", "description": "总时长估算"},
    ]
    required_models = ["deepseek"]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.llm = LLMService()
        self.engine = ScriptEngine(self.llm)
    
    async def execute(self, context: SkillContext) -> SkillResult:
        copy_text = context.data.get("copy_text", "")
        style = context.data.get("style_preset", "industrial_3d")
        num_scenes = context.data.get("num_scenes", 8)
        target_duration = context.data.get("target_duration", 60)
        
        try:
            scenes = await self.engine.split_script(
                copy_text=copy_text,
                style_preset=style,
                num_scenes=num_scenes,
                target_duration=target_duration
            )
            
            total_duration = sum(s.duration for s in scenes)
            
            return SkillResult(
                success=True,
                data={
                    "scenes": [s.model_dump() for s in scenes],
                    "scene_count": len(scenes),
                    "total_duration": total_duration,
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


class PromptEngineerSkill(BaseSkill):
    """AI提示词工程技能"""
    
    name = "prompt-engineer"
    category = "content"
    version = "1.0.0"
    description = "为每个分镜生成高质量的AI绘图/视频提示词"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "scenes", "type": "list", "description": "场景列表", "required": True},
    ]
    outputs = [
        {"name": "enhanced_scenes", "type": "list", "description": "增强后的场景(含提示词)"},
    ]
    required_models = ["deepseek"]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.llm = LLMService()
        self.engine = ScriptEngine(self.llm)
    
    async def execute(self, context: SkillContext) -> SkillResult:
        from app.models.script import Scene
        
        scenes_data = context.data.get("scenes", [])
        scenes = [Scene(**s) for s in scenes_data]
        
        try:
            enhanced = await self.engine.generate_prompts(scenes)
            
            return SkillResult(
                success=True,
                data={
                    "enhanced_scenes": [s.model_dump() for s in enhanced],
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))
