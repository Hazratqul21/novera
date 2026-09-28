import urllib.request

# 1. ГЛОБАЛЬНЫЙ ПАТЧ: Наглухо отключаем чтение сломанных прокси из Windows/VPN
urllib.request.getproxies = lambda: {}

import os
import json
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

app = FastAPI(title="Novera API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем любые подключения
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. ОЧИСТКА КЛЮЧЕЙ: Удаляем случайные скобки, пробелы и кавычки из .env
def clean_key(key):
    if not key: return ""
    return key.replace("[", "").replace("]", "").replace('"', "").replace("'", "").strip()


GEMINI_API_KEY = clean_key(os.getenv("GEMINI_API_KEY"))
TELEGRAM_BOT_TOKEN = clean_key(os.getenv("TELEGRAM_BOT_TOKEN"))
TELEGRAM_CHAT_ID = clean_key(os.getenv("TELEGRAM_CHAT_ID"))


class EstimateRequest(BaseModel):
    description: str = Field(..., min_length=5)
    urgency: str = Field(default="normal")


class LeadRequest(BaseModel):
    name: str = Field(..., min_length=2)
    contact: str = Field(..., min_length=5)
    details: str


def get_fallback():
    print("❌ ПЕРЕХОД НА ЗАГЛУШКУ")
    print("=" * 40 + "\n")
    return {
        "estimated_price": "Требуется аналитика",
        "estimated_time": "Индивидуально",
        "tech_stack": ["Индивидуальный подбор"],
        "recommendation": "Наши инженеры проанализируют задачу и свяжутся с вами."
    }


@app.post("/api/v1/estimate")
async def estimate_project(req: EstimateRequest):
    print("\n" + "=" * 40)
    print("=== БОЕВОЙ ЗАПУСК GEMINI 3.8 FLASH ===")

    if not GEMINI_API_KEY:
        print("❌ ОШИБКА: Ключ GEMINI_API_KEY не найден в файле .env!")
        return get_fallback()

    prompt = f"""
    Ты — технический директор IT-компании Novera.
    Проанализируй идею клиента: "{req.description}"

    Сделай оценку проекта. Твой ответ должен быть СТРОГО в формате JSON без разметки.
    Формат ответа:
    {{
        "estimated_price": "Бюджет от и до",
        "estimated_time": "Сроки",
        "tech_stack": ["Технология 1", "Технология 2"],
        "recommendation": "Краткая рекомендация (на русском)."
    }}
    """

    # Жестко используем 3.8 Flash по требованию Google
    target_model = "gemini-3.8-flash"

    # trust_env=False добивает остатки влияния Windows
    async with httpx.AsyncClient(timeout=25.0, trust_env=False) as client:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }

            print(f"Отправляем запрос напрямую в {target_model}...")
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                result_text = data["candidates"][0]["content"]["parts"][0]["text"]
                print("✅ УСПЕХ! JSON получен.")
                print("=" * 40 + "\n")
                return json.loads(result_text)
            else:
                print(f"ОШИБКА ГЕНЕРАЦИИ ОТ GOOGLE: {response.text}")

        except Exception as e:
            print(f"СИСТЕМНАЯ ОШИБКА СЕТИ: {e}")

    return get_fallback()


@app.post("/api/v1/lead")
async def submit_lead(lead: LeadRequest):
    text = (
        f"🔥 <b>Новая заявка с сайта Novera!</b>\n\n"
        f"👤 <b>Имя:</b> {lead.name}\n"
        f"📞 <b>Контакт:</b> {lead.contact}\n"
        f"📝 <b>Детали:</b>\n{lead.details}"
    )

    tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
        try:
            await client.post(tg_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"})
        except Exception as e:
            print(f"Ошибка отправки в Telegram: {e}")

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)