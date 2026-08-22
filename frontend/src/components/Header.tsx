import React from 'react'
import { Bell, Search, Settings, HelpCircle, KeyRound } from 'lucide-react'

interface HeaderProps {
  activeTab: 'chat' | 'video'
  googleKeyOk: boolean
  groqKeyOk: boolean
}

export default function Header({ activeTab, googleKeyOk, groqKeyOk }: HeaderProps) {
  return (
    <header className="glass-panel border-b border-white/5 h-16 px-6 flex items-center justify-between z-20 sticky top-0 backdrop-blur-md">
      {/* Mode / Breadcrumb */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-semibold text-slate-400">Workspace</span>
        <span className="text-sm font-semibold text-slate-500">/</span>
        <span className="text-sm font-bold text-white tracking-wide">
          {activeTab === 'chat' ? '💬 Chat AI' : '🎥 Video AI Analysis Studio'}
        </span>
      </div>

      {/* Action Strip */}
      <div className="flex items-center gap-5">
        {/* API Key Status Pill Container */}
        <div className="hidden md:flex items-center gap-3 bg-white/5 border border-white/10 px-3.5 py-1.5 rounded-full text-xs">
          <div className="flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${googleKeyOk ? 'bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.5)]' : 'bg-rose-500 shadow-[0_0_6px_rgba(244,63,94,0.5)]'}`} />
            <span className="text-slate-400 font-medium">Gemini API</span>
          </div>
          <div className="w-[1px] h-3 bg-white/15" />
          <div className="flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${groqKeyOk ? 'bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.5)]' : 'bg-rose-500 shadow-[0_0_6px_rgba(244,63,94,0.5)]'}`} />
            <span className="text-slate-400 font-medium">Groq API</span>
          </div>
        </div>

        {/* Search Input Box */}
        <div className="relative hidden lg:block w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input 
            type="text" 
            placeholder="Search dashboard..."
            className="w-full bg-white/5 hover:bg-white/8 focus:bg-white/10 border border-white/5 focus:border-white/10 text-xs py-2 pl-9 pr-4 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none transition-all duration-200"
          />
        </div>

        {/* Shortcut Buttons */}
        <div className="flex items-center gap-2">
          <button className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-xl transition cursor-pointer">
            <Bell className="w-4 h-4" />
          </button>
          <button className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-xl transition cursor-pointer">
            <HelpCircle className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  )
}
