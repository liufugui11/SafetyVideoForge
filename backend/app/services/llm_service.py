"""
LLM 统一服务层 - 多模型网关
支持：豆包、Kimi、DeepSeek、通义千问
"""
import os
import yaml
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings


class BaseLLMProvider(ABC):
    """LLM提供商基类"""
    
    def __init__(self, api_key: str, base_url: str, default_model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.client = httpx.AsyncClient(
            timeout=settings.LLM_TIMEOUT,
            headers={"Authorization": f"Bearer {api_key}"}
        )
    
    @abstractmethod
    async def chat(self, messages: list, model: Optional[str] = None, 
                   temperature: float = 0.7, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def generate_video(self, prompt: str, **kwargs) -> str:
        pass
    
    async def close(self):
        await self.client.aclose()


class OpenAICompatibleProvider(BaseLLMProvider):
    """OpenAI兼容格式提供商"""
    
    async def chat(self, messages: list, model: Optional[str] = None,
                   temperature: float = 0.7, json_mode: bool = False, **kwargs) -> str:
        """对话"""
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": messages if isinstance(messages, list) else [
                {"role": "user", "content": messages}
            ],
            "temperature": temperature,
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"LLM调用失败 [{self.__class__.__name__}]: {e}")
            raise
    
    async def generate_image(self, prompt: str, **kwargs) -> str:
        """文生图 (需要供应商支持)"""
        raise NotImplementedError("该供应商不支持文生图")
    
    async def generate_video(self, prompt: str, **kwargs) -> str:
        """文生视频 (需要供应商支持)"""
        raise NotImplementedError("该供应商不支持文生视频")


class DoubaoProvider(OpenAICompatibleProvider):
    """豆包 (字节跳动)"""
    pass


class KimiProvider(OpenAICompatibleProvider):
    """Kimi (Moonshot)"""
    pass


class DeepSeekProvider(OpenAICompatibleProvider):
    """DeepSeek"""
    pass


class QwenProvider(OpenAICompatibleProvider):
    """通义千问 (阿里云)"""
    
    async def generate_image(self, prompt: str, size: str = "1024x1024", **kwargs) -> str:
        """通义万相文生图"""
        try:
            response = await self.client.post(
                f"{self.base_url}/images/generations",
                json={
                    "model": "wanx-v1",
                    "prompt": prompt,
                    "size": size
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["url"]
        except Exception as e:
            logger.error(f"万相生图失败: {e}")
            raise


class WanxVideoProvider(BaseLLMProvider):
    """
    万相视频生成 (通义万相 Wan2.1)
    支持：文生视频、图生视频
    """
    
    async def chat(self, messages: list, **kwargs) -> str:
        raise NotImplementedError("视频模型不支持对话")
    
    async def generate_image(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("视频模型不支持生图")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=30))
    async def generate_video(self, prompt: str, image_url: Optional[str] = None,
                            duration: int = 5, resolution: str = "720p", **kwargs) -> str:
        """
        生成视频
        
        Args:
            prompt: 提示词
            image_url: 图片URL (图生视频时传入)
            duration: 时长(秒)
            resolution: 分辨率
        """
        model = "wanx2.1-t2v-plus" if image_url is None else "wanx2.1-i2v-plus"
        
        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
            }
        }
        
        if image_url:
            payload["input"]["img_url"] = image_url
        
        try:
            # 提交任务
            response = await self.client.post(
                f"{self.base_url}/services/aigc/video-generation/generation",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            task_id = data.get("output", {}).get("task_id")
            if not task_id:
                raise ValueError(f"未获取到task_id: {data}")
            
            logger.info(f"🎬 视频生成任务提交: {task_id}")
            
            # 轮询结果
            return await self._poll_video_result(task_id)
            
        except Exception as e:
            logger.error(f"万相视频生成失败: {e}")
            raise
    
    async def _poll_video_result(self, task_id: str, max_wait: int = 300) -> str:
        """轮询视频生成结果"""
        import asyncio
        
        waited = 0
        while waited < max_wait:
            response = await self.client.get(
                f"{self.base_url}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            data = response.json()
            
            status = data.get("output", {}).get("task_status", "PENDING")
            
            if status == "SUCCEEDED":
                video_url = data.get("output", {}).get("video_url")
                logger.info(f"✅ 视频生成完成: {task_id}")
                return video_url
            
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"视频生成失败: {status}")
            
            await asyncio.sleep(5)
            waited += 5
        
        raise TimeoutError(f"视频生成超时: {task_id}")


class LLMService:
    """
    LLM统一服务
    根据任务类型自动路由到最优模型
    """
    
    # 任务到首选模型的映射
    TASK_ROUTING = {
        "copywriting": "doubao",      # 文案生成 -> 豆包（中文强）
        "script_split": "deepseek",   # 脚本拆分 -> DeepSeek（推理强）
        "prompt_engineer": "deepseek", # 提示词工程 -> DeepSeek
        "long_context": "kimi",        # 长文本 -> Kimi
        "general": "qwen",             # 通用 -> 通义千问
    }
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._load_providers()
    
    def _load_providers(self):
        """从配置文件加载所有模型提供商"""
        config_path = settings.CONFIGS_DIR / "models.yaml"
        
        if not config_path.exists():
            logger.warning(f"模型配置文件不存在: {config_path}")
            return
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        provider_map = {
            "doubao": DoubaoProvider,
            "kimi": KimiProvider,
            "deepseek": DeepSeekProvider,
            "qwen": QwenProvider,
            "wanx": WanxVideoProvider,
        }
        
        for name, cfg in config.get("providers", {}).items():
            provider_cls = provider_map.get(name)
            if not provider_cls:
                logger.warning(f"未知的提供商: {name}")
                continue
            
            try:
                provider = provider_cls(
                    api_key=cfg.get("api_key", ""),
                    base_url=cfg.get("base_url", ""),
                    default_model=cfg.get("default_model", "")
                )
                self.providers[name] = provider
                logger.info(f"✅ 模型提供商加载成功: {name} ({cfg.get('default_model', '')})")
            except Exception as e:
                logger.error(f"❌ 加载提供商失败 {name}: {e}")
    
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """获取指定提供商"""
        return self.providers.get(name)
    
    def select_provider(self, task_type: str = "general") -> BaseLLMProvider:
        """
        根据任务类型选择最优模型
        
        Args:
            task_type: 任务类型
        
        Returns:
            最优提供商
        """
        preferred = self.TASK_ROUTING.get(task_type, "qwen")
        
        if preferred in self.providers:
            return self.providers[preferred]
        
        # 回退到任意可用
        if self.providers:
            return next(iter(self.providers.values()))
        
        raise RuntimeError("没有可用的LLM提供商，请检查配置文件")
    
    async def chat(self, prompt: str, model_preference: str = "auto",
                   task_type: str = "general", **kwargs) -> str:
        """
        统一对话接口
        
        Args:
            prompt: 提示词(字符串)或消息列表
            model_preference: 模型偏好 (auto/doubao/kimi/deepseek/qwen)
            task_type: 任务类型(用于自动路由)
        """
        if model_preference == "auto":
            provider = self.select_provider(task_type)
        else:
            provider = self.get_provider(model_preference)
            if not provider:
                logger.warning(f"指定模型不可用: {model_preference}, 使用自动路由")
                provider = self.select_provider(task_type)
        
        return await provider.chat(prompt, **kwargs)
    
    async def generate_image(self, prompt: str, provider_name: str = "qwen", **kwargs) -> str:
        """文生图"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"图像生成提供商不可用: {provider_name}")
        return await provider.generate_image(prompt, **kwargs)
    
    async def generate_video(self, prompt: str, image_url: Optional[str] = None,
                            provider_name: str = "wanx", **kwargs) -> str:
        """文生视频/图生视频"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"视频生成提供商不可用: {provider_name}")
        return await provider.generate_video(prompt, image_url=image_url, **kwargs)
    
    async def close_all(self):
        """关闭所有连接"""
        for name, provider in self.providers.items():
            await provider.close()
            logger.info(f"🔌 关闭连接: {name}")
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """获取可用模型列表"""
        return {
            name: {
                "default_model": p.default_model,
                "base_url": p.base_url,
            }
            for name, p in self.providers.items()
        }
