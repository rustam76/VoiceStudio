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
