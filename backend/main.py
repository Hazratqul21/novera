from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import asyncio

app = FastAPI(title="Novera API", version="1.0")

# Разрешаем запросы с локального сервера и основного домена
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8092", "https://innovera.uz", "https://www.innovera.uz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Схемы данных
class EstimateRequest(BaseModel):
    description: str = Field(..., min_length=10)
    urgency: str = Field(default="normal")


class LeadRequest(BaseModel):
    name: str = Field(..., min_length=2)
    contact: str = Field(..., min_length=5)
    details: str


# Эндпоинт 1: AI Калькулятор
@app.post("/api/v1/estimate")
async def estimate_project(req: EstimateRequest):
    await asyncio.sleep(1.5)  # Имитация работы AI

    # Простая логика для старта (позже можно подключить реальную LLM)
    desc = req.description.lower()
    base_price = 2500 if any(word in desc for word in ["app", "илов", "приложен", "mobil"]) else 1200

    return {
        "estimated_price": f"${base_price} - ${base_price + 1500}",
        "estimated_time": "3 - 6 недель / haftadan / weeks",
        "tech_stack": ["Python (FastAPI)", "React/Next.js", "PostgreSQL", "Docker"],
        "recommendation": "Для вашей задачи мы рекомендуем микросервисную архитектуру с высокой степенью масштабируемости."
    }


# Эндпоинт 2: Прием заявок
@app.post("/api/v1/lead")
async def submit_lead(lead: LeadRequest):
    # TODO: Замените на реальные токены вашего бота перед деплоем
    TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
    TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

    text = f"🔥 <b>Новая заявка с сайта Novera!</b>\n\n👤 Имя: {lead.name}\n📞 Контакт: {lead.contact}\n📝 Детали: {lead.details}"

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
            )
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)