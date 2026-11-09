# Contributing to VoiceStudio Online

This fork is a hosted web application. Read [README](../README.md) for setup,
HTTPS, models, licensing, API/MCP access and backup. Native apps and installers
are removed; historical upstream guides do not define this fork's scope.

## Development

Use Python 3.12, uv and the Bun version in root package.json. From the root:

```sh
uv sync --frozen --no-default-groups --group cpu --group dev --extra supertonic
bun install --frozen-lockfile --ignore-scripts
bun run dev:api
# In another terminal:
bun run --cwd frontend dev:web
```

Configure the API key and model acceptance/download as documented in README.
The frontend workspace is frontend/; backend/main.py composes the server.

## Quality gates

```sh
bun run typecheck
bun run test:frontend
bun run test
bun run build:web
HF_HUB_OFFLINE=1 HF_HUB_CACHE=/tmp/online-empty-hf-cache \
  .venv/bin/python -m pytest tests/test_docker_entrypoint.py -q
```

Use an empty HF cache, not a developer model cache. Active CI is
.github/workflows/ci.yml. It checks the full backend and browser, then builds
web and Docker for runtime changes. Documentation/test-only changes skip
product builds explicitly. Identity, CLA and security checks still apply.

Keep authentication, CSRF, protected audio/MCP and mark_synthetic intact.
Model downloads require explicit user action and licence acceptance is separate.
Do not add mandatory network services or idle downloads. User content must not
be sent to external services without explicit consent.

All visible strings use real translations in all 21 frontend runtime locale
catalogs. Reuse VoiceSelector and SearchableSelect with localized ariaLabel and
keyboard support. Run locale:check and tests/test_locale_parity.py after edits.

Root package.json is the version source; do not bump unless requested.
Regenerate bun.lock for JS manifest changes. Preserve licence notices and data.
Add a quiet changelog.d/<PR#>.<type>.md fragment for a numbered PR; credit human
contributors, never agents. Do not modify CHANGELOG.md directly.

Read CodeRabbit and Greptile findings before merge, fix them on the PR branch,
update from main and require Tests (backend + frontend) green and MERGEABLE.
Watch main CI after every merge. See ../AGENTS.md for the operating contract.
