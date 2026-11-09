# VoiceStudio web

The browser-only React/Vite workspace. The hosted entry is
`src/renderer/src/main.tsx`; the build writes `dist/`, served by FastAPI.
There is no Electron main process, preload implementation or native installer.
Shared browser modules and their optional legacy bridge declarations remain for
compatibility and unit tests; they do not create a desktop application.

From the repository root:

```sh
bun install --frozen-lockfile --ignore-scripts
bun run --cwd frontend dev:web
bun run typecheck
bun run test
bun run build:web
```

Run the full backend separately with `bun run dev:api`; configure the API key
and model as described in [the hosting guide](../README.md).
Translations live in `src/renderer/src/i18n/locales/` (all 21 languages).
Keep `src/shared/components/VoiceSelector.jsx` and `SearchableSelect.jsx` for
voice and select controls. Third-party notices include `T3CODE-LICENSE.txt`.
