from django.apps import AppConfig


class PoolbotServerCoreApp(AppConfig):
    name = 'core'

    def ready(self):
        import core.signals