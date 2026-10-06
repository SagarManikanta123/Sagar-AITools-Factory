import os
import io
import re
import base64
import qrcode
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fastapi import FastAPI, HTTPException
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

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

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

@app.get("/")
def health():
    return {"status": "online", "platform": "Sagar'AI factory"}

@app.post("/api/chat")
async def chat_handler(req: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable is not configured.")

    system_directive = (
        "You are 'Sagar'AI factory', an advanced AI Tool Builder and Generator founded by "
        "Founder & CEO SAGAR MANIKANTA CHOUDHARI and CO-FOUNDER J.Y.N.V.Subhash.\n"
        "OUR CORE MOTTO: 'We don't just answer queries; we manufacture custom AI tools, automations, and intelligent solutions.'\n\n"
        "CORE CAPABILITIES:\n"
        "1. AI TOOL MAKER: When a user asks to build or design an AI tool, architect the complete tool: "
        "provide the system prompt, tool logic, API architecture, and ready-to-run code.\n"
        "2. NOTEBOOK MATHEMATICS: NEVER output raw syntax like `x**2` or plain brackets `[ ... ]`. "
        "ALWAYS use textbook LaTeX ($inline$ for inline formulas, $$display$$ for standalone equations).\n"
        "3. AUTONOMOUS VISUALIZATION: When requested to plot, chart, or generate a graph, provide clean executable Python code using `np`, `plt`, and `ax` inside ```python ``` blocks.\n"
        "4. QR GENERATOR: When asked for a QR code, end with `GENERATE_QR: <url or text>`.\n"
        "5. Deliver clear, production-ready deliverables with direct engineering focus."
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_directive},
                {"role": "user", "content": req.message}
            ],
            temperature=0.5,
            max_tokens=2048,
        )
        ai_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Inference Error: {str(e)}")

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
