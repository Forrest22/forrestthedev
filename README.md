# forrestthe.dev — Static Site Generator

Built with Python + Jinja2. Pulls pinned GitHub repos via the GraphQL API. Meant to be deployed on DigitalOcean.

[See it live](https://forrestthe.dev/)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install jinja2
```

## Build

```bash
source venv/bin/activate

# Without a token (public repos only, 60 req/hr rate limit)
python build.py

# With a GitHub personal access token (recommended — avoids rate limits)
export GITHUB_TOKEN=$(cat .github_token)
python build.py

# Or pass it directly (CLI arg takes precedence over env var)
python build.py $(cat .github_token)

# Fail the build if GitHub API is unreachable instead of using fallback data
python build.py --no-fallback
```

Output is written to `dist/index.html`. **Commit the `dist/` directory** — the
DigitalOcean deployment has no build step and serves `dist/` directly.

## GitHub Token

Generate a fine-grained token at <https://github.com/settings/tokens>
with **read-only** access to public repositories. No extra scopes needed.

For local development, save the token to `.github_token` (already gitignored)
and load it with `export GITHUB_TOKEN=$(cat .github_token)`.
