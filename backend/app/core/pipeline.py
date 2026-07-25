"""
视频生成流水线引擎
协调各阶段技能按顺序执行
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from loguru import logger

from app.skills.registry import SkillRegistry
from app.models.video_project import PipelineStage, ProjectStatus


class PipelineStatus(str, Enum):
    """流水线状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineEngine:
    """流水线引擎"""
    
    # 默认阶段顺序
    DEFAULT_STAGES = [
        PipelineStage.COPYWRITING,
        PipelineStage.SCRIPT_SPLITTING,
        PipelineStage.VISUAL_CONCEPTION,
        PipelineStage.ASSET_GENERATION,
        PipelineStage.AUDIO_GENERATION,
        PipelineStage.ASSEMBLY,
        PipelineStage.QUALITY_CHECK,
        PipelineStage.DISTRIBUTION,
    ]
    
    # 阶段到技能的映射
    STAGE_SKILL_MAP = {
        PipelineStage.COPYWRITING: "safety-copywriter",
        PipelineStage.SCRIPT_SPLITTING: "script-splitter",
        PipelineStage.VISUAL_CONCEPTION: "prompt-engineer",
        PipelineStage.ASSET_GENERATION: ["image-generator", "video-generator"],
        PipelineStage.AUDIO_GENERATION: ["tts-narrator", "bgm-composer"],
        PipelineStage.ASSEMBLY: "video-assembler",
        PipelineStage.QUALITY_CHECK: "quality-inspector",
        PipelineStage.DISTRIBUTION: "distributor",
    }
    
    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self.running_pipelines: Dict[str, dict] = {}
    
    async def execute_pipeline(
        self,
        project_id: str,
        context: Dict[str, Any],
        stages: Optional[List[PipelineStage]] = None,
        skill_overrides: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        执行完整流水线
        
        Args:
            project_id: 项目ID
            context: 共享上下文数据
            stages: 指定执行的阶段(默认全部)
            skill_overrides: 技能覆盖配置
        
        Returns:
            执行结果
        """
        stages = stages or self.DEFAULT_STAGES
        skill_overrides = skill_overrides or {}
        
        pipeline_id = f"pipeline_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.running_pipelines[pipeline_id] = {
            "pipeline_id": pipeline_id,
            "project_id": project_id,
            "status": PipelineStatus.RUNNING,
            "current_stage": None,
            "progress": 0.0,
            "stages_total": len(stages),
            "stages_completed": 0,
            "results": {},
            "errors": [],
            "started_at": datetime.now(),
        }
        
        logger.info(f"🎬 流水线启动: {pipeline_id}, 阶段数: {len(stages)}")
        
        try:
            for i, stage in enumerate(stages):
                pipeline = self.running_pipelines[pipeline_id]
                pipeline["current_stage"] = stage.value
                pipeline["progress"] = (i / len(stages)) * 100
                
                logger.info(f"⏳ 执行阶段 [{i+1}/{len(stages)}]: {stage.value}")
                
                # 获取阶段对应的技能
                skill_names = self.STAGE_SKILL_MAP.get(stage, [])
                if isinstance(skill_names, str):
                    skill_names = [skill_names]
                
                # 应用技能覆盖
                skill_names = [
                    skill_overrides.get(sn, sn) for sn in skill_names
                ]
                
                # 执行阶段
                stage_result = await self._execute_stage(
                    pipeline_id=pipeline_id,
                    stage=stage,
                    skill_names=skill_names,
                    context=context
                )
                
                pipeline["results"][stage.value] = stage_result
                
                if stage_result.get("success"):
                    pipeline["stages_completed"] += 1
                    # 更新上下文
                    context.update(stage_result.get("data", {}))
                else:
                    error_msg = stage_result.get("error", "未知错误")
                    pipeline["errors"].append({
                        "stage": stage.value,
                        "error": error_msg
                    })
                    logger.error(f"❌ 阶段失败: {stage.value} - {error_msg}")
                    
                    # 是否继续？这里选择中断
                    pipeline["status"] = PipelineStatus.FAILED
                    break
            
            # 更新最终状态
            pipeline = self.running_pipelines[pipeline_id]
            if pipeline["status"] != PipelineStatus.FAILED:
                pipeline["status"] = PipelineStatus.COMPLETED
                pipeline["progress"] = 100.0
                logger.info(f"✅ 流水线完成: {pipeline_id}")
            
        except Exception as e:
            logger.exception(f"💥 流水线异常: {pipeline_id}")
            self.running_pipelines[pipeline_id]["status"] = PipelineStatus.FAILED
            self.running_pipelines[pipeline_id]["errors"].append({
                "stage": "pipeline",
                "error": str(e)
            })
        
        finally:
            self.running_pipelines[pipeline_id]["ended_at"] = datetime.now()
        
        return self.running_pipelines[pipeline_id]
    
    async def _execute_stage(
        self,
        pipeline_id: str,
        stage: PipelineStage,
        skill_names: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行单个阶段"""
        
        results = []
        
        for skill_name in skill_names:
            skill = self.registry.get_skill(skill_name)
            if not skill:
                return {
                    "success": False,
                    "error": f"技能未找到: {skill_name}",
                    "data": {}
                }
            
            try:
                result = await skill.execute(context)
                results.append({
                    "skill": skill_name,
                    "success": result.success,
                    "data": result.data,
                    "error": result.error
                })
            except Exception as e:
                results.append({
                    "skill": skill_name,
                    "success": False,
                    "error": str(e),
                    "data": {}
                })
        
        # 合并结果
        all_success = all(r["success"] for r in results)
        merged_data = {}
        for r in results:
            merged_data.update(r.get("data", {}))
        
        errors = [r["error"] for r in results if r.get("error")]
        
        return {
            "success": all_success,
            "data": merged_data,
            "error": "; ".join(errors) if errors else None,
            "details": results
        }
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[dict]:
        """获取流水线状态"""
        return self.running_pipelines.get(pipeline_id)
    
    def cancel_pipeline(self, pipeline_id: str) -> bool:
        """取消流水线"""
        if pipeline_id in self.running_pipelines:
            self.running_pipelines[pipeline_id]["status"] = PipelineStatus.CANCELLED
            logger.info(f"🛑 流水线已取消: {pipeline_id}")
            return True
        return False
