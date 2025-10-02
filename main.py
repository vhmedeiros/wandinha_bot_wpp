# main.py
import os
import json
import uvicorn
import requests
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv

# carrega as variaveis de ambiente
load_dotenv()

app = FastAPI()

# acessa as variaveis de ambiente
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

@app.get("/") # requisição do tipo GET na raiz print que o BOT ta rodando
def read_root():
    return {"Status": "Wandinha Bot is running."}

# Endpoint para a verificação do webhook (GET)
@app.get("/webhook")
# esse Request é a injeção de dependencia do FastAPI. Ele da o obj da requisição. É como o request do DJANGO
def webhook_verify(request: Request):
    """
    Esta def é chamada pelo wpp para verificar o endpoint do webhook.
    Ela espera um challenge e retorna-o para confirmar a autenticidade
    """

    # extrai os parametros da query
    mode = request.query_params.get("hub.mode") # extrai o valor do hub.mode da URL
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # verifica se o modo e o token estão presentes e corretos
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        # responde com o challenge para completar a verificaçaõ
        return Response(content=challenge, status_code=200, media_type="text/plain")
    else:
        # se a verificação falhar, retorna um erro
        print("WEBHOOK_VERIFICATION_FAILED")
        raise HTTPException(status_code=403, detail="Verification failed")
    
# endpoint para receber msgs do wpp (POST)
@app.post("/webhook")
async def webhook_post(request: Request):
    """
    Esta def recebe os dados das msgs enviadas ao seu numero de wpp
    """

    # extrai o corpo da requisição
    body = await request.body() # como da def é async, usamos await para esperar a leitura completa do body
    data = json.loads(body)

    # print o body da requisição no terminal para depuração
    print("Received WhatsApp message: ")
    print(json.dumps(data, indent=2))

    # logica de resposta
    # verifica se a notifica é de uma msg
    if "entry" in data and data["entry"]:
        entry = data["entry"][0]

        if "changes" in entry and entry["changes"]:
            change = entry["changes"][0]

            if "value" in change and "messages" in change["value"]:
                message_info = change["value"]["messages"][0]

                # extrai o numero do remetente e o texto da mensagem
                from_number = message_info["from"]
                message_text = message_info["text"]["body"]

                print(f"Message from {from_number}: {message_text}")

                # envia uma resposta de eco
                send_whatsapp_message(from_number, f"Recebido: {message_text}")

    # o wpp espera uma resposta 200 OK para confirmar recebimento
    return {"status": "ok"}

def send_whatsapp_message(to_number, message):
    """
    def para enviar uma mensagem de texto via API do wpp
    """
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message},
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Message sent successfully!")
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


