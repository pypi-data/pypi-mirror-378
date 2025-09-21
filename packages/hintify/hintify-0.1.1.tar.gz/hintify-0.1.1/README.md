<div align="center">
  <img src="https://github.com/user-attachments/assets/59c6b462-f88f-4fa9-88b6-e64525878f33" 
       alt="Hintify Logo" height="280">
  <p style="font-size:26px; font-weight:700; margin-top:16px;">
    SnapAssist AI – Real-time Study Assistant
  </p>
</div>
<br>

SnapAssist AI is a **real-time AI-powered study assistant** that helps students solve problems independently by giving **progressive hints instead of direct answers**.

Take a **screenshot of a question** (assignments, PDFs, exams, etc.). SnapAssist will:

- Detect the screenshot from the clipboard
- Extract text via OCR (Tesseract)
- Classify the question (MCQ or Descriptive) and estimate difficulty
- Query an AI model (Ollama locally, or Gemini via API) to generate stepwise hints
- Show hints in a simple GUI, or print them in headless mode

---

## ✨ Features

- 📸 **Cross-platform screenshot detection** – Uses clipboard on macOS, Windows, and Linux
- 🔎 **OCR with Tesseract** – Robust text extraction via `pytesseract`
- 🧩 **Question classification** – MCQ vs. descriptive
- ⚖️ **Difficulty estimation** – Easy / Medium / Hard
- 🤖 **LLM provider selection** – Local via Ollama, or cloud via Gemini
- ⬇️ **Auto-pull Ollama model** – Ensures the selected model is available before first use
- 🔐 **Keychain storage** – Saves Gemini API key securely via `keyring` (one-time setup)
- 🖥️ **GUI or headless** – Tkinter GUI if available, otherwise prints to console
- Beautiful, distraction-free UI with styled hints (bold labels, soft colors)

---

## 🛠 Tech Stack

**Languages & Libraries**

- `Python`
- `pillow` (Image handling, clipboard grab)
- `pytesseract` (OCR)
- `tkinter` (optional GUI)
- `keyring` (secure credential storage)
- `google-generativeai` (Gemini API)

**External Tools**

- **Tesseract OCR** → Text recognition
- **Ollama** → Local AI inference (default model `granite3.2-vision:2b`)

---

## 📦 Installation

1) Python deps
```
pip install -r requirements.txt
```

2) Install Tesseract (required)
- macOS: `brew install tesseract`
- Windows: `choco install tesseract` (or download from the UB Mannheim builds)
- Linux: `sudo apt-get install tesseract-ocr` (or your distro equivalent)

3) Option A: Local via Ollama (recommended for offline)
- Install Ollama from: `https://ollama.com/download`
- The app will auto-pull the model on first run

### Packaging / PyPI

This project is ready for publishing to PyPI with `pyproject.toml` metadata and a console script entry (`hintify`).

Steps:
1. Build artifacts:
```
python -m pip install --upgrade build twine
python -m build
```
2. Upload:
```
python -m twine upload 'dist/*'
```
3. Install:
```
pip install hintify
```

4) Option B: Gemini API (cloud)
- Get an API key from Google AI Studio: [`https://aistudio.google.com/apikey`](https://aistudio.google.com/apikey)
- The app will offer to open the page and save your key securely on first run

---

## 🚀 Quickstart

Run with GUI (default):
```
python hintify.py
```

Install via pip (once published on PyPI):
```
pip install hintify
hintify
```

Hotkeys:
- macOS (global): Cmd+Shift+H to capture (may require Accessibility permission)
- Windows (global): Ctrl+Shift+H to capture (opens Snipping Tool)
- In-app: press 'c' while the window is focused, or click Capture

Headless mode (no tkinter installed):
```
python hintify.py --no-gui
```

Take a screenshot and copy it to the clipboard. Hints will appear automatically.

- GUI extras:
  - Click the "Capture (press 'c')" button or press 'c' while the window is focused to select an area and process it immediately (macOS).

---

## ⚙️ Configuration

CLI options:
```
python hintify.py \
  --provider {ollama|gemini} \
  --ollama-model granite3.2-vision:2b \
  --gemini-model gemini-2.0-flash \
  --poll-interval 1.5 \
  --no-gui
```

Environment variables:
- `HINTIFY_PROVIDER` – Force provider (`ollama` or `gemini`)
- `HINTIFY_OLLAMA_MODEL` – Ollama model ID (default `granite3.2-vision:2b`)
- `GEMINI_API_KEY` – Gemini API key
- `GEMINI_MODEL` – Gemini model ID (default `gemini-2.0-flash`; auto-fallback to `gemini-1.5-flash`)

Provider behavior:
- If Ollama is installed, the app uses Ollama and auto-pulls the model if missing
- If Ollama is not installed, the app offers Gemini setup, opens the API key page, and saves the key in the system keychain
- If both are available, you can select via `--provider` or `HINTIFY_PROVIDER`

Key storage:
- Gemini key is stored securely with `keyring` (`service` = `hintify`, `username` = `gemini_api_key`)
- To clear the saved key:
```
python -c "import keyring; keyring.delete_password('hintify','gemini_api_key')"
```

---

## 🔄 How it Works

1. Monitor clipboard for images
2. OCR with Tesseract
3. Classify question type and difficulty
4. Build a “hints-only” prompt
5. Query Ollama or Gemini
6. Show 3–5 progressive hints (concept → formula → setup → approach → nudge)

---

## 🧰 Troubleshooting

- Tesseract not found: install it and ensure `tesseract` is on PATH (see Installation)
- Clipboard returns `None` on Linux: ensure a desktop environment/clipboard manager is running
- Ollama not found: install from `https://ollama.com/download`
- Gemini 2.5 model not available to your account: the app auto-falls back to `gemini-1.5-flash`

---

## 📌 Project Highlights

- 🔄 Real-time monitoring without user clicks
- 🖼 Optional GUI that doesn’t interrupt workflow
- 📚 Learning-first – Encourages solving, not spoon-feeding
- 🔗 Cross-cutting design – OCR, LLMs, GUI/headless
- 🛠 Extensible – Swap models, add features, redesign UI easily
