from datetime import timedelta
from django_redis_monitor import models
from django_sched.sched import BaseScheduler
from django_redis_monitor import signals


class SnapshotError(Exception):
    pass


class SnapshotScheduler(BaseScheduler):
    name = "Redis键快照任务调度器"
    interval = 30

    def schedule(self, now):
        tasks = models.KeySnapshotTask.objects.filter(next_run_at__lt=now, enable=True).select_related("key",
                                                                                                       "key__instance")
        errors = {}
        for task in tasks:
            signals.snapshot_started.send(sender=self.__class__, instance=task, now=now)
            snapshot = models.KeySnapshot(
                key=task.key,
                success=True,
                snapshot_time=now
            )
            try:
                snapshot.metrics = self.snapshot_key(task)
                snapshot.save()
            except models.MetricsRequestError as e:
                self.logger.error(f"Snapshot key {task.key.key_name} error: {e}")
                task.last_error = str(e)
                task.last_status = False
                errors[task.key] = str(e)
                signals.snapshot_error.send(sender=self.__class__, task=task, now=now, exception=e)
            task.last_run_at = now
            task.next_run_at = now + timedelta(seconds=task.interval)
            task.save(update_fields=["last_status", "last_error", "last_run_at", "next_run_at"])
            signals.snapshot_ended.send(sender=self.__class__, task=task, snapshot=snapshot, now=now)
        if len(tasks):
            self.logger.info(f"Snapshot finished, total {len(tasks)} tasks")
        if errors:
            error = "; ".join(f"{k.key_name}: {v}" for k, v in errors.items())
            raise SnapshotError(error)

    def snapshot_key(self, task):
        return task.key.get_metrics(using_cache=False)
