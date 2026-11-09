# VoiceStudio Web

Studio web untuk narasi YouTube: bahasa Indonesia dan Inggris, voice cloning,
profil suara, Stories beberapa karakter, riwayat, pemutar/unduh, dan REST API.
Workflow, panggilan, dubbing/video, transkripsi, penerjemah, LLM dan Cloud tidak
aktif pada deployment ini. Aplikasi desktop/mobile tidak disertakan.

Narasi memakai Supertonic-3 (OpenRAIL-M); cloning memakai konverter tone colour
OpenVoice V2 (MIT). Keduanya berjalan di CPU. OpenVoice mengubah warna suara,
bukan menjamin menyalin seluruh aksen/emosi; hasil Indonesia perlu didengarkan.
Model multilingual tetap utuh, meskipun pilihan bahasa dibatasi ke dua bahasa.

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
```

Buka web dan login dengan kunci yang sama. Backend dijalankan dalam server mode,
sehingga admin API tetap membutuhkan autentikasi. Cookie memakai CSRF bawaan.
API: `/docs`, `/openapi.json`, `/generate`, `/history`, dan `/v1/audio/speech`.
MCP tidak dimuat; integrasi audio menggunakan REST API.
Klien API memakai `Authorization: Bearer <OMNIVOICE_API_KEY>`.

Engine awal tetap Supertonic-3. Pada deployment lama, cache model serta database
menggunakan volume `studio-data:/data` yang sama: tidak perlu menghapus volume.
Untuk menyiapkan model secara eksplisit dari Terminal service `studio`:

```sh
HF_HUB_OFFLINE=0 python /app/scripts/online-model.py --cloning
```

Baca dan terima lisensi Supertonic di UI sebelum generate. Unduhan model
merupakan tindakan eksplisit; startup dan cloning hanya membaca cache lokal.
OpenVoice V2 memakai sekitar 131 MB tambahan, di luar model Supertonic.
Gunakan rekaman suara milik sendiri atau yang izinnya mencakup pemakaian ini.
Untuk YouTube monetisasi: OpenVoice V2 mengizinkan penggunaan komersial;
Supertonic tetap tunduk pada OpenRAIL-M, termasuk pengungkapan suara sintetis.
OmniVoice tidak disediakan karena bobotnya berlisensi nonkomersial.

Image menggunakan lockfile khusus `deploy/online/uv.lock`, tanpa WhisperX,
Demucs, Gradio, penerjemah, LLM/MCP dan paket pelatihan. PyTorch CPU tetap
perlu untuk konverter dan provenance. Batas awal Compose 2 CPU/4 GiB perlu
disesuaikan berdasarkan panjang audio dan RAM VPS. Background ASR, pemindaian
profil performa dan Cloud dihentikan; hasil akhir tetap melalui mark_synthetic.

Contoh integrasi (ID profil diperoleh dari `GET /profiles` setelah unggah suara):

```sh
curl -X POST "$VOICE_URL/generate" \
  -H "Authorization: Bearer $VOICE_API_KEY" \
  -F 'text=Halo, selamat datang di channel saya.' \
  -F 'language=Indonesian' -F "profile_id=$VOICE_PROFILE_ID"
```

Respons memuat lokasi audio; rincian parameter tersedia di `/docs`.

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
  uv run --project deploy/online --group dev python -m pytest tests/test_docker_entrypoint.py -q
```

`setup:api` memakai lockfile runtime khusus di `deploy/online/`. `dev:api`
menyalakan scope studio ringan yang sama dengan Docker. Test tooling memakai
grup `dev` terpisah, bukan dependency image produksi.

## Update, backup dan restore

Backup sebelum mengganti image. Pertahankan service `studio`, volume
`studio-data` dan mount `/data`. Jangan gunakan `docker compose down -v`.
Update melalui `docker compose build && docker compose up -d`, lalu periksa
`docker compose logs --tail 100 studio` dan `/health`. Simpan backup database
dan image sebelumnya untuk rollback; jangan menimpa database dengan versi
lama setelah migrasi tanpa restore backup yang sesuai.

Upstream bisa diperbarui secara selektif; jangan mengembalikan runtime native
atau menimpa konfigurasi hosting secara otomatis. Tes hosting menjaga entry
aplikasi web dan menolak folder desktop/mobile.
