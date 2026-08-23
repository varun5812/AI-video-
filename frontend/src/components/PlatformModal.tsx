import React, { useState } from 'react'
import { 
  X, 
  FolderGit2, 
  History as HistoryIcon, 
  Star, 
  Settings as SettingsIcon, 
  Search, 
  Check, 
  Trash2, 
  Plus, 
  ExternalLink,
  KeyRound,
  Cpu,
  Sparkles,
  Play
} from 'lucide-react'

interface PlatformModalProps {
  activeModal: 'projects' | 'history' | 'favorites' | 'settings' | null
  onClose: () => void
  googleKeyOk: boolean
  groqKeyOk: boolean
  selectedModel: string
  setSelectedModel: (model: string) => void
  onSelectHistoryPrompt?: (prompt: string) => void
}

export default function PlatformModal({
  activeModal,
  onClose,
  googleKeyOk,
  groqKeyOk,
  selectedModel,
  setSelectedModel,
  onSelectHistoryPrompt
}: PlatformModalProps) {
  const [historySearch, setHistorySearch] = useState('')
  const [activeTabSetting, setActiveTabSetting] = useState<'api' | 'model' | 'system'>('api')
  
  // Custom API key state overrides
  const [customGoogleKey, setCustomGoogleKey] = useState('')
  const [customGroqKey, setCustomGroqKey] = useState('')
  const [keySavedMsg, setKeySavedMsg] = useState(false)

  // Mock initial project items
  const [projectsList, setProjectsList] = useState([
    { id: 1, title: 'AI & Future of Tech Keynote', type: 'Video Analysis', date: 'Just now', items: 12, tag: 'Video AI' },
    { id: 2, title: 'LangChain & RAG Pipeline Study', type: 'Chat Session', date: '2 hours ago', items: 8, tag: 'Chat AI' },
    { id: 3, title: 'Qwen 3.6 27B Benchmark Data', type: 'Chat Session', date: 'Yesterday', items: 15, tag: 'Chat AI' },
    { id: 4, title: 'Kannada Audio Subtitles Project', type: 'Video Analysis', date: '3 days ago', items: 5, tag: 'Video AI' },
  ])
  const [newProjectName, setNewProjectName] = useState('')

  // Mock History items
  const [historyItems, setHistoryItems] = useState([
    { id: 1, type: 'chat', query: 'Explain general relativity in simple terms with an analogy', model: '✨ Google — Gemini 3.6 Flash', time: '10:42 AM' },
    { id: 2, type: 'video', query: 'Analyzed YouTube Video: AI Keynote 2026', model: '🧠 Groq — Qwen 3.6 27B', time: '09:15 AM' },
    { id: 3, type: 'chat', query: 'Write a Python function to parse URL query parameters', model: '✨ Google — Gemini 3.6 Flash', time: 'Yesterday' },
    { id: 4, type: 'chat', query: 'What is RAG (Retrieval-Augmented Generation)?', model: '🧠 Groq — Qwen 3.6 27B', time: 'Yesterday' },
  ])

  // Mock Favorites items
  const [favoritesList, setFavoritesList] = useState([
    { id: 1, title: '45% Compute Token Cost Reduction', desc: 'According to Vance (Director of Platform), implementing smaller specialized routers resulted in a 45% cost drop.', category: 'Video Takeaway' },
    { id: 2, title: 'Python URL Parser Snippet', desc: 'Standard urllib.parse implementation for URL query extraction.', category: 'Code Snippet' },
    { id: 3, title: 'General Relativity Rubber Sheet Analogy', desc: 'Mass curves space-time, and space-time curvature dictates how objects move.', category: 'Concept Explanation' },
  ])

  if (!activeModal) return null

  const handleAddProject = () => {
    if (!newProjectName.trim()) return
    setProjectsList(prev => [
      { id: Date.now(), title: newProjectName, type: 'Custom Project', date: 'Just now', items: 1, tag: 'Workspace' },
      ...prev
    ])
    setNewProjectName('')
  }

  const handleClearHistory = () => {
    setHistoryItems([])
  }

  const handleSaveKeys = () => {
    setKeySavedMsg(true)
    setTimeout(() => setKeySavedMsg(false), 3000)
  }

  const filteredHistory = historyItems.filter(item => 
    item.query.toLowerCase().includes(historySearch.toLowerCase()) ||
    item.model.toLowerCase().includes(historySearch.toLowerCase())
  )

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-[fadeIn_0.2s_ease-out]">
      <div className="glass-panel border border-white/10 rounded-3xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden relative">
        
        {/* Modal Header */}
        <div className="flex justify-between items-center p-5 border-b border-white/5 bg-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              {activeModal === 'projects' && <FolderGit2 className="w-5 h-5" />}
              {activeModal === 'history' && <HistoryIcon className="w-5 h-5" />}
              {activeModal === 'favorites' && <Star className="w-5 h-5" />}
              {activeModal === 'settings' && <SettingsIcon className="w-5 h-5" />}
            </div>
            <div>
              <h3 className="font-extrabold text-base text-white capitalize">
                {activeModal === 'projects' && 'Projects & Workspaces'}
                {activeModal === 'history' && 'Activity & Chat History'}
                {activeModal === 'favorites' && 'Saved Favorites & Highlights'}
                {activeModal === 'settings' && 'Platform Settings & API Keys'}
              </h3>
              <p className="text-xs text-slate-400">
                {activeModal === 'projects' && 'Manage your video analysis and chat workspace collections'}
                {activeModal === 'history' && 'Review your previous prompts, transcripts, and model queries'}
                {activeModal === 'favorites' && 'Quick access to bookmarked key insights and code snippets'}
                {activeModal === 'settings' && 'Configure active AI models, credentials, and system options'}
              </p>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body Content */}
        <div className="p-6 flex-1 overflow-y-auto">
          
          {/* ── 1. PROJECTS MODAL ── */}
          {activeModal === 'projects' && (
            <div className="flex flex-col gap-5">
              {/* Create project input */}
              <div className="flex gap-2">
                <input 
                  type="text"
                  placeholder="Create new workspace project..."
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddProject()}
                  className="flex-1 bg-white/5 border border-white/10 text-xs py-2.5 px-3.5 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50"
                />
                <button 
                  onClick={handleAddProject}
                  disabled={!newProjectName.trim()}
                  className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-bold text-xs px-4 py-2.5 rounded-xl transition flex items-center gap-1.5 cursor-pointer shadow-md"
                >
                  <Plus className="w-4 h-4" />
                  New Project
                </button>
              </div>

              {/* Project list */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {projectsList.map((proj) => (
                  <div key={proj.id} className="glass-card p-4 rounded-2xl border border-white/5 flex flex-col justify-between hover:border-indigo-500/30 transition group">
                    <div>
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-300">
                          {proj.tag}
                        </span>
                        <span className="text-[10px] text-slate-500">{proj.date}</span>
                      </div>
                      <h4 className="font-bold text-sm text-slate-100 group-hover:text-indigo-300 transition-colors mb-1">
                        {proj.title}
                      </h4>
                      <p className="text-xs text-slate-400">{proj.type}</p>
                    </div>

                    <div className="flex justify-between items-center mt-4 pt-3 border-t border-white/5 text-[11px] text-slate-400">
                      <span>{proj.items} items saved</span>
                      <button 
                        onClick={onClose}
                        className="text-indigo-400 font-bold hover:underline flex items-center gap-1 cursor-pointer"
                      >
                        Open <ExternalLink className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── 2. HISTORY MODAL ── */}
          {activeModal === 'history' && (
            <div className="flex flex-col gap-4">
              <div className="flex gap-3 items-center justify-between">
                <div className="relative flex-1">
                  <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-3" />
                  <input 
                    type="text"
                    placeholder="Search history..."
                    value={historySearch}
                    onChange={(e) => setHistorySearch(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 text-xs py-2 pl-9 pr-3 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none"
                  />
                </div>
                
                {historyItems.length > 0 && (
                  <button 
                    onClick={handleClearHistory}
                    className="text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 border border-rose-500/20 px-3 py-2 rounded-xl transition flex items-center gap-1.5 cursor-pointer"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Clear History
                  </button>
                )}
              </div>

              <div className="flex flex-col gap-2.5 max-h-[380px] overflow-y-auto pr-1">
                {filteredHistory.map((item) => (
                  <div 
                    key={item.id}
                    className="glass-card p-3.5 rounded-2xl border border-white/5 flex items-center justify-between hover:bg-white/5 transition group"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0 pr-3">
                      <div className="p-2 rounded-xl bg-white/5 text-indigo-400 border border-white/5 flex-shrink-0">
                        {item.type === 'chat' ? <Sparkles className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-semibold text-slate-200 truncate group-hover:text-indigo-300 transition-colors">
                          {item.query}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-[10px] text-slate-500">{item.time}</span>
                          <span className="text-[10px] text-indigo-400/80 font-medium">· {item.model}</span>
                        </div>
                      </div>
                    </div>

                    <button 
                      onClick={() => {
                        if (onSelectHistoryPrompt && item.type === 'chat') {
                          onSelectHistoryPrompt(item.query)
                        }
                        onClose()
                      }}
                      className="text-[11px] font-bold text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 px-3 py-1.5 rounded-xl border border-indigo-500/20 transition cursor-pointer"
                    >
                      Reuse
                    </button>
                  </div>
                ))}

                {filteredHistory.length === 0 && (
                  <div className="text-center py-12 text-slate-500 text-xs">
                    No history logs found.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ── 3. FAVORITES MODAL ── */}
          {activeModal === 'favorites' && (
            <div className="flex flex-col gap-3 max-h-[380px] overflow-y-auto pr-1">
              {favoritesList.map((fav) => (
                <div key={fav.id} className="glass-card p-4 rounded-2xl border border-white/5 hover:border-amber-500/30 transition">
                  <div className="flex justify-between items-start mb-1.5">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400">
                      ⭐ {fav.category}
                    </span>
                    <button 
                      onClick={() => setFavoritesList(prev => prev.filter(f => f.id !== fav.id))}
                      className="text-slate-500 hover:text-rose-400 transition cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <h4 className="font-bold text-sm text-slate-100 mb-1">{fav.title}</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">{fav.desc}</p>
                </div>
              ))}

              {favoritesList.length === 0 && (
                <div className="text-center py-12 text-slate-500 text-xs">
                  No bookmarked items yet. Star any response or takeaway to save it here.
                </div>
              )}
            </div>
          )}

          {/* ── 4. SETTINGS MODAL ── */}
          {activeModal === 'settings' && (
            <div className="flex flex-col gap-5">
              {/* Settings Nav Tabs */}
              <div className="flex border-b border-white/10 gap-4">
                <button 
                  onClick={() => setActiveTabSetting('api')}
                  className={`text-xs font-bold pb-2 border-b-2 transition cursor-pointer flex items-center gap-1.5 ${
                    activeTabSetting === 'api' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <KeyRound className="w-3.5 h-3.5" /> API Keys & Credentials
                </button>
                <button 
                  onClick={() => setActiveTabSetting('model')}
                  className={`text-xs font-bold pb-2 border-b-2 transition cursor-pointer flex items-center gap-1.5 ${
                    activeTabSetting === 'model' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Cpu className="w-3.5 h-3.5" /> AI Model Selection
                </button>
                <button 
                  onClick={() => setActiveTabSetting('system')}
                  className={`text-xs font-bold pb-2 border-b-2 transition cursor-pointer flex items-center gap-1.5 ${
                    activeTabSetting === 'system' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Sparkles className="w-3.5 h-3.5" /> System Info
                </button>
              </div>

              {/* Sub tab: API Keys */}
              {activeTabSetting === 'api' && (
                <div className="flex flex-col gap-4">
                  {/* Google key box */}
                  <div className="glass-panel p-4 rounded-2xl border border-white/5 flex flex-col gap-2">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-xs text-white flex items-center gap-2">
                        🔵 Google Gemini API Key
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        googleKeyOk ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                        {googleKeyOk ? 'Active & Ready' : 'Key Missing'}
                      </span>
                    </div>
                    <input 
                      type="password"
                      placeholder="AQ.Ab8RN6J..."
                      value={customGoogleKey}
                      onChange={(e) => setCustomGoogleKey(e.target.value)}
                      className="bg-white/5 border border-white/10 text-xs py-2 px-3 rounded-xl text-slate-200 focus:outline-none placeholder-slate-600"
                    />
                  </div>

                  {/* Groq key box */}
                  <div className="glass-panel p-4 rounded-2xl border border-white/5 flex flex-col gap-2">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-xs text-white flex items-center gap-2">
                        🟣 Groq API Key
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        groqKeyOk ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                        {groqKeyOk ? 'Active & Ready' : 'Key Missing'}
                      </span>
                    </div>
                    <input 
                      type="password"
                      placeholder="gsk_6HE5Kmrv..."
                      value={customGroqKey}
                      onChange={(e) => setCustomGroqKey(e.target.value)}
                      className="bg-white/5 border border-white/10 text-xs py-2 px-3 rounded-xl text-slate-200 focus:outline-none placeholder-slate-600"
                    />
                  </div>

                  <button 
                    onClick={handleSaveKeys}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs py-2.5 rounded-xl transition flex items-center justify-center gap-2 cursor-pointer"
                  >
                    {keySavedMsg ? <Check className="w-4 h-4 text-emerald-300" /> : null}
                    {keySavedMsg ? 'Settings Saved!' : 'Save Credentials'}
                  </button>
                </div>
              )}

              {/* Sub tab: Model Selection */}
              {activeTabSetting === 'model' && (
                <div className="flex flex-col gap-3">
                  {[
                    { id: '✨ Google — Gemini 3.6 Flash', provider: 'Google', name: 'Gemini 3.6 Flash', desc: 'Fast, highly accurate multimodal AI for general chat and video analysis.' },
                    { id: '🧠 Groq — Qwen 3.6 27B', provider: 'Groq', name: 'Qwen 3.6 27B', desc: 'Ultra-low latency open weights model hosted on Groq LPU hardware.' }
                  ].map((m) => (
                    <div 
                      key={m.id}
                      onClick={() => setSelectedModel(m.id)}
                      className={`glass-card p-4 rounded-2xl border transition cursor-pointer flex justify-between items-center ${
                        selectedModel === m.id ? 'border-indigo-500 bg-indigo-500/10' : 'border-white/5 hover:border-white/20'
                      }`}
                    >
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-bold text-sm text-white">{m.name}</h4>
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-slate-300 font-semibold">{m.provider}</span>
                        </div>
                        <p className="text-xs text-slate-400">{m.desc}</p>
                      </div>
                      {selectedModel === m.id && (
                        <div className="w-6 h-6 rounded-full bg-indigo-500 text-white flex items-center justify-center flex-shrink-0">
                          <Check className="w-4 h-4" />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Sub tab: System Info */}
              {activeTabSetting === 'system' && (
                <div className="glass-panel p-4 rounded-2xl border border-white/5 flex flex-col gap-3 text-xs text-slate-300">
                  <div className="flex justify-between py-1.5 border-b border-white/5">
                    <span className="text-slate-400">Backend Server:</span>
                    <span className="font-bold text-emerald-400">FastAPI (Python 3.11) — Online</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-white/5">
                    <span className="text-slate-400">Frontend Stack:</span>
                    <span className="font-bold text-indigo-400">Vite 8 + React 19 + Tailwind v4</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-white/5">
                    <span className="text-slate-400">Local Port:</span>
                    <span className="font-mono text-slate-200">http://localhost:8000</span>
                  </div>
                  <div className="flex justify-between py-1.5">
                    <span className="text-slate-400">Environment OS:</span>
                    <span className="font-semibold text-slate-200">Windows x64</span>
                  </div>
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
