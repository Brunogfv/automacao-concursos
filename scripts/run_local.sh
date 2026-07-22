#!/usr/bin/env bash
# Script auxiliar para rodar o monitor localmente e enviar o resultado por
# e-mail (opcional) ou apenas salvar o arquivo em reports/.
#
# Uso manual:
#   ./run_local.sh
#
# Para agendar no cron (Linux/Mac), rode "crontab -e" e adicione uma linha como:
#   0 9 * * 1 /caminho/completo/para/run_local.sh >> /caminho/completo/para/cron.log 2>&1
#   (isso roda toda segunda-feira às 9h)

set -euo pipefail
cd "$(dirname "$0")/.."

if [ -z "${GEMINI_API_KEY:-}" ]; then
    echo "ERRO: defina a variável GEMINI_API_KEY antes de rodar."
    echo "Obtenha uma chave gratuita em: https://aistudio.google.com/apikey"
    echo "Dica: coloque 'export GEMINI_API_KEY=sua_chave_aqui' no seu ~/.bashrc ou ~/.zshrc"
    exit 1
fi

python3 scripts/concurso_watch.py

# --- OPCIONAL: descomente as linhas abaixo para receber por e-mail via 'mail' ---
# (requer o utilitário 'mail'/'mailx' configurado no seu sistema)
#
# REPORT_FILE="reports/latest.md"
# if [ -f "$REPORT_FILE" ]; then
#     mail -s "Monitor de Concursos de TI - $(date +%Y-%m-%d)" seu-email@exemplo.com < "$REPORT_FILE"
# fi
