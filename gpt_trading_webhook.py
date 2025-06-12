from fastapi import FastAPI
from pydantic import BaseModel
import os
from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

# Klucze środowiskowe
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI()

class Alert(BaseModel):
    symbol: str
    bayesian: int
    macd: str
    zone: str

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print("❌ Błąd wysyłania Telegram:", e)

@app.post("/alert")
async def alert_endpoint(payload: Alert):
    # Warunki strategii
    if payload.bayesian >= 80 and payload.zone.lower() == "tak":
        if payload.macd.lower() == "bullish":
            direction = "LONG"
        elif payload.macd.lower() == "bearish":
            direction = "SHORT"
        else:
            return {"ok": False, "msg": "Nieznany kierunek MACD"}
    else:
        return {"ok": False, "msg": "Warunki nie spełnione"}

    # Wiadomość dla Telegrama
    message = f"🔔 {payload.symbol.upper()} {direction}"
    send_telegram(message)

    # Wysyłka do GPT dla komentarza
    prompt = (
        f"Otrzymano alert dla {payload.symbol.upper()}.\n"
        f"Kierunek: {direction}\n"
        f"MACD: {payload.macd}, strefa: {payload.zone}, bayesian: {payload.bayesian}.\n"
        f"Czy to dobre miejsce do wejścia? Odpowiedz jednym zdaniem."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem tradingowym."},
                {"role": "user", "content": prompt}
            ]
        )
        gpt_answer = response.choices[0].message.content
        send_telegram(f"🧠 GPT: {gpt_answer}")
        return {"ok": True, "msg": message, "gpt": gpt_answer}
    except Exception as e:
        print("❌ Błąd GPT:", e)
        send_telegram("⚠️ Błąd przetwarzania alertu przez GPT.")
        return {"ok": False, "error": str(e)}
