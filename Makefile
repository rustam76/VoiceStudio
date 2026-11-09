# Web hosting commands. See README.md for required environment variables.
.PHONY: dev build test

dev:
	bun run dev

build:
	bun run build:web

test:
	bun run test:frontend
	bun run test

virustotal: export VIRUSTOTAL_FILE = $(FILE)
virustotal:
	python3 scripts/virustotal.py
