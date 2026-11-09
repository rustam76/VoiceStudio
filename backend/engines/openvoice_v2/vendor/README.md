# OpenVoice converter modules

Vendored from myshell-ai/OpenVoice, commit
`74a1d147b17a8c3092dd5430504bd83ef6c7eb23` (MIT).
Only the acoustic model modules are included. Imports were made relative.
No ASR, base TTS, text frontend, web demo or download-at-import code is used.
`../converter.py` adapts the upstream ToneColorConverter operations and STFT
without its language-processing dependencies. Keep the accompanying LICENSE.
