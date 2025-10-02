# Wandinha-Bot: Secretária Pessoal para WhatsApp com IA

Este projeto tem como objetivo criar um bot de WhatsApp multifuncional chamado "Wandinha", que atua como uma secretária pessoal. O bot será capaz de interagir com APIs do Google (Calendar e Sheets) e utilizará a API Gemini do Google para processamento de linguagem natural e inteligência artificial.

O backend é construído em Python usando o framework FastAPI.

---

## Fase 0: Configuração do Ambiente e Infraestrutura

Esta fase documenta todos os passos necessários para preparar o ambiente de desenvolvimento local e os serviços em nuvem antes do início da codificação.

### ✅ 1. Ambiente de Desenvolvimento Local

- **Sistema Operacional:** Linux (baseado em Debian/Ubuntu).
- **Linguagem:** Instalado Python 3.10, `python3-pip` e `python3.10-venv`.
- **Containerização:** Instalado Docker e Docker Compose para gerenciamento de serviços.
- **Ferramentas:**
  - VS Code como editor de código principal.
  - DBeaver como cliente de banco de dados para PostgreSQL.

### ✅ 2. Banco de Dados com Docker

- Foi criado um arquivo `docker-compose.yml` para definir o serviço do banco de dados.
- **Serviço:** PostgreSQL, utilizando a imagem oficial `postgres:15`.
- **Configuração:** As credenciais do banco (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) são gerenciadas através de um arquivo `.env` para segurança.
- **Persistência de Dados:** Foi configurado um volume Docker (`postgres_data`) para garantir que os dados não sejam perdidos ao reiniciar o contêiner.
- **Acesso:** A porta `5432` do contêiner foi mapeada para a porta `5432` do host local, permitindo a conexão via DBeaver.

### ✅ 3. Configuração do Google Cloud Platform (GCP)

- Um novo projeto foi criado no Google Cloud Console.
- As seguintes APIs foram ativadas:
  - **Google Calendar API**
  - **Google Sheets API**
  - **Vertex AI API** (para acesso ao modelo Gemini)
- Foram geradas e salvas as seguintes credenciais:
  - **Credenciais de OAuth 2.0 (Client ID):** Salvas como `credentials.json` para acesso ao Calendar e Sheets.
  - **Chave de API (API Key):** Adicionada ao arquivo `.env` para autenticação com a API do Gemini.

### ✅ 4. Configuração da Plataforma Meta for Developers (WhatsApp)

- Um novo aplicativo do tipo "Negócios" foi criado no painel da Meta.
- O produto "WhatsApp" foi adicionado e configurado no aplicativo.
- Os seguintes valores essenciais foram obtidos e adicionados ao arquivo `.env`:
  - **Token de Acesso Temporário**
  - **ID do Número de Telefone de Teste**
  - **ID da Conta do WhatsApp Business**

Com a conclusão da Fase 0, a fundação do projeto está sólida e pronta para o início do desenvolvimento do backend na Fase 1.


---

## Fase 1: Conexão Inicial e Webhook com FastAPI

Esta fase foca em criar o esqueleto da aplicação com FastAPI e estabelecer a comunicação bidirecional com a API de Nuvem do WhatsApp, culminando em um bot que pode receber uma mensagem e ecoar uma resposta.

### ✅ 1. Estrutura do Projeto e Servidor Web

- **Ambiente Virtual:** Foi configurado um ambiente virtual Python (`venv`) para isolar as dependências do projeto.
- **Bibliotecas Instaladas:** As dependências iniciais foram instaladas via `uv`, incluindo `fastapi`, `uvicorn`, `python-dotenv` e `requests`.
- **Servidor Básico:** Criado o arquivo `main.py` com uma instância do FastAPI, servido localmente com Uvicorn.

### ✅ 2. Implementação do Webhook do WhatsApp

- **Endpoint de Verificação (GET):** Foi implementada a rota `GET /webhook` para que a plataforma da Meta pudesse verificar a autenticidade do endpoint. A lógica lida com os parâmetros `hub.mode`, `hub.verify_token` e `hub.challenge`.
- **Endpoint de Recebimento (POST):** Foi implementada a rota `POST /webhook` para receber e processar as notificações de mensagens enviadas pelo WhatsApp. A função foi configurada para extrair e exibir o payload JSON completo para fins de depuração.

### ✅ 3. Expondo o Servidor Local com Ngrok

- **Túnel Seguro:** A ferramenta `ngrok` foi instalada e utilizada para expor a porta local (`8000`) do servidor FastAPI para a internet através de uma URL pública `https`. Comando 'ngronk http <porta>'
- **Configuração na Meta:** A URL gerada pelo `ngrok` foi configurada como a "URL de callback" no painel do aplicativo da Meta.

### ✅ 4. Lógica de Resposta (Eco)

- **Análise do Payload:** O código do endpoint `POST /webhook` foi expandido para navegar na estrutura do JSON recebido, extraindo com segurança o número de telefone do remetente e o texto da mensagem.
- **Função de Envio:** Foi criada a função `send_whatsapp_message` para montar e enviar a mensagem de resposta.
- **Integração com a API Graph:** A função de envio utiliza a biblioteca `requests` para fazer uma requisição `POST` para a API Graph da Meta, incluindo o Token de Acesso para autenticação e o payload da mensagem formatado em JSON.

### ⚠️ 5. Status da Fase e Debugging

- Ao final da fase, a aplicação estava **recebendo mensagens com sucesso**, validando toda a configuração do webhook.
- O envio da resposta foi bloqueado por uma restrição da conta Meta (`"Business account is restricted from messaging users in this country."`). O código de envio está funcional e a resolução depende da conclusão da "Verificação da Empresa" no Gerenciador de Negócios da Meta, que está em andamento.