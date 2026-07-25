"""
模型管理路由
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_models():
    """列出可用模型"""
    from app.services.llm_service import LLMService
    
    llm = LLMService()
    models = llm.get_available_models()
    await llm.close_all()
    
    return models


@router.post("/test")
async def test_model(provider: str, prompt: str = "你好，请做一个简短自我介绍"):
    """测试模型连通性"""
    from app.services.llm_service import LLMService
    
    llm = LLMService()
    
    try:
        response = await llm.chat(prompt, model_preference=provider)
        await llm.close_all()
        
        return {
            "provider": provider,
            "status": "ok",
            "response": response[:200]
        }
    except Exception as e:
        await llm.close_all()
        return {
            "provider": provider,
            "status": "error",
            "error": str(e)
        }
