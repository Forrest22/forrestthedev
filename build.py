#!/usr/bin/env python3
"""
Static site generator for https://forrestthe.dev/
Fetches pinned GitHub repos via GraphQL API and renders via Jinja2.
"""

import json
import os
import shutil
import sys
import urllib.request
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

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
                return pinned, False
            return [r for r in recent if not r.get("isFork")][:6], False
    except Exception as e:
        print(f"Warning: Could not fetch GitHub data ({e}). Using fallback projects.")
        return get_fallback_projects(), True


def get_fallback_projects():
    """Fallback project data if GitHub API is unavailable."""
    return [
        {
            "name": "AOC-2025",
            "description": "Advent of Code 2025, completed using Python",
            "url": f"https://github.com/{GITHUB_USERNAME}/AOC-2025",
            "stargazerCount": 0,
            "forkCount": 0,
            "primaryLanguage": {"name": "Python", "color": "#3572A5"},
            "repositoryTopics": {"nodes": []},
            "homepageUrl": None,
        },
        {
            "name": "AOC-2024",
            "description": "Advent of Code 2024, completed using Go",
            "url": f"https://github.com/{GITHUB_USERNAME}/AOC-2024",
            "stargazerCount": 0,
            "forkCount": 0,
            "primaryLanguage": {"name": "Go", "color": "#00ADD8"},
            "repositoryTopics": {"nodes": []},
            "homepageUrl": None,
        },
        {
            "name": "disc-golf-event-buddy",
            "description": "A live scoreboard display for disc golf events with customizable features, made for large screens.",
            "url": f"https://github.com/{GITHUB_USERNAME}/disc-golf-event-buddy",
            "stargazerCount": 0,
            "forkCount": 0,
            "primaryLanguage": {"name": "HTML", "color": "#e34c26"},
            "repositoryTopics": {"nodes": []},
            "homepageUrl": None,
        },
        {
            "name": "discord-spotify-utility",
            "description": "Utility discord bot to analyze and build playlists off a discord channel that uses spotify links.",
            "url": f"https://github.com/{GITHUB_USERNAME}/discord-spotify-utility",
            "stargazerCount": 0,
            "forkCount": 0,
            "primaryLanguage": {"name": "Python", "color": "#3572A5"},
            "repositoryTopics": {"nodes": []},
            "homepageUrl": None,
        },
        {
            "name": "chess-botinator",
            "description": "Chess Botinator is a chess bot built to destroy Will's chess bot. Built to integrate to UCI, mainly will be using https://github.com/lichess-bot-devs/lichess-bot",
            "url": f"https://github.com/{GITHUB_USERNAME}/chess-botinator",
            "stargazerCount": 0,
            "forkCount": 0,
            "primaryLanguage": {"name": "Python", "color": "#3572A5"},
            "repositoryTopics": {"nodes": []},
            "homepageUrl": None,
        },
        {
            "name": "MrSuicideSheep-Backgrounds",
            "description": "A complation of Mr. Suicidesheep's backgrounds on a cyberpunk inspired static website.",
            "url": f"https://github.com/{GITHUB_USERNAME}/MrSuicideSheep-Backgrounds",
            "stargazerCount": 0,
            "forkCount": 0,
            "primaryLanguage": {"name": "JavaScript", "color": "#f1e05a"},
            "repositoryTopics": {"nodes": []},
            "homepageUrl": f"https://{GITHUB_USERNAME}.github.io/MrSuicideSheep-Backgrounds/",
        },
    ]


def build_site(token=None, require_github=False):
    env = Environment(loader=FileSystemLoader("templates"))
    env.filters["pretty_name"] = lambda s: s.replace("-", " ").replace("_", " ").title()

    projects, is_fallback = fetch_pinned_repos(token)
    if is_fallback:
        if require_github:
            print("Error: GitHub API unavailable and --no-fallback is set. Aborting.")
            sys.exit(1)
        print(f"Using {len(projects)} fallback projects (GitHub API unavailable).")
    else:
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
    if os.path.exists("profile.jpg"):
        shutil.copy("profile.jpg", "dist/profile.jpg")
        print("Copied profile.jpg to dist/")
    else:
        print("Warning: profile.jpg not found in root — add it before deploying.")
    if os.path.exists("favicon.ico"):
        shutil.copy("favicon.ico", "dist/favicon.ico")
        print("Copied favicon.ico to dist/")
    else:
        print("Warning: favicon.ico not found in root — add it before deploying.")


if __name__ == "__main__":
    args = sys.argv[1:]
    require_github = "--no-fallback" in args
    args = [a for a in args if a != "--no-fallback"]
    token = (args[0] if args else None) or os.environ.get("GITHUB_TOKEN")
    build_site(token, require_github=require_github)