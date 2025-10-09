# test_gemini.py

import os
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

# envs
load_dotenv()

# o SDK do google cloud usará automaticamente as credentials da env GOOGLE_APPLICATION_CREDENTIALS

# config do id do google cloud e regiao
PROJECT_ID = "wandinha-461008"
LOCATION = "us-east1"

def test_gemini_connection(prompt_text):
    """
    def para inicializar a vertex ai e testar a chamada para o modelo Gemini
    """
    try:
        #inicializa o SDK da vertex ai
        vertexai.init(project=PROJECT_ID, location=LOCATION)

        # carrega o generative model
        model = GenerativeModel("gemini-2.5-flash")

        print(f"Enviando prompt para o Gemini: '{prompt_text}'")

        # gera o content
        response = model.generate_content(prompt_text)

        # printa a resposta
        print("\n--- Resposta do Gemini ---")
        print(response.text)
        print("----------------------------")
        print("Conexão com Vertez AI (Gemini) bem sucedida!")

    except Exception as e:
        print(f" Falha na conexão com Vertex AI: {e}")

# roda o teste quando o script é executado
if __name__ == "__main__":
    # lembrar de definir a env antes de rodar:
    # export GOOGLE_APPLICATION_CREDENTIALS="service-account-key.json"

    test_gemini_connection("Olá, Gemini! Responda com uma saudação curta e um fato interessante sobre Wandinha Addams.")