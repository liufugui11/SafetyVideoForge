"""
技能数据模型
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SkillCategory(str, Enum):
    """技能类别"""
    CONTENT = "content"       # 内容生成
    VISUAL = "visual"         # 视觉生成
    AUDIO = "audio"           # 音频生成
    SYNTHESIS = "synthesis"   # 合成质检
    ANALYSIS = "analysis"     # 视频解析
    UTILITY = "utility"       # 工具


class SkillInputSchema(BaseModel):
    """技能输入参数定义"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class SkillOutputSchema(BaseModel):
    """技能输出定义"""
    name: str
    type: str
    description: str


class SkillInfo(BaseModel):
    """技能信息"""
    name: str = Field(..., description="技能唯一标识")
    category: SkillCategory = Field(..., description="技能类别")
    version: str = Field("1.0.0", description="版本")
    description: str = Field("", description="描述")
    author: str = Field("", description="作者")
    
    # 输入输出
    inputs: List[SkillInputSchema] = Field(default_factory=list, description="输入参数")
    outputs: List[SkillOutputSchema] = Field(default_factory=list, description="输出定义")
    
    # 依赖
    dependencies: List[str] = Field(default_factory=list, description="依赖的技能")
    required_models: List[str] = Field(default_factory=list, description="需要的模型")
    
    # 配置
    config_schema: Optional[Dict[str, Any]] = Field(None, description="配置schema")
    default_config: Dict[str, Any] = Field(default_factory=dict, description="默认配置")
    
    # 状态
    enabled: bool = Field(True, description="是否启用")


class SkillExecuteRequest(BaseModel):
    """执行技能请求"""
    skill_name: str
    params: Dict[str, Any] = Field(default_factory=dict, description="输入参数")
    config: Dict[str, Any] = Field(default_factory=dict, description="运行时配置")


class SkillExecuteResult(BaseModel):
    """技能执行结果"""
    skill_name: str
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict, description="输出数据")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(0.0, description="执行时间(秒)")


class SkillChainRequest(BaseModel):
    """技能链编排请求"""
    chain_name: str
    skills: List[str] = Field(..., description="技能名称列表")
    shared_context: Dict[str, Any] = Field(default_factory=dict, description="共享上下文")
    skill_configs: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="各技能配置")
