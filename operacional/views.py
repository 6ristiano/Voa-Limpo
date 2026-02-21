from datetime import date
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count, Max, Case, When, IntegerField, Value
from django.shortcuts import render, get_object_or_404
from .models import SessaoTreinamento, Aeronave, TipoAula, TipoSessao
from .services_sop import recomendar_dicas_sop
from django.shortcuts import render

@login_required
def painel(request):
    # filtros simples por GET
    data_ini = request.GET.get("data_ini")
    data_fim = request.GET.get("data_fim")
    aeronave_id = request.GET.get("aeronave")
    tipo_aula = request.GET.get("tipo_aula")

    qs = SessaoTreinamento.objects.filter(tipo_sessao=TipoSessao.VOO_REAL)

    if data_ini:
        qs = qs.filter(data__gte=data_ini)
    if data_fim:
        qs = qs.filter(data__lte=data_fim)
    if aeronave_id:
        qs = qs.filter(aeronave_id=aeronave_id)
    if tipo_aula:
        qs = qs.filter(tipo_aula=tipo_aula)

    qs = qs.with_metrics()

    resumo = qs.aggregate(
        n=Count("id"),
        litros=Sum("litros_calc"),
        co2=Sum("co2_calc"),
        lph=Avg("lph_calc"),
        l_toque=Avg("l_por_toque_calc"),
        l_100nm=Avg("l_100nm_calc"),
    )

    # lista curta para demo
    ultimas = (
        qs.with_metrics()
        .prefetch_related("alertas")
        .annotate(
            alertas_n=Count("alertas", distinct=True),
            alerta_nivel=Max(
                Case(
                    When(alertas__severidade="CRIT", then=Value(3)),
                    When(alertas__severidade="WARN", then=Value(2)),
                    When(alertas__severidade="INFO", then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
        )
        .order_by("-data")[:20]
    )

    return render(request, "painel.html", {
        "resumo": resumo,
        "ultimas": ultimas,
        "aeronaves": Aeronave.objects.all().order_by("modelo", "matricula"),
        "tipos_aula": TipoAula.choices,
        "filtros": {"data_ini": data_ini, "data_fim": data_fim, "aeronave": aeronave_id, "tipo_aula": tipo_aula},
    })

@login_required
def detalhe_sessao(request, pk):
    s = get_object_or_404(
        SessaoTreinamento.objects.with_metrics().prefetch_related("alertas"),
        pk=pk
    )
    dicas = recomendar_dicas_sop(s, limite=3)
    return render(request, "sessao_detalhe.html", {"s": s, "dicas": dicas})


@login_required
def home(request):
    return render(request, "home.html")

@login_required
def cadastros(request):
    return render(request, "cadastros.html")