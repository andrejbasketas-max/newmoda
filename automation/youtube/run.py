"""Make and post one Short: write the script, render the video, upload, record it in history.json.

    python run.py              # full run
    python run.py --no-upload  # render to out/ only
"""

import json
import sys
from datetime import date
from pathlib import Path

from make_video import make_video
from write_script import write_script

HERE = Path(__file__).parent
HISTORY = HERE / "history.json"


def main() -> None:
    history = json.loads(HISTORY.read_text()) if HISTORY.exists() else []
    script = write_script([h["title"] for h in history[-40:]])
    print(json.dumps(script, indent=2, ensure_ascii=False))

    out_dir = HERE / "out" / date.today().isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False))
    video = make_video(script, out_dir)
    print(f"Rendered {video}")

    if "--no-upload" in sys.argv:
        return
    from upload import upload

    video_id = upload(video, script)
    print(f"Uploaded https://youtube.com/shorts/{video_id}")
    history.append({"date": date.today().isoformat(), "id": video_id,
                    "scent": script["scent"], "title": script["title"]})
    HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
