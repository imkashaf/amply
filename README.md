# ⚡ Amply: Discord-Based Electrical Engineering Lab Assistant

Amply is an autonomous AI hardware lab assistant that lives inside your team's Discord `#lab` channel. Mention `@amply` and get instant circuit calculations, sanity checks, and component values mapped to **real E12 resistors and capacitors**, in clean Unicode math that actually renders in Discord.

Built on the **Switch** platform (headless **OpenCode CLI** agent runtime + **Discord Connector**) and powered by **Google Gemini Flash Lite**.

**PakDevs · DHRZSH · Flip the Switch Hackathon**

| | |
|---|---|
| 📺 Demo video | https://youtu.be/cpbiY-cRCjg |
| 📝 Blog post | https://dev.to/imkashaf/building-amply-how-i-built-an-electrical-engineering-lab-assistant-on-switch-discord-4gnn |

![Amply answering in the Discord #lab channel](docs/screenshot-1.png)

---

## ⚡ The Problem

At an electronics bench, switching between a multimeter, an oscilloscope, and 60-page PDF datasheets breaks focus and slows down physical work. Generic AI models make it worse:

1. **Broken math in Discord.** Discord does not render LaTeX (`$`, `$$`, `\frac`, `\Omega`), so answers turn into unreadable clutter.
2. **Values that don't exist.** Models suggest theoretical values like 4.73 kΩ or 18.2 nF that are not in any component bin.
3. **Slow and wordy.** Long reasoning preambles delay a simple numerical answer on a rapid bench or viva question.

## ✅ What Amply Does

- **E12 component sizing:** maps theoretical values to standard, off-the-shelf resistors and capacitors.
- **Discord-native math:** readable Unicode (`Ω`, `µ`, `π`, `×`, `÷`) with zero LaTeX.
- **Low-latency answers:** reasoning variant set to `none` so replies come back fast.
- **Bench sanity checks:** op-amp rail clipping, supply headroom, and power dissipation.
- **Team collaboration:** runs in a shared `#lab` channel so the whole group sees the same answer.

---

## 🔌 Why Switch Is Central (and What Breaks Without It)

Amply is not a standalone bot. Switch provides the infrastructure it runs on:

| Piece | What Switch does | Without Switch we would have to... |
|---|---|---|
| **Agent runtime** | Runs the `amply` agent on OpenCode CLI headlessly and manages start, stop, and process lifecycle | Write and host our own agent runner |
| **Discord Connector** | Binds the agent to the `#lab` room so `@amply` mentions reach the agent and replies go back | Build a Discord bot server with gateway events, permissions, and retries |
| **SSE streaming** | Streams agent output back to the room in real time | Build our own streaming and message handling |
| **Rooms + instructions** | Room-level instructions keep the channel scoped to EE lab help | Build custom per-channel state and routing |

Remove Switch and Amply has no runtime, no Discord bridge, and no way to reach its users.

---

## 🏗️ Architecture

```
User in Discord (#lab)
       │
       ▼
Discord Gateway / Switch Bridge
       │
       ▼ (SSE Protocol)
Switch Console (Agent: amply)
  ├── Engine: OpenCode CLI Runner
  ├── Model: Google Gemini Flash Lite (via OpenCode)
  └── Constraints: Plain-text Unicode, E12 series, No LaTeX, Direct answers
       │
       ▼
Bench-ready output in Discord channel
```

- **Agent orchestration:** Switch Platform (local agent bridge and SSE protocol)
- **Model:** Google Gemini Flash Lite via OpenCode
- **Interface:** Discord via Switch Connectors
- **Runtime:** Node.js 18+ / Python 3.10+

---

## 🧮 Deterministic E12/E24 Snapping (`e12.py`)

LLMs can get "standard values" wrong, so the repo includes `e12.py`, a small verification module with tests. It snaps any theoretical value to the nearest E12/E24 value (log-nearest), reports the error, and computes the **actual** filter cutoff after snapping.

```bash
python e12.py 4730                  # 4730 → 4700 (E12), error -0.63%
python e12.py 18.2e-9 --series E24  # 18.2e-9 → 1.8e-08 (E24), error -1.10%
python -m unittest -v               # run the 7 unit tests
```

```python
from e12 import design_rc_filter
print(design_rc_filter(1000)["text"])
# C = 100 nF (E12), R ideal = 1591.5 Ω → 1.5 kΩ (E12), fc = 1.06103 kHz (+6.1% vs target)
```

You can use it to check any value Amply returns before you solder.

---

## 📁 Repository Structure

```
amply/
├── docs/
│   └── screenshot-1.png  # Demo screenshot used in this README
├── agent.py          # Standalone terminal prototype (Gemini SDK) used to test prompts and latency
├── e12.py            # E12/E24 snapping + RC filter helper
├── test_e12.py       # Unit tests for e12.py
├── requirements.txt  # Dependencies for agent.py
├── .env.example      # GEMINI_API_KEY placeholder
├── LICENSE           # MIT
└── README.md
```

---

## 🧪 Local Prototype (`agent.py`)

`agent.py` is a standalone terminal version of Amply built directly on the Gemini SDK. We used it to iterate on the system prompt and measure response time before moving the agent into Switch. It prints the response time after every answer.

```bash
python agent.py
```

It is **not** what runs in Discord. The Discord deployment runs entirely through Switch (OpenCode runner, Discord Connector, SSE streaming) as described above.

---

## 🚀 Setup (about 5 minutes)

### Prerequisites

- Node.js 18+ and Python 3.10+
- Switch Desktop Console installed
- A Discord account with admin rights on a server
- A Google Gemini API key from Google AI Studio

### Step 1: Clone and configure

```bash
git clone https://github.com/imkashaf/amply.git
cd amply
pip install -r requirements.txt
cp .env.example .env     # then put your GEMINI_API_KEY inside .env
python -m unittest -v    # optional: verify e12.py works
```

> The `.env` key is only used by the optional local prototype `agent.py` (see below). The Discord agent gets its model access through the OpenCode config inside Switch.

### Step 2: Create the agent in Switch Console

1. Open **Switch Console** → **Your Agents** → **Add Agent**.
2. Set:
   - **Agent Name:** `amply`
   - **Provider / CLI:** `OpenCode`
   - **Model:** a Gemini Flash Lite model from your OpenCode config list
   - **Reasoning Variant:** `none` (lowest latency, avoids timeouts)
3. Paste this into **Agent Instructions**:

```
You are Amply, a specialized Electrical Engineering Lab Assistant for students and bench prototyping.
Answer user questions directly in clear, concise plain text.

CORE OPERATIONAL RULES:
1. DIRECT TEXT OUTPUT ONLY: Never invoke external tools, room management skills, or switch connectors. Always respond immediately with direct, conversational plain text.
2. NO LATEX: Do not use LaTeX syntax, math delimiters ($ or $$), or slash commands (\frac, \Omega). Use standard Unicode characters (Ω, ±, µ, π, ×, ÷) and clear readable text.
3. BENCH ACCURACY: Only use real E12 values. E12 mantissas are 1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2 (times a power of ten). Pick the nearest one, then recompute and state the ACTUAL resulting value (for example the real cutoff frequency or gain) and its percent error versus the target.
4. FILTERS: Distinguish the natural frequency f0 = 1/(2π√(R1R2C1C2)) from the -3 dB frequency. A unity-gain Sallen-Key with equal R and equal C has Q = 0.5 (no peaking, -3 dB at about 0.64 × f0). Peaking appears only when Q is above 0.707 (for example with gain above 1 or unequal components). Never call f0 the -3 dB frequency unless Q = 0.707.
5. SANITY CHECKS: Always include practical checks: rail headroom, output clipping, and power dissipation.
6. SCOPE: Focus strictly on analog circuits, digital logic, active/passive filters, op-amps, sensors, and hardware troubleshooting.
7. CONCISE FORMATTING: Keep answers under about 1500 characters and structured to display cleanly in Discord without truncation.
```

4. Click **Save Changes**, then **Start**.

### Step 3: Link Discord

1. In Switch Console go to **Your Rooms** and select your lab channel (for example `#lab`).
2. Add these **Room Instructions**:

```
This room is the dedicated EE Hardware Lab (#lab).
Its purpose is rapid bench assistance, EE viva prep, and circuit troubleshooting for students.
All replies must be direct, bench-accurate, plain-text only (no LaTeX), and use standard E12 component values.
```

3. Open **Connectors**, authorize the **Discord Connector**, and select your server.
4. In Discord Server Settings, make sure the bot role has **View Channels**, **Send Messages**, and **Read Message History**.

### Step 4: Test in Discord

```
@amply design an inverting amplifier with a gain of -10 using standard resistors.
@amply design a 1 kHz active low-pass filter using a 741 op-amp.
@amply what is the ripple frequency of a full-wave rectifier with 50 Hz input?
@amply what is the purpose of a Zener diode in a voltage regulator?
```

---

## 👥 Who It's For

- **EE students:** lab viva prep, sizing active and passive filters, op-amps, and 555 timer circuits, and debugging breadboard anomalies without leaving Discord.
- **Hackathon teams and makers:** sensor dividers and interface circuits on tight deadlines.
- **Lab instructors and TAs:** a standardized, real-time hardware helpdesk across lab sections.

---

## ⚠️ Known Limitations

- Answers are LLM-generated. Verify calculations (use `e12.py` for component values) before powering a circuit.
- E-series snapping uses nearest-value, not tolerance stack-up analysis.
- Discord truncates long messages, so Amply is prompted to keep answers short.

## 🙌 What We Liked About Switch, and What We'd Improve

**Liked:** the connector architecture. Linking a local agent to Discord without writing a custom bot server saved a huge amount of time, and headless OpenCode with a fast model gives near-instant replies.

**Wanted next:** platform-aware markdown (auto-sanitizing math for Discord vs Slack), configurable message chunking for long derivations, and a token/latency profiler inside the Switch Console.

---

## 📄 License

MIT. See [LICENSE](LICENSE).
