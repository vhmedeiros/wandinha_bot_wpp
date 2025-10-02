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