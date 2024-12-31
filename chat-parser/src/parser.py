from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import json
import os

class YouTubeChatFetcher:
    def __init__(self, chat_url, output_file="chat_logs.txt"):
        self.chat_url = chat_url
        self.output_file = output_file
        self.seen_messages = set()
        self.driver = None
        
    def initialize_driver(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get(self.chat_url)
        time.sleep(5)  # Wait for page load
        
    def save_message(self, message_data):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.output_file, "a", encoding="utf-8") as f:
            log_entry = f"[{timestamp}] {message_data['author']}: {message_data['message']}\n"
            f.write(log_entry)
            
    def fetch_chat_data(self):
        if not self.driver:
            self.initialize_driver()
            
        chat_elements = self.driver.find_elements(By.CSS_SELECTOR, "yt-live-chat-text-message-renderer")
        new_messages = []
        
        for element in chat_elements:
            author = element.find_element(By.CSS_SELECTOR, "#author-name").text
            message = element.find_element(By.CSS_SELECTOR, "#message").text
            
            # Create unique message identifier
            message_id = f"{author}:{message}"
            
            if message_id not in self.seen_messages:
                message_data = {
                    'author': author,
                    'message': message,
                }
                self.seen_messages.add(message_id)
                new_messages.append(message_data)
                self.save_message(message_data)
                
        return new_messages
    
    def monitor_chat(self, interval=5):
        try:
            print(f"Starting chat monitor. Saving to {self.output_file}")
            while True:
                new_messages = self.fetch_chat_data()
                if new_messages:
                    for msg in new_messages:
                        print(f"New message: {msg['author']}: {msg['message']}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping chat monitor...")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    chat_url = "https://www.youtube.com/live_chat?is_popout=1&v=C0_uMHfnZCc"
    chat_fetcher = YouTubeChatFetcher(chat_url)
    chat_fetcher.monitor_chat()