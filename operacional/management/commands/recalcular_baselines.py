from statistics import median
from django.core.management.base import BaseCommand
from django.db import transaction

from operacional.models import (
    SessaoTreinamento, TipoSessao, TipoAula,
    BaselineConsumo, IndicadorBaseline
)


def _mediana_decimals(valores):
    # median do Python funciona com Decimal
    return median(valores) if valores else None


class Command(BaseCommand):
    help = "Gera/Recalcula BaselinesConsumo automaticamente com base nas sessões (mediana)."

    def add_arguments(self, parser):
        parser.add_argument("--data-ini", type=str, default=None, help="YYYY-MM-DD")
        parser.add_argument("--data-fim", type=str, default=None, help="YYYY-MM-DD")
        parser.add_argument("--n-min", type=int, default=5, help="N mínimo de sessões válidas por grupo")
        parser.add_argument("--force", action="store_true", help="Sobrescreve baseline existente (mesmo ativo_desde)")
        parser.add_argument("--ativo-desde", type=str, default=None, help="YYYY-MM-DD (se não informado, usa data_ini ou a menor data do grupo)")

    def handle(self, *args, **opts):
        data_ini = opts["data_ini"]
        data_fim = opts["data_fim"]
        n_min = opts["n_min"]
        force = opts["force"]
        ativo_desde_param = opts["ativo_desde"]

        qs = SessaoTreinamento.objects.filter(tipo_sessao=TipoSessao.VOO_REAL).select_related(
            "aeroclube", "aeronave"
        )

        if data_ini:
            qs = qs.filter(data__gte=data_ini)
        if data_fim:
            qs = qs.filter(data__lte=data_fim)

        sessoes = list(qs.order_by("data"))
        self.stdout.write(self.style.WARNING(f"Analisando {len(sessoes)} sessões (VOO_REAL)..."))

        # Agrupa por (aeroclube_id, aeronave_id, tipo_aula)
        grupos = {}
        for s in sessoes:
            if not s.aeroclube_id or not s.aeronave_id:
                continue
            key = (s.aeroclube_id, s.aeronave_id, s.tipo_aula)
            grupos.setdefault(key, []).append(s)

        criados = 0
        atualizados = 0
        ignorados = 0

        for (aeroclube_id, aeronave_id, tipo_aula), itens in grupos.items():
            # Decide indicador alvo por tipo_aula
            if tipo_aula == TipoAula.NAVEGACAO:
                indicador = IndicadorBaseline.L_100NM
                valores = [s.l_por_100nm for s in itens if s.l_por_100nm is not None]
                if len(valores) < n_min:
                    # fallback: LPH
                    indicador = IndicadorBaseline.LPH
                    valores = [s.lph for s in itens if s.lph is not None]


            elif tipo_aula == TipoAula.TGL:

                indicador = IndicadorBaseline.LPH

                valores = [s.lph for s in itens if s.lph is not None]

            else:
                # LOCAL e OUTRA: LPH
                indicador = IndicadorBaseline.LPH
                valores = [s.lph for s in itens if s.lph is not None]

            if len(valores) < n_min:
                ignorados += 1
                continue

            ref = _mediana_decimals(valores)
            if ref is None:
                ignorados += 1
                continue

            # Define ativo_desde
            if ativo_desde_param:
                ativo_desde = ativo_desde_param
            elif data_ini:
                ativo_desde = data_ini
            else:
                ativo_desde = str(min(s.data for s in itens))

            # Carrega objetos de referência do grupo
            aeroclube = itens[0].aeroclube
            aeronave = itens[0].aeronave

            defaults = {
                "indicador_principal": indicador,
                "lph_ref": None,
                "l_por_toque_ref": None,
                "l_100nm_ref": None,
                "observacao": f"Gerado automaticamente (mediana) a partir de {len(valores)} sessões."
            }

            if indicador == IndicadorBaseline.LPH:
                defaults["lph_ref"] = ref
            elif indicador == IndicadorBaseline.L_POR_TOQUE:
                defaults["l_por_toque_ref"] = ref
            elif indicador == IndicadorBaseline.L_100NM:
                defaults["l_100nm_ref"] = ref

            with transaction.atomic():
                existente = BaselineConsumo.objects.filter(
                    aeroclube=aeroclube,
                    aeronave=aeronave,
                    tipo_aula=tipo_aula,
                    ativo_desde=ativo_desde,
                ).first()

                if existente and not force:
                    ignorados += 1
                    continue

                if existente and force:
                    for k, v in defaults.items():
                        setattr(existente, k, v)
                    existente.full_clean()
                    existente.save()
                    atualizados += 1
                else:
                    obj = BaselineConsumo(
                        aeroclube=aeroclube,
                        aeronave=aeronave,
                        tipo_aula=tipo_aula,
                        ativo_desde=ativo_desde,
                        **defaults
                    )
                    obj.full_clean()
                    obj.save()
                    criados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Baselines: criados={criados}, atualizados={atualizados}, ignorados={ignorados} (n_min={n_min})."
        ))