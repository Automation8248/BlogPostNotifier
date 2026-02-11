import os
import feedparser
import requests
import time

# --- GitHub Secrets ---
try:
    BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
    CHAT_ID = os.environ['CHANNEL_ID']
except KeyError:
    print("Error: Secrets set nahi hain. Kripya Github Secrets check karein.")
    exit(1)

# --- CONFIGURATION: BLOG LINKS ---
# Yahan aap apne saare Blog Links add kar sakte hain.
# Hamesha last mein comma (,) lagana na bhoolein agar naya link add karna ho.
RSS_URLS = [
    "https://technovexa.blogspot.com/feeds/posts/default",
    "https://nutravexia.blogspot.com/feeds/posts/default",
    # "https://future-blog-link.com/feeds/posts/default"  <-- Future mein aise add karein
]

# Data save karne ke liye text file
DB_FILE = "last_post.txt"

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
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def load_data():
    """Text file se purana data load karega"""
    data = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                for line in f:
                    if "==" in line:
                        parts = line.strip().split("==")
                        if len(parts) == 2:
                            data[parts[0]] = parts[1]
        except:
            return {}
    return data

def save_data(data):
    """Naya data text file mein save karega"""
    with open(DB_FILE, "w") as f:
        for url, link in data.items():
            f.write(f"{url}=={link}\n")

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
            
            # Check karein ki iss wale Blog ka last saved link kya tha
            last_link = last_seen_data.get(rss_url, None)

            # --- MATCHING LOGIC ---
            new_posts_found = []
            
            # Feed mein check karte jao jab tak purana link na mil jaye
            for entry in feed.entries:
                if entry.link == last_link:
                    break # Ruk jao, ye post hum pehle bhej chuke hain
                new_posts_found.append(entry)
            
            # Agar last_link None hai (First time run), toh sirf latest 1 post bhejo
            if last_link is None and new_posts_found:
                new_posts_found = [new_posts_found[0]]

            # Agar naye posts mile hain
            if new_posts_found:
                print(f"New Posts Found: {len(new_posts_found)}")
                
                # List ko reverse karein (Oldest to Newest) taaki line se jaye
                for post in reversed(new_posts_found):
                    latest_link = post.link
                    title = post.title
                    
                    # Message format (No Stars **, No Hashtags #)
                    final_message = f"{title}\n\n{latest_link}\n\n✅ Successfully Posted via Automation!"
                    
                    # Telegram par bhejo
                    if send_telegram(final_message):
                        # Agar message chala gaya, tabhi DB update ke liye ready karo
                        # Lekin hum loop mein DB update nahi karenge, memory mein karenge
                        last_seen_data[rss_url] = latest_link
                        data_changed = True
                        time.sleep(2) # Thoda wait karein taaki Telegram spam na samjhe
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
