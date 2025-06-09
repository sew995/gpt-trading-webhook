import requests
import os
from fastapi import FastAPI, Request
from openai import OpenAI
from dotenv import load_dotenv

# TELEGRAM
TELEGRAM_TOKEN = "TWÓJ_TOKEN_TUTAJ"
TELEGRAM_CHAT_ID = "TWÓJ_CHAT_ID_TUTAJ"

def wyslij_telegram(wiadomosc: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": wiadomosc
    }
    requests.post(url, data=payload)

# === ŁADOWANIE ZMIENNYCH ===
load_dotenv()

app = FastAPI()
client = OpenAI()  # z nowej wersji openai

# === FUNKCJA GPT ===
def analizuj_sygnal_z_gpt(dane: dict) -> str:
    wiadomosc = f"""
    Sprawdź, czy poniższe dane spełniają wszystkie warunki strategii Fibo + SMC + MACD + Trend.
    Odpowiadaj tylko TAK lub NIE, a potem uzasadnij po polsku.

    Dane:
    - Symbol: {dane.get('symbol')}
    - Bayesian Trend: {dane.get('bayesian')}%
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
        temperature=0.2
    )

    return odpowiedz.choices[0].message.content

# === ENDPOINT /alert ===
@app.post("/alert")
async def odbierz_alert(request: Request):
    dane = await request.json()
    odpowiedz_gpt = analizu_
