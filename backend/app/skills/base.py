"""
技能基类定义
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SkillContext:
    """技能执行上下文"""
    project_id: str = ""
    script_id: str = ""
    stage: str = ""
    data: Dict[str, Any] = None
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.config is None:
            self.config = {}


@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    data: Dict[str, Any] = None
    error: str = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.metadata is None:
            self.metadata = {}


class BaseSkill(ABC):
    """
    技能基类
    
    所有可复用技能必须继承此类并实现 execute 方法
    """
    
    # 技能元信息 (子类覆盖)
    name: str = ""
    category: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    
    # 输入输出定义
    inputs: list = []
    outputs: list = []
    
    # 依赖
    dependencies: list = []
    required_models: list = []
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.created_at = datetime.now()
    
    @abstractmethod
    async def execute(self, context: SkillContext) -> SkillResult:
        """
        执行技能
        
        Args:
            context: 执行上下文，包含项目ID、数据等
        
        Returns:
            SkillResult: 执行结果
        """
        pass
    
    def validate_input(self, context: SkillContext) -> tuple[bool, str]:
        """
        验证输入参数
        
        子类可覆盖此方法添加自定义验证逻辑
        
        Returns:
            (是否通过, 错误信息)
        """
        return True, ""
    
    def get_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return {
            "name": self.name,
            "category": self.category,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "dependencies": self.dependencies,
            "required_models": self.required_models,
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name}, v={self.version})>"
