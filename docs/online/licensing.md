# Lisensi dan atribusi

Audit menggunakan sumber lokal dan dokumen primer model pada revision
`724fb5abbf5502583fb520898d45929e62f02c0b`; diperiksa 2026-11-01.

| Komponen | Ketentuan |
|---|---|
| VoiceStudio dan perubahan fork | AGPL-3.0-only; LICENSE dan LICENSE-NOTICE.md dipertahankan |
| Adaptasi UI T3 Code | MIT; electron/T3CODE-LICENSE.txt dipertahankan |
| Kode omnivoice/ upstream | Apache-2.0 terpisah; tidak otomatis melisensikan bobot |
| Supertonic SDK 1.3.1 | MIT; paket PyPI upstream |
| Bobot/config/tokenizer karakter/preset Supertonic-3 | OpenRAIL-M yang menyertai snapshot; tidak direlisensikan oleh fork |
| Data training Supertonic | Tidak diberikan lisensinya oleh OpenRAIL-M; tidak disertakan di image |
| PyTorch/torchaudio, ONNX Runtime | Lisensi paket upstream masing-masing; CPU wheels, tanpa CUDA |
| Komponen Python/JS lain | Tetap membawa lisensi distribusinya; versi dicatat dalam dua lockfile |
| FFmpeg Debian | Distribusi Debian membawa ketentuan build/codec sendiri; bukan bagian dari lisensi model |

Teks lengkap lisensi bobot yang diperiksa disimpan di
[`deploy/online/licenses/SUPERTONIC-MODEL-LICENSE.txt`](../../deploy/online/licenses/SUPERTONIC-MODEL-LICENSE.txt).
[Sumber model](https://huggingface.co/Supertone/supertonic-3),
[lisensi pada revision runtime](https://huggingface.co/Supertone/supertonic-3/blob/724fb5abbf5502583fb520898d45929e62f02c0b/LICENSE),
[SDK](https://pypi.org/project/supertonic/1.3.1/).

OpenRAIL-M memberikan grant tanpa royalti, dengan pembatasan penggunaan.
Tidak ada larangan umum terhadap narasi komersial dalam teks yang diperiksa;
ini bukan izin tanpa syarat untuk setiap teks, suara, atau penggunaan.
Pasal 4–6 dan Attachment A tetap berlaku, termasuk larangan peniruan tanpa
persetujuan, konten merugikan tertentu, dan kewajiban mengungkap konten yang
dihasilkan mesin. Nyatakan bahwa narasi dibuat dengan AI saat mempublikasikan.
Jika layanan diberikan kepada pihak lain, ketentuan penggunaan dan penyampaian
lisensi model juga berlaku. Tidak ada pembayaran per request pada jalur lokal.

Gate penerimaan upstream tetap aktif dan terikat fingerprint: operator
membaca lalu menerima di UI. Unduh model tidak otomatis menerima lisensi.
Tidak ada voice cloning atau Voice Builder berbayar yang diperlukan.
Preset publik yang disertakan snapshot digunakan sebagaimana didistribusikan
upstream; tidak ada dataset atau persetujuan identitas pembicara tambahan yang
diklaim oleh fork.

Default OmniVoice tidak digunakan: LICENSE-NOTICE.md mencatat bobot CC-BY-NC
dan tokenizer Boson/Llama dengan syarat terpisah. Piper Indonesia tersedia,
tetapi card news_tts merujuk lisensi dataset ke URL eksternal tanpa grant
yang cukup jelas dalam card; tidak dipilih. KittenTTS yang dibundel adalah
English, bukan bukti dukungan Indonesia.

Jika fork yang dimodifikasi dipakai orang lain melalui jaringan, tawarkan
corresponding source fork yang sebenarnya di bawah AGPL, termasuk perubahan,
lockfile dan instruksi build. Link upstream saja tidak menggantikan kewajiban
ini. Jangan sertakan .env, database, audio pengguna atau model cache dalam
source offer. README.upstream.md menyimpan dokumentasi asli, bukan target
deployment yang aktif.
