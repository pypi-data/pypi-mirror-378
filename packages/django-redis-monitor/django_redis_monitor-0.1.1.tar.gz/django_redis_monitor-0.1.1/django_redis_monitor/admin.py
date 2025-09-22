from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html
from django.urls import path
from django.utils.safestring import mark_safe

from . import models


def get_formated_metrics(metrics) -> str:
    args = []
    for key, value in metrics.items():
        args.append(f"{key} = {value}")
    if len(args) == 5:
        args.append("···")
    return format_html('<span style="line-height: 1">%s</span>' % '<br>'.join(args))


@admin.register(models.RedisInstance)
class RedisInstanceAdmin(admin.ModelAdmin):
    list_display = ("name", "host", "port", "db", "is_active", "create_time", "update_time")
    list_filter = ("is_active",)
    search_fields = ("name", "host")
    ordering = ("name",)


@admin.register(models.MonitoredKey)
class MonitoredKeyAdmin(admin.ModelAdmin):
    list_display = ("id", "key_info", "metrics", "snapshot_task_info", "metrics_chart", "update_time")
    list_filter = ("key_type", "instance")
    search_fields = ("key_name", "instance__name")
    ordering = ("instance", "key_name")
    readonly_fields = ("create_time", "update_time")

    def key_info(self, obj: models.MonitoredKey):
        rows = []
        attribute = {
            "redis": obj.instance,
            "键类型": obj.key_type,
            "键名": obj.key_name,
        }
        for key, value in attribute.items():
            rows.append(f'<div style="margin-bottom:8px;">{key}: {value}</div>')
        return format_html(''.join(rows))
    key_info.short_description = "Key 信息"

    def metrics_chart(self, obj: models.MonitoredKey):
        """在 Admin 中嵌入一个 Chart.js 折线图"""
        snapshots = obj.snapshots.filter(success=True)[:10][::-1]  # 最近20条，按时间正序
        if not snapshots:
            return "无数据"
        import json
        labels = [s.snapshot_time.strftime("%H:%M") for s in snapshots]
        values = [s.metrics.get("length", 0) for s in snapshots]
        return format_html(
            """
            <canvas id="chart_{id}" width="400" height="180"></canvas>
            <script>
            (function() {{
                var ctx = document.getElementById("chart_{id}").getContext("2d");
                new Chart(ctx, {{
                    type: "line",
                    data: {{
                        labels: {labels},
                        datasets: [{{
                            label: "Length",
                            data: {values},
                            borderColor: "rgba(75, 192, 192, 1)",
                            backgroundColor: "rgba(75, 192, 192, 0.2)",
                            fill: true,
                            tension: 0.2
                        }}]
                    }},
                    options: {{
                        responsive: false,
                        maintainAspectRatio: true,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            x: {{ title: {{ display: true, text: "时间" }} }},
                            y: {{ title: {{ display: true, text: "数量" }} }}
                        }}
                    }}
                }});
            }})();
            </script>
            """,
            id=obj.pk,
            labels=mark_safe(json.dumps(labels, ensure_ascii=False)),
            values=mark_safe(json.dumps(values)),
        )

    metrics_chart.short_description = "指标趋势图"

    class Media:
        js = ["https://cdn.jsdelivr.net/npm/chart.js"]

    def snapshot_task_info(self, obj: models.MonitoredKey):
        rows = []
        try:
            snapshot_task = obj.snapshot_task
        except models.KeySnapshotTask.DoesNotExist:
            snapshot_task = None
        if snapshot_task:
            rows.append(
                f'<div style="margin-bottom:8px;"><a href="../{models.KeySnapshotTask._meta.model_name}/{snapshot_task.id}/change/">➡️ {snapshot_task.formatted_interval}</a></div>',
            )
        rows.append(
            f'<div style="margin-bottom:8px;"><a href="../{models.KeySnapshot._meta.model_name}/?key__id__exact={obj.pk}">➡️ 历史快照</a></div>',
        )
        return format_html(''.join(rows))

    snapshot_task_info.short_description = "快照任务"


    def related_snapshots(self, obj: models.MonitoredKey):
        return format_html(
            '<a href="{}">历史快照</a>',
            f'',
        )
    related_snapshots.short_description = "历史快照"

    def linked_snapshot_task(self, obj: models.MonitoredKey):
        try:
            snapshot_task = obj.snapshot_task
        except models.KeySnapshotTask.DoesNotExist:
            snapshot_task = None
        if snapshot_task:
            return format_html(
                '<a href="{}">{}</a>',
                f'../{models.KeySnapshotTask._meta.model_name}/{snapshot_task.id}/change/',
                snapshot_task.formatted_interval
            )
        return format_html(
            '<a href="{}">添加</a>',
            f'../{models.KeySnapshotTask._meta.model_name}/add/?key={obj.id}'
        )
    linked_snapshot_task.short_description = "快照任务"


    def refresh_metrics(self, obj):
        return format_html(
            '<a class="button" href="{}">刷新</a>',
            f'./metrics/{obj.id}/'
        )
    refresh_metrics.short_description = "刷新"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'metrics/<int:key_id>/',
                self.admin_site.admin_view(self.request_metrics),
                name='monitored_key-metrics',
            ),
        ]
        return custom_urls + urls

    def request_metrics(self, request, key_id):
        """刷新指定 Key 状态"""
        try:
            key = models.MonitoredKey.objects.get(id=key_id)
            key.get_metrics(using_cache=False)
        except models.MetricsRequestError as e:
            self.message_user(request, f"获取指标异常: {e}", level="error")
        except models.MonitoredKey.DoesNotExist:
            self.message_user(request, "Key不存在", level="error")
        return redirect(request.META.get("HTTP_REFERER", "../"))

    def metrics(self, obj: models.MonitoredKey) -> str:
        try:
            metrics = obj.get_metrics()
        except models.MetricsRequestError as e:
            return str(e)
        return get_formated_metrics(metrics)
    metrics.short_description = "当前状态"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("instance", "snapshot_task")


@admin.register(models.KeySnapshotTask)
class KeySnapshotTaskAdmin(admin.ModelAdmin):
    list_display = ("key", "next_run_at", "interval", "last_run_at", "last_status", "enable", "update_time")
    list_filter = ("interval", "last_status")
    search_fields = ("key__key_name", "key__instance__name")
    ordering = ("key__instance", "key__key_name")
    readonly_fields = ("last_run_at", "last_status", "last_error", "create_time", "update_time")
    fields = (
        ("key", "enable"),
        ("next_run_at", "interval",),
        "last_run_at", "last_status", "last_error", "create_time", "update_time"
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("key", "key__instance")


@admin.register(models.KeySnapshot)
class KeySnapshotAdmin(admin.ModelAdmin):
    list_display = ("key", "admin_metrics", "snapshot_time", "success", "create_time")
    list_filter = ("success", "key__key_name", "key__key_type", "key__instance")
    search_fields = ("key__key_name", "key__instance__name")
    readonly_fields = ("key", "snapshot_time", "success", "metrics", "create_time", "update_time")
    ordering = ("-snapshot_time",)
    fields = ("key", "snapshot_time", "success", "metrics", "create_time", "update_time")

    def admin_metrics(self, obj: models.KeySnapshot):
        return get_formated_metrics(obj.metrics)
    admin_metrics.short_description = "快照数据"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("key", "key__instance")