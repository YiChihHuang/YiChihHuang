#!/usr/bin/env python3
"""
AutoCourseGen - AI-Powered Course Video Generator
==================================================

A fully automated system that generates educational videos
based on user requirements and student background.

Usage:
    python main.py --requirement "學習Python基礎" --background "高中生，有基本數學概念"
    python main.py --step research --requirement "..." --background "..."
    python main.py --resume  # Continue from last checkpoint
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autocourse_gen.utils.config_loader import get_config, ConfigLoader
from autocourse_gen.providers.gemini_provider import GeminiProvider
from autocourse_gen.modules.deep_research import DeepResearchModule
from autocourse_gen.modules.curriculum_planner import CurriculumPlannerModule
from autocourse_gen.modules.slide_generator import SlideGeneratorModule
from autocourse_gen.modules.visual_anchor import VisualAnchorModule
from autocourse_gen.modules.composer import ComposerModule
from autocourse_gen.utils.resumable import load_json, load_text

console = Console()

# Load environment variables
load_dotenv(project_root / ".env")


BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║     _         _         ____                              ║
║    / \\  _   _| |_ ___  / ___|___  _   _ _ __ ___  ___     ║
║   / _ \\| | | | __/ _ \\| |   / _ \\| | | | '__/ __|/ _ \\    ║
║  / ___ \\ |_| | || (_) | |__| (_) | |_| | |  \\__ \\  __/    ║
║ /_/   \\_\\__,_|\\__\\___/ \\____\\___/ \\__,_|_|  |___/\\___|    ║
║                                                           ║
║           🎬 AI-Powered Course Video Generator            ║
╚═══════════════════════════════════════════════════════════════╝
"""


STEPS = ["research", "curriculum", "slides", "anchor", "compose", "all"]


def setup_provider(config: ConfigLoader) -> GeminiProvider:
    """Set up the LLM provider."""
    provider_name = config.get("llm.default_provider", "gemini")

    if provider_name == "gemini":
        gemini_config = config.get_section("llm").get("gemini", {})
        return GeminiProvider(gemini_config)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def run_research(
    provider: GeminiProvider,
    workspace: Path,
    requirement: str,
    background: str,
) -> str:
    """Run the deep research step."""
    module = DeepResearchModule(provider, workspace)
    return module.run(requirement, background)


def run_curriculum(
    provider: GeminiProvider,
    workspace: Path,
    research_report: str,
) -> dict:
    """Run the curriculum planning step."""
    module = CurriculumPlannerModule(provider, workspace)
    return module.run(research_report)


def run_slides(
    workspace: Path,
    syllabus: dict,
    config: ConfigLoader,
) -> Path:
    """Run the slide generation step."""
    slides_config = config.get_section("slides")
    module = SlideGeneratorModule(workspace, slides_config)
    return module.run(syllabus)


def run_anchor(
    provider: GeminiProvider,
    workspace: Path,
    syllabus: dict,
    pptx_path: Path,
) -> dict:
    """Run the visual anchor and script step."""
    module = VisualAnchorModule(provider, workspace, syllabus)
    return module.run(pptx_path)


def run_compose(
    workspace: Path,
    script_data: dict,
    config: ConfigLoader,
) -> Path:
    """Run the video composition step."""
    video_config = config.get_section("video")
    tts_config = config.get_section("tts")
    cursor_config = config.get_section("cursor")

    module = ComposerModule(workspace, video_config, tts_config, cursor_config)
    return module.run(script_data)


def run_all_steps(
    requirement: str,
    background: str,
    config: ConfigLoader,
    workspace: Path,
):
    """Run all steps in sequence."""
    console.print(Panel(BANNER, border_style="blue"))

    console.print(f"\n[bold]Learning Requirement:[/bold] {requirement}")
    console.print(f"[bold]Student Background:[/bold] {background}")
    console.print(f"[bold]Workspace:[/bold] {workspace}\n")

    # Set up provider
    provider = setup_provider(config)
    console.print(f"[green]✓ LLM Provider initialized: {provider.provider_name}[/green]\n")

    # Step 1: Deep Research
    research_report = run_research(provider, workspace, requirement, background)

    # Step 2: Curriculum Planning
    syllabus = run_curriculum(provider, workspace, research_report)

    # Step 3: Slide Generation
    pptx_path = run_slides(workspace, syllabus, config)

    # Step 4: Visual Anchor & Script
    script_data = run_anchor(provider, workspace, syllabus, pptx_path)

    # Step 5: Video Composition
    output_path = run_compose(workspace, script_data, config)

    # Done!
    console.print(Panel(
        f"[bold green]🎉 Course video generated successfully![/bold green]\n\n"
        f"Output: [cyan]{output_path}[/cyan]\n\n"
        f"Intermediate files saved in: [cyan]{workspace}[/cyan]",
        title="✅ Complete",
        border_style="green",
    ))


@click.command()
@click.option(
    "--requirement", "-r",
    help="Learning requirement (what to teach)",
)
@click.option(
    "--background", "-b",
    help="Student background (who the learner is)",
)
@click.option(
    "--step", "-s",
    type=click.Choice(STEPS),
    default="all",
    help="Which step to run (default: all)",
)
@click.option(
    "--workspace", "-w",
    type=click.Path(),
    help="Workspace directory (default: ./workspace)",
)
@click.option(
    "--resume",
    is_flag=True,
    help="Resume from last checkpoint",
)
@click.option(
    "--interactive", "-i",
    is_flag=True,
    help="Interactive mode (prompt for inputs)",
)
def main(
    requirement: Optional[str],
    background: Optional[str],
    step: str,
    workspace: Optional[str],
    resume: bool,
    interactive: bool,
):
    """
    AutoCourseGen - Generate educational course videos with AI.

    This tool creates complete course videos from your learning requirements,
    including research, curriculum planning, slides, narration, and video composition.
    """
    # Load configuration
    config = get_config()

    # Set up workspace
    if workspace:
        workspace_path = Path(workspace)
    else:
        workspace_path = config.workspace_dir

    workspace_path.mkdir(parents=True, exist_ok=True)

    # Interactive mode
    if interactive or (not requirement and not resume):
        console.print(Panel(BANNER, border_style="blue"))

        if not requirement:
            requirement = Prompt.ask(
                "\n[cyan]請輸入學習需求[/cyan]\n"
                "[dim]例如：學習 Python 基礎語法、了解機器學習原理[/dim]"
            )

        if not background:
            background = Prompt.ask(
                "\n[cyan]請描述學生背景[/cyan]\n"
                "[dim]例如：高中生，有基本數學概念、大學資工系學生[/dim]"
            )

    # Resume mode
    if resume:
        console.print("[yellow]Resuming from last checkpoint...[/yellow]")

        # Try to load existing requirement/background from workspace
        meta_file = workspace_path / "meta.json"
        if meta_file.exists():
            meta = load_json(meta_file)
            requirement = requirement or meta.get("requirement")
            background = background or meta.get("background")
        else:
            console.print("[red]No checkpoint found. Please provide requirement and background.[/red]")
            return

    # Validate inputs
    if not requirement or not background:
        console.print("[red]Error: Both --requirement and --background are required.[/red]")
        console.print("Use --interactive for guided input, or --help for usage.")
        return

    # Save meta info
    from autocourse_gen.utils.resumable import save_json
    save_json(
        {"requirement": requirement, "background": background},
        workspace_path / "meta.json",
    )

    # Run the appropriate step(s)
    try:
        if step == "all":
            run_all_steps(requirement, background, config, workspace_path)

        elif step == "research":
            provider = setup_provider(config)
            run_research(provider, workspace_path, requirement, background)

        elif step == "curriculum":
            # Need research report
            research_path = workspace_path / "1_research.md"
            if not research_path.exists():
                console.print("[red]Error: Research report not found. Run 'research' step first.[/red]")
                return

            research_report = load_text(research_path)
            provider = setup_provider(config)
            run_curriculum(provider, workspace_path, research_report)

        elif step == "slides":
            # Need syllabus
            syllabus_path = workspace_path / "2_syllabus.json"
            if not syllabus_path.exists():
                console.print("[red]Error: Syllabus not found. Run 'curriculum' step first.[/red]")
                return

            syllabus = load_json(syllabus_path)
            run_slides(workspace_path, syllabus, config)

        elif step == "anchor":
            # Need syllabus and slides
            syllabus_path = workspace_path / "2_syllabus.json"
            pptx_path = workspace_path / "3_slides.pptx"

            if not syllabus_path.exists() or not pptx_path.exists():
                console.print("[red]Error: Syllabus or slides not found. Run previous steps first.[/red]")
                return

            syllabus = load_json(syllabus_path)
            provider = setup_provider(config)
            run_anchor(provider, workspace_path, syllabus, pptx_path)

        elif step == "compose":
            # Need script data
            script_path = workspace_path / "4_script_with_coords.json"

            if not script_path.exists():
                console.print("[red]Error: Script data not found. Run 'anchor' step first.[/red]")
                return

            script_data = load_json(script_path)
            run_compose(workspace_path, script_data, config)

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise


if __name__ == "__main__":
    main()
