"""
Dynamic workflow utilities for django-fsm-2.

This module provides utilities for creating extensible FSM workflows that can be
modified by optional Django apps without requiring database migrations.

Key features:
- Dynamic state enums that can be extended at runtime
- Callable choices that prevent Django migrations
- Workflow extension framework for app-based extensions
- Transition builder utilities for programmatic transition creation

Based on the implementation patterns from examples/dynamic_workflow/.
"""

from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable

from django.apps import apps
from django.db.models.signals import class_prepared
from django_fsm import transition

if TYPE_CHECKING:
    from django.apps import AppConfig
    from django.db import models

logger = logging.getLogger(__name__)


class DynamicStateEnum:
    """
    Base class for extensible state enums.

    This class provides the core functionality for creating state enums that can
    be extended at runtime by other apps via monkeypatching, without requiring
    database migrations.

    Example:
        class MyStateEnum(DynamicStateEnum):
            NEW = 10
            PUBLISHED = 20
            HIDDEN = 30

        # Other apps can extend:
        MyStateEnum.IN_REVIEW = 15
    """

    @classmethod
    def get_choices(cls) -> list[tuple[int, str]]:
        """
        Returns all states as Django choices, including dynamically added ones.

        This method scans the class for uppercase integer attributes and converts
        them to Django choices format. State names are automatically converted
        from UPPER_CASE to "Title Case" for display.

        Returns:
            List of (value, display_name) tuples sorted by value
        """
        choices = []
        for attr_name in dir(cls):
            if attr_name.isupper() and not attr_name.startswith("_"):
                value = getattr(cls, attr_name)
                if isinstance(value, int):
                    # Convert STATE_NAME to "State Name" for display
                    display = attr_name.replace("_", " ").title()
                    choices.append((value, display))
        return sorted(choices, key=lambda x: x[0])

    @classmethod
    def get_values(cls) -> list[int]:
        """
        Returns list of state values only.

        Useful for database constraints and validation.

        Returns:
            List of integer state values
        """
        return [value for value, _ in cls.get_choices()]

    @classmethod
    def get_state_map(cls) -> dict[int, str]:
        """
        Returns a mapping of state values to display names.

        Returns:
            Dictionary mapping state values to display names
        """
        return dict(cls.get_choices())

    @classmethod
    def has_state(cls, value: int) -> bool:
        """
        Check if a state value exists in this enum.

        Args:
            value: State value to check

        Returns:
            True if state exists, False otherwise
        """
        return value in cls.get_values()

    @classmethod
    def add_state(cls, name: str, value: int) -> None:
        """
        Add a new state to this enum.

        This is a convenience method for monkeypatching that includes validation.

        Args:
            name: State name (should be UPPER_CASE)
            value: State value (integer)

        Raises:
            ValueError: If name is not uppercase or value is not integer or already exists
        """
        if not name.isupper():
            raise ValueError(f"State name '{name}' must be uppercase")

        if not isinstance(value, int):
            raise TypeError(f"State value must be integer, got {type(value)}")

        if hasattr(cls, name):
            existing_value = getattr(cls, name)
            if existing_value != value:
                raise ValueError(f"State '{name}' already exists with value {existing_value}")
            return  # Same state, no change needed

        if value in cls.get_values():
            existing_name = next(
                attr_name for attr_name in dir(cls) if attr_name.isupper() and getattr(cls, attr_name) == value
            )
            raise ValueError(f"State value {value} already used by '{existing_name}'")

        setattr(cls, name, value)
        logger.debug("Added state %s=%s to %s", name, value, cls.__name__)


class TransitionBuilder:
    """
    Utility for building and attaching FSM transitions programmatically.

    This class simplifies the process of creating transition methods with proper
    FSM metadata and attaching them to model classes.
    """

    def __init__(self, model_class: type[models.Model], field_name: str = "state"):
        """
        Initialize the transition builder.

        Args:
            model_class: The Django model class to add transitions to
            field_name: Name of the FSM field (default: 'state')
        """
        self.model_class = model_class
        self.field_name = field_name
        self.field = model_class._meta.get_field(field_name)
        self._transitions = []

    def add_transition(
        self,
        method_name: str,
        source: int | list[int] | str,
        target: int,
        method_impl: Callable | None = None,
        conditions: list[Callable] | None = None,
        permission: str | Callable | None = None,
        on_error: int | None = None,
        custom: dict[str, Any] | None = None,
    ) -> TransitionBuilder:
        """
        Add a transition method to be built.

        Args:
            method_name: Name of the transition method
            source: Source state(s) for the transition
            target: Target state for the transition
            method_impl: Optional custom implementation (defaults to no-op)
            conditions: List of condition functions
            permission: Permission string or callable
            on_error: Target state if method raises exception
            custom: Custom transition properties

        Returns:
            Self for method chaining
        """
        if method_impl is None:

            def default_impl(instance, **kwargs):
                logger.debug("Executing transition %s on %s with %s", method_name, instance, kwargs)

            method_impl = default_impl

        self._transitions.append(
            {
                "method_name": method_name,
                "source": source,
                "target": target,
                "method_impl": method_impl,
                "conditions": conditions or [],
                "permission": permission,
                "on_error": on_error,
                "custom": custom or {},
            }
        )

        return self

    def build_and_attach(self) -> None:
        """
        Build all transitions and attach them to the model class.

        This method creates the transition methods with proper FSM metadata
        and attaches them to the model class.
        """
        for transition_config in self._transitions:
            self._build_single_transition(transition_config)

        # Re-collect transitions to update django-fsm registry
        self.field._collect_transitions(sender=self.model_class)

        logger.debug("Built and attached %d transitions to %s", len(self._transitions), self.model_class.__name__)

    def _build_single_transition(self, config: dict[str, Any]) -> None:
        """Build a single transition and attach it to the model."""
        method_name = config["method_name"]
        method_impl = config["method_impl"]

        # Create the decorated transition method
        @transition(
            field=self.field,
            source=config["source"],
            target=config["target"],
            conditions=config["conditions"],
            permission=config["permission"],
            on_error=config["on_error"],
            custom=config["custom"],
        )
        def transition_method(instance, **kwargs):
            return method_impl(instance, **kwargs)

        # Set proper method name and documentation
        transition_method.__name__ = method_name
        transition_method.__qualname__ = f"{self.model_class.__name__}.{method_name}"

        if not method_impl.__doc__:
            transition_method.__doc__ = f"FSM transition: {config['source']} -> {config['target']}"
        else:
            transition_method.__doc__ = method_impl.__doc__

        # Attach to model class
        setattr(self.model_class, method_name, transition_method)


class WorkflowExtension:
    """
    Base class for creating workflow extensions in Django apps.

    This class provides a structured way to extend existing FSM workflows
    from other Django apps, handling the boilerplate of signal connections
    and error handling.

    Example:
        class ReviewWorkflowExtension(WorkflowExtension):
            target_model = 'blog.BlogPost'
            target_enum = 'blog.models.BlogPostStateEnum'

            def extend_states(self, enum_class):
                enum_class.add_state('IN_REVIEW', 15)
                enum_class.add_state('APPROVED', 17)

            def extend_transitions(self, model_class, enum_class):
                builder = TransitionBuilder(model_class)
                builder.add_transition('send_to_review', enum_class.NEW, enum_class.IN_REVIEW)
                builder.add_transition('approve', enum_class.IN_REVIEW, enum_class.APPROVED)
                builder.build_and_attach()
    """

    # Subclasses should override these
    target_model: str | None = None  # 'app_label.ModelName'
    target_enum: str | None = None  # 'module.path.EnumClass'

    def __init__(self, app_config: AppConfig):
        """
        Initialize the workflow extension.

        Args:
            app_config: The Django AppConfig instance
        """
        self.app_config = app_config
        self.logger = logging.getLogger(f"{app_config.name}.workflow_extension")

    def apply(self) -> bool:
        """
        Apply the workflow extension.

        This method handles the complete extension process, including error handling
        and signal connection.

        Returns:
            True if extension was applied successfully, False otherwise
        """
        try:
            # Import target classes
            model_class, enum_class = self._import_targets()
            if not model_class or not enum_class:
                return False

            # Extend states first
            self.extend_states(enum_class)

            # Connect to class_prepared signal for transition modifications
            def enhance_workflow(sender, **kwargs):
                if sender == model_class:
                    self.logger.debug("Enhancing workflow for %s", sender.__name__)
                    try:
                        self.extend_transitions(sender, enum_class)
                        self.modify_existing_transitions(sender, enum_class)
                    except Exception:
                        self.logger.exception("Error extending transitions")

            class_prepared.connect(enhance_workflow)
        except Exception:
            self.logger.exception("Failed to apply workflow extension")
            return False
        else:
            self.logger.info("Applied workflow extension for %s", model_class.__name__)
            return True

    def _import_targets(self) -> tuple[type[models.Model] | None, type | None]:
        """Import the target model and enum classes."""
        if not self.target_model or not self.target_enum:
            self.logger.error("target_model and target_enum must be specified")
            return None, None

        try:
            # Import model class
            app_label, model_name = self.target_model.split(".")
            model_class = apps.get_model(app_label, model_name)

            # Import enum class
            module_path, class_name = self.target_enum.rsplit(".", 1)
            module = importlib.import_module(module_path)
            enum_class = getattr(module, class_name)

        except ImportError as e:
            self.logger.warning("Could not import target classes: %s", e)
            return None, None
        except Exception:
            self.logger.exception("Error importing target classes")
            return None, None
        else:
            return model_class, enum_class

    def extend_states(self, enum_class: type[DynamicStateEnum]) -> None:
        """
        Extend the enum with new states.

        Subclasses should override this method to add their states.

        Args:
            enum_class: The target enum class to extend
        """
        ...

    def extend_transitions(self, model_class: type[models.Model], enum_class: type[DynamicStateEnum]) -> None:
        """
        Add new transitions to the model.

        Subclasses should override this method to add new transition methods.

        Args:
            model_class: The target model class
            enum_class: The enum class with states
        """
        ...

    def modify_existing_transitions(self, model_class: type[models.Model], enum_class: type[DynamicStateEnum]) -> None:
        """
        Modify existing transitions.

        Subclasses should override this method to modify existing transition methods.

        Args:
            model_class: The target model class
            enum_class: The enum class with states
        """
        ...


class TransitionModifier:
    """
    Utility for modifying existing FSM transitions.

    This class provides methods to safely modify existing transition metadata,
    such as changing source/target states or adding/removing conditions.
    """

    def __init__(self, model_class: type[models.Model], method_name: str):
        """
        Initialize the transition modifier.

        Args:
            model_class: The Django model class
            method_name: Name of the existing transition method

        Raises:
            ValueError: If method doesn't exist or doesn't have FSM metadata
        """
        self.model_class = model_class
        self.method_name = method_name

        if not hasattr(model_class, method_name):
            raise ValueError(f"Method '{method_name}' not found on {model_class.__name__}")

        self.method = getattr(model_class, method_name)

        if not hasattr(self.method, "_django_fsm"):
            raise ValueError(f"Method '{method_name}' has no FSM metadata")

        self.fsm_meta = self.method._django_fsm

    def clear_transitions(self) -> TransitionModifier:
        """
        Clear all existing transitions for this method.

        Returns:
            Self for method chaining
        """
        self.fsm_meta.transitions.clear()
        logger.debug("Cleared transitions for %s.%s", self.model_class.__name__, self.method_name)
        return self

    def add_transition(
        self,
        source: int | list[int] | str,
        target: int,
        conditions: list[Callable] | None = None,
        permission: str | Callable | None = None,
        on_error: int | None = None,
        custom: dict[str, Any] | None = None,
    ) -> TransitionModifier:
        """
        Add a new transition to this method.

        Args:
            source: Source state(s) for the transition
            target: Target state for the transition
            conditions: List of condition functions
            permission: Permission string or callable
            on_error: Target state if method raises exception
            custom: Custom transition properties

        Returns:
            Self for method chaining
        """
        self.fsm_meta.add_transition(
            method=self.method,
            source=source,
            target=target,
            on_error=on_error,
            conditions=conditions or [],
            permission=permission,
            custom=custom or {},
        )

        logger.debug("Added transition %s -> %s to %s.%s", source, target, self.model_class.__name__, self.method_name)
        return self

    def apply(self) -> None:
        """
        Apply the modifications by re-collecting transitions.

        This method must be called after making all modifications to update
        the django-fsm registry.
        """
        field = self.fsm_meta.field
        field._collect_transitions(sender=self.model_class)
        logger.debug("Applied transition modifications for %s.%s", self.model_class.__name__, self.method_name)


# Convenience functions for common patterns


def _resolve_state_value(state_ref: str | int, enum_class: type[DynamicStateEnum]) -> int:
    """Resolve a string state reference to its integer value."""
    return getattr(enum_class, state_ref) if isinstance(state_ref, str) else state_ref


def _build_transitions(
    builder: TransitionBuilder, transitions_config: list[dict[str, Any]], enum_class: type[DynamicStateEnum]
) -> None:
    """Build transitions from configuration."""
    for config in transitions_config:
        source = _resolve_state_value(config["source"], enum_class)
        target = _resolve_state_value(config["target"], enum_class)

        builder.add_transition(
            method_name=config["method_name"],
            source=source,
            target=target,
            method_impl=config.get("method_impl"),
            conditions=config.get("conditions"),
            permission=config.get("permission"),
            on_error=config.get("on_error"),
            custom=config.get("custom"),
        )


def _modify_transitions(
    modifier: TransitionModifier, transition_configs: list[dict[str, Any]], enum_class: type[DynamicStateEnum]
) -> None:
    """Modify transitions from configuration."""
    for trans_config in transition_configs:
        source = _resolve_state_value(trans_config["source"], enum_class)
        target = _resolve_state_value(trans_config["target"], enum_class)

        modifier.add_transition(
            source=source,
            target=target,
            conditions=trans_config.get("conditions"),
            permission=trans_config.get("permission"),
            on_error=trans_config.get("on_error"),
            custom=trans_config.get("custom"),
        )


def create_simple_workflow_extension(
    app_config: AppConfig,
    target_model: str,
    target_enum: str,
    states_to_add: dict[str, int],
    transitions_to_add: list[dict[str, Any]],
    transitions_to_modify: list[dict[str, Any]] | None = None,
) -> bool:
    """
    Create a simple workflow extension without subclassing.

    This function provides a quick way to create workflow extensions for simple cases
    without having to subclass WorkflowExtension.

    Args:
        app_config: The Django AppConfig instance
        target_model: Target model as 'app_label.ModelName'
        target_enum: Target enum as 'module.path.EnumClass'
        states_to_add: Dictionary of state_name -> state_value to add
        transitions_to_add: List of transition configurations
        transitions_to_modify: List of existing transition modifications

    Returns:
        True if extension was applied successfully, False otherwise

    Example:
        create_simple_workflow_extension(
            app_config=self,
            target_model='blog.BlogPost',
            target_enum='blog.models.BlogPostStateEnum',
            states_to_add={'IN_REVIEW': 15, 'APPROVED': 17},
            transitions_to_add=[
                {
                    'method_name': 'send_to_review',
                    'source': 'NEW',  # Will be resolved from enum
                    'target': 'IN_REVIEW'
                }
            ],
            transitions_to_modify=[
                {
                    'method_name': 'publish',
                    'clear_existing': True,
                    'transitions': [{'source': 'APPROVED', 'target': 'PUBLISHED'}]
                }
            ]
        )
    """

    class SimpleWorkflowExtension(WorkflowExtension):
        def extend_states(self, enum_class):
            for name, value in states_to_add.items():
                enum_class.add_state(name, value)

        def extend_transitions(self, model_class, enum_class):
            if transitions_to_add:
                builder = TransitionBuilder(model_class)
                _build_transitions(builder, transitions_to_add, enum_class)
                builder.build_and_attach()

        def modify_existing_transitions(self, model_class, enum_class):
            if not transitions_to_modify:
                return

            for config in transitions_to_modify:
                modifier = TransitionModifier(model_class, config["method_name"])

                if config.get("clear_existing", False):
                    modifier.clear_transitions()

                transition_configs = config.get("transitions", [])
                if transition_configs:
                    _modify_transitions(modifier, transition_configs, enum_class)

                modifier.apply()

    extension = SimpleWorkflowExtension(app_config)
    extension.target_model = target_model
    extension.target_enum = target_enum

    return extension.apply()
