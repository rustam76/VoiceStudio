# VoiceStudio Online — audit awal, 1 November 2026

## Kondisi sumber

Checkout lokal VoiceStudio 0.5.7, AGPL-3.0-only; tidak dilakukan clone.
`git status --short` kosong, branch awal `main`; sesudah fetch,
`git rev-list --left-right --count main...origin/main` = `0 0`.
Pekerjaan di `feat/voicestudio-online`; tidak ada commit/push otomatis.
Ukuran awal `du -sh`: checkout 312 MiB termasuk `.git` 195 MiB;
`electron` 29 MiB, `mobile` 12 MiB, `backend` 26 MiB.
Tidak ada node_modules atau .venv lokal. Docker CLI tersedia tetapi daemon
belum berjalan. Baseline runtime/image upstream belum dapat diukur.

## Peta dependensi yang diperiksa

| Bagian | Sumber dan hubungan |
|---|---|
| Build JS | package.json + bun.lock, workspace electron |
| Web | electron/vite.web.config.ts → electron/src/renderer → frontend/dist |
| Desktop | electron/src/main + preload, electron-vite, electron-builder, native |
| Bridge | renderer memakai bridge opsional; web punya HTTP client dan WebAuthGate |
| Shared | electron/src/shared: routing HTTP, auth session, komponen, bahasa; dipertahankan |
| Backend | backend/main.py: FastAPI, fan-out puluhan router dan warmup ASR/TTS/watermark |
| TTS | api/routers/generation.py → services/tts_backend.py + model_manager.py |
| Inferensi | registry backend, lazy import SDK, eviction single-engine, guarded executor |
| Supertonic | engines/supertonic3/backend.py → long-lived subprocess → sidecar.py |
| Model | config/models.yaml, model_licenses.json, model_acceptance.py, settings_store.py |
| MCP | mcp_server.py → in-process HTTP /generate; Streamable HTTP /mcp; stdio juga tersedia |
| Audio/data | generation_audio.py, audio_io.py, watermark.mark_synthetic_async; SQLite + outputs/voices dalam OMNIVOICE_DATA_DIR |
| Mobile | mobile/ios, mobile/android, mobile/contract; tidak diperlukan server |
| Deploy lama | deploy/Dockerfile menggunakan CUDA base bahkan pada profile Compose cpu; memasang semua dependensi pyproject |

Eksplorasi memakai graph fast/Tier 2 dan pembacaan sumber langsung. Coverage
path inti tidak mencatat gap; ini bukan bukti bahwa semua import dinamis telah
terpetakan. Konfigurasi dan manifest diperiksa langsung.

## Keputusan sebelum penghapusan

1. Reuse router `/generate`, history, autentikasi/session, penyimpanan SQLite,
   watermark chokepoint, engine Supertonic dan MCP yang ada. Composition root
   server terpisah diperlukan karena main.py mengimpor router opsional dan
   menyalakan layanan yang tidak diperlukan narasi.
2. Reuse React, Vite, komponen/style/i18n renderer. Entry khusus Online
   menghindari navigasi ke clone/dub/dictation/setup desktop.
3. Pisahkan dependensi runtime dan build Online, tanpa Redis/Celery/framework
   baru. Satu worker Uvicorn dan satu inference slot; overload ditolak.
4. Desktop/mobile/engine opsional dikeluarkan dari jalur deployment. Sumbernya
   tidak dihapus secara massal sebelum validasi import dan build; tidak ada
   database, model, lisensi, atribusi atau feed updater yang dihapus.

## Evaluasi model

- **Supertonic-3 dipilih**: adapter bawaan CPU ONNX, 99M parameter, sekitar
  400 MB menurut SDK; tujuh preset yang sudah diekspos adapter. Model card
  secara eksplisit mencantumkan `id`. SDK MIT, bobot OpenRAIL-M dengan
  pembatasan penggunaan. Gate persetujuan upstream tetap berlaku.
- OmniVoice bawaan: catalog sekitar 2.4 GiB; bobot CC-BY-NC dan tokenizer
  dengan ketentuan Boson/Llama terpisah menurut LICENSE-NOTICE.md. Tidak
  dipilih untuk deployment CPU narasi yang mungkin dimonetisasi.
- KittenTTS bawaan: dokumentasi dependency menyebut English, tidak ada bukti
  dukungan Indonesia; tidak dipilih.
- Piper `id_ID/news_tts/medium`: model Indonesia tersedia, satu pembicara,
  22050 Hz; model card hanya merujuk URL dataset untuk lisensi. Kepastian
  hak dataset/model kurang dari kandidat yang sudah terintegrasi.
- Engine lain tetap opsional di sumber; tidak dipasang seluruhnya untuk
  mengejar multilingual tanpa bukti Indonesia.

Sumber primer (diperiksa 2026-11-01):
- https://huggingface.co/Supertone/supertonic-3
- https://pypi.org/project/supertonic/1.3.1/
- https://huggingface.co/Supertone/supertonic-3/blob/main/LICENSE
- https://huggingface.co/rhasspy/piper-voices/blob/main/id/id_ID/news_tts/medium/MODEL_CARD

Belum ada klaim kualitas, penghematan RAM, atau hak komersial tanpa syarat.
Pelafalan angka/istilah campuran dan kualitas narasi perlu uji audio aktual.
