"""
视频项目数据模型
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    """项目状态"""
    DRAFT = "draft"           # 草稿
    SCRIPTING = "scripting"   # 脚本编写中
    GENERATING = "generating" # 素材生成中
    ASSEMBLING = "assembling" # 合成中
    REVIEWING = "reviewing"   # 审核中
    COMPLETED = "completed"   # 完成
    FAILED = "failed"         # 失败


class PipelineStage(str, Enum):
    """流水线阶段"""
    IDLE = "idle"
    COPYWRITING = "copywriting"
    SCRIPT_SPLITTING = "script_splitting"
    VISUAL_CONCEPTION = "visual_conception"
    ASSET_GENERATION = "asset_generation"
    AUDIO_GENERATION = "audio_generation"
    QUALITY_CHECK = "quality_check"
    ASSEMBLY = "assembly"
    DISTRIBUTION = "distribution"


class VideoProject(BaseModel):
    """视频项目"""
    project_id: str = Field(..., description="项目ID")
    name: str = Field(..., description="项目名称")
    description: str = Field("", description="项目描述")
    
    # 配置
    topic: str = Field("", description="主题")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    target_duration: int = Field(60, description="目标时长")
    target_platform: str = Field("视频号", description="目标平台")
    visual_style: str = Field("industrial_3d", description="视觉风格")
    
    # 状态
    status: ProjectStatus = Field(ProjectStatus.DRAFT, description="项目状态")
    current_stage: PipelineStage = Field(PipelineStage.IDLE, description="当前阶段")
    stage_progress: float = Field(0.0, description="当前阶段进度(0-100)")
    
    # 关联
    script_id: Optional[str] = Field(None, description="关联脚本ID")
    output_video_path: Optional[str] = Field(None, description="输出视频路径")
    
    # 质量评分
    quality_score: Optional[float] = Field(None, description="质量评分(0-100)")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ProjectCreateRequest(BaseModel):
    """创建项目请求"""
    name: str
    description: str = ""
    topic: str = ""
    keywords: List[str] = []
    target_duration: int = 60
    target_platform: str = "视频号"
    visual_style: str = "industrial_3d"


class PipelineExecuteRequest(BaseModel):
    """执行流水线请求"""
    project_id: str
    stages: List[str] = []  # 空列表表示执行全部阶段
    skill_overrides: Dict[str, str] = {}  # 技能覆盖配置
