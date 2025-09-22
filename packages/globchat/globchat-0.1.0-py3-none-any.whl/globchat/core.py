import requests
import time

BASE_URL = "https://globchat.vercel.app"

def send_message(user, text):
    return requests.post(f"{BASE_URL}/send", json={"user": user, "text": text}).json()

def get_messages():
    return requests.get(f"{BASE_URL}/messages").json()

def chat_loop(username):
    print(f"🌍 Connected as {username} — type your messages below (CTRL+C to quit)\n")
    last_len = 0
    while True:
        try:
            # fetch new messages
            msgs = get_messages()
            if len(msgs) > last_len:
                for msg in msgs[last_len:]:
                    print(f"[{msg['user']}] {msg['text']}")
                last_len = len(msgs)

            # input prompt (non-blocking hack)
            if not username:
                username = input("Enter username: ")

            text = input("> ")
            if text.strip():
                send_message(username, text)

        except KeyboardInterrupt:
            print("\n👋 Disconnected")
            break
        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(2)
