# 🏗️ SafetyVideoForge 系统架构设计

> 版本: v1.0.0 | 日期: 2026-07-26 | 状态: 设计阶段

---

## 1. 架构总览

SafetyVideoForge 采用 **前后端分离 + 模块化技能编排** 的架构模式：

- **前端**：Electron + React，提供跨平台桌面体验
- **后端**：Python + FastAPI，提供高性能异步API
- **核心引擎**：流水线驱动，技能可插拔
- **模型层**：统一网关，支持多模型热切换

---

## 2. 核心模块设计

### 2.1 视频生成流水线 (Video Generation Pipeline)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  输入    │───→│ 脚本引擎 │───→│ 素材工厂 │───→│ 合成车间 │
│ Input    │    │ Script   │    │ Material │    │ Assembly │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     ▼               ▼               ▼               ▼
  关键词/主题    分镜脚本JSON    图像/视频/音频    成品视频
```

**流水线阶段：**

| 阶段 | 模块 | 输入 | 输出 | 关键技能 |
|------|------|------|------|----------|
| P1 | 文案生成 | 关键词/主题 | 完整文案 | `safety-copywriter` |
| P2 | 脚本拆分 | 文案 | 分镜脚本(JSON) | `script-splitter` |
| P3 | 画面构想 | 分镜脚本 | 画面描述+提示词 | `prompt-engineer` |
| P4 | 素材生成 | 提示词列表 | 图像/视频片段 | `image-generator`, `video-generator` |
| P5 | 音频生成 | 文案/脚本 | TTS配音+BGM | `tts-narrator`, `bgm-composer` |
| P6 | 质检合成 | 所有素材 | 质检报告+成品 | `video-assembler`, `quality-inspector` |
| P7 | 分发 | 成品视频 | 发布/导出 | `distributor` |

### 2.2 脚本引擎 (Script Engine)

**分镜脚本 JSON Schema：**
```json
{
  "project_id": "uuid",
  "title": "视频标题",
  "duration_estimate": 60,
  "scenes": [
    {
      "scene_id": 1,
      "type": "opening|content|transition|closing",
      "duration": 5,
      "narration": "旁白文本",
      "visual_description": "画面描述",
      "prompt_image": "文生图提示词",
      "prompt_video": "图生视频提示词",
      "style_preset": "industrial_3d|realistic|animation",
      "assets": []
    }
  ]
}
```

### 2.3 视频解析引擎 (Video Analysis Engine)

**解析维度：**

```
输入视频
    ├── 语言风格分析
    │     ├── 语气检测 (正式/口语化/警示)
    │     ├── 节奏分析 (语速/停顿/重音)
    │     └── 表达方式 (叙述/对话/指令)
    ├── 画面风格分析
    │     ├── 色调分析 (色温/饱和度/对比度)
    │     ├── 构图分析 (三分法/中心/引导线)
    │     └── 转场风格 (硬切/淡入淡出/特效)
    ├── 呈现效果评估
    │     ├── 视觉冲击力 (动态范围/运动/景深)
    │     └── 信息密度 (单位时间信息熵)
    ├── 标准评级
    │     ├── 清晰度评分 (分辨率/锐度/压缩质量)
    │     └── 专业度评级 (行业对标)
    └── 传播效果预测
          ├── 完播率预测 (基于历史数据模型)
          └── 互动潜力评估 (点赞/评论/转发概率)
```

---

## 3. 技能库系统 (SKII - Skill Kit for Intelligent Ingenuity)

### 3.1 技能架构

```
skills/
├── base.py                    # 技能基类
├── registry.py                # 技能注册中心
├── content_skills/            # 内容生成
│   ├── safety_copywriter/     # 安全生产文案
│   ├── script_splitter/       # 脚本拆分
│   └── prompt_engineer/       # 提示词工程
├── visual_skills/             # 视觉生成
│   ├── image_generator/       # 文生图
│   ├── video_generator/       # 图生视频
│   └── style_transfer/        # 风格迁移
├── audio_skills/              # 音频生成
│   ├── tts_narrator/          # TTS配音
│   ├── bgm_composer/          # 背景音乐
│   └── audio_mixer/           # 音频混音
├── synthesis_skills/          # 合成质检
│   ├── video_assembler/       # 视频合成
│   ├── quality_inspector/     # 质量检查
│   └── subtitle_generator/    # 字幕生成
└── analysis_skills/           # 视频解析
    ├── style_analyzer/        # 风格分析
    ├── impact_evaluator/      # 效果评估
    └── viral_predictor/       # 传播预测
```

### 3.2 技能接口定义

```python
class BaseSkill(ABC):
    """所有技能的基类"""
    
    name: str           # 技能唯一标识
    category: str       # 技能类别
    version: str        # 版本
    description: str    # 描述
    
    @abstractmethod
    async def execute(self, context: SkillContext) -> SkillResult:
        """执行技能"""
        pass
    
    @abstractmethod
    def validate_input(self, params: dict) -> ValidationResult:
        """验证输入参数"""
        pass
```

### 3.3 技能编排

支持两种编排模式：

1. **顺序流水线**：固定阶段顺序执行
2. **DAG编排**：有向无环图，支持并行与条件分支

---

## 4. 多模型网关 (LLM Gateway)

### 4.1 统一接口

```python
class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list, **kwargs) -> str: ...
    
    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> str: ...
    
    @abstractmethod
    async def generate_video(self, prompt: str, **kwargs) -> str: ...
```

### 4.2 路由策略

| 任务类型 | 首选模型 | 备选模型 | 选择依据 |
|----------|----------|----------|----------|
| 中文文案生成 | 豆包 | 通义千问 | 中文语境理解 |
| 长文本分析 | Kimi | DeepSeek | 上下文长度 |
| 推理/提示词优化 | DeepSeek | 豆包 | 推理能力 |
| 文生图 | 通义万相 | 豆包 | 中文元素渲染 |
| 图生视频 | 万相(Wan2.1) | Seedance | 运动质量 |
| 本地部署 | CogVideo | - | 私有化需求 |

---

## 5. 数据流设计

```
用户输入
  │
  ▼
┌─────────────┐
│ 项目创建    │ ──→ 项目配置存储 (SQLite/JSON)
└─────────────┘
  │
  ▼
┌─────────────┐
│ 流水线执行  │ ──→ 状态机管理 (Redis/内存)
└─────────────┘
  │
  ├──→ 文案 ──→ LLM调用 ──→ 文案结果
  │
  ├──→ 脚本 ──→ 规则引擎 ──→ 分镜JSON
  │
  ├──→ 画面 ──→ 并发API调用 ──→ 素材文件
  │
  ├──→ 音频 ──→ TTS+音乐 ──→ 音频文件
  │
  └──→ 合成 ──→ FFmpeg ──→ 成品视频
  │
  ▼
┌─────────────┐
│ 质检报告    │ ──→ 质量评分 + 改进建议
└─────────────┘
  │
  ▼
┌─────────────┐
│ 导出/分发   │ ──→ 本地文件 / 平台API
└─────────────┘
```

---

## 6. 技术选型理由

| 技术 | 选型 | 理由 |
|------|------|------|
| 后端框架 | FastAPI | 高性能异步、自动文档、Python生态 |
| 桌面端 | Electron+React | 跨平台、UI灵活、前端生态丰富 |
| 视频处理 | FFmpeg+MoviePy | 工业标准、功能完备、Python绑定 |
| 数据存储 | SQLite+文件系统 | 本地化部署、零配置、足够轻量 |
| 消息队列 | 异步IO( asyncio ) | 简化架构、无需外部依赖 |
| 配置管理 | YAML | 可读性强、支持注释、层级结构 |

---

## 7. 部署架构

### 7.1 开发模式
```
[Electron Dev] ←──→ [FastAPI Dev Server :8000]
                          │
                    [本地文件系统]
```

### 7.2 生产模式 (Docker)
```
┌────────────────────────────────────────┐
│         Docker Compose                 │
│  ┌─────────┐      ┌─────────────┐     │
│  │ Backend │◄────►│   Frontend  │     │
│  │ :8000   │      │  (Electron) │     │
│  └────┬────┘      └─────────────┘     │
│       │                                │
│  ┌────┴────┐                          │
│  │ 数据卷  │ ./data ./outputs         │
│  └─────────┘                          │
└────────────────────────────────────────┘
```
