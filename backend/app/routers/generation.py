"""
视频生成路由
"""
from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/from-script")
async def generate_from_script(script_id: str):
    """从脚本生成视频"""
    # 委托给项目流水线执行
    return {"message": "请使用项目流水线执行接口 /api/v1/projects/{project_id}/execute"}


@router.post("/tts")
async def generate_tts(text: str, voice: str = "zh-CN-YunyangNeural"):
    """生成TTS配音"""
    from app.services.tts_service import TTSService
    
    tts = TTSService()
    path = await tts.synthesize(text, voice=voice)
    
    return {"audio_path": path}


@router.post("/image")
async def generate_image(prompt: str, provider: str = "qwen"):
    """生成图片"""
    from app.services.llm_service import LLMService
    from app.services.image_gen_service import ImageGenerationService
    
    llm = LLMService()
    img_gen = ImageGenerationService(llm)
    
    path = await img_gen.generate(prompt, provider=provider)
    await img_gen.close()
    
    return {"image_path": path}
