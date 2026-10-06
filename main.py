from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests, re, os, io, base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import qrcode

app = FastAPI(title="Sagar'AI Factory Core Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

class QueryPayload(BaseModel):
    message: str

def convert_to_notebook_math(text: str) -> str:
    if not text:
        return ""
    converted = re.sub(r"(?<!\\)\[\s*([\s\S]*?)\s*\]", r"$$\1$$", text)
    converted = re.sub(r"\\\(\s*([\s\S]*?)\s*\\\)", r"$\1$", converted)
    converted = re.sub(r"\\\[\s*([\s\S]*?)\s*\\\]", r"$$\1$$", converted)
    return converted

def execute_plot_code(code_snippet: str):
    plt.close("all")
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    safe_globals = {
        "np": np,
        "plt": plt,
        "fig": fig,
        "ax": ax,
        "sp": sp
    }
    try:
        exec(code_snippet, safe_globals)
        active_fig = safe_globals.get("fig") or plt.gcf()
        buf = io.BytesIO()
        active_fig.savefig(buf, format="png", bbox_inches="tight", dpi=160)
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return None

@app.get("/")
def health_check():
    return {"status": "online", "platform": "Sagar'AI factory"}

@app.post("/api/chat")
async def chat_handler(payload: QueryPayload):
    user_query = payload.message
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable is missing on server.")

    system_directive = (
        "You are Sagar'AI factory, founded by Founder & CEO SAGAR MANIKANTA CHOUDHARI "
        "and CO-FOUNDER J.Y.N.V.Subhash.\n"
        "DIRECTIVES:\n"
        "1. NOTEBOOK MATHEMATICS: NEVER output raw syntax like `x**2` or plain brackets `[ ... ]`. "
        "ALWAYS use LaTeX ($inline$ for terms, $$display$$ for standalone equations).\n"
        "2. DRAWING AGENT: When asked to plot, graph, or visualize an equation, function, or curve, "
        "provide clean executable Python code using `np`, `plt`, and `ax` inside ```python ``` at the bottom.\n"
        "3. QR CODE: If requested, conclude with `GENERATE_QR: <url or string>`.\n"
        "4. NO IN-BETWEEN CODE: Do NOT include raw code in your text explanation."
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": system_directive},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.2,
        "max_tokens": 1900
    }

    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=50)
    if res.status_code != 200:
        raise HTTPException(status_code=502, detail=res.text)

    raw_response = res.json()["choices"][0]["message"]["content"]

    plot_b64 = None
    code_match = re.search(r"```(?:python)?\s*(.*?)\s*```", raw_response, re.DOTALL)
    if code_match:
        plot_b64 = execute_plot_code(code_match.group(1))

    qr_b64 = None
    qr_match = re.search(r"GENERATE_QR:\s*(.+)", raw_response, re.IGNORECASE)
    if qr_match:
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(qr_match.group(1).strip())
        qr.make(fit=True)
        img_buf = io.BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(img_buf, format="PNG")
        qr_b64 = base64.b64encode(img_buf.getvalue()).decode("utf-8")

    cleaned = re.sub(r"GENERATE_QR:\s*.+", "", raw_response, flags=re.IGNORECASE)
    cleaned = re.sub(r"```(?:python)?\s*.*?```", "", cleaned, flags=re.DOTALL).strip()
    cleaned = convert_to_notebook_math(cleaned)

    return {
        "text": cleaned,
        "plot_image": plot_b64,
        "qr_image": qr_b64
    }
