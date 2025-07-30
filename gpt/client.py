# gpt/client.py

import openai

def consultar_gpt(api_key, mensaje_usuario):
    try:
        openai.api_key = api_key
        respuesta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un asistente que explica de forma clara y paso a paso problemas técnicos, científicos o de física."},
                {"role": "user", "content": mensaje_usuario}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        return respuesta['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"[ERROR en la API]: {e}"
