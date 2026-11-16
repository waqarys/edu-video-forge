"""Main video generation pipeline."""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

import edge_tts
from rich.console import Console

from .parser import parse_script
from .renderers import render_scene

console = Console()


def generate_video(
    script_path: str | Path,
    output_path: str | Path,
    voice: str = "en-US-AriaNeural",
    theme: str = "chalkboard",
    quality: str = "medium",
    work_dir: str | Path | None = None,
) -> Path:
    """Generate a complete educational video from a script.

    Args:
        script_path: Path to Markdown or JSON script
        output_path: Final MP4 path
        voice: edge-tts voice name
        theme: visual theme (chalkboard, light, dark)
        quality: low / medium / high (affects Manim quality)
        work_dir: temporary working directory

    Returns:
        Path to the generated video
    """
    script_path = Path(script_path)
    output_path = Path(output_path)
    work_dir = Path(work_dir or output_path.parent / f"{output_path.stem}_work")
    work_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold green]Parsing[/bold green] {script_path}")
    scenes = parse_script(script_path)

    audio_files = []
    video_clips = []
    srt_segments = []
    current_time = 0.0

    for i, scene in enumerate(scenes):
        console.print(f"[bold]Scene {i+1}/{len(scenes)}[/bold]: {scene['type']}")
        # TTS
        audio_path = work_dir / f"scene_{i:03d}.mp3"
        srt_path = work_dir / f"scene_{i:03d}.srt"
        asyncio.run(_generate_tts(scene["narration"], voice, audio_path, srt_path))
        audio_files.append(audio_path)

        # Duration from audio
        duration = _get_audio_duration(audio_path)
        scene["duration"] = duration

        # Render visual
        clip_path = work_dir / f"scene_{i:03d}.mp4"
        render_scene(scene, clip_path, theme=theme, quality=quality, work_dir=work_dir)
        video_clips.append(clip_path)

        # Collect SRT with offset
        if srt_path.exists():
            srt_segments.append((srt_path, current_time))
        current_time += duration

    # Compose final video
    console.print("[bold green]Composing final video...[/bold green]")
    _compose_video(video_clips, audio_files, output_path, work_dir)

    # Optional: merge SRT
    if srt_segments:
        final_srt = output_path.with_suffix(".srt")
        _merge_srts(srt_segments, final_srt)

    console.print(f"[bold green]Done![/bold green] Video saved to {output_path}")
    return output_path


async def _generate_tts(text: str, voice: str, audio_path: Path, srt_path: Path):
    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()
    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(submaker.get_srt())


def _get_audio_duration(path: Path) -> float:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, check=True
        )
        return float(result.stdout.strip())
    except Exception:
        return 5.0  # fallback


def _compose_video(videos: List[Path], audios: List[Path], output: Path, work_dir: Path):
    # Simple concatenation approach using ffmpeg concat demuxer + audio mux
    # For production: more sophisticated with transitions
    concat_file = work_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for v in videos:
            f.write(f"file '{v.resolve()}'\n")

    temp_video = work_dir / "temp_video.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c", "copy", str(temp_video)
    ], check=True, capture_output=True)

    # Mux first audio for now (extend later for multi-audio)
    if audios:
        subprocess.run([
            "ffmpeg", "-y", "-i", str(temp_video), "-i", str(audios[0]),
            "-c:v", "copy", "-c:a", "aac", "-shortest", str(output)
        ], check=True, capture_output=True)
    else:
        temp_video.rename(output)


def _merge_srts(segments: List[tuple], output: Path):
    # Placeholder – implement full SRT merge with time offsets
    with open(output, "w") as f:
        f.write("1\n00:00:00,000 --> 00:00:05,000\nSubtitles placeholder\n")
