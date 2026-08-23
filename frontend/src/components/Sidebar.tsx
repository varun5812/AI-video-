import React from 'react'
import { 
  MessageSquare, 
  Video, 
  FolderGit2, 
  History, 
  Star, 
  Settings, 
  ChevronLeft, 
  ChevronRight
} from 'lucide-react'

interface SidebarProps {
  collapsed: boolean
  setCollapsed: (collapsed: boolean) => void
  activeTab: 'chat' | 'video'
  setActiveTab: (tab: 'chat' | 'video') => void
  onOpenModal: (modal: 'projects' | 'history' | 'favorites' | 'settings') => void
}

export default function Sidebar({ collapsed, setCollapsed, activeTab, setActiveTab, onOpenModal }: SidebarProps) {
  const mainNav = [
    { id: 'chat', label: 'Chat AI', icon: MessageSquare },
    { id: 'video', label: 'Video AI', icon: Video },
  ]

  const secondaryNav = [
    { id: 'projects', label: 'Projects', icon: FolderGit2 },
    { id: 'history', label: 'History', icon: History },
    { id: 'favorites', label: 'Favorites', icon: Star },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

  return (
    <aside 
      className={`glass-panel min-h-screen relative flex flex-col transition-all duration-300 z-30 select-none ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="flex items-center gap-3 p-4 border-b border-white/5">
        <div className="bg-indigo-500/10 text-indigo-400 p-2 rounded-xl flex items-center justify-center font-bold text-lg aspect-square">
          🎬
        </div>
        {!collapsed && (
          <div className="flex flex-col">
            <span className="font-extrabold text-sm tracking-tight text-white">VideoAI</span>
            <span className="text-[10px] text-indigo-400 font-semibold tracking-wider uppercase">Workspace</span>
          </div>
        )}
      </div>

      {/* Nav Section */}
      <div className="flex-1 flex flex-col gap-6 py-6 px-3">
        {/* Main Workspaces */}
        <div className="flex flex-col gap-1">
          {!collapsed && (
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider px-2 mb-2">
              Workspaces
            </span>
          )}
          {mainNav.map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as 'chat' | 'video')}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group text-left cursor-pointer ${
                  isActive 
                    ? 'bg-indigo-500/15 text-indigo-400 border-l-2 border-indigo-400' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-300'}`} />
                {!collapsed && (
                  <span className="font-semibold text-sm tracking-wide">
                    {item.label}
                  </span>
                )}
              </button>
            )
          })}
        </div>

        {/* Secondary Navigation (Projects, History, Favorites, Settings) */}
        <div className="flex flex-col gap-1">
          {!collapsed && (
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider px-2 mb-2">
              Platform
            </span>
          )}
          {secondaryNav.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                onClick={() => onOpenModal(item.id as 'projects' | 'history' | 'favorites' | 'settings')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-all duration-200 text-left group cursor-pointer"
              >
                <Icon className="w-5 h-5 flex-shrink-0 text-slate-400 group-hover:text-slate-300" />
                {!collapsed && (
                  <span className="font-medium text-sm tracking-wide">
                    {item.label}
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Collapse Toggle Trigger */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute top-16 -right-3 bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 w-6 h-6 rounded-full flex items-center justify-center cursor-pointer transition-all z-40"
      >
        {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
      </button>

      {/* User Profile Footer */}
      <div 
        onClick={() => onOpenModal('settings')}
        className="p-4 border-t border-white/5 flex items-center gap-3 cursor-pointer hover:bg-white/5 transition"
      >
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-500 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
          U
        </div>
        {!collapsed && (
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-white truncate">User Account</p>
            <p className="text-[10px] text-slate-400 truncate">Settings & Profile</p>
          </div>
        )}
      </div>
    </aside>
  )
}
