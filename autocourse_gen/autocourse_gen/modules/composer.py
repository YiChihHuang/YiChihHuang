"""
Composer Module
===============

Combines slides, audio, and cursor animation
into the final course video.
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
from PIL import Image

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils.bezier import generate_smooth_path, generate_multi_segment_path
from ..utils.resumable import check_and_resume
from ..utils.cursor_generator import ensure_cursor_image

console = Console()


class ComposerModule:
    """
    Composer Module for video synthesis.

    This module:
    1. Generates TTS audio using edge-tts
    2. Creates cursor animation with Bezier curves
    3. Composites everything into final video
    """

    OUTPUT_FILE = "final_course_video.mp4"
    AUDIO_DIR = "audio"

    def __init__(
        self,
        workspace: Path,
        config: dict,
        tts_config: dict,
        cursor_config: dict,
    ):
        """
        Initialize the Composer Module.

        Args:
            workspace: Workspace directory
            config: Video configuration
            tts_config: TTS configuration
            cursor_config: Cursor animation configuration
        """
        self.workspace = workspace
        self.config = config
        self.tts_config = tts_config
        self.cursor_config = cursor_config

        self.output_path = workspace / self.OUTPUT_FILE
        self.audio_dir = workspace / self.AUDIO_DIR

        # Video settings
        self.width = config.get("width", 1920)
        self.height = config.get("height", 1080)
        self.fps = config.get("fps", 30)

        # TTS settings
        self.voice = tts_config.get("voice", "zh-TW-HsiaoChenNeural")
        self.rate = tts_config.get("rate", "+0%")
        self.volume = tts_config.get("volume", "+0%")

        # Cursor settings
        self.cursor_size = cursor_config.get("size", 32)
        self.bezier_steps = cursor_config.get("bezier_steps", 60)

    def run(
        self,
        script_data: Dict[str, Any],
        skip_if_exists: bool = True,
    ) -> Path:
        """
        Generate the final course video.

        Args:
            script_data: Script with coordinates
            skip_if_exists: Whether to skip if output exists

        Returns:
            Path to the final video
        """
        console.print(Panel(
            "[bold blue]Step 5: Video Composition[/bold blue]\n"
            "Generating audio and compositing video...",
            title="🎬 Composer Module",
        ))

        # Check for existing output
        if skip_if_exists:
            should_skip, _ = check_and_resume(
                self.output_path,
                "Video Composition",
                ask_user=True,
            )
            if should_skip:
                return self.output_path

        # Ensure audio directory exists
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        # Ensure cursor image exists
        assets_dir = self.workspace / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        cursor_path = ensure_cursor_image(assets_dir, "cursor.png", self.cursor_size)

        slides = script_data.get("slides", [])
        if not slides:
            console.print("[red]Error: No slides to process[/red]")
            return self.output_path

        # Step 1: Generate TTS audio for all slides
        console.print("\n[cyan]Generating TTS audio...[/cyan]")
        audio_paths = asyncio.run(self._generate_all_audio(slides))

        # Step 2: Get audio durations
        durations = self._get_audio_durations(audio_paths)

        # Step 3: Create video with cursor animation
        console.print("\n[cyan]Compositing video...[/cyan]")
        self._compose_video(slides, audio_paths, durations, cursor_path)

        console.print("\n[green]✓ Video composition complete![/green]")
        console.print(f"  Output saved to: [cyan]{self.output_path}[/cyan]")

        return self.output_path

    async def _generate_all_audio(
        self,
        slides: List[Dict[str, Any]],
    ) -> List[Path]:
        """Generate TTS audio for all slides."""
        import edge_tts

        audio_paths = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Generating audio...", total=len(slides))

            for i, slide in enumerate(slides):
                slide_num = slide.get("slide_number", i + 1)
                script = slide.get("script", "")

                if not script:
                    script = f"這是第 {slide_num} 張投影片。"

                audio_path = self.audio_dir / f"slide_{slide_num:03d}.mp3"

                # Generate audio
                communicate = edge_tts.Communicate(
                    script,
                    self.voice,
                    rate=self.rate,
                    volume=self.volume,
                )

                await communicate.save(str(audio_path))
                audio_paths.append(audio_path)

                progress.update(task, advance=1)

        console.print(f"  [green]Generated {len(audio_paths)} audio files[/green]")
        return audio_paths

    def _get_audio_durations(self, audio_paths: List[Path]) -> List[float]:
        """Get duration of each audio file."""
        durations = []

        for path in audio_paths:
            try:
                # Use ffprobe to get duration
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1",
                        str(path),
                    ],
                    capture_output=True,
                    text=True,
                )
                duration = float(result.stdout.strip())
                durations.append(duration)
            except Exception:
                # Default duration if ffprobe fails
                durations.append(5.0)

        return durations

    def _compose_video(
        self,
        slides: List[Dict[str, Any]],
        audio_paths: List[Path],
        durations: List[float],
        cursor_path: Path,
    ):
        """Compose final video with moviepy."""
        try:
            from moviepy.editor import (
                ImageClip,
                AudioFileClip,
                CompositeVideoClip,
                concatenate_videoclips,
            )
        except ImportError:
            console.print("[red]moviepy not available. Trying ffmpeg directly...[/red]")
            self._compose_video_ffmpeg(slides, audio_paths, durations)
            return

        # Load cursor image
        cursor_img = Image.open(cursor_path).convert("RGBA")
        cursor_array = np.array(cursor_img)

        clips = []

        with Progress() as progress:
            task = progress.add_task("Creating video clips...", total=len(slides))

            for i, slide in enumerate(slides):
                slide_num = slide.get("slide_number", i + 1)
                image_path = slide.get("image_path")
                anchor_points = slide.get("anchor_points", [])
                duration = durations[i] if i < len(durations) else 5.0

                if not image_path or not Path(image_path).exists():
                    console.print(f"[yellow]Warning: Image not found for slide {slide_num}[/yellow]")
                    continue

                # Create base image clip
                img_clip = ImageClip(image_path).set_duration(duration)

                # Add audio
                if i < len(audio_paths) and audio_paths[i].exists():
                    audio_clip = AudioFileClip(str(audio_paths[i]))
                    img_clip = img_clip.set_audio(audio_clip)

                # Generate cursor path
                cursor_positions = self._generate_cursor_path(
                    anchor_points,
                    duration,
                    self.width,
                    self.height,
                )

                # Create cursor overlay
                def make_cursor_frame(get_frame, t):
                    frame = get_frame(t)

                    # Find current cursor position
                    pos = self._get_cursor_position_at_time(cursor_positions, t)
                    if pos:
                        frame = self._overlay_cursor(
                            frame,
                            cursor_array,
                            int(pos[0]),
                            int(pos[1]),
                        )

                    return frame

                # Apply cursor overlay
                clip_with_cursor = img_clip.fl(make_cursor_frame)
                clips.append(clip_with_cursor)

                progress.update(task, advance=1)

        # Concatenate all clips
        if clips:
            console.print("[yellow]Concatenating clips...[/yellow]")
            final_clip = concatenate_videoclips(clips, method="compose")

            # Write final video
            console.print("[yellow]Writing final video...[/yellow]")
            final_clip.write_videofile(
                str(self.output_path),
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=str(self.workspace / "temp_audio.m4a"),
                remove_temp=True,
                verbose=False,
                logger=None,
            )

            # Clean up
            final_clip.close()
        else:
            console.print("[red]Error: No clips to concatenate[/red]")

    def _compose_video_ffmpeg(
        self,
        slides: List[Dict[str, Any]],
        audio_paths: List[Path],
        durations: List[float],
    ):
        """Fallback: Compose video using ffmpeg directly."""
        console.print("[yellow]Using ffmpeg fallback (no cursor animation)...[/yellow]")

        # Create a concat file
        concat_file = self.workspace / "concat.txt"

        with open(concat_file, "w") as f:
            for i, slide in enumerate(slides):
                image_path = slide.get("image_path")
                if image_path and Path(image_path).exists():
                    duration = durations[i] if i < len(durations) else 5.0
                    f.write(f"file '{image_path}'\n")
                    f.write(f"duration {duration}\n")

        # Generate video from images
        temp_video = self.workspace / "temp_video.mp4"

        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-vsync", "vfr",
            "-pix_fmt", "yuv420p",
            str(temp_video),
        ], capture_output=True)

        # Merge all audio files
        if audio_paths:
            audio_list = self.workspace / "audio_list.txt"
            with open(audio_list, "w") as f:
                for path in audio_paths:
                    if path.exists():
                        f.write(f"file '{path}'\n")

            merged_audio = self.workspace / "merged_audio.mp3"
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(audio_list),
                "-c", "copy",
                str(merged_audio),
            ], capture_output=True)

            # Combine video and audio
            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(temp_video),
                "-i", str(merged_audio),
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(self.output_path),
            ], capture_output=True)
        else:
            # Just rename temp video
            import shutil
            shutil.move(temp_video, self.output_path)

    def _generate_cursor_path(
        self,
        anchor_points: List[Dict[str, Any]],
        duration: float,
        width: int,
        height: int,
    ) -> List[Tuple[float, float, float]]:
        """Generate cursor path with Bezier curves."""
        if not anchor_points:
            # Default: center of screen
            return [(width / 2, height / 2, 0), (width / 2, height / 2, duration)]

        # Convert percentage coordinates to pixels
        waypoints = []
        timestamps = []
        current_time = 0

        for point in anchor_points:
            x = (point.get("x_percent", 50) / 100) * width
            y = (point.get("y_percent", 50) / 100) * height
            waypoints.append((x, y))

            duration_ratio = point.get("duration_ratio", 1 / len(anchor_points))
            timestamps.append(current_time)
            current_time += duration * duration_ratio

        # Generate smooth path
        if len(waypoints) >= 2:
            path_points = generate_multi_segment_path(
                waypoints,
                points_per_segment=self.bezier_steps,
                curvature=0.2,
            )

            # Add timestamps to path
            total_points = len(path_points)
            timestamped_path = []

            for i, (x, y) in enumerate(path_points):
                t = (i / (total_points - 1)) * duration if total_points > 1 else 0
                timestamped_path.append((x, y, t))

            return timestamped_path
        else:
            # Single point
            x, y = waypoints[0]
            return [(x, y, 0), (x, y, duration)]

    def _get_cursor_position_at_time(
        self,
        cursor_positions: List[Tuple[float, float, float]],
        t: float,
    ) -> Optional[Tuple[float, float]]:
        """Get cursor position at a specific time."""
        if not cursor_positions:
            return None

        # Find the two positions to interpolate between
        for i, (x, y, time) in enumerate(cursor_positions):
            if time >= t:
                if i == 0:
                    return (x, y)
                else:
                    # Interpolate
                    prev_x, prev_y, prev_t = cursor_positions[i - 1]
                    if time == prev_t:
                        return (x, y)

                    ratio = (t - prev_t) / (time - prev_t)
                    interp_x = prev_x + (x - prev_x) * ratio
                    interp_y = prev_y + (y - prev_y) * ratio
                    return (interp_x, interp_y)

        # Return last position
        return (cursor_positions[-1][0], cursor_positions[-1][1])

    def _overlay_cursor(
        self,
        frame: np.ndarray,
        cursor: np.ndarray,
        x: int,
        y: int,
    ) -> np.ndarray:
        """Overlay cursor on frame."""
        h, w = cursor.shape[:2]

        # Calculate position (cursor tip at x, y)
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(frame.shape[1], x + w)
        y2 = min(frame.shape[0], y + h)

        if x2 <= x1 or y2 <= y1:
            return frame

        # Cursor region to use
        cx1 = max(0, -x)
        cy1 = max(0, -y)
        cx2 = cx1 + (x2 - x1)
        cy2 = cy1 + (y2 - y1)

        # Create output frame
        result = frame.copy()

        # Get alpha channel
        if cursor.shape[2] == 4:
            alpha = cursor[cy1:cy2, cx1:cx2, 3:4] / 255.0
            cursor_rgb = cursor[cy1:cy2, cx1:cx2, :3]

            # Blend
            result[y1:y2, x1:x2] = (
                cursor_rgb * alpha +
                result[y1:y2, x1:x2] * (1 - alpha)
            ).astype(np.uint8)
        else:
            result[y1:y2, x1:x2] = cursor[cy1:cy2, cx1:cx2]

        return result

    def get_output_path(self) -> Path:
        """Get the output file path."""
        return self.output_path
