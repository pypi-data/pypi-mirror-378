"""
Django FSM Dynamic Workflows

Dynamic workflow extensions for django-fsm-2 that allow optional Django apps
to modify FSM state machines without creating database migrations.

Features:
- Dynamic state enums that can be extended at runtime
- Callable choices that prevent Django migrations
- Workflow extension framework for app-based extensions
- Transition builder utilities for programmatic transition creation
"""

from __future__ import annotations

from .__version__ import __version__
from .core import DynamicStateEnum
from .core import TransitionBuilder
from .core import TransitionModifier
from .core import WorkflowExtension
from .core import create_simple_workflow_extension

__all__ = [
    "DynamicStateEnum",
    "TransitionBuilder",
    "TransitionModifier",
    "WorkflowExtension",
    "__version__",
    "create_simple_workflow_extension",
]
