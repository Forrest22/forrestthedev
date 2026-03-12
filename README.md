# forrestthe.dev — Static Site Generator

Built with Python + Jinja2. Pulls pinned GitHub repos via the GraphQL API. Meant to be deployed on DigitalOcean.

[See it live](https://forrestthe.dev/)

## Setup

```bash
pip install jinja2
```

## Build

```bash
# Without a token (public repos only, 60 req/hr rate limit)
python build.py

# With a GitHub personal access token (recommended — avoids rate limits)
export GITHUB_TOKEN=ghp_your_token_here
python build.py

# Or pass it directly
python build.py ghp_your_token_here
```

Output is written to `dist/index.html`. Deploy that file to any static host
(Netlify, Vercel, GitHub Pages, etc.).

## GitHub Token

Generate a fine-grained token at <https://github.com/settings/tokens>
with **read-only** access to public repositories. No extra scopes needed.
