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
    candle: str
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
async def odbierz_alert(alert: Alert):
    print("✅ Odebrano alert:", alert)

    prompt = (
        f"Otrzymano alert dla {alert.symbol}. "
        f"MACD: {alert.macd}, świeca: {alert.candle}, strefa: {alert.zone}, bayes: {alert.bayesian}. "
        "Czy to dobre miejsce do wejścia? Odpowiedz jednym zdaniem."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem tradingowym."},
                {"role": "user", "content": prompt}
            ]
        )
        gpt_odpowiedz = response.choices[0].message.content
        print("📩 GPT:", gpt_odpowiedz)

        # Wysyłka do Telegrama
        send_telegram(f"🔔 ALERT dla {alert.symbol}\nGPT: {gpt_odpowiedz}")

        return {"ok": True, "gpt": gpt_odpowiedz}

    except Exception as e:
        print("❌ Błąd GPT:", e)
        send_telegram("⚠️ Błąd przetwarzania alertu przez GPT.")
        return {"ok": False, "error": str(e)}
