from .models import DicaSOP

def recomendar_dicas_sop(sessao, limite=3):
    """
    Retorna uma lista de DicaSOP recomendadas para uma sessão.
    Estratégia: específicas > por tipo_aula > gerais.
    """
    if sessao is None:
        return DicaSOP.objects.none()

    tipo_aula = sessao.tipo_aula
    modelo = (sessao.aeronave.modelo if sessao.aeronave else "") or ""

    alertas = list(sessao.alertas.all())
    tipos_alerta = [a.tipo for a in alertas]

    qs_base = DicaSOP.objects.filter(ativo=True).order_by("-prioridade", "titulo")

    selecionadas = []
    vistos = set()

    def add(qs):
        nonlocal selecionadas
        for d in qs:
            if d.id in vistos:
                continue
            vistos.add(d.id)
            selecionadas.append(d)
            if len(selecionadas) >= limite:
                return True
        return False

    # 1) Dicas específicas por alerta + tipo_aula (+ modelo opcional)
    if tipos_alerta:
        if add(qs_base.filter(tipo_aula=tipo_aula, tipo_alerta__in=tipos_alerta).filter(aeronave_modelo__in=["", modelo])):
            return selecionadas

    # 2) Dicas por tipo_aula (independente do alerta)
    if add(qs_base.filter(tipo_aula=tipo_aula, tipo_alerta="").filter(aeronave_modelo__in=["", modelo])):
        return selecionadas

    # 3) Dicas gerais (sem tipo_aula)
    add(qs_base.filter(tipo_aula="", tipo_alerta="").filter(aeronave_modelo__in=["", modelo]))

    return selecionadas