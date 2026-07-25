"""
分镜脚本数据模型
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SceneType(str, Enum):
    """场景类型"""
    OPENING = "opening"       # 开场
    CONTENT = "content"       # 内容
    TRANSITION = "transition" # 转场
    CLOSING = "closing"       # 结尾
    WARNING = "warning"       # 警示


class VisualStyle(str, Enum):
    """视觉风格"""
    INDUSTRIAL_3D = "industrial_3d"    # 工业3D渲染
    REALISTIC = "realistic"            # 写实风格
    ANIMATION = "animation"            # 动画风格
    DOCUMENTARY = "documentary"        # 纪录片风格
    CARTOON = "cartoon"                # 卡通风格


class SceneAsset(BaseModel):
    """场景素材"""
    asset_id: str = Field(..., description="素材唯一ID")
    asset_type: str = Field(..., description="素材类型: image|video|audio")
    url: Optional[str] = Field(None, description="素材URL或路径")
    prompt: Optional[str] = Field(None, description="生成提示词")
    status: str = Field("pending", description="状态: pending|generating|completed|failed")


class Scene(BaseModel):
    """分镜场景"""
    scene_id: int = Field(..., description="场景序号")
    type: SceneType = Field(SceneType.CONTENT, description="场景类型")
    duration: float = Field(5.0, description="时长(秒)")
    
    # 内容
    narration: str = Field("", description="旁白文本")
    visual_description: str = Field("", description="画面描述")
    
    # AI生成提示词
    prompt_image: str = Field("", description="文生图提示词")
    prompt_video: str = Field("", description="图生视频提示词")
    
    # 风格
    visual_style: VisualStyle = Field(VisualStyle.INDUSTRIAL_3D, description="视觉风格")
    
    # 素材
    assets: List[SceneAsset] = Field(default_factory=list, description="素材列表")
    
    # 状态
    status: str = Field("pending", description="状态")


class Script(BaseModel):
    """分镜脚本"""
    script_id: str = Field(..., description="脚本ID")
    project_id: str = Field(..., description="所属项目ID")
    title: str = Field(..., description="视频标题")
    
    # 元信息
    topic: str = Field("", description="主题/关键词")
    target_duration: int = Field(60, description="目标时长(秒)")
    target_platform: str = Field("视频号", description="目标平台")
    
    # 内容
    raw_copy: str = Field("", description="原始文案")
    scenes: List[Scene] = Field(default_factory=list, description="分镜列表")
    
    # 状态
    status: str = Field("draft", description="状态: draft|review|approved|generating|completed")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "script_id": "script_001",
                "project_id": "proj_001",
                "title": "高空作业安全规范",
                "topic": "高空作业安全",
                "target_duration": 60,
                "scenes": [
                    {
                        "scene_id": 1,
                        "type": "opening",
                        "duration": 3,
                        "narration": "高空作业，安全第一",
                        "visual_description": "建筑工地高空作业场景，安全帽和安全带特写",
                        "prompt_image": "Industrial construction site, worker wearing safety helmet and harness, 3D render, realistic lighting, safety theme, high quality",
                        "visual_style": "industrial_3d"
                    }
                ]
            }
        }


class ScriptCreateRequest(BaseModel):
    """创建脚本请求"""
    project_id: str
    topic: str
    target_duration: int = 60
    target_platform: str = "视频号"
    raw_copy: Optional[str] = None


class ScriptSplitRequest(BaseModel):
    """脚本拆分请求"""
    script_id: str
    copy_text: str
    style_preset: str = "industrial_3d"
    num_scenes: int = 8
