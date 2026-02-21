from django.urls import path
from .views import painel, detalhe_sessao

urlpatterns = [
    path("", painel, name="painel"),
    path("sessoes/<uuid:pk>/", detalhe_sessao, name="detalhe_sessao"),
]
