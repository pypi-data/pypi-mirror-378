from django.dispatch import Signal


__all__ = [
    "snapshot_started",
    "snapshot_ended",
    "snapshot_error",
]


# 内置调度器的生命周期
snapshot_started = Signal()         # payload: scheduler, task, now
snapshot_ended = Signal()           # payload: scheduler, task, now, snapshot
snapshot_error = Signal()           # payload: scheduler, task, now, exception
