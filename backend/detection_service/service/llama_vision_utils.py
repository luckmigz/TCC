import base64
from groq import Groq
import cv2
import json

client = Groq()

def analisar_frame_com_llama(frame, verbose=False):
    """
    Envia o frame ao modelo LLaMA (Groq) e retorna um dicionário com as contagens.
    Não altera o fluxo do YOLO — apenas adiciona uma visão paralela.
    """
    # converte o frame para base64
    _, buffer = cv2.imencode(".jpg", frame)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    # faz a requisição multimodal
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analise a imagem e conte quantas pessoas, cadeiras e mesas aparecem. "
                            "Responda apenas neste formato JSON: "
                            "{\"person\": <int>, \"chair\": <int>, \"dining_table\": <int>}."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    },
                ],
            }
        ],
        temperature=0,
        max_completion_tokens=128,
    )

    resposta = completion.choices[0].message.content.strip()
    if verbose:
        print("🧠 Resposta LLaMA:", resposta)

    try:
        dados = json.loads(resposta)
        return {
            "person": int(dados.get("person", 0)),
            "chair": int(dados.get("chair", 0)),
            "dining_table": int(dados.get("dining_table", 0)),
        }
    except Exception as e:
        print("⚠️ Erro ao interpretar resposta LLaMA:", resposta, e)
        return {"person": 0, "chair": 0, "dining_table": 0}
    time.sleep(10) 

