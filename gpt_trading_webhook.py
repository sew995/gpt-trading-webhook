import requests

TELEGRAM_TOKEN = "8180628484:AAFIU2s7tIoEs9LqZrrlTyIOvYrr2Wieo3Q"
TELEGRAM_CHAT_ID = "5651741157"

def wyslij_telegram(wiadomosc: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": wiadomosc
    }
    requests.post(url, data=payload)
from fastapi import FastAPI, Request
import openai
import os
import uvicorn
from dotenv import load_dotenv

# === ŁADOWANIE ZMIENNYCH ŚRODOWISKOWYCH ===
load_dotenv()

app = FastAPI()

# === KONFIGURACJA OPENAI API ===
openai.api_key = os.getenv("OPENAI_API_KEY")

# === FUNKCJA ANALIZUJĄCA SYGNAŁY ===
def analizuj_sygnal_z_gpt(dane: dict) -> str:
    wiadomosc = f"""
    Sprawdź, czy poniższe dane spełniają wszystkie warunki strategii Fibo + SMC + MACD + Trend. 
    Odpowiadaj tylko TAK lub NIE, a potem krótko uzasadnij po polsku.

    Dane:
    - Symbol: {dane.get('symbol')}
    - Bayesian Trend: {dane.get('bayesian')}%
    - MACD: {dane.get('macd')}
    - Formacja świecy: {dane.get('candle')}
    - Fibo strefa: {dane.get('zone')}
    """

    odpowiedz = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Jesteś asystentem tradera. Oceniaj dane techniczne po polsku."},
            {"role": "user", "content": wiadomosc}
        ],
        temperature=0.2
    )

    return odpowiedz.choices[0].message.content

# === ENDPOINT DLA WEBHOOKA ===
@app.post("/alert")
async def odbierz_alert(request: Request):
    dane = await request.json()
    odpowiedz_gpt = analizuj_sygnal_z_gpt(dane)
    print("\n📩 Nowy alert z TradingView:", dane)
    print("🤖 Odpowiedź GPT:", odpowiedz_gpt)
        wyslij_telegram(f"🔔 Nowy alert z TV:\n{odpowiedz_gpt}")
    return {"status": "ok", "odpowiedz": odpowiedz_gpt}

# === URUCHAMIANIE W RENDER.COM ===
# Render automatycznie uruchomi: uvicorn gpt_trading_webhook:app
