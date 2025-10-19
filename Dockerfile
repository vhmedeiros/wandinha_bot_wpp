# Usa uma imagem base oficial do Python, versão 3.12, na variante 'slim' (otimizada e menor).
FROM python:3.12-slim

# Instala as ferramentas de build essenciais do sistema operacional Debian (como o compilador 'cc').
# Isso é necessário ANTES de instalar as libs Python, pois algumas delas (como pydantic-core) precisam ser compiladas.
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho padrão dentro do contêiner. Todos os comandos seguintes serão executados a partir daqui.
WORKDIR /app

# Copia APENAS o arquivo de dependências para o contêiner.
COPY requirements.txt .

# Instala o 'uv', que é um gerenciador de pacotes mais rápido que o pip.
RUN pip install uv

# Usa o 'uv' para instalar todas as bibliotecas listadas no requirements.txt.
# '--system' instala no ambiente global do contêiner (não precisamos de venv aqui).
# '--no-cache' evita guardar arquivos de cache, mantendo a imagem menor.
RUN uv pip install --system --no-cache -r requirements.txt

# Copia todo o resto do código do seu projeto (main.py, ai_processor.py, etc.) para o diretório /app do contêiner.
COPY . .

# Informa ao Docker que o contêiner vai escutar na porta 8000 internamente.
EXPOSE 8000

# O comando que será executado quando o contêiner iniciar.
# Ele roda o servidor Uvicorn, apontando para o objeto 'app' no arquivo 'main.py'.
# '--host 0.0.0.0' faz o servidor ser acessível de fora do contêiner.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]