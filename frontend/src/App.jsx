import React, { useState } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  FileText, 
  Wand2, 
  BarChart3, 
  Settings, 
  Cpu,
  Play
} from 'lucide-react';

// 页面组件 (简化占位)
const Dashboard = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold mb-4">🏠 工作台</h1>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <div className="text-3xl font-bold text-blue-600">0</div>
        <div className="text-gray-500">进行中的项目</div>
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <div className="text-3xl font-bold text-green-600">0</div>
        <div className="text-gray-500">已完成视频</div>
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <div className="text-3xl font-bold text-purple-600">12</div>
        <div className="text-gray-500">可用技能</div>
      </div>
    </div>
    
    <div className="mt-8 bg-white rounded-xl p-6 shadow-sm border">
      <h2 className="text-lg font-semibold mb-4">快速开始</h2>
      <Link to="/projects/new" className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
        <Play className="w-4 h-4 mr-2" />
        新建视频项目
      </Link>
    </div>
  </div>
);

const Projects = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold mb-4">🎬 项目管理</h1>
    <p className="text-gray-500">创建和管理您的安全生产视频项目</p>
  </div>
);

const ScriptEditor = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold mb-4">📝 脚本编辑器</h1>
    <p className="text-gray-500">AI辅助分镜脚本编写与拆分</p>
  </div>
);

const SkillLibrary = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold mb-4">🛠️ 技能库 (SKII)</h1>
    <p className="text-gray-500">浏览和配置可复用技能</p>
    <div className="mt-4 space-y-2">
      {['safety-copywriter', 'script-splitter', 'prompt-engineer', 
        'image-generator', 'video-generator', 'tts-narrator', 
        'video-assembler', 'quality-inspector', 'style-analyzer'].map(skill => (
        <div key={skill} className="bg-white rounded-lg p-3 border flex justify-between items-center">
          <span>{skill}</span>
          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">可用</span>
        </div>
      ))}
    </div>
  </div>
);

const Analysis = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold mb-4">📊 视频解析</h1>
    <p className="text-gray-500">上传视频进行多维度分析</p>
  </div>
);

const ModelSettings = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold mb-4">⚙️ 模型配置</h1>
    <p className="text-gray-500">管理LLM API密钥和模型偏好</p>
    <div className="mt-4 bg-white rounded-xl p-6 border">
      <h3 className="font-semibold mb-2">支持的模型</h3>
      <ul className="space-y-2 text-sm">
        <li className="flex items-center"><span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>豆包 (字节跳动)</li>
        <li className="flex items-center"><span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>Kimi (Moonshot)</li>
        <li className="flex items-center"><span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>DeepSeek</li>
        <li className="flex items-center"><span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>通义千问 (阿里云)</li>
        <li className="flex items-center"><span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>万相视频生成</li>
      </ul>
    </div>
  </div>
);

function Sidebar() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: Home, label: '工作台' },
    { path: '/projects', icon: FileText, label: '项目' },
    { path: '/scripts', icon: FileText, label: '脚本' },
    { path: '/skills', icon: Cpu, label: '技能库' },
    { path: '/analysis', icon: BarChart3, label: '视频解析' },
    { path: '/settings', icon: Settings, label: '设置' },
  ];
  
  return (
    <aside className="w-64 bg-white border-r h-screen flex flex-col">
      <div className="p-4 border-b">
        <h1 className="text-xl font-bold text-blue-600">SafetyVideoForge</h1>
        <p className="text-xs text-gray-400">安全生产视频智能工坊</p>
      </div>
      
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(item => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center px-3 py-2 rounded-lg text-sm transition-colors ${
              location.pathname === item.path 
                ? 'bg-blue-50 text-blue-600' 
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <item.icon className="w-4 h-4 mr-3" />
            {item.label}
          </Link>
        ))}
      </nav>
      
      <div className="p-4 border-t text-xs text-gray-400">
        v1.0.0 | SafetyVideoForge
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects/*" element={<Projects />} />
          <Route path="/scripts" element={<ScriptEditor />} />
          <Route path="/skills" element={<SkillLibrary />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/settings" element={<ModelSettings />} />
        </Routes>
      </main>
    </div>
  );
}
