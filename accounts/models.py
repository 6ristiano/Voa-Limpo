from django.conf import settings
from django.db import models
from core.models import TimeStampedUUIDModel


class Aeroclube(TimeStampedUUIDModel):
    nome = models.CharField(max_length=180)
    cidade = models.CharField(max_length=120, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Aeroclube / Escola"
        verbose_name_plural = "Aeroclubes / Escolas"
        indexes = [models.Index(fields=["nome"])]

    def __str__(self):
        return self.nome


class PapelMembro(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    GESTOR = "GESTOR", "Gestor"
    INSTRUTOR = "INSTRUTOR", "Instrutor"
    ALUNO = "ALUNO", "Aluno"
    LEITOR = "LEITOR", "Leitor"


class MembroAeroclube(TimeStampedUUIDModel):
    aeroclube = models.ForeignKey(Aeroclube, on_delete=models.CASCADE, related_name="membros")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vinculos_voa_limpo")
    papel = models.CharField(max_length=20, choices=PapelMembro.choices)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Membro do aeroclube"
        verbose_name_plural = "Membros do aeroclube"
        constraints = [
            models.UniqueConstraint(fields=["aeroclube", "user"], name="uq_membro_aeroclube_user")
        ]
        indexes = [
            models.Index(fields=["aeroclube", "papel", "ativo"]),
        ]

    def __str__(self):
        return f"{self.user} @ {self.aeroclube} ({self.papel})"
