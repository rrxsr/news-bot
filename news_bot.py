import os
import requests

# --- Konfiguratsioon ---
GROQ_API_KEY = os.environ["GROQ_CLOUD"]
NEWS_API_KEY = os.environ["NEWS_API"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# --- Uudiste toomine ---
def get_news():
    topics = [
        "economy OR inflation OR interest rates",
        "war OR geopolitics OR sanctions",
        "investing OR stock market OR ETF"
    ]
    articles = []
    for topic in topics:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": NEWS_API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("articles"):
            for a in data["articles"]:
                articles.append(f"- {a['title']}: {a.get('description', '')}")
    return "\n".join(articles[:15])

# --- Kokkuvõte Groq AI abil ---
def summarize(news_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""Sa oled finants- ja geopoliitikauudiste analüütik. 
Siin on tänased ingliskeelsed uudised:

{news_text}

Tee neist lühike ja selge kokkuvõte EESTI KEELES. 
Jaota kolmeks osaks:
💰 Majandus
⚔️ Sõjandus ja geopoliitika  
📈 Investeerimine

Iga osa: 2-3 lauset. Kasuta lihtsat keelt."""

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000
    }
    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    return data["choices"][0]["message"]["content"]

# --- Telegrami saatmine ---
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🗞 *Päeva uudiste kokkuvõte*\n\n{message}",
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# --- Käivitus ---
if __name__ == "__main__":
    print("Toon uudiseid...")
    news = get_news()
    print("Teen kokkuvõtet...")
    summary = summarize(news)
    print("Saadan Telegrami...")
    send_telegram(summary)
    print("Valmis!")
