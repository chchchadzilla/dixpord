<p align="center">
  <img src="banner.png" alt="DixporD Banner — Darrel the Cybernetic Duck from the Future" width="100%">
</p>

<h1 align="center">
  <img src="icon.png" alt="DixporD Icon" width="64" height="64" style="vertical-align: middle;">
  DixporD — Discord Log Exporter
</h1>

<p align="center">
  <strong>🦆 "Quack Quack, motherfeathers!" 🦆</strong><br>
  <em>Export your Discord messages from DMs, servers, and channels.</em><br>
  Save them as <code>.txt</code>, <code>.md</code> (Markdown), or <code>.pdf</code> files — with powerful search and filtering built in.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/status-quack%20quack-yellow.svg" alt="Status: Quack Quack">
</p>

---

### 🦆 The Legend of Darrel the DixporD Duck

> *In the year 2094, the world was about to end. Some crazy ass nuke type stuff.*
>
> *See, Pete Hegseth had started storing ALL the nuclear launch codes in Discord instead of Signal. And when the time came to stop the launch... they couldn't. There was no chat log export feature. The missiles flew. The world burned.*
>
> *But in the ashes, they built one last thing: a time machine.*
>
> *And they sent back their best operative — their only hope — a cybernetic duck named **Darrel**.*
>
> *His mission: travel back to this very moment and create **DixporD** — the Discord chat exporter that does it all. Server exports, DM exports, bulk exports, cross-server search, multi-user filtering, date ranges, keyword search, .txt, .md, .pdf — the whole nine yards. So that the world is saved in the future.*
>
> *But there was a catch. If the apocalypse never happens... the time machine is never built. And if the time machine is never built... Darrel can never go home.*
>
> *So he found a way to digitize himself — to live within the internet, among the 1s and 0s, the only semblance of familiarity he could find in this cold, analogue world.*
>
> *And now he lives there. Helping people export their Discord files. Making sure the world is saved. For a species he's not part of. For a timeline he doesn't belong in.*
>
> *Because he has **integrity**, god damn it.*
>
> *And today? Integrity is spelled **D — U — C — K**.*
>
> *Thank you, Darrel.* 🫡

---

## 📋 Table of Contents

1. [What Does This Tool Do?](#-what-does-this-tool-do)
2. [What You'll Need Before Starting](#-what-youll-need-before-starting)
3. [Step 1 — Install Python](#-step-1--install-python)
4. [Step 2 — Download This Project](#-step-2--download-this-project)
5. [Step 3 — Get Your Discord User Token (Recommended)](#-step-3--get-your-discord-user-token-recommended)
6. [Step 3 (Alt) — Create a Discord Bot (Optional)](#-step-3-alt--create-a-discord-bot-optional)
7. [Step 4 — Configure the .env File](#️-step-4--configure-the-env-file)
8. [Step 5 — Install Dependencies](#-step-5--install-dependencies)
9. [Step 6 — Run the Tool](#️-step-6--run-the-tool)
10. [How to Use the Tool](#-how-to-use-the-tool)
11. [Filter Options Explained](#-filter-options-explained)
12. [Export Formats Explained](#-export-formats-explained)
13. [Where Are My Exported Files?](#-where-are-my-exported-files)
14. [Troubleshooting / Common Errors](#-troubleshooting--common-errors)
15. [Frequently Asked Questions](#-frequently-asked-questions)
16. [Feature List](#-feature-list)
17. [Project Files](#️-project-files)
18. [Security & Privacy](#-security--privacy)

---

## 🤔 What Does This Tool Do?

Dixpord is a command-line tool that connects to Discord and downloads messages from:

- ✅ Any **server** (guild) channel you have access to
- ✅ **All your personal DMs** — one-on-one and group DMs
- ✅ **Cross-server keyword search** — find a word across every server you're in
- ✅ **Bulk export** — dump every DM conversation at once

### Two Modes

| Mode | Token Type | DMs | Servers | Best For |
|---|---|---|---|---|
| **User mode** (recommended) | Your personal Discord token | ✅ **ALL your DMs** | ✅ All your servers | Exporting YOUR messages — DMs, servers, everything |
| **Bot mode** | A Discord bot token | ❌ Only bot DMs | ✅ Servers the bot is in | Server-only exports where you don't want to use your personal token |

> 💡 **User mode is recommended.** It uses your own Discord account token to access everything you can see in Discord — including all your personal DMs with friends.

You can **filter** messages by date range, username, keyword, and more — then save them as a text file, Markdown file, or styled PDF.

---

## 🧰 What You'll Need Before Starting

Before you do anything, make sure you have:

| Requirement | Where to Get It | Cost |
|---|---|---|
| A computer (Windows, Mac, or Linux) | You're on one right now | Free |
| An internet connection | — | — |
| A Discord account | [discord.com](https://discord.com) | Free |
| Python 3.10 or newer | See [Step 1](#-step-1--install-python) below | Free |
| Your Discord user token **OR** a Discord bot token | See [Step 3](#-step-3--get-your-discord-user-token-recommended) below | Free |

You do **NOT** need:

- Any coding experience
- Any paid software
- Admin access to a Discord server (for user mode — you can access everything you can see)

---

## 🏠 Step 1 — Install Python

Python is the programming language this tool is written in. You need it installed on your computer.

### How to check if you already have Python

1. **Open a terminal:**
   - **Windows:** Press `Win + R`, type `cmd`, press Enter
   - **Mac:** Open "Terminal" from Spotlight (`Cmd + Space`, type "Terminal")
   - **Linux:** Open your terminal application
2. **Type this and press Enter:**
   ```
   python --version
   ```
3. If you see something like `Python 3.10.x` or higher, you're good — **skip to [Step 2](#-step-2--download-this-project)!**
4. If you see an error like `'python' is not recognized`, you need to install it.

### How to install Python

1. Go to: **<https://www.python.org/downloads/>**
2. Click the big yellow **"Download Python 3.x.x"** button
3. Run the downloaded installer
4. ⚠️ **CRITICAL ON WINDOWS:** Check the box that says **"Add Python to PATH"** at the bottom of the installer. If you miss this, nothing will work.
5. Click **"Install Now"**
6. When it's done, close and re-open your terminal, then run `python --version` again to confirm

> **Mac users:** If `python --version` doesn't work, try `python3 --version` instead. On Mac, you may need to use `python3` instead of `python` for all commands below.

---

## 📥 Step 2 — Download This Project

You have two options:

### Option A: Download as a ZIP (easiest — no Git needed)

1. Go to the GitHub page for this project
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Find the downloaded ZIP file (usually in your Downloads folder)
5. Right-click the ZIP → **"Extract All"** (Windows) or double-click it (Mac)
6. You should now have a folder called `Dixpord` (or `Dixpord-main`)
7. **Remember where this folder is** — you'll need the path later

### Option B: Clone with Git (if you have Git installed)

1. Open your terminal
2. Navigate to where you want to put the project:
   ```
   cd C:\Users\YourName\Desktop
   ```
3. Clone it:
   ```
   git clone https://github.com/chchchadzilla/dixpord.git
   ```
4. Enter the folder:
   ```
   cd Dixpord
   ```

> Don't have Git? Download it from **<https://git-scm.com/downloads>** or just use Option A.

---

## 🔑 Step 3 — Get Your Discord User Token (Recommended)

Your **user token** is what Discord uses internally to authenticate you. Using it gives the tool access to **everything** you can see — all your DMs, all your servers, all your messages. This is the recommended approach.

### How to Get Your Token

1. Open **Discord in your web browser** (not the desktop app):
   → Go to **<https://discord.com/app>** and log in

2. Press **F12** to open Developer Tools (or right-click anywhere → "Inspect")

3. Click the **"Network"** tab at the top of Developer Tools

4. In the **filter bar**, type `api` to narrow the results

5. Now do something in Discord — click on a channel, open a DM, anything to trigger an API request

6. You'll see requests appear in the list. **Click on any one** of them

7. In the right panel, look at the **"Request Headers"** section

8. Find the header called **`Authorization`** — the value next to it is your token

9. **Copy that value** — that's your Discord user token

> 💡 **Alternative method:** In Developer Tools, go to the **"Console"** tab and paste this:
> ``` js
> (webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
> ```
> Press Enter — your token will be printed.

### ⚠️ Security Warnings

- **NEVER share your user token with anyone.** It provides full access to your Discord account.
- **NEVER commit it to Git** or post it online.
- If your token is compromised, **change your Discord password immediately** — this invalidates all existing tokens.
- The token is stored only in your local `.env` file, which is gitignored.

### Does My Token Expire?

Your token stays valid until you change your Discord password or log out of all sessions. If the tool suddenly says "Authentication failed", just get a fresh token using the steps above.

---

## 🤖 Step 3 (Alt) — Create a Discord Bot (Optional - Skip To Step 4 If You Already Have Your User Token)

> **Only use this if you don't want to use your personal token.** Bot mode is more limited — bots cannot access your personal DMs - If you did the above step, go ahead and skip to step 4.

### 3a. Create a Discord Application

1. Open your web browser and go to: **<https://discord.com/developers/applications>**
2. Log in with your Discord account (the same one you use for chatting)
3. Click the **"New Application"** button (top-right, blue button)
4. Give it a name — anything works, like `My Log Exporter`
5. Agree to the Terms of Service
6. Click **"Create"**

### 3b. Get Your Bot Token

1. You should now be on your new application's page (every new application automatically has a bot user — you don't need to create one separately)
2. Look at the **left sidebar** and click **"Bot"**
3. You'll see a section called "Token" with a **"Reset Token"** button
4. Click **"Reset Token"**
5. It may ask you to confirm or enter a 2FA code — do so
6. ✅ **A long string of letters and numbers will appear — THIS IS YOUR BOT TOKEN**
7. Click **"Copy"** to copy it to your clipboard

> ⚠️ **SAVE THIS TOKEN SOMEWHERE SAFE** — you can only see it once! If you lose it, you'll have to click "Reset Token" again.

### 3c. Turn On Required Bot Settings

While you're still on the Bot page:

1. Scroll down to **"Privileged Gateway Intents"**
2. Turn **ON** (toggle to blue) these three switches:
   - ✅ **PRESENCE INTENT**
   - ✅ **SERVER MEMBERS INTENT**
   - ✅ **MESSAGE CONTENT INTENT** ← *This one is essential!*
3. Click **"Save Changes"** at the bottom if it appears

### 3d. Invite the Bot to Your Server(s)

Your bot needs to be in the same servers as the messages you want to export.

1. In the left sidebar, click **"Installation"**
2. Under **"Installation Contexts"**, make sure **"Guild Install"** is checked
3. Under **"Install Link"**, select **"Discord Provided Link"** from the dropdown
4. Under **Guild Install → SCOPES**, add: ✅ `bot`
5. Under **Guild Install → PERMISSIONS**, check:
   - ✅ `View Channels`
   - ✅ `Read Message History`
6. Click **"Save Changes"**
7. Copy the **"Discord Provided Link"** URL
8. Paste it in your browser → pick your server → **"Authorize"**

**Repeat this for every server you want to export from.**

---

## ⚙️ Step 4 — Configure the `.env` File

The `.env` file is where you put your token and settings. It's basically a hidden file in your system.

### 4a. Create your `.env` file

1. Open the `Dixpord` project folder on your computer
2. Find the file called **`.env.example`**
3. **Make a copy of it:**
   - **Windows:** Right-click → Copy → Paste (you'll get `.env.example - Copy`)
   - **Mac/Linux:** In terminal: `cp .env.example .env`
4. **Rename the copy** to exactly **`.env`** (remove the `.example` part)
   - **Windows:** Right-click → Rename → type `.env` → press Enter
   - If Windows warns "the file may become unusable" — click **Yes**, that's fine
   - If you can't see file extensions: In File Explorer, click **View** (top menu) → check **"File name extensions"**

### 4b. Edit the `.env` file

1. Open the `.env` file in a text editor (Notepad, VS Code, etc.)
2. **For user mode (recommended):** Find this line:
   ```
   DISCORD_USER_TOKEN=YOUR_USER_TOKEN_HERE
   ```
   Replace `YOUR_USER_TOKEN_HERE` with the token you copied in Step 3.
3. **For bot mode (alternative):** Find this line:
   ```
   DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
   ```
   Replace `YOUR_BOT_TOKEN_HERE` with your bot token from Step 3 Alt.
4. ⚠️ **No quotes. No spaces around the `=`. Just paste the token directly.**
5. **Save the file** (`Ctrl+S` on Windows, `Cmd+S` on Mac)

> 💡 You can set **both** tokens if you want. The tool will ask which mode to use at startup.

### What about the other settings?

The file has other optional settings. Here's what they all mean:

| Setting | What It Does | Default | Do I Need to Change It? |
| --- | --- | --- | --- |
| `DISCORD_USER_TOKEN` | Your personal Discord token | (none) | ✅ **YES — if using user mode** |
| `DISCORD_BOT_TOKEN` | Your bot's secret token | (none) | ✅ **YES — if using bot mode** |
| `GITHUB_USER_NAME` | Your GitHub username | (empty) | ❌ No — only for contributors |
| `GITHUB_TOKEN` | Your GitHub personal access token | (empty) | ❌ No — only for contributors |
| `DISCORD_USER_NAME` | Your Discord email | (empty) | ❌ No — just for your reference |
| `DISCORD_USER_PASSWORD` | Your Discord password | (empty) | ❌ No — just for your reference |
| `EXPORT_DIR` | Folder where exports are saved | `./exports` | ❌ No — default is fine |
| `DEFAULT_FORMAT` | Default file format (txt/md/pdf) | `txt` | ❌ No — you choose each time |
| `FETCH_LIMIT` | Messages per API batch (max 100) | `100` | ❌ No — leave it at 100 |

> ⚠️ **IMPORTANT:** The `.env` file contains secrets. **Never share it, never post it online, never commit it to GitHub.** It is already in the `.gitignore` so Git will ignore it.

---

## 📦 Step 5 — Install Dependencies

"Dependencies" are other software packages that Dixpord needs to work. You install them once.

### 5a. Open a terminal in the project folder

**Windows:**

1. Open File Explorer and navigate to the `Dixpord` folder
2. Click in the **address bar** at the top (where it shows the folder path)
3. Type `cmd` and press Enter — a black terminal window will open in the right folder

**Mac / Linux:**

1. Open Terminal
2. Type `cd ` (with a space), then drag the Dixpord folder onto the terminal window — it will paste the path
3. Press Enter

### 5b. (Recommended) Create a virtual environment

This keeps Dixpord's packages separate from your system. It's optional but recommended.

**Windows:**

```
python -m venv venv
```
then press enter
then enter
```
venv\Scripts\activate.bat
```
then press enter. It'll go to a blank line below your cursor, and it will stay that way for about 20 seconds
(or more if you have a potatocomputer)
then it'll go back to where it looks like its ready to type in again (usually C:\ or D:\ or where ever you installed it)


**Mac / Linux:**

```
python3 -m venv venv
source venv/bin/activate
```

After activating, you should see `(venv)` at the beginning of your terminal line. This means it's working. 
like this: `(venv) C:\AI\DixporD\` or whatever the location you cloned the DixporD folder to.

### 5c. Install the packages

enter into the scary black code box this:
```
pip install -r requirements.txt
```
and press enter.

> **Mac users:** If `pip` doesn't work, try `pip3` instead.

You'll see a bunch of text scroll by as it downloads. When it's done and you see no red error messages, you're good!

> **Getting an error about "pip is not recognized"?** Make sure you installed Python with "Add to PATH" checked ([Step 1](#-step-1--install-python)). Try restarting your terminal, or use `python -m pip install -r requirements.txt` instead.

---

## ▶️ Step 6 — Run the Tool

Make sure your terminal is in the DixporD folder (and your virtual environment is activated if you created one).

And enter this:
```
python run.py
```
then press enter.

> **Mac users:** Use `python3 run.py` if `python` doesn't work.

**If you have both tokens set**, you'll see a mode selection first:

```
╭──────────────────────────────────────────────────────────╮
│  Dixpord — Discord Log Exporter                          │
│  Export your Discord messages from DMs, servers &         │
│  channels.                                                │
╰──────────────────────────────────────────────────────────╯

  Choose a mode:
    [1]  User mode  (recommended — full access to your DMs & servers)
    [2]  Bot mode   (limited — only servers the bot is invited to)

  Enter 1 or 2 [1]:
```

**If you only have a user token**, it goes straight to user mode:

```
✅ Connected as YourName#1234 (ID: 123456789012345678)

 Main Menu
  1   Export from a server channel
  2   Export from a DM
  3   Search messages across all servers
  4   Export all DMs
  5   List your servers
  6   List your DMs
  0   Quit
```

🎉 **You're in!** Read the next section to learn how to use it.

---

## 🎮 How to Use the Tool

The tool gives you a numbered menu. Just type a number and press Enter.

### Option 1: Export from a server channel

1. Choose `1` from the main menu
2. A list of your servers appears — type the number next to the one you want
3. A list of text channels appears — type the number of the channel
4. Answer the filter questions (see below) or just press Enter to skip each one
5. Pick your export format: `txt`, `md`, or `pdf`
6. Wait while it fetches messages (you'll see a progress counter)
7. Done! It tells you where the file was saved

### Option 2: Export from a DM

1. Choose `2` from the main menu
2. A list of your recent DMs appears — pick one
3. Set filters and format
4. Done!

### Option 3: Search across all servers

1. Choose `3` from the main menu
2. Type a keyword to search for (e.g., `meeting notes`)
3. Optionally set date range and username filter
4. Pick export format
5. The tool searches every channel in every server you have access to
6. All matches are combined into one export file

### Option 4: Export all DMs

1. Choose `4` from the main menu
2. Set filters and format
3. The tool exports each DM conversation as a separate file
4. All files saved to the `exports` folder

### Option 5 & 6: List servers / DMs

These just show you a table of what's available — useful for checking what servers and DMs the tool can see.

### Option 0: Quit

Closes the tool cleanly.

---

## 🔍 Filter Options Explained

Every time you export, the tool asks you some filter questions. You can **press Enter to skip** any of them.

| Prompt | What It Does | Example Input | What Happens If You Skip |
|---|---|---|---|
| Start date | Only include messages **after** this date | `2024-01-01` | Gets all messages from the beginning |
| End date | Only include messages **before** this date | `2025-12-31` | Gets messages up to the present |
| Filter by username | Only include messages from a specific person — or type `multi` for **multi-user mode** (see below) | `john` or `multi` | Gets messages from everyone |
| Filter by keyword | Only include messages containing specific text | `meeting` | Gets all messages regardless of content |
| Include bot messages? | Whether to include messages from bots | `y` or `n` | Default: yes (includes bots) |
| Pinned messages only? | Export only pinned messages | `y` or `n` | Default: no (gets all messages) |
| Max messages | Stop after this many messages | `500` | No limit — gets everything |

**Date formats that work:** `2024-01-15`, `Jan 15 2024`, `2024-01-15 14:30`, `yesterday`, `last week`

### 👥 Multi-User Filtering

When the tool asks **"Filter by username"**, type `multi` to enter **multi-user mode**. This lets you build a list of usernames to include, each with its own optional date range.

**How it works:**

1. Type `multi` at the username prompt
2. Enter usernames one at a time — each one is a partial match (e.g., `john` matches `johnny123`)
3. For each username, you're asked for an optional **start date** and **end date** that apply only to that user
4. Press Enter with no name when you're done adding users
5. A message matches the export if it matches **any** of the users you listed (OR logic)

**Example scenario:**

> *I want all messages from alice (any date), but only messages from bob after 2024-06-01.*

```
Filter by username (or "multi" for multi-user): multi
  Username #1 (Enter to finish): alice
    Start date for alice (Enter=use global):    ← press Enter
    End date for alice (Enter=use global):      ← press Enter
  Username #2 (Enter to finish): bob
    Start date for bob (Enter=use global): 2024-06-01
    End date for bob (Enter=use global):        ← press Enter
  Username #3 (Enter to finish):                ← press Enter to finish
```

This exports all messages from **alice** (using the global date range) plus messages from **bob** only after June 1, 2024.

---

## 📄 Export Formats Explained

| Format | Extension | Best For | Details |
|---|---|---|---|
| Text | `.txt` | Simple reading, searching, archiving | Clean plain text with day separators, timestamps, and indented content |
| Markdown | `.md` | Reading on GitHub, blogs, or Markdown-capable apps | Rich formatting with headers, bold, links, blockquotes, emoji |
| PDF | `.pdf` | Sharing, printing, formal archiving | Styled document with Discord-themed blue day headers, wrapped text |

All three formats include: message content, author names, timestamps, attachments (name + URL), embeds, reactions, reply references, pinned message indicators, and edit timestamps.

---

## 📂 Where Are My Exported Files?

By default, all exports are saved in the `exports/` folder inside the Dixpord project folder:

```
Dixpord/
└── exports/
    ├── My Server - general_20260221_143052.txt
    ├── DM with Alice_20260221_143210.md
    └── DM with Bob_20260221_143315.pdf
```

The filename includes the server/channel name and the date+time of the export, so you'll never accidentally overwrite an old export.

To change the save location, edit `EXPORT_DIR` in your `.env` file.

---

## 🔧 Troubleshooting / Common Errors

### ❌ "No token configured" / "Please set at least one token"

**Cause:** You haven't created the `.env` file, or the token is still a placeholder value.

**Fix:**

1. Make sure you copied `.env.example` to `.env` (see [Step 4](#️-step-4--configure-the-env-file))
2. Make sure you pasted your real token after `DISCORD_USER_TOKEN=` (or `DISCORD_BOT_TOKEN=`)
3. Make sure there are **no quotes** around the token
4. Make sure the file is called exactly `.env` (not `.env.txt` or `.env.example`)

---

### ❌ "Authentication failed" / "Invalid token" (User mode)

**Cause:** Your user token is wrong, expired, or Discord has invalidated it.

**Fix:**

1. User tokens expire when you log out, change your password, or enable/disable 2FA
2. Get a fresh token using the F12 method in [Step 3](#-step-3--get-your-discord-user-token-recommended)
3. Paste the new token into your `.env` file and save
4. Try again

---

### ❌ "This integration requires code grant" / "Requires OAuth2 code grant" (Bot mode)

**Cause:** A setting called "Require OAuth2 Code Grant" is turned on for your bot.

**Fix:**

1. Go to <https://discord.com/developers/applications>
2. Click your application → **Bot**
3. Find **"Require OAuth2 Code Grant"** and make sure it is **OFF** (grey/disabled)
4. Click **"Save Changes"**
5. Try the invite link again

---

### ❌ "Login failed! Check your DISCORD_BOT_TOKEN" (Bot mode)

**Cause:** Your bot token is wrong or expired.

**Fix:**

1. Go to <https://discord.com/developers/applications>
2. Click your application → **Bot** → **"Reset Token"**
3. Copy the new token
4. Paste it into your `.env` file
5. Save and try again

---

### ❌ "'python' is not recognized as an internal or external command"

**Cause:** Python isn't installed, or it wasn't added to PATH.

**Fix:**

1. Reinstall Python from <https://www.python.org/downloads/>
2. ⚠️ Make sure you check **"Add Python to PATH"** during installation
3. Close and re-open your terminal after installing

---

### ❌ "'pip' is not recognized"

**Fix:** Try this instead:

```
python -m pip install -r requirements.txt
```

---

### ❌ "ModuleNotFoundError: No module named 'discord'" or "No module named 'aiohttp'"

**Cause:** Dependencies aren't installed, or you're not in the virtual environment.

**Fix:**

1. If you created a virtual environment, activate it first:
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`
2. Then run: `pip install -r requirements.txt`

---

### ❌ "No servers found" / "No DMs found"

**In user mode:** Make sure your user token is correct. If you have no DMs, there's nothing to export — you need at least one DM conversation on your account.

**In bot mode (No servers):** The bot hasn't been invited to any servers. Follow [Step 3 Alt](#-step-3-alt--set-up-a-discord-bot-alternative) to invite it.

**In bot mode (No DMs):** Bots can only see DMs sent directly to the bot — not your personal DMs with other users. **Switch to user mode** to export your personal DMs.

---

### ❌ "Access denied" / "Forbidden" on a channel

**In user mode:** You don't have permission to view that channel in Discord.

**In bot mode:** The bot doesn't have permission to read that channel. In your Discord server:

1. Right-click the channel → "Edit Channel" → "Permissions"
2. Add your bot's role
3. Make sure it has **"View Channel"** and **"Read Message History"** permissions

---

### ❌ Messages export but content is empty (Bot mode)

**Cause:** The "Message Content Intent" isn't enabled.

**Fix:**

1. Go to <https://discord.com/developers/applications>
2. Click your app → **Bot** → Scroll to **"Privileged Gateway Intents"**
3. Turn **ON** "Message Content Intent"
4. Save and restart the tool

---

### ❌ The tool is taking a very long time

**Cause:** You're exporting a channel with thousands of messages.

**What to do:**

- Use date filters to narrow the range
- Use the "Max messages" limit
- Be patient — the tool shows progress. Large channels (50,000+ messages) can take several minutes.

---

## ❓ Frequently Asked Questions

**Q: Is this free?**
A: Yes. 100% free and open source under the [MIT License](LICENSE).

**Q: Is this against Discord's Terms of Service?**
A: **User mode** uses your personal token with the same API calls your browser makes — Discord doesn't officially endorse this but it accesses only your own data. **Bot mode** uses the official Discord Bot API, which is fully sanctioned. Either way, you're only exporting your own messages. Use responsibly.

**Q: Can I export my personal DMs?**
A: **Yes!** That's what user mode is for. Set your `DISCORD_USER_TOKEN` in the `.env` file and you'll have full access to all your DM conversations.

**Q: Can I export someone else's DMs?**
A: No. In user mode, you can only access conversations you're a part of. In bot mode, the bot can only see DMs sent directly to it.

**Q: Does this work with Discord Nitro?**
A: Nitro doesn't affect the tool. It works the same for free and Nitro accounts.

**Q: Can I run this on my phone?**
A: No. This is a command-line tool that runs on a computer (Windows, Mac, or Linux).

**Q: Can I schedule automatic exports?**
A: Not built-in, but you could use Windows Task Scheduler or a cron job to run `python run.py` on a schedule with non-interactive mode (would require custom modifications).

**Q: What happens if my token leaks?**
A: **User token:** Someone could access your entire Discord account. Immediately change your Discord password — this invalidates the old token. **Bot token:** Someone could use your bot in your servers. Go to [Discord Developer Portal](https://discord.com/developers/applications), click your app → Bot → "Reset Token".

**Q: How many messages can I export?**
A: There's no hard limit. The tool fetches 100 messages at a time (Discord's max per request) and keeps going until it has them all. Channels with hundreds of thousands of messages will work — they'll just take a while.

**Q: Will I get rate-limited by Discord?**
A: The tool has built-in rate-limit protection. It adds small delays between API requests, pauses every 300 messages, and automatically waits and retries if Discord returns a 429 (rate limit) response. Even exporting 500+ messages happens in just a few API calls and should never trigger rate limiting under normal use.

**Q: My user token stopped working — what happened?**
A: User tokens expire when you change your password, enable/disable 2FA, or log out of that session. Just get a fresh token using the F12 method in [Step 3](#-step-3--get-your-discord-user-token-recommended).

---

## ✨ Feature List

| Feature | Description |
| --- | --- |
| 🔑 Dual mode | User-token mode (full access) or bot mode — your choice |
| 🏠 Server export | Browse your servers → pick a channel → export |
| 💬 DM export | Export any direct message conversation (including personal DMs in user mode) |
| 📦 Bulk DM export | Export ALL your DM conversations at once |
| 🔍 Cross-server search | Search for a keyword across every server you're in |
| 📅 Date filtering | Only export messages within a date range |
| 👤 Username filtering | Filter by author name (partial match) — supports **multi-user mode** with per-user date ranges |
| 🔒 Keyword filtering | Only include messages containing specific text |
| 🤖 Bot filtering | Include or exclude bot messages |
| 📌 Pinned-only mode | Export only pinned messages |
| 🔢 Message limit | Cap the number of messages exported |
| 📝 TXT export | Clean plain-text log format |
| 📘 Markdown export | Rich `.md` with headers, embeds, reactions |
| 📕 PDF export | Styled PDF with Discord-themed blue day headers |
| 📎 Attachments | Logged with filename, size, and URL |
| 🖼️ Embeds | Captured with title, description, fields |
| 😀 Reactions | Emoji + count recorded |
| ↩️ Replies | Reply-to reference IDs preserved |
| 📌 Pinned markers | Pinned messages are flagged |
| ✏️ Edit timestamps | Shows when messages were edited |
| 🎨 Interactive CLI | Beautiful Rich-powered menus and tables |

---

## 🗂️ Project Files

Here's what every file in the project does:

```
Dixpord/
├── run.py                     ← Run this to start the tool
├── requirements.txt           ← List of Python packages needed
├── .env.example               ← Template for your settings (copy to .env)
├── .env                       ← YOUR settings with secrets (never share!)
├── .gitignore                 ← Tells Git what files to ignore
├── LICENSE                    ← MIT open source license
├── README.md                  ← This file you're reading now
├── banner.png                 ← Darrel the DixporD Duck — banner image
├── icon.png                   ← Darrel the DixporD Duck — icon image
│
├── dixpord/                   ← Main application code
│   ├── __init__.py            ← Package marker (ignore this)
│   ├── __main__.py            ← Allows "python -m dixpord" to work
│   ├── cli.py                 ← The interactive menu and user interface
│   ├── config.py              ← Reads your .env settings
│   ├── fetcher.py             ← Downloads messages from Discord (bot mode)
│   ├── user_client.py         ← Discord HTTP client (user mode)
│   ├── models.py              ← Data structures for messages
│   └── exporters/             ← File format exporters
│       ├── __init__.py        ← Exporter registry
│       ├── base.py            ← Shared exporter logic
│       ├── txt_exporter.py    ← Writes .txt files
│       ├── md_exporter.py     ← Writes .md files
│       └── pdf_exporter.py    ← Writes .pdf files
│
└── exports/                   ← Your exported files appear here
```

---

## 🔒 Security & Privacy

- 🔐 Your tokens (user and/or bot) are stored only in your local `.env` file — they are never uploaded, transmitted, or logged by this tool
- 🔐 The `.env` file is listed in `.gitignore` — Git will never commit it, even if you push code to GitHub
- 🔐 Exported files are saved locally on your computer — they are never sent anywhere
- 🔐 The `exports/` folder is also gitignored — your chat logs won't be committed to version control
- 🔐 **User token warning:** Your user token grants full access to your Discord account. Treat it like a password. Never share it with anyone.
- 🔐 If your user token is compromised, **change your Discord password immediately** — this invalidates all user tokens
- 🔐 If your bot token is compromised, go to the Developer Portal and click **"Reset Token"** to revoke it
- 🔐 You can delete the bot from the Developer Portal at any time to revoke all bot access permanently

---

*Built with 🤘🏼 using [discord.py](https://discordpy.readthedocs.io/), [Rich](https://rich.readthedocs.io/), [aiohttp](https://docs.aiohttp.org/), and [fpdf2](https://py-pdf.github.io/fpdf2/).*
