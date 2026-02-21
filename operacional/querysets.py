from decimal import Decimal
from django.db import models
from django.db.models import F, Value, Case, When, DecimalField, ExpressionWrapper
from django.db.models.functions import Cast, Coalesce

DEC_10_4 = DecimalField(max_digits=10, decimal_places=4)
DEC_12_2 = DecimalField(max_digits=12, decimal_places=2)

class SessaoTreinamentoQuerySet(models.QuerySet):
    def with_metrics(self):
        tempo_h = ExpressionWrapper(
            Cast(F("tempo_bloco_min"), DEC_10_4) / Value(Decimal("60")),
            output_field=DEC_10_4,
        )

        litros_est = ExpressionWrapper(
            Cast(F("lph_snapshot"), DEC_10_4) * tempo_h,
            output_field=DEC_12_2,
        )

        litros_calc = Coalesce(F("litros_consumidos"), litros_est, output_field=DEC_12_2)

        co2_calc = ExpressionWrapper(
            litros_calc * Cast(F("fator_co2_snapshot"), DEC_10_4),
            output_field=DEC_12_2,
        )

        lph_calc = Case(
            When(tempo_bloco_min__gt=0, then=ExpressionWrapper(litros_calc / tempo_h, output_field=DEC_12_2)),
            default=None,
            output_field=DEC_12_2,
        )

        l_toque_calc = Case(
            When(toques__gt=0, then=ExpressionWrapper(litros_calc / Cast(F("toques"), DEC_10_4), output_field=DEC_12_2)),
            default=None,
            output_field=DEC_12_2,
        )

        l_100nm_calc = Case(
            When(milhas_nauticas__gt=0, then=ExpressionWrapper(litros_calc / Cast(F("milhas_nauticas"), DEC_10_4) * Value(Decimal("100")), output_field=DEC_12_2)),
            default=None,
            output_field=DEC_12_2,
        )

        return self.annotate(
            tempo_h=tempo_h,
            litros_calc=litros_calc,
            co2_calc=co2_calc,
            lph_calc=lph_calc,
            l_por_toque_calc=l_toque_calc,
            l_100nm_calc=l_100nm_calc,
        )
