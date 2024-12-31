from googleapiclient.discovery import build
import time
import os
from gtts import gTTS

# YouTube API setup
API_KEY = 'AIzaSyAUgrKmZm6uVYcY6p-fLryWqLRC7aFlwRQ'
youtube = build('youtube', 'v3', developerKey=API_KEY)

def load_existing_messages():
    messages = set()
    if os.path.exists('chat_messages.txt'):
        with open('chat_messages.txt', 'r', encoding='utf-8') as f:
            messages = set(f.read().splitlines())
    return messages

def save_message(message, messages_set):
    with open('chat_messages.txt', 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")
    messages_set.add(message)

def text_to_speech(text):
    try:
        tts = gTTS(text, lang='th')  # ใช้ภาษาไทย
        tts.save("message.mp3")
        os.system("start message.mp3")  # เล่นไฟล์เสียง
    except Exception as e:
        print(f"Error in TTS: {e}")

def get_live_chat_messages(video_id):
    try:
        video_response = youtube.videos().list(
            part="liveStreamingDetails",
            id=video_id
        ).execute()
        live_chat_id = video_response['items'][0]['liveStreamingDetails']['activeLiveChatId']
        live_chat_response = youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part="snippet,authorDetails"
        ).execute()
        return live_chat_response['items']
    except Exception as e:
        print(f"Error: {e}")
        return []

def main(video_id):
    existing_messages = load_existing_messages()
    
    while True:
        try:
            messages = get_live_chat_messages(video_id)
            
            for item in messages:
                author = item['authorDetails']['displayName']
                message = item['snippet']['displayMessage']
                full_message = f"{author}: {message}"
                
                if full_message not in existing_messages:
                    print(f"{full_message}")
                    save_message(full_message, existing_messages)

                    # ใช้ TTS กับข้อความจาก Live Chat
                    text_to_speech(full_message)
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\nStopping chat monitor...")
            break
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    video_id = input("Please enter YouTube video ID: ").strip()
    main(video_id)
