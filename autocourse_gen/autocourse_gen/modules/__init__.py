"""
AutoCourseGen Modules
=====================

Core modules for the course generation pipeline.
"""

from .deep_research import DeepResearchModule
from .curriculum_planner import CurriculumPlannerModule
from .slide_generator import SlideGeneratorModule
from .visual_anchor import VisualAnchorModule
from .composer import ComposerModule

__all__ = [
    "DeepResearchModule",
    "CurriculumPlannerModule",
    "SlideGeneratorModule",
    "VisualAnchorModule",
    "ComposerModule",
]
