# AutoPoster-Agent

An open-source AI Agent framework for generating high-fidelity academic conference posters using LaTeX Beamer.

Born from a rigorous ICLR 2026 submission workflow, this tool provides AI Agents (GPT-4o, Claude, Gemini, local LLMs, etc.) with a battle-tested Standard Operating Procedure (SOP) to avoid common LaTeX rendering pitfalls, eradicate layout overflows ("Overfull \vbox"), and enforce strict data integrity (Zero Hallucination).

## Features

- **Agentic SOP (`agent_sop.md`)**: A battle-tested prompt that teaches LLMs how to construct a 4-column, 185×90cm academic poster without hallucinating numbers or breaking the layout.
- **Robust Beamer Template (`academic_poster_template.tex`)**: Optimized for conference printing. Pre-patched against the "ghost padding" bug caused by `\begin{figure}` inside `\begin{block}`.
- **Multi-Provider LLM Support**: Works with any OpenAI-compatible API — OpenAI, Anthropic (via proxy), Google, local vLLM, Ollama, etc.
- **Secure API Key Management**: Uses your OS-native keychain (macOS Keychain, Windows Credential Locker, Linux Secret Service) — never stores keys in plain text.
- **Figure Pre-processing**: Included script to strip gray/yellow backgrounds from PDF screenshots.

## Platform Compatibility

| Platform | Install Script | Keychain | LaTeX Compiler | Status |
|----------|---------------|----------|----------------|--------|
| **macOS** | `install.sh` | ✅ Keychain | `brew install tectonic` | ✅ Fully supported |
| **Linux** | `install.sh` | ✅ Secret Service | `cargo install tectonic` or `apt install texlive-full` | ✅ Fully supported |
| **Windows** | Manual (see below) | ✅ Credential Locker | [Tectonic releases](https://github.com/tectonic-typesetting/tectonic/releases) | ⚠️ Manual setup |

## Prerequisites

> ⚠️ **Required System Dependency**: You need a LaTeX compiler installed on your system. We recommend **[Tectonic](https://tectonic-typesetting.github.io/)** — it auto-downloads all LaTeX packages on first run and requires no configuration.
>
> ```bash
> # macOS
> brew install tectonic
>
> # Linux (via Cargo)
> cargo install tectonic
>
> # Alternative: pdflatex (requires texlive-full, ~4GB)
> # macOS: brew install --cask mactex
> # Ubuntu: sudo apt install texlive-full
> ```

## Installation & Setup

### Quick Start (macOS / Linux)

```bash
git clone https://github.com/houyili/AutoPoster-Agent.git
cd AutoPoster-Agent
chmod +x install.sh
./install.sh
```

This will:
1. Check Python 3.8+ is installed
2. Create an isolated `.venv` virtual environment
3. Install all Python dependencies
4. Optionally set up your API key in the system keychain

### Manual Setup (Windows / Advanced)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python setup_keychain.py      # Optional: store API key securely
```

### LaTeX Dependencies

The template requires these LaTeX packages: `beamerposter`, `tcolorbox`, `tikz`, `tabularx`, `colortbl`, `booktabs`, `amsmath`. 

- **Tectonic** (recommended): Auto-downloads all packages on first compile.
- **pdflatex**: Requires `texlive-full` or equivalent (`brew install --cask mactex` on macOS).

### Python Dependencies

Requires Python **3.8+**. Dependencies in `requirements.txt`:
- `keyring>=24.0.0` — OS-native credential storage
- `openai>=1.0.0` — LLM API client (works with any OpenAI-compatible endpoint)
- `Pillow>=10.0.0` — Image processing for figure cleanup
- `numpy>=1.26.0` — Used by figure background cleaner

## Autonomous Agent Loop (New in v3)

AutoPoster-Agent is now a fully autonomous **4-Step Agent Loop**:
1. **Step 1 (Outliner)**: Reads your raw LaTeX paper source and extracts a structured `outline.md` (Motivation, Methods, Results, Figures to keep).
2. **Step 2 (Generator)**: Fills the Beamer template to create `poster.tex` and compiles it.
3. **Step 3 (Evaluator)**: Runs deterministic Python checks (missing figures, forbidden LaTeX syntax like `\begin{figure}`) and LLM Rubric checks (visual balance, text overlaps) to output a `problem.md` report.
4. **Step 4 (Retry Loop)**: If the poster fails, the Generator is called again with the feedback to fix its mistakes. Maximum 3 retries.

### Fully Automated Mode (End-to-End)

```bash
source .venv/bin/activate
python agent_loop.py path/to/your/paper.tex --figures-dir path/to/figures/
```

If you already have an `outline.md` and want to skip Step 1:
```bash
python agent_loop.py outline.md --figures-dir path/to/figures/
```

### Manual Step-by-Step Execution

You can run each agent individually:
```bash
# Step 1: Generate Outline
python step1_outliner.py path/to/paper.tex -o outline.md

# Step 2: Generate Poster
python step2_generator.py outline.md --figures-dir path/to/figures/ -o poster.tex

# Step 3: Evaluate Poster
python step3_evaluator.py poster.tex outline.md -o problem.md
```

**CLI Options for `agent_loop.py`**:

| Flag | Description | Default |
|------|-------------|---------|
| `--model` | LLM model name | `gpt-4o` |
| `--base-url` | Custom API endpoint (for vLLM, Ollama, etc.) | OpenAI |
| `--figures-dir` | Directory of images to embed | None |

**Examples:**

```bash
# Use GPT-4o (default)
python generate_poster.py outline.md --figures-dir ./figures/

# Use a local vLLM server
python generate_poster.py outline.md --base-url http://localhost:8000/v1 --model mistral-7b

# Use Claude via OpenAI-compatible proxy
python generate_poster.py outline.md --base-url https://api.anthropic.com/v1 --model claude-sonnet-4-20250514

# Generate .tex only, compile manually later
python generate_poster.py outline.md --no-compile
```

### Manual IDE Mode (Cursor / Copilot / Aider)

1. Open your AI code editor.
2. Add `templates/prompt_sops/agent_sop.md` to the Agent's context.
3. Provide `templates/academic_poster_template.tex` and your `outline.md`.
4. Instruct: *"Use the agent_sop.md to fill out the academic_poster_template.tex with my outline."*

### Pre-processing Figures

Strip ugly gray backgrounds from screenshots before embedding:

```bash
python tools/clean_figure_backgrounds.py path/to/raw_figure.png
# → Outputs: path/to/raw_figure_clean.png
```

### Compiling the Poster

```bash
tectonic poster.tex           # Recommended
# or
pdflatex poster.tex           # Alternative (requires texlive-full)
```

## Project Structure

```
AutoPoster-Agent/
├── agent_loop.py                   # Master Orchestrator (Step 4 Retry loop)
├── step1_outliner.py               # Outliner Agent
├── step2_generator.py              # Generator Agent
├── step3_evaluator.py              # Evaluator/Judge Agent
├── setup_keychain.py               # Secure API key storage
├── install.sh                      # One-click installer (macOS/Linux)
├── requirements.txt                # Python dependencies
├── templates/
│   ├── academic_poster_template.tex  # Beamer template (185×90cm)
│   └── prompt_sops/
│       ├── agent_sop.md              # Generator SOP
│       └── rubric_evaluator.md       # Evaluator Rubric
├── tools/
│   └── clean_figure_backgrounds.py   # Image background stripper
└── examples/
    └── sample_outline.md             # Example outline format
```

## Contributing

We welcome contributions to expand the SOPs and templates for other conferences (NeurIPS, CVPR, ACL, EMNLP). PRs for Windows install scripts and additional LLM provider integrations are especially appreciated.

## License

MIT License
