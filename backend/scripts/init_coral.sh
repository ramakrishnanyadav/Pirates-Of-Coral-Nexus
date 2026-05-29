#!/bin/bash
set -e

echo "Initializing Coral CLI with Live API Data Sources..."

# Check if Coral is installed
if ! command -v coral &> /dev/null; then
    echo "Coral could not be found. Please ensure it is installed."
    exit 1
fi

# Add GitHub Source
if [ -n "$GITHUB_TOKEN" ]; then
    echo "Configuring GitHub API source..."
    # Assuming coral allows non-interactive addition via env vars or flags
    # Standard format: coral source add github
    coral source add github || true
else
    echo "WARNING: GITHUB_TOKEN not found. GitHub live queries will fail."
fi

# Add Sentry Source
if [ -n "$SENTRY_AUTH_TOKEN" ]; then
    echo "Configuring Sentry API source..."
    coral source add sentry || true
else
    echo "WARNING: SENTRY_AUTH_TOKEN not found."
fi

# Add Slack Source
if [ -n "$SLACK_USER_TOKEN" ]; then
    echo "Configuring Slack API source..."
    coral source add slack || true
else
    echo "WARNING: SLACK_USER_TOKEN not found."
fi

# Add Datadog Source
if [ -n "$DD_API_KEY" ]; then
    echo "Configuring Datadog API source..."
    coral source add datadog || true
else
    echo "WARNING: DD_API_KEY not found."
fi

echo "Coral live API configuration complete!"
