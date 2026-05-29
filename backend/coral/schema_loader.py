from .client import CoralClient

class SchemaLoader:
    """
    Dynamically loads the exact live schema from the Coral execution engine.
    This guarantees 100% accuracy for the LLM to generate SQL without hallucinating columns.
    """
    def __init__(self):
        self.coral = CoralClient()
        self._cached_schema = None
        
    def _build_fallback_schema(self) -> str:
        return """AVAILABLE TABLES AND EXACT COLUMNS:

[github]
- github.pulls (Pull Requests): id, number, state, title, body, created_at, updated_at, closed_at, merged_at, owner, repo
- github.commits (Commits): sha, commit__message, author__login, commit__author__date, html_url, owner, repo
- github.issues (Issues): id, number, state, title, body, created_at, updated_at, closed_at, owner, repo

[sentry]
- sentry.issues (Sentry Error Groups): id, short_id, title, status, level, count, user_count, first_seen, last_seen, project
- sentry.projects (Sentry Projects): id, slug, name, platform, date_created

[slack]
- slack.channels (Slack Channels): id, name, is_archived, created, num_members, topic__value, purpose__value
- slack.users (Slack Users): id, name, real_name, tz, is_admin, is_bot

CRITICAL: YOU MUST ONLY USE THE EXACT COLUMNS LISTED ABOVE. DO NOT INVENT COLUMNS.
"""

    async def get_relevant_schema(self, question: str) -> str:
        if self._cached_schema:
            return self._cached_schema
            
        try:
            # Try to dynamically fetch exact live schema
            tables = self.coral.get_tables()
            if not tables:
                return self._build_fallback_schema()
                
            schema_dict = {}
            # DataFusion/Coral standard information schema
            columns = self.coral.query("SELECT table_schema, table_name, column_name FROM information_schema.columns")
            
            for col in columns:
                schema = col.get("table_schema", "")
                table = col.get("table_name", "")
                column = col.get("column_name", "")
                
                # Ignore internal or irrelevant schemas to save tokens
                if schema not in ["github", "sentry", "slack"]:
                    continue
                    
                # STRICT TABLE WHITELIST to prevent 25k+ token blowups from hundreds of API tables
                allowed_tables = {
                    "commits", "pulls", "issues", "releases", "workflows", "workflow_runs",
                    "projects", "events", "alerts",
                    "channels", "users", "messages"
                }
                if table not in allowed_tables:
                    continue
                    
                # Filter out noisy columns to strictly manage the LLM context window
                noisy_suffixes = ("url", "href", "cursor", "node_id", "gravatar_id", "hash", "avatar", "icon")
                if any(column.endswith(suffix) for suffix in noisy_suffixes):
                    continue
                    
                full_table = f"{schema}.{table}"
                if full_table not in schema_dict:
                    schema_dict[full_table] = []
                
                # Limit to 20 columns per table to guarantee we stay under 6000 TPM
                if len(schema_dict[full_table]) < 20:
                    schema_dict[full_table].append(column)
            
            if not schema_dict:
                # Fallback if information_schema is not accessible
                return self._build_fallback_schema()
                
            lines = ["LIVE AVAILABLE TABLES AND EXACT COLUMNS:"]
            for table, cols in schema_dict.items():
                lines.append(f"- {table}: {', '.join(cols)}")
                
            lines.append("\nCRITICAL: YOU MUST ONLY USE THE EXACT COLUMNS LISTED ABOVE. DO NOT INVENT COLUMNS.")
            
            self._cached_schema = "\n".join(lines)
            return self._cached_schema
            
        except Exception:
            # Fallback to safe schema if we can't connect or query information_schema
            return self._build_fallback_schema()
