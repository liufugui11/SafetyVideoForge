"""
项目管理路由
"""
import uuid
from typing import List

from fastapi import APIRouter, HTTPException

from app.models.video_project import (
    VideoProject, ProjectCreateRequest, 
    PipelineExecuteRequest, ProjectStatus, PipelineStage
)
from app.core.pipeline import PipelineEngine
from app.skills.registry import SkillRegistry

router = APIRouter()

# 内存存储（生产环境应使用数据库）
_projects: dict = {}


@router.post("/", response_model=VideoProject)
async def create_project(req: ProjectCreateRequest):
    """创建新项目"""
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    
    project = VideoProject(
        project_id=project_id,
        name=req.name,
        description=req.description,
        topic=req.topic,
        keywords=req.keywords,
        target_duration=req.target_duration,
        target_platform=req.target_platform,
        visual_style=req.visual_style,
    )
    
    _projects[project_id] = project
    return project


@router.get("/", response_model=List[VideoProject])
async def list_projects():
    """列出所有项目"""
    return list(_projects.values())


@router.get("/{project_id}", response_model=VideoProject)
async def get_project(project_id: str):
    """获取项目详情"""
    project = _projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.post("/{project_id}/execute")
async def execute_pipeline(project_id: str, req: PipelineExecuteRequest):
    """执行视频生成流水线"""
    project = _projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 获取引擎和注册表
    from app.main import app
    registry: SkillRegistry = app.state.skill_registry
    engine: PipelineEngine = app.state.pipeline_engine
    
    # 构建上下文
    context = {
        "project_id": project_id,
        "topic": project.topic,
        "keywords": project.keywords,
        "target_duration": project.target_duration,
        "visual_style": project.visual_style,
        "target_platform": project.target_platform,
    }
    
    # 更新项目状态
    project.status = ProjectStatus.GENERATING
    
    # 执行流水线
    result = await engine.execute_pipeline(
        project_id=project_id,
        context=context,
        stages=req.stages or None,
        skill_overrides=req.skill_overrides
    )
    
    # 更新项目状态
    if result["status"] == "completed":
        project.status = ProjectStatus.COMPLETED
    elif result["status"] == "failed":
        project.status = ProjectStatus.FAILED
    
    return result


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="项目不存在")
    del _projects[project_id]
    return {"message": "项目已删除"}
