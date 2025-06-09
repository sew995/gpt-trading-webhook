import os
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from openai import OpenAI
import requests

# Wczytaj zmienne środowiskowe (API keys itp.)
load_dotenv()

# Inicjalizacja klienta OpenAI (v1+)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Inicjalizacja FastAPI
app = FastAPI()

# === FUNKCJA ANALIZY ===
def analizuj_sygnal_z_gpt(dane: dict) -> str:
    wiadomosc = f"""
    Sprawdź, czy poniższe dane spełniają warunki strategii Fibo + SMC + MACD + Trend.
    Odpowiadaj tylko TAK lub NIE, a potem krótko uzasadnij po polsku.

    Dane:
    - Symbol: {dane.get('symbol')}
    - Bayesian Trend: {dane.get('bayesian')}
    - MACD: {dane.get('macd')}
    - Formacja świecy: {dane.get('candle')}
    - Fibo strefa: {dane.get('zone')}
    """

    odpowiedz = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Jesteś asystentem tradera. Oceniaj dane techniczne po polsku."},
            {"role": "user", "content": wiadomosc}
        ],
        temperature=0.2,
    )
    return odpowiedz.choices[0].message.content

# === FUNKCJA WYSYŁKI NA TELEGRAM ===
def wyslij_telegram(wiadomosc: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ Brak TOKEN lub CHAT_ID w zmiennych środowiskowych")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": wiadomosc
    }
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        print("✅ Telegram: wiadomość wysłana.")
    except Exception as e:
        print(f"❌ Błąd przy wysyłce Telegram: {e}")

# === ENDPOINT DLA WEBHOOKA ===
@app.post("/alert")
async def odbierz_alert(request: Request):
    dane = await request.json()
    odpowiedz_gpt = analizuj_sygnal_z_gpt(dane)

    print("\n📊 Nowy alert z TradingView:", dane)
    print("🤖 Odpowiedź GPT:", odpowiedz_gpt)

    wyslij_telegram(f"🚨 Nowy alert z TV:\n{odpowiedz_gpt}")

    return {"status": "ok", "odpowiedz": odpowiedz_gpt}
