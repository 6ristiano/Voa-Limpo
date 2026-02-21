from django.contrib import admin
from .models import Aeroclube, MembroAeroclube

@admin.register(Aeroclube)
class AeroclubeAdmin(admin.ModelAdmin):
    list_display = ("nome", "cidade", "estado", "ativo", "criado_em")
    list_filter = ("ativo", "estado")
    search_fields = ("nome", "cidade")

@admin.register(MembroAeroclube)
class MembroAeroclubeAdmin(admin.ModelAdmin):
    list_display = ("aeroclube", "user", "papel", "ativo", "criado_em")
    list_filter = ("papel", "ativo", "aeroclube")
    search_fields = ("user__username", "user__email", "aeroclube__nome")