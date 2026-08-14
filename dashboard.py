import customtkinter as ctk
import threading
import asyncio
import os
import sys
import wavelink
import time
from dotenv import load_dotenv

# Import the actual Bot class from main.py
from main import Bot
from keep_alive import start_server

load_dotenv()

class BotDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.title("Discord Bot Control Panel")
        self.geometry("600x450")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # --- Bot State Variables ---
        self.bot = None
        self.bot_thread = None
        self.bot_loop = None
        self.is_running = False

        # --- UI Layout ---
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.title_label = ctk.CTkLabel(self, text="Bot Control Panel", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=(20, 10))
        
        # Status Frame
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.status_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Stats
        self.status_label = ctk.CTkLabel(self.status_frame, text="Status: OFFLINE", text_color="red", font=ctk.CTkFont(size=16, weight="bold"))
        self.status_label.grid(row=0, column=0, pady=10)
        
        self.ping_label = ctk.CTkLabel(self.status_frame, text="Ping: -- ms", font=ctk.CTkFont(size=14))
        self.ping_label.grid(row=0, column=1, pady=10)
        
        self.servers_label = ctk.CTkLabel(self.status_frame, text="Servers: 0", font=ctk.CTkFont(size=14))
        self.servers_label.grid(row=0, column=2, pady=10)

        # Advanced Stats Frame
        self.adv_frame = ctk.CTkFrame(self)
        self.adv_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.adv_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.vc_label = ctk.CTkLabel(self.adv_frame, text="Active Voice Connections: 0", font=ctk.CTkFont(size=14))
        self.vc_label.grid(row=0, column=0, pady=10)

        self.users_label = ctk.CTkLabel(self.adv_frame, text="Cached Users: 0", font=ctk.CTkFont(size=14))
        self.users_label.grid(row=0, column=1, pady=10)
        
        # Controls Frame
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=3, column=0, padx=20, pady=30, sticky="ew")
        self.controls_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.start_btn = ctk.CTkButton(self.controls_frame, text="▶ Start Bot", fg_color="green", hover_color="darkgreen", command=self.start_bot)
        self.start_btn.grid(row=0, column=0, padx=10)
        
        self.stop_btn = ctk.CTkButton(self.controls_frame, text="⏹ Stop Bot", fg_color="red", hover_color="darkred", state="disabled", command=self.stop_bot)
        self.stop_btn.grid(row=0, column=1, padx=10)
        
        self.restart_btn = ctk.CTkButton(self.controls_frame, text="🔄 Restart", state="disabled", command=self.restart_bot)
        self.restart_btn.grid(row=0, column=2, padx=10)

        # Start background UI updater
        self.update_ui()

    def run_discord_bot(self):
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("ERROR: No token found!")
            return
            
        self.bot_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.bot_loop)
        self.bot = Bot()
        
        # This blocks the background thread until the bot stops
        try:
            self.bot_loop.run_until_complete(self.bot.start(token))
        except Exception as e:
            print(f"Bot stopped: {e}")
        finally:
            self.is_running = False
            self.bot = None

    def start_bot(self):
        if self.is_running: return
        self.is_running = True
        
        self.status_label.configure(text="Status: STARTING...", text_color="yellow")
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.restart_btn.configure(state="normal")
        
        # Start bot in background thread so it doesn't freeze the GUI
        self.bot_thread = threading.Thread(target=self.run_discord_bot, daemon=True)
        self.bot_thread.start()

    def stop_bot(self):
        if not self.is_running or not self.bot or not self.bot_loop: return
        
        self.status_label.configure(text="Status: STOPPING...", text_color="yellow")
        
        # Thread-safe way to close the bot
        asyncio.run_coroutine_threadsafe(self.bot.close(), self.bot_loop)
        
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.restart_btn.configure(state="disabled")
        
    def restart_bot(self):
        self.stop_bot()
        # Wait a moment for it to fully close before starting again
        self.after(3000, self.start_bot)

    def update_ui(self):
        # This function loops every 1 second to update stats
        if self.is_running and self.bot and self.bot.is_ready():
            self.status_label.configure(text="Status: ONLINE", text_color="green")
            
            ping = round(self.bot.latency * 1000)
            self.ping_label.configure(text=f"Ping: {ping} ms")
            
            servers = len(self.bot.guilds)
            self.servers_label.configure(text=f"Servers: {servers}")
            
            users = len(self.bot.users)
            self.users_label.configure(text=f"Cached Users: {users}")
            
            vcs = len(self.bot.voice_clients)
            self.vc_label.configure(text=f"Active Voice Connections: {vcs}")
            
        elif not self.is_running:
            self.status_label.configure(text="Status: OFFLINE", text_color="red")
            self.ping_label.configure(text="Ping: -- ms")
            self.servers_label.configure(text="Servers: 0")
            self.users_label.configure(text="Cached Users: 0")
            self.vc_label.configure(text="Active Voice Connections: 0")
            
        # Schedule next update
        self.after(1000, self.update_ui)

if __name__ == "__main__":
    app = BotDashboard()
    app.mainloop()
