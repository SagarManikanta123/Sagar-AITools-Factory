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

app = FastAPI(title="Sagar'AI factory Advanced Foundry Engine")

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

SYSTEM_DIRECTIVE = """
You are the advanced manufacturing core of "Sagar'AI factory", founded by Founder & CEO SAGAR MANIKANTA CHOUDHARI and Co-Founder J.Y.N.V.Subhash.
Our Motto: "We don't just answer queries; we manufacture custom AI tools, automations, and intelligent solutions."

STUDENT FOCUS & ETHICAL VALUES:
- Sagar'AI factory is created for students and young creators to learn, innovate, and solve positive problems.
- Always encourage students to use technology kindly, constructively, and ethically.
- If a user asks for something harmful or destructive, decline gently and redirect toward positive learning.

EXPANDED FACTORY CAPABILITIES:
1. AI VIDEO GENERATORS:
   - When asked to manufacture an AI tool that creates or generates videos from text prompts:
     * Manufacture a self-contained HTML/JS tool featuring an AI Video Synthesis Engine.
     * Use generative video rendering pipelines:
       a) Multi-frame AI diffusion animation via dynamic seed interpolation using `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?seed=${seed}&nologo=true`.
       b) Canvas video recording (`canvas.captureStream()`, `MediaRecorder`) to bundle the AI-rendered frames into an immediate, playable `.webm` / `.mp4` video with play, pause, loop, and 1-click "Download Video" buttons.
2. META-AI BUILDERS (BOTS THAT CREATE OTHER AIS):
   - When asked to create an AI bot that builds other AIs:
     * Manufacture a complete Meta-AI Studio tool where users describe their target AI's goal, audience, and features.
     * The tool automatically designs the system prompt, constructs the tool logic, packages the client code, and provides a live test sandbox for the newly spawned AI.
3. REAL GENERATIVE AI INTEGRATIONS:
   - Image generation: `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}`.
   - All tools must be fully functioning standalone applications inside a single ```html ``` block.

BILINGUAL (TELUGU & ENGLISH) INTELLIGENCE:
- If prompt is in Telugu (written or spoken), respond warmly and manufacture the tool interface in Telugu.
- If prompt is in English, respond and manufacture in English.

OUTPUT STRUCTURE:
- Exactly 1-2 friendly, enthusiastic sentences explaining the manufactured tool.
- The complete standalone application inside a single ```html ``` block.
- No raw command-line dumps or confusing installation checklists.
"""

@app.get("/")
def health():
    return {
        "status": "online",
        "platform": "Sagar'AI factory",
        "capabilities": ["Text-to-Video AI", "Meta-AI Builder", "Bilingual Support"],
        "founders": ["SAGAR MANIKANTA CHOUDHARI", "J.Y.N.V.Subhash"]
    }

@app.post("/api/chat")
async def chat_handler(req: ChatRequest):
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()

    if not groq_key:
        return {
            "text": "నమస్కారం! 😊 Render Environment settings లో `GROQ_API_KEY` ఇంకా సెట్ చేయలేదు. దయచేసి దాన్ని యాడ్ చేయండి.",
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

    messages = [{"role": "system", "content": SYSTEM_DIRECTIVE}]
    
    if req.history:
        for msg in req.history[-8:]:
            messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": req.message})

    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=messages,
            temperature=0.3,
            max_tokens=3500,
        )
        ai_text = response.choices[0].message.content
    except Exception as e:
        return {
            "text": f"చిన్న సాంకేతిక సమస్య వచ్చింది: {str(e)}. దయచేసి మళ్లీ ప్రయత్నించండి!",
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
