# VoiceStudio Online support

For hosting setup, model preparation, authentication, HTTPS, logs, update and
backup/restore, follow [README](../README.md). For problems specific to this
fork, open an issue in this fork with sanitized server logs and a reproducible
example. Never include API keys, cookies, private text, audio or environment files.
Report security issues privately using [SECURITY.md](SECURITY.md).

This fork provides a website, not desktop installers or mobile applications.
Before removing a deployment, back up the Docker data volume. Stopping the
container does not require deleting its data; never use `docker compose down -v`
unless you intentionally want to erase the persistent database, audio and models.
