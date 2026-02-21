from django.contrib import admin

from .models import (
    Aeronave, Aluno, Instrutor,
    ParametroAeroclube, PerfilConsumoAeronave,
    SessaoTreinamento, BaselineConsumo, DicaSOP
)


@admin.register(Aeronave)
class AeronaveAdmin(admin.ModelAdmin):
    list_display = ("aeroclube", "matricula", "modelo", "combustivel", "ativo")
    list_filter = ("aeroclube", "modelo", "combustivel", "ativo")
    search_fields = ("matricula", "modelo")


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("aeroclube", "nome", "matricula", "ativo")
    list_filter = ("aeroclube", "ativo")
    search_fields = ("nome", "matricula")


@admin.register(Instrutor)
class InstrutorAdmin(admin.ModelAdmin):
    list_display = ("aeroclube", "nome", "codigo", "ativo")
    list_filter = ("aeroclube", "ativo")
    search_fields = ("nome", "codigo")


@admin.register(ParametroAeroclube)
class ParametroAeroclubeAdmin(admin.ModelAdmin):
    list_display = ("aeroclube", "ativo_desde", "fator_co2_kg_por_l", "observacao")
    list_filter = ("aeroclube",)
    date_hierarchy = "ativo_desde"


@admin.register(PerfilConsumoAeronave)
class PerfilConsumoAeronaveAdmin(admin.ModelAdmin):
    list_display = ("aeroclube", "aeronave", "ativo_desde", "lph_padrao")
    list_filter = ("aeroclube", "aeronave")
    date_hierarchy = "ativo_desde"


@admin.register(SessaoTreinamento)
class SessaoTreinamentoAdmin(admin.ModelAdmin):
    list_display = (
        "aeroclube", "data", "tipo_sessao", "tipo_aula",
        "aluno", "instrutor", "aeronave", "tempo_bloco_min",
        "litros_consumidos", "col_desvio"
    )
    list_filter = ("aeroclube", "tipo_sessao", "tipo_aula", "aeronave")
    search_fields = ("aluno__nome", "instrutor__nome", "aeronave__matricula")
    date_hierarchy = "data"
    readonly_fields = ("lph_snapshot", "fator_co2_snapshot")

    def col_desvio(self, obj):
        return obj.desvio_pct

    col_desvio.short_description = "Desvio (%)"




@admin.register(BaselineConsumo)
class BaselineConsumoAdmin(admin.ModelAdmin):
    list_display = ("aeroclube", "aeronave", "tipo_aula", "ativo_desde", "indicador_principal", "lph_ref", "l_por_toque_ref", "l_100nm_ref")
    list_filter = ("aeroclube", "aeronave", "tipo_aula", "indicador_principal")
    date_hierarchy = "ativo_desde"






@admin.register(DicaSOP)
class DicaSOPAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo_aula", "tipo_alerta", "aeronave_modelo", "prioridade", "ativo")
    list_filter = ("ativo", "tipo_aula", "tipo_alerta")
    search_fields = ("titulo", "texto", "aeronave_modelo")
    ordering = ("-prioridade", "titulo")
