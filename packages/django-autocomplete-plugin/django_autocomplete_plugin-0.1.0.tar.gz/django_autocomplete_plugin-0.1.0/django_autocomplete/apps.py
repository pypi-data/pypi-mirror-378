from django.apps import AppConfig

class DjangoAutocompleteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_autocomplete'
    
    def ready(self):
        # Auto-generate autocomplete data on startup
        from django.conf import settings
        if not settings.DEBUG:
            from .utils import update_autocomplete_data
            update_autocomplete_data()