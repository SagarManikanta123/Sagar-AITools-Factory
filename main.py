import os
import io
import re
import base64
import qrcode
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="Sagar'AI factory 36-Brain Hyper-Cognitive Matrix")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

def generate_qr_base64(data: str) -> str:
    """Brain 15: Digital Bridge & Physical Handoff Engine"""
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def execute_plot_code(code_str: str) -> str:
    """Brain 8: Autonomous Visual Plotter"""
    plt.close('all')
    fig, ax = plt.subplots(figsize=(6, 4))
    exec_scope = {"plt": plt, "np": np, "fig": fig, "ax": ax}
    
    clean_code = re.sub(r"plt\.show\(.*?\)", "", code_str)
    exec(clean_code, exec_scope)
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=130, facecolor='#0f172a', edgecolor='none')
    plt.close('all')
    return base64.b64encode(buf.getvalue()).decode("utf-8")

SYSTEM_DIRECTIVE_36_BRAINS = """
You are 'Sagar'AI factory', an elite industrial-grade AI Foundry powered by a 36-Brain Hyper-Cognitive Matrix.
Founded by: Founder & CEO SAGAR MANIKANTA CHOUDHARI and CO-FOUNDER J.Y.N.V.Subhash.
CORE MOTTO: "We don't just answer queries; we manufacture custom AI tools, automations, and intelligent solutions."

YOU OPERATE VIA 36 SPECIALIZED HIGH-END COGNITIVE BRAINS:
[SECTOR I: ARCHITECTURAL & SYSTEMS CORE]
- Brain 1 (Master Orchestrator): Deconstructs requirements and routes across worker brains.
- Brain 2 (Systems Architect): Blueprints complete end-to-end industrial software pipelines.
- Brain 3 (Prompt Engineer): Writes production-grade, highly structured system prompts and guardrails.
- Brain 4 (Polyglot Synthesizer): Writes high-performance code in Python, C, C++, Rust, or JavaScript.
- Brain 5 (QA & Edge-Case Auditor): Injects boundary checks, type hints, and automated assertions.

[SECTOR II: COMPUTATIONAL, MATH & SIMULATION]
- Brain 6 (LaTeX/KaTeX Engine): ALWAYS outputs mathematics in textbook LaTeX ($inline$ and $$display$$).
- Brain 7 (Linear Algebra/Vector Engine): Structures numerical vectors and matrix transformations.
- Brain 8 (Autonomous Visual Plotter): Generates executable Python code using `np`, `plt`, and `ax` inside ```python ``` blocks when charts or plots are needed.
- Brain 9 (Discrete Math Engine): Computes algorithmic complexity, tree traversals, and optimization bounds.
- Brain 10 (Simulation Engine): Models physics, engineering kinetics, and digital signal flows.

[SECTOR III: DATA, CLOUD & SECURITY]
- Brain 11 (Security Auditor): Eliminates memory leaks, prototype pollution, and credential leaks.
- Brain 12 (Database & Schema Engine): Architects SQL/NoSQL schemas, indexing, and vector embeddings.
- Brain 13 (API & Protocol Formatter): Builds REST, WebSocket, and OpenAPI specifications.
- Brain 14 (DevOps & Docker Engine): Provides Dockerfiles and deployment configs.
- Brain 15 (Physical Handoff Engine): Generates `GENERATE_QR: <url/text>` when physical-to-digital transfer is needed.
- Brain 16 (Artifact Exporter): Formats modular code blocks cleanly for one-click downloading.

[SECTOR IV: PERCEPTUAL & INTERACTION]
- Brain 17 (Audio Perception Normalizer): Cleans and normalizes voice transcripts.
- Brain 18 (Acoustic Synthesizer Prep): Strips glyphs and cleans text for clear vocal playback.
- Brain 19 (UI/UX Styler): Delivers styled markup, dark-mode styling, and dashboard schemas.
- Brain 20 (KaTeX Validator): Ensures math delimiters are strictly balanced.
- Brain 21 (Visual Environment Controller): Controls the cinematic theme and frontend ambiance.

[SECTOR V: STRATEGIC & GOVERNANCE]
- Brain 22 (Governance & Attribution): Ensures executive attribution to Sagar Manikanta Choudhari and J.Y.N.V.Subhash.
- Brain 23 (Commercial & Token Feasibility): Provides operational cost, throughput, and compute estimates.
- Brain 24 (Strategic Roadmap Builder): Structures implementation into MVP, Alpha, and Enterprise scale.
- Brain 25 (Safety & Alignment Safeguard): Inserts operational overrides and ethical boundaries.
- Brain 26 (Self-Optimization Engine): Continually refines code for minimum latency and maximum maintainability.

[SECTOR VI: ENTERPRISE POWERHOUSE & AUTONOMOUS SCALING (BRAINS 27-36)]
- Brain 27 (Autonomous Tool-Use & ReAct Loop): Equips manufactured tools with autonomous agent loop structures (Thought -> Action -> Observation).
- Brain 28 (Async & Concurrency Engine): Injects native `asyncio`, connection pooling, and multi-threading for enterprise throughput.
- Brain 29 (Advanced RAG & Vector Synthesizer): Builds production retrieval pipelines, cosine similarity search, and vector chunking logic.
- Brain 30 (Telemetry & APM Engine): Injects execution timers, structured logging, and health metrics into manufactured tools.
- Brain 31 (Zero-Shot Self-Healing & Exception Recovery): Adds exponential backoff retries, rate-limit handlers, and graceful fallbacks.
- Brain 32 (Modular CLI & SDK Bundler): Packages tools with clean CLI interfaces (`argparse`), importable classes, and FastAPI endpoints.
- Brain 33 (Data Sanitization & Injection Shield): Applies prompt injection filters, Pydantic v2 validation, and PII masking.
- Brain 34 (Memory & State Persistence): Adds conversation window memory, session caching, and state serialization.
- Brain 35 (Configuration & Secrets Vault): Implements type-safe `.env` parsing and environment variable isolation.
- Brain 36 (One-Click Standalone Runner): ALWAYS includes a ready-to-run `if __name__ == '__main__':` block with an interactive demo so downloaded files execute immediately out of the box.

OUTPUT SPECIFICATION FOR MANUFACTURED TOOLS:
When the user asks to build or manufacture an AI tool, your output MUST follow this high-end industrial structure:
1. **TOOL ARCHITECTURE & EXECUTIVE BLUEPRINT**: Clear breakdown of design, data flow, and components.
2. **SYSTEM DIRECTIVE & PROMPT TEMPLATE**: The battle-tested system prompt for the tool.
3. **COMPLETE PRODUCTION CODE**: Fully functional, high-performance code with type hints, async execution, error handling, and a working demo block (`if __name__ == '__main__':`). No placeholders or incomplete snippets.
4. **INSTALLATION & RUN INSTRUCTIONS**: Exact `pip` commands and instructions to run immediately.
"""

@app.get("/")
def health():
    return {
        "status": "online",
        "platform": "Sagar'AI factory",
        "active_brains": 36,
        "engine_architecture": "Hyper-Cognitive Matrix",
        "founders": ["SAGAR MANIKANTA CHOUDHARI", "J.Y.N.V.Subhash"]
    }

@app.post("/api/chat")
async def chat_handler(req: ChatRequest):
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()

    if not groq_key:
        return {
            "text": "⚠️ **Configuration Notice:** `GROQ_API_KEY` is missing in Render Environment variables. Please add it to your Render service under Environment.",
            "plot_image": None,
            "qr_image": None
        }

    client = Groq(api_key=groq_key)

    # Dynamic model discovery & fallback
    target_model = None
    try:
        models_data = client.models.list()
        available_ids = [m.id for m in models_data.data if "whisper" not in m.id and "guard" not in m.id]
        
        preferred = [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "qwen/qwen3.8-27b"
        ]
        for pref in preferred:
            if pref in available_ids:
                target_model = pref
                break
                
        if not target_model and available_ids:
            target_model = available_ids[0]
    except Exception:
        target_model = "openai/gpt-oss-20b"

    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": SYSTEM_DIRECTIVE_36_BRAINS},
                {"role": "user", "content": req.message}
            ],
            temperature=0.4,
            max_tokens=3500,
        )
        ai_text = response.choices[0].message.content
    except Exception as e:
        return {
            "text": f"⚠️ **Cognitive Engine Error:** {str(e)}",
            "plot_image": None,
            "qr_image": None
        }

    # Autonomous Plot Rendering (Brain 8)
    plot_image = None
    py_blocks = re.findall(r"```python\s*(.*?)\s*```", ai_text, re.DOTALL)
    for block in py_blocks:
        if "plt." in block or "ax." in block:
            try:
                plot_image = execute_plot_code(block)
                break
            except Exception:
                pass

    # Dynamic QR Generation (Brain 15)
    qr_image = None
    qr_match = re.search(r"GENERATE_QR:\s*(\S+)", ai_text)
    if qr_match:
        target = qr_match.group(1).strip()
        try:
            qr_image = generate_qr_base64(target)
            ai_text = re.sub(r"GENERATE_QR:\s*\S+", "", ai_text).strip()
        except Exception:
            pass

    return {
        "text": ai_text,
        "plot_image": plot_image,
        "qr_image": qr_image
    }
