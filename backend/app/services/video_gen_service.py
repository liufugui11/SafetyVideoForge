"""
视频生成服务
封装图生视频/文生视频API调用
"""
import os
import asyncio
from typing import List, Optional
from pathlib import Path

from loguru import logger

from app.config import settings
from app.services.llm_service import LLMService


class VideoGenerationService:
    """视频生成服务"""
    
    def __init__(self, llm_service: LLMService, output_dir: str = None):
        self.llm = llm_service
        self.output_dir = Path(output_dir or settings.TEMP_DIR / "videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_from_image(
        self,
        image_path: str,
        prompt: str,
        output_filename: Optional[str] = None,
        provider: str = "wanx",
        duration: int = 5
    ) -> str:
        """
        图生视频
        
        Args:
            image_path: 输入图片路径
            prompt: 视频运动描述
            output_filename: 输出文件名
            provider: 提供商
            duration: 时长(秒)
        
        Returns:
            视频文件路径
        """
        if not output_filename:
            import hashlib
            img_hash = hashlib.md5(image_path.encode()).hexdigest()[:8]
            output_filename = f"vid_i2v_{img_hash}.mp4"
        
        output_path = self.output_dir / output_filename
        
        if output_path.exists():
            logger.debug(f"🎯 视频缓存命中: {output_filename}")
            return str(output_path)
        
        try:
            # 上传图片获取URL (简化：假设使用本地路径或已上传的URL)
            # 实际生产需要上传到对象存储
            image_url = f"file://{image_path}"  # 需要替换为实际可访问URL
            
            video_url = await self.llm.generate_video(
                prompt=prompt,
                image_url=image_url,
                provider_name=provider,
                duration=duration
            )
            
            # 下载视频
            await self._download_video(video_url, output_path)
            
            logger.info(f"🎬 图生视频完成: {output_filename}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ 图生视频失败: {e}")
            raise
    
    async def generate_from_text(
        self,
        prompt: str,
        output_filename: Optional[str] = None,
        provider: str = "wanx",
        duration: int = 5
    ) -> str:
        """
        文生视频
        
        Args:
            prompt: 提示词
            output_filename: 输出文件名
            provider: 提供商
            duration: 时长(秒)
        
        Returns:
            视频文件路径
        """
        if not output_filename:
            import hashlib
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
            output_filename = f"vid_t2v_{prompt_hash}.mp4"
        
        output_path = self.output_dir / output_filename
        
        if output_path.exists():
            logger.debug(f"🎯 视频缓存命中: {output_filename}")
            return str(output_path)
        
        try:
            video_url = await self.llm.generate_video(
                prompt=prompt,
                provider_name=provider,
                duration=duration
            )
            
            await self._download_video(video_url, output_path)
            
            logger.info(f"🎬 文生视频完成: {output_filename}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ 文生视频失败: {e}")
            raise
    
    async def generate_batch(
        self,
        items: List[dict],  # [{"type": "i2v", "image_path": "...", "prompt": "..."}, ...]
        provider: str = "wanx",
        max_concurrent: int = 2
    ) -> List[str]:
        """
        批量生成视频（带并发控制）
        
        注意：视频生成API通常并发限制较严格，建议 max_concurrent <= 2
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def _generate_one(i: int, item: dict) -> str:
            async with semaphore:
                filename = f"scene_{i+1:03d}.mp4"
                
                if item.get("type") == "i2v":
                    return await self.generate_from_image(
                        image_path=item["image_path"],
                        prompt=item["prompt"],
                        output_filename=filename,
                        provider=provider
                    )
                else:
                    return await self.generate_from_text(
                        prompt=item["prompt"],
                        output_filename=filename,
                        provider=provider
                    )
        
        tasks = [_generate_one(i, item) for i, item in enumerate(items)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        paths = []
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"批量视频生成失败: {r}")
                paths.append(None)
            else:
                paths.append(r)
        
        return paths
    
    async def _download_video(self, url: str, output_path: Path):
        """下载视频"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=120)
            response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(response.content)
