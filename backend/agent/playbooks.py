PLAYBOOKS = {
    "incident_autopsy": {
        "name": "Incident Autopsy",
        "description": "Correlate recent GitHub deployments (commits), Sentry errors, Slack alerts/channels, and Slack users.",
        "sql": """SELECT
    g.sha AS deploy_commit,
    g.author_login AS deployed_by,
    g.author_date AS deploy_time,
    s.title AS error_title,
    s.count AS error_count,
    s.first_seen AS error_first_seen,
    sl.name AS slack_channel,
    sl.topic AS slack_topic,
    u.name AS slack_user
FROM github.commits g
JOIN sentry.issues s
    ON s.first_seen BETWEEN CAST(g.author_date AS TIMESTAMP) AND CAST(g.author_date AS TIMESTAMP) + INTERVAL '2 hours'
LEFT JOIN slack.channels sl
    ON sl.topic ILIKE '%' || g.sha || '%'
LEFT JOIN slack.users u
    ON sl.purpose ILIKE '%' || u.name || '%'
WHERE g.author_date >= NOW() - INTERVAL '7 days'
AND g.owner = 'withcoral' AND g.repo = 'coral'
ORDER BY s.count DESC
LIMIT 25"""
    },
    "sprint_health": {
        "name": "Sprint Health",
        "description": "Check GitHub PRs and related Slack discussions for active project sprints.",
        "sql": """SELECT
    g.number AS pr_number,
    g.title AS pr_title,
    g.state AS pr_state,
    g.created_at AS created_at,
    g.merged_at AS merged_at,
    sl.name AS slack_channel,
    sl.topic AS slack_topic
FROM github.pulls g
LEFT JOIN slack.channels sl
    ON sl.topic ILIKE '%' || g.title || '%'
WHERE g.state = 'open' OR g.merged_at >= NOW() - INTERVAL '7 days'
AND g.owner = 'withcoral' AND g.repo = 'coral'
ORDER BY g.created_at DESC
LIMIT 25"""
    },
    "security_radar": {
        "name": "Security Radar",
        "description": "Find potential secrets exposed in recent GitHub commits and correlated Sentry issues.",
        "sql": """SELECT
    g.sha AS commit_sha,
    g.commit_message AS commit_message,
    g.author_login AS author,
    g.author_date AS committed_at,
    s.title AS related_sentry_error,
    s.project AS project,
    sl.name AS slack_channel
FROM github.commits g
LEFT JOIN sentry.issues s
    ON s.first_seen BETWEEN CAST(g.author_date AS TIMESTAMP) AND CAST(g.author_date AS TIMESTAMP) + INTERVAL '2 hours'
LEFT JOIN slack.channels sl
    ON sl.topic ILIKE '%secret%' OR sl.purpose ILIKE '%security%'
WHERE (
    g.commit_message ILIKE '%secret%'
    OR g.commit_message ILIKE '%api_key%'
    OR g.commit_message ILIKE '%password%'
    OR g.commit_message ILIKE '%token%'
  )
  AND g.author_date >= NOW() - INTERVAL '30 days'
  AND g.owner = 'withcoral' AND g.repo = 'coral'
ORDER BY g.author_date DESC
LIMIT 25"""
    },
    "oncall_briefing": {
        "name": "On-Call Briefing",
        "description": "Correlate urgent alerts from Slack channels with recent Sentry errors and GitHub commits.",
        "sql": """SELECT
    sl.name AS slack_channel,
    sl.topic AS alert_topic,
    sl.created AS channel_created,
    s.title AS sentry_error,
    s.count AS error_frequency,
    g.sha AS last_deploy,
    g.author_date AS deployed_at
FROM slack.channels sl
LEFT JOIN sentry.issues s
    ON sl.topic ILIKE '%' || s.project || '%'
LEFT JOIN github.commits g
    ON g.author_date >= s.first_seen - INTERVAL '4 hours'
WHERE sl.name ILIKE '%incident%' OR sl.name ILIKE '%alert%'
AND g.owner = 'withcoral' AND g.repo = 'coral'
ORDER BY sl.created DESC
LIMIT 20"""
    }
}
