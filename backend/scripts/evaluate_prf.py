import asyncio
import os
import re
import sys
from unittest.mock import patch
from dotenv import load_dotenv

# Ensure backend module is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from agent.nexus_agent import NexusAgent
from coral.schema_loader import SchemaLoader

TEST_CASES = [
    {
        "name": "Incident Autopsy Playbook",
        "question": "Run playbook: incident_autopsy",
        "expected_tables": ["github.commits", "sentry.issues", "slack.channels", "slack.users"],
        "expected_columns": ["sha", "first_seen", "topic", "name"]
    },
    {
        "name": "Security Radar Playbook",
        "question": "Run playbook: security_radar",
        "expected_tables": ["github.commits", "sentry.issues", "slack.channels"],
        "expected_columns": ["commit_message", "title", "project"]
    },
    {
        "name": "Cross-Source Join Sentry + Slack",
        "question": "Show me errors from the frontend project in Sentry correlated with slack channels about alerts",
        "expected_tables": ["sentry.issues", "slack.channels"],
        "expected_columns": ["project", "name"]
    },
    {
        "name": "GitHub + Sentry Correlation",
        "question": "Which github commits caused issues in sentry over the last 7 days?",
        "expected_tables": ["github.commits", "sentry.issues"],
        "expected_columns": ["sha", "first_seen"]
    }
]

@patch('agent.nexus_agent.CoralClient')
async def evaluate(MockCoralClient):
    agent = NexusAgent()
    schema_loader = SchemaLoader()
    
    total_expected = 0
    total_predicted = 0
    true_positives = 0
    
    print("Starting PRF Evaluation for SQL Generation...\n")
    
    for tc in TEST_CASES:
        print(f"--- Running Test: {tc['name']} ---")
        question = tc["question"]
        schema_context = await schema_loader.get_relevant_schema(question)
        
        try:
            sql = await agent._generate_sql(question, schema_context, {})
            print(f"Generated SQL:\n{sql}\n")
        except Exception as e:
            print(f"LLM Error: {e}\n")
            total_expected += len(tc["expected_tables"]) + len(tc["expected_columns"])
            continue
            
        sql_lower = sql.lower()
        
        expected_items = tc["expected_tables"] + tc["expected_columns"]
        
        # Rough heuristic: count total words that look like identifiers as 'predicted items' 
        # to calculate precision. A more accurate parser would be needed for a real AST evaluation.
        words = set(re.findall(r'[a-z_]+', sql_lower))
        predicted_items_count = len([w for w in words if len(w) > 3 and w not in ['select', 'from', 'where', 'join', 'inner', 'left', 'and', 'cast', 'timestamp', 'interval']])
        
        total_predicted += predicted_items_count
        
        tc_tp = 0
        for item in expected_items:
            total_expected += 1
            if item.lower() in sql_lower:
                true_positives += 1
                tc_tp += 1
            else:
                print(f"  [MISSING] Expected '{item}' not found in SQL.")
                
        print(f"  Test Score: {tc_tp}/{len(expected_items)} expected items found.\n")
        
    precision = true_positives / total_predicted if total_predicted > 0 else 0
    recall = true_positives / total_expected if total_expected > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    accuracy = recall # In retrieval context, recall of expected concepts is often proxy for accuracy
    
    print("=========================================")
    print("          FINAL EVALUATION METRICS       ")
    print("=========================================")
    print(f"True Positives (Expected found):  {true_positives}")
    print(f"Total Expected Elements:          {total_expected}")
    print(f"Total Predicted Elements:         {total_predicted}")
    print("-----------------------------------------")
    print(f"Accuracy (Recall proxy):          {accuracy:.2%}")
    print(f"Precision:                        {precision:.2f}")
    print(f"Recall:                           {recall:.2f}")
    print(f"F1 Score:                         {f1:.2f}")
    print("=========================================")
    
    # Save results to a file
    with open('prf_results.txt', 'w') as f:
        f.write(f"Accuracy: {accuracy:.2%}\nPrecision: {precision:.2f}\nRecall: {recall:.2f}\nF1: {f1:.2f}\n")

if __name__ == "__main__":
    asyncio.run(evaluate())
