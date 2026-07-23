#!/usr/bin/env python3
"""
Monitor de Concursos de TI — pesquisa no web (DuckDuckGo, gratuito, sem chave)
os concursos listados em prompt.md, depois usa o Google Gemini para estruturar
o relatório, e salva em reports/AAAA-MM-DD.md.

Requisitos:
    pip install google-genai duckduckgo_search

Variáveis de ambiente necessárias:
    GEMINI_API_KEY  -> sua chave de API do Google AI Studio (aistudio.google.com/apikey)

Uso local:
    python3 concurso_watch.py

Uso no GitHub Actions:
    chamado automaticamente pelo workflow .github/workflows/concurso-watch.yml
"""

import os
import sys
import datetime
import re
from pathlib import Path

try:
    from google import genai
except ImportError:
    print("Faltou instalar a biblioteca: pip install google-genai")
    sys.exit(1)

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print("Faltou instalar a biblioteca: pip install ddgs")
        sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "prompt.md"
REPORTS_DIR = ROOT / "reports"

MODEL = "gemini-3.5-flash"
SEARCH_QUERIES = [
    "concurso Banco do Nordeste BNB TI edital 2026",
    "concurso Petrobras analista sistemas TI edital 2026",
    "concurso TRF5 Tribunal Regional Federal 5 Região TI",
    "concurso TRT6 Tribunal Regional Trabalho Pernambuco TI",
    "concurso ATI-PE Agência Estadual Tecnologia Informação",
    "Dataprev concurso desenvolvimento software edital 2026",
]


def load_prompt() -> str:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    marker = "---\n"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()


def search_web() -> str:
    resultados = []
    with DDGS() as ddgs:
        for query in SEARCH_QUERIES:
            try:
                results = list(ddgs.text(query, max_results=5))
                resultados.append(f"--- Pesquisa: {query} ---")
                for r in results:
                    title = r.get("title", "")
                    body = r.get("body", "")
                    href = r.get("href", "")
                    resultados.append(f"- {title}: {body[:300]}")
                    resultados.append(f"  Fonte: {href}")
            except Exception as e:
                resultados.append(f"--- Pesquisa: {query} ---")
                resultados.append(f"  Erro ao pesquisar: {e}")
            resultados.append("")
    return "\n".join(resultados)


def run_watch() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Defina a variável de ambiente GEMINI_API_KEY antes de rodar.")
        print("Obtenha uma chave gratuita em: https://aistudio.google.com/apikey")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    prompt_text = load_prompt()
    today = datetime.date.today().isoformat()

    print("Pesquisando concursos na web...")
    web_results = search_web()

    user_message = (
        f"Data de hoje: {today}\n\n"
        f"{prompt_text}\n\n"
        f"## Resultados de busca na web (use como base)\n\n"
        f"{web_results}"
    )

    print("Enviando para o Gemini estruturar o relatório...")
    response = client.models.generate_content(
        model=MODEL,
        contents=user_message,
    )

    return response.text.strip()


def save_report(content: str) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    today = datetime.date.today().isoformat()
    out_path = REPORTS_DIR / f"{today}.md"
    out_path.write_text(content, encoding="utf-8")

    latest_path = REPORTS_DIR / "latest.md"
    latest_path.write_text(content, encoding="utf-8")

    return out_path


def main():
    report = run_watch()
    out_path = save_report(report)
    print(f"Relatório salvo em: {out_path}")
    print("\n--- PRÉVIA ---\n")
    print(report[:1500])


if __name__ == "__main__":
    main()
