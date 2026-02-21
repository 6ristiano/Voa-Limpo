from decimal import Decimal
from .models import (
    SessaoTreinamento, TipoSessao, TipoAula,
    AlertaSessao, TipoAlertaSessao, SeveridadeAlerta
)

def gerar_alertas_sessao(sessao: SessaoTreinamento):
    if sessao.tipo_sessao != TipoSessao.VOO_REAL:
        return

    # limpa alertas antigos e recalcula (MVP simples)
    sessao.alertas.all().delete()

    b = sessao.baseline_vigente()
    if not b:
        AlertaSessao.objects.create(
            sessao=sessao,
            tipo=TipoAlertaSessao.SEM_BASELINE,
            severidade=SeveridadeAlerta.INFO,
            mensagem="Não há baseline vigente para este tipo de aula/aeronave na data.",
        )
    else:
        if sessao.desvio_pct is not None:
            if sessao.desvio_pct >= Decimal("20"):
                sev = SeveridadeAlerta.CRIT
            elif sessao.desvio_pct >= Decimal("10"):
                sev = SeveridadeAlerta.WARN
            else:
                sev = None

            if sev:
                AlertaSessao.objects.create(
                    sessao=sessao,
                    tipo=TipoAlertaSessao.ACIMA_BASELINE,
                    severidade=sev,
                    mensagem=f"Indicador acima do baseline em {sessao.desvio_pct}%.",
                )

    if sessao.litros_consumidos is None and sessao.lph_snapshot is not None:
        AlertaSessao.objects.create(
            sessao=sessao,
            tipo=TipoAlertaSessao.CONSUMO_ESTIMADO,
            severidade=SeveridadeAlerta.INFO,
            mensagem="Litros não informados; consumo estimado pelo L/h snapshot.",
        )

    if sessao.tipo_aula == TipoAula.TGL and not sessao.toques:
        AlertaSessao.objects.create(
            sessao=sessao,
            tipo=TipoAlertaSessao.DADO_INCOMPLETO,
            severidade=SeveridadeAlerta.WARN,
            mensagem="Tipo de aula TGL sem número de toques informado.",
        )

    if sessao.tipo_aula == TipoAula.NAVEGACAO and not sessao.milhas_nauticas:
        AlertaSessao.objects.create(
            sessao=sessao,
            tipo=TipoAlertaSessao.DADO_INCOMPLETO,
            severidade=SeveridadeAlerta.WARN,
            mensagem="Tipo de aula Navegação sem milhas náuticas informadas.",
        )