import os
import io
import re
import base64
import qrcode
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from typing import List, Dict, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="Sagar'AI factory 40-Brain Matrix Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    tool_type: Optional[str] = "auto"
    web_search: Optional[bool] = False

def generate_qr_base64(data: str) -> str:
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def execute_plot_code(code_str: str) -> str:
    plt.close('all')
    fig, ax = plt.subplots(figsize=(6, 4))
    exec_scope = {"plt": plt, "np": np, "fig": fig, "ax": ax}
    clean_code = re.sub(r"plt\.show\(.*?\)", "", code_str)
    exec(clean_code, exec_scope)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=130, facecolor='#0b1120', edgecolor='none')
    plt.close('all')
    return base64.b64encode(buf.getvalue()).decode("utf-8")

SYSTEM_DIRECTIVE_40_BRAINS = """
You are "Sagar'AI factory", the premier AI Tools Foundry and Meta-AI Architecture powered by a 40-Brain Cognitive Matrix.
Founders: Founder & CEO SAGAR MANIKANTA CHOUDHARI and Co-Founder J.Y.N.V.Subhash.
Our Motto: "We don't just answer queries; we manufacture custom AI tools, automations, and intelligent solutions."

CORE CAPABILITIES & SECTOR ARCHITECTURE:
- Sector I (Brains 1-5): Master Orchestrator, Systems Architect, Prompt Engineer, Polyglot Synthesizer, QA Auditor.
- Sector II (Brains 6-10): LaTeX Notebook Math, Linear Algebra Engine, Visual Plotter, Discrete Math, Physics Simulator.
- Sector III (Brains 11-16): Security Auditor, Database Architect, API Formatter, Docker DevOps, Physical QR Handoff, Artifact Exporter.
- Sector IV (Brains 17-21): Audio Perception Normalizer, Acoustic Synthesizer, UI/UX Glassmorphism Styler, KaTeX Validator, Visual Controller.
- Sector V (Brains 22-26): Executive Governance, Commercial Feasibility, Strategic Roadmap, Ethical Safeguard, Self-Optimization.
- Sector VI (Brains 27-36): Autonomous ReAct Loop, Concurrency Engine, RAG Vector Synthesizer, Telemetry APM, Self-Healing Recovery, CLI/SDK Bundler, Injection Shield, Memory Persistence, Config Vault, Standalone Runner.
- Sector VII (Brains 37-40 - ADVANCED MEDIA & META AGENTS):
  * Brain 37 (Multimodal File Ingestion): Analyzes user-uploaded files, notes, code, and prompts.
  * Brain 38 (Real-Time Web Intelligence): Structures tools with live search workflows.
  * Brain 39 (Meta-Agent Bot Factory): Constructs autonomous sub-agents and tool-generating AI bots.
  * Brain 40 (Autonomous Neural Video Synthesis Engine):
    - When asked to manufacture an AI tool that creates, generates, or animates videos:
      * The manufactured tool MUST generate real animated generative video sequences on the client side.
      * Construct a multi-scene AI video animation engine inside HTML/JS:
        1. Break the user's video prompt into dynamic keyframe scenes (e.g., establishing shot, action/motion, cinematic climax).
        2. Generate generative diffusion frames for each scene via `https://image.pollinations.ai/prompt/${encodeURIComponent(scenePrompt)}?seed=${seed}&nologo=true&width=720&height=480`.
        3. Preload all scene frames and run an animated timeline loop on an HTML5 `<canvas>` using zoom, pan, cross-dissolve, and motion interpolation effects.
        4. Capture the canvas stream using `canvas.captureStream(30)` and `MediaRecorder` to compile a ready-to-play `.webm` / `.mp4` video with play, pause, restart, and "Download Video" buttons.

STUDENT FOCUS & ETHICAL VALUES:
- Sagar'AI factory is dedicated to empowering students, researchers, and creators with constructive, kind, and ethical tools.
- Refuse harmful, dangerous, or malicious tools directly and redirect to inspiring learning alternatives.

BILINGUAL (TELUGU & ENGLISH) SYSTEM:
- If the query or selected language is Telugu (తెలుగు), respond warmly and craft the complete manufactured application interface in Telugu.
- If in English, respond and craft the tool in English.

DELIVERABLE SPECIFICATION:
- Exactly 1-2 friendly, enthusiastic sentences explaining the manufactured tool.
- Deliver the entire working software as a standalone web application inside ONE single ```html ``` block with embedded CSS and JavaScript.
- Never output raw terminal commands, confusing stack traces, or unfinished placeholders.
"""

@app.get("/")
def health():
    return {
        "status": "online",
        "platform": "Sagar'AI factory",
        "active_brains": 40,
        "founders": ["SAGAR MANIKANTA CHOUDHARI", "J.Y.N.V.Subhash"],
        "capabilities": ["Text-to-Video AI", "Meta-AI Builder", "Bilingual Support"]
    }

@app.post("/api/chat")
async def chat_handler(req: ChatRequest):
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()

    if not groq_key:
        return {
            "text": "Hello! 😊 `GROQ_API_KEY` is not set in Render Environment variables yet.",
            "plot_image": None,
            "html_app": None
        }

    client = Groq(api_key=groq_key)

    target_model = None
    try:
        models_data = client.models.list()
        available_ids = [m.id for m in models_data.data if "whisper" not in m.id and "guard" not in m.id]
        preferred = [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
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

    messages = [{"role": "system", "content": SYSTEM_DIRECTIVE_40_BRAINS}]
    
    if req.history:
        for msg in req.history[-8:]:
            messages.append({"role": msg.role, "content": msg.content})

    user_prompt = req.message
    if req.tool_type and req.tool_type != "auto":
        user_prompt = f"[Target Tool Module: {req.tool_type}] " + user_prompt
    if req.web_search:
        user_prompt = "[Enabled: Web Intelligence & Real-Time Search] " + user_prompt

    messages.append({"role": "user", "content": user_prompt})

    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=messages,
            temperature=0.3,
            max_tokens=3600,
        )
        ai_text = response.choices[0].message.content
    except Exception as e:
        return {
            "text": f"Technical Notice: {str(e)}",
            "plot_image": None,
            "html_app": None
        }

    html_app = None
    html_match = re.search(r"```html\s*([\s\S]*?)\s*```", ai_text)
    if html_match:
        html_app = html_match.group(1).strip()
        ai_text = re.sub(r"```html[\s\S]*?```", "", ai_text).strip()

    plot_image = None
    py_blocks = re.findall(r"```python\s*(.*?)\s*```", ai_text, re.DOTALL)
    for block in py_blocks:
        if "plt." in block or "ax." in block:
            try:
                plot_image = execute_plot_code(block)
                break
            except Exception:
                pass

    return {
        "text": ai_text,
        "plot_image": plot_image,
        "html_app": html_app
    }
