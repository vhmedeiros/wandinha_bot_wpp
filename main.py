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
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://evolution_api:8080")
EVOLUTION_API_KEY = os.getenv("AUTHENTICATION_API_KEY")

@app.get("/") # requisição do tipo GET na raiz print que o BOT ta rodando
def read_root():
    return {"Status": "Wandinha Bot is running."}
    
# endpoint para receber msgs do wpp (POST)
@app.post("/webhook")
async def webhook_post(request: Request):
    """
    Esse webhook recebe todas as notificações da Evolution API
    Compatível com payloads 'messages.upsert' que venham como objeto ou lista
    """
    data = await request.json()

    print("--- Webhook recebido da Evolution API ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("-----------------------------------------")

    event = data.get("event")
    raw = data.get("data")

    # processando novas mensagens de texto
    if event != "messages.upsert" or raw is None:
        return {"status": "ignored", "reason": "not messages.upsert or empty data"}

    #normaliza: 'raw' poder ser objeto UNICO ou LISTA de mensagens
    messages = []
    if isinstance(raw, dict) and ("message" in raw or "key" in raw):
        messages = [raw]
    elif isinstance(raw, list):
        messages = raw
    else:
        # alguns conectores mandam em 'messages' em vez de 'data'
        alt = data.get("messages")
        if isinstance(alt, list):
            messages = alt

    if not messages:
        print("Nenhuma mensagem útil no payload.")
        return {"status": "ignored", "reason": "no parsable messages"}
    
    for msg in messages:
        key = msg.get("key", {})
        from_me = key.get("fromMe", False) # não assuma true por default
        if from_me:
            print("Mensagem ignorada (enviada pelo proprio bot)")
            continue

        sender_number = key.get("remoteJid") or msg.get("chatId")
        message_obj = msg.get("message", {})

        # extrai texto de conversation OU extendedTextMessage
        message_text = None
        if isinstance(message_obj, dict):
            if message_obj.get("conversation"):
                message_text = message_obj["conversation"]
            else:
                etm = message_obj.get("extendedTextMessage") or {}
                message_text = etm.get("text")

        if not message_text:
            print(f"Mensagem sem texto (talvez midia/audio). Sender: {sender_number}")
            continue

        print(f"Texto recebido de {sender_number}: {message_text!r}")

        # chama Vertex - requer GOOGLE_APPLICATION_CREDENTIAL no container
        gemini_response = get_gemini_response(message_text)

        # envia resposta via Evolution
        if sender_number and gemini_response:
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
            "presence": "composing",
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


