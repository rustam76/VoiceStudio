# Agent Rules — VoiceStudio Online

## Product scope (owner decision, 2026-11-09)

This repository is web-only for hosting. Mobile apps, Electron runtime,
installers, native desktop helpers and store releases have been removed.
Do not restore them. The browser UI belongs in `frontend/`; the hosted entry
is `frontend/src/renderer/src/main.tsx`. Shared browser modules and
legacy type declarations are not a native app. Backend hosting uses
`backend/main.py`, `deploy/online/Dockerfile` and root `docker-compose.yml`.
Older desktop/mobile documentation is historical, not a product requirement.
CLAUDE.md contains the full operating rules.

## Working rules

- Short responses; one-line status updates. Read existing CI output first.
- Structural exploration uses the installed codebase-memory skill; fall back to
  source inspection if its tools are unavailable.
- Root-cause fixes, smallest correct change, targeted regression checks.
- Preserve existing user data, models, licences, notices and immutable updater
  feeds. No version bump unless requested; root package.json is canonical.
- Never commit, push, deploy or publish unless requested.
- Start new branches from freshly fetched origin/main; preserve local work.
- All visible strings use i18n with real translations in all 21
  `frontend/src/renderer/src/i18n/locales/*.json` catalogs.
- Reuse `frontend/src/shared/components/SearchableSelect.jsx`; voice choices use
  VoiceSelector. Localized ariaLabel, keyboard/disabled support, menuPortal in
  clipping containers. Do not introduce native select controls.
- Keep server authentication, CSRF and protected audio/MCP access intact.
  No required new network services. Model downloads require explicit action;
  synthetic output goes through mark_synthetic.
- JavaScript manifest changes require regenerating root bun.lock.
- Run targeted tests; HF_HUB_OFFLINE=1 and an empty HF_HUB_CACHE for backend
  checks. Run appropriate full checks before landing.
- Update affected active docs. PR changelog fragments go in changelog.d/;
  never edit CHANGELOG.md or invent a PR number.
- Commit/PR attribution uses only the submitter's identity; no agent credits.
- Never merge without review: harvest CodeRabbit/Greptile, fix findings on the
  PR branch, merge latest main, require MERGEABLE and Tests (backend + frontend)
  green; after merging watch main's own CI to green.

## References

- Active installation, hosting, backup and HTTPS instructions: README.md.
- Online architecture and validation: docs/online/.
- Project skills: .agents/skills/ (Vite and FastAPI).
- Issues: gh CLI, docs/agents/issue-tracker.md and triage-labels.md.
- Older upstream guidance and screenshots are retained as historical material.
