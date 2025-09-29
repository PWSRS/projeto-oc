# controle/apps.py
from django.apps import AppConfig


class ControleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "controle"

    def ready(self):
        import controle.signals  # Importa os sinais
