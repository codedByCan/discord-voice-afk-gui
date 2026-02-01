import customtkinter as ctk
import discord
import asyncio
import threading
import json
import os
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

SETTINGS_FILE = "config.json"

class AFKBot(discord.Client):
    def __init__(self, ui_callback, loop):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True
        intents.presences = True
        super().__init__(intents=intents, loop=loop)
        self.ui_callback = ui_callback

    async def on_ready(self):
        self.ui_callback("ready", self.guilds)

    async def manage_voice(self, channel_id, is_mute, is_deaf):
        try:
            channel = self.get_channel(channel_id)
            if not channel:
                return False, "Kanal Bulunamadı"

            if self.voice_clients:
                vc = self.voice_clients[0]
                if vc.channel.id == channel_id:
                    await vc.edit(self_mute=is_mute, self_deaf=is_deaf)
                    return True, "Ses Ayarları Güncellendi"
                else:
                    await vc.move_to(channel)
                    await vc.edit(self_mute=is_mute, self_deaf=is_deaf)
                    return True, f"Taşındı: {channel.name}"
            else:
                await channel.connect(self_mute=is_mute, self_deaf=is_deaf)
                return True, f"Bağlandı: {channel.name}"
        except Exception as e:
            return False, str(e)

    async def set_presence(self, status, activity_type, text):
        try:
            d_status = discord.Status.online
            if status == "Rahatsız Etmeyin": d_status = discord.Status.dnd
            elif status == "Boşta": d_status = discord.Status.idle
            elif status == "Görünmez": d_status = discord.Status.invisible

            act = None
            if text:
                if activity_type == "Oynuyor": act = discord.Game(name=text)
                elif activity_type == "İzliyor": act = discord.Activity(type=discord.ActivityType.watching, name=text)
                elif activity_type == "Dinliyor": act = discord.Activity(type=discord.ActivityType.listening, name=text)
                elif activity_type == "Yayında": act = discord.Streaming(name=text, url="https://twitch.tv/discord")

            await self.change_presence(status=d_status, activity=act)
        except:
            pass

class BotPanel(ctk.CTkFrame):
    def __init__(self, parent, token, config, save_cb):
        super().__init__(parent, fg_color="transparent")
        self.token = token
        self.config = config
        self.save_cb = save_cb
        self.loop = asyncio.new_event_loop()
        self.client = AFKBot(self.bot_callback, self.loop)
        self.guilds_map = {}
        self.channels_map = {}

        self.setup_ui()
        threading.Thread(target=self.start_bot, daemon=True).start()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)

        self.status_bar = ctk.CTkLabel(self, text="Bot Başlatılıyor...", font=("Roboto Medium", 14), text_color="#3B8ED0")
        self.status_bar.grid(row=0, column=0, pady=(0, 20), sticky="w")

        voice_frame = ctk.CTkFrame(self, corner_radius=10)
        voice_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        ctk.CTkLabel(voice_frame, text="SES BAĞLANTISI", font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w", padx=15, pady=(15, 5))

        self.cb_guild = ctk.CTkComboBox(voice_frame, command=self.on_guild_change, values=["Yükleniyor..."])
        self.cb_guild.pack(fill="x", padx=15, pady=5)
        
        self.cb_channel = ctk.CTkComboBox(voice_frame, values=[])
        self.cb_channel.pack(fill="x", padx=15, pady=5)

        switch_frame = ctk.CTkFrame(voice_frame, fg_color="transparent")
        switch_frame.pack(fill="x", padx=15, pady=10)

        self.sw_mute = ctk.CTkSwitch(switch_frame, text="Mikrofonu Kapat", command=self.quick_update)
        self.sw_mute.pack(side="left", padx=(0, 20))
        if self.config.get("mute", True): self.sw_mute.select()
        
        self.sw_deaf = ctk.CTkSwitch(switch_frame, text="Sağırlaştır", command=self.quick_update)
        self.sw_deaf.pack(side="left")
        if self.config.get("deaf", False): self.sw_deaf.select()

        self.btn_join = ctk.CTkButton(voice_frame, text="Bağlan / Güncelle", command=self.do_join, height=35)
        self.btn_join.pack(fill="x", padx=15, pady=(5, 15))

        presence_frame = ctk.CTkFrame(self, corner_radius=10)
        presence_frame.grid(row=2, column=0, sticky="ew", pady=15)

        ctk.CTkLabel(presence_frame, text="DURUM & AKTİVİTE", font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w", padx=15, pady=(15, 5))

        self.cb_status = ctk.CTkComboBox(presence_frame, values=["Çevrimiçi", "Rahatsız Etmeyin", "Boşta", "Görünmez"])
        self.cb_status.set(self.config.get("status", "Çevrimiçi"))
        self.cb_status.pack(fill="x", padx=15, pady=5)

        self.cb_act_type = ctk.CTkComboBox(presence_frame, values=["Oynuyor", "İzliyor", "Dinliyor", "Yayında"])
        self.cb_act_type.set(self.config.get("act_type", "Oynuyor"))
        self.cb_act_type.pack(fill="x", padx=15, pady=5)

        self.ent_act_text = ctk.CTkEntry(presence_frame, placeholder_text="Aktivite metni...")
        self.ent_act_text.insert(0, self.config.get("act_text", ""))
        self.ent_act_text.pack(fill="x", padx=15, pady=5)

        self.btn_presence = ctk.CTkButton(presence_frame, text="Durumu İşle", command=self.do_presence, height=35, fg_color="#2B2D31", hover_color="#3F4148")
        self.btn_presence.pack(fill="x", padx=15, pady=(5, 15))

    def start_bot(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.client.start(self.token))
        except Exception as e:
            self.status_bar.configure(text=f"Hata: {str(e)[:30]}...", text_color="red")

    def bot_callback(self, type, data):
        if type == "ready":
            self.status_bar.configure(text=f"Aktif: {self.client.user.name}", text_color="#2CC170")
            self.guilds_map = {g.name: g for g in data}
            self.cb_guild.configure(values=list(self.guilds_map.keys()))
            
            saved_g = self.config.get("guild")
            saved_c = self.config.get("channel")
            
            if saved_g in self.guilds_map:
                self.cb_guild.set(saved_g)
                self.on_guild_change(saved_g)
                if saved_c and saved_c in self.channels_map:
                    self.cb_channel.set(saved_c)
            
            self.do_presence()

    def on_guild_change(self, choice):
        guild = self.guilds_map.get(choice)
        if guild:
            chans = [c for c in guild.channels if isinstance(c, discord.VoiceChannel)]
            self.channels_map = {c.name: c.id for c in chans}
            self.cb_channel.configure(values=list(self.channels_map.keys()))
            self.cb_channel.set("")

    def quick_update(self):
        if self.client.is_ready():
            self.do_join()

    def do_join(self):
        c_name = self.cb_channel.get()
        c_id = self.channels_map.get(c_name)
        if not c_id: return

        mute = self.sw_mute.get() == 1
        deaf = self.sw_deaf.get() == 1

        async def _run():
            res, msg = await self.client.manage_voice(c_id, mute, deaf)
            print(msg)
        
        asyncio.run_coroutine_threadsafe(_run(), self.loop)
        self.save_config()

    def do_presence(self):
        st = self.cb_status.get()
        at = self.cb_act_type.get()
        txt = self.ent_act_text.get()

        asyncio.run_coroutine_threadsafe(self.client.set_presence(st, at, txt), self.loop)
        self.save_config()

    def save_config(self):
        data = {
            "token": self.token,
            "guild": self.cb_guild.get(),
            "channel": self.cb_channel.get(),
            "mute": self.sw_mute.get() == 1,
            "deaf": self.sw_deaf.get() == 1,
            "status": self.cb_status.get(),
            "act_type": self.cb_act_type.get(),
            "act_text": self.ent_act_text.get()
        }
        self.save_cb(self.token, data)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AFK Manager Pro github.com/codedByCan")
        self.geometry("900x600")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self.sidebar, text="AFK MANAGER", font=("Roboto", 20, "bold")).grid(row=0, column=0, padx=20, pady=20)

        self.entry_token = ctk.CTkEntry(self.sidebar, placeholder_text="Bot Token")
        self.entry_token.grid(row=1, column=0, padx=10, pady=10)
        
        ctk.CTkButton(self.sidebar, text="+ Bot Ekle", command=self.add_bot).grid(row=2, column=0, padx=10, pady=5, sticky="n")

        self.scroll_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll_frame.grid(row=3, column=0, sticky="nsew")

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.configs = self.load_configs()
        self.current_frame = None

        for token in self.configs:
            self.create_nav_btn(token)

    def load_configs(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f: return json.load(f)
            except: return {}
        return {}

    def save_all(self, token, data):
        self.configs[token] = data
        with open(SETTINGS_FILE, "w") as f: json.dump(self.configs, f, indent=4)

    def add_bot(self):
        token = self.entry_token.get().strip()
        if token and token not in self.configs:
            self.configs[token] = {}
            self.create_nav_btn(token)
            self.entry_token.delete(0, "end")
            self.show_bot(token)

    def create_nav_btn(self, token):
        name = f"Bot {token[-4:]}"
        btn = ctk.CTkButton(self.scroll_frame, text=name, command=lambda t=token: self.show_bot(t), fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        btn.pack(fill="x", padx=5, pady=2)

    def show_bot(self, token):
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = BotPanel(self.main_area, token, self.configs[token], self.save_all)
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
