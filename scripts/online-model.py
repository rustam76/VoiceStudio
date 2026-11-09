"""Explicitly prepare the pinned Supertonic model in the server's own cache."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cloning", action="store_true", help="Also install the MIT-licensed OpenVoice V2 converter")
    args = parser.parse_args()
    from engines.supertonic3.constants import MODEL_REPO_ID, PINNED_REVISION_SHA
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id=MODEL_REPO_ID, revision=PINNED_REVISION_SHA,
                      allow_patterns=["onnx/*", "voice_styles/*", "config.json", "LICENSE", "README.md"])
    if args.cloning:
        from engines.openvoice_v2.converter import MODEL_REPO_ID, PINNED_REVISION_SHA, CONVERTER_FILES
        snapshot_download(repo_id=MODEL_REPO_ID, revision=PINNED_REVISION_SHA,
                          allow_patterns=[*CONVERTER_FILES, "README.md", "LICENSE*"])
    print("Model installed. Review and accept its licence in the Web UI before generation.")
