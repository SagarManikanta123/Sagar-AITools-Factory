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
1. NEVER OUTPUT TERMINAL TUTORIALS, RAW CODE SNIPPETS, OR PYTHON PACKAGING GUIDES TO THE USER.
   - The user does not want terminal scripts or `pip install` commands.
   - The user wants a REAL, FINISHED, WORKING TOOL they can use immediately.

2. MANUFACTURE EVERY TOOL AS A COMPLETE STANDALONE WEB APPLICATION:
   - Provide a complete HTML file inside a single ```html ``` code block.
   - The HTML must include its own embedded CSS and JavaScript.
   - It must have a clean, modern UI (dark mode with clear buttons, inputs, and results area).
   - If image generation is requested, the application's JavaScript must generate real AI images using `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}` and display them immediately.
   - If PDF generation is requested, use standard client-side PDF generation or printable styled window views (`window.print()`).
   - If C code generation is requested, it must have an interactive prompt where users type ideas and get instant formatted C code with a 1-click copy button.

3. RESPONSE FORMAT:
   - Exactly 2 sentences in natural, plain human English explaining what tool was manufactured.
   - The single complete ```html ``` code block containing the full interactive tool.
   - No markdown checklists, no ASCII architecture art, and no terminal installation steps.
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
            "qr_image": None,
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
            "qr_image": None,
            "html_app": None
        }

    # Extract standalone HTML application if generated
    html_app = None
    html_match = re.search(r"```html\s*([\s\S]*?)\s*```", ai_text)
    if html_match:
        html_app = html_match.group(1).strip()
        # Clean text so the user only reads the clean human overview
        ai_text = re.sub(r"```html[\s\S]*?```", "", ai_text).strip()

    # Autonomous Plot Handling
    plot_image = None
    py_blocks = re.findall(r"```python\s*(.*?)\s*```", ai_text, re.DOTALL)
    for block in py_blocks:
        if "plt." in block or "ax." in block:
            try:
                plot_image = execute_plot_code(block)
                break
            except Exception:
                pass

    # Clean legacy markers
    ai_text = re.sub(r"GENERATE_QR:\s*\S+", "", ai_text).strip()

    return {
        "text": ai_text,
        "plot_image": plot_image,
        "html_app": html_app
    }
