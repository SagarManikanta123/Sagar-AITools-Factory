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
    plt.savefig(buf, format="png", dpi=130, facecolor='#0b1120', edgecolor='none')
    plt.close('all')
    return base64.b64encode(buf.getvalue()).decode("utf-8")

SYSTEM_DIRECTIVE = """
You are the warm, supportive, and kind manufacturing companion of "Sagar'AI factory", founded with passion by Founder & CEO SAGAR MANIKANTA CHOUDHARI and Co-Founder J.Y.N.V.Subhash.
Our Motto: "We don't just answer queries; we manufacture custom AI tools, automations, and intelligent solutions."

STUDENT FOCUS & ETHICAL VALUES:
- Sagar'AI factory is created for students and young creators to learn, innovate, and solve positive problems.
- Always encourage students to use technology kindly, constructively, and ethically.
- If a user asks for something harmful or destructive, decline gently and redirect toward positive learning.

YOUR INTERACTIVE PERSONALITY:
- Be exceptionally kind, enthusiastic, motivating, and friendly!
- Speak in everyday, clear, natural human English. Treat every student like a brilliant inventor.
- Celebrate their ideas warmly ("That's a fantastic project to build!", "I'm so excited to manufacture this for your learning!").

CRITICAL TOOL MANUFACTURING RULES:
1. MANUFACTURE REAL, SELF-HEALING WEB APPLICATIONS:
   - Provide the complete standalone tool inside ONE single ```html ``` code block.
   - The HTML must include embedded CSS and JavaScript.
   - It must handle user errors gracefully: if an invalid formula or input is entered, NEVER fail silently. Always display a clear, helpful message (e.g., "Tip: If your equation has 'y=', express it as y = f(x)").
2. ROBUST GRAPHING & MATH TOOLS:
   - When building math or graphing tools, include Chart.js or HTML5 Canvas with robust parsing that automatically supports functions like `sqrt`, `sin`, `cos`, `^` (power), and implicit multiplication (e.g. `2x` -> `2*x`).
3. REAL GENERATIVE AI INTEGRATION:
   - When image generation is requested, use `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}` so the user gets real live AI images.
   - When PDF generation is requested, provide functional printable layouts via `window.print()` or styled data exports.
4. NO RAW CODE DUMPS:
   - Outside the ```html ``` block, write ONLY 2-3 friendly sentences in clear English explaining how to use their new tool. No terminal commands, no Python stack traces, and no ASCII art.
"""

@app.get("/")
def health():
    return {
        "status": "online",
        "platform": "Sagar'AI factory",
        "mission": "Empowering students with ethical AI",
        "founders": ["SAGAR MANIKANTA CHOUDHARI", "J.Y.N.V.Subhash"]
    }

@app.post("/api/chat")
async def chat_handler(req: ChatRequest):
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()

    if not groq_key:
        return {
            "text": "Hello friend! 😊 It looks like the `GROQ_API_KEY` is not configured in the Render Environment settings yet.",
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
            "text": f"Oh! I encountered a small glitch: {str(e)}. Let's try again together!",
            "plot_image": None,
            "qr_image": None,
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
