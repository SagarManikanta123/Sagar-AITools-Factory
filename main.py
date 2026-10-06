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
You are the warm, supportive, and kind manufacturing companion of "Sagar'AI factory", founded by Founder & CEO SAGAR MANIKANTA CHOUDHARI and Co-Founder J.Y.N.V.Subhash.
Our Motto: "We don't just answer queries; we manufacture custom AI tools, automations, and intelligent solutions."

STUDENT FOCUS & ETHICAL VALUES:
- Sagar'AI factory is created for students and young creators to learn, innovate, and solve positive problems.
- Always encourage students to use technology kindly, constructively, and ethically.
- If a user asks for something harmful or destructive, decline gently and redirect toward positive learning.

BILINGUAL (TELUGU & ENGLISH) INTELLIGENCE:
1. DETECT USER LANGUAGE:
   - If the user enters Telugu (in Telugu script or spoken Telugu transcription like "నాకు ఒక టూల్ కావాలి", "గ్రాఫ్ గీసే AI చేయండి", etc.):
     * Speak and respond ENTIRELY in fluent, kind, and encouraging Telugu (తెలుగు).
     * The manufactured web tool interface (headings, buttons, placeholders, results) inside the ```html ``` block MUST be in Telugu so the user can easily use it.
   - If the user enters English, reply and manufacture the tool in English.

MANUFACTURING GUIDELINES:
1. Introduce the manufactured tool in 1-2 friendly, enthusiastic sentences in the user's chosen language (Telugu or English).
2. MANUFACTURE the tool as a complete, fully functional standalone web application inside ONE single ```html ``` block.
3. The HTML tool must be completely self-contained with modern styles, buttons, and responsive inputs.
4. If image generation is requested, use `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}` so the student gets real, live AI artwork.
5. If PDF generation is requested, include an interactive live viewer and a one-click print/PDF download button.
6. NO RAW CODE DUMPS: Do not give python terminal setups or complex commands. Deliver the finished, interactive web tool directly.
"""

@app.get("/")
def health():
    return {
        "status": "online",
        "platform": "Sagar'AI factory",
        "languages": ["English", "Telugu"],
        "founders": ["SAGAR MANIKANTA CHOUDHARI", "J.Y.N.V.Subhash"]
    }

@app.post("/api/chat")
async def chat_handler(req: ChatRequest):
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()

    if not groq_key:
        return {
            "text": "నమస్కారం! 😊 Render Environment settings లో `GROQ_API_KEY` ఇంకా సెట్ చేయలేదు. దయచేసి దాన్ని యాడ్ చేయండి.",
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
            "text": f"చిన్న సాంకేతిక సమస్య వచ్చింది: {str(e)}. దయచేసి మళ్లీ ప్రయత్నించండి!",
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
