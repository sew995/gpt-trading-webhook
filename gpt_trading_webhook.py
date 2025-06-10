from fastapi import FastAPI, Request
from pydantic import BaseModel
import os, requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class Alert(BaseModel):
    symbol: str
    bayesian: int
    macd: str
    candle: str
    zone: str

def wyslij_telegram(wiadomosc):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": wiadomosc
    }
    response = requests.post(url, data=payload)
    print("📬 TELEGRAM:", response.status_code, response.text)

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

        wiadomosc = (
            f"📈 Alert dla {alert.symbol}:\n"
            f"MACD: {alert.macd}, świeca: {alert.candle}, strefa: {alert.zone}, bayes: {alert.bayesian}\n"
            f"🤖 GPT: {gpt_odpowiedz}"
        )
        wyslij_telegram(wiadomosc)

        return {"ok": True, "gpt": gpt_odpowiedz}

    except Exception as e:
        print("❌ Błąd GPT:", e)
        return {"ok": False, "error": str(e)}
