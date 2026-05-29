from .client import CoralClient

class SchemaLoader:
    """
    Loads schema dynamically from Coral to inject into the LLM prompt.
    """
    def __init__(self):
        self.coral = CoralClient()
        
    async def get_relevant_schema(self, question: str) -> str:
        """
        In a production system, this would do semantic search over the schema.
        For this prototype, we return the core tables to guide the LLM.
        """
        tables = self.coral.get_tables()
        schema_str = "AVAILABLE TABLES:\n"
        
        # Group by schema_name
        schemas = {}
        for row in tables:
            s_name = row.get("schema_name")
            t_name = row.get("table_name")
            desc = row.get("description", "")
            if s_name not in schemas:
                schemas[s_name] = []
            schemas[s_name].append(f"- {s_name}.{t_name}: {desc}")
            
        for s_name, t_list in schemas.items():
            schema_str += f"[{s_name}]\n" + "\n".join(t_list) + "\n\n"
            
        return schema_str
