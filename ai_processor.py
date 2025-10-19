# ai_processor.py
import os
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

# As credenciais são carregadas automaticamente pela variável de ambiente
# GOOGLE_APPLICATION_CREDENTIALS que você já configurou.

PROJECT_ID = "wandinha-461008"
LOCATION = "us-east1"

# inicializa o SDK da Vertex AI uma unica vez
vertexai.init(project=PROJECT_ID, location=LOCATION)



def get_gemini_response(prompt_text: str) -> str:
    """
    Envia um prompt para o model gemini e retorna a resposta em texto
    """
    try:
        # carrega o model generativo
        model = GenerativeModel("gemini-2.5-flash")

        print(f"Enviando para o Gemini: {prompt_text}")

        # gera o content
        response = model.generate_content(prompt_text)

        print(f"Resposta do Gemini recebida.")
        return response.text

    except Exception as e:
        print(f"Erro da chamada da API do Gemini: {e}")
        return "Peço desculpas, mas não consigo responder no momento. Um corvo deve ter bichado meu cabo de rede."