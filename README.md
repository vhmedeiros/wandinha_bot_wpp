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