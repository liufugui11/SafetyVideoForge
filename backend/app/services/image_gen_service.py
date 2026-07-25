"""
图像生成服务
封装文生图API调用，支持多供应商
"""
import os
import asyncio
from typing import List, Optional, Dict
from pathlib import Path

import httpx
from PIL import Image
from loguru import logger

from app.config import settings
from app.services.llm_service import LLMService


class ImageGenerationService:
    """图像生成服务"""
    
    def __init__(self, llm_service: LLMService, output_dir: str = None):
        self.llm = llm_service
        self.output_dir = Path(output_dir or settings.TEMP_DIR / "images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.http_client = httpx.AsyncClient(timeout=120)
    
    async def generate(
        self,
        prompt: str,
        output_filename: Optional[str] = None,
        provider: str = "qwen",
        size: str = "1024x1024",
        style: str = "industrial_3d"
    ) -> str:
        """
        生成单张图片
        
        Args:
            prompt: 提示词
            output_filename: 输出文件名
            provider: 提供商
            size: 尺寸
            style: 风格标签
        
        Returns:
            本地文件路径
        """
        # 增强提示词
        enhanced_prompt = self._enhance_prompt(prompt, style)
        
        if not output_filename:
            import hashlib
            prompt_hash = hashlib.md5(enhanced_prompt.encode()).hexdigest()[:12]
            output_filename = f"img_{provider}_{prompt_hash}.png"
        
        output_path = self.output_dir / output_filename
        
        # 缓存检查
        if output_path.exists():
            logger.debug(f"🎯 图像缓存命中: {output_filename}")
            return str(output_path)
        
        try:
            # 调用API生成
            image_url = await self.llm.generate_image(
                enhanced_prompt, 
                provider_name=provider,
                size=size
            )
            
            # 下载图片
            await self._download_image(image_url, output_path)
            
            logger.info(f"🖼️ 图像生成完成: {output_filename}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ 图像生成失败: {e}")
            raise
    
    async def generate_batch(
        self,
        prompts: List[str],
        provider: str = "qwen",
        size: str = "1024x1024",
        style: str = "industrial_3d",
        max_concurrent: int = 3
    ) -> List[str]:
        """
        批量生成图片（带并发控制）
        
        Args:
            prompts: 提示词列表
            provider: 提供商
            size: 尺寸
            style: 风格
            max_concurrent: 最大并发数
        
        Returns:
            文件路径列表
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def _generate_one(i: int, prompt: str) -> str:
            async with semaphore:
                filename = f"batch_{i+1:03d}.png"
                return await self.generate(prompt, filename, provider, size, style)
        
        tasks = [_generate_one(i, p) for i, p in enumerate(prompts)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        paths = []
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"批量生图失败: {r}")
                paths.append(None)
            else:
                paths.append(r)
        
        return paths
    
    async def _download_image(self, url: str, output_path: Path):
        """下载图片"""
        response = await self.http_client.get(url)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """增强提示词"""
        style_enhancements = {
            "industrial_3d": "3D render, industrial environment, realistic materials, professional lighting, safety equipment, high detail, 8k quality",
            "realistic": "photorealistic, documentary photography, natural lighting, real world scene, high resolution",
            "animation": "motion graphics style, clean vector art, smooth gradients, professional animation style",
        }
        
        enhancement = style_enhancements.get(style, style_enhancements["industrial_3d"])
        
        # 避免重复
        if enhancement.lower() in prompt.lower():
            return prompt
        
        return f"{prompt}, {enhancement}"
    
    def resize_for_video(self, image_path: str, target_size: tuple = (1080, 1920)) -> str:
        """
        调整图片尺寸为视频比例 (9:16竖屏)
        
        Args:
            image_path: 图片路径
            target_size: 目标尺寸 (宽, 高)
        
        Returns:
            调整后图片路径
        """
        img = Image.open(image_path)
        
        # 创建目标比例的画布
        target_w, target_h = target_size
        target_ratio = target_w / target_h
        
        img_w, img_h = img.size
        img_ratio = img_w / img_h
        
        if img_ratio > target_ratio:
            # 图片更宽，按高度缩放
            new_h = target_h
            new_w = int(new_h * img_ratio)
        else:
            # 图片更高，按宽度缩放
            new_w = target_w
            new_h = int(new_w / img_ratio)
        
        img = img.resize((new_w, new_h), Image.LANCZOS)
        
        # 居中裁剪
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        img = img.crop((left, top, left + target_w, top + target_h))
        
        # 保存
        output_path = image_path.replace(".png", "_video.png").replace(".jpg", "_video.jpg")
        img.save(output_path, quality=95)
        
        return output_path
    
    async def close(self):
        await self.http_client.aclose()
