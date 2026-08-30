from app.tasks.status import TaskStatus


ALLOWED_TRANSITION = {
    TaskStatus.PENDING: {
        TaskStatus.PROCESSING
    },
    TaskStatus.PROCESSING: {
        TaskStatus.SUCCESS,
        TaskStatus.FAILED
    },
    TaskStatus.FAILED: {
        TaskStatus.PENDING,
    },
    TaskStatus.SUCCESS: set()
}


def can_transition(current_status, target_status):
    return target_status in ALLOWED_TRANSITION.get(
            current_status,
            set()
    )


def transition_task(task, target_status):
    if not can_transition(task.status, target_status):
        raise ValueError(
            f"Invalid task status transition: "
            f"{task.status} -> {target_status}"
        )

    task.status = target_status
    return task
