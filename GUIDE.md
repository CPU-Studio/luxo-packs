# Making 3D packs with an AI agent

A step-by-step guide for people who have never used a terminal or written code.

Luxo can show old 2D games in 3D. How a game looks in 3D comes from a **pack**: a small
file that says which parts of the screen are walls, floors, water or trees, and which
characters become 3D models. You don't have to write a pack yourself. An **AI agent** (an
assistant such as Claude Code, Codex or OpenCode) can play the game, study it, build 3D
models in Blender and write the pack, while you watch, answer its questions and decide
whether you like the result.

This guide takes you from nothing to a finished pack you can play on your phone, and, if
you want, share with everyone.

> **Coming soon.** The **Luxo app** for your phone (Step 7) is not published yet. You can
> make a pack and check it on your computer now; this guide will say how to get the app
> the day it is out.

---

## Contents

1. [What you will need](#what-you-will-need)
2. [Words you will meet](#words-you-will-meet)
3. [Step 1: Install Blender and connect it to agents](#step-1-install-blender-and-connect-it-to-agents)
4. [Step 2: Install your AI agent](#step-2-install-your-ai-agent)
5. [Step 3: Get the Luxo pack tools](#step-3-get-the-luxo-pack-tools)
6. [Step 4: Prepare your game](#step-4-prepare-your-game)
7. [Step 5: Ask your agent to build the pack](#step-5-ask-your-agent-to-build-the-pack)
8. [Step 6: While the agent works](#step-6-while-the-agent-works)
9. [Step 7: Try your pack on your phone](#step-7-try-your-pack-on-your-phone)
10. [Step 8: Improve someone else's pack](#step-8-improve-someone-elses-pack)
11. [Step 9: Share your pack with everyone](#step-9-share-your-pack-with-everyone)
12. [Rules for packs on the public list](#rules-for-packs-on-the-public-list)
13. [When something goes wrong](#when-something-goes-wrong)
14. [Questions people ask](#questions-people-ask)

---

## What you will need

| What | Why | Cost |
|---|---|---|
| **A computer** running Linux, or Windows with WSL (see below) | The agent and the pack tools run here | – |
| **A game you own**, as a ROM file you made from your own cartridge | The agent plays it to learn how it looks | – |
| **Blender** (free 3D program) | The agent builds the 3D models in it | Free |
| **An AI agent** (Claude Code, Codex, OpenCode, …) and an account for it | It does the work | A paid plan (see each agent below) |
| **The Luxo pack tools** | Let the agent run the game and check the pack | Free |
| **An Android phone with the Luxo app** | To play with your pack | Free, *coming soon* |
| **Time** | A first pack usually takes the agent one to a few hours | – |

**About the computer.** The Luxo pack tools currently run on Linux. On Windows 10 or 11 you
can use **WSL** (Windows Subsystem for Linux), which gives Windows a Linux inside it:
open the Start menu, type *PowerShell*, right-click it, choose *Run as administrator*, type
`wsl --install` and press Enter, then restart. After that, a program called *Ubuntu* in the
Start menu opens your Linux. Mac support is not available yet.

**About the game.** Only use games you own, and make the ROM file from your own cartridge.
Never download ROMs, and never share them: packs never contain the game itself, and the
public list refuses any pack that does.

**About money.** Building a pack is long work for an agent, and it uses a lot of your plan's
allowance. Plans with higher limits make a first pack much smoother.

---

## Words you will meet

- **Terminal**: a window where you type commands instead of clicking. On Linux it is called
  *Terminal*; on Windows with WSL, open *Ubuntu*. You type a command, press **Enter**, and
  read what it prints. In this guide, commands are shown in grey boxes: copy them exactly.
- **Agent**: an AI assistant that works in your terminal. It can read files, run programs
  and build things, and it asks your permission before doing anything important.
- **MCP**: the way an agent connects to other programs, such as Blender and the Luxo tools.
  You set it up once per program; after that the agent can use them by itself.
- **Pack**: the result: a folder (and later a `.zip` file) with a `pack.json` file, which
  holds the rules, and a `models` folder, which holds the 3D models.
- **Source bundle**: the pack plus the Blender files and scripts used to build it, so
  anyone can improve it later. It ends in `-src.zip`.
- **ROM ID**: a fingerprint of your game file (40 letters and digits). The pack lists it so
  Luxo knows which game the pack is for. The agent works it out for you.
- **Save state**: a snapshot of a game at one moment, like a bookmark. Agents use them to
  jump to a level without replaying everything.

---

## Step 1: Install Blender and connect it to agents

1. **Install Blender** from <https://www.blender.org/download/> (version 3.0 or newer; the
   newest is best). On Linux you can also install it from your software centre.
2. **Install `uv`**, a small helper the Blender connection needs. In a terminal:

   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   Close the terminal and open a new one afterwards.
3. **Install the Blender add-on** that lets agents use Blender (*MCP for Blender*, by
   ahujasid; <https://github.com/ahujasid/blender-mcp>). In a terminal:

   ```
   uvx mcp-for-blender install-addon
   ```

4. **Turn the add-on on.** Open Blender. Go to **Edit → Preferences → Add-ons**, find
   **MCP for Blender**, and tick its box.
5. **Start the connection** (do this every time you open Blender for the agent). In the big
   3D view, press the **N** key: a side panel opens. Click its **MCP for Blender** tab, then
   the button that starts the server (**Start MCP Server**; some versions call it
   **Connect to Claude**). Leave Blender open while the agent works.

> **Safety.** While this button is on, programs on your computer can control Blender. Only
> start it when you are working with your agent, and save any other Blender work first.

You will connect your agent to Blender in Step 2.

---

## Step 2: Install your AI agent

Pick **one** agent. They all work; use the one whose plan you already have. Each section
shows how to install it, sign in, and connect it to Blender.

### Claude Code (by Anthropic)

- **Account:** a Claude Pro, Max, Team or Enterprise plan, or an Anthropic Console
  account. The free Claude plan does not include Claude Code.
- **Install** (Linux or WSL):

  ```
  curl -fsSL https://claude.ai/install.sh | bash
  ```

  Check it worked: `claude --version` should print a version number.
- **Sign in:** type `claude` and press Enter. It opens your browser to log in; approve, then
  come back to the terminal.
- **Connect Blender** (once):

  ```
  claude mcp add blender -- uvx mcp-for-blender
  ```

- **Check the connections:** `claude mcp list` shows each one with **✔ Connected** when it
  works (start the Blender server first, Step 1.5). Inside Claude Code, typing `/mcp` shows
  the same.

### Codex (by OpenAI)

- **Account:** a ChatGPT plan that includes Codex, or an OpenAI API key.
- **Install** (Linux or WSL):

  ```
  curl -fsSL https://chatgpt.com/codex/install.sh | sh
  ```

  Other ways to install are on <https://learn.chatgpt.com/codex/cli>.
- **Sign in:** type `codex` and choose **Sign in with ChatGPT**. On a computer without a
  browser, use `codex login --device-auth` and follow what it prints. `codex login status`
  tells you whether you are signed in.
- **Connect Blender** (once):

  ```
  codex mcp add blender -- uvx mcp-for-blender
  ```

- **Check:** `codex mcp list`.

### OpenCode (open source; works with many AI providers)

- **Account:** OpenCode itself is free; you connect it to an AI provider you pay for (or
  its own OpenCode Go plan).
- **Install** (Linux or WSL):

  ```
  curl -fsSL https://opencode.ai/v2/install | bash
  ```

  More ways are on <https://opencode.ai/docs/>.
- **Sign in:** type `opencode`; inside it, type `/connect` and choose your provider.
- **Connect Blender** (once):

  ```
  opencode mcp add blender -- uvx mcp-for-blender
  ```

- **Check:** `opencode mcp list`.

### Other agents

Any agent that can use **MCP servers** and run commands works (for example Gemini CLI or
Cursor). You need to give it two MCP servers: Blender (`uvx mcp-for-blender`) and the Luxo
tools (Step 3). Look for "MCP" in your agent's documentation; the settings usually look
like this:

```json
{
  "mcpServers": {
    "blender": { "command": "uvx", "args": ["mcp-for-blender"] }
  }
}
```

---

## Step 3: Get the Luxo pack tools

The tools are at <https://github.com/CPU-Studio/luxo-pack-tools>. They include `luxo3d`
(which plays your game invisibly, records what is on screen, and draws previews of your
pack), the connection your agent uses, and instructions written for agents.

1. **Download and set them up.** In a terminal, copy these three lines (press Enter after
   each):

   ```
   git clone https://github.com/CPU-Studio/luxo-pack-tools.git ~/luxo-pack-tools
   cd ~/luxo-pack-tools
   sh setup.sh
   ```

   If it says `git: command not found`, first run `sudo apt update && sudo apt install -y git`
   (it asks for your computer password; nothing shows while you type it, that is normal).

   `setup.sh` checks your computer. If something is missing, it prints **one command to
   copy**: run it (it asks for your password), then run `sh setup.sh` again. Building takes
   a few minutes the first time. It is done when it says **Ready.**
2. **Connect the tools to your agent** (once), from that folder:
   - **Claude Code:** in `~/luxo-pack-tools`, type `claude`. It finds the Luxo tools by
     itself and asks once whether to allow them: answer yes.
   - **Codex:**

     ```
     codex mcp add luxo3d -- python3 ~/luxo-pack-tools/tools/luxo3d/luxo3d_mcp.py
     ```

   - **OpenCode:**

     ```
     opencode mcp add luxo3d -- python3 ~/luxo-pack-tools/tools/luxo3d/luxo3d_mcp.py
     ```

   - **Other agents:** add an MCP server whose command is `python3` with the argument
     `~/luxo-pack-tools/tools/luxo3d/luxo3d_mcp.py` (write your full home folder path if
     `~` isn't accepted).
3. **Check** that both **blender** and **luxo3d** show as connected (`claude mcp list`,
   `codex mcp list` or `opencode mcp list`; start Blender's server first, Step 1.5).

The tools come with instructions written for agents (`AGENTS.md`, `MODELS.md` and
`EDITING.md`). You don't need to read them; your agent does.

To get newer versions of the tools later: `cd ~/luxo-pack-tools`, then `git pull`, then
`sh setup.sh`.

---

## Step 4: Prepare your game

1. **Make a work folder** called `my-packs` inside the tools folder (`~/luxo-pack-tools/my-packs`). Everything for
   your pack will live here.
2. **Copy your ROM file** into it. Keep the name the file came with.
3. **Save states (optional, and you can skip this).** The agent can start from the title
   screen and play its way to the part you want; it only takes it longer. If you're
   comfortable with your phone's developer options, the agent can also copy save states you
   made in the Luxo app from the phone (over a USB cable with *USB debugging* on); just ask
   it.
4. **Decide what you want.** A few sentences are enough, for example:
   - which game and which part (the first level, the whole overworld, the races…);
   - the look you'd like (a toy diorama, chunky blocks, smooth and detailed…);
   - what matters most to you (the hero, the enemies, the scenery).

---

## Step 5: Ask your agent to build the pack

1. Open a terminal **in the tools folder** (`cd ~/luxo-pack-tools`), and start Blender with its
   MCP server on (Step 1.5).
2. Start your agent: `claude`, `codex` or `opencode`.
3. Paste the message below, after filling in the parts in **[brackets]**.

```
I want a Luxo 3D pack for my game. Please read tools/luxo3d/AGENTS.md and
tools/luxo3d/MODELS.md first, and the pack format at the top of
app/src/main/cpp/port/scene/pack.h.

Game: [name of the game] for [system: NES, Game Boy, SNES, Mega Drive, ...]
ROM: my-packs/[file name of your ROM]
Save states (if any): my-packs/[file names]
What to cover: [e.g. the first world: the overworld map and the first two levels]
Look: [e.g. a bright toy diorama; chunky and colourful]

Please:
- capture the parts above, with save states at interesting moments;
- give the scenery depth (walls, floors, water, trees) and keep the score and
  other on-screen information flat and sharp;
- build 3D models in my running Blender (through the Blender MCP tools) for the
  hero and the main characters and objects. Characters must be original designs
  that fit each sprite's role, not copies of the game's characters;
- keep the Blender scripts that rebuild every model in my-packs/[pack-id]/sources/;
- check the result: render previews and short clips, and validate the pack with
  no warnings;
- write the pack in my-packs/[pack-id]/ with version 0.1.0, a title,
  licence CC-BY-SA-4.0, and authors [your name or nickname] and the agent.

Tell me what you are doing as you go, show me previews, and ask me when you need
a decision. Don't share or upload anything.
```

**Tips**
- **[pack-id]** is a short name in lowercase with dashes, like `zelda-overworld`.
- Choose a licence you're happy with; **CC-BY-SA-4.0** lets others improve your pack as long
  as they credit you and share their changes the same way.
- If you'd rather start small, ask for one level only. You can always ask for more later.

---

## Step 6: While the agent works

- **It will ask permission.** Agents ask before running programs or changing files. Read
  each question; for the Luxo tools, Blender and files in your work folder, allowing is
  normal. If it asks to do something outside your work folder, or to send something
  anywhere online, it's fine to say no and ask why.
- **Watch Blender.** You will see models appear and change. You can ask the agent to change
  anything: "make the hero's hat red", "the trees are too tall".
- **Look at the previews.** The agent shows pictures with the original 2D game on the left
  and the 3D view on the right. Say what you like and what you don't.
- **It takes a while.** One to a few hours is normal for a first pack. You can leave it
  running; agents often pause to ask you something, so check in now and then.
- **If you stop for the day:** ask the agent to write down what is done and what is left
  (for example in `my-packs/[pack-id]/NOTES.md`). Next time, start the agent in the same
  folder and ask it to read that file and carry on.

**When it's finished**, your work folder has `my-packs/[pack-id]/` with `pack.json`, a
`models` folder and a `sources` folder, and the agent has told you the pack validates.

---

## Step 7: Try your pack on your phone

> **The Luxo app is coming soon.** These steps are how it will work.

1. **Make the zip.** Ask your agent:

   ```
   Please package my pack: luxo3d package my-packs/[pack-id] --out my-packs/[pack-id]-0.1.0.zip
   ```

2. **Copy the zip to your phone** any way you like: a USB cable, Google Drive, email it to
   yourself, a messaging app to yourself, …
3. **Install it.** In the Luxo app, start the game, open **MENU → 3D packs → Install from
   file…**, and pick the zip. The app warns that the pack isn't from the public list (that
   is expected for your own packs) and installs it.
4. **Turn it on.** In **MENU → 3D view**, pick the side or top-down view. Your pack shows as
   *private file* in the 3D packs menu.

**Faster, for the curious:** with *USB debugging* turned on in your phone's developer
options and the phone connected, the agent can send the pack straight to the app with
`luxo3d push`, and you see each change within seconds.

---

## Step 8: Improve someone else's pack

Every pack on the public list can be improved: packs with models come with their Blender
files and scripts. Your agent makes a copy for you to change; the original stays as it is.

1. Find the pack's **id** in the list: <https://cpu-studio.github.io/luxo-packs/index.json>
   (each entry starts with `"id"`), or in the app under **3D packs → Get packs…**.
2. Start your agent in the tools folder and paste:

```
I'd like to improve the Luxo pack [pack-id]. Please read tools/luxo3d/EDITING.md
and follow it. [Choose one:]
- Make a full copy I can change freely, called [my-new-id].
- Make an overlay: a small pack on top of the original that only changes what I ask.

What I'd like to change: [e.g. a more detailed castle, or models for the enemies
that are still flat].

Open the Blender files with scripts turned off, as EDITING.md says. Keep the
original authors in the credits and the same licence. Show me previews before
and after, and validate the result.
```

The agent downloads the pack's sources, checks they really come from the public list, and
sets everything up. Then it's just like Steps 6 and 7.

---

## Step 9: Share your pack with everyone

Sharing is optional. If you do, your pack goes on the **public list**: anyone using Luxo can
install it from **3D packs → Get packs…**, with your name on it. Before you start, read
[the rules](#rules-for-packs-on-the-public-list) below.

### 1. Make the two files

Ask your agent:

```
Please prepare my pack my-packs/[pack-id] for the public Luxo pack list, following
the "Share" step in tools/luxo3d/EDITING.md: make [pack-id]-[version].zip and, since
it has models, [pack-id]-[version]-src.zip, then run registry_check.py on both
with --blender and tell me the result.
```

Both files must pass the check. A pack with **no** 3D models needs only the first file.

### 2. Send them (a "pull request")

A *pull request* is GitHub's way of saying "please add my files". You need a free GitHub
account (<https://github.com/signup>).

**The easy way: let your agent do it.** If your agent can use GitHub (install the GitHub
command-line tool with your agent's help and log in once with `gh auth login`), ask:

```
Please open a pull request to github.com/CPU-Studio/luxo-packs that adds my two files
to the submissions folder. Use a short title like "Add [pack title] [version]" and
describe the pack in a few sentences. Don't change anything else.
```

**The by-hand way, in your web browser** (for files under 25 MB each):

1. Go to <https://github.com/CPU-Studio/luxo-packs> and click **Fork** (top right), then
   **Create fork**. You now have your own copy of the list.
2. In your copy, click the **submissions** folder.
3. Click **Add file → Upload files**, and drag your zip file(s) into the page.
4. Below, choose **Create a new branch for this commit and start a pull request**, and
   click **Propose changes**.
5. On the next page, check the title, write a few words about your pack, and click
   **Create pull request**.

If a file is larger than 25 MB, the browser won't take it: use the agent way instead.

### 3. What happens next

- An automatic **check** runs on your files within a few minutes. A green tick means they
  passed. A red cross means something needs fixing: open the details, copy the message, and
  give it to your agent.
- The **maintainer** looks at your pack, mainly for copyright (see the rules). They may ask
  questions in the pull request; you'll get an email.
- When it's accepted, your pack appears in **Get packs…** for everyone soon after.

To update your pack later, increase its version (e.g. `0.1.0` → `0.2.0`), make both files
again and send a new pull request.

---

## Rules for packs on the public list

The maintainer reviews every pack before it goes on the list. The full rules are in the
[README](README.md#what-is-accepted). In short:

**Welcome**
- characters you or your agent **designed**: a hero, an enemy or a racer that fits the
  sprite's role, size and colours, but is not a copy of the game's character;
- **ordinary objects**: trees, houses, karts, coins, crates, pipes, shells;
- **rules-only packs** (no models): their look is built on each player's phone from their
  own game.

**Not accepted**
- anything taken from the game: ROMs, graphics, sounds, screenshots;
- models traced from the game's sprites, or recreations of its characters, logos or levels;
- a licence that forbids changes ("ND" licences): packs here must be improvable.

**Credit:** if you improved someone else's pack, keep their names and their licence (your
agent does this when it follows `EDITING.md`).

Packs that don't fit these rules can still be used privately: on your own phone, or shared
with friends as a file. They just can't go on the public list.

---

## When something goes wrong

| What you see | What to do |
|---|---|
| The agent says it **can't reach Blender** | Open Blender, press **N**, open the **MCP for Blender** tab and start the server. Then ask the agent to try again. |
| `claude mcp list` (or codex/opencode) shows **✘ Failed to connect** for luxo3d | Check the path to the tools folder in the command you used to add it; remove it and add it again with the full path. |
| The agent **stops and waits** | It probably needs your answer or permission: read its last message. |
| You **run out of allowance** on your plan | Ask the agent to write its progress to `NOTES.md` first, and carry on when your allowance renews. |
| The computer says the **disk is full** | Game captures take space. Ask the agent to delete old captures it no longer needs (it keeps track of them). |
| The pack looks **wrong in the app** but fine in previews | Make sure you installed the newest zip (the version number in **3D packs** tells you), and that the 3D view is on. |
| The **check fails** on your pull request | Copy the error from the check's details and give it to your agent. |
| Something else | Copy the exact message and ask your agent what it means. Agents are good at explaining errors. |

---

## Questions people ask

**Do I need to know how to code?** No. You need to type a few commands from this guide,
describe what you want, and give feedback. The agent does the rest.

**Is it safe to let an agent run programs on my computer?** Agents ask before doing
anything important. Work in your tools folder, read the questions, and say no to anything
you don't understand. Packs themselves are only data: they cannot run code on your phone.

**Will my game be shared?** No. Captures and screenshots stay in your work folder. Packs
contain only rules and models, and the public list refuses anything containing game data.
Don't put your ROM inside a pack folder.

**Which agent is best?** Any agent that supports MCP can do this. Use the one you already
pay for. Results depend more on clear instructions and good feedback than on the agent.

**How good will it look?** It depends on the game and on how much you guide the agent. A
first pass gives depth to the scenery and models for the main characters; you can keep
asking for more.

**Can two people work on the same pack?** Yes: one shares it on the public list, and the
other improves it with Step 8. Every change keeps everyone's credit.

**Who do I ask for help?** Open an issue at <https://github.com/CPU-Studio/luxo-packs/issues>.
