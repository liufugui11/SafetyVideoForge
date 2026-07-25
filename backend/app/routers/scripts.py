"""
脚本管理路由
"""
import uuid
from typing import List

from fastapi import APIRouter, HTTPException

from app.models.script import Script, ScriptCreateRequest, ScriptSplitRequest

router = APIRouter()

_scripts: dict = {}


@router.post("/", response_model=Script)
async def create_script(req: ScriptCreateRequest):
    """创建脚本"""
    script_id = f"script_{uuid.uuid4().hex[:8]}"
    
    script = Script(
        script_id=script_id,
        project_id=req.project_id,
        topic=req.topic,
        target_duration=req.target_duration,
        target_platform=req.target_platform,
        raw_copy=req.raw_copy or "",
    )
    
    _scripts[script_id] = script
    return script


@router.get("/{script_id}", response_model=Script)
async def get_script(script_id: str):
    """获取脚本"""
    script = _scripts.get(script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    return script


@router.post("/{script_id}/split")
async def split_script(script_id: str, req: ScriptSplitRequest):
    """拆分文案为分镜脚本"""
    from app.main import app
    from app.services.llm_service import LLMService
    from app.core.script_engine import ScriptEngine
    
    script = _scripts.get(script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    llm = LLMService()
    engine = ScriptEngine(llm)
    
    scenes = await engine.split_script(
        copy_text=req.copy_text,
        style_preset=req.style_preset,
        num_scenes=req.num_scenes,
        target_duration=script.target_duration
    )
    
    # 生成提示词
    scenes = await engine.generate_prompts(scenes)
    
    script.scenes = scenes
    script.raw_copy = req.copy_text
    script.status = "approved"
    
    return script


@router.get("/", response_model=List[Script])
async def list_scripts():
    """列出所有脚本"""
    return list(_scripts.values())
