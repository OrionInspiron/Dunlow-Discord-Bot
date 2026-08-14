import customtkinter as ctk
import threading
import asyncio
import os
import sys
import wavelink
import time
import re
from dotenv import load_dotenv

from main import Bot
from keep_alive import start_server

load_dotenv()

# Utility to strip ANSI codes from logs before inserting into the Textbox
def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, str_data):
        self.buffer += str_data
        if "\n" in self.buffer:
            clean_text = strip_ansi(self.buffer)
            self.text_widget.insert(ctk.END, clean_text)
            self.text_widget.see(ctk.END)
            self.buffer = ""

    def flush(self):
        pass

class BotDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.title("Discord Bot Control Panel - Advanced")
        self.geometry("900x650")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # --- Bot State Variables ---
        self.bot = None
        self.bot_thread = None
        self.bot_loop = None
        self.is_running = False

        # --- UI Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==================== LEFT SIDEBAR ====================
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Bot Control", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Controls
        self.start_btn = ctk.CTkButton(self.sidebar_frame, text="▶ Start Bot", fg_color="green", hover_color="darkgreen", command=self.start_bot)
        self.start_btn.grid(row=1, column=0, padx=20, pady=10)
        
        self.stop_btn = ctk.CTkButton(self.sidebar_frame, text="⏹ Stop Bot", fg_color="red", hover_color="darkred", state="disabled", command=self.stop_bot)
        self.stop_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.restart_btn = ctk.CTkButton(self.sidebar_frame, text="🔄 Restart", state="disabled", command=self.restart_bot)
        self.restart_btn.grid(row=3, column=0, padx=20, pady=10)

        # Basic Stats
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Status: OFFLINE", text_color="red", font=ctk.CTkFont(weight="bold"))
        self.status_label.grid(row=4, column=0, padx=20, pady=(30, 5))
        
        self.ping_label = ctk.CTkLabel(self.sidebar_frame, text="Ping: -- ms")
        self.ping_label.grid(row=5, column=0, padx=20, pady=5)

        # ==================== RIGHT MAIN AREA ====================
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure((0, 1), weight=1)

        # Servers List
        self.servers_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Active Servers (0)", height=150)
        self.servers_frame.grid(row=0, column=0, padx=(0, 10), pady=(0, 20), sticky="nsew")

        # Music Sessions List
        self.music_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Active Music Sessions (0)", height=150)
        self.music_frame.grid(row=0, column=1, padx=(10, 0), pady=(0, 20), sticky="nsew")

        # Console
        self.console_label = ctk.CTkLabel(self.main_frame, text="Live Console Output", font=ctk.CTkFont(weight="bold"))
        self.console_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        self.console_textbox = ctk.CTkTextbox(self.main_frame, state="normal", font=ctk.CTkFont(family="Consolas", size=12))
        self.console_textbox.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # Redirect standard output
        sys.stdout = ConsoleRedirector(self.console_textbox)
        sys.stderr = ConsoleRedirector(self.console_textbox)

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
        
        print("\n--- Starting Bot ---")
        
        self.bot_thread = threading.Thread(target=self.run_discord_bot, daemon=True)
        self.bot_thread.start()

    def stop_bot(self):
        if not self.is_running or not self.bot or not self.bot_loop: return
        
        self.status_label.configure(text="Status: STOPPING...", text_color="yellow")
        print("\n--- Stopping Bot ---")
        
        asyncio.run_coroutine_threadsafe(self.bot.close(), self.bot_loop)
        
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.restart_btn.configure(state="disabled")
        
    def restart_bot(self):
        self.stop_bot()
        self.after(3000, self.start_bot)

    def refresh_scrollable_frame(self, frame, items, empty_text="None"):
        for widget in frame.winfo_children():
            widget.destroy()
            
        if not items:
            lbl = ctk.CTkLabel(frame, text=empty_text, text_color="gray")
            lbl.pack(pady=5, padx=10, anchor="w")
        else:
            for item in items:
                lbl = ctk.CTkLabel(frame, text=f"• {item}")
                lbl.pack(pady=2, padx=10, anchor="w")

    def update_ui(self):
        if self.is_running and self.bot and self.bot.is_ready():
            self.status_label.configure(text="Status: ONLINE", text_color="green")
            
            ping = round(self.bot.latency * 1000)
            self.ping_label.configure(text=f"Ping: {ping} ms")
            
            servers = self.bot.guilds
            self.servers_frame.configure(label_text=f"Active Servers ({len(servers)})")
            
            vcs = self.bot.voice_clients
            self.music_frame.configure(label_text=f"Active Music Sessions ({len(vcs)})")
            
            if not hasattr(self, '_last_server_count') or self._last_server_count != len(servers):
                server_names = [g.name for g in servers]
                self.refresh_scrollable_frame(self.servers_frame, server_names, "No servers joined.")
                self._last_server_count = len(servers)
                
            if not hasattr(self, '_last_vc_count') or self._last_vc_count != len(vcs):
                vc_names = [vc.guild.name for vc in vcs if vc.guild]
                self.refresh_scrollable_frame(self.music_frame, vc_names, "No music playing.")
                self._last_vc_count = len(vcs)
            
        elif not self.is_running:
            self.status_label.configure(text="Status: OFFLINE", text_color="red")
            self.ping_label.configure(text="Ping: -- ms")
            self.servers_frame.configure(label_text="Active Servers (0)")
            self.music_frame.configure(label_text="Active Music Sessions (0)")
            if hasattr(self, '_last_server_count') and self._last_server_count != 0:
                self.refresh_scrollable_frame(self.servers_frame, [])
                self._last_server_count = 0
            if hasattr(self, '_last_vc_count') and self._last_vc_count != 0:
                self.refresh_scrollable_frame(self.music_frame, [])
                self._last_vc_count = 0
            
        self.after(1000, self.update_ui)

if __name__ == "__main__":
    app = BotDashboard()
    app.mainloop()
