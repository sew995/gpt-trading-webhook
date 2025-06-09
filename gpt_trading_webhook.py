from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
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
        odpowiedz = response.choices[0].message.content
        print("📩 Odpowiedź GPT:", odpowiedz)
        return {"ok": True, "gpt": odpowiedz}

    except Exception as e:
        print("❌ Błąd GPT:", e)
        return {"ok": False, "error": str(e)}
