"""
技能注册中心
动态加载和管理所有技能
"""
import os
import importlib
import inspect
from typing import Dict, List, Optional, Type
from pathlib import Path

from loguru import logger

from app.skills.base import BaseSkill
from app.config import settings


class SkillRegistry:
    """技能注册中心"""
    
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._skill_classes: Dict[str, Type[BaseSkill]] = {}
    
    def register(self, skill_class: Type[BaseSkill], config: dict = None):
        """
        注册技能类
        
        Args:
            skill_class: 技能类
            config: 技能配置
        """
        if not issubclass(skill_class, BaseSkill):
            raise ValueError(f"技能类必须继承 BaseSkill: {skill_class}")
        
        name = skill_class.name
        if not name:
            raise ValueError(f"技能类未定义 name 属性: {skill_class}")
        
        self._skill_classes[name] = skill_class
        self._skills[name] = skill_class(config=config)
        
        logger.info(f"✅ 技能注册成功: {name} (v{skill_class.version})")
    
    def unregister(self, name: str):
        """注销技能"""
        if name in self._skills:
            del self._skills[name]
            del self._skill_classes[name]
            logger.info(f"🗑️ 技能已注销: {name}")
    
    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """获取技能实例"""
        return self._skills.get(name)
    
    def get_skill_class(self, name: str) -> Optional[Type[BaseSkill]]:
        """获取技能类"""
        return self._skill_classes.get(name)
    
    def list_skills(self, category: str = None) -> List[Dict]:
        """列出所有技能"""
        skills = []
        for name, skill in self._skills.items():
            if category and skill.category != category:
                continue
            skills.append(skill.get_info())
        return skills
    
    def get_categories(self) -> List[str]:
        """获取所有技能类别"""
        categories = set()
        for skill in self._skills.values():
            categories.add(skill.category)
        return sorted(list(categories))
    
    def load_all_skills(self):
        """自动加载所有技能"""
        # 内置技能路径
        skills_dir = Path(__file__).parent
        
        # 扫描所有子目录中的 skill.py
        for subdir in skills_dir.iterdir():
            if not subdir.is_dir() or subdir.name.startswith("__"):
                continue
            
            skill_file = subdir / "skill.py"
            if skill_file.exists():
                self._load_skill_module(subdir.name, skill_file)
        
        logger.info(f"📦 技能库加载完成: 共 {len(self._skills)} 个技能")
    
    def _load_skill_module(self, module_name: str, file_path: Path):
        """加载单个技能模块"""
        try:
            # 动态导入
            spec = importlib.util.spec_from_file_location(
                f"app.skills.{module_name}", file_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找技能类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, BaseSkill) and 
                    obj is not BaseSkill and 
                    hasattr(obj, 'name') and obj.name):
                    
                    # 避免重复注册
                    if obj.name not in self._skills:
                        self.register(obj)
                        
        except Exception as e:
            logger.error(f"❌ 加载技能模块失败 {module_name}: {e}")
