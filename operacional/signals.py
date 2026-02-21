from django.db.models.signals import post_save
from django.dispatch import receiver
from operacional.models import SessaoTreinamento
from operacional.services_alertas import gerar_alertas_sessao

@receiver(post_save, sender=SessaoTreinamento)
def sessao_pos_save(sender, instance, **kwargs):
    gerar_alertas_sessao(instance)