import { useState } from 'react'
import { QueryConsole } from './components/QueryConsole'
import { SchemaExplorer } from './components/SchemaExplorer'
import { Activity, ShieldAlert, Zap, LayoutDashboard, Terminal } from 'lucide-react'

function App() {
  const [activePlaybook, setActivePlaybook] = useState<string | null>(null)

  return (
    <div className="flex h-screen w-full overflow-hidden selection:bg-cyan-500/30 font-sans">
      
      {/* Ambient background glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-600/10 blur-[120px] pointer-events-none" />

      {/* Left Sidebar */}
      <div className="w-72 flex flex-col glass-panel border-r-0 border-r-white/5 z-10 relative shadow-2xl">
        <div className="p-6 border-b border-white/5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white shadow-[0_0_20px_rgba(8,145,178,0.4)]">
            <Activity size={22} className="animate-pulse-slow" />
          </div>
          <div>
            <div className="font-bold tracking-widest text-sm uppercase text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">NEXUS</div>
            <div className="text-[10px] text-cyan-500 tracking-widest uppercase font-mono mt-0.5">War Room Engine</div>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto pt-6">
          <div className="px-6 mb-8">
            <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <span className="w-4 h-[1px] bg-gray-600"></span>
              Playbooks
            </h3>
            <div className="space-y-1">
              <PlaybookItem icon={<ShieldAlert size={14}/>} title="Incident Autopsy" onClick={() => setActivePlaybook("incident_autopsy")} />
              <PlaybookItem icon={<LayoutDashboard size={14}/>} title="Sprint Health" onClick={() => setActivePlaybook("sprint_health")} />
              <PlaybookItem icon={<Zap size={14}/>} title="Security Radar" onClick={() => setActivePlaybook("security_radar")} />
              <PlaybookItem icon={<Terminal size={14}/>} title="On-Call Briefing" onClick={() => setActivePlaybook("oncall_briefing")} />
            </div>
          </div>
          
          <div className="px-6 pb-6">
            <SchemaExplorer />
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative h-full z-0">
        {/* Header pattern */}
        <div className="absolute top-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-30 shadow-[0_0_10px_rgba(6,182,212,0.8)]"></div>
        
        <div className="flex-1 overflow-hidden p-8">
          <div className="max-w-[1400px] mx-auto h-full flex flex-col">
            <QueryConsole initialPlaybook={activePlaybook} />
          </div>
        </div>
      </div>
    </div>
  )
}

function PlaybookItem({ icon, title, onClick }: { icon: React.ReactNode, title: string, onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium text-gray-400 hover:text-white hover:bg-white/5 border border-transparent hover:border-white/10 transition-all text-left group"
    >
      <span className="text-gray-500 group-hover:text-cyan-400 transition-colors">{icon}</span>
      <span className="tracking-wide">{title}</span>
    </button>
  )
}

export default App
