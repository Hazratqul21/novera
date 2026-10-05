import urllib.request

# Отключаем чтение сломанных прокси из Windows/VPN
urllib.request.getproxies = lambda: {}

import os
import json
import asyncio
import httpx
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Novera API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clean_key(key):
    if not key: return ""
    return key.replace("[", "").replace("]", "").replace('"', "").replace("'", "").strip()


GEMINI_API_KEY = clean_key(os.getenv("GEMINI_API_KEY"))
OPENAI_API_KEY = clean_key(os.getenv("OPENAI_API_KEY"))
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
    print("❌ ВСЕ НЕЙРОСЕТИ МИРА УПАЛИ -> ПЕРЕХОД НА ЗАГЛУШКУ")
    print("=" * 50 + "\n")
    return {
        "estimated_price": "Требуется аналитика",
        "estimated_time": "Индивидуально",
        "tech_stack": ["Индивидуальный подбор"],
        "recommendation": "Наши инженеры детально проанализируют вашу задачу и свяжутся с вами."
    }


@app.post("/api/v1/estimate")
async def estimate_project(req: EstimateRequest):
    print("\n" + "=" * 50)
    print("=== МУЛЬТИ-ИИ РОУТИНГ (OPENAI -> GOOGLE) ===")

    prompt = f"""
    Ты — опытный технический директор IT-компании Novera (Узбекистан).
    Клиент описал свою идею: "{req.description}"

    Сделай реалистичную, профессиональную оценку проекта. 
    1. Бюджет указывай в долларах США (например, "от $5,000 до $12,000").
    2. Сроки оценивай адекватно сложности.
    3. В рекомендациях дай один конкретный технический или бизнесовый совет (не пиши банальности вроде "исследуйте рынок").

    Твой ответ должен быть СТРОГО в формате JSON без разметки (без ```json).
    Формат ответа:
    {{
        "estimated_price": "Бюджет",
        "estimated_time": "Сроки",
        "tech_stack": ["Технология 1", "Технология 2"],
        "recommendation": "Твой экспертный совет (1-2 предложения)."
    }}
    """

    # === ЭТАП 1: Основной ИИ - OpenAI (ChatGPT) ===
    if OPENAI_API_KEY:
        print("⏳ Пробуем основной ИИ: OpenAI (GPT-4o-mini)...")
        try:
            url_openai = "[https://api.openai.com/v1/chat/completions](https://api.openai.com/v1/chat/completions)"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload_openai = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system",
                     "content": "Ты технический директор. Отвечай строго в формате JSON, без маркдауна."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }

            async with httpx.AsyncClient(timeout=20.0, trust_env=False) as client:
                response = await client.post(url_openai, headers=headers, json=payload_openai)

                if response.status_code == 200:
                    data = response.json()
                    result_text = data["choices"][0]["message"]["content"]
                    print("✅ УСПЕХ! Ответ получен от OpenAI.")
                    print("=" * 50 + "\n")
                    return json.loads(result_text)
                else:
                    print(f"⚠️ Ошибка OpenAI (Код: {response.status_code}): {response.text}")

        except Exception as e:
            print(f"⚠️ Ошибка сети OpenAI: {e}")

    # === ЭТАП 2: Резервный ИИ - Google Gemini ===
    if GEMINI_API_KEY:
        print("\n🔄 Переключаемся на резервный ИИ Google Gemini...")
        models_to_try = [
            "gemini-3.1-pro-preview",
            "gemini-2.5-pro",
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-omni-1.1-flash"
        ]

        payload_gemini = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
        }

        async with httpx.AsyncClient(timeout=15.0, trust_env=False) as client:
            for model in models_to_try:
                try:
                    url = f"[https://generativelanguage.googleapis.com/v1beta/models/](https://generativelanguage.googleapis.com/v1beta/models/){model}:generateContent?key={GEMINI_API_KEY}"
                    print(f"⏳ Пробуем Gemini: {model}...")

                    response = await client.post(url, json=payload_gemini)

                    if response.status_code == 200:
                        data = response.json()
                        result_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        print(f"✅ УСПЕХ! Ответ получен от Google ({model}).")
                        print("=" * 50 + "\n")
                        return json.loads(result_text)
                    else:
                        print(f"⚠️ Модель {model} недоступна (Код: {response.status_code}).")
                        continue

                except Exception as e:
                    print(f"⚠️ Ошибка сети Gemini {model}: {e}")
                    continue

    # === ЭТАП 3: Если легли вообще все провайдеры ===
    print("\n⚠️ СПАСАЕМ ИДЕЮ КЛИЕНТА: ОТПРАВЛЯЕМ В TELEGRAM...")

    fallback_text = (
        f"🔴 <b>СБОЙ ИИ | СОХРАНЕННАЯ ИДЕЯ</b>\n\n"
        f"Клиент пытался оценить проект на сайте Novera, но все нейросети недоступны.\n\n"
        f"📝 <b>Текст идеи:</b>\n<i>{req.description}</i>"
    )

    tg_url = f"[https://api.telegram.org/bot](https://api.telegram.org/bot){TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
        try:
            await client.post(tg_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": fallback_text, "parse_mode": "HTML"})
            print("✅ Идея успешно перехвачена и отправлена в Telegram!")
        except Exception as e:
            print(f"❌ Ошибка отправки резервного сообщения в Telegram: {e}")

    # Выдаем клиенту заглушку
    return get_fallback()


@app.post("/api/v1/lead")
async def submit_lead(lead: LeadRequest):
    print("\n=== ОТПРАВКА ЗАЯВКИ В TELEGRAM ===")

    # Получаем текущее время в Ташкенте (UTC+5)
    tz_tashkent = timedelta(hours=5)
    current_time = (datetime.utcnow() + tz_tashkent).strftime("%d.%m.%Y %H:%M")

    # Формируем красивое сообщение для Novera
    text = (
        f"🟢 <b>НОВАЯ ЗАЯВКА | NOVERA</b>\n\n"
        f"👤 <b>Клиент:</b> {lead.name}\n"
        f"📞 <b>Связь:</b> <code>{lead.contact}</code>\n"
        f"🕒 <b>Время:</b> {current_time}\n\n"
        f"📝 <b>Детали задачи:</b>\n{lead.details}\n\n"
        f"🌐 <i>Отправлено с сайта innovera.uz</i>"
    )

    tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient(timeout=15.0, trust_env=False) as client:
        for attempt in range(1, 4):
            try:
                print(f"⏳ Попытка {attempt} из 3...")
                response = await client.post(tg_url,
                                             json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"})

                if response.status_code == 200:
                    print("✅ ЗАЯВКА УСПЕШНО ОТПРАВЛЕНА!")
                    print("==================================\n")
                    return {"status": "success"}
                else:
                    print(f"⚠️ Ошибка Telegram (Код {response.status_code}): {response.text}")

            except Exception as e:
                print(f"⚠️ Сетевая ошибка Telegram: {e}")

            await asyncio.sleep(1.5)

    print("❌ НЕ УДАЛОСЬ ОТПРАВИТЬ ЗАЯВКУ ПОСЛЕ 3 ПОПЫТОК")
    print("==================================\n")
    from fastapi import HTTPException
    raise HTTPException(status_code=500, detail="Telegram API Error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)