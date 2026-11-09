# Latest upstream browser application without native apps

Owner request, 2026-11-09: pull the latest application but remove desktop and
mobile applications. Preserve the complete web interface, not the earlier
minimal narration-only Online entry.

## Source and scope

`origin/main` was force-updated to upstream commit `d40fd359c`, replacing the
earlier custom web-only history. Work starts on
`refactor/latest-web-without-native` directly from this new base. The previous
`refactor/web-only-hosting` branch preserves the old implementation.

Keep the latest React App/router, all browser pages, shared controls, translations
and the full backend. Move the browser workspace from electron/ to frontend/.
Remove Electron main/preload implementations, native helpers, mobile apps,
store/native release tooling, and their dedicated checks. Optional legacy
bridge declarations are type-only compatibility for browser modules.

## Hosting

The default hosted entry is now frontend/src/renderer/src/main.tsx plus
backend.main:app. The former Online composition root was deliberately limited
to narration and cannot provide the full web app's routes.

Use the upstream frozen Python lock with the CPU group and Supertonic extra.
The runtime image therefore includes more dependencies than the old narration
image. Availability and performance of individual engines still depend on the
server and explicitly installed models. Browser-incompatible native functions
retain the upstream browser restrictions.

Keep the existing Compose project name, service studio, volume studio-data and
/data mount, HF_HOME=/data/huggingface, and Supertonic pinned revision. Preserve
server-mode authentication, CSRF, watermark processing and all notices. Do not
delete models or user data. Back up the database before deploying newer upstream
migrations. No manual version bump: version metadata comes from the imported
upstream snapshot.

## Checks

- [x] Fail-before/pass-after source check for full UI and native app exclusion.
- [x] Frozen Bun install, web typecheck and full browser production build.
- [x] Root development, API and hosting script checks: 76 tests passed.
- [x] Full renderer suite: 316 files / 2096 tests passed with the upstream Vite+ runner.
- [x] Shared suite missing-file fixture corrected and its 83 tests pass.
- [x] Targeted backend/auth, configuration, locale and source guards: 774 tests and 30 subtests passed offline.
- [x] Independent source review: no confirmed important defects remaining.
- [x] Full shared suite: 339 files / 3124 tests passed.
- [x] Linux ARM64 CPU image builds and starts; /health returns HTTP 200.
- [x] Real browser login, workspace, cloning, dubbing, transcription and models
  pages render without JavaScript errors; the master key is not stored in localStorage.
- [x] Model cache stays empty at startup when HF is offline.

The first ARM64 build exposed sphn's vendored Opus/CMake incompatibility. The
image links to Debian's Opus using pkg-config/libopus-dev instead. Browser smoke
also exposed the upstream local-install wizard's 8 GiB hardware gate; hosted
builds now open the workspace directly. Privacy consent remains explicit,
model licences remain independently gated, and local setup completion is not
written. Both hosted gate changes have failing-before/passing-after tests.

Graph tools are unavailable; manifest and source inspection are the fallback.
The owner subsequently requested committing and pushing this update. No deployment is performed.
