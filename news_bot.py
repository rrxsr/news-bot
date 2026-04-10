import os
import requests

# --- Konfiguratsioon ---
GROQ_API_KEY = os.environ["GROQ_CLOUD"]
NEWS_API_KEY = os.environ["NEWS_API"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# --- Uudiste toomine ---
def get_news():
    queries = [
        "Federal Reserve interest rates inflation CPI GDP",
        "central bank monetary policy quantitative tightening",
        "geopolitical risk sanctions trade war tariffs supply chain",
        "S&P500 earnings recession yield curve bonds",
        "oil price OPEC commodities gold dollar index FX",
        "China economy property crisis export",
        "Europe ECB energy crisis fiscal policy",
        "emerging markets currency crisis debt",
        "tech sector AI earnings Microsoft Apple Nvidia",
        "banking sector credit risk liquidity",
    ]
    articles = []
    seen = set()

    for query in queries:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": NEWS_API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("articles"):
            for a in data["articles"]:
                title = a.get("title", "")
                desc = a.get("description", "")
                if not title or not desc:
                    continue
                if title in seen:
                    continue
                skip_words = ["birthday", "celebrity", "recipe", "sport", "soccer", "nfl", "nba", "sale", "deal", "discount", "horoscope", "dating"]
                if any(w in title.lower() for w in skip_words):
                    continue
                seen.add(title)
                articles.append(f"- {title}: {desc}")

    return "\n".join(articles[:30])

# --- Kokkuvõte Groq AI abil ---
def summarize(news_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = """Sa oled institutsionaalse taseme makromajandusliku ja geopoliitilise analüüsi ekspert, kes aitab ka jaeinvestoreid praktilisi otsuseid tegema.

Sinu ülesanne on filtreerida uudistest välja müra ja tuvastada ainult olulised signaalid.

Reeglid:
- Ignoreeri üldisi pealkirju ilma põhjuseta
- Eelista uudiseid mis sisaldavad arve, protsente, tikereid, konkreetseid otsuseid
- Too välja põhjus-tagajärg seosed
- Iga punkti juures märgi signaali suund:
  ↑ bullish (positiivne mõju varaklassile)
  ↓ bearish (negatiivne mõju varaklassile)
  ⚠️ risk (ebaselge või ohtlik olukord)

Vastuse formaat on EESTI KEELES, neli osa:

💰 MAKROMAJANDUS
[2-3 punkti numbritega ja põhjus-tagajärg loogikaga, iga punkti lõpus → mõju varaklassile + suund]

⚔️ GEOPOLIITILISED RISKID
[2-3 punkti mis mõjutavad turuhindu, kaubandust või energiat + suund]

📈 TURULIIKUMISED
[2-3 punkti konkreetsete tikerite, sektorite või varaklassidega + suund]

💡 PRAKTILINE INVESTORInurk
[1-2 konkreetset nõuannet tänaste uudiste põhjal – mida vaadata, mida vältida, mis sektor/vara võib lähiajal liikuda ja miks. Ole konkreetne – nimeta tikerid, ETF-id või sektorid.]

Iga punkt max 2 lauset. Kui kvaliteetseid uudiseid on vähe, kirjuta vähem – ära täida ruumi müraga."""

    user_prompt = f"""Siin on tänased uudised. Filtreeri välja signaalid ja anna praktiline analüüs:

{news_text}"""

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.3
    }
    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    return data["choices"][0]["message"]["content"]

# --- Telegrami saatmine ---
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🗞 *Kratt – Päeva signaalid*\n\n{message}",
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# --- Käivitus ---
if __name__ == "__main__":
    print("Toon uudiseid...")
    news = get_news()
    print(f"Leitud {len(news.splitlines())} uudist")
    print("Analüüsin signaale...")
    summary = summarize(news)
    print("Saadan Telegrami...")
    send_telegram(summary)
    print("Valmis!")
