# controle/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from .models import CasaPrisional, Alojamento


@receiver(post_save, sender=CasaPrisional)
def validate_alojamento(sender, instance, created, **kwargs):
    if instance.tipo_estrutura == "apenas_alojamento":
        if not Alojamento.objects.filter(casa_prisional=instance).exists():
            print(
                f"AVISO: Casa Prisional {instance.nome} com tipo 'apenas_alojamento' não tem alojamentos associados."
            )
            # Adiciona uma mensagem de aviso no admin
            # O request não está diretamente disponível em sinais, então usamos um workaround no admin
