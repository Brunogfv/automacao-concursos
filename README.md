# Monitor de Concursos de TI — Automação

Este pacote monitora periodicamente o status de concursos de TI relevantes (Banco do Nordeste,
Petrobras, TRF5, TRT6-PE, ATI-PE, Dataprev) usando uma IA com acesso à busca na web, e gera um
relatório em Markdown. Duas formas de rodar: **GitHub Actions** (na nuvem, recomendado) ou
**localmente no seu computador** (via cron).

## Estrutura de arquivos

```
automacao-concursos/
├── prompt.md                          # o prompt usado pela IA (pode editar à vontade)
├── README.md                          # este arquivo
├── scripts/
│   ├── concurso_watch.py              # script principal (chama a API do Google Gemini)
│   └── run_local.sh                   # wrapper para rodar localmente / agendar no cron
├── reports/                           # relatórios gerados (criado automaticamente)
└── .github/workflows/
    └── concurso-watch.yml             # workflow do GitHub Actions (roda toda segunda-feira)
```

---

## Opção A — Rodar no GitHub Actions (recomendado, não precisa do seu PC ligado)

1. **Crie um repositório novo no GitHub** (pode ser privado) e suba esta pasta inteira para ele:
   ```bash
   cd automacao-concursos
   git init
   git add .
   git commit -m "Setup inicial do monitor de concursos"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPO.git
   git push -u origin main
   ```

2. **Gere uma chave de API do Google Gemini (gratuita)** em https://aistudio.google.com/apikey
   (crie com sua conta Google, é de graça e tem cota generosa para uso semanal).

3. **Cadastre a chave como "Secret" no repositório:**
   - Vá em `Settings` → `Secrets and variables` → `Actions` → `New repository secret`
   - Nome: `GEMINI_API_KEY`
   - Valor: cole sua chave

4. **Habilite as Issues do repositório** (se não estiverem habilitadas):
   `Settings` → `General` → seção `Features` → marque `Issues`

5. Pronto. O workflow já está configurado para rodar **toda segunda-feira às 9h (horário de
   Brasília)**. Cada execução:
   - Roda o script, que pesquisa na web e gera o relatório
   - Salva o relatório em `reports/AAAA-MM-DD.md` e commita no repositório (fica seu histórico)
   - Abre uma **Issue** no repositório com o conteúdo do relatório — e o GitHub te manda um
     e-mail automático sempre que uma issue nova é criada (se você estiver "watching" o repo)

6. **Para testar sem esperar a segunda-feira:** vá na aba `Actions` do repositório, clique no
   workflow "Monitor de Concursos de TI" e depois em `Run workflow` (botão manual).

7. **Para mudar a frequência:** edite a linha `cron:` em
   `.github/workflows/concurso-watch.yml`. Exemplos:
   - `0 12 * * 1` → toda segunda-feira às 9h de Brasília
   - `0 12 1,15 * *` → todo dia 1 e 15 do mês às 9h de Brasília
   - `0 12 * * *` → todo dia às 9h de Brasília (não recomendado, editais não mudam tão rápido)

---

## Opção B — Rodar localmente no seu computador (via cron)

1. Instale as dependências Python:
   ```bash
   pip install google-genai duckduckgo_search
   ```

2. Defina sua chave de API como variável de ambiente (adicione ao `~/.bashrc` ou `~/.zshrc`
   para não precisar repetir toda vez):
   ```bash
   export GEMINI_API_KEY="sua_chave_aqui"
   ```

3. Dê permissão de execução ao script:
   ```bash
   chmod +x scripts/run_local.sh
   ```

4. Teste rodando manualmente:
   ```bash
   ./scripts/run_local.sh
   ```
   O relatório será salvo em `reports/AAAA-MM-DD.md` e `reports/latest.md`.

5. Para automatizar com **cron** (Linux/Mac), rode `crontab -e` e adicione:
   ```
   0 9 * * 1 /caminho/completo/para/automacao-concursos/scripts/run_local.sh >> /caminho/completo/para/automacao-concursos/cron.log 2>&1
   ```
   Isso roda toda segunda-feira às 9h. Ajuste o caminho para o local real da pasta no seu PC.

   No Windows, o equivalente é o **Agendador de Tarefas** (Task Scheduler), apontando para rodar
   `run_local.sh` via WSL/Git Bash, ou adaptando o script para `.ps1`/`.bat` se preferir.

---

## Como ler os relatórios

Cada relatório segue o formato definido em `prompt.md`: status por órgão, vagas, salário,
datas, fonte e nível de confiança da informação. Sempre confira a fonte linkada antes de tomar
qualquer decisão — a IA pode errar ou encontrar informação desatualizada, então trate o
relatório como um **alerta para investigar**, não como fato definitivo.

## Editando o que é monitorado

Para adicionar ou remover órgãos da lista, edite a seção "Órgãos a monitorar" em `prompt.md`.
Não precisa mexer em nenhum script — o prompt é lido dinamicamente a cada execução.
