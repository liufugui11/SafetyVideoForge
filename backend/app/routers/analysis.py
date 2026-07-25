"""
视频解析路由
"""
from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/analyze")
async def analyze_video(video_path: str):
    """分析视频"""
    from app.services.video_analyzer import VideoAnalyzer
    
    analyzer = VideoAnalyzer()
    report = await analyzer.analyze(video_path)
    
    return {
        "overall_score": report.overall_score,
        "language_style": report.language_style,
        "visual_style": report.visual_style,
        "presentation": report.presentation,
        "quality_rating": report.quality_rating,
        "viral_potential": report.viral_potential,
        "suggestions": report.suggestions,
    }


@router.post("/compare")
async def compare_videos(video_paths: list):
    """对比多个视频"""
    from app.services.video_analyzer import VideoAnalyzer
    
    analyzer = VideoAnalyzer()
    results = []
    
    for path in video_paths:
        report = await analyzer.analyze(path)
        results.append({
            "video_path": path,
            "overall_score": report.overall_score,
        })
    
    # 排序
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    
    return {"comparison": results}
