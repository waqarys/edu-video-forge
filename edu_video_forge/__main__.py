"""CLI for EduVideoForge."""
import typer
from pathlib import Path
from rich.console import Console

from .pipeline import generate_video

app = typer.Typer(help="EduVideoForge - Generate educational videos from scripts")
console = Console()


@app.command()
def generate(
    script: Path = typer.Argument(..., help="Path to script (.md or .json)"),
    output: Path = typer.Option("output.mp4", "--output", "-o", help="Output video path"),
    voice: str = typer.Option("en-US-AriaNeural", "--voice", help="edge-tts voice"),
    theme: str = typer.Option("chalkboard", "--theme", help="Visual theme"),
    quality: str = typer.Option("medium", "--quality", help="low/medium/high"),
    bg_music: Path = typer.Option(None, "--bg-music", help="Optional background music file (low volume mix)"),
    no_chapters: bool = typer.Option(False, "--no-chapters", help="Skip embedding chapter markers"),
):
    """Generate video from script."""
    try:
        result = generate_video(
            script,
            output,
            voice=voice,
            theme=theme,
            quality=quality,
            bg_music=bg_music,
            add_chapters=not no_chapters,
        )
        console.print(f"[green]Success:[/green] {result}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
