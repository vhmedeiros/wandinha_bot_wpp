# Wandinha-Bot: Secretária Pessoal para WhatsApp com IA

Este projeto tem como objetivo criar um bot de WhatsApp multifuncional chamado "Wandinha", que atua como uma secretária pessoal. O bot será capaz de interagir com APIs do Google (Calendar e Sheets) e utilizará a API Gemini do Google para processamento de linguagem natural e inteligência artificial.

O backend é construído em Python usando o framework FastAPI, e a conexão com o WhatsApp é feita através de uma instância auto-hospedada da Evolution API.

---

## Fase 0: Configuração do Ambiente e Infraestrutura

Esta fase documenta todos os passos necessários para preparar o ambiente de desenvolvimento local e os serviços em nuvem antes do início da codificação. A arquitetura final utiliza um ambiente multi-contêiner totalmente gerenciado com Docker Compose.

### ✅ 1. Ambiente de Desenvolvimento Local

- **Sistema Operacional:** Linux (baseado em Debian/Ubuntu).
- **Linguagem:** Instalado Python 3.10, `python3-pip` e `python3.10-venv`.
- **Containerização:** Instalado Docker e Docker Compose para gerenciamento de serviços.
- **Ferramentas:**
  - VS Code como editor de código, visualizador de Banco de Dados e dos Containers.

### ✅ 2. Infraestrutura de Serviços com Docker Compose

Toda a infraestrutura de backend (banco de dados, cache e a própria API do WhatsApp) é orquestrada por um único arquivo `docker-compose.yml`. Isso garante um ambiente de desenvolvimento consistente, portátil e isolado.

O ambiente é composto por três serviços principais:

- **`db` (PostgreSQL):**
  - **Imagem:** `postgres:15`.
  - **Função:** Banco de dados relacional para armazenamento persistente dos dados da aplicação.
  - **Configuração:** Gerenciada por variáveis no arquivo `.env` e utiliza um volume (`postgres_data`) para persistência dos dados. A porta `5432` é exposta para permitir a conexão via DBeaver.

- **`redis` (Redis Cache):**
  - **Imagem:** `redis:7-alpine`.
  - **Função:** Servidor de cache em memória. Foi adicionado para garantir a estabilidade e a performance da Evolution API, que o utiliza para gerenciar sessões e dados temporários.
  - **Configuração:** Utiliza um volume (`redis_data`) para persistência e um `healthcheck` para garantir que o serviço esteja saudável antes que outros serviços dependentes iniciem.

- **`evolution_api` (API do WhatsApp):**
  - **Imagem:** `atendai/evolution-api:v1.8.0`.
  - **Função:** O coração da nossa conexão com o WhatsApp. É uma API não-oficial que se conecta ao WhatsApp via QR Code.
  - **Configuração:** Foi configurada para se conectar aos serviços `db` e `redis` através da rede interna do Docker. O `depends_on` com `healthcheck` garante a ordem de inicialização correta, prevenindo erros de "condição de corrida". A porta `8080` é exposta para acessarmos sua interface web e documentação.

### ✅ 3. Configuração do Google Cloud Platform (GCP)

- Um novo projeto foi criado no Google Cloud Console.
- As seguintes APIs foram ativadas:
  - **Google Calendar API**
  - **Google Sheets API**
  - **Vertex AI API** (para acesso ao modelo Gemini)
- Foram geradas e salvas duas credenciais distintas para diferentes finalidades:

  - #### **`credentials.json` (ID do Cliente OAuth 2.0)**
    - **Função:** Esta credencial é usada para ações que o bot executa **em nome do usuário**. Pense nela como uma "autorização para um chofer". Para que o bot possa, por exemplo, adicionar um evento na *sua* agenda (Google Calendar) ou ler uma linha da *sua* planilha (Google Sheets), ele precisa da *sua permissão*. Este arquivo gerencia o fluxo de autorização onde você concede essa permissão ao aplicativo.
    - **Uso:** O arquivo `credentials.json` deve ser mantido na raiz do projeto.

  - #### **Chave de API (`GEMINI_API_KEY`) para Vertex AI**
    - **Função:** Esta chave é usada para acesso direto do servidor a uma API pública que não manipula dados privados de um usuário específico. Pense nela como a "chave de um carro de controle remoto". Ela simplesmente autentica nosso programa (o bot) como um usuário válido da API de IA (Gemini), sem precisar da sua permissão a cada pergunta.
    - **Uso:** A chave é armazenada de forma segura no arquivo `.env` (ex: `GEMINI_API_KEY="..."`) e foi restringida no painel do GCP para funcionar exclusivamente com a **Vertex AI API**, aumentando a segurança.

### ✅ 4. Conexão da Evolution API

- **Aviso de Segurança:** Foi utilizado um **número de telefone de teste/descartável** para a conexão, pois o uso de APIs não-oficiais viola os termos de serviço do WhatsApp e acarreta risco de banimento.
- **Processo:**
  1. Acessamos a interface web da API em `http://localhost:8080`.
  2. Criamos uma nova instância, selecionando o canal `Baileys`.
  3. Escaneamos o QR Code gerado usando o aplicativo do WhatsApp no celular de teste (em `Aparelhos Conectados`).
  4. Verificamos a mudança de status da instância para **"Connected"**.

Com a conclusão da Fase 0, a fundação do projeto está sólida e pronta para o início do desenvolvimento do backend em Python na Fase 1.

---

## Fase 1: Containerização do Bot, Webhook e Integração com IA

Nesta fase, o projeto ganhou vida. O objetivo foi criar o serviço do bot em Python, containerizá-lo com Docker, e estabelecer o fluxo completo de comunicação: receber uma mensagem do WhatsApp via Evolution API, processá-la com a IA da Vertex AI (Gemini) e enviar a resposta de volta ao usuário.

### ✅ 1. Containerização do Bot (`wandinha-bot`)

A arquitetura foi solidificada movendo o bot FastAPI para dentro do seu próprio contêiner Docker, gerenciado pelo `docker-compose.yml`.

- **`Dockerfile`:** Foi criado um `Dockerfile` para construir a imagem do nosso bot.
  - **Base:** Utiliza a imagem otimizada `python:3.12-slim`.
  - **Dependências de Build:** Instala o pacote `build-essential` para permitir a compilação de bibliotecas Python que usam código C ou Rust.
  - **Gerenciador de Pacotes:** Instala e utiliza o `uv` para uma instalação de dependências mais rápida a partir do `requirements.txt`.
- **Serviço no Docker Compose:** O bot agora é o serviço `wandinha_bot`, garantindo que ele opere na mesma rede interna que os outros serviços (`db`, `redis`, `evolution_api`), simplificando a comunicação.

### ✅ 2. Módulo de Processamento de IA (Vertex AI)

A inteligência do bot foi implementada em um módulo dedicado.

- **`ai_processor.py`:** Um novo arquivo foi criado para isolar toda a lógica de comunicação com a API da Vertex AI.
- **Autenticação:** O método de autenticação foi corrigido. Em vez de uma Chave de API, agora utilizamos uma **Conta de Serviço (Service Account)**. O arquivo de credenciais (`service-account-key.json`) é passado para o contêiner `wandinha-bot` através da variável de ambiente `GOOGLE_APPLICATION_CREDENTIALS`, definida no `docker-compose.yml`.
- **Função Principal:** A função `get_gemini_response()` recebe o texto da mensagem do usuário, envia para o modelo Gemini e retorna a resposta gerada pela IA.

### ✅ 3. Implementação do Webhook e Lógica de Resposta

O `main.py` foi adaptado para a nova arquitetura e para orquestrar o fluxo de mensagens.

- **Recepção de Webhook:** A rota `POST /webhook` foi configurada para receber as notificações de mensagem (`messages.upsert`) enviadas pelo serviço `evolution_api`.
- **Análise do Payload:** O código agora é capaz de analisar a estrutura JSON da Evolution API, extrair o número do remetente (`remoteJid`) e o texto da mensagem (seja de um `conversation` ou `extendedTextMessage`).
- **Orquestração do Fluxo:** Ao receber uma mensagem, o `main.py` agora executa a seguinte sequência:
  1. Extrai o texto da mensagem do usuário.
  2. Chama a função `get_gemini_response()` do `ai_processor.py`.
  3. Envia a resposta retornada pela IA de volta ao usuário através da função `send_evolution_message()`.
- **Envio de Resposta:** A função de envio foi reescrita para fazer uma requisição `POST` para o serviço `evolution_api` na rede interna do Docker (`http://evolution_api:8080`), utilizando a `AUTHENTICATION_API_KEY` para autorização.

### ⚠️ 4. Desafio e Solução: Comunicação Interna no Docker

O principal desafio da Fase 1 foi garantir que a `evolution_api` conseguisse enviar os webhooks para o contêiner `wandinha_bot`. Após uma longa investigação, a causa raiz foi identificada:

- **O Problema:** A Evolution API possui uma validação interna de URL de webhook que **não aceita underscores (`_`)** no nome do host, pois isso viola a especificação RFC para hostnames. Nosso serviço, inicialmente nomeado `wandinha_bot`, estava sendo rejeitado.
- **A Solução:** Foi necessário renomear o serviço e o nome do contêiner para usar um hífen, tornando-o compatível com a validação.

A configuração final e funcional no `docker-compose.yml` ficou assim:

```yaml
services:
  wandinha-bot: # <-- Uso de hífen no nome do serviço
    container_name: wandinha-bot # <-- Uso de hífen no nome do contêiner
    build: .
    # ... resto da configuração do serviço

  evolution_api:
    environment:
      # Aponta para o nome do serviço corrigido
      - WEBHOOK_GLOBAL_URL=http://wandinha-bot:8000/webhook
      - WEBHOOK_GLOBAL_EVENTS=MESSAGES_UPSERT
      # ...