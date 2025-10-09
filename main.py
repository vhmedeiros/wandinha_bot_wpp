# main.py
import os
import json
import uvicorn
import requests
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv
from ai_processor import get_gemini_response


# carrega as variaveis de ambiente
load_dotenv()

app = FastAPI()

# Obtém as configurações da Evolution API do arquivo .env
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("AUTHENTICATION_API_KEY")

@app.get("/") # requisição do tipo GET na raiz print que o BOT ta rodando
def read_root():
    return {"Status": "Wandinha Bot is running."}
    
# endpoint para receber msgs do wpp (POST)
@app.post("/webhook")
async def webhook_post(request: Request):
    """
    Esse webhook recebe todas as notificações da Evolution API
    """
    data = await request.json()

    print("--- Webhook recebido da Evolution API ---")
    print(json.dumps(data, indent=2))
    print("-----------------------------------------")

    # processando eventos de novas mensagens de texto
    if data.get("event") == "messages.upsert" and data.get("data"):
        message_data = data["data"]

        # garante que a mensagem não é do proprio bot
        if message_data.get("key", {}).get("fromMe", True):
            print("Mensagem ignorada (enviada pelo próprio bot).")
            return {"status": "ok", "message": "Ignored own message"}
        
        # pega a primeira mensagem da lista
        message = message_data.get("message", {})

        # verifica se é uma mensagem de texto simples (conversation)
        if "conversation" in message:
            sender_number = message_data["key"]["remoteJid"]
            message_text = message["conversation"]

            print(f"Mensagem de texto recebida de {sender_number}: '{message_text}")

            # obtem a resposta do gemini
            gemini_response = get_gemini_response(message_text)

            # envia a resposta de volta ao user via Evolution API
            send_evolution_message(sender_number, gemini_response)

    # o wpp espera uma resposta 200 OK para confirmar recebimento
    return {"status": "ok"}

def send_evolution_message(to_number, message):
    """
    def para enviar uma mensagem de texto usando a instancia local da Evolution API
    """
    # A URL para enviar msg de texto da Evolution API
    api_url = f"{EVOLUTION_API_URL}/message/sendText/wandinha"
    
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json",
    }
    
    payload = {
        "number": to_number,
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "textMessage": {
            "text": message
        },
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        print("Message sent successfully for Evolution API!")
        print(response.json())

    except requests.exceptions.RequestException as e:
        print(f"Erro sending message: {e}")

        if e.response is not None:
            print(f"Corpo da resposta de erro: {e.response.text}")

# permite rodar o server com 'python main.py'
if __name__ == "__main__": 
    uvicorn.run(        # uvicorn é o server
        app,            # intancia do FastAPI que sera servida
        host="0.0.0.0", # faz o server escutar todas as interfaces de rede, naão apenas localhost. pode acessar de outra maquina sabe o ip desta
        port=8000,      # porta que o servidor ir rodar 
    )


