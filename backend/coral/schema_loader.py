from .client import CoralClient

class SchemaLoader:
    """
    Provides hyper-optimized exact schema definitions for the hackathon demo.
    This prevents the 8B LLM from hallucinating columns and keeps token usage extremely low to avoid rate limits.
    """
    def __init__(self):
        pass
        
    async def get_relevant_schema(self, question: str) -> str:
        return """AVAILABLE TABLES AND EXACT COLUMNS:

[github]
- github.pulls (Pull Requests): id, number, state, title, body, created_at, updated_at, closed_at, merged_at, owner, repo
- github.commits (Commits): sha, commit_message, author_login, author_date, html_url, owner, repo
- github.issues (Issues): id, number, state, title, body, created_at, updated_at, closed_at, owner, repo

[sentry]
- sentry.issues (Sentry Error Groups): id, short_id, title, status, level, count, user_count, first_seen, last_seen, project
- sentry.projects (Sentry Projects): id, slug, name, platform, date_created

[slack]
- slack.channels (Slack Channels): id, name, is_archived, created, num_members, topic, purpose
- slack.users (Slack Users): id, name, real_name, tz, is_admin, is_bot

CRITICAL: YOU MUST ONLY USE THE EXACT COLUMNS LISTED ABOVE. DO NOT INVENT COLUMNS LIKE 'messages' or 'message'.
"""
