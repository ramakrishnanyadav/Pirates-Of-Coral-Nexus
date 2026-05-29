PLAYBOOKS = {
    "incident_autopsy": {
        "name": "Incident Autopsy",
        "description": "Correlate recent deployments, errors, and Slack alerts.",
        "sql": """SELECT
    g.sha                    AS deploy_commit,
    g.author__login          AS deployed_by,
    g.merged_at              AS deploy_time,
    g.title                  AS pr_title,
    s.title                  AS error_title,
    s.culprit                AS error_location,
    s.count                  AS error_count,
    s.first_seen             AS error_first_seen,
    sl.text                  AS slack_message,
    sl.user__name            AS slack_author,
    d.title                  AS datadog_monitor,
    d.status                 AS monitor_status
FROM github.commits g
JOIN sentry.issues s
    ON s.first_seen >= g.merged_at
    AND s.first_seen <= g.merged_at + INTERVAL '2 hours'
LEFT JOIN slack.messages sl
    ON sl.ts >= s.first_seen
    AND sl.channel__name IN ('incidents', 'engineering', 'alerts')
LEFT JOIN datadog.monitors d
    ON d.overall_state = 'Alert'
    AND d.modified >= g.merged_at
WHERE g.merged_at >= NOW() - INTERVAL '7 days'
ORDER BY s.count DESC
LIMIT 25"""
    },
    "sprint_health": {
        "name": "Sprint Health",
        "description": "Check Linear tickets against GitHub PRs and Slack discussions.",
        "sql": """SELECT
    l.identifier             AS ticket_id,
    l.title                  AS ticket_title,
    l.state__name            AS status,
    l.assignee__name         AS owner,
    l.priority               AS priority,
    g.state                  AS pr_state,
    g.title                  AS pr_title,
    g.review_decision        AS pr_review,
    sl.text                  AS last_discussion,
    sl.ts                    AS discussed_at
FROM linear.issues l
LEFT JOIN github.pull_requests g
    ON g.title ILIKE '%' || l.identifier || '%'
LEFT JOIN slack.messages sl
    ON sl.text ILIKE '%' || l.identifier || '%'
    AND sl.ts >= NOW() - INTERVAL '7 days'
WHERE l.cycle__is_active = true
ORDER BY l.priority ASC, l.updated_at DESC"""
    },
    "security_radar": {
        "name": "Security Radar",
        "description": "Find potential secrets exposed in recent commits.",
        "sql": """SELECT
    g.path                   AS file_path,
    g.patch                  AS diff_preview,
    g.commit__message        AS commit_message,
    g.commit__author__login  AS author,
    g.commit__committed_date AS committed_at,
    s.title                  AS related_sentry_error,
    sl.text                  AS slack_mention
FROM github.file_changes g
LEFT JOIN sentry.issues s
    ON s.culprit ILIKE '%' || g.path || '%'
LEFT JOIN slack.messages sl
    ON sl.text ILIKE '%secret%'
    OR sl.text ILIKE '%token%'
    OR sl.text ILIKE '%password%'
WHERE (
    g.patch ILIKE '%secret%'
    OR g.patch ILIKE '%api_key%'
    OR g.patch ILIKE '%password%'
    OR g.patch ILIKE '%token%'
  )
  AND g.committed_at >= NOW() - INTERVAL '30 days'
ORDER BY g.committed_at DESC"""
    },
    "oncall_briefing": {
        "name": "On-Call Briefing",
        "description": "Correlate PagerDuty incidents with Sentry errors and Datadog monitors.",
        "sql": """SELECT
    pd.title                 AS incident_title,
    pd.urgency               AS urgency,
    pd.status                AS incident_status,
    pd.created_at            AS opened_at,
    s.title                  AS sentry_error,
    s.count                  AS error_frequency,
    g.sha                    AS last_deploy,
    g.merged_at              AS deployed_at,
    d.title                  AS triggered_monitor
FROM pagerduty.incidents pd
LEFT JOIN sentry.issues s
    ON s.first_seen >= pd.created_at - INTERVAL '30 minutes'
    AND s.first_seen <= pd.created_at + INTERVAL '30 minutes'
LEFT JOIN github.commits g
    ON g.merged_at >= pd.created_at - INTERVAL '4 hours'
LEFT JOIN datadog.monitors d
    ON d.overall_state = 'Alert'
WHERE pd.status IN ('triggered', 'acknowledged')
ORDER BY pd.urgency DESC, pd.created_at DESC
LIMIT 20"""
    }
}
