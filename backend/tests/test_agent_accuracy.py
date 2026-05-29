import pytest
import asyncio
from backend.agent.nexus_agent import NexusAgent

@pytest.fixture
def agent():
    return NexusAgent()

def test_sql_generation_prompt(agent):
    """
    Test that the system prompt correctly enforces LIMIT 25 and standard SQL rules
    so the LLM doesn't hallucinate invalid Coral queries.
    """
    prompt = agent._sql_system_prompt("schema test")
    assert "LIMIT clauses (default: 25 rows)" in prompt
    assert "JOIN patterns" in prompt.lower()
    
def test_source_counting(agent):
    """
    Verify the UI correctly highlights active sources based on the generated SQL.
    """
    sql = "SELECT * FROM github_commits g JOIN sentry_issues s ON g.sha = s.culprit"
    count = agent._count_sources(sql)
    # the function counts 'github' 'sentry' based on simple match 'github.' or 'github_'
    assert count >= 1

def test_structured_answer_parser(agent):
    """
    Verify that the mock reasoning markdown is properly sliced into the UI components.
    """
    sample_text = """
## Root Cause
The payment processor broke.

## Evidence
- Row 1 shows payment failures.

## Timeline
- 1:00 AM: Thing broke.
- 1:05 AM: We noticed.

## Recommended Actions
1. Fix it.
    """
    parsed = agent._parse_structured_answer(sample_text)
    assert "The payment processor broke." in parsed["root_cause"]
    assert "Row 1 shows payment failures." in parsed["evidence"]
    assert "1:00 AM: Thing broke." in parsed["timeline"]
    assert "Fix it." in parsed["recommended_actions"]
