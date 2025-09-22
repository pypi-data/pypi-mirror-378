from django.apps import AppConfig


class DjangoLtfiWsapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_ltfi_wsap'
    verbose_name = 'LTFI-WSAP Django Integration'
    
    def ready(self):
        """Initialize WSAP integration when Django starts"""
        from . import signals  # noqa