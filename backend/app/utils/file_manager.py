"""
文件管理工具
"""
import os
import shutil
from pathlib import Path
from typing import Optional

from app.config import settings


class FileManager:
    """文件管理器"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or settings.TEMP_DIR)
    
    def ensure_dir(self, path: str) -> Path:
        """确保目录存在"""
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p
    
    def save_upload(self, file_data: bytes, filename: str, 
                    subdir: str = "uploads") -> str:
        """保存上传文件"""
        save_dir = self.base_dir / subdir
        save_dir.mkdir(parents=True, exist_ok=True)
        
        save_path = save_dir / filename
        with open(save_path, "wb") as f:
            f.write(file_data)
        
        return str(save_path)
    
    def cleanup_temp(self, max_age_hours: int = 24):
        """清理临时文件"""
        import time
        
        now = time.time()
        max_age = max_age_hours * 3600
        
        for root, dirs, files in os.walk(self.base_dir):
            for f in files:
                path = os.path.join(root, f)
                if now - os.path.getmtime(path) > max_age:
                    os.remove(path)
