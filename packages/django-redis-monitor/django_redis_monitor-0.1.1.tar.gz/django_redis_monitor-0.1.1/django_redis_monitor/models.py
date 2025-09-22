from functools import wraps
from django.db import models
from django.utils import timezone
from django.core.cache import cache
import redis
import json


def key_metrics_cache(ttl=5):
    def decorator(func):
        @wraps(func)
        def wrapper(model: 'MonitoredKey', **kwargs):
            using_cache = kwargs.pop('using_cache', True)
            kwargs_str = json.dumps(kwargs, sort_keys=True)
            key = f"{func.__name__}:{model.instance.name}:{model.instance.db}:{model.key_name}:{kwargs_str}"
            if using_cache:
                result = cache.get(key)
                if result is not None:
                    return result
            result = func(model, **kwargs)
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator


class MetricsRequestError(Exception):
    """自定义异常，用于表示获取监控数据失败"""
    pass


class RedisInstance(models.Model):
    """支持多 Redis 连接的配置"""
    name = models.CharField(max_length=100, unique=True, verbose_name="实例名称")
    host = models.CharField(max_length=255, verbose_name="Redis 主机")
    port = models.IntegerField(default=6379, verbose_name="端口")
    db = models.IntegerField(default=0, verbose_name="数据库编号")
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name="密码")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    _clients_pool = {}

    @property
    def client(self):
        key = f"{self.host}:{self.port}/{self.db}"
        if key not in RedisInstance._clients_pool:
            pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )
            RedisInstance._clients_pool[key] = redis.Redis(connection_pool=pool)
        return RedisInstance._clients_pool[key]

    class Meta:
        verbose_name = verbose_name_plural = "Redis 实例"
        db_table = "django_redis_instance"

    def __str__(self):
        return f"{self.name}(db={self.db})"


class MonitoredKey(models.Model):
    """需要监控的 Key 配置"""
    KEY_TYPES = [
        # ("string", "String"),
        ("list", "List"),
        ("set", "Set"),
        ("zset", "ZSet"),
        ("hash", "Hash"),
        ("stream", "Stream"),
    ]

    instance = models.ForeignKey(RedisInstance, on_delete=models.CASCADE, related_name="keys", verbose_name="Redis实例")
    key_name = models.CharField(max_length=255, verbose_name="键名")
    key_type = models.CharField(max_length=20, choices=KEY_TYPES, verbose_name="键类型")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    @key_metrics_cache(ttl=10)
    def get_metrics(self) -> dict:
        client = self.instance.client  # 使用 RedisInstance 的连接池
        metrics = {}
        try:
            if self.key_type == "list":
                length = client.llen(self.key_name)
            elif self.key_type == "set":
                length = client.scard(self.key_name)
            elif self.key_type == "zset":
                length = client.zcard(self.key_name)
            elif self.key_type == "hash":
                length = client.hlen(self.key_name)
            elif self.key_type == "stream":
                length = client.xlen(self.key_name)
            else:
                raise MetricsRequestError(f"Unsupported key type: {self.key_type}")
        except Exception as e:
            raise MetricsRequestError(str(e)) from e
        else:
            metrics["length"] = length
        return metrics

    class Meta:
        verbose_name = verbose_name_plural = "监控键"
        unique_together = ("instance", "key_name")
        db_table = "django_redis_monitored_key"

    def __str__(self):
        return f"{self.key_name} ({self.key_type})"


class KeySnapshotTask(models.Model):
    """监控任务配置"""
    key = models.OneToOneField(MonitoredKey, on_delete=models.CASCADE, related_name="snapshot_task", verbose_name="监控键")
    enable = models.BooleanField(default=True, verbose_name="是否启用")
    interval = models.IntegerField(default=5 * 60, verbose_name="采集间隔（秒）")
    next_run_at = models.DateTimeField(default=timezone.now, verbose_name="下次运行时间")
    last_run_at = models.DateTimeField(null=True, blank=True, verbose_name="上次运行时间")
    last_status = models.BooleanField(null=True, blank=True, default=True, verbose_name="上次运行状态")
    last_error = models.TextField(null=True, blank=True, verbose_name="错误信息")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间", db_index=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    @property
    def formatted_interval(self):
        if self.interval < 60:
            return f"每 {self.interval} 秒"
        elif self.interval < 3600:
            minutes = self.interval // 60
            seconds = self.interval % 60
            return f"每 {minutes} 分钟 {seconds} 秒" if seconds else f"每 {minutes} 分种"
        else:
            hours = self.interval // 3600
            minutes = (self.interval % 3600) // 60
            return f"每 {hours} 小时 {minutes} 分种" if minutes else f"每 {hours} 小时"

    class Meta:
        verbose_name = verbose_name_plural = "快照任务"
        db_table = "django_redis_key_snapshot_task"

    def __str__(self):
        return f"快照任务: {self.key.key_name} 每 {self.interval}s"


class KeySnapshot(models.Model):
    """监控时抓取的 Key 状态快照"""
    key = models.ForeignKey(MonitoredKey, on_delete=models.DO_NOTHING, verbose_name="监控键", related_name="snapshots")
    success = models.BooleanField(default=True, verbose_name="成功")
    metrics = models.JSONField(default=dict, verbose_name="监控数据")
    snapshot_time = models.DateTimeField(default=timezone.now, verbose_name="快照时间")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = verbose_name_plural = "键快照"
        db_table = "django_redis_key_snapshot"
        ordering = ["-snapshot_time"]

    def __str__(self):
        return f"{self.key.key_name} @ {self.snapshot_time:%Y-%m-%d %H:%M:%S}"

