# 🔧 SafetyVideoForge — 安全生产视频智能工坊

> 面向安全生产类视频号博主的本地化自动化视频生产桌面工具
> 从文案输入到成品分发，全流程AI驱动，工业级输出标准

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![Electron](https://img.shields.io/badge/Electron-28+-47848F.svg)](https://electronjs.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 核心功能

### 一、自动化视频生成流水线
| 阶段 | 功能 | 技术方案 |
|------|------|----------|
| 1. 文案生成 | 根据关键词/主题自动生成安全生产类文案，智能检索素材库 | LLM + RAG检索 |
| 2. 脚本拆分 | 按场景/镜头自动拆分为结构化分镜脚本 | LLM + 规则引擎 |
| 3. 画面构想 | 为每个分镜生成详细画面描述及AI绘图/视频提示词 | 多模态LLM |
| 4. 画面生成 | 调用大模型生成工业级、现实3D渲染风格画面 | 文生图/图生视频API |
| 5. 语音与音乐 | 自动生成旁白配音(TTS)及背景音乐 | 火山TTS / 本地TTS + 音乐生成 |
| 6. 质检与合成 | 自动检查各元素质量并合成最终视频 | FFmpeg + MoviePy + 质量评分 |
| 7. 分发 | 一键导出并支持发布到视频号等平台 | 视频号API / 本地导出 |

### 二、视频解析功能
- **语言风格分析**：语气、节奏、表达方式
- **画面风格分析**：色调、构图、转场风格
- **呈现效果评估**：视觉冲击力、信息密度
- **标准评级**：清晰度、专业度分级
- **传播效果预测**：完播率预测、互动潜力评估

### 三、技能库系统（SKII）
模块化可复用技能，按需调用，支持自定义编排。

### 四、多模型接口集成
- 豆包（字节跳动）
- Kimi（Moonshot AI）
- DeepSeek
- 通义千问（阿里云）
- 万相/通义万相（文生视频）

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron + React 桌面端                    │
│         (跨平台UI / 项目管理 / 可视化编排 / 预览)              │
└─────────────────────────────────────────────────────────────┘
                              │ REST API / WebSocket
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI 后端服务                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │项目管理 │ │脚本引擎 │ │生成管线 │ │解析引擎 │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │技能库   │ │LLM网关  │ │素材管理 │ │分发中心 │           │
│  │(SKII)   │ │(多模型) │ │         │ │         │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              FFmpeg / MoviePy / 本地模型推理                   │
│         (视频合成 / 音频处理 / 可选本地图生视频)               │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              云端大模型API (豆包/Kimi/DeepSeek/Qwen)           │
│              文生视频API (万相/Seedance/CogVideo)              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
SafetyVideoForge/
├── backend/              # Python + FastAPI 后端核心
│   ├── app/              # 应用代码
│   │   ├── core/         # 核心引擎（流水线/脚本/质检/分发）
│   │   ├── services/     # 业务服务（LLM/TTS/图像/视频/音乐/解析）
│   │   ├── skills/       # 技能库系统（SKII）
│   │   ├── routers/      # API路由
│   │   ├── models/       # 数据模型
│   │   └── utils/        # 工具函数
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # Electron + React 桌面端
│   ├── src/              # 前端源码
│   └── electron/         # Electron主进程
├── skills_library/       # 可复用技能库（SKII）
│   └── skills/           # 技能定义文件
├── configs/              # 配置文件
│   ├── models.yaml       # 模型API配置
│   └── pipeline.yaml     # 流水线默认配置
├── docs/                 # 文档
│   ├── ARCHITECTURE.md   # 架构设计
│   ├── API.md            # API文档
│   └── DEPLOYMENT.md     # 部署指南
└── docker-compose.yml    # Docker部署
```

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- FFmpeg 6.0+ (系统安装)

### 后端启动
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端启动
```bash
cd frontend
npm install
npm run dev        # 开发模式
npm run build      # 打包桌面应用
```

### Docker部署
```bash
docker-compose up -d
```

---

## 📋 技能库（SKII）概览

| 技能类别 | 示例技能 | 说明 |
|----------|----------|------|
| 内容生成 | `safety-copywriter` | 安全生产文案生成 |
| 内容生成 | `script-splitter` | 分镜脚本拆分 |
| 视觉生成 | `prompt-engineer` | AI绘图/视频提示词生成 |
| 视觉生成 | `image-generator` | 文生图调用 |
| 视觉生成 | `video-generator` | 图生视频调用 |
| 音频生成 | `tts-narrator` | 旁白配音生成 |
| 音频生成 | `bgm-composer` | 背景音乐生成 |
| 合成质检 | `video-assembler` | 视频合成 |
| 合成质检 | `quality-inspector` | 质量检查 |
| 视频解析 | `style-analyzer` | 风格分析 |
| 视频解析 | `impact-evaluator` | 传播效果评估 |

---

## 🔌 支持的模型API

| 模型 | 类型 | 能力 | 推荐场景 |
|------|------|------|----------|
| **豆包** | LLM + 多模态 | 中文理解强，支持角色扮演 | 文案生成、脚本拆分 |
| **Kimi** | LLM | 长文本处理优秀 | 长脚本分析、素材检索 |
| **DeepSeek** | LLM | 推理能力强，性价比高 | 画面构想、提示词优化 |
| **通义千问** | LLM + 多模态 | 中文生态完整 | 通用对话、内容生成 |
| **万相(Wan2.1)** | 视频生成 | 文生视频/图生视频 | 画面生成（推荐） |
| **Seedance** | 视频生成 | 高质量人物/场景 | 人物特写画面 |
| **CogVideo** | 视频生成 | 开源可本地部署 | 本地私有化部署 |

---

## 📜 开源基础框架参考

本项目在以下优秀开源项目的基础上进行架构设计与模块扩展：

| 项目 | 用途 | 链接 |
|------|------|------|
| MoneyPrinterAICreate | 视频生成流水线参考 | [GitHub](https://github.com/q1uki/MoneyPrinterAICreate) |
| ai-mixed-cut | FFmpeg视频处理参考 | [GitHub](https://github.com/toki-plus/ai-mixed-cut) |
| Toonflow-app | 桌面端架构参考 | [GitHub](https://github.com/HBAI-Ltd/Toonflow-app) |
| CogVideo | 开源文生视频模型 | [GitHub](https://github.com/zai-org/CogVideo) |

---

## 📄 License

MIT License © 2026 SafetyVideoForge Team
