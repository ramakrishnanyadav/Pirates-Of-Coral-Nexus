import { useState, useEffect } from 'react';

export function SchemaExplorer() {
  const [schema, setSchema] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/schema')
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
    <div>
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Live Catalog</h3>
      <div className="space-y-4">
        {Object.entries(grouped).map(([schemaName, tables]) => (
          <div key={schemaName}>
            <div className="text-xs font-mono text-cyan-500 mb-1 flex items-center gap-1">
              {schemaName} <span className="text-gray-600">({tables.length})</span>
            </div>
            <div className="space-y-0.5 pl-2 border-l border-border">
              {tables.map(t => (
                <div key={t.table_name} className="text-[11px] text-gray-400 font-mono truncate" title={t.description}>
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
