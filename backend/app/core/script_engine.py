"""
脚本引擎 - 文案拆分与分镜生成
"""
import json
import re
from typing import List, Dict, Any
from loguru import logger

from app.models.script import Script, Scene, SceneType, VisualStyle, SceneAsset
from app.services.llm_service import LLMService


class ScriptEngine:
    """脚本引擎"""
    
    # 安全生产主题预设
    SAFETY_TOPICS = {
        "high_altitude": "高空作业安全",
        "electrical": "用电安全",
        "fire": "消防安全",
        "machinery": "机械操作安全",
        "chemical": "化学品安全",
        "confined_space": "有限空间作业",
        "ppe": "个人防护装备",
        "emergency": "应急处置",
        "traffic": "厂内交通安全",
        "lifting": "起重吊装安全",
    }
    
    # 场景类型映射规则
    SCENE_TYPE_RULES = [
        (r"^(开场|引入|开头|片头)", SceneType.OPENING),
        (r"^(结尾|总结|片尾|结束)", SceneType.CLOSING),
        (r"^(警示|警告|注意|危险)", SceneType.WARNING),
        (r"^(转场|过渡|切换)", SceneType.TRANSITION),
    ]
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def generate_copy(self, topic: str, keywords: List[str], 
                           duration: int = 60, platform: str = "视频号") -> str:
        """
        生成安全生产类文案
        
        Args:
            topic: 主题
            keywords: 关键词
            duration: 目标时长(秒)
            platform: 目标平台
        
        Returns:
            生成的文案
        """
        word_count = self._estimate_word_count(duration)
        
        prompt = f"""你是一位专业的安全生产宣传教育文案撰写专家。请根据以下要求创作一段短视频文案：

主题：{topic}
关键词：{', '.join(keywords)}
目标时长：{duration}秒
目标平台：{platform}
字数要求：约{word_count}字

要求：
1. 语言风格：专业、严肃但不枯燥，有警示性但不过度恐吓
2. 结构：开头抓眼球 → 核心内容(规范/案例/要点) → 结尾强调
3. 适合配音：句子长度适中，有自然的停顿节奏
4. 符合安全生产宣传规范，引用标准要准确
5. 可适当加入真实案例元素增强说服力

请直接输出文案正文，不要加标题和额外说明。"""
        
        copy = await self.llm.chat(prompt, model_preference="doubao")
        logger.info(f"📝 文案生成完成: {len(copy)}字")
        return copy.strip()
    
    async def split_script(
        self,
        copy_text: str,
        style_preset: str = "industrial_3d",
        num_scenes: int = 8,
        target_duration: int = 60
    ) -> List[Scene]:
        """
        将文案拆分为分镜脚本
        
        Args:
            copy_text: 完整文案
            style_preset: 视觉风格预设
            num_scenes: 目标场景数
            target_duration: 目标总时长
        
        Returns:
            场景列表
        """
        avg_duration = target_duration / num_scenes
        
        prompt = f"""你是一位专业的短视频分镜导演。请将以下安全生产宣传文案拆分为{num_scenes}个分镜场景。

文案内容：
---
{copy_text}
---

要求：
1. 每个分镜包含：场景序号、场景类型(opening/content/transition/closing/warning)、旁白文本(从原文案中精确提取)、画面描述
2. 场景类型分配：1个开场 + 1个结尾 + {num_scenes-2}个内容场景
3. 每个场景时长控制在3-8秒
4. 画面描述要具体、可执行，适合AI图像/视频生成
5. 视觉风格：{style_preset}（工业3D渲染/写实/动画）

请严格按照以下JSON格式输出（不要包含任何其他文本）：
{{
  "scenes": [
    {{
      "scene_id": 1,
      "type": "opening",
      "duration": 5,
      "narration": "旁白文本",
      "visual_description": "详细的画面描述"
    }}
  ]
}}"""
        
        response = await self.llm.chat(
            prompt, 
            model_preference="deepseek",
            json_mode=True
        )
        
        try:
            data = json.loads(response)
            scenes_data = data.get("scenes", [])
            
            scenes = []
            for sd in scenes_data:
                scene_type = self._parse_scene_type(sd.get("type", "content"))
                
                scene = Scene(
                    scene_id=sd.get("scene_id", len(scenes) + 1),
                    type=scene_type,
                    duration=float(sd.get("duration", avg_duration)),
                    narration=sd.get("narration", ""),
                    visual_description=sd.get("visual_description", ""),
                    visual_style=VisualStyle(style_preset) if style_preset in [e.value for e in VisualStyle] else VisualStyle.INDUSTRIAL_3D,
                    assets=[]
                )
                scenes.append(scene)
            
            logger.info(f"🎬 脚本拆分完成: {len(scenes)}个场景")
            return scenes
            
        except json.JSONDecodeError as e:
            logger.error(f"脚本JSON解析失败: {e}")
            # 降级：按段落简单拆分
            return self._fallback_split(copy_text, num_scenes, avg_duration, style_preset)
    
    async def generate_prompts(self, scenes: List[Scene]) -> List[Scene]:
        """
        为每个场景生成AI绘图/视频提示词
        
        Args:
            scenes: 场景列表
        
        Returns:
            更新后的场景列表
        """
        for scene in scenes:
            # 生成文生图提示词
            img_prompt = await self._generate_image_prompt(scene)
            scene.prompt_image = img_prompt
            
            # 生成图生视频提示词
            vid_prompt = await self._generate_video_prompt(scene)
            scene.prompt_video = vid_prompt
            
            logger.debug(f"🎨 提示词生成: Scene {scene.scene_id}")
        
        return scenes
    
    async def _generate_image_prompt(self, scene: Scene) -> str:
        """生成文生图提示词"""
        style_keywords = {
            VisualStyle.INDUSTRIAL_3D: "3D render, industrial style, realistic lighting, high detail, safety theme",
            VisualStyle.REALISTIC: "photorealistic, documentary style, natural lighting, high quality",
            VisualStyle.ANIMATION: "animated, motion graphics, clean design, professional",
            VisualStyle.DOCUMENTARY: "documentary footage, realistic, cinematic lighting",
            VisualStyle.CARTOON: "cartoon style, flat design, bright colors, friendly",
        }
        
        style_kw = style_keywords.get(scene.visual_style, style_keywords[VisualStyle.INDUSTRIAL_3D])
        
        prompt = f"""将以下画面描述转换为专业的AI文生图提示词（英文）：

画面描述：{scene.visual_description}
风格要求：{style_kw}

要求：
1. 提示词必须是英文
2. 包含主体、环境、光影、风格、质量描述
3. 长度控制在50-100词
4. 适合Stable Diffusion / DALL-E / 通义万相等模型

直接输出提示词，不要加任何说明。"""
        
        result = await self.llm.chat(prompt, model_preference="deepseek")
        return result.strip()
    
    async def _generate_video_prompt(self, scene: Scene) -> str:
        """生成图生视频提示词"""
        prompt = f"""将以下画面描述转换为专业的AI图生视频提示词（英文）：

画面描述：{scene.visual_description}
旁白：{scene.narration}

要求：
1. 提示词必须是英文
2. 描述画面的动态变化、镜头运动
3. 包含时间感、空间感描述
4. 适合Wan2.1 / CogVideo / Seedance等视频生成模型
5. 长度控制在30-80词

直接输出提示词，不要加任何说明。"""
        
        result = await self.llm.chat(prompt, model_preference="deepseek")
        return result.strip()
    
    def _parse_scene_type(self, type_str: str) -> SceneType:
        """解析场景类型"""
        type_lower = type_str.lower().strip()
        
        for pattern, scene_type in self.SCENE_TYPE_RULES:
            if re.search(pattern, type_lower):
                return scene_type
        
        # 默认映射
        mapping = {
            "opening": SceneType.OPENING,
            "content": SceneType.CONTENT,
            "transition": SceneType.TRANSITION,
            "closing": SceneType.CLOSING,
            "warning": SceneType.WARNING,
        }
        return mapping.get(type_lower, SceneType.CONTENT)
    
    def _fallback_split(self, text: str, num_scenes: int, 
                        avg_duration: float, style_preset: str) -> List[Scene]:
        """降级拆分策略：按段落简单拆分"""
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        scenes = []
        for i, para in enumerate(paragraphs[:num_scenes]):
            scene_type = SceneType.OPENING if i == 0 else (
                SceneType.CLOSING if i == len(paragraphs) - 1 else SceneType.CONTENT
            )
            
            scenes.append(Scene(
                scene_id=i + 1,
                type=scene_type,
                duration=avg_duration,
                narration=para[:200],
                visual_description=f"Scene showing: {para[:100]}",
                visual_style=VisualStyle(style_preset) if style_preset in [e.value for e in VisualStyle] else VisualStyle.INDUSTRIAL_3D,
                assets=[]
            ))
        
        return scenes
    
    def _estimate_word_count(self, duration: int) -> int:
        """根据时长估算字数 (按正常语速约200字/分钟)"""
        return int((duration / 60) * 200 * 1.2)  # 1.2倍余量
