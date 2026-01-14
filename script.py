import os
import feedparser
import requests

# GitHub Secrets se data le rahe hain (Inko edit mat karna)
BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHANNEL_ID']

# AAPKA BLOG URL (Maine add kar diya hai)
RSS_URL = "https://technovexa.blogspot.com/feeds/posts/default"
DB_FILE = "last_post.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "disable_web_page_preview": False  # Link ka preview dikhega
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Message sent to Telegram.")
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    print("Checking for new posts...")
    
    # 1. RSS Feed Read karna
    try:
        feed = feedparser.parse(RSS_URL)
        if not feed.entries:
            print("No posts found in RSS feed.")
            return
        
        # Latest post nikalna
        latest_post = feed.entries[0]
        latest_link = latest_post.link
        
    except Exception as e:
        print(f"Error reading RSS feed: {e}")
        return

    # 2. Last posted link file se check karna
    last_link = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_link = f.read().strip()

    # 3. Match karna (Agar link naya hai to bhejo)
    if latest_link != last_link:
        print(f"New Post Found: {latest_link}")
        
        # --- FINAL MESSAGE FORMAT ---
        final_message = f"{latest_link}\n\n✅ Successfully Posted via Automation!"
        
        # Telegram par bhejna
        send_telegram(final_message)
        
        # File update karna (Taaki dubara na bheje)
        with open(DB_FILE, "w") as f:
            f.write(latest_link)
    else:
        print(f"No new posts. Last post was: {last_link}")

if __name__ == "__main__":
    main()
