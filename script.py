import os
import feedparser
import requests
import json

# --- GitHub Secrets ---
BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHANNEL_ID']

# --- CONFIGURATION: BLOG LINKS ---
# Yahan aap apne saare Blog Links add kar sakte hain.
# Hamesha last mein comma (,) lagana na bhoolein agar naya link add karna ho.
RSS_URLS = [
    "https://technovexa.blogspot.com/feeds/posts/default",
    "https://nutravexia.blogspot.com/feeds/posts/default",
    # "https://future-blog-link.com/feeds/posts/default"  <-- Future mein aise add karein
]

# Data save karne ke liye file name
DB_FILE = "rss_data.json"

def send_telegram(message):
    """Telegram par message bhejne ka function"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "disable_web_page_preview": False 
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Message sent to Telegram.")
    except Exception as e:
        print(f"Error sending message: {e}")

def load_data():
    """Purana data load karega (kaunsa link last post hua tha)"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    """Naya data save karega"""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def main():
    print("Starting Sequence Check...")
    
    # Database load karein
    last_seen_data = load_data()
    data_changed = False

    # --- LOOP START: Har link ko ek-ek karke check karega ---
    for rss_url in RSS_URLS:
        print(f"--- Checking: {rss_url} ---")
        
        try:
            feed = feedparser.parse(rss_url)
            
            # Agar feed empty hai ya load nahi hui
            if not feed.entries:
                print(f"No posts found or Error loading: {rss_url}")
                continue 
            
            latest_post = feed.entries[0]
            latest_link = latest_post.link
            
            # Check karein ki iss wale Blog ka last saved link kya tha
            last_link = last_seen_data.get(rss_url, "")

            # --- MATCHING LOGIC ---
            if latest_link != last_link:
                print(f"New Post Found: {latest_link}")
                
                # Message format
                final_message = f"{latest_link}\n\n✅ Successfully Posted via Automation!"
                
                # Telegram par bhejo
                send_telegram(final_message)
                
                # Database dictionary update karein
                last_seen_data[rss_url] = latest_link
                data_changed = True
            else:
                print(f"No new posts for this URL.")
                
        except Exception as e:
            print(f"Error processing {rss_url}: {e}")
            continue # Error aane par next link check karega, rukega nahi

    # --- LOOP END ---

    # Agar kuch naya post hua tha, tabhi file save karein
    if data_changed:
        save_data(last_seen_data)
        print("Database updated successfully.")
    else:
        print("No new updates found in any feed.")

if __name__ == "__main__":
    main()
