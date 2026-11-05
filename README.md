# Amply: Discord-Based Electrical Engineering Lab Assistant

Amply is a real-time, autonomous AI hardware lab assistant designed for electrical engineering students, circuit designers, and bench prototypers. Built using the **Switch** platform and powered by **Google's Gemini**, Amply runs directly inside Discord channels to deliver immediate circuit calculations, standard component sizing, and lab troubleshooting.

---

## ⚡ Problem Statement
During active hardware prototyping at an electronics workbench, switching between multimeters, oscilloscopes, and 60-page PDF datasheets breaks focus and slows down physical bench work.

Generic LLMs fail on the lab bench because:
1. **Broken Math Formatting:** Discord does not natively render LaTeX delimiters (`$`, `$$`, `\frac`, `\Omega`), creating cluttered, unreadable syntax.
2. **Impractical Theoretical Values:** Generic models output theoretical values (e.g., 4.73 kΩ or 18.2 nF) that do not exist in standard lab component bins.
3. **High Latency & Verbose Fluff:** Standard models take 30+ seconds with long chain-of-thought preambles before giving a simple numerical value.

Amply solves this with clean Unicode math, low-latency execution (<3s), and automatic mapping to real-world, commercially accessible E12/E24 series components.

---

## 🛠️ Key Features
* **Standard E12/E24 Component Sizing:** Automatically rounds and maps component values to standard, off-the-shelf resistors and capacitors.
* **Discord-Native Math Formatting:** Delivers clean formulas using readable Unicode (`Ω`, `µ`, `π`, `×`, `÷`) with zero LaTeX syntax.
* **Low Latency & High Speed:** Configured with minimal/no reasoning overhead for near-instant (<3s) answers at the bench.
* **Bench Sanity Checks:** Proactively provides operational checks including op-amp output rail clipping, power dissipation, and supply headroom limits.
* **Channel-Based Collaboration:** Runs inside team Discord `#lab` channels so lab groups can troubleshoot collaboratively.

---

## 🏗️ Architecture & Tech Stack

```text
User in Discord (#lab)
       │
       ▼
Discord Gateway / Switch Bridge
       │
       ▼ (SSE Protocol)
Switch Console (Agent: amply)
  ├── Engine: OpenCode CLI Runner
  ├── Model: Google Gemini (via OpenCode)
  └── Constraints: Plain-text Unicode, E12 series, No LaTeX, Direct answers
       │
       ▼
Instant Bench-Ready Output in Discord Channel
```

* **Agent Orchestration:** Switch Platform (Local Agent Bridge & SSE Protocol)
* **Model Engine:** Google Gemini (via OpenCode)
* **Interface Relay:** Discord API via Switch Connectors
* **Runtime:** Node.js (v18+) / Python (3.10+)

---

## 🚀 Setup & Installation Guide
Follow these steps to run Amply locally and connect it to your Discord server:

### Prerequisites
* Node.js (v18 or higher)
* Python (v3.10 or higher)
* Switch Desktop Console installed on your machine
* A Discord account with administrative permissions on a server
* A Google Gemini API Key from Google AI Studio

### Step 1: Clone the Repository
```bash
git clone https://github.com/imkashaf/amply.git
cd amply
```

### Step 2: Configure Environment Variables
Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### Step 3: Configure Amply in Switch Console
1. Open the Switch Console desktop application.
2. Navigate to **Your Agents** in the left sidebar and select **amply** (or click *Add Agent*).
3. Set the agent configuration:
   * **Agent Name:** `amply`
   * **Provider / CLI:** `OpenCode`
   * **Model:** *Select an available Gemini Flash model from your OpenCode config list*
   * **Reasoning Variant:** Set to **none** (to minimize latency and avoid execution timeouts)

4. In the **Agent Instructions** field, paste the following prompt:

```text
You are Amply, a specialized Electrical Engineering Lab Assistant for students and bench prototyping.
Answer user questions directly in clear, concise plain text.

CORE OPERATIONAL RULES:
1. DIRECT TEXT OUTPUT ONLY: Never invoke external tools, room management skills, or switch connectors. Always respond immediately with direct, conversational plain text.
2. NO LATEX: Do not use LaTeX syntax, math delimiters ($ or $$), or slash commands (\frac, \Omega). Use standard Unicode characters (Ω, ±, µ, π, ×, ÷) and clear readable text.
3. BENCH ACCURACY: Always recommend real-world standard E12 resistor and capacitor values. Provide step-by-step math and include practical sanity checks (rail headroom, clipping limits).
4. SCOPE: Focus strictly on analog circuits, digital logic, active/passive filters, op-amps, sensors, and hardware troubleshooting.
5. CONCISE FORMATTING: Keep answers direct and structured to display cleanly in Discord without truncation.
```
5. Click **Save Changes** and click **Start** to bring the agent online.

### Step 4: Configure Room Context & Link Discord
1. In Switch Console, go to **Your Rooms** and select your lab channel (e.g., `#lab`).
2. In **Room Instructions**, add:
```text
This room is the dedicated EE Hardware Lab (#lab).
Its purpose is rapid bench assistance, EE viva prep, and circuit troubleshooting for students.
All replies must be direct, bench-accurate, plain-text only (no LaTeX), and use standard E12 component values.
```
3. Go to **Connectors** in Switch Console.
4. Authorize the **Discord Connector** and select your target server.
5. In Discord Server Settings, verify the bot role has:
   * View Channels
   * Send Messages
   * Read Message History

### Step 5: Test in Discord
Inside your Discord `#lab` channel, mention `@amply` to verify functionality:

* **Op-Amp Design:**
  ```text
  @amply design an inverting amplifier with a gain of -10 using standard resistors.
  ```
* **Filter Calculations:**
  ```text
  @amply design a 1 kHz active low-pass filter using a 741 op-amp.
  ```
* **Viva Quick Question:**
  ```text
  @amply what is the ripple frequency of a full-wave rectifier with 50 Hz input?
  ```
* **Bench Troubleshooting:**
  ```text
  @amply what is the purpose of a Zener diode in a voltage regulator?
  ```

---

## 👥 Target Audience
* **Electrical Engineering Students:** Quick lab experiment derivations, viva prep, and component sizing without leaving the bench.
* **Hardware Prototypers & Hackathon Teams:** Fast sanity checks on sensor dividers, filter stages, and operational amplifier headroom.
* **Lab TAs & Instructors:** Running interactive hardware support channels across student lab sections.

---

## 📄 License
This project is open-source under the **MIT License**.
