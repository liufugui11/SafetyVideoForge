"""
分发模块 - 视频导出与平台发布
"""
import os
import shutil
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from loguru import logger


class Distributor:
    """分发器"""
    
    # 平台配置
    PLATFORM_CONFIGS = {
        "视频号": {
            "format": "mp4",
            "max_duration": 300,      # 5分钟
            "max_size_mb": 1000,      # 1GB
            "recommended_resolution": (1080, 1920),
            "recommended_fps": 30,
        },
        "抖音": {
            "format": "mp4",
            "max_duration": 600,      # 10分钟
            "max_size_mb": 4000,      # 4GB
            "recommended_resolution": (1080, 1920),
            "recommended_fps": 30,
        },
        "快手": {
            "format": "mp4",
            "max_duration": 600,
            "max_size_mb": 2000,
            "recommended_resolution": (1080, 1920),
            "recommended_fps": 30,
        },
        "本地导出": {
            "format": "mp4",
            "max_duration": None,
            "max_size_mb": None,
            "recommended_resolution": (1080, 1920),
            "recommended_fps": 30,
        }
    }
    
    def __init__(self, output_dir: str = "./outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def export_video(
        self,
        video_path: str,
        project_name: str,
        platform: str = "视频号",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        导出视频到指定平台格式
        
        Args:
            video_path: 源视频路径
            project_name: 项目名称
            platform: 目标平台
            metadata: 视频元数据
        
        Returns:
            导出结果
        """
        config = self.PLATFORM_CONFIGS.get(platform, self.PLATFORM_CONFIGS["本地导出"])
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self._sanitize_filename(project_name)
        output_name = f"{safe_name}_{platform}_{timestamp}.{config['format']}"
        output_path = self.output_dir / output_name
        
        try:
            # 复制/转码视频
            # 简化处理：直接复制，实际生产应使用FFmpeg转码
            shutil.copy2(video_path, output_path)
            
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            
            result = {
                "success": True,
                "output_path": str(output_path),
                "platform": platform,
                "file_size_mb": round(file_size, 2),
                "filename": output_name,
                "message": f"视频已导出: {output_name}"
            }
            
            # 检查平台限制
            if config["max_size_mb"] and file_size > config["max_size_mb"]:
                result["warning"] = f"文件大小({file_size:.1f}MB)超出平台限制({config['max_size_mb']}MB)"
            
            logger.info(f"📤 视频导出成功: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 视频导出失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform
            }
    
    async def batch_export(
        self,
        video_path: str,
        project_name: str,
        platforms: List[str],
        metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """批量导出到多个平台"""
        results = []
        for platform in platforms:
            result = await self.export_video(video_path, project_name, platform, metadata)
            results.append(result)
        return results
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name[:50]  # 限制长度
    
    async def prepare_platform_upload(
        self,
        video_path: str,
        platform: str,
        title: str = "",
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        准备平台上传信息
        
        注：实际发布需要各平台的API授权，此处仅生成准备信息
        """
        tags = tags or []
        
        # 安全生产类标签建议
        default_tags = ["安全生产", "安全教育", "安全规范", "安全意识"]
        all_tags = list(set(default_tags + tags))
        
        return {
            "platform": platform,
            "video_path": video_path,
            "title": title,
            "description": description,
            "tags": all_tags,
            "suggested_cover_time": 1.0,  # 建议封面截取时间点
            "note": "请使用对应平台的创作者工具完成最终发布",
            "platform_links": {
                "视频号": "https://channels.weixin.qq.com/",
                "抖音": "https://creator.douyin.com/",
                "快手": "https://cp.kuaishou.com/",
            }
        }
