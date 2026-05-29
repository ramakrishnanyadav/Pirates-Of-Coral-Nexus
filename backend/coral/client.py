import subprocess
import json
import shutil
import os

class CoralError(Exception):
    pass

class CoralClient:
    """
    Clean interface to the LIVE Coral CLI.
    Natively connects to APIs. Zero mock data.
    """
    
    def __init__(self):
        self._verify_coral_installed()
    
    def _verify_coral_installed(self):
        if not shutil.which("coral"):
            raise CoralError("Coral CLI not found. Please ensure it is installed in the container via curl -fsSL https://withcoral.com/install.sh | sh")
    
    def query(self, sql: str, timeout: int = 45) -> list[dict]:
        """Execute LIVE SQL via Coral CLI, return list of row dicts."""
        try:
            result = subprocess.run(
                ["coral", "sql", "--format", "json", sql],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode != 0:
                raise CoralError(f"Coral live query failed: {result.stderr.strip()}")
            
            data = json.loads(result.stdout)
            return data.get("rows", data) if isinstance(data, dict) else data
            
        except json.JSONDecodeError:
            raise CoralError("Failed to parse JSON output from Coral.")
        except subprocess.TimeoutExpired:
            raise CoralError("Live Coral query timed out after 45 seconds.")
            
    def list_sources(self) -> list[dict]:
        """List all connected LIVE Coral sources."""
        result = subprocess.run(
            ["coral", "source", "list"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return []
        
        sources = []
        lines = result.stdout.split('\n')
        if len(lines) > 2:
            for line in lines[2:]:
                if line.strip():
                    parts = line.split()
                    if parts:
                        sources.append({"name": parts[0]})
        return sources
    
    def get_tables(self) -> list[dict]:
        """Get all available tables from the live Coral catalog."""
        try:
            return self.query(
                "SELECT schema_name, table_name, description "
                "FROM coral.tables ORDER BY schema_name, table_name"
            )
        except Exception as e:
            raise CoralError(f"Failed to fetch live schema: {e}")
            
    def health_check(self) -> dict:
        """Check if Coral is operational and which sources are connected."""
        sources = self.list_sources()
        if not sources:
            return {"status": "error", "message": "No live sources configured. Add API tokens to .env"}
            
        try:
            tables = self.get_tables()
            return {
                "status": "healthy",
                "source_count": len(sources),
                "table_count": len(tables),
                "sources": [s["name"] for s in sources]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
