"""
GitHub telemetry for the homepage display (Afterburner).

GitHub only serves contribution history to authenticated requests, so this runs
on the server: the token stays in the environment and never reaches the browser.
Results are cached so the page makes at most one GitHub call per hour.

Setup: put a GitHub token in the GITHUB_TOKEN environment variable
(.env locally, the PWS environment variables in production). A fine-grained
token with no extra permissions is enough, because every field read here is public.
Without a token, get_github_telemetry() returns None and the page falls back
to the browser-side readouts.
"""
import logging
import os
from datetime import date, datetime

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

GITHUB_USER = "DJITOE-IPUN"
GRAPHQL_URL = "https://api.github.com/graphql"
CACHE_KEY = "afterburner:github-telemetry:v1"
CACHE_SECONDS = 60 * 60          # one GitHub call per hour at most
FAILURE_CACHE_SECONDS = 10 * 60  # after a failure, wait before trying again
REQUEST_TIMEOUT = 4              # seconds; the homepage must never hang on GitHub

# Drawing area of the trace, matching the SVG viewBox in index.html
TRACE_WIDTH = 600
TRACE_HEIGHT = 64
TRACE_PADDING = 6

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    latest: repositories(
      first: 1
      privacy: PUBLIC
      ownerAffiliations: OWNER
      orderBy: {field: PUSHED_AT, direction: DESC}
    ) {
      nodes { name url pushedAt }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def get_github_telemetry():
    """Return the telemetry dict for the homepage, or None when it isn't available."""
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached or None  # False marks a recent failure

    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        return None

    try:
        response = requests.post(
            GRAPHQL_URL,
            json={"query": QUERY, "variables": {"login": GITHUB_USER}},
            headers={"Authorization": f"Bearer {token}"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        user = response.json()["data"]["user"]
        telemetry = build_telemetry(user)
    except Exception:  # network error, bad token, rate limit, schema change
        logger.warning("GitHub telemetry unavailable", exc_info=True)
        cache.set(CACHE_KEY, False, FAILURE_CACHE_SECONDS)
        return None

    cache.set(CACHE_KEY, telemetry, CACHE_SECONDS)
    return telemetry


def build_telemetry(user):
    """Turn GitHub's GraphQL `user` payload into what the template needs."""
    calendar = user["contributionsCollection"]["contributionCalendar"]
    weeks = [w["contributionDays"] for w in calendar["weeks"] if w["contributionDays"]]
    weekly = [sum(day["contributionCount"] for day in days) for days in weeks]

    peak = max(weekly) if weekly else 0
    peak_index = weekly.index(peak) if weekly else 0
    points = trace_points(weekly, peak)

    latest_nodes = user["latest"]["nodes"]
    latest = latest_nodes[0] if latest_nodes else None

    return {
        "total": calendar["totalContributions"],
        "repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "weeks": len(weekly),
        "trace_points": " ".join(f"{x:.1f},{y:.1f}" for x, y in points),
        "top_speed": peak,
        "top_week": date.fromisoformat(weeks[peak_index][0]["date"]) if weeks else None,
        "top_x": round(points[peak_index][0], 1) if points else 0,
        "top_y": round(points[peak_index][1], 1) if points else TRACE_HEIGHT - TRACE_PADDING,
        "last_repo": latest["name"] if latest else None,
        "last_repo_url": latest["url"] if latest else None,
        "pushed_at": _parse_datetime(latest["pushedAt"]) if latest and latest["pushedAt"] else None,
    }


def trace_points(values, peak=None):
    """Scale weekly totals into (x, y) points inside the trace's drawing area."""
    if not values:
        return []
    peak = peak if peak is not None else max(values)
    span = max(len(values) - 1, 1)
    usable = TRACE_HEIGHT - TRACE_PADDING * 2
    baseline = TRACE_HEIGHT - TRACE_PADDING
    return [
        (i / span * TRACE_WIDTH, baseline - (v / peak * usable if peak else 0))
        for i, v in enumerate(values)
    ]


def _parse_datetime(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
