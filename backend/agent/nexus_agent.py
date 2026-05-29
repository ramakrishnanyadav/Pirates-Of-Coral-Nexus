import os
import json
import re
import time
from typing import AsyncIterator
from openai import AsyncOpenAI
from coral.client import CoralClient
from coral.schema_loader import SchemaLoader

class NexusAgent:
    """
    The core NEXUS agent. Takes a natural language question,
    generates Coral SQL, executes it, and reasons over results.
    Uses Grok API (via openai package structure).
    """
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "dummy_key")
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.coral = CoralClient()
        self.schema = SchemaLoader()
    
    async def investigate(self, question: str, context: dict) -> AsyncIterator[dict]:
        # Step 1: Load live Coral schema
        schema_context = await self.schema.get_relevant_schema(question)
        
        # Step 2: Generate SQL from natural language
        yield {"type": "thinking", "content": "Analyzing question and available data sources..."}
        sql = await self._generate_sql(question, schema_context, context)
        yield {"type": "sql_generated", "sql": sql}
        
        # Step 3: Execute against Coral with Auto-Correction
        max_retries = 3
        results = None
        error_msg = None
        
        for attempt in range(max_retries):
            yield {"type": "query_executing", "source_count": self._count_sources(sql)}
            try:
                start_time = time.time()
                results = self.coral.query(sql)
                exec_time = round(time.time() - start_time, 2)
                # Guarantee at least some minimal visual delay for cinematic effect
                if exec_time < 0.5:
                    await __import__("asyncio").sleep(0.5 - exec_time)
                    exec_time = 0.5
                
                yield {
                    "type": "results_received", 
                    "row_count": len(results), 
                    "execution_time": exec_time,
                    "data": results
                }
                break
            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    yield {"type": "thinking", "content": f"Database error detected. Self-correcting query... (Attempt {attempt+1}/{max_retries})"}
                    sql = await self._fix_sql(sql, error_msg, schema_context, context)
                    yield {"type": "sql_generated", "sql": sql}
        
        if results is None:
            yield {"type": "error", "message": f"Query failed after {max_retries} attempts: {error_msg}"}
            return
            
        # Step 4: Reason over results (streaming)
        async for event in self._reason_over_results(question, sql, results):
            yield event
            
        yield {"type": "done"}
        
    def _count_sources(self, sql: str) -> int:
        sources = ["github", "sentry", "slack", "linear", "datadog", "pagerduty"]
        count = 0
        for s in sources:
            if s + "." in sql.lower():
                count += 1
        return max(1, count)

    async def _generate_sql(self, question: str, schema: str, context: dict) -> str:
        response = await self.client.chat.completions.create(
            model="llama-3.1-8b-instant", # Switched to 8b to bypass the exhausted 100k TPD limit on 70B
            messages=[
                {"role": "system", "content": self._sql_system_prompt(schema)},
                {"role": "user", "content": f"Question: {question}\nContext: {json.dumps(context)}"}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content
        return self._extract_sql(content)
        
    async def _fix_sql(self, bad_sql: str, error_msg: str, schema: str, context: dict) -> str:
        prompt = f"""You are a Coral SQL expert fixing a failed query.
AVAILABLE SCHEMA:
{schema}

FAILED QUERY:
```sql
{bad_sql}
```

ERROR RETURNED BY DATABASE:
{error_msg}

INSTRUCTIONS:
1. Fix the SQL query to resolve the exact error reported by the database.
2. Ensure you ONLY use the exact columns listed in the error message or schema. DO NOT invent columns.
3. Return ONLY the fixed SQL query, no explanation, no markdown fences.
"""
        response = await self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content
        return self._extract_sql(content)

    def _extract_sql(self, text: str) -> str:
        # Try to find SQL in markdown blocks
        match = re.search(r"```sql(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return text.strip()

    def _sql_system_prompt(self, schema: str) -> str:
        return f"""You are a Coral SQL expert. Coral provides a unified SQL interface over multiple data sources.

AVAILABLE SCHEMA:
{schema}

RULES:
1. Always use cross-source JOINs when the question touches multiple tools
2. Use LEFT JOIN for optional data, INNER JOIN for required correlation
3. Coral uses standard SQL with these source.table notation: github.issues, sentry.events, slack.messages, etc.
4. Always add LIMIT clauses (default: 25 rows)
5. Use ILIKE for fuzzy text matching
6. Time filtering: use NOW() - INTERVAL '7 days' syntax
7. Return ONLY the SQL query, no explanation, no markdown fences
8. CRITICAL API LIMITATION: When querying ANY `github.*` table (like github.workflows, github.issues, github.commits), you MUST include a hardcoded filter for BOTH the `owner` and `repo`. For this demo, always use `owner = 'withcoral'` AND `repo = 'coral'`. For example: `WHERE github.workflows.owner = 'withcoral' AND github.workflows.repo = 'coral'`
9. AVAILABLE SOURCES: ONLY use `github`, `sentry`, and `slack`. DO NOT use `pagerduty`, `linear`, or `datadog` in your SQL. If asked about them, use `slack` channels or messages as a proxy.
10. DATE ARITHMETIC: In Coral (DataFusion), you CANNOT subtract intervals directly from strings. You MUST cast them to timestamps first. Example: `CAST(github.pulls.merged_at AS TIMESTAMP) - INTERVAL '1 hour'`.

CROSS-SOURCE JOIN PATTERNS YOU KNOW:
- GitHub commits JOIN Sentry issues: ON sentry.issues.first_seen BETWEEN CAST(github.commits.author_date AS TIMESTAMP) AND CAST(github.commits.author_date AS TIMESTAMP) + INTERVAL '2 hours'
- GitHub PRs JOIN Sentry issues: ON sentry.issues.first_seen BETWEEN CAST(github.pulls.merged_at AS TIMESTAMP) - INTERVAL '1 hour' AND CAST(github.pulls.merged_at AS TIMESTAMP) + INTERVAL '1 hour'
- Any source JOIN Slack channels: ON slack.channels.name ILIKE '%' || identifier || '%'
"""

    async def _reason_over_results(self, question: str, sql: str, results: list) -> AsyncIterator[dict]:
        results_summary = json.dumps(results[:20], indent=2, default=str)
        
        system_prompt = """You are NEXUS, an engineering intelligence system. 
You receive data from a cross-source SQL query over GitHub, Sentry, Slack, Linear, Datadog, and PagerDuty.
Your job is to reason over this unified data and give a structured engineering answer.

ALWAYS structure your response as:
## Root Cause (2 sentences max)
## Evidence (bullet points citing specific data rows)
## Timeline (if temporal data available)  
## Recommended Actions (numbered list)
## Related Signals (other anomalies in the data)

Be specific. Cite commit SHAs, error IDs, Slack usernames, ticket IDs. Never be vague."""

        stream = await self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {question}\n\nSQL Executed:\n{sql}\n\nData Returned:\n{results_summary}"}
            ],
            stream=True,
            temperature=0.3
        )
        
        full_content = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_content += text
                yield {"type": "reasoning", "content": text}
                
        # Send the final structured answer event
        yield {"type": "answer", "structured": self._parse_structured_answer(full_content)}
        
    def _parse_structured_answer(self, text: str) -> dict:
        # A rudimentary parser to turn markdown into a dict for the UI
        # In a full app this might use function calling or more rigorous parsing
        sections = {"root_cause": "", "evidence": "", "timeline": "", "recommended_actions": "", "related_signals": ""}
        current_section = None
        
        for line in text.split('\n'):
            line_clean = line.strip()
            if "## Root Cause" in line_clean:
                current_section = "root_cause"
            elif "## Evidence" in line_clean:
                current_section = "evidence"
            elif "## Timeline" in line_clean:
                current_section = "timeline"
            elif "## Recommended Actions" in line_clean:
                current_section = "recommended_actions"
            elif "## Related Signals" in line_clean:
                current_section = "related_signals"
            elif current_section:
                sections[current_section] += line + "\n"
                
        return {k: v.strip() for k, v in sections.items()}
