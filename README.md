# Amply: Discord-Based Electrical Engineering Lab Assistant

Amply is a real-time, low-latency AI lab companion for electronics engineering students and hardware developers, built using **Switch** and powered by Google's `gemini-3.5-flash-lite`. 

It operates directly inside team Discord channels, providing instant workbench calculations, standard component sizing (E12/E24 series), and circuit diagnostics using clean plain-text/Unicode formatting without broken LaTeX syntax.

---

## ⚡ Problem Statement
When testing circuits at an electronics workbench, switching between multimeters, oscilloscopes, and desktop SPICE simulators breaks concentration. Standard LLMs in chat channels suffer from:
1. **Broken Math Formatting:** Discord does not natively render LaTeX delimiters (`\frac`, `$$`).
2. **High Latency:** Heavy multimodal models hit rate limits and introduce slow response times during live lab testing.

---

## 🛠️ Tech Stack & Architecture
- **Orchestration:** [Switch](https://github.com/sandbox-quantum/switch) (Local Agent Bridge & SSE Protocol)
- **Engine:** Google Gemini (`gemini-3.5-flash-lite`)
- **Chat Relay:** Discord via Switch Console
- **System Constraints:** Pure Unicode/plain-text math formatting (`kΩ`, `µF`, `π`, `Av`)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone [https://github.com/imkashaf/amply.git](https://github.com/imkashaf/amply.git)
cd amply