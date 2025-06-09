from fastapi import FastAPI, Request
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analizuj_sygnal_z_gpt(dane: dict) -> str:
    wiadomosc = (
        f"Otrzymano dane z TradingView:\n"
        f"Symbol: {dane.get('symbol')}\n"
        f"Bayesian: {dane.get('bayesian')}\n"
        f"MACD: {dane.get('macd')}\n"
        f"Świeca: {dane.get('candle')}\n"
        f"Strefa: {dane.get('zone')}\n\n"
        f"Na podstawie powyższych danych, podaj rekomendację: LONG, SHORT czy BRAK."
    )

    odpowiedz = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Jesteś analitykiem rynków finansowych."},
            {"role": "user", "content": wiadomosc}
        ]
    )

    return odpowiedz.choices[0].message.content

def wyslij_telegram(tresc: str):
    # Tutaj możesz zaimplementować wysyłkę do Telegrama, np. przez requests.post
    print(f"[TELEGRAM] {tresc}")

@app.post("/alert")
async def odbierz_alert(request: Request):
    dane = await request.json()
    odpowiedz_gpt = analizuj_sygnal_z_gpt(dane)

    print("\n📢 Nowy alert z TradingView:", dane)
    print("🤖 Odpowiedź GPT:", odpowiedz_gpt)

    wyslij_telegram(f"🚨 Nowy alert z TV:\n{odpowiedz_gpt}")

    return {"status": "ok", "odpowiedz": odpowiedz_gpt}
