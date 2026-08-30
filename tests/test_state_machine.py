import pytest
from app.tasks.state_machine import can_transition, transition_task
from app.tasks.status import TaskStatus


class MockTask:
    def __init__(self, status):
        self.status = status


def test_pending_to_processing():
    task = MockTask(TaskStatus.PENDING)
    transition_task(task, TaskStatus.PROCESSING)
    assert task.status == TaskStatus.PROCESSING


def test_processing_to_success():
    task = MockTask(TaskStatus.PROCESSING)
    transition_task(task, TaskStatus.SUCCESS)
    assert task.status == TaskStatus.SUCCESS


def test_processing_to_failure():
    task = MockTask(TaskStatus.PROCESSING)
    transition_task(task, TaskStatus.FAILED)
    assert task.status == TaskStatus.FAILED


def test_failure_to_pending():
    task = MockTask(TaskStatus.FAILED)
    transition_task(task, TaskStatus.PENDING)
    assert task.status == TaskStatus.PENDING


def test_success_cannot_to_processing():
    task = MockTask(TaskStatus.SUCCESS)

    with pytest.raises(ValueError):
        transition_task(task, TaskStatus.PROCESSING)


def test_pending_cannot_to_success():
    task = MockTask(TaskStatus.PENDING)

    with pytest.raises(ValueError):
        transition_task(task, TaskStatus.SUCCESS)


def test_failed_cannot_to_success():
    task = MockTask(TaskStatus.FAILED)

    with pytest.raises(ValueError):
        transition_task(task, TaskStatus.SUCCESS)


def test_can_transition():
    assert can_transition(
        TaskStatus.PENDING,
        TaskStatus.PROCESSING
    )

    assert can_transition(
        TaskStatus.PROCESSING,
        TaskStatus.SUCCESS
    )

    assert not can_transition(
        TaskStatus.SUCCESS,
        TaskStatus.PROCESSING
    )
