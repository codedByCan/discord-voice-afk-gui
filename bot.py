import tkinter as tk
from tkinter import ttk, messagebox
import discord
import asyncio
import threading
import json
import os

class AFKBot(discord.Client):
    def __init__(self, tab_controller, loop):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True
        super().__init__(intents=intents, loop=loop)
        self.tab_controller = tab_controller
        self.connected_voice_client = None

    async def on_ready(self):
        self.tab_controller.update_guild_list(self.guilds)
        self.tab_controller.update_status_label(f"Bağlandı: {self.user.name}")
        self.tab_controller.enable_controls()

    async def join_voice_channel(self, channel_id):
        channel = self.get_channel(channel_id)
        if channel:
            try:
                if self.connected_voice_client:
                    await self.connected_voice_client.disconnect()
                self.connected_voice_client = await channel.connect(self_deaf=True)
                return True, "Sese bağlanıldı."
            except Exception as e:
                return False, str(e)
        return False, "Kanal bulunamadı."

    async def change_presence_status(self, status_type, activity_text, status_mode):
        s_mode = discord.Status.online
        if status_mode == "Rahatsız Etmeyin": s_mode = discord.Status.dnd
        elif status_mode == "Boşta": s_mode = discord.Status.idle
        elif status_mode == "Görünmez": s_mode = discord.Status.invisible

        act = None
        if activity_text:
            if status_type == "Oynuyor":
                act = discord.Game(name=activity_text)
            elif status_type == "İzliyor":
                act = discord.Activity(type=discord.ActivityType.watching, name=activity_text)
            elif status_type == "Dinliyor":
                act = discord.Activity(type=discord.ActivityType.listening, name=activity_text)

        await self.change_presence(status=s_mode, activity=act)

class BotTab(ttk.Frame):
    def __init__(self, parent, token):
        super().__init__(parent)
        self.token = token
        self.bot_loop = asyncio.new_event_loop()
        self.bot_client = AFKBot(self, self.bot_loop)
        self.guild_map = {}
        self.channel_map = {}
        self.setup_ui()
        self.thread = threading.Thread(target=self.start_bot_thread, daemon=True)
        self.thread.start()

    def setup_ui(self):
        self.lbl_status = tk.Label(self, text="Bağlanıyor...", fg="blue", font=("Arial", 10, "bold"))
        self.lbl_status.pack(pady=5)

        frame_server = ttk.LabelFrame(self, text="Sunucu ve Kanal")
        frame_server.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_server, text="Sunucu Seç:").grid(row=0, column=0, padx=5, pady=5)
        self.cb_guilds = ttk.Combobox(frame_server, state="disabled")
        self.cb_guilds.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.cb_guilds.bind("<<ComboboxSelected>>", self.on_guild_select)

        tk.Label(frame_server, text="Ses Kanalı:").grid(row=1, column=0, padx=5, pady=5)
        self.cb_channels = ttk.Combobox(frame_server, state="disabled")
        self.cb_channels.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.btn_join = ttk.Button(frame_server, text="Ses'e Gir (AFK)", command=self.join_voice, state="disabled")
        self.btn_join.grid(row=2, column=0, columnspan=2, pady=10)

        frame_status = ttk.LabelFrame(self, text="Durum ve Aktivite")
        frame_status.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_status, text="Durum:").grid(row=0, column=0, padx=5)
        self.cb_status_mode = ttk.Combobox(frame_status, values=["Çevrimiçi", "Rahatsız Etmeyin", "Boşta", "Görünmez"], state="readonly")
        self.cb_status_mode.current(0)
        self.cb_status_mode.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_status, text="Tip:").grid(row=1, column=0, padx=5)
        self.cb_act_type = ttk.Combobox(frame_status, values=["Oynuyor", "İzliyor", "Dinliyor"], state="readonly")
        self.cb_act_type.current(0)
        self.cb_act_type.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame_status, text="Açıklama:").grid(row=2, column=0, padx=5)
        self.entry_act_text = ttk.Entry(frame_status)
        self.entry_act_text.grid(row=2, column=1, padx=5, pady=2)

        self.btn_update_status = ttk.Button(frame_status, text="Durumu Güncelle", command=self.update_presence, state="disabled")
        self.btn_update_status.grid(row=3, column=0, columnspan=2, pady=5)

    def start_bot_thread(self):
        asyncio.set_event_loop(self.bot_loop)
        try:
            self.bot_loop.run_until_complete(self.bot_client.start(self.token))
        except Exception as e:
            self.update_status_label(f"Hata: {str(e)}")

    def update_guild_list(self, guilds):
        self.guild_map = {g.name: g for g in guilds}
        self.cb_guilds['values'] = list(self.guild_map.keys())

    def update_status_label(self, text):
        self.lbl_status.config(text=text)

    def enable_controls(self):
        self.cb_guilds.config(state="readonly")
        self.cb_channels.config(state="readonly")
        self.btn_join.config(state="normal")
        self.btn_update_status.config(state="normal")

    def on_guild_select(self, event):
        guild_name = self.cb_guilds.get()
        guild = self.guild_map.get(guild_name)
        if guild:
            voice_channels = [c for c in guild.channels if isinstance(c, discord.VoiceChannel)]
            self.channel_map = {c.name: c.id for c in voice_channels}
            self.cb_channels['values'] = list(self.channel_map.keys())
            self.cb_channels.set('')

    def join_voice(self):
        channel_name = self.cb_channels.get()
        channel_id = self.channel_map.get(channel_name)
        if channel_id:
            asyncio.run_coroutine_threadsafe(
                self.bot_client.join_voice_channel(channel_id), 
                self.bot_loop
            )
        else:
            messagebox.showwarning("Uyarı", "Lütfen bir ses kanalı seçin.")

    def update_presence(self):
        st_mode = self.cb_status_mode.get()
        act_type = self.cb_act_type.get()
        act_text = self.entry_act_text.get()
        
        asyncio.run_coroutine_threadsafe(
            self.bot_client.change_presence_status(act_type, act_text, st_mode),
            self.bot_loop
        )

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Discord Ses AFK Yöneticisi")
        self.geometry("400x500")
        self.saved_tokens_file = "tokens.json"

        frame_top = tk.Frame(self, bg="#2C2F33")
        frame_top.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_top, text="Bot Token:", bg="#2C2F33", fg="white").pack(side="left")
        self.entry_token = ttk.Entry(frame_top, width=30)
        self.entry_token.pack(side="left", padx=5)
        
        btn_add = ttk.Button(frame_top, text="Bot Ekle", command=self.add_bot_manual)
        btn_add.pack(side="left")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load_saved_tokens()

    def load_saved_tokens(self):
        if os.path.exists(self.saved_tokens_file):
            try:
                with open(self.saved_tokens_file, "r") as f:
                    data = json.load(f)
                    for token in data.get("tokens", []):
                        self.create_tab(token)
            except:
                pass

    def save_new_token(self, token):
        tokens = []
        if os.path.exists(self.saved_tokens_file):
            try:
                with open(self.saved_tokens_file, "r") as f:
                    data = json.load(f)
                    tokens = data.get("tokens", [])
            except:
                pass
        
        if token not in tokens:
            tokens.append(token)
            with open(self.saved_tokens_file, "w") as f:
                json.dump({"tokens": tokens}, f)

    def add_bot_manual(self):
        token = self.entry_token.get().strip()
        if not token:
            messagebox.showerror("Hata", "Token boş olamaz!")
            return
        
        self.save_new_token(token)
        self.create_tab(token)
        self.entry_token.delete(0, tk.END)

    def create_tab(self, token):
        tab_name = f"Bot {len(self.notebook.tabs()) + 1}" 
        new_tab = BotTab(self.notebook, token)
        self.notebook.add(new_tab, text=tab_name)
        self.notebook.select(new_tab)

if __name__ == "__main__":
    app = App()
    app.mainloop()