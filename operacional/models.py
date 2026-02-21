# operacional/models.py
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from core.models import TimeStampedUUIDModel
from accounts.models import Aeroclube
from django.utils import timezone
from .querysets import SessaoTreinamentoQuerySet



def parametro_vigente(aeroclube, data):
    return (ParametroAeroclube.objects
            .filter(aeroclube=aeroclube, ativo_desde__lte=data)
            .order_by("-ativo_desde")
            .first())

def perfil_consumo_vigente(aeroclube, aeronave, data):
    if not aeronave:
        return None
    return (PerfilConsumoAeronave.objects
            .filter(aeroclube=aeroclube, aeronave=aeronave, ativo_desde__lte=data)
            .order_by("-ativo_desde")
            .first())


class TipoCombustivel(models.TextChoices):
    AVGAS_100LL = "AVGAS_100LL", "AvGas 100LL"
    MOGAS = "MOGAS", "Mogas"
    JET_A1 = "JET_A1", "Jet A-1"
    OUTRO = "OUTRO", "Outro"


class Aeronave(TimeStampedUUIDModel):
    aeroclube = models.ForeignKey(Aeroclube, on_delete=models.CASCADE, related_name="aeronaves")
    matricula = models.CharField(max_length=12, help_text="Ex.: PT-ABC / PR-XYZ")
    modelo = models.CharField(max_length=60, help_text="Ex.: C152 / C172 / PA-28")
    fabricante = models.CharField(max_length=60, blank=True)
    combustivel = models.CharField(max_length=20, choices=TipoCombustivel.choices, default=TipoCombustivel.AVGAS_100LL)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Aeronave"
        verbose_name_plural = "Aeronaves"
        constraints = [
            models.UniqueConstraint(fields=["aeroclube", "matricula"], name="uq_aeronave_aeroclube_matricula"),
        ]
        indexes = [
            models.Index(fields=["aeroclube", "modelo", "ativo"]),
            models.Index(fields=["aeroclube", "matricula"]),
        ]

    def __str__(self):
        return f"{self.matricula} ({self.modelo})"


class Aluno(TimeStampedUUIDModel):
    aeroclube = models.ForeignKey(Aeroclube, on_delete=models.CASCADE, related_name="alunos")
    nome = models.CharField(max_length=160)
    matricula = models.CharField(max_length=40, blank=True, help_text="Matrícula interna do aeroclube (se houver).")
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        indexes = [
            models.Index(fields=["aeroclube", "nome"]),
            models.Index(fields=["aeroclube", "ativo"]),
        ]

    def __str__(self):
        return self.nome


class Instrutor(TimeStampedUUIDModel):
    aeroclube = models.ForeignKey(Aeroclube, on_delete=models.CASCADE, related_name="instrutores")
    nome = models.CharField(max_length=160)
    codigo = models.CharField(max_length=40, blank=True, help_text="Identificador interno/abreviação (opcional).")
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Instrutor"
        verbose_name_plural = "Instrutores"
        indexes = [
            models.Index(fields=["aeroclube", "nome"]),
            models.Index(fields=["aeroclube", "ativo"]),
        ]

    def __str__(self):
        return self.nome


class ParametroAeroclube(TimeStampedUUIDModel):
    aeroclube = models.ForeignKey(Aeroclube, on_delete=models.CASCADE, related_name="parametros")
    ativo_desde = models.DateField()
    fator_co2_kg_por_l = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal("0.0000"))
    observacao = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Parâmetro do aeroclube"
        verbose_name_plural = "Parâmetros do aeroclube"
        constraints = [
            models.UniqueConstraint(fields=["aeroclube", "ativo_desde"], name="uq_parametro_aeroclube_ativo_desde"),
        ]
        indexes = [
            models.Index(fields=["aeroclube", "ativo_desde"]),
        ]

    def __str__(self):
        return f"Parâmetros {self.aeroclube} (desde {self.ativo_desde})"


class PerfilConsumoAeronave(TimeStampedUUIDModel):
    aeroclube = models.ForeignKey(Aeroclube, on_delete=models.CASCADE, related_name="perfis_consumo")
    aeronave = models.ForeignKey(Aeronave, on_delete=models.CASCADE, related_name="perfis_consumo")
    ativo_desde = models.DateField()
    lph_padrao = models.DecimalField(max_digits=6, decimal_places=2, help_text="Litros por hora (referência).")
    observacao = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Perfil de consumo (aeronave)"
        verbose_name_plural = "Perfis de consumo (aeronave)"
        constraints = [
            models.UniqueConstraint(fields=["aeroclube", "aeronave", "ativo_desde"], name="uq_perfil_consumo_vigencia"),
        ]
        indexes = [
            models.Index(fields=["aeroclube", "aeronave", "ativo_desde"]),
        ]

    def __str__(self):
        return f"{self.aeronave} L/h={self.lph_padrao} (desde {self.ativo_desde})"



class IndicadorBaseline(models.TextChoices):
    LPH = "LPH", "L/h"
    L_POR_TOQUE = "L_POR_TOQUE", "L/Toque"
    L_100NM = "L_100NM", "L/100NM"


class TipoSessao(models.TextChoices):
    VOO_REAL = "VOO_REAL", "Voo real"
    SIMULADOR = "SIMULADOR", "Simulador"


class TipoAula(models.TextChoices):
    LOCAL = "LOCAL", "Local"
    NAVEGACAO = "NAVEGACAO", "Navegação"
    TGL = "TGL", "Tráfego / TGL"
    OUTRA = "OUTRA", "Outra"


class TipoTreinoSimulador(models.TextChoices):
    PROCEDIMENTOS = "PROCEDIMENTOS", "Procedimentos"
    MANOBRAS = "MANOBRAS", "Manobras"
    TGL = "TGL", "TGL"
    NAVEGACAO = "NAVEGACAO", "Navegação"
    INSTRUMENTO = "INSTRUMENTO", "Instrumento"
    OUTRO = "OUTRO", "Outro"


class BaselineConsumo(TimeStampedUUIDModel):
    aeroclube = models.ForeignKey(Aeroclube, on_delete=models.CASCADE, related_name="baselines")
    aeronave = models.ForeignKey(Aeronave, on_delete=models.CASCADE, related_name="baselines")

    tipo_aula = models.CharField(max_length=12, choices=TipoAula.choices)
    ativo_desde = models.DateField()

    indicador_principal = models.CharField(max_length=20, choices=IndicadorBaseline.choices)

    # Referências (preencha só as que fizerem sentido)
    lph_ref = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    l_por_toque_ref = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    l_100nm_ref = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    observacao = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Baseline de consumo"
        verbose_name_plural = "Baselines de consumo"
        constraints = [
            models.UniqueConstraint(
                fields=["aeroclube", "aeronave", "tipo_aula", "ativo_desde"],
                name="uq_baseline_vigencia"
            ),
        ]
        indexes = [
            models.Index(fields=["aeroclube", "aeronave", "tipo_aula", "ativo_desde"]),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.indicador_principal == IndicadorBaseline.LPH and self.lph_ref is None:
            errors["lph_ref"] = "Para indicador L/h, informe lph_ref."
        if self.indicador_principal == IndicadorBaseline.L_POR_TOQUE and self.l_por_toque_ref is None:
            errors["l_por_toque_ref"] = "Para indicador L/Toque, informe l_por_toque_ref."
        if self.indicador_principal == IndicadorBaseline.L_100NM and self.l_100nm_ref is None:
            errors["l_100nm_ref"] = "Para indicador L/100NM, informe l_100nm_ref."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.aeronave} {self.tipo_aula} ({self.indicador_principal}) desde {self.ativo_desde}"

    @classmethod
    def vigente(cls, aeroclube, aeronave, tipo_aula, data):
        return (cls.objects
                .filter(aeroclube=aeroclube, aeronave=aeronave, tipo_aula=tipo_aula, ativo_desde__lte=data)
                .order_by("-ativo_desde")
                .first())


class SessaoTreinamento(TimeStampedUUIDModel):
    objects = SessaoTreinamentoQuerySet.as_manager()
    aeroclube = models.ForeignKey(Aeroclube, on_delete=models.CASCADE, related_name="sessoes")

    aluno = models.ForeignKey(Aluno, on_delete=models.PROTECT, related_name="sessoes")
    instrutor = models.ForeignKey(Instrutor, on_delete=models.PROTECT, related_name="sessoes")

    tipo_sessao = models.CharField(max_length=12, choices=TipoSessao.choices)
    tipo_aula = models.CharField(max_length=12, choices=TipoAula.choices, default=TipoAula.OUTRA)

    # Voo real: exige aeronave. Simulador: aeronave deve ser nula.
    aeronave = models.ForeignKey(Aeronave, on_delete=models.PROTECT, null=True, blank=True, related_name="sessoes")

    # Simulador: classifica o treino
    treino_simulador = models.CharField(max_length=20, choices=TipoTreinoSimulador.choices, blank=True)

    data = models.DateField()
    tempo_bloco_min = models.PositiveIntegerField(help_text="Tempo de bloco em minutos (ex.: 65).")

    toques = models.PositiveIntegerField(null=True, blank=True, help_text="Toques/pousos (se aplicável).")
    milhas_nauticas = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="NM (se aplicável).")

    # Litros consumidos (não “abastecidos”). Se não souber, deixa em branco e o sistema estima.
    litros_consumidos = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Snapshots para reprodutibilidade histórica
    lph_snapshot = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fator_co2_snapshot = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)

    # Proxy densidade/condições (opcional)
    temperatura_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    qnh_hpa = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    observacoes = models.TextField(blank=True)

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessoes_criadas",
    )

    class Meta:
        verbose_name = "Sessão de treinamento"
        verbose_name_plural = "Sessões de treinamento"
        indexes = [
            models.Index(fields=["aeroclube", "data"]),
            models.Index(fields=["aeroclube", "tipo_sessao", "data"]),
            models.Index(fields=["aeroclube", "tipo_aula", "data"]),
            models.Index(fields=["aeroclube", "aluno", "data"]),
            models.Index(fields=["aeroclube", "instrutor", "data"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="ck_sessao_voo_real_exige_aeronave",
                check=Q(tipo_sessao=TipoSessao.VOO_REAL, aeronave__isnull=False) | Q(tipo_sessao=TipoSessao.SIMULADOR),
            ),
            models.CheckConstraint(
                name="ck_sessao_simulador_proibe_aeronave",
                check=Q(tipo_sessao=TipoSessao.SIMULADOR, aeronave__isnull=True) | Q(tipo_sessao=TipoSessao.VOO_REAL),
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.tipo_sessao == TipoSessao.VOO_REAL:
            if self.treino_simulador:
                errors["treino_simulador"] = "Este campo é apenas para sessões de SIMULADOR."
        elif self.tipo_sessao == TipoSessao.SIMULADOR:
            if not self.treino_simulador:
                errors["treino_simulador"] = "Para SIMULADOR, informe o tipo de treino."

        if errors:
            raise ValidationError(errors)

    @property
    def tempo_bloco_horas(self) -> Decimal:
        return (Decimal(self.tempo_bloco_min) / Decimal("60"))

    @property
    def litros_utilizados(self) -> Decimal | None:
        """
        Regra: se foi informado, usa; senão estima por L/h snapshot (se existir).
        """
        if self.litros_consumidos is not None:
            return self.litros_consumidos

        if self.lph_snapshot is None:
            return None

        try:
            return (self.tempo_bloco_horas * Decimal(self.lph_snapshot)).quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError):
            return None

    @property
    def lph(self) -> Decimal | None:
        litros = self.litros_utilizados
        if litros is None:
            return None
        horas = self.tempo_bloco_horas
        if horas <= 0:
            return None
        return (litros / horas).quantize(Decimal("0.01"))

    @property
    def l_por_100nm(self) -> Decimal | None:
        litros = self.litros_utilizados
        if litros is None or not self.milhas_nauticas:
            return None
        if self.milhas_nauticas <= 0:
            return None
        return (litros / Decimal(self.milhas_nauticas) * Decimal("100")).quantize(Decimal("0.01"))

    @property
    def l_por_toque(self) -> Decimal | None:
        litros = self.litros_utilizados
        if litros is None or not self.toques:
            return None
        if self.toques <= 0:
            return None
        return (litros / Decimal(self.toques)).quantize(Decimal("0.01"))

    @property
    def co2_kg(self) -> Decimal | None:
        litros = self.litros_utilizados
        if litros is None or self.fator_co2_snapshot is None:
            return None
        return (litros * Decimal(self.fator_co2_snapshot)).quantize(Decimal("0.01"))

    @property
    def indicador_valor(self):
        return self.indicador_principal_valor()

    @property
    def baseline_ref(self):
        return self.indicador_principal_referencia()

    @property
    def indicador_nome(self):
        b = self.baseline_vigente()
        if not b:
            return None
        return dict(IndicadorBaseline.choices).get(b.indicador_principal)

    def __str__(self):
        return f"{self.get_tipo_sessao_display()} {self.data} - {self.aluno} / {self.instrutor}"

    def _carregar_fator_co2_vigente(self):
        from .models import ParametroAeroclube  # se der circular, me avisa e eu ajusto
        p = (ParametroAeroclube.objects
             .filter(aeroclube=self.aeroclube, ativo_desde__lte=self.data)
             .order_by("-ativo_desde")
             .first())
        return p.fator_co2_kg_por_l if p else None

    def _carregar_lph_vigente(self):
        from .models import PerfilConsumoAeronave
        if not self.aeronave:
            return None
        perf = (PerfilConsumoAeronave.objects
                .filter(aeroclube=self.aeroclube, aeronave=self.aeronave, ativo_desde__lte=self.data)
                .order_by("-ativo_desde")
                .first())
        return perf.lph_padrao if perf else None

    def baseline_vigente(self):
        if not (self.data and self.aeroclube and self.aeronave):
            return None
        return BaselineConsumo.vigente(self.aeroclube, self.aeronave, self.tipo_aula, self.data)

    def indicador_principal_valor(self):
        b = self.baseline_vigente()
        if not b:
            return None

        if b.indicador_principal == IndicadorBaseline.LPH:
            return self.lph
        if b.indicador_principal == IndicadorBaseline.L_POR_TOQUE:
            return self.l_por_toque
        if b.indicador_principal == IndicadorBaseline.L_100NM:
            return self.l_por_100nm
        return None

    def indicador_principal_referencia(self):
        b = self.baseline_vigente()
        if not b:
            return None

        if b.indicador_principal == IndicadorBaseline.LPH:
            return b.lph_ref
        if b.indicador_principal == IndicadorBaseline.L_POR_TOQUE:
            return b.l_por_toque_ref
        if b.indicador_principal == IndicadorBaseline.L_100NM:
            return b.l_100nm_ref
        return None

    @property
    def desvio_pct(self):
        """
        (valor - ref) / ref * 100
        """
        valor = self.indicador_principal_valor()
        ref = self.indicador_principal_referencia()
        if valor is None or ref is None:
            return None
        if ref <= 0:
            return None
        try:
            return ((Decimal(valor) - Decimal(ref)) / Decimal(ref) * Decimal("100")).quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError):
            return None

    def save(self, *args, **kwargs):
        # Sanitiza coerência
        if self.tipo_sessao == TipoSessao.VOO_REAL:
            self.treino_simulador = ""

        # Snapshots
        if self.data and self.aeroclube:
            if self.fator_co2_snapshot is None:
                self.fator_co2_snapshot = self._carregar_fator_co2_vigente()

            if self.tipo_sessao == TipoSessao.VOO_REAL and self.lph_snapshot is None:
                self.lph_snapshot = self._carregar_lph_vigente()

        super().save(*args, **kwargs)

        # Gera alertas automaticamente (MVP simples e robusto)
        from .services_alertas import gerar_alertas_sessao
        gerar_alertas_sessao(self)




class SeveridadeAlerta(models.TextChoices):
    INFO = "INFO", "Info"
    WARN = "WARN", "Atenção"
    CRIT = "CRIT", "Crítico"


class TipoAlertaSessao(models.TextChoices):
    SEM_BASELINE = "SEM_BASELINE", "Sem baseline"
    ACIMA_BASELINE = "ACIMA_BASELINE", "Acima do baseline"
    DADO_INCOMPLETO = "DADO_INCOMPLETO", "Dado incompleto"
    CONSUMO_ESTIMADO = "CONSUMO_ESTIMADO", "Consumo estimado"


class AlertaSessao(TimeStampedUUIDModel):
    sessao = models.ForeignKey("SessaoTreinamento", on_delete=models.CASCADE, related_name="alertas")
    tipo = models.CharField(max_length=20, choices=TipoAlertaSessao.choices)
    severidade = models.CharField(max_length=10, choices=SeveridadeAlerta.choices, default=SeveridadeAlerta.INFO)
    mensagem = models.CharField(max_length=220)

    class Meta:
        verbose_name = "Alerta da sessão"
        verbose_name_plural = "Alertas das sessões"
        indexes = [models.Index(fields=["tipo", "severidade"])]

    def __str__(self):
        return f"{self.get_severidade_display()} - {self.get_tipo_display()}"

class DicaSOP(TimeStampedUUIDModel):
    titulo = models.CharField(max_length=120)
    texto = models.TextField()

    tipo_aula = models.CharField(
        max_length=12,
        choices=TipoAula.choices,
        blank=True,
        help_text="Opcional. Se vazio, vale para qualquer tipo de aula."
    )

    tipo_alerta = models.CharField(
        max_length=20,
        choices=TipoAlertaSessao.choices,
        blank=True,
        help_text="Opcional. Se vazio, vale para qualquer alerta."
    )

    aeronave_modelo = models.CharField(
        max_length=60,
        blank=True,
        help_text="Opcional. Ex.: C152. Se vazio, vale para qualquer aeronave."
    )

    prioridade = models.PositiveIntegerField(default=10)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Dica SOP"
        verbose_name_plural = "Dicas SOP"
        indexes = [
            models.Index(fields=["ativo", "prioridade"]),
            models.Index(fields=["tipo_aula", "tipo_alerta"]),
        ]

    def __str__(self):
        return self.titulo