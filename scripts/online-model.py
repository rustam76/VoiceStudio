"""Explicitly prepare the pinned Supertonic model in the server's own cache."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

if __name__ == "__main__":
    from engines.supertonic3.constants import MODEL_REPO_ID, PINNED_REVISION_SHA
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id=MODEL_REPO_ID, revision=PINNED_REVISION_SHA,
                      allow_patterns=["onnx/*", "voice_styles/*", "config.json", "LICENSE", "README.md"])
    print("Model installed. Review and accept its licence in the Web UI before generation.")
