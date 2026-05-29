import { useState, useEffect } from 'react';
import { Database, Zap, FileTerminal } from 'lucide-react';

export function SQLInspector({ sql, isExecuting }: { sql: string, isExecuting: boolean }) {
  const [displayedSql, setDisplayedSql] = useState('');
  
  // Typing effect for the SQL
  useEffect(() => {
    if (!sql) {
      setDisplayedSql('');
      return;
    }
    
    // If not executing (just displaying history), show instantly
    if (!isExecuting) {
      setDisplayedSql(sql);
      return;
    }

    setDisplayedSql('');
    let i = 0;
    const intervalId = setInterval(() => {
      setDisplayedSql(sql.substring(0, i));
      i += 5; // Type 5 chars at a time for speed
      if (i > sql.length) {
        clearInterval(intervalId);
        setDisplayedSql(sql);
      }
    }, 10);
    
    return () => clearInterval(intervalId);
  }, [sql, isExecuting]);

  return (
    <div className="flex flex-col h-full bg-[#1e1e1e] border border-border rounded-xl overflow-hidden shadow-2xl relative group">
      {/* Scanline effect */}
      {isExecuting && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-xl z-10">
          <div className="w-full h-8 bg-cyan-500/10 blur-sm animate-[scan_2s_ease-in-out_infinite]" />
        </div>
      )}
      <div className="px-4 py-3 border-b border-[#333] bg-[#252526] flex items-center justify-between z-20 relative">
        <div className="flex items-center gap-2 text-xs font-mono text-gray-400">
          <FileTerminal size={14} className="text-cyan-500" />
          <span className="tracking-widest uppercase">Coral Execution Engine</span>
        </div>
        {isExecuting && (
          <div className="flex items-center gap-2 px-2 py-1 bg-cyan-500/10 rounded border border-cyan-500/20 text-[10px] font-mono text-cyan-400">
            <Zap size={12} className="animate-pulse" />
            <span className="animate-pulse">EXECUTING CROSS-SOURCE JOIN</span>
          </div>
        )}
      </div>
      
      <div className="p-5 flex-1 overflow-auto bg-[#1e1e1e] relative z-0">
        <pre className="text-[13px] leading-relaxed font-mono text-[#d4d4d4]">
          <code dangerouslySetInnerHTML={{ __html: highlightSQL(displayedSql) + (isExecuting && displayedSql.length < sql.length ? '<span class="animate-pulse bg-cyan-500 w-2 h-4 inline-block ml-1 align-middle"></span>' : '') }} />
        </pre>
      </div>
      
      {/* Decorative gradient when running */}
      {isExecuting && (
        <div className="absolute bottom-0 left-0 h-1 w-full overflow-hidden bg-[#333]">
          <div className="h-full bg-gradient-to-r from-transparent via-cyan-500 to-transparent w-1/2 animate-[slide_1.5s_linear_infinite]" />
        </div>
      )}
    </div>
  );
}

// Very basic syntax highlighting for demo purposes
function highlightSQL(sql: string) {
  const keywords = ['SELECT', 'FROM', 'JOIN', 'LEFT JOIN', 'INNER JOIN', 'WHERE', 'AND', 'OR', 'ORDER BY', 'LIMIT', 'ON', 'AS', 'ILIKE', 'DESC', 'ASC', 'INTERVAL'];
  
  let highlighted = sql
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
    
  keywords.forEach(kw => {
    const regex = new RegExp(`\\b${kw}\\b`, 'g');
    highlighted = highlighted.replace(regex, `<span style="color: #569CD6">${kw}</span>`);
  });
  
  // Highlight table names (e.g., github.commits)
  highlighted = highlighted.replace(/\b([a-z_]+\.[a-z_]+)\b/g, '<span style="color: #4EC9B0">$1</span>');
  
  return highlighted;
}
