from django.apps import AppConfig


class KeysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'keys'
    
    def ready(self):
        import keys.signals