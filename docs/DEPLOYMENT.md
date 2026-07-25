# 🚀 SafetyVideoForge 部署指南

## 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4核 | 8核+ |
| RAM | 8GB | 16GB+ |
| 磁盘 | 20GB | 100GB SSD |
| GPU | 可选 | NVIDIA RTX 3060+ (本地视频生成) |
| 网络 | 稳定互联网 | 高速网络 (API调用) |

## 依赖安装

### 1. 安装 FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
下载 [FFmpeg](https://ffmpeg.org/download.html) 并添加到 PATH

### 2. 安装 Python 依赖

```bash
cd backend
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. 安装 Node.js 依赖

```bash
cd frontend
npm install
```

## 配置API密钥

复制配置文件模板并填写你的API密钥：

```bash
cp configs/models.yaml.template configs/models.yaml
```

编辑 `configs/models.yaml`：

```yaml
providers:
  doubao:
    api_key: "your-doubao-api-key"
    base_url: "https://ark.cn-beijing.volces.com/api/v3"
    default_model: "doubao-pro-128k"
    
  kimi:
    api_key: "your-kimi-api-key"
    base_url: "https://api.moonshot.cn/v1"
    default_model: "moonshot-v1-128k"
    
  deepseek:
    api_key: "your-deepseek-api-key"
    base_url: "https://api.deepseek.com/v1"
    default_model: "deepseek-chat"
    
  qwen:
    api_key: "your-qwen-api-key"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    default_model: "qwen-max"
    
  wanx:
    api_key: "your-wanx-api-key"
    base_url: "https://dashscope.aliyuncs.com/api/v1"
    # 文生视频
    video_model: "wanx2.1-t2v-plus"
    # 图生视频
    image_to_video_model: "wanx2.1-i2v-plus"
```

## 启动方式

### 方式一：开发模式（推荐开发）

**终端1 - 启动后端：**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**终端2 - 启动前端：**
```bash
cd frontend
npm run dev
```

### 方式二：Docker部署

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 方式三：打包桌面应用

```bash
cd frontend
npm run build
npm run dist
```

打包后的应用位于 `frontend/dist/` 目录。

## 验证安装

1. 打开浏览器访问 `http://localhost:8000/docs` 查看后端API文档
2. 桌面端应用启动后，在设置页面测试各模型API连通性
3. 创建一个测试项目，运行完整流水线验证

## 常见问题

### Q: FFmpeg 未找到？
确保 FFmpeg 已安装并在 PATH 中：
```bash
ffmpeg -version
```

### Q: CUDA/GPU 支持？
如需本地视频生成加速，安装 CUDA 版 PyTorch：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Q: 模型API调用失败？
检查 `configs/models.yaml` 中的 API 密钥和 base_url 是否正确，并确保网络可访问对应服务。

---

## 目录结构说明

| 目录 | 用途 |
|------|------|
| `backend/data/` | 数据库、项目元数据 |
| `backend/outputs/` | 生成的视频、音频、图像 |
| `backend/temp/` | 临时文件（自动清理） |
| `frontend/dist/` | 打包后的桌面应用 |
