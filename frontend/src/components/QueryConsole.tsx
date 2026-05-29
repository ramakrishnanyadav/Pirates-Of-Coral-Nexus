import { useState, useEffect } from "react";
import { useStreaming } from "../hooks/useStreaming";
import { SQLInspector } from "./SQLInspector";
import { ResultsPanel } from "./ResultsPanel";
import { Send, Loader2 } from "lucide-react";

interface StreamEvent {
  type: "thinking" | "sql_generated" | "query_executing" | 
        "results_received" | "reasoning" | "answer" | "done" | "error";
  content?: string;
  sql?: string;
  source_count?: number;
  row_count?: number;
  data?: any[];
  structured?: any;
  message?: string;
}

export function QueryConsole({ initialPlaybook }: { initialPlaybook?: string | null }) {
  const [question, setQuestion] = useState("");
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentSQL, setCurrentSQL] = useState("");
  const [sourcesActive, setSourcesActive] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<{rows?: number, time?: number, count?: number}>({});
  const { stream } = useStreaming();
  
  useEffect(() => {
    if (initialPlaybook) {
      setQuestion(`Run playbook: ${initialPlaybook}`);
    }
  }, [initialPlaybook]);

  const handleQuery = async () => {
    if (!question.trim() || isRunning) return;
    setEvents([]);
    setCurrentSQL("");
    setSourcesActive([]);
    setIsRunning(true);
    
    // Use environment variable for API URL or fallback to localhost
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    await stream(`${apiUrl}/api/query`, { question }, (event: StreamEvent) => {
      setEvents(prev => [...prev, event]);
      
      if (event.type === "sql_generated") {
        setCurrentSQL(event.sql || "");
        const sources = extractSources(event.sql || "");
        setSourcesActive(sources);
      }
      
      if (event.type === "results_received") {
        // @ts-ignore - execution_time comes from backend
        setMetrics({ rows: event.row_count, time: event.execution_time, count: sourcesActive.length || extractSources(currentSQL).length });
      }
      
      if (event.type === "done" || event.type === "error") setIsRunning(false);
    });
  };
  
  return (
    <div className="flex flex-col h-full gap-6 max-h-full">
      {/* Input Area */}
      <div className="relative group cyber-border rounded-2xl">
        <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-2xl blur-lg opacity-50 group-hover:opacity-100 transition duration-500" />
        <div className="relative flex gap-2 p-2 bg-[#0c0c0f]/80 backdrop-blur-2xl border border-white/5 rounded-2xl shadow-[0_10px_40px_-10px_rgba(0,0,0,0.8)] focus-within:bg-[#0c0c0f]/95 transition-all">
          <input
            className="flex-1 bg-transparent px-5 py-4 text-white placeholder-gray-500 text-lg focus:outline-none tracking-wide"
            placeholder="Ask anything about your engineering stack... e.g. 'Why did prod break at 2am?'"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleQuery()}
            disabled={isRunning}
          />
          <button
            onClick={handleQuery}
            disabled={isRunning || !question.trim()}
            className="px-8 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:from-gray-800 disabled:to-gray-800 disabled:text-gray-500
                       text-white rounded-xl font-bold tracking-widest uppercase text-[11px] transition-all shadow-[0_0_20px_rgba(8,145,178,0.3)] disabled:shadow-none flex items-center gap-3 relative overflow-hidden group/btn"
          >
            {isRunning && <div className="absolute inset-0 w-full h-full bg-white/10 animate-[slide-up-fade_1s_ease-in-out_infinite]" />}
            {isRunning ? <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin relative z-10" /> : <Send size={16} className="relative z-10 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />}
            <span className="relative z-10">{isRunning ? "PROCESSING" : "EXECUTE"}</span>
          </button>
        </div>
      </div>
      
      {/* Source activity indicators & Metrics */}
      <div className="flex-none h-6 flex justify-between items-center px-1">
        <div>
          {sourcesActive.length > 0 && (
            <SourceIndicators sources={sourcesActive} isActive={isRunning} />
          )}
        </div>
        
        {/* Query Metrics */}
        {metrics.time !== undefined && !isRunning && (
          <div className="flex gap-4 text-[11px] font-mono text-gray-500 bg-surface px-3 py-1 rounded-full border border-border">
            <span><span className="text-cyan-500 font-bold">{metrics.count || sourcesActive.length}</span> sources joined</span>
            <span><span className="text-emerald-500 font-bold">{metrics.rows}</span> correlated rows</span>
            <span><span className="text-purple-500 font-bold">{metrics.time}s</span> execution</span>
          </div>
        )}
      </div>
      
      <div className="flex-1 overflow-hidden grid grid-cols-1 lg:grid-cols-2 gap-6 mt-2 min-h-0">
        {/* Left Side - Code & Process */}
        <div className="flex flex-col gap-4 overflow-hidden rounded-xl min-w-0">
            {currentSQL && (
            <SQLInspector sql={currentSQL} isExecuting={isRunning} />
            )}
        </div>
        
        {/* Right Side - Intelligence Results */}
        <div className="flex flex-col overflow-hidden glass-panel rounded-xl min-w-0">
            <ResultsPanel events={events} isRunning={isRunning} />
        </div>
      </div>
    </div>
  );
}

function extractSources(sql: string): string[] {
    const available = ["github", "sentry", "slack", "linear", "datadog", "pagerduty"];
    return available.filter(s => sql.toLowerCase().includes(s + "."));
}

function SourceIndicators({ sources, isActive }: { sources: string[], isActive: boolean }) {
  const sourceColors: Record<string, string> = {
    github: "bg-gray-600 shadow-[0_0_10px_rgba(75,85,99,0.5)]",
    sentry: "bg-purple-600 shadow-[0_0_10px_rgba(147,51,234,0.5)]",
    slack: "bg-emerald-600 shadow-[0_0_10px_rgba(5,150,105,0.5)]", 
    linear: "bg-blue-600 shadow-[0_0_10px_rgba(37,99,235,0.5)]",
    datadog: "bg-orange-600 shadow-[0_0_10px_rgba(234,88,12,0.5)]",
    pagerduty: "bg-red-600 shadow-[0_0_10px_rgba(220,38,38,0.5)]"
  };
  
  return (
    <div className="flex gap-2 items-center">
      <span className="text-gray-500 text-xs font-mono tracking-widest uppercase flex items-center gap-2">
        {isActive && <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span>}
        Coral Orchestrator:
      </span>
      <div className="flex gap-2">
        {sources.map((source, index) => (
            <span
            key={source}
            // Stagger the animation delay based on index for cinematic effect
            style={{ animationDelay: `${index * 150}ms` }}
            className={`px-2 py-0.5 rounded text-[10px] font-mono text-white uppercase tracking-wider transition-all duration-300
                        ${sourceColors[source] || "bg-gray-600"}
                        ${isActive ? "animate-pulse opacity-100 scale-105" : "opacity-70 scale-100"}`}
            >
            ✓ {source}
            </span>
        ))}
      </div>
    </div>
  );
}
