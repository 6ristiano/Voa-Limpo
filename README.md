cat > README.md <<'EOF'
# Voa Limpo (MVP)

MVP acadêmico para medir eficiência operacional e apoiar cultura de economia de combustível na instrução de voo.

## Setup (dev)
1. Crie e ative um venv
2. Instale dependências:
   - `pip install -r requirements.txt`
3. Copie `.env.example` para `.env` e ajuste valores
4. Migre e rode:
   - `python manage.py migrate`
   - `python manage.py runserver`

## Rotas
- `/` Início
- `/painel/` Painel
- `/cadastros/` Cadastros (atalhos)
- `/admin/` Django Admin
EOF

git add README.md
git commit -m "Add README"
git push
