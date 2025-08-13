import requests
import os
from datetime import datetime

# Configurações - usar variáveis de ambiente no Railway
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Função para pegar último vídeo
def get_latest_video():
    url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=1"
    resp = requests.get(url).json()
    if "items" in resp and resp["items"]:
        video = resp["items"][0]
        video_id = video["id"].get("videoId")
        title = video["snippet"]["title"]
        thumb = video["snippet"]["thumbnails"]["high"]["url"]
        if video_id:
            return {"id": video_id, "title": title, "thumb": thumb}
    return None

# Enviar para Telegram
def send_to_telegram(video):
    url = f"https://www.youtube.com/watch?v={video['id']}"
    text = f"🎥 Novo vídeo no canal!\n\n{video['title']}\n{url}"
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHAT_ID, "text": text}
    )

# Enviar para Discord
def send_to_discord(video):
    url = f"https://www.youtube.com/watch?v={video['id']}"
    data = {
        "embeds": [
            {
                "title": video["title"],
                "url": url,
                "image": {"url": video["thumb"]},
                "color": 16711680,
                "footer": {"text": "Novo vídeo no canal!"}
            }
        ]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=data)

# Execução única
def main():
    last_video_id = None
    if os.path.exists("last_video.txt"):
        with open("last_video.txt", "r") as f:
            last_video_id = f.read().strip()

    latest = get_latest_video()
    if latest and latest["id"] != last_video_id:
        send_to_telegram(latest)
        send_to_discord(latest)
        with open("last_video.txt", "w") as f:
            f.write(latest["id"])
        print(f"✅ Vídeo enviado: {latest['title']}")
    else:
        print("Nenhum vídeo novo.")

if __name__ == "__main__":
    main()