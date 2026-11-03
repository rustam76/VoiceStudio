# VoiceStudio Online Implementation Plan

**Goal:** deployment CPU server untuk narasi Indonesia, Web UI, API dan MCP.
**Architecture:** composition root FastAPI yang memakai router dan engine
upstream; entry React Online di renderer existing; runtime Docker terpisah.
**Tech Stack:** Python/FastAPI/SQLite, Supertonic ONNX, React/Vite, Docker.
**Spec:** permintaan pemilik dalam sesi ini; temuan sumber di audit.md.

## Constraints

Tidak clone, commit, push, version bump, hapus data/lisensi atau framework baru.
Pertahankan kontrak `/generate` dan MCP; satu engine lokal, bahasa default id.
Autentikasi wajib termasuk audio dan MCP; cookie memakai CSRF bawaan.

## Tasks

- [x] Audit Git, manifest, graf dependensi, deployment dan model; audit.md.
- [ ] Tambah regression test server: key wajib, auth loopback/proxy, input
  kosong/panjang, engine terlarang, model error, audio path dan persistence.
- [ ] Tambah composition root `backend/online.py`, reuse router generation,
  auth/session, model licence dan MCP; bounded body/concurrency, lifecycle.
- [ ] Entry `electron/src/renderer/src/online/` memakai i18n/style/komponen
  existing; tampilkan preset, teks, speed, generate, player dan download.
- [ ] Runtime requirements dengan lock tersendiri; build web tanpa Electron;
  Docker non-root/volume/health/log limits/loopback Compose dan env example.
- [ ] Validasi dependency install, frontend build, backend auth/API/MCP,
  inference dua teks Indonesia dan pengukuran; catat gate yang belum jalan.
- [ ] README instalasi/HTTPS/API/MCP/update/backup/restore/licensing dan hasil.

## Review focus

Proxy loopback tidak boleh bypass key; audio dan MCP harus tetap terlindung.
Body chunked tidak boleh bypass limit. Cancel/overload tidak menambah model.
Model tidak boleh mengunduh saat idle; penerimaan lisensi tidak otomatis.
Sumber opsional tetap di repository sampai dependensinya terbukti terpisah.

## Execution ledger

Pemilik telah menginstruksikan lanjut implementasi tanpa konfirmasi kecil;
implementasi dilakukan langsung, tanpa commit/push. Docker daemon belum aktif.
