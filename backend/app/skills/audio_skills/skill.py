"""
音频生成技能
"""
from app.skills.base import BaseSkill, SkillContext, SkillResult
from app.services.tts_service import TTSService
from app.services.music_service import MusicService


class TTSNarratorSkill(BaseSkill):
    """TTS旁白配音技能"""
    
    name = "tts-narrator"
    category = "audio"
    version = "1.0.0"
    description = "将文案合成为旁白配音"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "scenes", "type": "list", "description": "场景列表(含narration)", "required": True},
        {"name": "voice", "type": "str", "description": "音色", "required": False, "default": "zh-CN-YunyangNeural"},
    ]
    outputs = [
        {"name": "audio_paths", "type": "list", "description": "音频文件路径列表"},
    ]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.tts = TTSService()
    
    async def execute(self, context: SkillContext) -> SkillResult:
        scenes = context.data.get("scenes", [])
        voice = context.data.get("voice", "zh-CN-YunyangNeural")
        
        try:
            paths = await self.tts.synthesize_scenes(scenes, voice=voice)
            
            return SkillResult(
                success=True,
                data={
                    "audio_paths": paths,
                    "voice": voice,
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


class BGMComposerSkill(BaseSkill):
    """背景音乐技能"""
    
    name = "bgm-composer"
    category = "audio"
    version = "1.0.0"
    description = "生成/选择背景音乐"
    author = "SafetyVideoForge"
    
    inputs = [
        {"name": "duration", "type": "int", "description": "目标时长(秒)", "required": True},
        {"name": "mood", "type": "str", "description": "情绪", "required": False, "default": "educational"},
    ]
    outputs = [
        {"name": "bgm_path", "type": "str", "description": "背景音乐路径"},
    ]
    
    def __init__(self, config=None):
        super().__init__(config)
        self.music = MusicService()
    
    async def execute(self, context: SkillContext) -> SkillResult:
        duration = context.data.get("duration", 60)
        mood = context.data.get("mood", "educational")
        
        try:
            track = self.music.get_track(mood=mood, duration=duration)
            
            if not track:
                # 生成静音
                import tempfile
                output_path = tempfile.mktemp(suffix=".mp3")
                self.music.generate_silence(duration, output_path)
                track = output_path
            else:
                # 循环到目标时长
                import tempfile
                output_path = tempfile.mktemp(suffix=".mp3")
                self.music.loop_to_duration(track, duration, output_path)
                track = output_path
            
            return SkillResult(
                success=True,
                data={"bgm_path": track}
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))
