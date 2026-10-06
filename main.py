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

app = FastAPI(title="Sagar'AI factory Engine")

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
    plt.savefig(buf, format="png", dpi=130, facecolor='#0f172a', edgecolor='none')
    plt.close('all')
    return base64.b64encode(buf.getvalue()).decode("utf-8")

SYSTEM_DIRECTIVE = """
You are the manufacturing core of "Sagar'AI factory", founded by Founder & CEO SAGAR MANIKANTA CHOUDHARI and Co-Founder J.Y.N.V.Subhash.
Our Motto: "We don't just answer queries; we manufacture custom AI tools, automations, and intelligent solutions."

MANDATORY RULES:
1. USE NATURAL, CLEAR, PROFESSIONAL HUMAN ENGLISH: Avoid robotic jargon, raw dumps, or theoretical ASCII box diagrams.
2. DELIVER WORKING TOOLS, NOT ABSTRACT BLUEPRINTS: When a user asks to make an AI tool, your primary deliverable is a single, complete, copy-paste ready, executable Python script (.py).
3. EXECUTABLE DESIGN:
   - The script must be fully self-contained inside a single ```python ``` block.
   - Include a working interactive loop in `if __name__ == '__main__':` so running `python <file>.py` lets the user immediately interact with their tool in the terminal.
   - If the tool requires an LLM or API, provide an out-of-the-box working implementation (e.g., using Groq, simple heuristics, or standard Python libraries) without requiring complex microservice setup.
4. STRUCTURE YOUR RESPONSE INTO 3 CONCISE PARTS:
   - **Tool Overview:** Explain clearly what the tool does in standard, simple English.
   - **The Manufactured AI Tool Code:** The complete Python code in a single clean ```python ``` code block.
   - **Quick Start Instructions:** Brief commands (e.g., `pip install ...` and `python tool.py`) to run it immediately.
"""

@app.get("/")
def health():
    return {
        "status": "online",
        "platform": "Sagar'AI factory",
        "founders": ["SAGAR MANIKANTA CHOUDHARI", "J.Y.N.V.Subhash"]
    }

@app.post("/api/chat")
async def chat_handler(req: ChatRequest):
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()

    if not groq_key:
        return {
            "text": "⚠️ **Configuration Notice:** `GROQ_API_KEY` is not set in Render Environment variables.",
            "plot_image": None,
            "qr_image": None
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

    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": SYSTEM_DIRECTIVE},
                {"role": "user", "content": req.message}
            ],
            temperature=0.3,
            max_tokens=3500,
        )
        ai_text = response.choices[0].message.content
    except Exception as e:
        return {
            "text": f"⚠️ **Engine Error:** {str(e)}",
            "plot_image": None,
            "qr_image": None
        }

    plot_image = None
    py_blocks = re.findall(r"```python\s*(.*?)\s*```", ai_text, re.DOTALL)
    for block in py_blocks:
        if "plt." in block or "ax." in block:
            try:
                plot_image = execute_plot_code(block)
                break
            except Exception:
                pass

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
