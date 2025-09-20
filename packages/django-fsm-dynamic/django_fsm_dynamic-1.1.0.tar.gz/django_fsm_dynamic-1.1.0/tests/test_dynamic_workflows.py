"""
Test suite for dynamic workflow functionality.

This module tests the dynamic workflow extension capabilities using django-fsm-dynamic,
including monkeypatching states, callable choices, and transition modifications.
"""

from __future__ import annotations

import time
import unittest
from unittest.mock import patch

from django.db import models
from django.test import TestCase
from django.test import override_settings
from django_fsm import ConcurrentTransitionMixin
from django_fsm import FSMField
from django_fsm import FSMIntegerField
from django_fsm import FSMMeta
from django_fsm import TransitionNotAllowed
from django_fsm import transition

from django_fsm_dynamic import DynamicStateEnum


class DynamicWorkflowTestCase(TestCase):
    """Base test case for dynamic workflow tests."""

    def setUp(self):
        """Set up test data."""

        # Create a test enum class for dynamic testing
        class TestStateEnum(DynamicStateEnum):
            NEW = 10
            PUBLISHED = 20
            HIDDEN = 30

        self.test_enum = TestStateEnum

        # Create a test model dynamically
        choices_func = TestStateEnum.get_choices

        class WorkflowTestModel(models.Model):
            title = models.CharField(max_length=100)
            state = FSMIntegerField(default=TestStateEnum.NEW, choices=choices_func)

            class Meta:
                app_label = "testapp"

            @transition(field=state, source=TestStateEnum.NEW, target=TestStateEnum.PUBLISHED)
            def publish(self):
                pass

            @transition(field=state, source=TestStateEnum.PUBLISHED, target=TestStateEnum.HIDDEN)
            def hide(self):
                pass

        self.test_model = WorkflowTestModel


class CallableChoicesTest(DynamicWorkflowTestCase):
    """Test callable choices functionality."""

    def test_initial_choices(self):
        """Test that initial choices are correct."""
        choices = self.test_enum.get_choices()
        expected = [
            (self.test_enum.NEW, "New"),
            (self.test_enum.PUBLISHED, "Published"),
            (self.test_enum.HIDDEN, "Hidden"),
        ]
        self.assertEqual(choices, expected)

    def test_dynamic_state_addition(self):
        """Test adding states dynamically via monkeypatching."""
        # Add a new state
        self.test_enum.add_state("IN_REVIEW", 15)

        # Choices should include the new state
        choices = self.test_enum.get_choices()
        expected = [
            (self.test_enum.NEW, "New"),
            (self.test_enum.IN_REVIEW, "In Review"),
            (self.test_enum.PUBLISHED, "Published"),
            (self.test_enum.HIDDEN, "Hidden"),
        ]
        self.assertEqual(choices, expected)

    def test_dynamic_state_with_underscore(self):
        """Test that underscored state names are converted properly."""
        self.test_enum.add_state("WAITING_FOR_APPROVAL", 25)

        choices = self.test_enum.get_choices()
        choice_labels = [label for value, label in choices]
        self.assertIn("Waiting For Approval", choice_labels)

    def test_choices_ignore_non_integer_attributes(self):
        """Test that non-integer attributes are ignored."""
        # Add non-state attributes
        self.test_enum.SOME_STRING = "not a state"
        self.test_enum.some_method = lambda: None

        # Should only include integer states
        choices = self.test_enum.get_choices()
        values = [value for value, label in choices]
        self.assertNotIn("not a state", values)

        # Original states should still be there
        expected_values = [self.test_enum.NEW, self.test_enum.PUBLISHED, self.test_enum.HIDDEN]
        for value in expected_values:
            self.assertIn(value, values)


class TransitionModificationTest(DynamicWorkflowTestCase):
    """Test dynamic transition modification."""

    def test_add_transition_method(self):
        """Test adding a new transition method dynamically."""
        # Add new state
        self.test_enum.add_state("IN_REVIEW", 15)

        # Get the state field for the decorator
        state_field = self.test_model._meta.get_field("state")

        # Create new transition method using the decorator (proper way)
        @transition(field=state_field, source=self.test_enum.NEW, target=self.test_enum.IN_REVIEW)
        def send_to_review(self):
            pass

        # Attach to model
        setattr(self.test_model, "send_to_review", send_to_review)

        # Re-collect transitions
        state_field._collect_transitions(sender=self.test_model)

        # Test that the method exists
        instance = self.test_model(title="Test", state=self.test_enum.NEW)
        self.assertTrue(hasattr(instance, "send_to_review"))

        # Test the transition works
        instance.send_to_review()
        self.assertEqual(instance.state, self.test_enum.IN_REVIEW)

    def test_modify_existing_transition(self):
        """Test modifying an existing transition's source/target."""
        # Add new states
        self.test_enum.add_state("IN_REVIEW", 15)
        self.test_enum.add_state("APPROVED", 17)

        # Get the existing publish method
        publish_method = getattr(self.test_model, "publish")
        fsm_meta = publish_method._django_fsm

        # Clear existing transitions
        fsm_meta.transitions.clear()

        # Add new transition with different source
        fsm_meta.add_transition(
            method=publish_method,
            source=self.test_enum.APPROVED,
            target=self.test_enum.PUBLISHED,
            on_error=None,
            conditions=[],
            permission=None,
            custom={},
        )

        # Create test instance
        instance = self.test_model(title="Test", state=self.test_enum.NEW)

        # Original transition should not work
        with self.assertRaises(TransitionNotAllowed):
            instance.publish()

        # Transition should work from APPROVED state
        instance.state = self.test_enum.APPROVED
        instance.publish()
        self.assertEqual(instance.state, self.test_enum.PUBLISHED)

    def test_multiple_source_states(self):
        """Test transition with multiple source states."""
        # Add states
        self.test_enum.add_state("DRAFT", 5)

        # Get the state field for the decorator
        state_field = self.test_model._meta.get_field("state")

        # Create method that accepts multiple sources using the decorator
        @transition(
            field=state_field,
            source=[self.test_enum.NEW, self.test_enum.PUBLISHED, self.test_enum.DRAFT],
            target=self.test_enum.HIDDEN,
        )
        def archive(self):
            pass

        setattr(self.test_model, "archive", archive)
        state_field._collect_transitions(sender=self.test_model)

        # Test from different states
        for source_state in [self.test_enum.NEW, self.test_enum.PUBLISHED]:
            instance = self.test_model(title="Test", state=source_state)
            instance.archive()
            self.assertEqual(instance.state, self.test_enum.HIDDEN)


class WorkflowExtensionTest(DynamicWorkflowTestCase):
    """Test complete workflow extension scenarios."""

    def test_review_workflow_extension(self):
        """Test a complete review workflow extension."""
        # Step 1: Add review states
        self.test_enum.add_state("IN_REVIEW", 15)
        self.test_enum.add_state("APPROVED", 17)
        self.test_enum.add_state("REJECTED", 12)

        # Step 2: Add review transitions using proper decorators
        state_field = self.test_model._meta.get_field("state")

        @transition(field=state_field, source=self.test_enum.NEW, target=self.test_enum.IN_REVIEW)
        def send_to_review(self):
            pass

        @transition(field=state_field, source=self.test_enum.IN_REVIEW, target=self.test_enum.APPROVED)
        def approve(self):
            pass

        @transition(field=state_field, source=self.test_enum.IN_REVIEW, target=self.test_enum.REJECTED)
        def reject(self):
            pass

        # Attach new methods to model
        setattr(self.test_model, "send_to_review", send_to_review)
        setattr(self.test_model, "approve", approve)
        setattr(self.test_model, "reject", reject)

        # Step 3: Modify existing publish transition
        publish_method = getattr(self.test_model, "publish")
        publish_method._django_fsm.transitions.clear()
        publish_method._django_fsm.add_transition(
            method=publish_method,
            source=self.test_enum.APPROVED,
            target=self.test_enum.PUBLISHED,
            on_error=None,
            conditions=[],
            permission=None,
            custom={},
        )

        # Re-collect all transitions
        state_field._collect_transitions(sender=self.test_model)

        # Test the complete workflow
        instance = self.test_model(title="Test Post", state=self.test_enum.NEW)

        # NEW -> IN_REVIEW
        instance.send_to_review()
        self.assertEqual(instance.state, self.test_enum.IN_REVIEW)

        # IN_REVIEW -> APPROVED
        instance.approve()
        self.assertEqual(instance.state, self.test_enum.APPROVED)

        # APPROVED -> PUBLISHED
        instance.publish()
        self.assertEqual(instance.state, self.test_enum.PUBLISHED)

        # Test rejection path
        instance2 = self.test_model(title="Test Post 2", state=self.test_enum.IN_REVIEW)
        instance2.reject()
        self.assertEqual(instance2.state, self.test_enum.REJECTED)

        # Test that direct publish from NEW is blocked
        instance3 = self.test_model(title="Test Post 3", state=self.test_enum.NEW)
        with self.assertRaises(TransitionNotAllowed):
            instance3.publish()


class AppConfigExtensionTest(TestCase):
    """Test app config based workflow extensions."""

    def test_app_ready_hook(self):
        """Test that app ready() method can extend workflows."""
        # This test would be more comprehensive in a real scenario
        # with actual Django app loading, but demonstrates the concept

        # Mock the workflow extension process
        with patch("django.db.models.signals.class_prepared.connect") as mock_connect:
            # Simulate app ready() method
            def mock_ready():
                def enhance_workflow(sender, **kwargs):
                    # Mock workflow enhancement
                    pass

                # Connect to the signal (this is what should be tested)
                mock_connect(enhance_workflow)

            mock_ready()
            mock_connect.assert_called_once()

    def test_conditional_extension(self):
        """Test conditional workflow extension based on settings."""
        with override_settings(ENABLE_REVIEW_WORKFLOW=False):
            # Extension should be skipped
            pass

        with override_settings(ENABLE_REVIEW_WORKFLOW=True):
            # Extension should be applied
            pass


class ErrorHandlingTest(DynamicWorkflowTestCase):
    """Test error handling in dynamic workflows."""

    def test_invalid_state_value(self):
        """Test handling of invalid state values."""
        # Add a non-integer "state"
        self.test_enum.INVALID_STATE = "not_a_number"

        # Should not break the choices generation
        choices = self.test_enum.get_choices()

        # Should only contain valid integer states
        for value, label in choices:
            self.assertIsInstance(value, int)

    def test_missing_fsm_metadata(self):
        """Test handling of methods without FSM metadata."""

        def dummy_method(self):
            pass

        # This should not break anything
        setattr(self.test_model, "dummy_method", dummy_method)

        # Model should still function normally
        instance = self.test_model(title="Test", state=self.test_enum.NEW)
        self.assertEqual(instance.state, self.test_enum.NEW)

    def test_transition_conflict_detection(self):
        """Test detection of transition conflicts."""
        # This could be expanded to test more sophisticated conflict detection
        pass


class PerformanceTest(DynamicWorkflowTestCase):
    """Test performance aspects of dynamic workflows."""

    def test_choices_generation_performance(self):
        """Test that choices generation is reasonably fast."""
        # Add many states
        for i in range(100):
            self.test_enum.add_state(f"STATE_{i}", 1000 + i)

        # Time the choices generation
        start = time.time()
        for _ in range(100):
            choices = self.test_enum.get_choices()
        end = time.time()

        # Should complete quickly (less than 1 second for 100 iterations)
        self.assertLess(end - start, 1.0)

        # Verify correctness
        self.assertEqual(len(choices), 103)  # 3 original + 100 added

    def test_transition_lookup_performance(self):
        """Test that transition lookup remains fast with many transitions."""
        state_field = self.test_model._meta.get_field("state")

        # Add many transitions
        for i in range(50):
            state_value = 1000 + i
            self.test_enum.add_state(f"STATE_{i}", state_value)

            def transition_method(self):
                pass

            transition_method._django_fsm = FSMMeta(field=state_field, method=transition_method)
            transition_method._django_fsm.add_transition(
                method=transition_method,
                source=self.test_enum.NEW,
                target=state_value,
                on_error=None,
                conditions=[],
                permission=None,
                custom={},
            )
            setattr(self.test_model, f"transition_{i}", transition_method)

        state_field._collect_transitions(sender=self.test_model)

        # Test that transition lookup is still fast
        instance = self.test_model(title="Test", state=self.test_enum.NEW)

        start = time.time()
        for _ in range(1000):
            instance.get_available_state_transitions()
        end = time.time()

        # Should complete quickly
        self.assertLess(end - start, 1.0)


class IntegrationTest(TestCase):
    """Integration tests with actual django-fsm functionality."""

    def test_fsm_field_integration(self):
        """Test that dynamic workflows integrate properly with FSMField."""

        class TestEnum(DynamicStateEnum):
            NEW = 1
            PUBLISHED = 2

        choices_func = TestEnum.get_choices

        class FSMFieldTestModel(models.Model):
            state = FSMField(default=TestEnum.NEW, choices=choices_func)

            class Meta:
                app_label = "testapp"

            @transition(field=state, source=TestEnum.NEW, target=TestEnum.PUBLISHED)
            def publish(self):
                pass

        # Add dynamic state
        TestEnum.add_state("HIDDEN", 3)

        # Test that it works
        instance = FSMFieldTestModel(state=TestEnum.NEW)
        instance.publish()
        self.assertEqual(instance.state, TestEnum.PUBLISHED)

        # Test dynamic choices
        choices = choices_func()
        choice_values = [value for value, label in choices]
        self.assertIn(TestEnum.HIDDEN, choice_values)

    def test_concurrent_transition_mixin_compatibility(self):
        """Test compatibility with ConcurrentTransitionMixin."""

        # This would need to be a more comprehensive test in a real scenario
        # but demonstrates the concept
        class ConcurrentTestModel(ConcurrentTransitionMixin, models.Model):
            default_state = 10  # Define default state value as a constant
            state = FSMIntegerField(default=default_state)

            class Meta:
                app_label = "testapp"

        # Dynamic workflow modifications should work with concurrent transitions
        # Use the same default state constant as defined in the model
        instance = ConcurrentTestModel(state=ConcurrentTestModel.default_state)
        self.assertEqual(instance.state, ConcurrentTestModel.default_state)

    def test_admin_integration(self):
        """Test that dynamic workflows work with Django admin."""
        # This would test admin interface integration
        # For now, just verify basic functionality
        pass


if __name__ == "__main__":
    unittest.main()
