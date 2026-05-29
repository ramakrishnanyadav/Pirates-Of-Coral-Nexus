PLAYBOOKS = {
    "incident_autopsy": {
        "name": "Incident Autopsy",
        "description": "Generate a comprehensive SQL query to correlate recent GitHub deployments (commits), Sentry errors, Slack alerts/channels, and Slack users to find the root cause of an incident. Return the commit sha, author, time, error title, error count, and slack channel info."
    },
    "sprint_health": {
        "name": "Sprint Health",
        "description": "Generate a SQL query to check GitHub PRs and related Slack discussions for active project sprints. Return the PR number, title, state, creation/merge times, and related slack channel topics."
    },
    "security_radar": {
        "name": "Security Radar",
        "description": "Generate a SQL query to find potential secrets exposed in recent GitHub commits and correlate them with Sentry security issues and Slack channels. Look for 'secret', 'api_key', 'password', or 'token' in the commit messages."
    },
    "oncall_briefing": {
        "name": "On-Call Briefing",
        "description": "Generate a SQL query to correlate urgent alerts from Slack channels with recent Sentry errors and GitHub commits. Return the channel name, alert topic, sentry error frequency, and the last deployment details."
    }
}
