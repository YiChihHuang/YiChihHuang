"""
Deep Research Module
====================

Performs in-depth research on the learning topic,
identifying knowledge gaps and misconceptions based on student background.
"""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from ..providers.base import LLMProvider
from ..utils.resumable import check_and_resume, save_text, load_text

console = Console()


class DeepResearchModule:
    """
    Deep Research Module for analyzing learning topics.

    This module:
    1. Analyzes the learning requirement and student background
    2. Identifies knowledge gaps and common misconceptions
    3. Researches the topic using LLM (with search if available)
    4. Generates a comprehensive research report
    """

    OUTPUT_FILE = "1_research.md"

    SYSTEM_PROMPT = """你是一位專業的教育研究員，專門分析學習需求並找出最有效的教學策略。

你的任務是：
1. 深入分析學生的背景知識
2. 找出學習這個主題時可能遇到的「知識斷層」(Knowledge Gap)
3. 識別常見的「迷思概念」(Misconceptions)
4. 搜尋最新的相關文獻和最佳實踐
5. 提出教學策略建議

請使用繁體中文回答，並保持專業但易懂的語調。"""

    RESEARCH_PROMPT_TEMPLATE = """## 研究任務

請針對以下學習需求進行深度研究：

### 學習需求
{learning_requirement}

### 學生背景
{student_background}

---

請提供完整的研究報告，包含以下章節：

## 1. 主題概述
- 這個主題的核心概念是什麼？
- 為什麼這個主題重要？

## 2. 知識斷層分析
- 根據學生背景，他們可能缺乏哪些先備知識？
- 從現有知識到目標知識，需要跨越哪些認知跳躍？
- 建議的知識橋樑 (Scaffolding) 是什麼？

## 3. 常見迷思概念
- 學習這個主題時，常見的錯誤理解有哪些？
- 這些迷思概念是如何形成的？
- 如何有效地糾正這些迷思？

## 4. 最新趨勢與最佳實踐
- 這個領域最新的發展是什麼？
- 業界/學界推薦的最佳實踐是什麼？
- 有哪些實用的案例或應用場景？

## 5. 教學策略建議
- 推薦的教學順序是什麼？
- 應該使用哪些比喻或類比來解釋抽象概念？
- 建議的練習和評估方式？

## 6. 參考資源
- 推薦的延伸學習資源
- 相關工具或平台

請確保分析深入且具體，並根據學生背景提供個人化的建議。"""

    def __init__(self, llm_provider: LLMProvider, workspace: Path):
        """
        Initialize the Deep Research Module.

        Args:
            llm_provider: LLM provider for generating research
            workspace: Workspace directory for output
        """
        self.llm = llm_provider
        self.workspace = workspace
        self.output_path = workspace / self.OUTPUT_FILE

    def run(
        self,
        learning_requirement: str,
        student_background: str,
        skip_if_exists: bool = True,
    ) -> str:
        """
        Execute deep research on the learning topic.

        Args:
            learning_requirement: What the student wants to learn
            student_background: Student's current knowledge level
            skip_if_exists: Whether to skip if output file exists

        Returns:
            Research report as markdown string
        """
        console.print(Panel(
            "[bold blue]Step 1: Deep Research[/bold blue]\n"
            "Analyzing learning requirements and student background...",
            title="🔬 Research Module",
        ))

        # Check for existing output
        if skip_if_exists:
            should_skip, existing_data = check_and_resume(
                self.output_path,
                "Deep Research",
                ask_user=True,
                load_func=load_text,
            )
            if should_skip and existing_data:
                return existing_data

        # Display inputs
        console.print("\n[cyan]Learning Requirement:[/cyan]")
        console.print(f"  {learning_requirement}")
        console.print("\n[cyan]Student Background:[/cyan]")
        console.print(f"  {student_background}")
        console.print()

        # Generate research prompt
        prompt = self.RESEARCH_PROMPT_TEMPLATE.format(
            learning_requirement=learning_requirement,
            student_background=student_background,
        )

        # Call LLM
        console.print("[yellow]Generating research report...[/yellow]")

        with console.status("[bold green]Researching with AI..."):
            response = self.llm.text_generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.7,
            )

        research_report = response.content

        # Save output
        save_text(research_report, self.output_path)

        # Display result
        console.print("\n[green]✓ Research complete![/green]")
        console.print(f"  Output saved to: [cyan]{self.output_path}[/cyan]")

        # Show preview
        preview_lines = research_report.split("\n")[:20]
        preview = "\n".join(preview_lines) + "\n..."
        console.print(Panel(
            Markdown(preview),
            title="Research Report Preview",
            border_style="green",
        ))

        # Show token usage if available
        if response.usage:
            console.print(f"\n[dim]Token usage: {response.usage}[/dim]")

        return research_report

    def get_output_path(self) -> Path:
        """Get the output file path."""
        return self.output_path

    def load_existing(self) -> Optional[str]:
        """Load existing research report if available."""
        if self.output_path.exists():
            return load_text(self.output_path)
        return None
