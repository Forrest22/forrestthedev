#!/usr/bin/env python3
"""
Static site generator for forrestthe.dev
Fetches pinned GitHub repos via GraphQL API and renders via Jinja2.
"""

import json
import urllib.request
import urllib.error
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

GITHUB_USERNAME = "Forrest22"

# GraphQL query to get pinned repos
PINNED_REPOS_QUERY = """
{
  user(login: "%s") {
    pinnedItems(first: 6, types: REPOSITORY) {
      nodes {
        ... on Repository {
          name
          description
          url
          stargazerCount
          forkCount
          primaryLanguage {
            name
            color
          }
          repositoryTopics(first: 5) {
            nodes {
              topic {
                name
              }
            }
          }
          homepageUrl
          updatedAt
        }
      }
    }
    repositories(first: 6, orderBy: {field: UPDATED_AT, direction: DESC}, privacy: PUBLIC) {
      nodes {
        name
        description
        url
        stargazerCount
        forkCount
        primaryLanguage {
          name
          color
        }
        repositoryTopics(first: 5) {
          nodes {
            topic {
              name
            }
          }
        }
        homepageUrl
        updatedAt
        isFork
      }
    }
  }
}
""" % GITHUB_USERNAME


def fetch_pinned_repos(token=None):
    """Fetch pinned repos from GitHub GraphQL API."""
    url = "https://api.github.com/graphql"
    payload = json.dumps({"query": PINNED_REPOS_QUERY}).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "forrestthe.dev-static-generator",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            user = data.get("data", {}).get("user", {})
            pinned = user.get("pinnedItems", {}).get("nodes", [])
            recent = user.get("repositories", {}).get("nodes", [])

            # Use pinned if available, otherwise fall back to recent non-fork repos
            if pinned:
                return pinned
            return [r for r in recent if not r.get("isFork")][:6]
    except Exception as e:
        print(f"Warning: Could not fetch GitHub data ({e}). Using fallback projects.")
        return get_fallback_projects()


def get_fallback_projects():
    """Fallback project data if GitHub API is unavailable."""
    return [
        {
            "name": "personal-site",
            "description": "My personal website built with Python, Jinja2, and vanilla HTML/CSS. Pulls pinned repos from the GitHub GraphQL API at build time.",
            "url": f"https://github.com/{GITHUB_USERNAME}/personal-site",
            "stargazerCount": 0,
            "forkCount": 0,
            "primaryLanguage": {"name": "Python", "color": "#3572A5"},
            "repositoryTopics": {"nodes": [{"topic": {"name": "jinja2"}}, {"topic": {"name": "static-site"}}]},
            "homepageUrl": "https://forrestthe.dev",
        },
        {
            "name": "project-two",
            "description": "A backend service showcasing REST API design patterns and clean service architecture.",
            "url": f"https://github.com/{GITHUB_USERNAME}",
            "stargazerCount": 0,
            "forkCount": 0,
            "primaryLanguage": {"name": "TypeScript", "color": "#2b7489"},
            "repositoryTopics": {"nodes": [{"topic": {"name": "nodejs"}}, {"topic": {"name": "rest-api"}}]},
            "homepageUrl": None,
        },
        {
            "name": "project-three",
            "description": "A React app with a focus on usability and clean component design.",
            "url": f"https://github.com/{GITHUB_USERNAME}",
            "stargazerCount": 0,
            "forkCount": 0,
            "primaryLanguage": {"name": "JavaScript", "color": "#f1e05a"},
            "repositoryTopics": {"nodes": [{"topic": {"name": "react"}}, {"topic": {"name": "frontend"}}]},
            "homepageUrl": None,
        },
    ]


def build_site(token=None):
    env = Environment(loader=FileSystemLoader("templates"))
    env.filters["pretty_name"] = lambda s: s.replace("-", " ").replace("_", " ").title()

    projects = fetch_pinned_repos(token)
    print(f"Fetched {len(projects)} projects from GitHub.")

    template = env.get_template("index.html")
    context = {
        "name": "Forrest Dodds",
        "tagline": "Full Stack Software Engineer",
        "github_url": f"https://github.com/{GITHUB_USERNAME}",
        "linkedin_url": "https://www.linkedin.com/in/forrest-dodds/",
        "forrestthedev_github_url": "https://github.com/Forrest22/forrestthedev",
        "projects": projects,
        "year": datetime.now().year,
    }

    os.makedirs("dist", exist_ok=True)
    output = template.render(**context)
    with open("dist/index.html", "w", encoding="utf-8") as f:
        f.write(output)
    print("Built dist/index.html successfully.")

    # Copy static assets
    import shutil
    if os.path.exists("profile.jpg"):
        shutil.copy("profile.jpg", "dist/profile.jpg")
        print("Copied profile.jpg to dist/")
    else:
        print("Warning: profile.jpg not found in root — add it before deploying.")


if __name__ == "__main__":
    import sys
    token = os.environ.get("GITHUB_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)
    build_site(token)