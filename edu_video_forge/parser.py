"""Parse Markdown or JSON scripts into scene lists."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict, Any


def parse_script(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        import json
        return json.loads(text)

    # Markdown parser
    scenes = []
    current = None
    for line in text.splitlines():
        if line.startswith("## Scene:"):
            if current:
                scenes.append(current)
            scene_type = line.split(":", 1)[1].strip().lower()
            current = {"type": scene_type, "narration": "", "content": ""}
        elif current is not None:
            if line.startswith("**Narration:**"):
                current["narration"] = line.split("**Narration:**", 1)[1].strip()
            elif line.startswith("**Content:**"):
                # content follows until next section or end
                pass
            else:
                if current["content"] or not line.startswith("**"):
                    current["content"] += line + "\n"
    if current:
        scenes.append(current)

    # Clean content
    for s in scenes:
        s["content"] = s["content"].strip()
        # Extract code blocks
        if "```" in s["content"]:
            m = re.search(r"```(?:python)?\n(.*?)```", s["content"], re.DOTALL)
            if m:
                s["content"] = m.group(1).strip()

    return scenes or [{"type": "chalkboard", "narration": text[:200], "content": text}]
