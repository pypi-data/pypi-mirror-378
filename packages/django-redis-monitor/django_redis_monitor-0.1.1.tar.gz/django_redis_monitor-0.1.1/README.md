# DjangoRedisMonitor

轻量的 Django 应用，用于管理与监控 Redis 键，支持按任务周期采集 Key 快照并在 Admin 中查看指标与趋势图。

概览
- 配置多 Redis 连接：[`django_redis_monitor.models.RedisInstance`](django_redis_monitor/models.py)
- 注册需要监控的 Key：[`django_redis_monitor.models.MonitoredKey`](django_redis_monitor/models.py)
- 定时采集任务：[`django_redis_monitor.models.KeySnapshotTask`](django_redis_monitor/models.py)
- 采集结果快照：[`django_redis_monitor.models.KeySnapshot`](django_redis_monitor/models.py)
- 后台采集线程：[`django_redis_monitor.snapshot.SnapshotThread`](django_redis_monitor/snapshot.py) / [`django_redis_monitor.snapshot.start_snapshot_threads`](django_redis_monitor/snapshot.py)
- Admin 支持：[`django_redis_monitor.admin.RedisInstanceAdmin`](django_redis_monitor/admin.py)、[`django_redis_monitor.admin.MonitoredKeyAdmin`](django_redis_monitor/admin.py)、[`django_redis_monitor.admin.KeySnapshotTaskAdmin`](django_redis_monitor/admin.py)、[`django_redis_monitor.admin.KeySnapshotAdmin`](django_redis_monitor/admin.py)

快速开始
1. 安装依赖（示例使用 pyproject 中定义的依赖）：
   - 参见 [`pyproject.toml`](pyproject.toml)

2. 数据库迁移与创建管理员：
   - 运行迁移：python manage.py migrate （参见项目入口 [`django_redis_monitor_server/manage.py`](django_redis_monitor_server/manage.py)）
   - 创建超级用户：python manage.py createsuperuser

3. 运行开发服务器：
   - python manage.py runserver
   - 应用在启动时会在 `runserver` 或 `gunicorn` 情况下自动启动后台快照线程（参见 [`django_redis_monitor.apps.DjangoRedisMonitorConfig.ready`](django_redis_monitor/apps.py)）

使用说明（Admin）
- 在 Django Admin 中添加 Redis 实例：参见模型实现 [`django_redis_monitor.models.RedisInstance`](django_redis_monitor/models.py)。
- 为实例添加需要监控的 Key（`MonitoredKey`），并为其创建/关联一个 `KeySnapshotTask` 来配置采集间隔与启用状态（参见 [`django_redis_monitor.models.MonitoredKey`](django_redis_monitor/models.py) 与 [`django_redis_monitor.models.KeySnapshotTask`](django_redis_monitor/models.py)）。
- 在 MonitoredKey 的列表页面可以查看当前指标、历史快照并展示趋势图（实现位于 [`django_redis_monitor/admin.py`](django_redis_monitor/admin.py)）。Admin 使用 Chart.js 渲染趋势图（静态示例在 [`django_redis_monitor/static/admin/js/metrics_chart.js`](django_redis_monitor/static/admin/js/metrics_chart.js)）。

实现细节
- Redis 客户端池由 [`django_redis_monitor.models.RedisInstance.client`](django_redis_monitor/models.py) 管理，避免重复创建连接池。
- Key 指标读取逻辑在 [`django_redis_monitor.models.MonitoredKey.get_metrics`](django_redis_monitor/models.py) 中，根据 `key_type` 使用不同的 Redis 命令（llen / scard / zcard / hlen / xlen）。
- 为减少频繁读取，提供了简易的缓存装饰器 [`django_redis_monitor.models.key_metrics_cache`](django_redis_monitor/models.py)，默认缓存 ttl 可配置（装饰 `get_metrics`）。
- 后台采集线程会查找 `KeySnapshotTask` 中 `next_run_at` 早于当前时间且 `enable=True` 的任务，采集并保存为 `KeySnapshot`（参见 [`django_redis_monitor/snapshot.py`](django_redis_monitor/snapshot.py)）。

注意事项
- 当前配置仅用于开发/内部使用：静态 SECRET_KEY、DEBUG=True、SQLite；生产部署请参考 Django 文档并在 [`django_redis_monitor_server/django_redis_monitor_server/settings.py`](django_redis_monitor_server/django_redis_monitor_server/settings.py) 中调整。
- snapshot 线程在 App.ready 中根据进程参数启动，确保不会在不期望的进程中启动（参见 [`django_redis_monitor/apps.py`](django_redis_monitor/apps.py)）。
- 若需扩展 key 类型或指标，请修改 [`django_redis_monitor.models.MonitoredKey.get_metrics`](django_redis_monitor/models.py)。

项目文件（主要）
- [`django_redis_monitor/models.py`](django_redis_monitor/models.py)
- [`django_redis_monitor/admin.py`](django_redis_monitor/admin.py)
- [`django_redis_monitor/snapshot.py`](django_redis_monitor/snapshot.py)
- [`django_redis_monitor/apps.py`](django_redis_monitor/apps.py)
- [`django_redis_monitor/static/admin/js/metrics_chart.js`](django_redis_monitor/static/admin/js/metrics_chart.js)
- 项目入口与配置：[`django_redis_monitor_server/manage.py`](django_redis_monitor_server/manage.py)、[`django_redis_monitor_server/django_redis_monitor_server/settings.py`](django_redis_monitor_server/django_redis_monitor_server/settings.py)

许可证
- MIT：见 [`LICENSE`](LICENSE)

贡献
- 欢迎提交 issue / PR，改进监控项、错误处理和高并发下的稳定性。