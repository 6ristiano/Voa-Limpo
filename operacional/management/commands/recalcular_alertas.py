from django.core.management.base import BaseCommand
from django.db import transaction

from operacional.models import SessaoTreinamento
from operacional.services_alertas import gerar_alertas_sessao


class Command(BaseCommand):
    help = "Recalcula alertas de todas as sessões (ou por período)."

    def add_arguments(self, parser):
        parser.add_argument("--data-ini", type=str, default=None, help="YYYY-MM-DD")
        parser.add_argument("--data-fim", type=str, default=None, help="YYYY-MM-DD")
        parser.add_argument("--limite", type=int, default=None, help="Limita quantidade para teste")

    def handle(self, *args, **options):
        qs = SessaoTreinamento.objects.all().order_by("data")

        data_ini = options["data_ini"]
        data_fim = options["data_fim"]
        limite = options["limite"]

        if data_ini:
            qs = qs.filter(data__gte=data_ini)
        if data_fim:
            qs = qs.filter(data__lte=data_fim)
        if limite:
            qs = qs[:limite]

        total = qs.count() if not limite else len(list(qs))
        self.stdout.write(self.style.WARNING(f"Recalculando alertas para {total} sessões..."))

        ok = 0
        for s in qs.iterator() if not limite else qs:
            with transaction.atomic():
                s.alertas.all().delete()
                gerar_alertas_sessao(s)
            ok += 1
            if ok % 50 == 0:
                self.stdout.write(f"{ok}...")

        self.stdout.write(self.style.SUCCESS(f"Concluído: {ok} sessões."))