# Hosting releases

This fork ships the Online website and backend through Docker. Native desktop,
mobile and store release pipelines have been removed. Root package.json is the
version source; do not bump, tag, push or publish without owner instruction.
Maintain pyproject.toml and backend/core/version.py mirrors when bumping.

Before releasing, review findings and run active Online CI: frozen dependency
installs, frontend tests/typecheck/build, offline backend tests, Docker build and
Compose validation. Validate authentication, model-licence acceptance and
persistent data with the built image. Keep licences and source available.

Back up data before updating. Follow README.md for deployment, health checks,
rollback and restore. Never delete a data volume as an update step. Historical
updater feeds remain immutable; this fork publishes no replacement installers.

Version bumps are manual and require owner approval.
