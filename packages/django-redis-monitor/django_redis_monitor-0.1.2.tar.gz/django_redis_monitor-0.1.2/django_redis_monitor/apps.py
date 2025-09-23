from django.apps import AppConfig
import logging


class DjangoRedisMonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_redis_monitor'
    verbose_name = "Redis键管理"

    def ready(self):
        logger = logging.getLogger(self.name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(levelname)s] %(asctime)s %(name)s %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
