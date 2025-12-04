# WebFetchMailer

Agente simples que busca notícias em RSS, extrai o conteúdo das páginas, gera um resumo em HTML usando `Gemini` e envia por email via SMTP. Ideal para um boletim diário de tecnologia.

## Visão Geral

- Busca links em `Bing News RSS` com base no tópico (`TOPIC`).
- Faz a extração de texto relevante com `trafilatura`.
- Gera um HTML de newsletter usando `google-generativeai` (Gemini).
- Envia o resultado por email usando `SMTP` do Gmail.

Principais funções:
- `search_web` em `main.py:21` — consulta RSS do Bing e retorna links.
- `scrape_content` em `main.py:42` — extrai texto limpo das páginas.
- `send_email` em `main.py:52` — envia o HTML por email.
- `generate_newsletter` em `main.py:83` — orquestra o fluxo e é o ponto de entrada chamado em `main.py:132`.

## Pré‑requisitos

- `Python 3.9+`
- Conta Gmail (recomenda‑se usar `App Password` com 2FA)
- Chave de API do `Gemini`

## Instalação

```bash
# Clonar o projeto (se aplicável)
# git clone <repo>
# cd WebFetchMailer

# Criar e ativar um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows PowerShell

# Instalar dependências
pip install -r requirements.txt

# Dependência adicional necessária (não listada no requirements.txt)
pip install trafilatura
```

## Configuração

Crie um arquivo `.env` na raiz (baseado em `.env.example`) com as variáveis:

```env
# Gemini
GEMINI_API_KEY=suachave
TOPIC=tecnologia

# Email (Gmail SMTP)
EMAIL_FROM=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_ou_app_password
EMAIL_TO=destinatario@gmail.com
```

## Uso

```bash
# Com o ambiente virtual ativado e .env configurado
python main.py
```

- O script irá:
  - Buscar até 5 links no RSS do Bing para o tópico configurado.
  - Extrair o texto das páginas.
  - Gerar HTML de newsletter via `Gemini` (`gemini-2.0-flash`).
  - Enviar o HTML por email.

## Agendamento (Opcional)

Para executar diariamente às 8h via `cron` (macOS/Linux):

```bash
crontab -e
# Exemplo de entrada:
0 8 * * * cd /Users/victorhugo/Documents/WebFetchMailer && /Users/victorhugo/Documents/WebFetchMailer/.venv/bin/python main.py >> /Users/victorhugo/Documents/WebFetchMailer/cron.log 2>&1
```

## Estrutura

```
.
├── main.py            # Fluxo principal e funções
├── requirements.txt   # Dependências de Python
├── .env.example       # Exemplo de variáveis de ambiente
└── README.md          # Este arquivo
```

## Erros Comuns

- `❌ Credenciais de email não configuradas no .env` — adicione `EMAIL_FROM`, `EMAIL_PASSWORD`, `EMAIL_TO`.
- `❌ Erro no Gemini` — verifique `GEMINI_API_KEY` e cotas de uso.
- `❌ Erro ao enviar email` — use `App Password` do Gmail (com 2FA) ou confirme que o SMTP está acessível.
- Conteúdo vazio em `scrape_content` — algumas páginas bloqueiam scraping; tente outro link.

## Segurança

- Não compartilhe sua `GEMINI_API_KEY` e credenciais de email.
- Prefira `App Password` no Gmail com autenticação em dois fatores.
- Evite logar conteúdo sensível; o projeto já não grava segredos em arquivos.

## Licença

Defina a licença do projeto conforme sua preferência (MIT, Apache‑2.0, etc.).

