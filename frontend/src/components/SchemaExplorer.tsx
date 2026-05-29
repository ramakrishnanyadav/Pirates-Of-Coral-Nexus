import { useState, useEffect } from 'react';

export function SchemaExplorer() {
  const [schema, setSchema] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    fetch(`${apiUrl}/api/schema`)
      .then(res => res.json())
      .then(data => {
        setSchema(data.tables || []);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="text-xs text-gray-500">Loading catalog...</div>;

  // Group by schema
  const grouped = schema.reduce((acc, row) => {
    if (!acc[row.schema_name]) acc[row.schema_name] = [];
    acc[row.schema_name].push(row);
    return acc;
  }, {} as Record<string, any[]>);

  return (
    <div className="mt-8">
      <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
        <span className="w-4 h-[1px] bg-gray-600"></span>
        Live Catalog
      </h3>
      <div className="space-y-4">
        {(Object.entries(grouped) as any[]).map(([schemaName, tables]: any) => (
          <div key={schemaName} className="group">
            <div className="text-[11px] font-mono text-cyan-500 mb-1.5 flex items-center gap-2 group-hover:text-cyan-400 transition-colors">
              <span className="text-gray-600">[{tables.length}]</span> {schemaName}
            </div>
            <div className="space-y-1 pl-2 border-l-2 border-white/5 group-hover:border-white/10 transition-colors">
              {tables.map((t: any) => (
                <div key={t.table_name} className="text-[10px] text-gray-400 font-mono truncate hover:text-white cursor-help" title={t.description}>
                  {t.table_name}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
