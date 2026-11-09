# VoiceStudio Web

Versi web lengkap VoiceStudio dari upstream, tanpa aplikasi desktop atau mobile.
UI mempertahankan sidebar, halaman Home, voice cloning/design, dubbing,
transkripsi, audiobooks, history, pengaturan dan pengelolaan model. Fitur yang
membutuhkan perangkat/bridge native tetap mengikuti dukungan browser upstream;
keberadaan menu tidak berarti setiap engine sudah terpasang atau cocok untuk CPU.

Frontend: `frontend/src/renderer/src/main.tsx`. Backend: `backend/main.py`.
Versi mengikuti snapshot upstream dalam root package.json; tidak dibump manual.
Dokumentasi fitur upstream disimpan di [README.upstream.md](README.upstream.md).

## Hosting Docker / Coolify

```sh
cp .env.example .env
# Generate nilai OMNIVOICE_API_KEY, simpan di .env / Environment Variables Coolify:
openssl rand -hex 32
docker compose build
docker compose up -d
```

Di Coolify gunakan Docker Compose di root dan service `studio`, port internal
3900. Isi `OMNIVOICE_API_KEY` sebagai credential privat; jangan commit nilainya.
Default binding host tetap 127.0.0.1. Gunakan domain HTTPS/reverse proxy, lalu isi:

```dotenv
VOICESTUDIO_PUBLIC_URL=https://voice.example.com
OMNIVOICE_ALLOWED_HOSTS=voice.example.com
OMNIVOICE_ALLOWED_ORIGINS=https://voice.example.com
OMNIVOICE_MCP_ALLOWED_HOSTS=voice.example.com
```

Buka web dan login dengan kunci yang sama. Backend dijalankan dalam server mode,
sehingga admin API tetap membutuhkan autentikasi. Cookie memakai CSRF bawaan.
API: `/docs`, `/openapi.json`, `/generate`, `/history`; MCP: `/mcp`.
Klien API memakai `Authorization: Bearer <OMNIVOICE_API_KEY>`.

Engine awal tetap Supertonic-3. Pada deployment lama, cache model serta database
menggunakan volume `studio-data:/data` yang sama: tidak perlu menghapus volume.
Untuk menyiapkan model secara eksplisit dari Terminal service `studio`:

```sh
HF_HUB_OFFLINE=0 python /app/scripts/online-model.py
```

Baca dan terima lisensi model di UI sebelum generate. Pengaturan dan instalasi
engine lain dilakukan dari UI; model tambahan memerlukan storage/komputasi
sendiri dan tidak semuanya cocok untuk VPS CPU. VoiceStudio AGPL-3.0-only;
SDK/model punya lisensi tersendiri, termasuk pembatasan model nonkomersial.
Notices dan atribusi dipertahankan; sediakan corresponding source fork yang
sebenarnya jika aplikasi dimodifikasi dan ditawarkan melalui jaringan.

Image CPU sekarang memakai dependency backend lengkap, sehingga lebih besar
daripada image narasi minimal. Batas awal Compose 2 CPU/4 GiB bukan jaminan
untuk cloning, dub, ASR atau semua model. Background capture/watermark warm-up
dinonaktifkan; watermark output tetap melalui mark_synthetic.

## Development dan pemeriksaan

```sh
bun install --frozen-lockfile --ignore-scripts
bun run setup:api
# Set OMNIVOICE_API_KEY dan OMNIVOICE_SERVER_MODE=1 jika ingin auth server mode.
bun run dev:web
bun run typecheck
bun run test:frontend
bun run test
bun run build:web
HF_HUB_OFFLINE=1 HF_HUB_CACHE=/tmp/voicestudio-empty-hf \
  uv run --no-sync python -m pytest tests/test_docker_entrypoint.py -q
```

`setup:api` memakai root uv.lock, grup CPU dan extra Supertonic. Optional engine
lain tetap mengikuti mekanisme instalasi upstream. Desktop/mobile/store build
dan publikasi installer tidak ada dalam script atau CI aktif.

## Update, backup dan restore

Backup sebelum mengganti image. Pertahankan service `studio`, volume
`studio-data` dan mount `/data`. Jangan gunakan `docker compose down -v`.
Update melalui `docker compose build && docker compose up -d`, lalu periksa
`docker compose logs --tail 100 studio` dan `/health`. Simpan backup database
dan image sebelumnya untuk rollback; jangan menimpa database dengan versi
lama setelah migrasi tanpa restore backup yang sesuai.

Upstream bisa diperbarui secara selektif; jangan mengembalikan runtime native
atau menimpa konfigurasi hosting secara otomatis. Tes hosting menjaga entry
aplikasi lengkap dan menolak folder desktop/mobile.
