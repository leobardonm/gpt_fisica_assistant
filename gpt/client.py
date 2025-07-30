import requests
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_ENDPOINTS = {
    "Gemini 1.5 Pro": "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent",
    "Gemini 1.5 Flash": "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
}

def consultar_gpt(api_key, texto, modelo="Gemini 1.5 Pro"):
    endpoint = GEMINI_ENDPOINTS.get(modelo)
    prompt = f"""{texto}

Al final, proporciona la respuesta numérica final en decimal exacto.
"""
    body = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }

    response = requests.post(endpoint, headers=headers, json=body)
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "⚠️ Error: No se pudo interpretar la respuesta del modelo."
    else:
        return f"[ERROR Gemini]: {response.status_code} - {response.text}"
