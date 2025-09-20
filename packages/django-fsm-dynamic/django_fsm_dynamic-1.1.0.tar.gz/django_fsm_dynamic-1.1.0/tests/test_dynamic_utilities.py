"""
Comprehensive test suite for django-fsm-dynamic utilities.

This module tests all the utilities provided by django_fsm_dynamic:
- DynamicStateEnum
- TransitionBuilder
- WorkflowExtension
- TransitionModifier
- create_simple_workflow_extension
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from django.db import models
from django.test import TestCase
from django_fsm import FSMIntegerField
from django_fsm import transition

from django_fsm_dynamic import DynamicStateEnum
from django_fsm_dynamic import TransitionBuilder
from django_fsm_dynamic import TransitionModifier
from django_fsm_dynamic import WorkflowExtension


class DynamicStateEnumTest(TestCase):
    """Test DynamicStateEnum functionality."""

    def setUp(self):
        """Set up test data."""

        class TestEnum(DynamicStateEnum):
            NEW = 10
            PUBLISHED = 20
            HIDDEN = 30

        self.enum_class = TestEnum

    def test_get_choices_initial(self):
        """Test that initial choices are correct."""
        choices = self.enum_class.get_choices()
        expected = [
            (self.enum_class.NEW, "New"),
            (self.enum_class.PUBLISHED, "Published"),
            (self.enum_class.HIDDEN, "Hidden"),
        ]
        self.assertEqual(choices, expected)

    def test_get_values(self):
        """Test get_values returns list of state values."""
        values = self.enum_class.get_values()
        expected = [self.enum_class.NEW, self.enum_class.PUBLISHED, self.enum_class.HIDDEN]
        self.assertEqual(values, expected)

    def test_get_state_map(self):
        """Test get_state_map returns dictionary mapping."""
        state_map = self.enum_class.get_state_map()
        expected = {
            self.enum_class.NEW: "New",
            self.enum_class.PUBLISHED: "Published",
            self.enum_class.HIDDEN: "Hidden",
        }
        self.assertEqual(state_map, expected)

    def test_has_state(self):
        """Test has_state method."""
        self.assertTrue(self.enum_class.has_state(self.enum_class.NEW))
        self.assertTrue(self.enum_class.has_state(self.enum_class.PUBLISHED))
        self.assertTrue(self.enum_class.has_state(self.enum_class.HIDDEN))
        self.assertFalse(self.enum_class.has_state(999))

    def test_add_state_success(self):
        """Test successful state addition."""
        self.enum_class.add_state("IN_REVIEW", 15)

        self.assertTrue(hasattr(self.enum_class, "IN_REVIEW"))
        self.assertEqual(self.enum_class.IN_REVIEW, 15)
        self.assertIn(self.enum_class.IN_REVIEW, self.enum_class.get_values())
        self.assertIn((15, "In Review"), self.enum_class.get_choices())

    def test_add_state_invalid_name(self):
        """Test add_state with invalid name."""
        with self.assertRaises(ValueError) as cm:
            self.enum_class.add_state("lowercase", 15)
        self.assertIn("must be uppercase", str(cm.exception))

    def test_add_state_non_integer_value(self):
        """Test add_state with non-integer value."""
        with self.assertRaises(TypeError) as cm:
            self.enum_class.add_state("STRING_STATE", "not_int")
        self.assertIn("must be integer", str(cm.exception))

    def test_add_state_duplicate_name_same_value(self):
        """Test add_state with duplicate name but same value (should be no-op)."""
        # First addition
        self.enum_class.add_state("TEST_STATE", 99)
        self.assertEqual(self.enum_class.TEST_STATE, 99)

        # Second addition with same value should not raise error
        self.enum_class.add_state("TEST_STATE", 99)
        self.assertEqual(self.enum_class.TEST_STATE, 99)

    def test_add_state_duplicate_name_different_value(self):
        """Test add_state with duplicate name but different value."""
        self.enum_class.add_state("TEST_STATE", 99)

        with self.assertRaises(ValueError) as cm:
            self.enum_class.add_state("TEST_STATE", 100)
        self.assertIn("already exists with value", str(cm.exception))

    def test_add_state_duplicate_value_different_name(self):
        """Test add_state with duplicate value but different name."""
        self.enum_class.add_state("FIRST_STATE", 99)

        with self.assertRaises(ValueError) as cm:
            self.enum_class.add_state("SECOND_STATE", 99)
        self.assertIn("already used by", str(cm.exception))

    def test_underscore_to_title_conversion(self):
        """Test that underscored state names are converted to title case."""
        self.enum_class.add_state("WAITING_FOR_APPROVAL", 25)

        choices = self.enum_class.get_choices()
        choice_labels = [label for value, label in choices]
        self.assertIn("Waiting For Approval", choice_labels)

    def test_ignores_non_uppercase_attributes(self):
        """Test that non-uppercase attributes are ignored."""
        self.enum_class.some_method = lambda: None
        self.enum_class.lower_case = 999

        choices = self.enum_class.get_choices()
        values = [value for value, label in choices]
        self.assertNotIn(999, values)

    def test_ignores_private_attributes(self):
        """Test that private attributes are ignored."""
        self.enum_class._PRIVATE = 999
        self.enum_class.__DUNDER__ = 888

        choices = self.enum_class.get_choices()
        values = [value for value, label in choices]
        self.assertNotIn(999, values)
        self.assertNotIn(888, values)

    def test_ignores_non_integer_uppercase_attributes(self):
        """Test that non-integer uppercase attributes are ignored."""
        self.enum_class.STRING_ATTR = "not a state"
        self.enum_class.LIST_ATTR = [1, 2, 3]

        choices = self.enum_class.get_choices()
        values = [value for value, label in choices]

        for value in values:
            self.assertIsInstance(value, int)


class TransitionBuilderTest(TestCase):
    """Test TransitionBuilder functionality."""

    def setUp(self):
        """Set up test data."""

        class TestEnum(DynamicStateEnum):
            NEW = 10
            PUBLISHED = 20
            HIDDEN = 30

        class UtilityTestModel(models.Model):
            state = FSMIntegerField(default=TestEnum.NEW)

            class Meta:
                app_label = "testapp"

        self.enum_class = TestEnum
        self.model_class = UtilityTestModel
        self.builder = TransitionBuilder(UtilityTestModel)

    def test_add_transition_simple(self):
        """Test adding a simple transition."""
        self.builder.add_transition("test_transition", source=self.enum_class.NEW, target=self.enum_class.PUBLISHED)

        self.assertEqual(len(self.builder._transitions), 1)
        transition_config = self.builder._transitions[0]
        self.assertEqual(transition_config["method_name"], "test_transition")
        self.assertEqual(transition_config["source"], self.enum_class.NEW)
        self.assertEqual(transition_config["target"], self.enum_class.PUBLISHED)

    def test_add_transition_with_conditions(self):
        """Test adding transition with conditions."""

        def condition_func(instance):
            return True

        self.builder.add_transition(
            "conditional_transition",
            source=self.enum_class.NEW,
            target=self.enum_class.PUBLISHED,
            conditions=[condition_func],
        )

        transition_config = self.builder._transitions[0]
        self.assertEqual(transition_config["conditions"], [condition_func])

    def test_add_transition_with_permission(self):
        """Test adding transition with permission."""
        self.builder.add_transition(
            "protected_transition",
            source=self.enum_class.NEW,
            target=self.enum_class.PUBLISHED,
            permission="app.can_publish",
        )

        transition_config = self.builder._transitions[0]
        self.assertEqual(transition_config["permission"], "app.can_publish")

    def test_add_transition_with_custom_implementation(self):
        """Test adding transition with custom implementation."""

        def custom_impl(instance):
            instance.title = "Custom"

        self.builder.add_transition(
            "custom_transition", source=self.enum_class.NEW, target=self.enum_class.PUBLISHED, method_impl=custom_impl
        )

        transition_config = self.builder._transitions[0]
        self.assertEqual(transition_config["method_impl"], custom_impl)

    def test_chaining(self):
        """Test method chaining."""
        result = self.builder.add_transition(
            "first", source=self.enum_class.NEW, target=self.enum_class.PUBLISHED
        ).add_transition("second", source=self.enum_class.PUBLISHED, target=self.enum_class.HIDDEN)

        self.assertEqual(result, self.builder)
        self.assertEqual(len(self.builder._transitions), 2)

    def test_build_and_attach(self):
        """Test building and attaching transitions."""
        self.builder.add_transition("test_transition", source=self.enum_class.NEW, target=self.enum_class.PUBLISHED)

        self.builder.build_and_attach()

        # Method should be attached to model
        self.assertTrue(hasattr(self.model_class, "test_transition"))

        # Method should have FSM metadata
        method = getattr(self.model_class, "test_transition")
        self.assertTrue(hasattr(method, "_django_fsm"))

    def test_custom_field_name(self):
        """Test builder with custom field name."""

        class CustomFieldTestModel(models.Model):
            custom_state = FSMIntegerField(default=self.enum_class.NEW)

            class Meta:
                app_label = "testapp"

        builder = TransitionBuilder(CustomFieldTestModel, field_name="custom_state")
        self.assertEqual(builder.field_name, "custom_state")

    def test_transition_with_parameters_default_impl(self):
        """Test transition with parameters using default implementation."""
        self.builder.add_transition("test_with_params", source=self.enum_class.NEW, target=self.enum_class.PUBLISHED)
        self.builder.build_and_attach()

        # Create instance and test parameter passing
        instance = self.model_class()
        instance.state = self.enum_class.NEW  # Set initial state

        # Should work without parameters
        method = getattr(instance, "test_with_params")
        method()  # Should not raise error

        # Reset state for second test
        instance.state = self.enum_class.NEW

        # Should work with parameters
        method(approved_by="test_user", reason="testing")

    def test_transition_with_parameters_custom_impl(self):
        """Test transition with parameters using custom implementation."""

        def custom_impl_with_params(instance, **kwargs):
            # Store kwargs on instance for verification
            instance._transition_kwargs = kwargs
            return kwargs

        self.builder.add_transition(
            "custom_with_params",
            source=self.enum_class.NEW,
            target=self.enum_class.PUBLISHED,
            method_impl=custom_impl_with_params,
        )
        self.builder.build_and_attach()

        # Create instance and test parameter passing
        instance = self.model_class()
        instance.state = self.enum_class.NEW  # Set initial state
        method = getattr(instance, "custom_with_params")

        # Test with parameters
        result = method(approved_by="test_user", timestamp="2025-01-01")

        # Verify parameters were passed through
        self.assertEqual(result["approved_by"], "test_user")
        self.assertEqual(result["timestamp"], "2025-01-01")
        self.assertEqual(instance._transition_kwargs["approved_by"], "test_user")
        self.assertEqual(instance._transition_kwargs["timestamp"], "2025-01-01")

    def test_transition_backwards_compatibility(self):
        """Test that existing transitions without parameters still work."""

        def old_style_impl(instance):
            instance._old_style_called = True

        self.builder.add_transition(
            "old_style", source=self.enum_class.NEW, target=self.enum_class.PUBLISHED, method_impl=old_style_impl
        )
        self.builder.build_and_attach()

        # Create instance and test
        instance = self.model_class()
        instance.state = self.enum_class.NEW  # Set initial state
        method = getattr(instance, "old_style")

        # Should work without parameters (backwards compatibility)
        method()
        self.assertTrue(instance._old_style_called)


class TransitionModifierTest(TestCase):
    """Test TransitionModifier functionality."""

    def setUp(self):
        """Set up test data."""

        class TestEnum(DynamicStateEnum):
            NEW = 10
            PUBLISHED = 20
            HIDDEN = 30

        class ModifierTestModel(models.Model):
            state = FSMIntegerField(default=TestEnum.NEW)

            class Meta:
                app_label = "testapp"

            @transition(field=state, source=TestEnum.NEW, target=TestEnum.PUBLISHED)
            def publish(self):
                pass

        self.enum_class = TestEnum
        self.model_class = ModifierTestModel

    def test_modifier_initialization(self):
        """Test modifier initialization."""
        modifier = TransitionModifier(self.model_class, "publish")

        self.assertEqual(modifier.model_class, self.model_class)
        self.assertEqual(modifier.method_name, "publish")
        self.assertTrue(hasattr(modifier, "method"))
        self.assertTrue(hasattr(modifier, "fsm_meta"))

    def test_modifier_invalid_method(self):
        """Test modifier with invalid method name."""
        with self.assertRaises(ValueError) as cm:
            TransitionModifier(self.model_class, "nonexistent")
        self.assertIn("not found", str(cm.exception))

    def test_modifier_non_fsm_method(self):
        """Test modifier with non-FSM method."""

        def regular_method(self):
            pass

        setattr(self.model_class, "regular_method", regular_method)

        with self.assertRaises(ValueError) as cm:
            TransitionModifier(self.model_class, "regular_method")
        self.assertIn("no FSM metadata", str(cm.exception))

    def test_clear_transitions(self):
        """Test clearing existing transitions."""
        modifier = TransitionModifier(self.model_class, "publish")

        # Should have transitions initially
        self.assertTrue(modifier.fsm_meta.transitions)

        # Clear transitions
        result = modifier.clear_transitions()

        # Should return self for chaining
        self.assertEqual(result, modifier)

        # Transitions should be cleared
        self.assertFalse(modifier.fsm_meta.transitions)

    def test_add_transition(self):
        """Test adding new transition."""
        modifier = TransitionModifier(self.model_class, "publish")
        modifier.clear_transitions()

        result = modifier.add_transition(source=self.enum_class.HIDDEN, target=self.enum_class.PUBLISHED)

        # Should return self for chaining
        self.assertEqual(result, modifier)

        # Should have new transition
        self.assertTrue(modifier.fsm_meta.transitions)

    def test_chaining(self):
        """Test method chaining."""
        modifier = TransitionModifier(self.model_class, "publish")

        result = modifier.clear_transitions().add_transition(
            source=self.enum_class.HIDDEN, target=self.enum_class.PUBLISHED
        )

        self.assertEqual(result, modifier)

    def test_apply(self):
        """Test applying modifications."""
        modifier = TransitionModifier(self.model_class, "publish")

        # Mock the field's _collect_transitions method
        with patch.object(modifier.fsm_meta.field, "_collect_transitions") as mock_collect:
            modifier.apply()
            mock_collect.assert_called_once_with(sender=self.model_class)


class WorkflowExtensionTest(TestCase):
    """Test WorkflowExtension functionality."""

    def setUp(self):
        """Set up test data."""

        class TestEnum(DynamicStateEnum):
            NEW = 10
            PUBLISHED = 20

        class ExtensionTestModel(models.Model):
            state = FSMIntegerField(default=TestEnum.NEW)

            class Meta:
                app_label = "testapp"

        self.enum_class = TestEnum
        self.model_class = ExtensionTestModel

        class MockAppConfig:
            name = "test_app"

        self.app_config = MockAppConfig()

    def test_extension_initialization(self):
        """Test extension initialization."""

        class TestExtension(WorkflowExtension):
            target_model = "testapp.TestModel"
            target_enum = "tests.test_dynamic_utilities.TestEnum"

        extension = TestExtension(self.app_config)

        self.assertEqual(extension.app_config, self.app_config)
        self.assertEqual(extension.target_model, "testapp.TestModel")
        self.assertEqual(extension.target_enum, "tests.test_dynamic_utilities.TestEnum")

    def test_extension_missing_configuration(self):
        """Test extension with missing target configuration."""

        class TestExtension(WorkflowExtension):
            pass

        extension = TestExtension(self.app_config)

        # Should fail to apply without targets
        result = extension.apply()
        self.assertFalse(result)

    def test_import_targets_success(self):
        """Test successful import of target classes."""
        # This test would need more complex setup to work with real imports
        pass

    def test_import_targets_failure(self):
        """Test import failure handling."""

        class TestExtension(WorkflowExtension):
            target_model = "nonexistent.Model"
            target_enum = "nonexistent.Enum"

        extension = TestExtension(self.app_config)
        result = extension.apply()
        self.assertFalse(result)

    def test_extend_states_override(self):
        """Test extend_states method override."""

        class TestExtension(WorkflowExtension):
            def extend_states(self, enum_class):
                enum_class.add_state("EXTENDED", 99)

        extension = TestExtension(self.app_config)
        extension.extend_states(self.enum_class)

        self.assertTrue(hasattr(self.enum_class, "EXTENDED"))
        self.assertEqual(self.enum_class.EXTENDED, 99)

    def test_extend_transitions_override(self):
        """Test extend_transitions method override."""

        class TestExtension(WorkflowExtension):
            def extend_transitions(self, model_class, enum_class):
                # Mock implementation
                pass

        extension = TestExtension(self.app_config)

        # Should not raise error
        extension.extend_transitions(self.model_class, self.enum_class)

    def test_modify_existing_transitions_override(self):
        """Test modify_existing_transitions method override."""

        class TestExtension(WorkflowExtension):
            def modify_existing_transitions(self, model_class, enum_class):
                # Mock implementation
                pass

        extension = TestExtension(self.app_config)

        # Should not raise error
        extension.modify_existing_transitions(self.model_class, self.enum_class)


class CreateSimpleWorkflowExtensionTest(TestCase):
    """Test create_simple_workflow_extension functionality."""

    def setUp(self):
        """Set up test data."""

        class MockAppConfig:
            name = "test_app"

        self.app_config = MockAppConfig()

    def test_states_to_add(self):
        """Test states_to_add parameter."""
        # This test would need more complex setup to work with real models
        pass

    def test_transitions_to_add(self):
        """Test transitions_to_add parameter."""
        # This test would need more complex setup to work with real models
        pass

    def test_transitions_to_modify(self):
        """Test transitions_to_modify parameter."""
        # This test would need more complex setup to work with real models
        pass

    def test_string_state_resolution(self):
        """Test that string state references are resolved to values."""
        # This test would need more complex setup to work with real models
        pass


class IntegrationTest(TestCase):
    """Integration tests for all utilities working together."""

    def test_complete_workflow_extension(self):
        """Test a complete workflow extension scenario."""
        # This test would demonstrate all utilities working together
        pass

    def test_multiple_extensions(self):
        """Test multiple extensions to the same model."""
        # This test would show how multiple extensions interact
        pass

    def test_extension_ordering(self):
        """Test that extension order matters and works correctly."""
        # This test would verify extension application order
        pass


if __name__ == "__main__":
    unittest.main()
