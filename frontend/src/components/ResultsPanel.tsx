import { useEffect, useRef } from "react";
import { CheckCircle2, ChevronRight } from "lucide-react";

export function ResultsPanel({ events, isRunning }: { events: any[], isRunning: boolean }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  const reasoningEvents = events.filter(e => e.type === "reasoning");
  const answerEvent = events.find(e => e.type === "answer");

  
  // Determine severity based on content
  const fullText = answerEvent ? JSON.stringify(answerEvent.structured) : "";
  const isCritical = fullText.toLowerCase().includes("rollback") || fullText.toLowerCase().includes("spike") || fullText.toLowerCase().includes("500s");
  const isWarning = fullText.toLowerCase().includes("warning") || fullText.toLowerCase().includes("elevated");
  const severityColor = isCritical ? "bg-red-500" : isWarning ? "bg-orange-500" : "bg-cyan-500";
  const severityText = isCritical ? "CRITICAL INCIDENT" : isWarning ? "WARNING" : "INVESTIGATION";

  return (
    <div className="flex flex-col h-full bg-transparent relative">
      {/* Severity Indicator Top Bar */}
      {answerEvent && (
        <div className={`absolute top-0 left-0 w-full h-1 ${severityColor} shadow-[0_0_15px_rgba(239,68,68,0.5)] z-10 transition-colors duration-1000`} />
      )}
      
      <div className="px-5 py-4 border-b border-white/5 bg-transparent flex items-center justify-between">
        <h3 className="font-bold text-sm tracking-widest uppercase text-transparent bg-clip-text bg-gradient-to-r from-gray-200 to-gray-400 flex items-center gap-2">
          {answerEvent && <span className={`w-2 h-2 rounded-full ${severityColor} animate-pulse`}></span>}
          Intelligence Briefing
        </h3>
        {answerEvent && (
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${isCritical ? 'bg-red-500/20 text-red-400 border border-red-500/50' : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'}`}>
            {severityText}
          </span>
        )}
      </div>
      
      <div ref={scrollRef} className="flex-1 overflow-auto p-6 space-y-6">
        
        {events.length === 0 && !isRunning && (
          <div className="h-full flex flex-col items-center justify-center text-gray-500">
            <div className="w-12 h-12 rounded-full border border-gray-700 flex items-center justify-center mb-4">
              <span className="font-serif italic text-xl">N</span>
            </div>
            <p className="text-sm">Ready to analyze system events.</p>
          </div>
        )}

        {events.map((event, i) => (
          <StatusEvent key={i} event={event} />
        ))}

        {reasoningEvents.length > 0 && !answerEvent && (
          <div className="prose prose-invert prose-sm max-w-none">
            <span className="text-gray-300">
              {reasoningEvents.map(e => e.content).join("")}
            </span>
            <span className="inline-block w-2 h-4 ml-1 bg-cyan-500 animate-pulse align-middle" />
          </div>
        )}

        {answerEvent && answerEvent.structured && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-700 delay-150 fill-mode-both">
            <Section title="Root Cause" content={answerEvent.structured.root_cause} icon="🔴" />
            <EvidenceCards content={answerEvent.structured.evidence} />
            {answerEvent.structured.timeline && (
              <TimelineSection content={answerEvent.structured.timeline} />
            )}
            <Section title="Recommended Actions" content={answerEvent.structured.recommended_actions} icon="✅" />
          </div>
        )}
      </div>
    </div>
  );
}

function StatusEvent({ event }: { event: any }) {
  if (["reasoning", "answer", "done"].includes(event.type)) return null;
  
  let text = "";
  let success = false;
  
  if (event.type === "thinking") text = event.content;
  if (event.type === "sql_generated") {
    text = "Generated unified SQL query";
    success = true;
  }
  if (event.type === "query_executing") text = `Executing JOIN across ${event.source_count} sources...`;
  if (event.type === "results_received") {
    text = `Received ${event.row_count} correlated records`;
    success = true;
  }
  if (event.type === "error") text = `Error: ${event.message}`;
  
  if (!text) return null;
  
  return (
    <div className="flex items-center gap-3 text-xs font-mono animate-in fade-in slide-in-from-left-2 duration-300">
      {success ? (
        <CheckCircle2 size={14} className="text-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] rounded-full" />
      ) : event.type === "error" ? (
        <span className="text-red-500">✗</span>
      ) : (
        <ChevronRight size={14} className="text-cyan-500 animate-pulse shadow-[0_0_8px_rgba(6,182,212,0.5)] rounded-full" />
      )}
      <span className={event.type === "error" ? "text-red-400" : "text-gray-300 tracking-wide"}>{text}</span>
    </div>
  );
}

function Section({ title, content, icon }: { title: string, content: string, icon: string }) {
  if (!content) return null;
  return (
    <div className="glass-card rounded-xl p-5 shadow-lg relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-1 h-full bg-cyan-600/50 group-hover:bg-cyan-500 transition-colors"></div>
      <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
        <span>{icon}</span> {title}
      </h4>
      <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap font-medium">
        {content}
      </div>
    </div>
  );
}

function EvidenceCards({ content }: { content: string }) {
  if (!content) return null;
  
  return (
    <div className="glass-card rounded-xl p-5 shadow-lg relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-1 h-full bg-blue-600/50 group-hover:bg-blue-500 transition-colors"></div>
      <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
        <span>📊</span> Tangible Evidence
      </h4>
      <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap font-medium">
        {content}
      </div>
    </div>
  );
}

function TimelineSection({ content }: { content: string }) {
  if (!content) return null;
  
  return (
    <div className="glass-card rounded-xl p-5 shadow-lg relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-1 h-full bg-purple-600/50 group-hover:bg-purple-500 transition-colors"></div>
      <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
        <span>⏱️</span> Incident Timeline
      </h4>
      <div className="relative pl-4 border-l-2 border-white/10 space-y-4">
        {content.split('\n').filter(l => l.trim()).map((line, i) => (
          <div key={i} className="relative">
            <div className="absolute -left-[21px] top-1.5 w-2 h-2 rounded-full bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.8)]"></div>
            <div className="text-sm text-gray-300 leading-relaxed pl-2 font-mono">
              {line.replace(/^-\s*/, '')}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
