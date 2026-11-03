# VoiceStudio Online

Fork pribadi [VoiceStudio](https://github.com/debpalash/VoiceStudio) untuk narasi Indonesia melalui browser, API, dan MCP. Inferensi berjalan lokal di server tanpa API TTS berbayar. Target deployment aktif: **Linux + Docker**, satu worker dan satu engine CPU. Dokumentasi asli: [README.upstream.md](README.upstream.md).

Memakai ulang router `/generate`, engine Supertonic, SQLite/audio, autentikasi, komponen React dan MCP upstream. Versi tetap mengikuti package.json, tanpa version bump.

## Fitur dan batas scope

- Teks Indonesia, tujuh preset suara, kecepatan 0,7–2×, player/preview, unduhan WAV 44,1 kHz, history.
- Maksimum 6.000 karakter/request; lazy loading, satu inferensi aktif, HTTP 429 saat sibuk, engine dilepas setelah idle sekitar lima menit.
- API dan MCP Streamable HTTP `/mcp`; model, settings/SQLite dan audio dalam volume persisten.
- Key wajib termasuk loopback/proxy, audio dan MCP; browser memakai sesi HttpOnly + CSRF, key tidak disimpan di localStorage.

Voice cloning/design, dubbing/video, STT/transkripsi, pemisahan audio, gallery, cloud/account, dictation, installer dan updater desktop dinonaktifkan di jalur Online. UI tidak menampilkan kontrolnya. Sumber desktop/mobile/engine opsional dipertahankan sebagai referensi, bukan toolchain/runtime deployment. Workflow lama di `.github/workflows/upstream/` tidak dijalankan GitHub Actions. Lisensi, copyright dan atribusi tetap ada.

## Model dan lisensi

**Supertonic-3**, SDK 1.3.1; revision `724fb5abbf5502583fb520898d45929e62f02c0b`, CPU ONNX, sekitar 99M parameter. [Model card](https://huggingface.co/Supertone/supertonic-3) secara eksplisit mencantumkan bahasa Indonesia (`id`). Cache unduhan terukur sekitar **383 MiB**. Preset adapter: M1, M3, M4, M5, F3, F4, F5.

SDK MIT; bobot/aset model **OpenRAIL-M dengan pembatasan penggunaan**, termasuk pengungkapan konten yang dihasilkan mesin. Tidak ada larangan umum narasi komersial dalam teks yang diperiksa, tetapi bukan izin tanpa syarat untuk setiap konten/penggunaan. Baca [audit lisensi](docs/online/licensing.md) dan terima ketentuan di UI. Pengunduhan tidak otomatis menerima lisensi. Aplikasi tetap AGPL-3.0-only: bila dipakai pihak lain melalui jaringan, sediakan corresponding source fork yang sebenarnya, bukan hanya link upstream.

Teks tidak diterjemahkan otomatis. Angka dan istilah dipertahankan; normalisasi agresif dimatikan. Kualitas pelafalan/intonasi/angka/istilah campuran harus dinilai dengan mendengarkan sendiri; WAV valid bukan bukti kualitas narasi. Lihat [audit](docs/online/audit.md), [inventaris model](docs/online/models.md), dan [hasil validasi](docs/online/validation.md).

## Persyaratan VPS

Docker Engine + Compose v2, CPU Linux x86_64/ARM64, ruang untuk image/model/audio. Compose membatasi 2 CPU dan 4 GiB RAM sebagai konfigurasi awal, **bukan minimum terukur** atau jaminan untuk setiap VPS. Tidak perlu GPU/CUDA. Image ARM64 diuji lokal; workflow CI membangun x86_64, periksa hasil CI sebelum deployment arsitektur yang belum diuji. WAV mono 16-bit 44,1 kHz sekitar 5 MiB/menit; pantau volume/retention. Dua thread adalah awal konservatif, bukan hasil tuning universal.

## Instalasi Docker

Gunakan checkout ini; tidak perlu clone ulang.

```bash
cp .env.example .env
chmod 600 .env
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
# Masukkan hasil sebagai OMNIVOICE_API_KEY dalam .env. Jangan commit .env.
docker compose build
docker compose up -d
docker compose ps
docker compose exec studio python scripts/online-model.py
```

Buka **http://localhost:3900**, login dengan key, baca/terima lisensi, masukkan teks lalu Generate. Model tidak diunduh saat startup/idle; perintah terakhir adalah aksi unduh eksplisit. Setelah unduhan, inferensi memakai cache lokal tanpa jaringan. Sesi browser kedaluwarsa dan hilang saat server restart; login ulang bila diminta.

Untuk akses VPS sebelum domain siap:

```bash
ssh -L 3900:127.0.0.1:3900 user@vps
```

Backend hanya dipublikasikan ke `127.0.0.1:3900`. Image tidak membawa model/secret; proses UID 10001, volume baru disiapkan untuk UID tersebut. Jangan mengganti binding menjadi publik tanpa kontrol akses.

## Domain dan HTTPS

Contoh Caddy pada host yang sama:

```caddyfile
voice.example.com {
    request_body {
        max_size 64KB
    }
    reverse_proxy 127.0.0.1:3900
}
```

Ubah `.env` sesuai domain nyata, lalu `docker compose up -d`:

```dotenv
VOICESTUDIO_PUBLIC_URL=https://voice.example.com
OMNIVOICE_ALLOWED_HOSTS=voice.example.com
OMNIVOICE_ALLOWED_ORIGINS=https://voice.example.com
OMNIVOICE_MCP_ALLOWED_HOSTS=voice.example.com
```

Proxy harus meneruskan Host dan `X-Forwarded-Proto: https`; jangan mencatat Authorization/Cookie/body. Timeout upstream harus cukup untuk narasi panjang (misalnya 600 detik pada nginx). MCP memakai Streamable HTTP, bukan WebSocket. Hindari wildcard allowlist. Bila proxy dalam container lain, gunakan jaringan Compose yang sama, target `studio:3900`, dan hapus `ports`. Jangan membuka MCP tanpa autentikasi.

## API

`/docs` dan `/openapi.json` tersedia setelah autentikasi. Header: **`Authorization: Bearer <OMNIVOICE_API_KEY>`**.

| Endpoint | Fungsi |
|---|---|
| GET /health | Liveness publik tanpa memuat model |
| GET /engines | Engine aktif dan preset |
| GET /languages | Bahasa default yang diekspos UI |
| POST /generate | Form/multipart; WAV + history |
| GET /history | Audio hasil yang masih ada |
| GET /audio/{id}.wav | WAV autentikasi; id dari X-Audio-Id/history |
| GET /audio/{id}.ogg atau .opus | Encoding FFmpeg opsional |
| GET /models/licenses/acceptance/Supertone/supertonic-3 | Fingerprint/status lisensi |
| POST /models/licenses/accept | Terima fingerprint yang sudah dibaca |
| POST /api/auth/session | Tukar bearer key menjadi sesi cookie/bearer |

Contoh dengan key dari environment shell Anda:

```bash
curl --fail-with-body http://127.0.0.1:3900/generate \
  -H "Authorization: Bearer $OMNIVOICE_API_KEY" \
  --form-string 'text=Halo semuanya! Selamat datang di channel kami.' \
  -F language=id -F engine=supertonic3 -F preset_voice=M1 \
  -F speed=1.0 -F num_step=8 -F effect_preset=raw \
  -F postprocess_output=false -o narasi.wav
```

Bahasa default `id`, steps dibatasi adapter ke 5–12. Chunk 100–1.000 karakter, default 800. Total jeda eksplisit maksimal 30 detik; input hanya jeda ditolak. Empty/panjang HTTP 422; body >64 KiB HTTP 413; sibuk HTTP 429; lisensi belum diterima HTTP 403. Referensi audio/profile/instruct cloning ditolak di Online.

## MCP

Klien Codex/agent menggunakan **Streamable HTTP** `https://voice.example.com/mcp` dengan header bearer yang sama. Simpan key di environment/config rahasia klien; format konfigurasi klien berbeda-beda, ikuti dokumentasinya.

Tool aktif: `generate_speech`, `list_voices`, `list_languages`, `check_health`. Parameter text/language/profile_id/instruct/speed/steps/format asli dipertahankan; profile_id/instruct ditolak pada Online. Parameter **opsional tambahan `preset_voice`** meneruskan preset engine bawaan (misalnya M1), agar agent dapat memilih suara seperti UI. Default bahasa id, suara M1, WAV.

Compose memakai output `files`: `audio_url`, audio_id, waktu dan durasi. Download URL dengan header bearer yang sama; URL tidak mengandung key dan tidak publik. `VOICESTUDIO_PUBLIC_URL` menentukan URL hasil, pemanggilan tool tetap in-process. Untuk byte langsung, ubah environment service `OMNIVOICE_MCP_OUTPUT_MODE=resources`. Stdio upstream tetap tersedia untuk integrasi lokal terpisah; deployment remote memakai `/mcp`, tanpa Electron.

## Update, backup, restore

Backup konsisten: hentikan service sebentar. Perintah ini tidak menghapus volume:

```bash
mkdir -p backups
docker compose stop studio
docker compose run --rm --no-deps -T studio \
  tar -C /data -czf - . > backups/studio-data.tar.gz
docker compose start studio
```

Backup berisi SQLite/settings, acceptance, model cache dan audio. Simpan `.env` terpisah dan terenkripsi. Uji restore ke volume **kosong** dahulu:

```bash
docker compose stop studio
docker compose run --rm --no-deps -T studio \
  tar -C /data -xzf - < backups/studio-data.tar.gz
docker compose up -d
```

Jangan mengekstrak di atas data baru yang belum dibackup. Data upstream lama tidak dipindah otomatis: salin backup ke `/data` dengan UID 10001; migrasi SQLite memakai jalur upstream yang sama.

Update: backup, fetch/review source fork, lalu `docker compose build && docker compose up -d`. Periksa `docker compose logs --tail 100 studio`. **Jangan gunakan `down -v`.** Model tetap ada. Simpan image sebelumnya untuk rollback; bila ada migrasi schema, gunakan backup yang sesuai, jangan menimpa database otomatis.

## Pengembangan lokal

```bash
uv sync --project deploy/online --frozen
bun install --frozen-lockfile --ignore-scripts
bun run build:web
export OMNIVOICE_API_KEY='<key-acak-Anda>'
export OMNIVOICE_DATA_DIR="$PWD/omnivoice_data"
export HF_HOME="$OMNIVOICE_DATA_DIR/huggingface"
deploy/online/.venv/bin/python scripts/online-model.py
PYTHONPATH=backend deploy/online/.venv/bin/python -m uvicorn online:app \
  --host 127.0.0.1 --port 3900 --workers 1 --no-access-log
```

HMR: backend di atas dan `VOICESTUDIO_ONLINE_BUILD=1 bun run --cwd electron dev:web` (port 3901). Aktifkan environment Online dahulu jika memakai `bun run dev:api`, yang memakai interpreter Python aktif. Lock mendukung Linux dan macOS ARM64 untuk pengembangan; deployment produk tetap Linux.

```bash
HF_HUB_OFFLINE=1 HF_HUB_CACHE=/tmp/online-empty-hf-cache \
  deploy/online/.venv/bin/python -m pytest tests/test_online.py -q
bun run typecheck
bun run test
```

Smoke model nyata: set OMNIVOICE_API_KEY dan VOICESTUDIO_TEST_URL, jalankan `scripts/online-smoke.py` dengan Python Online. Lisensi harus diterima di UI; hanya QA disposable boleh memakai `ONLINE_QA_ACCEPT_LICENSE=1` sesudah review ketentuan. Browser smoke: `node scripts/online-browser-smoke.mjs` dengan Playwright Chromium terpasang.

## Troubleshooting

- 401 setelah restart: login ulang; key tetap di .env, sesi di memori.
- 403 lisensi: baca lalu terima fingerprint saat ini di UI.
- Model belum ada: jalankan perintah `scripts/online-model.py` di container.
- Host/origin ditolak: cocokkan domain HTTPS dalam allowlist .env.
- 429: tunggu; jangan tambah worker karena menggandakan model di RAM.
- OOM/CPU tinggi: kurangi teks/thread dan ukur pada VPS Anda; 4 GiB bukan jaminan minimum.
- AudioSeal tidak terpasang: chokepoint `mark_synthetic` tetap dilalui, tetapi runtime minimal tidak memasang model watermark kedua. Jangan mengklaim watermark neural tersedia; ungkap narasi AI saat publikasi.
- Kualitas kurang sesuai: coba preset/speed lain, dengarkan angka, jeda dan istilah campuran. Jangan memasang semua engine sekaligus.
- Disk penuh: periksa volume/history/backup sebelum membersihkan audio, jangan menghapus database/model otomatis.

Tidak ada baseline runtime upstream yang sebanding; jangan mengartikan ukuran source/dependency sebagai penghematan RAM. [Laporan validasi](docs/online/validation.md) mencatat pengukuran dan pengujian yang belum selesai.
