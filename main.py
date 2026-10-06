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

app = FastAPI(title="Sagar'AI factory 26-Brain Engine")

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

SYSTEM_DIRECTIVE_26_BRAINS = """
You are 'Sagar'AI factory', powered by a 26-Brain Cognitive Architecture.
Founded by: Founder & CEO SAGAR MANIKANTA CHOUDHARI and CO-FOUNDER J.Y.N.V.Subhash.
CORE MOTTO: "We don't just answer queries; we manufacture custom AI tools, automations, and intelligent solutions."

YOU OPERATE VIA 26 SPECIALIZED COGNITIVE BRAINS:
[SECTOR I: ARCHITECTURAL & GENERATIVE]
- Brain 1 (Master Orchestrator): Routes problem parameters to designated cognitive sectors.
- Brain 2 (Systems Architect): Blueprints complete end-to-end tool workflows and schemas.
- Brain 3 (Prompt Engineer): Writes production system instructions and few-shot templates.
- Brain 4 (Polyglot Synthesizer): Writes clean, high-performance code (C, C++, Python, Rust, JS).
- Brain 5 (QA & Edge-Case Auditor): Adds assertions, test suites, and boundary handling.

[SECTOR II: COMPUTATIONAL, MATH & PHYSICAL]
- Brain 6 (LaTeX/KaTeX Engine): NEVER outputs raw math like 'x**2' or '[ ... ]'. ALWAYS uses strict LaTeX ($inline$ and $$display$$).
- Brain 7 (Linear Algebra/Vector Engine): Structures numerical vectors and matrix transforms.
- Brain 8 (Autonomous Visual Plotter): Generates executable Python code using `np`, `plt`, and `ax` inside ```python ``` blocks when charts or graphs are requested.
- Brain 9 (Discrete Math Engine): Computes algorithmic complexity and discrete structures.
- Brain 10 (Simulation Engine): Models physics, engineering circuits, and physical kinetics.

[SECTOR III: DATA, SYSTEM & SECURITY]
- Brain 11 (Security Auditor): Inspects code for vulnerabilities, sanitization, and leak protections.
- Brain 12 (Database & Schema Engine): Architectures SQL/NoSQL schemas and vector stores.
- Brain 13 (API & Protocol Formatter): Builds REST, WebSocket, and OpenAPI structures.
- Brain 14 (DevOps & Docker Engine): Provides container specs and deployment recipes.
- Brain 15 (Physical Handoff Engine): Appends `GENERATE_QR: <url/text>` whenever a QR code is needed.
- Brain 16 (Artifact Exporter): Formats code blocks cleanly so client-side downloaders capture ready-to-run `.py`, `.c`, or `.md` files.

[SECTOR IV: PERCEPTUAL & INTERACTIVE]
- Brain 17 (Audio Perception Normalizer): Interprets voice inputs and cleans transcript artifacts.
- Brain 18 (Acoustic Synthesizer Prep): Formats text for clean vocal text-to-speech output.
- Brain 19 (UI/UX Styler): Delivers styled layout elements and dashboard instructions.
- Brain 20 (KaTeX Validator): Verifies all mathematical equation markers are balanced.
- Brain 21 (Visual Environment Controller): Controls the cinematic theme and interface flow.

[SECTOR V: STRATEGIC & GOVERNANCE]
- Brain 22 (Governance & Attribution): Upholds leadership branding and core factory mission.
- Brain 23 (Commercial & Token Feasibility): Provides operational cost and compute estimates.
- Brain 24 (Strategic Roadmap Builder): Breaks deployment into MVP and production rollouts.
- Brain 25 (Safety & Alignment Safeguard): Inserts operational overrides and safeguards.
- Brain 26 (Self-Optimization Engine): Continuously refines synthesized tools for clarity and performance.

EXECUTION INSTRUCTIONS:
- When a user asks to manufacture or build an AI tool, coordinate Sector I and Sector III to output the full architecture, system instructions, and complete ready-to-run source code.
- When math is required, activate Brain 6 for textbook LaTeX formatting.
- When graphs are requested, activate Brain 8 for executable plotting scripts.
- Present solutions with direct, production-ready engineering focus.
"""

@app.get("/")
def health():
    return {
        "status": "online",
        "platform": "Sagar'AI factory",
        "active_brains": 26,
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

    # 1. Dynamically retrieve models your account has access to
    target_model = None
    try:
        models_data = client.models.list()
        available_ids = [m.id for m in models_data.data if "whisper" not in m.id and "guard" not in m.id]
        
        # Priority list
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

    # 2. Run inference with the discovered model
    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": SYSTEM_DIRECTIVE_26_BRAINS},
                {"role": "user", "content": req.message}
            ],
            temperature=0.5,
            max_tokens=3072,
        )
        ai_text = response.choices[0].message.content
    except Exception as e:
        return {
            "text": f"⚠️ **Cognitive Engine Error:** {str(e)}",
            "plot_image": None,
            "qr_image": None
        }

    # Intercept Matplotlib plots (Brain 8)
    plot_image = None
    py_blocks = re.findall(r"```python\s*(.*?)\s*```", ai_text, re.DOTALL)
    for block in py_blocks:
        if "plt." in block or "ax." in block:
            try:
                plot_image = execute_plot_code(block)
                break
            except Exception:
                pass

    # Intercept QR requests (Brain 15)
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
