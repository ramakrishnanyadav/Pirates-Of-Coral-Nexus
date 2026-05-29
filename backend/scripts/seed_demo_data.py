import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "demo_sources.db")

def create_tables(cursor):
    cursor.executescript("""
        DROP TABLE IF EXISTS github_commits;
        CREATE TABLE github_commits (
            sha TEXT PRIMARY KEY,
            author__login TEXT,
            merged_at DATETIME,
            title TEXT,
            message TEXT
        );

        DROP TABLE IF EXISTS sentry_issues;
        CREATE TABLE sentry_issues (
            id TEXT PRIMARY KEY,
            title TEXT,
            culprit TEXT,
            count INTEGER,
            first_seen DATETIME
        );

        DROP TABLE IF EXISTS slack_messages;
        CREATE TABLE slack_messages (
            ts DATETIME,
            channel__name TEXT,
            user__name TEXT,
            text TEXT
        );

        DROP TABLE IF EXISTS datadog_monitors;
        CREATE TABLE datadog_monitors (
            id TEXT PRIMARY KEY,
            title TEXT,
            overall_state TEXT,
            modified DATETIME
        );
        
        DROP TABLE IF EXISTS pagerduty_incidents;
        CREATE TABLE pagerduty_incidents (
            id TEXT PRIMARY KEY,
            title TEXT,
            urgency TEXT,
            status TEXT,
            created_at DATETIME
        );
    """)

def seed_incident_timeline(cursor):
    """
    The Perfect Incident Timeline:
    1:47 AM - PR Merged (github)
    2:03 AM - Sentry Spike (sentry)
    2:05 AM - Datadog Alert (datadog)
    2:07 AM - Slack incident discussion (slack)
    2:12 AM - Rollback started / PD incident triggered
    """
    base_time = datetime.utcnow().replace(hour=1, minute=0, second=0, microsecond=0)
    
    # 1. GitHub
    cursor.execute("""
        INSERT INTO github_commits (sha, author__login, merged_at, title, message)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "a1b2c3d4", "johndoe", 
        (base_time + timedelta(minutes=47)).isoformat(),
        "Refactor payment processor null checks",
        "Refactoring the payment processor to remove redundant null checks. Fixes #892."
    ))

    # 2. Sentry
    cursor.execute("""
        INSERT INTO sentry_issues (id, title, culprit, count, first_seen)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "SEN-9021", 
        "TypeError: Cannot read properties of null (reading 'amount')", 
        "payments/processor.ts", 
        847, 
        (base_time + timedelta(hours=1, minutes=3)).isoformat()
    ))

    # 3. Datadog
    cursor.execute("""
        INSERT INTO datadog_monitors (id, title, overall_state, modified)
        VALUES (?, ?, ?, ?)
    """, (
        "DD-104", 
        "High Error Rate - Checkout API", 
        "Alert", 
        (base_time + timedelta(hours=1, minutes=5)).isoformat()
    ))

    # 4. Slack
    slack_msgs = [
        ((base_time + timedelta(hours=1, minutes=7)).isoformat(), "incidents", "alice_oncall", "Anyone seeing elevated 500s on checkout? Just got a Datadog alert."),
        ((base_time + timedelta(hours=1, minutes=8)).isoformat(), "incidents", "bob_backend", "Yeah, Sentry is blowing up with TypeError in processor.ts"),
        ((base_time + timedelta(hours=1, minutes=10)).isoformat(), "incidents", "alice_oncall", "Looking at recent deploys... a1b2c3d4 went out 20 mins ago."),
        ((base_time + timedelta(hours=1, minutes=12)).isoformat(), "incidents", "bob_backend", "Rollback initiated. Opening PagerDuty incident to track.")
    ]
    for msg in slack_msgs:
        cursor.execute("INSERT INTO slack_messages (ts, channel__name, user__name, text) VALUES (?, ?, ?, ?)", msg)

    # 5. PagerDuty
    cursor.execute("""
        INSERT INTO pagerduty_incidents (id, title, urgency, status, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "PD-2891", 
        "Checkout API 500s Spiking", 
        "high", 
        "triggered", 
        (base_time + timedelta(hours=1, minutes=12)).isoformat()
    ))
    
    # Add some noise (normal commits/messages)
    cursor.execute("""
        INSERT INTO github_commits (sha, author__login, merged_at, title, message)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "f8e7d6c5", "sarah_ui", 
        (base_time - timedelta(hours=12)).isoformat(),
        "Update button styles",
        "Updating button styles to match new design system."
    ))

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Creating tables in {DB_PATH}...")
    create_tables(cursor)
    
    print("Seeding cinematic incident timeline...")
    seed_incident_timeline(cursor)
    
    conn.commit()
    conn.close()
    print("✅ Demo database seeded successfully.")

if __name__ == "__main__":
    main()
