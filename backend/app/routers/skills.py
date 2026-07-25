"""
技能库路由
"""
from typing import List

from fastapi import APIRouter, HTTPException

from app.models.skill import SkillInfo, SkillExecuteRequest, SkillExecuteResult

router = APIRouter()


@router.get("/", response_model=List[SkillInfo])
async def list_skills(category: str = None):
    """列出所有技能"""
    from app.main import app
    registry = app.state.skill_registry
    return registry.list_skills(category=category)


@router.get("/categories")
async def get_categories():
    """获取技能类别"""
    from app.main import app
    registry = app.state.skill_registry
    return registry.get_categories()


@router.post("/{skill_name}/execute", response_model=SkillExecuteResult)
async def execute_skill(skill_name: str, req: SkillExecuteRequest):
    """执行单个技能"""
    from app.main import app
    from app.skills.base import SkillContext
    
    registry = app.state.skill_registry
    skill = registry.get_skill(skill_name)
    
    if not skill:
        raise HTTPException(status_code=404, detail=f"技能不存在: {skill_name}")
    
    context = SkillContext(
        data=req.params,
        config=req.config
    )
    
    result = await skill.execute(context)
    
    return SkillExecuteResult(
        skill_name=skill_name,
        success=result.success,
        data=result.data,
        error=result.error,
        execution_time=result.execution_time
    )


@router.get("/{skill_name}")
async def get_skill_info(skill_name: str):
    """获取技能详情"""
    from app.main import app
    registry = app.state.skill_registry
    skill = registry.get_skill(skill_name)
    
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    
    return skill.get_info()
