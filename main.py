The model 'llama-3.1-8b-instant' does not exist or you do not have access to it.
```

Everything in your frontend, download engine, and backend communication is working[cite: 20, 21]. The reason you saw that error is that **`main.py` is still using `'llama-3.1-8b-instant'`**, which is not accessible on your Groq tier.

On Groq's standard developer tier, the active production models are **`llama-3.3-70b-versatile`** or **`openai/gpt-oss-20b`**.

To make your backend resilient against model availability changes, we will use a **fallback chain**: it tries `llama-3.3-70b-versatile` first, and if Groq rejects it, it automatically falls back to `openai/gpt-oss-20b` or `qwen/qwen3.8-27b`.

---

### Step 1: Update `main.py` on GitHub

1. Open your **GitHub** tab for **`Sagar-AITools-Factory`**.
2. Click on **`main.py`** $\rightarrow$ click the **Pencil icon** (Edit).
3. Select everything (`Ctrl + A`), delete it, and paste this complete code:

```python
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

# Candidate models in order of preference
CANDIDATE_MODELS = [
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b"
]

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
    ai_text = None
    last_error = None

    # Multi-model fallback: try each model until one succeeds
    for model_id in CANDIDATE_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": SYSTEM_DIRECTIVE_26_BRAINS},
                    {"role": "user", "content": req.message}
                ],
                temperature=0.5,
                max_tokens=3072,
            )
            ai_text = response.choices[0].message.content
            break
        except Exception as e:
            last_error = str(e)
            continue

    if not ai_text:
        return {
            "text": f"⚠️ **Groq API Error:** {last_error}",
            "plot_image": None,
            "qr_image": None
        }

    # Intercept Matplotlib plots
    plot_image = None
    py_blocks = re.findall(r"```python\s*(.*?)\s*```", ai_text, re.DOTALL)
    for block in py_blocks:
        if "plt." in block or "ax." in block:
            try:
                plot_image = execute_plot_code(block)
                break
            except Exception:
                pass

    # Intercept QR requests
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
    }The model 'llama-3.1-8b-instant' does not exist or you do not have access to it.
```

Everything in your frontend, download engine, and backend communication is working[cite: 20, 21]. The reason you saw that error is that **`main.py` is still using `'llama-3.1-8b-instant'`**, which is not accessible on your Groq tier.

On Groq's standard developer tier, the active production models are **`llama-3.3-70b-versatile`** or **`openai/gpt-oss-20b`**.

To make your backend resilient against model availability changes, we will use a **fallback chain**: it tries `llama-3.3-70b-versatile` first, and if Groq rejects it, it automatically falls back to `openai/gpt-oss-20b` or `qwen/qwen3.8-27b`.

---

### Step 1: Update `main.py` on GitHub

1. Open your **GitHub** tab for **`Sagar-AITools-Factory`**.
2. Click on **`main.py`** $\rightarrow$ click the **Pencil icon** (Edit).
3. Select everything (`Ctrl + A`), delete it, and paste this complete code:

```python
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

# Candidate models in order of preference
CANDIDATE_MODELS = [
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b"
]

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
    ai_text = None
    last_error = None

    # Multi-model fallback: try each model until one succeeds
    for model_id in CANDIDATE_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": SYSTEM_DIRECTIVE_26_BRAINS},
                    {"role": "user", "content": req.message}
                ],
                temperature=0.5,
                max_tokens=3072,
            )
            ai_text = response.choices[0].message.content
            break
        except Exception as e:
            last_error = str(e)
            continue

    if not ai_text:
        return {
            "text": f"⚠️ **Groq API Error:** {last_error}",
            "plot_image": None,
            "qr_image": None
        }

    # Intercept Matplotlib plots
    plot_image = None
    py_blocks = re.findall(r"```python\s*(.*?)\s*```", ai_text, re.DOTALL)
    for block in py_blocks:
        if "plt." in block or "ax." in block:
            try:
                plot_image = execute_plot_code(block)
                break
            except Exception:
                pass

    # Intercept QR requests
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
