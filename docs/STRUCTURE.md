# VoiceStudio Online structure

| Path | Responsibility |
| --- | --- |
| frontend/src/renderer/src/main.tsx | Hosted React entry |
| frontend/src/renderer/src/i18n/ | Runtime translations, 21 languages |
| frontend/src/shared/ | Shared browser controls, API utilities and tests |
| frontend/public/ | Browser assets |
| frontend/dist/ | Generated browser build, ignored by git |
| backend/main.py | Authenticated hosted FastAPI composition root |
| deploy/online/ | CPU Dockerfile using the root frozen uv.lock |
| docker-compose.yml | Persistent, non-root hosting configuration |
| tests/frontend/ | Browser utility and hosting boundary checks |
| docs/online/ | Active architecture, licensing and validation |

There is no mobile or desktop application. Optional legacy bridge declarations
support existing shared browser code and tests; no Electron runtime is shipped.
Upstream manuals retained elsewhere in docs/ describe historical functionality.
