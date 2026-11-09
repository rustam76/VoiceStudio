# Long narration implementation plan

Goal: render Indonesian/English narration of about 30 minutes on the hosted CPU
studio using the existing Stories cache/resume pipeline. No new model or service.

The reported restart does not prove OOM; VPS kernel/container events are still
needed to identify that particular death. Independently, current OpenVoice calls
convert an entire utterance at once, whole Stories chapters collect all audio in
RAM, and the Clone UI uses a silent HTTP request until synthesis finishes.

- [x] Bound CPU text calls to 240 characters and OpenVoice conversion windows to
  8 seconds; reuse one target embedding during each conversion.
- [x] Split oversized hosted Stories chapters into small deterministic parts
  (960 text characters and 20 seconds of explicit silence), preserving cast,
  speed, emotion and pauses. Reuse existing disk caches and resume manifests.
- [x] Use existing NDJSON keepalives for browser Generate without automatically
  playing preview PCM. Keep the canonical saved WAV, cancellation and deadline.
- [x] Reproduce limits with tests, verify a 30-minute synthetic timeline using
  a stub inference engine and actual WAV/mux processing, and run a real short
  cloning smoke test. Do not claim a 30-minute real inference benchmark on the VPS.
- [x] Review, document deployment/long-form use, commit and push the tested fix.

Constraints: keep authentication/CSRF, explicit offline model loading, final
mark_synthetic, English/Indonesian only, Stories and REST API, existing versions
and data. No blind increase of the 4 GiB limit on a host reporting only 2.2 GiB free.

Validation: 132 targeted backend tests and all 2,101 frontend tests passed.
Web build, locale checks and TypeScript passed. Real OpenVoice conversion
completed a 19-second waveform across three windows. The 30-minute timeline
uses stub inference with actual cached WAVs and ffmpeg; full VPS model
inference and its restart cause remain unverified.
