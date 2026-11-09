# Hosted narration scope

The Docker and development API select OMNIVOICE_STUDIO_LITE=1. This loads only
narration, profiles, Stories, history/export, model/settings/auth, events and
OpenAI-compatible speech routes. It excludes MCP, telephony, Cloud, capture ASR
and the performance-profile reconciliation task. Unrelated upstream source is
kept for updates but is not imported as a workspace at startup.

Languages: English and Indonesian. Supertonic provides the spoken source;
OpenVoice V2 conditions the converter on both the source audio's speaker
embedding and the uploaded target voice embedding. It needs no reference
transcript, ASR, VAD or MeloTTS. Final converted audio goes through the existing
mark_synthetic pipeline. A silent/invalid or >30-second reference fails clearly.
Use a clear 1–30 second reference from one speaker, preferably 5–15 seconds.

The converter loads only pinned local files; explicit installation is available
through Model Catalogue or `scripts/online-model.py --cloning`. Its MIT modules
are vendored from OpenVoice 74a1d147b17a8c3092dd5430504bd83ef6c7eb23;
weights are pinned at f36e7edfe1684461a8343844af60babc2efbb727.
See backend/engines/openvoice_v2/vendor/LICENSE. Upstream model terms:
https://huggingface.co/myshell-ai/OpenVoiceV2/blob/f36e7edfe1684461a8343844af60babc2efbb727/README.md

The native multilingual model files cannot be made smaller by hiding languages.
Savings come from excluding unrelated runtime dependency trees and loading the
32.8M-parameter converter only on the first cloning request. Preset narration
does not load it. Runtime uses a dedicated frozen lockfile; dev tests are separate.
Preserve the existing studio-data volume, auth/CSRF boundaries and version.

The sidebar reads only narration engine status. It does not poll diarisation,
dictation, translation, batch jobs or performance-profile selection. Legacy
diarisation status requests return an explicit disabled response in hosted mode;
a missing catalogue entry is treated as unavailable rather than raising.

## Long narration (about 30 minutes)

Use **Stories** for long narration. Hosted rendering divides chapters into
bounded parts (at most 960 spoken characters and 20 seconds of explicit pauses),
then saves each completed part and sentence to the existing disk cache. The
final MP3/M4B is assembled from those files with ffmpeg. If a render is
interrupted, use its existing Resume action; keep the studio-data volume and
cache. A browser disconnect can cancel active work; completed cached parts are
reused on resume.

CPU synthesis calls are limited to 240 characters. OpenVoice conversion uses
8-second windows with context, preserving the source sample count. Browser
Generate uses the existing NDJSON stream with 15-second keepalives and progress,
without playing or transmitting preview PCM. The final saved WAV and normal
playback settings remain in use. API clients can POST `stream=true` and
`preview_audio=false` to `/generate`; the final `done.audio_path` identifies the
saved WAV. OpenAI-compatible clients retain their existing response format.

Keep proxy response streaming enabled (no response buffering or compression
that holds keepalive bytes). These changes limit work size; they do not prove
the cause of a VPS/container restart or guarantee a completion time on its CPU.
After a backend restart, sign in again if the old session's WebSocket gets 403.
Do not disable authentication to resolve that response.

Validation: offline regression tests exercise a 1,800-second timeline using
stub inference, real WAV cache writes, cache reuse and a real ffmpeg MP3 mux.
This is not a 30-minute model benchmark. A real 19-second OpenVoice conversion
across three windows also passed locally (about 978 MiB process peak RSS on the
test Mac); total VPS/container memory, output quality and CPU speed still need
measurement with the user's full script.
