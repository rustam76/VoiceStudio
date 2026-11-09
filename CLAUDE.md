# VoiceStudio Online operating contract

## Owner-approved scope

As of 2026-11-09, this fork is a hosted web application. Native iOS/Android,
Electron main/preload, desktop installers and store release pipelines are
removed. This decision supersedes older upstream platform and release rules.
Do not restore native apps. Retain the full browser application and public API.

The frontend workspace is `frontend/`. The browser entry is
`frontend/src/renderer/src/main.tsx`, with shared browser modules under
`frontend/src/shared/`. Vite builds `frontend/dist/`, served by the authenticated
FastAPI app `backend/main.py`. CPU deployment uses `deploy/online/Dockerfile`
and root `docker-compose.yml`, a single worker and persistent `/data` volume.

Version bumps are manual and happen only when the owner asks.

## Required safeguards

- Follow AGENTS.md for workflow, i18n, controls, reviews and attribution.
- Preserve existing backend models/engine compatibility and user data; never
  delete databases, generated audio, model caches, licences or updater feeds.
- Preserve mark_synthetic as the output chokepoint and explicit model-licence
  acceptance. Downloads never imply accepting a model's terms.
- Authentication covers API, audio and MCP. Cookie authentication retains CSRF.
  Do not bypass auth for localhost/proxies or bake credentials into web assets.
- Keep the Docker process non-root, secrets in deployment configuration, the
  default published port on loopback, and explain HTTPS in hosting instructions.
- No new mandatory external services, downloads at idle or telemetry without
  consent. Preserve existing licensed-source and attribution obligations.
- Root package.json is the single version source; do not bump without asking.
  pyproject.toml and backend/core/version.py are maintained mirrors.
- Preserve root bun.lock and deploy/online/uv.lock frozen installs. Do not add
  frameworks or dependencies when existing ones suffice.
- Local tests are targeted; backend tests use HF_HUB_OFFLINE=1 with an empty
  HF_HUB_CACHE. Report existing failures and untested deployment limits honestly.
- Never commit, push, merge, tag, publish or deploy unless the user requests it.

## Sources of truth

README.md and docs/online/ describe this fork. Other upstream desktop/mobile
manuals and release notes are historical references, not active instructions.
Only YAML directly under .github/workflows/ runs as GitHub Actions; archived
upstream workflows are not active CI or supported release paths.
