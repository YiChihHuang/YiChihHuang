"""
Resumable Step Logic
====================

Provides functionality to check for existing intermediate files
and optionally skip steps that have already been completed.
"""

import json
from pathlib import Path
from typing import Optional, Any, Callable, TypeVar
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.prompt import Confirm

console = Console()

T = TypeVar("T")


class StepStatus(Enum):
    """Status of a resumable step."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


@dataclass
class ResumableStep:
    """
    Represents a step in the pipeline that can be resumed.

    Attributes:
        name: Step name (e.g., "research", "syllabus")
        output_file: Expected output file path
        description: Human-readable description
    """
    name: str
    output_file: Path
    description: str
    status: StepStatus = StepStatus.NOT_STARTED


def check_and_resume(
    output_file: Path,
    step_name: str,
    ask_user: bool = True,
    load_func: Optional[Callable[[Path], T]] = None,
) -> tuple[bool, Optional[T]]:
    """
    Check if a step's output already exists and handle resumption.

    Args:
        output_file: Path to the expected output file
        step_name: Name of the step for user prompts
        ask_user: Whether to ask user before skipping
        load_func: Optional function to load the existing file

    Returns:
        Tuple of (should_skip, loaded_data)
        - should_skip: True if step should be skipped
        - loaded_data: Loaded data if skipping, None otherwise
    """
    if not output_file.exists():
        return False, None

    # File exists - ask user what to do
    console.print(f"\n[yellow]Found existing output for step: {step_name}[/yellow]")
    console.print(f"  File: [cyan]{output_file}[/cyan]")

    if ask_user:
        skip = Confirm.ask(
            "  Skip this step and use existing file?",
            default=True,
        )
    else:
        skip = True
        console.print("  [dim]Auto-skipping (resumable mode)[/dim]")

    if skip:
        console.print(f"  [green]Skipping {step_name}, using existing file[/green]")

        # Load existing data if function provided
        if load_func is not None:
            try:
                data = load_func(output_file)
                return True, data
            except Exception as e:
                console.print(f"  [red]Error loading file: {e}[/red]")
                console.print("  [yellow]Will regenerate...[/yellow]")
                return False, None

        return True, None

    console.print(f"  [yellow]Regenerating {step_name}...[/yellow]")
    return False, None


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    """Load a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_json(data: Any, path: Path):
    """Save data as JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_text(content: str, path: Path):
    """Save content as text file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


class ResumableWorkflow:
    """
    Manages a workflow with resumable steps.

    Tracks step status and provides utilities for
    checking/skipping completed steps.
    """

    def __init__(self, workspace: Path, ask_before_skip: bool = True):
        """
        Initialize workflow.

        Args:
            workspace: Workspace directory path
            workspace: Workspace directory path
            ask_before_skip: Whether to ask user before skipping steps
        """
        self.workspace = workspace
        self.ask_before_skip = ask_before_skip
        self.steps: list[ResumableStep] = []
        self._status_file = workspace / ".workflow_status.json"

        # Ensure workspace exists
        workspace.mkdir(parents=True, exist_ok=True)

    def add_step(self, name: str, output_file: str, description: str) -> ResumableStep:
        """
        Add a step to the workflow.

        Args:
            name: Step identifier
            output_file: Output filename (relative to workspace)
            description: Human-readable description

        Returns:
            The created ResumableStep
        """
        step = ResumableStep(
            name=name,
            output_file=self.workspace / output_file,
            description=description,
        )
        self.steps.append(step)
        return step

    def check_step(
        self,
        step: ResumableStep,
        load_func: Optional[Callable[[Path], T]] = None,
    ) -> tuple[bool, Optional[T]]:
        """
        Check if a step should be skipped.

        Args:
            step: The step to check
            load_func: Optional function to load existing data

        Returns:
            Tuple of (should_skip, loaded_data)
        """
        should_skip, data = check_and_resume(
            step.output_file,
            step.description,
            self.ask_before_skip,
            load_func,
        )

        if should_skip:
            step.status = StepStatus.SKIPPED
        else:
            step.status = StepStatus.IN_PROGRESS

        return should_skip, data

    def complete_step(self, step: ResumableStep):
        """Mark a step as completed."""
        step.status = StepStatus.COMPLETED
        self._save_status()

    def _save_status(self):
        """Save workflow status to file."""
        status = {
            step.name: step.status.value
            for step in self.steps
        }
        save_json(status, self._status_file)

    def print_status(self):
        """Print current workflow status."""
        console.print("\n[bold]Workflow Status:[/bold]")
        for step in self.steps:
            status_icon = {
                StepStatus.NOT_STARTED: "[dim]○[/dim]",
                StepStatus.IN_PROGRESS: "[yellow]◐[/yellow]",
                StepStatus.COMPLETED: "[green]●[/green]",
                StepStatus.SKIPPED: "[blue]◎[/blue]",
            }.get(step.status, "?")

            console.print(f"  {status_icon} {step.description}")
