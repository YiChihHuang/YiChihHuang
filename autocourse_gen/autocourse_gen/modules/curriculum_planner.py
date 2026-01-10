"""
Curriculum Planner Module
=========================

Plans the course curriculum based on research,
with humor and vivid metaphors.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from ..providers.base import LLMProvider
from ..utils.resumable import check_and_resume, save_json, load_json

console = Console()


class CurriculumPlannerModule:
    """
    Curriculum Planner Module for designing course structure.

    This module:
    1. Analyzes the research report
    2. Designs a structured course syllabus
    3. Uses CoT (Chain of Thought) for self-correction
    4. Creates engaging content with humor and metaphors
    """

    OUTPUT_FILE = "2_syllabus.json"

    SYSTEM_PROMPT = """你是一位幽默風趣、善於比喻的課程設計師。

你的風格特點：
- 使用生動的比喻 (Metaphor) 解釋複雜概念
- 適時加入輕鬆幽默的元素，但不失專業
- 循序漸進，確保學生能跟上節奏
- 注重實用性和互動性

在設計課程時，請先進行以下自我檢查 (Chain of Thought)：
1. 這個觀念是否跳太快？學生能否順利銜接？
2. 引用的資料是否正確？比喻是否恰當？
3. 內容是否太抽象？需要更多具體例子嗎？

請使用繁體中文，並保持活潑但專業的語調。"""

    PLANNING_PROMPT_TEMPLATE = """## 課程規劃任務

請根據以下研究報告，設計一個完整的課程大綱。

### 研究報告
{research_report}

---

## 請輸出以下 JSON 格式的課程大綱：

```json
{{
  "course_title": "課程標題",
  "course_description": "課程簡介（2-3句話，吸引人）",
  "target_audience": "目標受眾描述",
  "learning_objectives": [
    "學習目標1",
    "學習目標2",
    "學習目標3"
  ],
  "prerequisites": [
    "先備知識1",
    "先備知識2"
  ],
  "total_duration_minutes": 預估總時長（分鐘）,
  "sections": [
    {{
      "section_id": 1,
      "title": "章節標題",
      "description": "章節描述",
      "duration_minutes": 章節時長,
      "key_concepts": ["概念1", "概念2"],
      "metaphor": "用於解釋核心概念的生動比喻",
      "talking_points": [
        {{
          "point_id": 1,
          "topic": "主題",
          "content": "詳細講解內容（要寫出來，這會變成逐字稿的基礎）",
          "notes": "講解注意事項或補充"
        }}
      ],
      "common_mistakes": ["學生常見錯誤1"],
      "practice_suggestions": ["練習建議"]
    }}
  ],
  "summary": "課程總結",
  "next_steps": ["進階學習建議"]
}}
```

## 重要指示：

1. **CoT 自我檢查**：在設計每個章節前，請先思考：
   - 這個章節銜接前一章節是否順暢？
   - 概念難度是否適合目標學生？
   - 比喻是否貼切且易懂？

2. **內容要求**：
   - 每個章節的 `talking_points` 要寫得詳細，因為這會成為投影片和逐字稿的基礎
   - 比喻要生動有趣，幫助學生建立直覺
   - 適時加入幽默元素，但不要太刻意

3. **結構要求**：
   - 章節數量建議 3-7 個
   - 每章節應有 2-5 個 talking points
   - 時間分配要合理

請直接輸出 JSON，不要加其他說明文字。"""

    def __init__(self, llm_provider: LLMProvider, workspace: Path):
        """
        Initialize the Curriculum Planner Module.

        Args:
            llm_provider: LLM provider for generating curriculum
            workspace: Workspace directory for output
        """
        self.llm = llm_provider
        self.workspace = workspace
        self.output_path = workspace / self.OUTPUT_FILE

    def run(
        self,
        research_report: str,
        skip_if_exists: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate course curriculum based on research.

        Args:
            research_report: Research report from Deep Research module
            skip_if_exists: Whether to skip if output file exists

        Returns:
            Course syllabus as dictionary
        """
        console.print(Panel(
            "[bold blue]Step 2: Curriculum Planning[/bold blue]\n"
            "Designing course structure with humor and metaphors...",
            title="📚 Curriculum Planner",
        ))

        # Check for existing output
        if skip_if_exists:
            should_skip, existing_data = check_and_resume(
                self.output_path,
                "Curriculum Planning",
                ask_user=True,
                load_func=load_json,
            )
            if should_skip and existing_data:
                self._display_syllabus(existing_data)
                return existing_data

        # Generate planning prompt
        prompt = self.PLANNING_PROMPT_TEMPLATE.format(
            research_report=research_report[:8000]  # Limit length
        )

        # Call LLM
        console.print("[yellow]Generating course curriculum...[/yellow]")

        with console.status("[bold green]Planning with AI..."):
            response = self.llm.text_generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.7,
            )

        # Parse JSON response
        syllabus = self._parse_json_response(response.content)

        # Save output
        save_json(syllabus, self.output_path)

        # Display result
        console.print("\n[green]✓ Curriculum planning complete![/green]")
        console.print(f"  Output saved to: [cyan]{self.output_path}[/cyan]")

        self._display_syllabus(syllabus)

        return syllabus

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        # Try to extract JSON from markdown code block
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end > start:
                content = content[start:end]
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end > start:
                content = content[start:end]

        # Clean up
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            console.print(f"[red]Warning: JSON parsing failed: {e}[/red]")
            console.print("[yellow]Attempting to fix JSON...[/yellow]")

            # Try to fix common JSON issues
            content = content.replace("，", ",")
            content = content.replace("：", ":")
            content = content.replace(""", '"')
            content = content.replace(""", '"')

            try:
                return json.loads(content)
            except:
                # Return a basic structure
                return {
                    "course_title": "課程",
                    "course_description": "課程內容",
                    "sections": [],
                    "_raw_response": content,
                    "_parse_error": str(e),
                }

    def _display_syllabus(self, syllabus: Dict[str, Any]):
        """Display syllabus as a tree."""
        tree = Tree(f"[bold]{syllabus.get('course_title', 'Course')}[/bold]")

        # Add description
        desc_node = tree.add("[dim]Description[/dim]")
        desc_node.add(syllabus.get('course_description', 'No description'))

        # Add sections
        sections_node = tree.add("[cyan]Sections[/cyan]")
        for section in syllabus.get("sections", []):
            section_node = sections_node.add(
                f"[bold]{section.get('section_id', '?')}. {section.get('title', 'Untitled')}[/bold] "
                f"[dim]({section.get('duration_minutes', '?')} min)[/dim]"
            )

            # Add talking points
            for point in section.get("talking_points", []):
                section_node.add(f"• {point.get('topic', 'Topic')}")

            # Add metaphor if present
            if section.get("metaphor"):
                section_node.add(f"[yellow]💡 {section['metaphor'][:50]}...[/yellow]")

        console.print(tree)

    def get_output_path(self) -> Path:
        """Get the output file path."""
        return self.output_path

    def load_existing(self) -> Optional[Dict[str, Any]]:
        """Load existing syllabus if available."""
        if self.output_path.exists():
            return load_json(self.output_path)
        return None
