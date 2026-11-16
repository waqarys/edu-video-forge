"""Main video generation pipeline."""
from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple

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
    bg_music: str | Path | None = None,
    add_chapters: bool = True,
) -> Path:
    """Generate a complete educational video from a script."""
    script_path = Path(script_path)
    output_path = Path(output_path)
    work_dir = Path(work_dir or output_path.parent / f"{output_path.stem}_work")
    work_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold green]Parsing[/bold green] {script_path}")
    scenes = parse_script(script_path)

    audio_files: List[Path] = []
    video_clips: List[Path] = []
    srt_segments: List[Tuple[Path, float]] = []
    chapter_info: List[Tuple[float, str]] = []  # (start_time, title)
    current_time = 0.0

    for i, scene in enumerate(scenes):
        scene_type = scene.get("type", "unknown")
        console.print(f"[bold]Scene {i+1}/{len(scenes)}[/bold]: {scene_type}")
        audio_path = work_dir / f"scene_{i:03d}.mp3"
        srt_path = work_dir / f"scene_{i:03d}.srt"
        asyncio.run(_generate_tts(scene.get("narration", ""), voice, audio_path, srt_path))
        audio_files.append(audio_path)

        duration = _get_audio_duration(audio_path)
        scene["duration"] = duration

        # Chapter title: first 60 chars of narration or type
        title = (scene.get("narration", "") or scene_type).strip()[:60]
        chapter_info.append((current_time, title or f"Scene {i+1}"))

        clip_path = work_dir / f"scene_{i:03d}.mp4"
        render_scene(scene, clip_path, theme=theme, quality=quality, work_dir=work_dir)
        video_clips.append(clip_path)

        if srt_path.exists():
            srt_segments.append((srt_path, current_time))
        current_time += duration

    console.print("[bold green]Composing final video...[/bold green]")
    temp_output = work_dir / "composed.mp4"
    _compose_video(video_clips, audio_files, temp_output, work_dir)

    # Optional background music
    if bg_music and Path(bg_music).exists():
        console.print("[bold]Mixing background music...[/bold]")
        mixed = work_dir / "mixed.mp4"
        _mix_bg_music(temp_output, Path(bg_music), mixed)
        temp_output = mixed

    # Chapter markers
    if add_chapters and chapter_info:
        console.print("[bold]Adding chapter markers...[/bold]")
        final_with_chapters = work_dir / "final_chapters.mp4"
        _add_chapters(temp_output, chapter_info, current_time, final_with_chapters)
        final_with_chapters.replace(output_path)
    else:
        temp_output.replace(output_path)

    if srt_segments:
        final_srt = output_path.with_suffix(".srt")
        _merge_srts(srt_segments, final_srt)

    console.print(f"[bold green]Done![/bold green] Video saved to {output_path}")
    return output_path


async def _generate_tts(text: str, voice: str, audio_path: Path, srt_path: Path):
    if not text.strip():
        text = " "
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
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, check=True
        )
        return float(result.stdout.strip())
    except Exception:
        return 5.0


def _compose_video(videos: List[Path], audios: List[Path], output: Path, work_dir: Path):
    """Proper multi-scene composition: mux each video+audio then concat."""
    muxed = []
    for i, (v, a) in enumerate(zip(videos, audios)):
        muxed_path = work_dir / f"muxed_{i:03d}.mp4"
        # Mux video with its matching audio, trim/pad to audio length
        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(v),
            "-i", str(a),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(muxed_path)
        ], check=True, capture_output=True)
        muxed.append(muxed_path)

    concat_file = work_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for m in muxed:
            f.write(f"file '{m.resolve()}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c", "copy", str(output)
    ], check=True, capture_output=True)


def _mix_bg_music(video: Path, music: Path, output: Path):
    """Mix low-volume background music under the narration."""
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(music),
        "-filter_complex",
        "[1:a]volume=0.15[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output)
    ], check=True, capture_output=True)


def _add_chapters(video: Path, chapters: List[Tuple[float, str]], total_duration: float, output: Path):
    """Add chapter markers via FFmpeg metadata."""
    meta_path = video.parent / "chapters.txt"
    lines = [";FFMETADATA1\n"]
    for i, (start, title) in enumerate(chapters):
        end = chapters[i+1][0] if i + 1 < len(chapters) else total_duration
        # TIMEBASE=1/1000 means milliseconds
        start_ms = int(start * 1000)
        end_ms = int(end * 1000)
        lines.append(
            f"[CHAPTER]\n"
            f"TIMEBASE=1/1000\n"
            f"START={start_ms}\n"
            f"END={end_ms}\n"
            f"title={title}\n"
        )
    meta_path.write_text("".join(lines), encoding="utf-8")

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(meta_path),
        "-map_metadata", "1",
        "-codec", "copy",
        str(output)
    ], check=True, capture_output=True)


def _merge_srts(segments: List[Tuple[Path, float]], output: Path):
    """Merge per-scene SRTs with time offsets."""
    def parse_time(t: str) -> float:
        h, m, s = t.replace(",", ".").split(":")
        return int(h)*3600 + int(m)*60 + float(s)

    def format_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

    index = 1
    lines = []
    for srt_path, offset in segments:
        if not srt_path.exists():
            continue
        content = srt_path.read_text(encoding="utf-8")
        blocks = content.strip().split("\n\n")
        for block in blocks:
            parts = block.split("\n")
            if len(parts) < 3:
                continue
            times = parts[1].split(" --> ")
            if len(times) != 2:
                continue
            start = parse_time(times[0]) + offset
            end = parse_time(times[1]) + offset
            text = "\n".join(parts[2:])
            lines.append(f"{index}\n{format_time(start)} --> {format_time(end)}\n{text}\n")
            index += 1

    output.write_text("\n".join(lines), encoding="utf-8")
