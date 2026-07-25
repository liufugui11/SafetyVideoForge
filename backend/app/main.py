"""
SafetyVideoForge - FastAPI Application
安全生产视频智能工坊后端服务
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import projects, scripts, skills, generation, analysis, models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    from app.skills.registry import SkillRegistry
    from app.core.pipeline import PipelineEngine
    
    app.state.skill_registry = SkillRegistry()
    app.state.skill_registry.load_all_skills()
    
    app.state.pipeline_engine = PipelineEngine(
        registry=app.state.skill_registry
    )
    
    print(f"🚀 SafetyVideoForge Backend started at {settings.HOST}:{settings.PORT}")
    print(f"📚 API文档: http://{settings.HOST}:{settings.PORT}/docs")
    yield
    # 关闭时清理
    print("👋 SafetyVideoForge Backend shutting down...")


app = FastAPI(
    title="SafetyVideoForge API",
    description="安全生产视频智能工坊 - 自动化视频生成与解析",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件 (输出目录)
app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")

# 注册路由
app.include_router(projects.router, prefix="/api/v1/projects", tags=["项目管理"])
app.include_router(scripts.router, prefix="/api/v1/scripts", tags=["脚本管理"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["技能库"])
app.include_router(generation.router, prefix="/api/v1/generation", tags=["视频生成"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["视频解析"])
app.include_router(models.router, prefix="/api/v1/models", tags=["模型管理"])


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "SafetyVideoForge"
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "SafetyVideoForge",
        "description": "安全生产视频智能工坊",
        "docs": "/docs",
        "version": "1.0.0"
    }
