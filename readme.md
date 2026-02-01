# Discord Voice AFK Manager (GUI) 🎧

A simple, user-friendly GUI tool built with Python to manage multiple Discord bots simultaneously. It allows you to keep bots in voice channels (AFK), change their status, and saves your tokens automatically for easy access.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Library](https://img.shields.io/badge/Library-discord.py-7289DA)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

* **Multi-Bot Support:** Manage multiple bots in separate tabs within a single window.
* **GUI Interface:** Easy-to-use graphical interface (Tkinter) instead of command line.
* **Auto-Save Tokens:** Tokens are saved to `tokens.json` locally, so you don't have to re-enter them every time.
* **Voice AFK:** Connects bots to voice channels with "Self-Deafen" enabled to save bandwidth.
* **Custom Status:** Set custom activities (Playing, Watching, Listening) and status modes (Online, DND, Idle, Invisible).
* **Auto-Fetch:** Automatically retrieves server (Guild) and voice channel lists for the bot.

## 📷 Screenshots

<img width="488" height="595" alt="image" src="https://github.com/user-attachments/assets/99784d38-5495-4b4d-9136-df1ceb0eda0b" />


## 🛠️ Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/codedByCan/discord-voice-afk-gui.git](https://github.com/codedByCan/discord-voice-afk-gui.git)
    cd discord-voice-afk-gui
    ```

2.  **Install dependencies**
    You need Python installed. Then run:
    ```bash
    pip install discord.py
    ```
    *(Note: Tkinter usually comes pre-installed with Python. If not, you may need to install `python-tk` depending on your OS).*

## 🚀 Usage

1.  Run the script:
    ```bash
    python main.py
    ```
    *(Replace `main.py` with whatever you named your python file)*

2.  **Add a Bot:**
    * Paste your Bot Token in the input field at the top.
    * Click **"Bot Ekle"** (Add Bot).
    * A new tab will be created for that bot.

3.  **Connect to Voice:**
    * Select the **Server** from the dropdown list.
    * Select the **Voice Channel**.
    * Click **"Ses'e Gir (AFK)"**. The bot will join and deafen itself.

4.  **Change Status:**
    * Choose status (e.g., "Do Not Disturb") and activity type (e.g., "Playing").
    * Type your description (e.g., "Minecraft").
    * Click **"Durumu Güncelle"**.

## ⚠️ Important Notes

* **Privileged Intents:** Make sure to enable **"Server Members Intent"** in the Discord Developer Portal for your bot to load the server list correctly.
* **Local Storage:** Your tokens are stored locally in `tokens.json`. Do not share this file with anyone.
* **Uptime:** The bots will stay connected as long as the application is running on your computer.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/NewFeature`)
3.  Commit your Changes (`git commit -m 'Add some NewFeature'`)
4.  Push to the Branch (`git push origin feature/NewFeature`)
5.  Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

---

**Developed by [Can](https://github.com/codedByCan)**
